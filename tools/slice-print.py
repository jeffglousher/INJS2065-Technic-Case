"""Slice and validate the current five-part project without contacting a printer."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def module(name):
    spec = importlib.util.spec_from_file_location(name.replace('-','_'), ROOT/'tools'/f'{name}.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

verify = module('verify-print')
audit = module('audit-toolpaths')

def main(binary, update):
    parts = verify.audit_project()
    path = ROOT/'docs/validation.json'
    evidence = json.loads(path.read_text())
    with tempfile.TemporaryDirectory(prefix='servo-holder-slice-') as folder:
        output = Path(folder)
        process = subprocess.run([str(binary),'--slice','1','--load-filaments',
            str(ROOT/'print/bambu-petg-basic.json'),'--outputdir',str(output),
            str(ROOT/evidence['project'])],capture_output=True,text=True,timeout=180,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        verify.check(process.returncode == 0, 'Slicer failed: '+(process.stdout+process.stderr)[-1500:])
        native = json.loads((output/'result.json').read_text())
        verify.check(native['return_code'] == 0 and len(native['sliced_plates']) == 1, 'Native slice failed')
        plate = native['sliced_plates'][0]
        verify.check(not plate['warning_message'] and len(plate['objects']) == 5, 'Native warnings/object count differ')
        gcode = output/'plate_1.gcode'
        rows = list(audit.segments(gcode))
        verify.check({r['object'] for r in rows} == {1,2,3,4,5}, 'Missing or extra printed object')
        absent = not any(any(s in r['feature'].lower() for s in ('support','brim','skirt')) for r in rows)
        solid = not any(r['object'] in (3,4) and r['feature']=='Sparse infill' for r in rows)
        verify.check(absent and solid, 'Support/brim/skirt or non-solid clips')
        probes=[]
        for obj,cy,expected in ((1,55,74),(2,175,181)):
            for x in (30.21,69.79):
                for y in (cy-5.2,cy+5.2):
                    layers={round(r['z'],5) for r in rows if r['object']==obj and r['feature']=='Outer wall'
                            and abs(r['a'][0]-x)<.002 and abs(r['b'][0]-x)<.002
                            and min(r['a'][1],r['b'][1])<y-.1 and max(r['a'][1],r['b'][1])>y+.1}
                    verify.check(len(layers)==expected, f'End-wall continuity differs at object {obj}, X{x}, Y{y}')
                    probes.append({'object':obj,'x_mm':x,'y_mm':y,'continuous_layers':len(layers)})
        heights={str(i):sorted({round(r['layer_height'],5) for r in rows if r['object']==i
                  and r['feature'] in ('Outer wall','Inner wall')}) for i in (1,2)}
        verify.check(heights == {'1':[.12,.16,.2],'2':[.12,.16,.2]}, 'Shell detail layer heights differ')
        verify.check(verify.sha(ROOT/evidence['project'])==evidence['project_sha256'], 'Project changed during slice')
        result={'gcode_sha256':hashlib.sha256(gcode.read_bytes()).hexdigest(),
                'supports_brims_skirts_absent':absent,'clips_slice_solid':solid,
                'shell_layer_heights_mm':heights,'end_wall_probes':probes}
    if update:
        evidence.update(parts=parts,native_slice=native,toolpaths=result,print_sent=False)
        path.write_text(json.dumps(evidence,indent=2)+'\n')
    print(f'PASS fresh five-part slice: {plate["total_predication"]:.2f} s, {plate["filaments"][0]["total_used_g"]:.2f} g; continuous end-wall probes; no supports/brims/skirts.')

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slicer',type=Path,default=Path('C:/Program Files/Bambu Studio/bambu-studio.exe'))
    parser.add_argument('--update-evidence',action='store_true')
    args=parser.parse_args()
    main(args.slicer,args.update_evidence)
