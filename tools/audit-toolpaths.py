"""Inspect commanded Bambu extrusion speeds/widths and layer bands, without a printer."""
import re

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
