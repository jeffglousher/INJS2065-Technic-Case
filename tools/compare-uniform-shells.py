"""Create a review candidate with shell-wide speeds instead of regional modifiers.

Keeps printable mesh payloads, placement, layer bands and clip/hub settings intact.
The canonical print projects are never overwritten.
"""
from pathlib import Path
import importlib.util
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('quality', ROOT / 'tools/configure-local-quality.py')
quality = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quality)
OUT = ROOT / 'review/grooves-20261105'
OUT.mkdir(exist_ok=True)
source = ROOT / 'print/assembly-petg.3mf'
target = OUT / 'assembly-uniform-shells.3mf'
with zipfile.ZipFile(source) as z:
    data = {name: z.read(name) for name in z.namelist()}
model = ET.fromstring(data['3D/3dmodel.model'])
cfg = ET.fromstring(data['Metadata/model_settings.config'])
owned = {'201', '202', '203', '204'}
for obj in cfg.findall('object')[:2]:
    parts = obj.findall("part[@subtype='modifier_part']")
    assert len(parts) == 2 and all(p.get('id') in owned for p in parts)
    for part in parts:
        obj.remove(part)
    for key, value in quality.SPEEDS.items():
        quality.meta(obj, key, ','.join([value] * 6))
resources = model.find('{' + quality.NS + '}resources')
for obj in list(resources):
    if obj.get('id') in owned:
        resources.remove(obj)
    else:
        components = obj.find('{' + quality.NS + '}components')
        if components is not None:
            for c in list(components):
                if c.get('objectid') in owned:
                    components.remove(c)
quality.meta(cfg.find('plate'), 'plater_name', 'INJS2065 - uniform shell speeds - groove review')
data['3D/3dmodel.model'] = ET.tostring(model, encoding='utf-8', xml_declaration=True)
data['Metadata/model_settings.config'] = ET.tostring(cfg, encoding='utf-8', xml_declaration=True)
with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for name, content in data.items():
        z.writestr(name, content)
with zipfile.ZipFile(source) as a, zipfile.ZipFile(target) as b:
    assert b.testzip() is None
    for name in a.namelist():
        if name not in ('3D/3dmodel.model', 'Metadata/model_settings.config'):
            assert a.read(name) == b.read(name), name
    assert ET.tostring(ET.fromstring(a.read('3D/3dmodel.model')).find('{' + quality.NS + '}build')) == ET.tostring(model.find('{' + quality.NS + '}build'))
print(target)
