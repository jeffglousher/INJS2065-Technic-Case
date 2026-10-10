"""Native hub-only bridge-setting trials; never sends a print."""
from pathlib import Path
import ast, hashlib, json, math, re, subprocess, zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hub-bridge-20261010')
SOURCE=ROOT/'review/hub-orientation-20261010/flipped-no-support.3mf'
FILAMENT=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007/bambu-petg-basic-resolved.json')
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ROOT/'design/current.model.json')=='19a73dd1a82072cfbd80a95da27a19720c7a09fef52b39dab940d3c3ec4ec340'
audit=json.loads((SOURCE.parent/'comparison.json').read_text())
assert sha(SOURCE)==audit['flipped-no-support']['project_sha256']
with zipfile.ZipFile(SOURCE) as z:original={n:z.read(n) for n in z.namelist()}
old_cfg=ET.fromstring(original['Metadata/model_settings.config'])
base_hub=next(o for o in old_cfg.findall('object') if o.get('id')=='105')

# Reuse the recorded geometric path parser without executing its slice workflow.
parser_source=(ROOT/'review/hub-orientation-20261010/compare.py').read_text()
function=next(n for n in ast.parse(parser_source).body if isinstance(n,ast.FunctionDef) and n.name=='paths')
parser_text=ast.get_source_segment(parser_source,function)
parser_text=parser_text.replace('E=0.)','E=0.,F=0.)').replace("e=extruded,points=points","e=extruded,points=points,speed_mm_s=pos['F']/60,fan=fan")
parser_text=parser_text.replace("out.append(dict(feature", "\n        if len(points)==2:\n            a,b=points;count=max(1,math.ceil(math.dist(a,b)/.04))\n            points=[(a[0]+(b[0]-a[0])*j/count,a[1]+(b[1]-a[1])*j/count) for j in range(count+1)]\n        out.append(dict(feature")
parser_text=parser_text.replace("out=[]","out=[];fan=None")
parser_text=parser_text.replace("cmd=line.split(';',1)[0].strip()", "cmd=line.split(';',1)[0].strip()\n        if cmd.startswith('M106 '):\n            fv={k:float(v) for k,v in re.findall(r'([PS])([-+]?[0-9.]+)',cmd)}\n            if fv.get('P',1)==1:fan=fv.get('S',0)\n        if cmd.startswith('M107'):fan=0")
exec(compile(parser_text,'<recorded-hub-path-parser>','exec'))

def summary(gcode):
    q=paths(gcode)
    b=[p for p in q if p['feature']=='Bridge']
    assert not any(p['feature'] in ('Support','Support interface','Sparse infill') for p in q)
    interior=[p for p in q if .25<p['z']<3.40 and any(math.hypot(x,y)<2.55 for x,y in p['points'])]
    assert not interior,'Hub model intrudes into conservative servo interior'
    floor=[p for p in q if p['feature'] not in ('Skirt','Brim') and any(math.hypot(x,y)<2.55 for x,y in p['points'])]
    return {'bridge_z_mm':sorted(set(round(p['z'],5) for p in b)),
        'bridge_height_mm':sorted(set(p['height'] for p in b)),
        'bridge_width_mm':sorted(set(p['width'] for p in b)),
        'bridge_speed_mm_s':sorted(set(round(p['speed_mm_s'],4) for p in b)),
        'bridge_part_fan_command_255':sorted(set(p['fan'] for p in b)),
        'bridge_extruded_filament_mm':sum(p['e'] for p in b),
        'bridge_extrusion_segments':len(b),
        'servo_floor_first_nozzle_z_mm':min(p['z'] for p in floor),
        'servo_floor_first_features':sorted(set(p['feature'] for p in floor if abs(p['z']-min(p['z'] for p in floor))<1e-5)),
        'supports':False,'sparse_infill':False,'conservative_servo_interior_centerline_hits':len(interior)}

