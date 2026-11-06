"""Verify the current print project and saved model without a printer connection."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"

def check(condition, message):
    if not condition:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def metadata(node):
    return {m.get("key"):m.get("value") for m in node.findall("metadata") if m.get("key")}

def audit_mesh(raw, name):
    model = ET.fromstring(raw)
    vertices = [tuple(float(v.get(a)) for a in ('x', 'y', 'z')) for v in model.iter(NS + 'vertex')]
    triangles = list(model.iter(NS + 'triangle'))
    check(all(math.isfinite(v) for p in vertices for v in p), f'{name}: nonfinite vertex')
    welded = {}
    ids = []
    for p in vertices:
        key = tuple(round(v * 100000) for v in p)
        ids.append(welded.setdefault(key, len(welded)))
    parent = list(range(len(welded)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    edges, orientation, faces, paint = Counter(), Counter(), set(), Counter()
    volume = 0.0
    degenerate = duplicate = 0
    for t in triangles:
        original = tuple(int(t.get(a)) for a in ('v1', 'v2', 'v3'))
        check(all(0 <= i < len(vertices) for i in original), f'{name}: invalid index')
        a, b, c = (vertices[i] for i in original)
        volume += (a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0])) / 6
        face = tuple(ids[i] for i in original)
        if len(set(face)) < 3:
            degenerate += 1
        key = tuple(sorted(face))
        if key in faces:
            duplicate += 1
        faces.add(key)
        for a, b in zip(face, face[1:] + face[:1]):
            edge = tuple(sorted((a, b)))
            edges[edge] += 1
            orientation[edge] += 1 if a < b else -1
            parent[find(a)] = find(b)
        for key, value in t.attrib.items():
            if 'support' in key:
                paint[value] += 1
    components = len({find(x) for x in range(len(parent))})
    bad_edges = sum(v != 2 for v in edges.values())
    bad_winding = sum(v != 0 for v in orientation.values())
    check(not degenerate and not duplicate and not bad_edges and not bad_winding and components == 1 and volume > 0,
          f'{name}: mesh failed closure/connectivity/winding/volume checks')
    return {'name': name, 'triangles': len(triangles), 'volume_mm3': volume,
            'components': components, 'bad_edges': bad_edges, 'bad_winding': bad_winding,
            'duplicate_faces': duplicate, 'collapsed_faces_at_1e_5_mm': degenerate,
            'support_paint_counts': dict(paint), 'mesh_sha256': hashlib.sha256(raw).hexdigest()}


def audit_project():
    evidence = json.loads((ROOT / 'docs/validation.json').read_text())
    check(len(evidence['parts']) == 5, 'Expected five mesh reference records')
    path = ROOT / evidence['project']
    check(sha(path) == evidence['project_sha256'], 'Print-project hash differs')
    check(sha(ROOT / 'design/current.model.json') == evidence['model_sha256'], 'Editable model hash differs')
    check(sha(ROOT / 'design/current.nbcad') == evidence['native_model_sha256'], 'Native model hash differs')
    with zipfile.ZipFile(ROOT / 'design/current.nbcad') as saved:
        check(json.loads(saved.read('model.json')) == json.loads((ROOT / 'design/current.model.json').read_text()),
              'Saved native model and JSON differ')
    with zipfile.ZipFile(path) as z:
        check(z.testzip() is None, 'Damaged 3MF archive')
        settings = json.loads(z.read('Metadata/project_settings.config'))
        cfg = ET.fromstring(z.read('Metadata/model_settings.config'))
        model = ET.fromstring(z.read('3D/3dmodel.model'))
        objects = cfg.findall('object')
        build = model.find(NS + 'build')
        resources = model.find(NS + 'resources')
        check(len(objects) == len(build) == len(resources) == 5, 'Expected five printable objects')
        check(not cfg.findall(".//part[@subtype='modifier_part']"), 'Unexpected modifier volumes')
        check(settings['printer_settings_id'] == 'Bambu Lab X2D 0.4 nozzle', 'Wrong printer/nozzle')
        check(settings['filament_type'] == ['PETG'] and any('PETG Basic' in s for s in settings['filament_settings_id']), 'Wrong material')
        check(settings['print_sequence'] == metadata(cfg.find('plate'))['print_sequence'] == 'by object', 'Wrong print sequence')
        check(settings['enable_support'] == '0' and settings['brim_type'] == 'no_brim'
              and settings['brim_width'] == '0' and settings['skirt_loops'] == '0', 'Unexpected supports/brim/skirt')
        check(settings['layer_height'] == '0.16' and settings['initial_layer_print_height'] == '0.2'
              and settings['wall_loops'] == '4' and settings['sparse_infill_density'] == '25%', 'Wrong main process')
        check(settings['wall_generator'] == 'arachne'
              and 'wall_generator' in settings['different_settings_to_system'][0].split(';'), 'Shell Arachne setting missing')
        bands = ET.fromstring(z.read('Metadata/layer_config_ranges.xml'))
        expected = {'1':[(5.0,10.95)], '2':[(0.2,3.6),(8.5,15.5),(18.0,24.45)]}
        check(sorted(n.get('id') for n in bands) == ['1','2'], 'Unexpected layer-band owners')
        for node in bands:
            check([(float(n.get('min_z')),float(n.get('max_z'))) for n in node] == expected[node.get('id')], 'Wrong detail bands')
            check(all(len(n) == 1 and n[0].get('opt_key') == 'layer_height' and n[0].text == '0.12' for n in node), 'Wrong band options')
        speeds = {'outer_wall_speed':'30','inner_wall_speed':'45','gap_infill_speed':'30',
                  'internal_solid_infill_speed':'45','top_surface_speed':'30','small_perimeter_speed':'25'}
        names = ['Lower clamshell','Upper clamshell','Clip +Y','Clip -Y','Output hub']
        translations = [(50,55,0),(50,175,0),(150,55,0),(150,175,0),(220,115,15.700000763)]
        rows = []
        for i,(obj,name,record,item,resource,translation) in enumerate(zip(objects,names,evidence['parts'],build,resources,translations),1):
            values = metadata(obj)
            check(values['name'] == name, 'Object names/order differ')
            check(obj.get('id') == resource.get('id') == item.get('objectid') == str(100+i), 'Wrong component ownership')
            check(len(obj.findall("part[@subtype='normal_part']")) == 1 and len(obj.findall('part')) == 1, 'Unexpected printable parts')
            components = resource.find(NS+'components')
            check(components is not None and len(components) == 1 and components[0].get('objectid') == str(i), 'Wrong mesh attachment')
            check([float(v) for v in components[0].get('transform').split()] == [1,0,0,0,1,0,0,0,1,0,0,0], 'Unexpected component transform')
            check(components[0].get('{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}path') == f'/3D/Objects/object_{i}.model', 'Wrong mesh payload')
            transform = [float(v) for v in item.get('transform').split()]
            rotation = [1,0,0,0,1,0,0,0,1] if i != 5 else [1,0,0,0,-1,0,0,0,-1]
            check(transform[:9] == rotation and all(abs(a-b)<1e-7 for a,b in zip(transform[9:],translation)), 'Wrong print placement')
            row = audit_mesh(z.read(f'3D/Objects/object_{i}.model'),name)
            check(row['mesh_sha256'] == record['mesh_sha256'] and not row['support_paint_counts'], 'Mesh hash or support paint differs')
            check(values.get('enable_support',settings['enable_support']) == '0'
                  and values.get('brim_type',settings['brim_type']) == 'no_brim', 'Unexpected per-object support/brim')
            if i <= 2:
                check(all(values.get(k) == ','.join([v]*6) for k,v in speeds.items()), 'Wrong shell-wide speeds')
                check('wall_generator' not in values, 'Shell must inherit Arachne')
            else:
                check(values.get('wall_generator') == 'classic', 'Wrong clip/hub generator')
            if i == 5:
                check(all(values.get(k) == v for k,v in {'layer_height':'0.08','wall_loops':'6','sparse_infill_density':'100',
                      'outer_wall_speed':'30','inner_wall_speed':'60','bridge_flow':'0.9','bridge_speed':'25',
                      'thick_bridges':'0','bridge_no_support':'1'}.items()), 'Wrong hub process')
            rows.append(row)
    return rows


def main():
    rows = audit_project()
    evidence = json.loads((ROOT/'docs/validation.json').read_text())
    check(evidence['native_slice']['return_code'] == 0, 'Native slice failed')
    check(all(not p['warning_message'] and len(p['objects']) == 5 for p in evidence['native_slice']['sliced_plates']), 'Native warnings/count differ')
    check(evidence['toolpaths']['supports_brims_skirts_absent'] and evidence['toolpaths']['clips_slice_solid'], 'Unqualified toolpaths')
    print(f'PASS {len(rows)} closed, connected print meshes; model consistency, placement, settings and slice receipt.')


if __name__ == '__main__':
    main()
