"""Inspect commanded Bambu extrusion speeds/widths and layer bands, without a printer."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

TOKENS = re.compile(r'([A-Z])([-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?)')


def segments(path):
    pos = {'X': 0., 'Y': 0., 'Z': 0.}
    relative_e = True
    epos = feed = width = height = zheight = 0.
    obj = None
    feature = ''
    for line in path.read_text().splitlines():
        if line.startswith('; start printing object, unique label id: '):
            obj = int(line.rsplit(': ',1)[1])
        elif line.startswith('; stop printing object'):
            obj = None
        elif line.startswith('; FEATURE: '):
            feature = line[11:]
        elif line.startswith('; LINE_WIDTH: '):
            width = float(line[14:])
        elif line.startswith('; LAYER_HEIGHT: '):
            height = float(line[16:])
        elif line.startswith('; Z_HEIGHT: '):
            zheight = float(line[12:])
        command = line.split(';',1)[0].strip()
        if not command:
            continue
        code = command.split()[0]
        values = {k:float(v) for k,v in TOKENS.findall(command)}
        if code == 'M83':
            relative_e = True
        elif code == 'M82':
            relative_e = False
        elif code == 'G92':
            if 'E' in values:
                epos = values['E']
        elif code in ('G0','G1','G2','G3'):
            before = dict(pos)
            if 'F' in values:
                feed = values['F'] / 60
            for axis in pos:
                if axis in values:
                    pos[axis] = values[axis]
            extrusion = values.get('E',0) if relative_e else values.get('E',epos)-epos
            if 'E' in values:
                epos = values['E']
            if obj and extrusion > 0 and ('X' in values or 'Y' in values):
                yield {'object':obj,'feature':feature,'a':[before[a] for a in ('X','Y')],
                       'b':[pos[a] for a in ('X','Y')],'z':zheight,'layer_height':height,
                       'speed':feed,'width':width,'e':extrusion,'arc':code in ('G2','G3'),
                       'arc_center':[before['X']+values.get('I',0),before['Y']+values.get('J',0)] if code in ('G2','G3') else None,
                       'clockwise':code == 'G2'}


def rail(s):
    if s['object'] not in (1,2):
        return False
    center = 55 if s['object']==1 else 175
    # Keep 0.2 mm away from the modifier boundary to avoid straddling segment ambiguity.
    return all(5.4 <= abs(p[1]-center) <= 12.2 for p in (s['a'],s['b']))


def stats(rows):
    by_feature = defaultdict(list)
    for s in rows:
        if rail(s) and s['z'] > 0.21:
            by_feature[s['feature']].append(s)
    return {k:{'segments':len(v),'speed_min_mm_s':min(s['speed'] for s in v),
               'speed_median_mm_s':statistics.median(s['speed'] for s in v),
               'speed_max_mm_s':max(s['speed'] for s in v),
               'width_min_mm':min(s['width'] for s in v),'width_max_mm':max(s['width'] for s in v)}
            for k,v in sorted(by_feature.items())}


def audit(path):
    rows = list(segments(path))
    data = {'gcode_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rail_stats':stats(rows),
            'shell_layer_heights_mm':{str(i):sorted({round(s['layer_height'],5) for s in rows if s['object']==i and s['feature'] in ('Outer wall','Inner wall')}) for i in (1,2)},
            'supports_brims_skirts_absent':not any(any(w in s['feature'].lower() for w in ('support','brim','skirt')) for s in rows)}
    return data, rows


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('gcode',type=Path)
    args=parser.parse_args()
    print(json.dumps(audit(args.gcode)[0],indent=2))
