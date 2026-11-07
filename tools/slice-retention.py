"""Slice the retention trials and inspect actual extrusion paths; never sends a job."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/f'{name}.py')
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
audit=module('audit-toolpaths')
verify=module('verify-print')

def point_distance(row,point):
    a,b=row['a'],row['b'];dx,dy=b[0]-a[0],b[1]-a[1]
    if row['arc']:
        cx,cy=row['arc_center']
        start=math.atan2(a[1]-cy,a[0]-cx);end=math.atan2(b[1]-cy,b[0]-cx)
        angle=math.atan2(point[1]-cy,point[0]-cx)
        span=(start-end) % math.tau if row['clockwise'] else (end-start) % math.tau
        along=(start-angle) % math.tau if row['clockwise'] else (angle-start) % math.tau
        if along<=span+1e-8 or math.hypot(dx,dy)<1e-8:
            return abs(math.hypot(point[0]-cx,point[1]-cy)-math.hypot(a[0]-cx,a[1]-cy))
        return min(math.dist(point,a),math.dist(point,b))
    length=dx*dx+dy*dy
    t=max(0,min(1,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/length)) if length else 0
    return math.hypot(a[0]+t*dx-point[0],a[1]+t*dy-point[1])

def main(binary):
    path=ROOT/'docs/retention-validation.json';evidence=json.loads(path.read_text())
    for label,count in [('receivers',3),('clips',3),('holder',5)]:
        record=evidence['projects'][label];project=ROOT/record['path']
        verify.check(verify.sha(project)==record['sha256'],'Project changed since mesh validation')
        with tempfile.TemporaryDirectory(prefix='servo-retention-') as directory:
            out=Path(directory)
            p=subprocess.run([str(binary),'--slice','1','--load-filaments',str(ROOT/'print/bambu-petg-basic.json'),
                '--outputdir',str(out),str(project)],capture_output=True,text=True,timeout=180,
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            detail=(out/'result.json').read_text() if (out/'result.json').exists() else (p.stdout+p.stderr)[-2000:]
            verify.check(p.returncode==0,'Native slicer failed: '+detail)
            result=json.loads((out/'result.json').read_text())
            verify.check(result['return_code']==0 and len(result['sliced_plates'])==1,'Native plate failed')
            plate=result['sliced_plates'][0]
            verify.check(not plate['warning_message'] and len(plate['objects'])==count,'Native warnings or missing objects')
            gcode=out/'plate_1.gcode';rows=list(audit.segments(gcode))
            verify.check({r['object'] for r in rows}==set(range(1,count+1)),'Unexpected toolpath objects')
            verify.check(not any(any(k in r['feature'].lower() for k in ('support','brim','skirt')) for r in rows),'Unexpected support/brim/skirt')
            clips=(1,2,3) if label=='clips' else (3,4) if label=='holder' else ()
            verify.check(not any(r['object'] in clips and r['feature']=='Sparse infill' for r in rows),'Clip contains sparse infill')
            probes=[]
            if label=='clips':
                for obj,center_x,center_y,bottom in [(2,50,175,19),(3,150,55,19.2)]:
                    relevant=[r for r in rows if r['object']==obj and r['z']<=1.201]
                    layers=sorted({round(r['z'],5) for r in relevant})
                    verify.check(len(layers)>=6,'Insufficient backing layers')
                    for z0,z1 in [(bottom-.6,bottom),(20.2,20.8)]:
                        point=(center_x-6.525,center_y+(z0+z1)/2-18.25)
                        distance=min(point_distance(r,point) for r in relevant)
                        verify.check(distance>.19,f'Slicer bridges flex slot in object {obj}: {distance}')
                        probes.append({'object':obj,'slot_center_xy_mm':point,'minimum_extrusion_center_distance_mm':distance,'layers_checked':len(layers)})
                    # Each backing layer must retain a continuous long path through the arm.
                    for layer in layers:
                        continuous=any(not r['arc'] and abs(r['z']-layer)<1e-5 and abs(r['a'][1]-r['b'][1])<.01
                            and min(r['a'][0],r['b'][0])<center_x-7 and max(r['a'][0],r['b'][0])>center_x-6
                            and center_y+bottom-18.25<r['a'][1]<center_y+20.2-18.25 for r in relevant)
                        verify.check(continuous,f'Beam continuity missing at object {obj}, Z{layer}')
            elif label=='holder':
                # Preserve the groove fix: continuous end walls on complete shells.
                for obj,cy,expected in ((1,55,74),(2,175,181)):
                    for x in (30.21,69.79):
                        for y in (cy-5.2,cy+5.2):
                            layers={round(r['z'],5) for r in rows if r['object']==obj and r['feature']=='Outer wall'
                                and abs(r['a'][0]-x)<.002 and abs(r['b'][0]-x)<.002
                                and min(r['a'][1],r['b'][1])<y-.1 and max(r['a'][1],r['b'][1])>y+.1}
                            verify.check(len(layers)==expected,f'End-wall continuity differs at {obj}, {x}, {y}')
                            probes.append({'object':obj,'xy_mm':[x,y],'continuous_layers':len(layers)})
            record['native_slice']=result
            record['toolpaths']={'gcode_sha256':hashlib.sha256(gcode.read_bytes()).hexdigest(),
                'no_support_brim_skirt':True,'clips_solid':True,'probes':probes}
            print(f'PASS {label}: {plate["total_predication"]:.2f} s, {plate["filaments"][0]["total_used_g"]:.2f} g',flush=True)
    path.write_text(json.dumps(evidence,indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slicer',type=Path,default=Path('C:/Program Files/Bambu Studio/bambu-studio.exe'))
    main(parser.parse_args().slicer)
