"""Apply the approved no-support/no-brim policy without altering mesh geometry."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PAINT = re.compile(rb'\s+paint_supports="[^"]*"')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def set_meta(parent, key, value):
    matches = [m for m in parent.findall('metadata') if m.get('key') == key]
    if matches:
        matches[0].set('value', value)
        for extra in matches[1:]:
            parent.remove(extra)
    else:
        ET.SubElement(parent, 'metadata', key=key, value=value)


def main():
    rows = []
    for filename in ['assembly-petg.3mf', 'fit-test-petg.3mf']:
        path = ROOT / 'print' / filename
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            payloads = {i.filename: archive.read(i.filename) for i in infos}
        settings = json.loads(payloads['Metadata/project_settings.config'])
        settings.update(enable_support='0', brim_type='no_brim', brim_width='0', skirt_loops='0')
        payloads['Metadata/project_settings.config'] = (json.dumps(settings, indent=2) + '\n').encode()
        cfg = ET.fromstring(payloads['Metadata/model_settings.config'])
        for obj in cfg.findall('object'):
            # Clear stale shell support parameters; retained hub bridge overrides are independent.
            for m in list(obj.findall('metadata')):
                key = m.get('key', '')
                if key.startswith('support_') or key == 'enable_support':
                    obj.remove(m)
            set_meta(obj, 'enable_support', '0')
            set_meta(obj, 'brim_type', 'no_brim')
            set_meta(obj, 'brim_width', '0')
        set_meta(cfg.find('plate'), 'plater_name', 'INJS2065 PETG - no supports or brims')
        payloads['Metadata/model_settings.config'] = ET.tostring(cfg, encoding='utf-8', xml_declaration=True)
        geometry = []
        for name, original in list(payloads.items()):
            if name.startswith('3D/Objects/') and name.endswith('.model'):
                clean = PAINT.sub(b'', original)
                # Vertex coordinates, triangle indices and all other mesh attributes remain byte-identical.
                assert b'paint_supports' not in clean
                payloads[name] = clean
                geometry.append({'mesh': name, 'geometry_without_support_paint_sha256': sha(clean),
                                 'geometry_unchanged': True})
        temporary = path.with_suffix('.3mf.tmp')
        with zipfile.ZipFile(temporary, 'w') as archive:
            for info in infos:
                archive.writestr(info, payloads[info.filename])
        with zipfile.ZipFile(temporary) as archive:
            assert archive.testzip() is None
            assert all(archive.read(name) == raw for name, raw in payloads.items())
        temporary.replace(path)
        rows.append({'project': 'print/' + filename, 'project_sha256': sha(path.read_bytes()), 'meshes': geometry})
    manifest_path = ROOT / 'review/current/files.json'
    manifest = json.loads(manifest_path.read_text())
    for row in rows:
        path = ROOT / row['project']
        manifest[row['project']] = {'bytes': path.stat().st_size, 'sha256': row['project_sha256']}
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    (ROOT / 'review/current/support-policy.json').write_text(json.dumps({
        'supports_enabled': False, 'brims_enabled': False, 'support_paint_removed': True,
        'cad_geometry_changed': False, 'projects': rows,
        'fallback_policy': 'If support is later authorized, use a confirmed PETG-compatible interface material on the auxiliary extruder; no material or nozzle assignment has been guessed.'
    }, indent=2) + '\n')
    print('Configured both projects with no supports, no brim/skirt, and no support paint; mesh geometry preserved.')


if __name__ == '__main__':
    main()
