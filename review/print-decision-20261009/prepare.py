"""Prepare a clearly labeled, geometry-preserving PETG assembly for user review.

Only project/plate labels change. Native slicing stays local and sends no job.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'review/retention-fit-20261009/assembly-fit-candidate.3mf'
FIT = ROOT / 'review/contact-fix-20261009/registered-receivers.3mf'
OUT = Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-decision-20261009')
CANONICAL_SHA = '19a73dd1a82072cfbd80a95da27a19720c7a09fef52b39dab940d3c3ec4ec340'
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(ROOT / 'design/current.model.json') == CANONICAL_SHA
previous = json.loads(SOURCE.with_name('assembly-fit-candidate-audit.json').read_text())
assert sha(SOURCE) == previous['project_sha256']
with zipfile.ZipFile(SOURCE) as archive:
    original = {name: archive.read(name) for name in archive.namelist()}
data = original.copy()
ET.register_namespace('', NS)
ET.register_namespace('p', 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
main = ET.fromstring(data['3D/3dmodel.model'])
for meta in main.findall('{' + NS + '}metadata'):
    if meta.get('name') == 'Title':
        meta.text = 'INJS2065 full PETG assembly - user print decision - geometry 613402c'
main.set('xmlns:BambuStudio', 'http://schemas.bambulab.com/package/2021')
cfg = ET.fromstring(data['Metadata/model_settings.config'])
for meta in cfg.findall('plate/metadata'):
    if meta.get('key') == 'plater_name':
        meta.set('value', 'Complete assembly - PETG - awaiting user go/no-go')
data['3D/3dmodel.model'] = ET.tostring(main, encoding='utf-8', xml_declaration=True)
data['Metadata/model_settings.config'] = ET.tostring(cfg, encoding='utf-8', xml_declaration=True)
assert len(main.find('{' + NS + '}build')) == 5
assert len(cfg.findall('object')) == 5
settings = json.loads(data['Metadata/project_settings.config'])
assert settings['printer_settings_id'] == 'Bambu Lab X2D 0.4 nozzle'
assert settings['filament_settings_id'] == ['Bambu PETG Basic @BBL X2D 0.4 nozzle']
assert settings['print_sequence'] == 'by object'
project = HERE / 'assembly-petg-review.3mf'
with zipfile.ZipFile(project, 'w', zipfile.ZIP_DEFLATED) as archive:
    for name, raw in data.items():
        archive.writestr(name, raw)
with zipfile.ZipFile(project) as archive:
    assert set(archive.namelist()) == set(original)
    for name in original:
        if name not in ['3D/3dmodel.model', 'Metadata/model_settings.config']:
            assert archive.read(name) == original[name], name
old_main = ET.fromstring(original['3D/3dmodel.model'])
assert ET.tostring(old_main.find('{' + NS + '}build')) == ET.tostring(main.find('{' + NS + '}build'))
assert ET.tostring(old_main.find('{' + NS + '}resources')) == ET.tostring(main.find('{' + NS + '}resources'))
old_cfg = ET.fromstring(original['Metadata/model_settings.config'])
assert [ET.tostring(obj) for obj in cfg.findall('object')] == [ET.tostring(obj) for obj in old_cfg.findall('object')]
OUT.mkdir(parents=True, exist_ok=True)
command = [
    'C:/Program Files/Bambu Studio/bambu-studio.exe', '--load-filaments',
    'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007/bambu-petg-basic-resolved.json',
    '--slice', '1', '--outputdir', str(OUT), '--export-settings', str(OUT / 'resolved-settings.json'), str(project),
]
run = subprocess.run(command, cwd=OUT, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=180)
(OUT / 'cli.log').write_bytes(run.stdout + run.stderr)
result = json.loads((OUT / 'result.json').read_text())
assert run.returncode == result['return_code'] == 0, result
assert not result['sliced_plates'][0]['warning_message'], result
assert len(result['sliced_plates'][0]['objects']) == 5
fit_audit = json.loads(FIT.with_name('registered-receivers-audit.json').read_text())
assert sha(FIT) == fit_audit['project_sha256']
overrides = {obj.get('id'): {m.get('key'): m.get('value') for m in obj.findall('metadata') if m.get('key')} for obj in cfg.findall('object')}
receipt = {
    'canonical_sha256': CANONICAL_SHA, 'canonical_geometry_changed': False,
    'source_project_sha256': sha(SOURCE), 'project_sha256': sha(project),
    'all_mesh_payloads_byte_identical': True, 'build_transforms_identical': True,
    'object_overrides_identical': True, 'project_settings_byte_identical': True,
    'only_changes': ['main project Title', 'plate plater_name', 'XML serialization and ZIP packaging'],
    'native_result': result, 'gcode_sha256': sha(OUT / 'plate_1.gcode'),
    'registered_fit_project_sha256': sha(FIT), 'object_metadata': overrides,
    'prepared_by_script_sha256': sha(Path(__file__)), 'print_sent': False,
    'mechanical_qualification': 'Not established; numerical contact experiment rejected. User decides go/no-go.',
}
(HERE / 'package-audit.json').write_text(json.dumps(receipt, indent=2) + '\n')
plate = result['sliced_plates'][0]
print(json.dumps({'native_slice': 'pass', 'warnings': plate['warning_message'], 'parts': len(plate['objects']),
    'seconds': plate['total_predication'], 'grams': plate['filaments'][0]['total_used_g'], 'geometry_changed': False}))
