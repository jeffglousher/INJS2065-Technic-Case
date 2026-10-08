import subprocess,json,hashlib,time
from pathlib import Path
o=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-readiness-20261008')
s=o/'slice-final';s.mkdir(exist_ok=True)
exe=Path('C:/Program Files/Bambu Studio/bambu-studio.exe')
filament=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007/bambu-petg-basic-resolved.json')
cmd=[str(exe),'--load-filaments',str(filament),'--slice','1','--outputdir',str(s),'--export-settings',str(s/'resolved-settings.json'),str(o/'assembly-petg-hub-quality.3mf')]
print('Checking full five-part native Bambu slice...',flush=True)
p=subprocess.Popen(cmd,cwd=s,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
bounded=False
start=time.monotonic()
while True:
 try:
  stdout,stderr=p.communicate(timeout=10);break
 except subprocess.TimeoutExpired:
  if (s/'result.json').exists() and (s/'plate_1.gcode').exists():
   d=json.loads((s/'result.json').read_text())
   if d.get('return_code')==0:
    p.kill();stdout,stderr=p.communicate(timeout=10);bounded=True;break
  if time.monotonic()-start>150:
   p.kill();stdout,stderr=p.communicate(timeout=10)
   (s/'cli.log').write_bytes(stdout+stderr)
   raise RuntimeError('Native slicer did not finish within 150 seconds')
(s/'cli.log').write_bytes(stdout+stderr)
d=json.loads((s/'result.json').read_text());assert d['return_code']==0,d
project=json.loads((o/'assembly-project.json').read_text())
objects=d['sliced_plates'][0]['objects'];assert len(objects)==5
for intended,actual in zip(project['parts'],objects):
 assert actual['name']==intended['name'] and actual['triangle_count']==intended['triangles'],(intended,actual)
 assert abs(actual['bbox']['height']-intended['plate_bounds_mm'][2][1])<1e-5,(intended,actual)
assert d['sliced_plates'][0]['feature_type_times']['Support']>0
assert not d['sliced_plates'][0]['warning_message']
settings=json.loads((s/'resolved-settings.json').read_text());assert settings['filament_settings_id'][0]=='Bambu PETG Basic @BBL X2D 0.4 nozzle';assert settings['printer_settings_id']=='Bambu Lab X2D 0.4 nozzle';assert settings['layer_height']=='0.12'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
proof={'native_exit_code':p.returncode,'bounded_owned_child_shutdown':bounded,'elapsed_seconds':time.monotonic()-start,'native_result':d,'project_sha256':sha(o/'assembly-petg-hub-quality.3mf'),'gcode_sha256':sha(s/'plate_1.gcode'),'sliced_project_sha256':sha(s/'assembly-petg-sliced.3mf') if (s/'assembly-petg-sliced.3mf').exists() else None,'settings':{k:settings[k] for k in ['printer_settings_id','filament_settings_id','layer_height','wall_loops','sparse_infill_density','enable_support']},'print_sent':False}
(o/'native-slice.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(proof,indent=2),flush=True)

