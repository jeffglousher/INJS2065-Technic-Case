"""Verify the current saved Bambu projects without dependencies or a printer connection."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NS = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'


def check(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(node):
    return {n.get('key'): n.get('value') for n in node.findall('metadata') if n.get('key')}


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


def audit_project(filename, count):
    path = ROOT / 'print' / filename
    with zipfile.ZipFile(path) as z:
        settings = json.loads(z.read('Metadata/project_settings.config'))
        cfg = ET.fromstring(z.read('Metadata/model_settings.config'))
        model = ET.fromstring(z.read('3D/3dmodel.model'))
        objects = cfg.findall('object')
        check(len(objects) == count and len(model.find(NS + 'build')) == count, f'{filename}: object count')
        expected_names = ['Lower clamshell', 'Upper clamshell', 'Clip +Y', 'Clip -Y', 'Output hub'][:count]
        check([metadata(o)['name'] for o in objects] == expected_names, f'{filename}: unexpected object names/order')
        check(settings['printer_settings_id'] == 'Bambu Lab X2D 0.4 nozzle', 'Wrong printer/nozzle')
        check(settings['filament_type'] == ['PETG'] and any('PETG Basic' in s for s in settings['filament_settings_id']), 'Wrong material')
        check(settings['print_sequence'] == 'by object' and metadata(cfg.find('plate'))['print_sequence'] == 'by object', 'Wrong print sequence')
        check(settings['brim_type'] == 'no_brim' and settings['brim_width'] == '0'
              and settings['skirt_loops'] == '0' and settings['enable_support'] == '0', 'Unexpected global brim/skirt/support')
        check(settings['layer_height'] == '0.16' and settings['wall_loops'] == '4' and settings['sparse_infill_density'] == '25%', 'Wrong main process')
        check(settings['wall_generator'] == 'arachne', 'Shell Arachne process missing')
        check('wall_generator' in settings['different_settings_to_system'][0].split(';'), 'GUI reload would discard Arachne')
        bands = ET.fromstring(z.read('Metadata/layer_config_ranges.xml'))
        expected_bands = {'1':[(5.0,10.95)], '2':[(0.2,3.6),(8.5,15.5),(18.0,24.45)]}
        check(len(bands.findall('object')) == 2, 'Unexpected height-band object count')
        for node in bands.findall('object'):
            check(node.get('id') in expected_bands, 'Height band affects clip/hub')
            check([(float(r.get('min_z')),float(r.get('max_z'))) for r in node.findall('range')] == expected_bands[node.get('id')], 'Wrong height bands')
            check(all(len(r.findall('option')) == 1 and r.find('option').get('opt_key') == 'layer_height'
                      and r.find('option').text == '0.12' for r in node.findall('range')), 'Wrong band options')
        rows = []
        for i, obj in enumerate(objects, 1):
            values = metadata(obj)
            name = values['name']
            row = audit_mesh(z.read(f'3D/Objects/object_{i}.model'), name)
            check(values.get('enable_support', settings['enable_support']) == '0', f'{name}: unexpected support')
            check(values.get('brim_type', settings['brim_type']) == 'no_brim'
                  and values.get('brim_width', settings['brim_width']) == '0', f'{name}: unexpected brim')
            check(not row['support_paint_counts'], f'{name}: stale support paint')
            check(len(obj.findall("part[@subtype='normal_part']")) == 1, f'{name}: unexpected printable parts')
            modifiers = obj.findall("part[@subtype='modifier_part']")
            if i <= 2:
                check('wall_generator' not in values, 'Shell does not inherit the validated process generator')
                check(len(modifiers) == 2, f'{name}: missing rail modifiers')
                required_speeds = {'outer_wall_speed':'30','inner_wall_speed':'45','gap_infill_speed':'30',
                                   'internal_solid_infill_speed':'45','top_surface_speed':'30','small_perimeter_speed':'25'}
                resources = model.find(NS + 'resources')
                for modifier in modifiers:
                    mv = metadata(modifier)
                    check(mv.get('name','').startswith('Technic rail quality '), 'Unknown modifier')
                    check(all(mv.get(k) == ','.join([v]*6) for k,v in required_speeds.items()), 'Modifier nullable speeds differ')
                    mesh = next(n for n in resources if n.get('id') == modifier.get('id'))
                    audit_mesh(ET.tostring(mesh), mv['name'])
            else:
                check(not modifiers and values.get('wall_generator') == 'classic', f'{name}: unintended modifiers/generator')
            if name == 'Output hub':
                required = {'enable_support':'0', 'layer_height':'0.08', 'wall_loops':'6', 'sparse_infill_density':'100',
                            'outer_wall_speed':'30', 'inner_wall_speed':'60',
                            'bridge_flow':'0.9', 'bridge_speed':'25', 'thick_bridges':'0', 'bridge_no_support':'1'}
                check(all(values.get(k) == v for k, v in required.items()), 'Hub settings differ')
                item = next(item for item in model.find(NS + 'build') if item.get('objectid') == obj.get('id'))
                check([float(x) for x in item.get('transform').split()][:9] == [1,0,0,0,-1,0,0,0,-1], 'Hub is not flipped')
            row['object_overrides'] = values
            rows.append(row)
        return {'file': 'print/' + filename, 'project_sha256': sha(path), 'objects': rows,
                'printer': settings['printer_settings_id'], 'sequence': settings['print_sequence']}


def main():
    manifest = json.loads((ROOT / 'review/current/files.json').read_text())
    for name, entry in manifest.items():
        check(sha(ROOT / name) == entry['sha256'], f'Current file changed: {name}')
    with zipfile.ZipFile(ROOT / 'design/current.nbcad') as z:
        check(json.loads(z.read('model.json')) == json.loads((ROOT / 'design/current.model.json').read_text()), 'Native project and JSON differ')
    assembly = audit_project('assembly-petg.3mf', 5)
    fit = audit_project('fit-test-petg.3mf', 4)
    check([r['mesh_sha256'] for r in assembly['objects'][:4]] == [r['mesh_sha256'] for r in fit['objects']], 'Fit meshes differ')
    for project, receipt_name in [(assembly, 'assembly-slice.json'), (fit, 'fit-test-slice.json')]:
        receipt = json.loads((ROOT / 'review/current' / receipt_name).read_text())
        check(receipt['project_sha256'] == project['project_sha256'] and receipt['native_result']['return_code'] == 0, 'Slice receipt does not match project')
        check(receipt['supports_absent'] and receipt['brims_skirts_absent'], 'Slice contains supports/brims/skirts')
        quality = json.loads((ROOT / 'review/current/local-quality-check.json').read_text())
        record = next(r for r in quality['projects'] if r['project'] == project['file'])
        check(quality['passed'] and record['project_sha256'] == project['project_sha256']
              and record['gcode_sha256'] == receipt['gcode_sha256'], 'Local toolpath receipt is stale')
        for plate in receipt['native_result']['sliced_plates']:
            check(not plate['warning_message'], 'Native slice warning')
            check(not any('support' in k.lower() or 'brim' in k.lower() or 'skirt' in k.lower()
                          for k in plate['feature_type_times']), 'Native slice has support/brim/skirt paths')
    result = {'passed': True, 'projects': [assembly, fit], 'weld_tolerance_mm': 1e-5,
              'limits': 'Topology and saved settings audit; no exhaustive triangle self-intersection, measured printer accuracy or physical snap/strength qualification.',
              'print_sent': False}
    (ROOT / 'review/current/print-project-check.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: five assembly / four fit-test parts; closed connected positive meshes; four non-printing rail modifiers; shell detail bands/Arachne; no supports or brims; clip/hub overrides preserved; matching slice receipts.')


if __name__ == '__main__':
    main()
