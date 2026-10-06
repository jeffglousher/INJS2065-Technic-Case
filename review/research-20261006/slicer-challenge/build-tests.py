import json, struct, zipfile, re
from pathlib import Path
root=Path(r'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005')
template=Path(r'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/history-cleanup-20261004/archive/reviews/ridge-centered-detents-20261004/nozzle-designed-scurve/bambu-check/X2D-PETG-SCurve.3mf')
petg=json.loads((root/'petg-settings.json').read_text()); pla=json.loads((root/'pla-settings.json').read_text())
cases=[('petg-classic-016','clip-fine',petg,{}),('petg-coarse-016','clip-coarse',petg,{}),('petg-arachne-016','clip-fine',petg,{'wall_generator':'arachne'}),('petg-classic-012','clip-fine',petg,{'layer_height':'0.12'}),('petg-classic-020','clip-fine',petg,{'layer_height':'0.20'}),('pla-classic-016','clip-fine',pla,{}),('petg-lower-shell-016','lower-shell-fine',petg,{}),('petg-upper-shell-016','upper-shell-fine',petg,{})]
base={name:zipfile.ZipFile(template).read(name) for name in zipfile.ZipFile(template).namelist()}
manifest=[]
for name,meshname,settings,overrides in cases:
 raw=(root/(meshname+'.stl')).read_bytes(); count=struct.unpack_from('<I',raw,80)[0]; vertices=[]; triangles=[]; lookup={}
 for i in range(count):
  triangle=[]
  for v in range(3):
   x,y,z=struct.unpack_from('<fff',raw,84+50*i+12+12*v)
   if meshname.startswith('clip'): p=(x-6.525,z-18.25,12-y)
   elif meshname.startswith('lower'): p=(x-8,y,z-8)
   else: p=(x-8,-y,42-z)
   if p not in lookup: lookup[p]=len(vertices);vertices.append(p)
   triangle.append(lookup[p])
  triangles.append(triangle)
 mesh='<mesh><vertices>'+''.join(f'<vertex x="{x:.9f}" y="{y:.9f}" z="{z:.9f}"/>' for x,y,z in vertices)+'</vertices><triangles>'+''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in triangles)+'</triangles></mesh>'
 obj='<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources><object id="1" type="model">'+mesh+'</object></resources></model>'
 entries=base.copy();entries['3D/Objects/object_1.model']=obj.encode()
 entries['Metadata/model_settings.config']=re.sub(r'27156',str(count),entries['Metadata/model_settings.config'].decode()).replace('BuckleClipYP Nozzle designed S-curve nubs',name).replace('S-curve 0.4 PETG check',name).encode()
 entries['3D/3dmodel.model']=entries['3D/3dmodel.model'].decode().replace('Full walls corner detents PETG clip check','Current committed CAD '+name).encode()
 config=settings.copy();config.update(overrides); entries['Metadata/project_settings.config']=json.dumps(config).encode()
 case=root/name;case.mkdir(exist_ok=True)
 with zipfile.ZipFile(case/(name+'.3mf'),'w',compression=zipfile.ZIP_DEFLATED) as archive:
  for path,data in entries.items(): archive.writestr(path,data)
 manifest.append({'name':name,'source_mesh':meshname+'.stl','triangles':count,'vertices':len(vertices),'layer_height':config['layer_height'],'material':config['filament_type'],'wall_generator':config['wall_generator'],'wall_loops':config['wall_loops'],'print_orientation':'outer face down, pockets up' if meshname.startswith('clip') else 'external broad face down, cavity up','source_commit':'ec73ea966a47196b562c603a77cf7eb713e16893'})
(root/'cases.json').write_text(json.dumps(manifest,indent=2)); print(json.dumps(manifest))