baseline_gcode=OUT.parent/'hub-orientation-20261010/flipped-no-support/plate_1.gcode'
assert sha(baseline_gcode)==audit['flipped-no-support']['gcode_sha256']
results={'baseline':{'toolpaths':summary(baseline_gcode)}}
cases={
    'thin-flow-090':{'bridge_flow':'0.9','thick_bridges':'0','bridge_speed':'25','bridge_no_support':'1','counterbore_hole_bridging':'none'},
    'thick-flow-090':{'bridge_flow':'0.9','thick_bridges':'1','bridge_speed':'25','bridge_no_support':'1','counterbore_hole_bridging':'none'},
    'counterbore-partial':{'counterbore_hole_bridging':'partiallybridge'},
    'counterbore-sacrificial':{'counterbore_hole_bridging':'sacrificiallayer'},
}
for mode,overrides in cases.items():
    data=original.copy();cfg=ET.fromstring(data['Metadata/model_settings.config'])
    hub=next(o for o in cfg.findall('object') if o.get('id')=='105')
    for key,value in overrides.items():
        m=next((m for m in hub.findall('metadata') if m.get('key')==key),None)
        if m is None:m=ET.SubElement(hub,'metadata',{'key':key})
        m.set('value',value)
    for m in cfg.findall('plate/metadata'):
        if m.get('key')=='plater_name':m.set('value','Full PETG assembly - hub '+mode)
    data['Metadata/model_settings.config']=ET.tostring(cfg,encoding='utf-8',xml_declaration=True)
    # The entire project is preserved except declared hub overrides and plate label.
    restored=ET.fromstring(data['Metadata/model_settings.config'])
    restored_hub=next(o for o in restored.findall('object') if o.get('id')=='105')
    for key in overrides:
        m=next(m for m in restored_hub.findall('metadata') if m.get('key')==key)
        old=next((m for m in base_hub.findall('metadata') if m.get('key')==key),None)
        if old is None:restored_hub.remove(m)
        else:m.set('value',old.get('value'))
    for m in restored.findall('plate/metadata'):
        if m.get('key')=='plater_name':m.set('value',next(m.get('value') for m in old_cfg.findall('plate/metadata') if m.get('key')=='plater_name'))
    assert ET.tostring(restored)==ET.tostring(old_cfg)
    assert all(data[n]==original[n] for n in data if n!='Metadata/model_settings.config')
    project=OUT/(mode+'.3mf')
    with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED) as z:
        for n,raw in data.items():z.writestr(n,raw)
    folder=OUT/mode;folder.mkdir(exist_ok=True)
    command=['C:/Program Files/Bambu Studio/bambu-studio.exe','--load-filaments',str(FILAMENT),'--slice','1','--outputdir',str(folder),'--export-settings',str(folder/'resolved.json'),str(project)]
    run=subprocess.run(command,cwd=folder,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=180)
    (folder/'cli.log').write_bytes(run.stdout+run.stderr)
    result=json.loads((folder/'result.json').read_text());plate=result['sliced_plates'][0]
    assert run.returncode==result['return_code']==0 and len(plate['objects'])==5 and not plate['warning_message']
    q=paths(folder/'plate_1.gcode')
    results[mode]={'overrides':overrides,'project_sha256':sha(project),'gcode_sha256':sha(folder/'plate_1.gcode'),
        'native_result':result,'toolpaths':summary(folder/'plate_1.gcode'),
        'baseline_hub_paths_identical':q==paths(baseline_gcode),
        'meshes_and_placements_unchanged':True,'global_and_other_object_settings_unchanged':True,'print_sent':False}
    print(mode,json.dumps(results[mode]['toolpaths']),flush=True)
receipt={'source_project_sha256':sha(SOURCE),'script_sha256':sha(Path(__file__)),
    'source_tag':{'name':'v02.08.02.61','commit':{'sha':'926a7192574bcb9b3a732e1ec59a46d79cb45466'}},'cases':results}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n')
(HERE/'assembly-petg-bridge-tuned.3mf').write_bytes((OUT/'thin-flow-090.3mf').read_bytes())
