import subprocess,json,hashlib,time
from pathlib import Path
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-layout-20261008');exe='C:/Program Files/Bambu Studio/bambu-studio.exe';filament='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007/bambu-petg-basic-resolved.json'
for name in ['assembly-petg-sequential-no-brim','assembly-petg-sequential-clip-quality']:
 d=out/name;d.mkdir(exist_ok=True)
 cmd=[exe,'--load-filaments',filament,'--slice','1','--outputdir',str(d),'--export-settings',str(d/'resolved-settings.json'),str(out/(name+'.3mf'))]
 p=subprocess.run(cmd,cwd=d,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=90)
 (d/'cli.log').write_bytes(p.stdout+p.stderr)
 if not (d/'result.json').exists():print(name,'No result',p.returncode,p.stderr[-1500:]);continue
 result=json.loads((d/'result.json').read_text());result['process_exit_code']=p.returncode;result['project_sha256']=hashlib.sha256((out/(name+'.3mf')).read_bytes()).hexdigest()
 if (d/'plate_1.gcode').exists():result['gcode_sha256']=hashlib.sha256((d/'plate_1.gcode').read_bytes()).hexdigest()
 (out/(name+'-slice.json')).write_text(json.dumps(result,indent=2))
 print(name,json.dumps(result,indent=2),flush=True)
