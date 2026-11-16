"""Put the six validated retention coupons on one sequential, single-filament plate.

No scaling, rotation, geometry edits or layer-schedule changes. Run after preparing
the separate source projects. Slicing and its clearance checks remain required.
"""
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
P = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
tag = lambda name: '{' + NS + '}' + name
ET.register_namespace('', NS)
ET.register_namespace('p', P)

# Wide spacing permits original per-object layer bands and avoids changing the
# cooling history to a shared layer schedule. Native slicer must also accept it.
PLACEMENTS = [(60, 28), (60, 128), (60, 224),
              (180, 40), (180, 128), (180, 216)]


def main():
    reference = json.loads((ROOT/'docs/retention-validation.json').read_text())
    sources = {}
    for label in ('receivers', 'clips'):
        path = ROOT/reference['projects'][label]['path']
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != reference['projects'][label]['sha256']:
            raise ValueError(f'{label}: source changed since mesh validation')
        with zipfile.ZipFile(path) as z:
            sources[label] = {name: z.read(name) for name in z.namelist()}
    data = {name: raw for name, raw in sources['clips'].items()
            if not name.startswith('3D/Objects/')}
    settings = json.loads(data['Metadata/project_settings.config'])
    if settings['print_sequence'] != 'by object' or settings['filament_type'] != ['PETG']:
        raise ValueError('Expected sequential single-filament PETG source')
    config = ET.fromstring(data['Metadata/model_settings.config'])
    for obj in config.findall('object'):
        config.remove(obj)
    plate = config.find('plate')
    for inst in plate.findall('model_instance'):
        plate.remove(inst)
    plate.find("metadata[@key='plater_name']").set('value', 'Retention coupons 1-6 - PETG')
    assemble = config.find('assemble')
    assemble.clear()
    model = ET.fromstring(data['3D/3dmodel.model'])
    resources, build = model.find(tag('resources')), model.find(tag('build'))
    resources.clear()
    build.clear()
    relationships = ET.Element('{' + REL + '}Relationships')
    ranges = ET.Element('objects')
    records = []
    for index in range(1, 7):
        label, source_index = ('receivers', index) if index <= 3 else ('clips', index-3)
        source = sources[label]
        source_name = f'3D/Objects/object_{source_index}.model'
        mesh_root = ET.fromstring(source[source_name])
        mesh = mesh_root.find('.//' + tag('mesh'))
        mesh_bytes = ET.tostring(mesh)
        mesh_root.find('.//' + tag('object')).set('id', str(index))
        data[f'3D/Objects/object_{index}.model'] = ET.tostring(mesh_root, encoding='utf-8', xml_declaration=True)
        if ET.tostring(ET.fromstring(data[f'3D/Objects/object_{index}.model']).find('.//' + tag('mesh'))) != mesh_bytes:
            raise ValueError('Mesh changed during composition')
        obj = copy.deepcopy(ET.fromstring(source['Metadata/model_settings.config']).findall('object')[source_index-1])
        obj.set('id', str(100+index))
        obj.find('part').set('id', str(index))
        config.append(obj)
        x, y = PLACEMENTS[index-1]
        transform = f'1 0 0 0 1 0 0 0 1 {x} {y} 0'
        inst = ET.SubElement(plate, 'model_instance')
        for key, value in [('object_id', str(100+index)), ('instance_id', '0'), ('identify_id', str(index))]:
            ET.SubElement(inst, 'metadata', {'key': key, 'value': value})
        ET.SubElement(assemble, 'assemble_item', {'object_id': str(100+index), 'instance_id': '0', 'transform': transform, 'offset': '0 0 0'})
        wrapper = ET.SubElement(resources, tag('object'), {'id': str(100+index), 'type': 'model'})
        components = ET.SubElement(wrapper, tag('components'))
        ET.SubElement(components, tag('component'), {'{'+P+'}path': f'/3D/Objects/object_{index}.model', 'objectid': str(index), 'transform': '1 0 0 0 1 0 0 0 1 0 0 0'})
        ET.SubElement(build, tag('item'), {'objectid': str(100+index), 'transform': transform, 'printable': '1'})
        ET.SubElement(relationships, '{'+REL+'}Relationship', {'Target': f'/3D/Objects/object_{index}.model', 'Id': f'rel-{index}', 'Type': 'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'})
        original_range = ET.fromstring(source['Metadata/layer_config_ranges.xml']).find(f"object[@id='{source_index}']")
        if original_range is not None:
            original_range.set('id', str(index))
            ranges.append(original_range)
        points = [[float(v.get(k)) for k in ('x', 'y', 'z')] for v in mesh.iter(tag('vertex'))]
        bounds = [[min(p[j] for p in points), max(p[j] for p in points)] for j in range(3)]
        if min(bounds[0][0]+x, bounds[1][0]+y) < 5 or max(bounds[0][1]+x, bounds[1][1]+y) > 251:
            raise ValueError('Coupon too close to bed edge')
        records.append({'object': index, 'name': obj.find("metadata[@key='name']").get('value'),
                        'source': label, 'source_object': source_index,
                        'mesh_sha256': hashlib.sha256(mesh_bytes).hexdigest(),
                        'center_xy_mm': [x, y], 'mesh_bounds_mm': bounds})
    for name, tree in [('Metadata/model_settings.config', config), ('3D/3dmodel.model', model),
                       ('Metadata/layer_config_ranges.xml', ranges), ('3D/_rels/3dmodel.model.rels', relationships)]:
        ET.register_namespace('', REL if name.endswith('.rels') else NS)
        data[name] = ET.tostring(tree, encoding='utf-8', xml_declaration=True)
    ET.register_namespace('', NS)
    output = ROOT/'print/retention/coupons-complete.3mf'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, raw in data.items():
            z.writestr(name, raw)
    evidence = {'status': 'awaiting native slice and physical fit test',
                'path': 'print/retention/coupons-complete.3mf',
                'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                'source_project_sha256': {label: reference['projects'][label]['sha256'] for label in sources},
                'geometry_and_original_layer_bands_preserved': True,
                'single_filament': 'Bambu PETG Basic', 'print_sequence': 'by object',
                'parts': records}
    (ROOT/'docs/retention-complete-validation.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print('Prepared six unchanged coupons on one PETG plate; native clearance validation required.')


if __name__ == '__main__':
    main()
