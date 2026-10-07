"""Native isolated slicing with resolved installed Bambu PETG Basic preset.

No printer connection or user-project writes. Machine/process/mesh stay inherited
from the reviewed 3MF; native CLI replaces the filament settings explicitly.
"""
import hashlib,json,subprocess
from pathlib import Path
profiles=Path('C:/Program Files/Bambu Studio/resources/profiles/BBL/filament')
source=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/local-corner-flex-20261005')
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007')
report_dir=Path(__file__).resolve().parent
out.mkdir(parents=True,exist_ok=True);read_files={}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(name,stack=()):
    assert name not in stack,(name,stack)
    path=profiles/(name+'.json');data=json.loads(path.read_text());read_files[str(path)]=sha(path)
    result=resolve(data['inherits'],stack+(name,)) if data.get('inherits') else {}
    for include in data.get('include',[]):result.update(resolve(include,stack+(name,)))
    result.update({k:v for k,v in data.items() if k not in ('inherits','include')})
    return result
filament=resolve('Bambu PETG Basic @BBL X2D 0.4 nozzle')
flat=out/'bambu-petg-basic-resolved.json';flat.write_text(json.dumps(filament,indent=2))
manifest={'filament_name':filament['name'],'resolved_preset_sha256':sha(flat),'preset_source_sha256':read_files,'native_executable':'C:/Program Files/Bambu Studio/bambu-studio.exe','native_executable_sha256':sha(Path('C:/Program Files/Bambu Studio/bambu-studio.exe')),'print_sent':False,'cases':[]}
for name in ('petg-classic-016','petg-classic-012'):
    directory=out/name;directory.mkdir(exist_ok=True)
    original=source/name/(name+'.3mf')
    command=[manifest['native_executable'],'--load-filaments',str(flat),'--slice','1','--outputdir',str(directory),'--export-settings',str(directory/'resolved-settings.json'),str(original)]
    result=subprocess.run(command,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    (directory/'cli.log').write_bytes(result.stdout+result.stderr)
    record={'case':name,'source_project_sha256':sha(original),'command':command,'exit_code':result.returncode}
    if (directory/'result.json').exists():record['native_result']=json.loads((directory/'result.json').read_text())
    print(json.dumps({'case':name,'exit':result.returncode,'files':[p.name for p in directory.iterdir()]}),flush=True)
    assert result.returncode==0,(record,(result.stdout+result.stderr)[-2000:])
    assert (directory/'plate_1.gcode').exists(),record
    settings=json.loads((directory/'resolved-settings.json').read_text())
    assert settings['filament_settings_id'][0]=='Bambu PETG Basic @BBL X2D 0.4 nozzle',settings['filament_settings_id']
    assert settings['printer_settings_id']=='Bambu Lab X2D 0.4 nozzle'
    record.update(gcode_sha256=sha(directory/'plate_1.gcode'),resolved_settings_sha256=sha(directory/'resolved-settings.json'),effective_settings={k:settings[k] for k in ['filament_settings_id','filament_vendor','filament_density','filament_flow_ratio','filament_max_volumetric_speed','nozzle_temperature','nozzle_temperature_initial_layer','printer_settings_id','layer_height','wall_generator','outer_wall_line_width']})
    manifest['cases'].append(record)
(report_dir/'native-basic-slicing.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'material':manifest['filament_name'],'cases':[{k:r[k] for k in ('case','exit_code','gcode_sha256','effective_settings')} for r in manifest['cases']]}),flush=True)
