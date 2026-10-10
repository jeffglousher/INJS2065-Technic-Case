from pathlib import Path
import ast, hashlib, json, re, subprocess, zipfile
import xml.etree.ElementTree as E
ROOT=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case')
OUT=Path(__file__).parent
SOURCE=ROOT/'review/hub-bridge-20261010/assembly-petg-bridge-tuned.3mf'
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
E.register_namespace('',ns);E.register_namespace('p','http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(SOURCE) as z:template={n:z.read(n) for n in z.namelist()}
src=(ROOT/'review/retention-fit-20261009/projects.py').read_text()
tree=ast.parse(src);f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='mesh')
import struct
exec(compile(ast.get_source_segment(src,f),'<recorded-stl-to-3mf>','exec'))
import sys
for tag in sys.argv[1:] or ['nub-28','nub-30']:
 data=template.copy();cfg=E.fromstring(data['Metadata/model_settings.config']);main=E.fromstring(data['3D/3dmodel.model'])
 for i,(bid,transform) in enumerate([(8,lambda x,y,z:(x-8,y,z-8)),(18,lambda x,y,z:(x-8,-y,42-z)),(173,lambda x,y,z:(x-6.525,z-18.25,12-y)),(267,lambda x,y,z:(x-6.525,18.25-z,12+y))],1):
  data[f'3D/Objects/object_{i}.model'],count=mesh((OUT/f'{tag}-{bid}.stl').read_bytes(),transform,i)
  obj=next(o for o in cfg.findall('object') if o.get('id')==str(100+i))
  next(m for m in obj.findall('metadata') if 'face_count' in m.attrib).set('face_count',str(count));obj.find('part/mesh_stat').set('face_count',str(count))
 label=f'INJS2065 unbeveled hex - {tag} - rotary gap 0.205 mm - PETG test'
 for m in main.findall('{'+ns+'}metadata'):
  if m.get('name')=='Title':m.text=label
 for m in cfg.findall('plate/metadata'):
  if m.get('key')=='plater_name':m.set('value',label)
 main.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
 data['3D/3dmodel.model']=E.tostring(main,encoding='utf-8',xml_declaration=True);data['Metadata/model_settings.config']=E.tostring(cfg,encoding='utf-8',xml_declaration=True)
 data={k:v for k,v in data.items() if not k.endswith('.png')}
 # Check complete profiles and object overrides after reversing only face counts/label.
 old=E.fromstring(template['Metadata/model_settings.config']);check=E.fromstring(data['Metadata/model_settings.config'])
 for a,b in zip(old.findall('object'),check.findall('object')):
  for x,y in zip(a.findall('metadata'),b.findall('metadata')):
   if 'face_count' in x.attrib:y.set('face_count',x.get('face_count'))
  b.find('part/mesh_stat').set('face_count',a.find('part/mesh_stat').get('face_count'))
 assert [E.tostring(o) for o in old.findall('object')]==[E.tostring(o) for o in check.findall('object')]
 assert data['Metadata/project_settings.config']==template['Metadata/project_settings.config']
 assert data['3D/Objects/object_5.model']==template['3D/Objects/object_5.model']
 assert E.tostring(main.find('{'+ns+'}build'))==E.tostring(E.fromstring(template['3D/3dmodel.model']).find('{'+ns+'}build'))
 project=OUT/f'{tag}.3mf'
 with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED) as z:
  for k,v in data.items():z.writestr(k,v)
 d=OUT/f'{tag}-slice';d.mkdir(exist_ok=True)
 cmd=['C:/Program Files/Bambu Studio/bambu-studio.exe','--load-filaments','D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007/bambu-petg-basic-resolved.json','--slice','1','--outputdir',str(d),'--export-settings',str(d/'resolved-settings.json'),str(project)]
 p=subprocess.run(cmd,cwd=d,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=180);(d/'cli.log').write_bytes(p.stdout+p.stderr)
 r=json.loads((d/'result.json').read_text());assert p.returncode==r['return_code']==0,r
 assert not r['sliced_plates'][0]['warning_message'],r
 assert len(r['sliced_plates'][0]['objects'])==5,r
 audit={'source_project_sha256':sha(SOURCE),'project_sha256':sha(project),'gcode_sha256':sha(d/'plate_1.gcode'),'native_result':r,'hub_mesh_unchanged':True,'all_poses_profiles_and_object_overrides_unchanged':True,'print_sent':False}
 (OUT/f'{tag}-slice.json').write_text(json.dumps(audit,indent=2))
 print(tag,'native slice PASS',r['sliced_plates'][0]['total_predication'],flush=True)
