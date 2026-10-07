import json,struct,zipfile,re,subprocess,hashlib,sys
from pathlib import Path
r=Path(__file__).parent;template=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/local-corner-flex-20261005/petg-classic-012/petg-classic-012.3mf');flat=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007/bambu-petg-basic-resolved.json')
settings=json.loads(Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007/petg-classic-012/resolved-settings.json').read_text());base={n:zipfile.ZipFile(template).read(n) for n in zipfile.ZipFile(template).namelist()};records=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in (sys.argv[1:] or ['clip-fine','lower-fine','upper-fine']):
    raw=(r/(name+'.stl')).read_bytes();count=struct.unpack_from('<I',raw,80)[0];vv=[];tt=[];lookup={}
    for i in range(count):
        tri=[]
        for k in range(3):
            x,y,z=struct.unpack_from('<fff',raw,84+50*i+12+12*k)
            p=(x-6.525,z-18.25,12-y) if name.startswith('clip') else ((x-8,y,z-8) if name.startswith('lower') else (x-8,-y,42-z))
            if p not in lookup:lookup[p]=len(vv);vv.append(p)
            tri.append(lookup[p])
        tt.append(tri)
    mesh='<mesh><vertices>'+''.join(f'<vertex x="{x:.9f}" y="{y:.9f}" z="{z:.9f}"/>' for x,y,z in vv)+'</vertices><triangles>'+''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in tt)+'</triangles></mesh>'
    entries=base.copy();entries['3D/Objects/object_1.model']=('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources><object id="1" type="model">'+mesh+'</object></resources></model>').encode()
    config=settings.copy();config['layer_height']='0.12';config['wall_loops']='4';entries['Metadata/project_settings.config']=json.dumps(config).encode();directory=r/name;directory.mkdir(exist_ok=True);project=directory/(name+'.3mf')
    with zipfile.ZipFile(project,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for n,data in entries.items():z.writestr(n,data)
    command=['C:/Program Files/Bambu Studio/bambu-studio.exe','--load-filaments',str(flat),'--slice','1','--outputdir',str(directory),'--export-settings',str(directory/'resolved-settings.json'),str(project)]
    native_complete=False;bounded_shutdown=False
    process=subprocess.Popen(command,cwd=directory,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        stdout,stderr=process.communicate(timeout=25);result_code=process.returncode
    except subprocess.TimeoutExpired:
        native=json.loads((directory/'result.json').read_text()) if (directory/'result.json').exists() else {}
        assert native.get('return_code')==0 and (directory/'plate_1.gcode').exists(),native
        process.kill();stdout,stderr=process.communicate(timeout=10);result_code=process.returncode;bounded_shutdown=True
    (directory/'cli.log').write_bytes(stdout+stderr)
    native=json.loads((directory/'result.json').read_text());assert native['return_code']==0
    effective=json.loads((directory/'resolved-settings.json').read_text());assert effective['filament_settings_id'][0]=='Bambu PETG Basic @BBL X2D 0.4 nozzle';assert effective['printer_settings_id']=='Bambu Lab X2D 0.4 nozzle';assert effective['layer_height']=='0.12'
    rr={'part':name,'mesh_sha256':sha(r/(name+'.stl')),'source_project_sha256':sha(project),'triangles':count,'native_exit_code':result_code,'bounded_owned_child_shutdown_after_successful_slicing':bounded_shutdown,'gcode_sha256':sha(directory/'plate_1.gcode'),'native_result':json.loads((directory/'result.json').read_text()),'effective_settings':{k:effective[k] for k in ['filament_settings_id','filament_flow_ratio','filament_max_volumetric_speed','nozzle_temperature','nozzle_temperature_initial_layer','printer_settings_id','layer_height','wall_loops','wall_generator']},'print_sent':False};records.append(rr);print(name,rr['native_exit_code'],rr['gcode_sha256'],flush=True)
if (r/'native-slicing.json').exists():
    previous=json.loads((r/'native-slicing.json').read_text());records+=[v for v in previous['cases'] if v['part'] not in {x['part'] for x in records}]
(r/'native-slicing.json').write_text(json.dumps({'cases':records,'filament_profile_sha256':sha(flat),'native_executable_sha256':sha(Path(command[0]))},indent=2))
