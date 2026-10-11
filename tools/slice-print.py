"""Slice both canonical projects and verify actual rail paths; optionally refresh evidence."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'review/current'


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / 'tools' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify = load_tool('verify-print')
audit = load_tool('audit-local-quality')


def slice_project(binary, project, output, count):
    output.mkdir()
    process = subprocess.run([str(binary), '--slice', '1', '--load-filaments',
                              str(ROOT / 'print/bambu-petg-basic.json'), '--outputdir', str(output),
                              str(project)], capture_output=True, text=True, timeout=180,
                             creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    verify.check(process.returncode == 0, f'Slicer failed: {(process.stderr + process.stdout)[-2000:]}')
    native = json.loads((output / 'result.json').read_text(encoding='utf-8'))
    verify.check(native['return_code'] == 0 and len(native['sliced_plates']) == 1, 'Native failure')
    plate = native['sliced_plates'][0]
    verify.check(not plate['warning_message'] and len(plate['objects']) == count,
                 'Native warning or object count mismatch')
    return native, audit.audit(output / 'plate_1.gcode')


def part_paths(rows, object_id):
    def signature(s):
        r = lambda v: round(v, 5)
        return (s['feature'], tuple(map(r,s['a'])), tuple(map(r,s['b'])), r(s['z']),
                r(s['width']), r(s['e']), r(s['speed']), s['arc'],
                tuple(map(r,s['arc_center'])) if s['arc_center'] else (), s['clockwise'])
    return Counter(signature(s) for s in rows if s['object'] == object_id and s['feature'] != 'Custom')


def paths_sha(counter):
    return hashlib.sha256(json.dumps(sorted(counter.items()), separators=(',',':')).encode()).hexdigest()


def validate_paths(data, rows, object_count):
    verify.check(data['supports_brims_skirts_absent'], 'Support/brim/skirt extrusion found')
    verify.check({s['object'] for s in rows if s['feature'] != 'Custom'} == set(range(1, object_count + 1)),
                 'Missing or unexpected printed object')
    verify.check(data['shell_layer_heights_mm'] == {'1':[.12,.16,.2], '2':[.12,.16,.2]},
                 'Unexpected shell layer heights')
    stats = data['rail_stats']
    for feature, maximum in [('Inner wall',45), ('Gap infill',30), ('Internal solid infill',45), ('Top surface',30)]:
        verify.check(feature in stats and stats[feature]['speed_max_mm_s'] <= maximum + .001,
                     f'{feature}: rail speed limit exceeded')
    verify.check(stats['Outer wall']['speed_median_mm_s'] == 30
                 and stats['Outer wall']['speed_max_mm_s'] <= 40.001,
                 'Outer-wall speeds differ from reviewed smoothing envelope')
    verify.check(not any(s['object'] in (3,4) and s['feature'] == 'Sparse infill' for s in rows),
                 'Clips no longer slice solid')


def run(binary, update, baseline_ref):
    manifest = json.loads((REVIEW / 'files.json').read_text(encoding='utf-8'))
    for name, record in manifest.items():
        verify.check(verify.sha(ROOT / name) == record['sha256'], f'Canonical file changed: {name}')
    quality = json.loads((REVIEW / 'local-quality-check.json').read_text(encoding='utf-8'))
    records = []
    receipts = {}
    with tempfile.TemporaryDirectory(prefix='injs-slice-') as temporary:
        output_root = Path(temporary).resolve()
        verify.check(output_root.parent == Path(tempfile.gettempdir()).resolve(), 'Unexpected temporary directory')
        baseline_bytes = baseline_rows = None
        if baseline_ref:
            baseline_ref = subprocess.check_output(['git','rev-parse',baseline_ref], cwd=ROOT, text=True).strip()
            baseline_bytes = subprocess.check_output(['git','show',f'{baseline_ref}:print/assembly-petg.3mf'], cwd=ROOT)
            baseline = output_root / 'baseline.3mf'
            baseline.write_bytes(baseline_bytes)
            _, (_, baseline_rows) = slice_project(binary, baseline, output_root / 'baseline', 5)
        for name, count, receipt_name in [('assembly-petg',5,'assembly-slice.json'),
                                          ('fit-test-petg',4,'fit-test-slice.json')]:
            project = verify.audit_project(name + '.3mf', count)
            native, (data, rows) = slice_project(binary, ROOT / project['file'], output_root / name, count)
            plate = native['sliced_plates'][0]
            validate_paths(data, rows, count)
            old = next(r for r in quality['projects'] if r['project'] == project['file'])
            verify.check(old['project_sha256'] == project['project_sha256'], 'Comparison evidence is for another project')
            verify.check(data['rail_stats'] == old['rail_stats'], 'Actual rail paths differ from reviewed evidence')
            verify.check(verify.sha(ROOT / project['file']) == project['project_sha256'], 'Project changed during slice')
            if baseline_bytes is not None:
                with zipfile.ZipFile(io.BytesIO(baseline_bytes)) as before, zipfile.ZipFile(ROOT / project['file']) as after:
                    for i in range(1, count + 1):
                        payload = f'3D/Objects/object_{i}.model'
                        verify.check(before.read(payload) == after.read(payload), 'Printable mesh changed from baseline')
                    b = verify.ET.fromstring(before.read('3D/3dmodel.model')).find(verify.NS + 'build')
                    a = verify.ET.fromstring(after.read('3D/3dmodel.model')).find(verify.NS + 'build')
                    verify.check([n.attrib for n in a] == [n.attrib for n in b][:count], 'Print placements changed')
            fingerprints = {}
            for i in range(3, count + 1):
                actual = part_paths(rows,i)
                expected = paths_sha(part_paths(baseline_rows,i)) if baseline_rows is not None else old.get('non_shell_toolpath_sha256',{}).get(str(i))
                fingerprints[str(i)] = paths_sha(actual)
                verify.check(expected is not None, 'No accepted path fingerprint; supply the reviewed --baseline-ref')
                verify.check(fingerprints[str(i)] == expected, 'Clip/hub extrusion changed from baseline')
            record = dict(old, **data)
            record.update(non_shell_extrusions_match_baseline={str(i):True for i in range(3,count+1)},
                          non_shell_toolpath_sha256=fingerprints, printable_meshes_and_placements_unchanged=True,
                          baseline_commit=baseline_ref or old['baseline_commit'])
            records.append(record)
            receipts[receipt_name] = {
                'project_sha256':project['project_sha256'], 'gcode_sha256':data['gcode_sha256'],
                'native_result':native, 'supports_absent':True, 'brims_skirts_absent':True,
                'clips_slice_solid':True, 'local_quality_validated':True, 'print_sent':False,
            }
            print(f'PASS {name}: actual rail paths/layers match; {plate["total_predication"]:.2f} s; no supports/brims/skirts.', flush=True)
    if update:
        quality.update(passed=True, projects=records)
        receipts['local-quality-check.json'] = quality
        receipts['toolpath-check.json'] = {
            'supports_absent':True, 'brims_skirts_absent':True, 'print_sent':False,
            'projects':[{key:r[key] for key in ('project','project_sha256','gcode_sha256',
                                              'supports_brims_skirts_absent','shell_layer_heights_mm')} for r in records],
            'local_quality_evidence':'local-quality-check.json',
            'limits':'Commanded paths and sliceability checked; no measured fit, surface finish or mechanical qualification.',
        }
        # Both projects must pass before any consolidated evidence is replaced.
        for filename, receipt in receipts.items():
            path = REVIEW / filename
            staging = path.with_suffix('.tmp')
            staging.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
            staging.replace(path)
        verify.main()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slicer', type=Path, default=Path('C:/Program Files/Bambu Studio/bambu-studio.exe'))
    parser.add_argument('--update-evidence', action='store_true', help='Refresh matching receipts after both slices pass')
    parser.add_argument('--baseline-ref', help='Recheck clip/hub paths against a reviewed Git commit; otherwise use saved fingerprints')
    args = parser.parse_args()
    run(args.slicer.resolve(), args.update_evidence, args.baseline_ref)
