"""Fresh native slices: clearance, single filament, preserved layer schedules and flex slots."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'tools'/f'{name}.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    audit, probe = module('audit-toolpaths'), module('slice-retention')
    evidence_path = ROOT/'docs/retention-complete-validation.json'
    evidence = json.loads(evidence_path.read_text())
    combined = ROOT/evidence['path']
    assert hashlib.sha256(combined.read_bytes()).hexdigest() == evidence['sha256'], 'Combined project changed'
    slices = {}
    for label, project in [('receivers', ROOT/'print/retention/coupons-receivers.3mf'),
                           ('clips', ROOT/'print/retention/coupons-clips.3mf'),
                           ('complete', combined)]:
        if label != 'complete':
            assert hashlib.sha256(project.read_bytes()).hexdigest() == evidence['source_project_sha256'][label], 'Source changed'
        with tempfile.TemporaryDirectory(prefix='coupon-check-', dir=ROOT/'local/retention') as tmp:
            run = subprocess.run(['C:/Program Files/Bambu Studio/bambu-studio.exe', '--slice', '1',
                                  '--load-filaments', str(ROOT/'print/bambu-petg-basic.json'),
                                  '--outputdir', tmp, str(project)], capture_output=True, text=True, timeout=180,
                                 creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            assert run.returncode == 0, run.stderr[-2000:]
            result = json.loads((Path(tmp)/'result.json').read_text())
            assert result['return_code'] == 0 and len(result['sliced_plates']) == 1, result
            plate = result['sliced_plates'][0]
            assert not plate['warning_message'], plate['warning_message']
            assert len(plate['objects']) == (6 if label == 'complete' else 3), 'Object missing'
            assert len(plate['filaments']) == 1 and plate['filament_change_times'] == 0, 'Multiple filaments'
            gcode = Path(tmp)/'plate_1.gcode'
            slices[label] = list(audit.segments(gcode))
            if label == 'complete':
                evidence['native_slice'] = result
                evidence['gcode_sha256'] = hashlib.sha256(gcode.read_bytes()).hexdigest()
    rows = slices['complete']
    assert {r['object'] for r in rows} == set(range(1, 7)), 'Unexpected extrusion objects'
    assert not any(any(k in r['feature'].lower() for k in ('support', 'skirt')) for r in rows), 'Support/skirt appeared'
    assert {r['object'] for r in rows if 'brim' in r['feature'].lower()} == {1, 2, 3}, 'Receiver-only brims changed'
    assert not any(r['object'] >= 4 and r['feature'] == 'Sparse infill' for r in rows), 'Clip not solid'
    checks = []
    for part in evidence['parts']:
        index = part['object']
        current = [r for r in rows if r['object'] == index and 'brim' not in r['feature'].lower()]
        source = [r for r in slices[part['source']] if r['object'] == part['source_object'] and 'brim' not in r['feature'].lower()]
        schedule = lambda paths: sorted({(round(r['z'], 5), round(r['layer_height'], 5)) for r in paths})
        assert schedule(current) == schedule(source), f'Layer phase changed on {index}'
        checks.append({'object': index, 'layer_schedule_matches_source': True, 'extrusion_layer_count': len(schedule(current))})
    for index, cy, bottom in [(5, 128, 19.0), (6, 216, 19.2)]:
        relevant = [r for r in rows if r['object'] == index and r['z'] <= 1.201]
        for low, high in [(bottom-.6, bottom), (20.2, 20.8)]:
            point = (180-6.525, cy+(low+high)/2-18.25)
            distance = min(probe.point_distance(r, point) for r in relevant)
            assert distance > .19, f'Flex slot bridged on {index}'
            checks.append({'object': index, 'slot_center_xy_mm': point, 'extrusion_center_distance_mm': distance})
        for layer in {round(r['z'], 5) for r in relevant}:
            assert any(not r['arc'] and abs(r['z']-layer) < 1e-5 and abs(r['a'][1]-r['b'][1]) < .01
                       and min(r['a'][0], r['b'][0]) < 173 and max(r['a'][0], r['b'][0]) > 174
                       and cy+bottom-18.25 < r['a'][1] < cy+20.2-18.25 for r in relevant), f'Beam broken on {index}'
    evidence['toolpath_checks'] = checks
    evidence['status'] = 'native checks passed; physical fit and retention unaccepted'
    evidence_path.write_text(json.dumps(evidence, indent=2)+'\n')
    plate = evidence['native_slice']['sliced_plates'][0]
    print(f'PASS: six objects, one filament, no warnings, original layer phases, receiver-only brims, solid clips, open slots and continuous tongues; {plate["total_predication"]:.1f}s, {plate["filaments"][0]["total_used_g"]:.2f}g')


if __name__ == '__main__':
    main()
