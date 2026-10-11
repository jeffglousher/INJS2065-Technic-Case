"""Add non-printing rail speed modifiers and measured-height detail bands to Bambu projects."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
ET.register_namespace('', NS)
ET.register_namespace('p', PROD)
ET.register_namespace('BambuStudio', 'http://schemas.bambulab.com/package/2021')
SPEEDS = {'outer_wall_speed': '30', 'inner_wall_speed': '45', 'gap_infill_speed': '30',
          'internal_solid_infill_speed': '45', 'top_surface_speed': '30',
          'small_perimeter_speed': '25'}
# Heights are in each already-oriented shell's build coordinates.
BANDS = {1: [(5.0, 10.95)], 2: [(0.2, 3.6), (8.5, 15.5), (18.0, 24.45)]}
HEIGHTS = {1: 10.95, 2: 24.45}


def meta(parent, key, value):
    entries = [m for m in parent.findall('metadata') if m.get('key') == key]
    for m in entries:
        parent.remove(m)
    ET.SubElement(parent, 'metadata', key=key, value=value)


def box(resources, resource_id, bounds):
    lo, hi = bounds
    obj = ET.SubElement(resources, '{' + NS + '}object', id=str(resource_id), type='model')
    mesh = ET.SubElement(obj, '{' + NS + '}mesh')
    vertices = ET.SubElement(mesh, '{' + NS + '}vertices')
    points = [(lo[0],lo[1],lo[2]), (hi[0],lo[1],lo[2]), (hi[0],hi[1],lo[2]), (lo[0],hi[1],lo[2]),
              (lo[0],lo[1],hi[2]), (hi[0],lo[1],hi[2]), (hi[0],hi[1],hi[2]), (lo[0],hi[1],hi[2])]
    for p in points:
        ET.SubElement(vertices, '{' + NS + '}vertex', **dict(zip(('x','y','z'), map(str,p))))
    triangles = ET.SubElement(mesh, '{' + NS + '}triangles')
    for t in [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
              (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]:
        ET.SubElement(triangles, '{' + NS + '}triangle', **dict(zip(('v1','v2','v3'),map(str,t))))


def configure(source, target, generator):
    with zipfile.ZipFile(source) as z:
        infos = z.infolist()
        payloads = {i.filename: z.read(i.filename) for i in infos}
    settings = json.loads(payloads['Metadata/project_settings.config'])
    settings['wall_generator'] = generator
    # GUI reload reconciles against the named system preset. Preserve this edit there,
    # as well as in the resolved config used by command-line slicing.
    differences = settings.get('different_settings_to_system', ['', '', ''])
    process_keys = set(filter(None,differences[0].split(';')))
    process_keys.add('wall_generator')
    differences[0] = ';'.join(sorted(process_keys))
    settings['different_settings_to_system'] = differences
    payloads['Metadata/project_settings.config'] = (json.dumps(settings,indent=2)+'\n').encode()
    model = ET.fromstring(payloads['3D/3dmodel.model'])
    resources = model.find('{' + NS + '}resources')
    cfg = ET.fromstring(payloads['Metadata/model_settings.config'])
    owned_ids = set()
    if len(cfg.findall('object')) not in (4, 5):
        raise ValueError('Expected canonical fit-test or assembly objects')
    # Only replace modifiers owned by this script; reject unknown modifiers rather than delete them.
    for index, obj in enumerate(cfg.findall('object')[:2], 1):
        name = next((m.get('value') for m in obj.findall('metadata') if m.get('key') == 'name'), None)
        if name != ('Lower clamshell' if index == 1 else 'Upper clamshell'):
            raise ValueError('Expected canonical shell order')
        for part in list(obj.findall('part')):
            if part.get('subtype') == 'modifier_part':
                name = next((m.get('value','') for m in part.findall('metadata') if m.get('key') == 'name'), '')
                expected = {str(200+(index-1)*2+1): 'Technic rail quality -Y',
                            str(200+(index-1)*2+2): 'Technic rail quality +Y'}
                if expected.get(part.get('id')) != name:
                    raise ValueError('Existing unrelated modifier must be preserved and reviewed')
                owned_ids.add(part.get('id'))
                obj.remove(part)
    for node in list(resources):
        if node.get('id') in ('201','202','203','204'):
            if node.get('id') not in owned_ids:
                raise ValueError('Modifier resource ID collides with an unrelated object')
            resources.remove(node)
    if 'Metadata/layer_config_ranges.xml' in payloads:
        previous = ET.fromstring(payloads['Metadata/layer_config_ranges.xml'])
        expected_ranges = ET.Element('objects')
        for index, bands in BANDS.items():
            entry = ET.SubElement(expected_ranges, 'object', id=str(index))
            for low, high in bands:
                band = ET.SubElement(entry, 'range', min_z=str(low), max_z=str(high))
                ET.SubElement(band, 'option', opt_key='layer_height').text = '0.12'
        if ET.tostring(previous) != ET.tostring(expected_ranges):
            raise ValueError('Existing unrelated layer ranges must be preserved and reviewed')
    ranges = ET.Element('objects')
    for index, obj in enumerate(cfg.findall('object')[:2], 1):
        parent = next(o for o in resources if o.get('id') == obj.get('id'))
        components = parent.find('{' + NS + '}components')
        for c in list(components):
            if c.get('objectid') in ('201','202','203','204'):
                components.remove(c)
        # Shells inherit the generator; clips and hub below explicitly retain Classic.
        for m in list(obj.findall('metadata')):
            if m.get('key') == 'wall_generator':
                obj.remove(m)
        for side in (-1, 1):
            rid = 200 + (index-1)*2 + (1 if side < 0 else 2)
            ylo, yhi = (-12.5,-5.2) if side < 0 else (5.2,12.5)
            box(resources, rid, ((-21,ylo,-0.01),(21,yhi,HEIGHTS[index]+0.01)))
            ET.SubElement(components, '{' + NS + '}component', objectid=str(rid), transform='1 0 0 0 1 0 0 0 1 0 0 0')
            part = ET.SubElement(obj, 'part', id=str(rid), subtype='modifier_part')
            meta(part,'name',f'Technic rail quality {"+Y" if side > 0 else "-Y"}')
            meta(part,'matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
            for key, value in SPEEDS.items():
                # X2D process options have six nullable nozzle/flow entries. A scalar only
                # sets the first entry; other entries can fall back to faster defaults.
                meta(part,key,','.join([value]*6))
        entry = ET.SubElement(ranges, 'object', id=str(index))
        for low, high in BANDS[index]:
            band = ET.SubElement(entry, 'range', min_z=str(low), max_z=str(high))
            ET.SubElement(band,'option',opt_key='layer_height').text='0.12'
    plate = cfg.find('plate')
    for obj in cfg.findall('object')[2:]:
        meta(obj,'wall_generator','classic')
    meta(plate,'plater_name','INJS2065 PETG - local rail quality - no supports or brims')
    payloads['3D/3dmodel.model'] = ET.tostring(model,encoding='utf-8',xml_declaration=True)
    payloads['Metadata/model_settings.config'] = ET.tostring(cfg,encoding='utf-8',xml_declaration=True)
    payloads['Metadata/layer_config_ranges.xml'] = ET.tostring(ranges,encoding='utf-8',xml_declaration=True)
    target.parent.mkdir(parents=True,exist_ok=True)
    temporary=target.with_suffix('.tmp')
    with zipfile.ZipFile(temporary,'w') as z:
        for info in infos:
            z.writestr(info,payloads.pop(info.filename))
        for name, raw in payloads.items():
            z.writestr(name,raw,compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(temporary) as z:
        if z.testzip() is not None:
            raise ValueError('Archive validation failed')
    temporary.replace(target)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,required=True)
    parser.add_argument('--wall-generator',choices=['classic','arachne'],default='arachne')
    args=parser.parse_args()
    for name in ('assembly-petg.3mf','fit-test-petg.3mf'):
        configure(ROOT/'print'/name,args.output_directory/name,args.wall_generator)
    print('Configured four regional rail modifiers and 0.12 mm shell height bands; printable meshes unchanged.')
