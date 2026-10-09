from pathlib import Path
import json,struct,zipfile,xml.etree.ElementTree as E,subprocess,hashlib,re
root=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');out=Path(__file__).parent
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
E.register_namespace('',ns)
E.register_namespace('p','http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
with zipfile.ZipFile(root/'review/flat-clip-base-20261008/assembly-petg-flat-clip-base.3mf') as z:template={n:z.read(n) for n in z.namelist()}
def mesh(raw,transform,i):
 binary_count=struct.unpack_from('<I',raw,80)[0]
 if len(raw)==84+50*binary_count:
  source=[struct.unpack_from('<fff',raw,84+j*50+12+k*12) for j in range(binary_count) for k in range(3)]
 else:
  source=[tuple(map(float,m)) for m in re.findall(rb'\bvertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)',raw)]
  assert len(source)>0 and len(source)%3==0
 count=len(source)//3;vertices=[];triangles=[];lookup={}
 for j in range(count):
  ids=[]
  for k in range(3):
   p=transform(*source[3*j+k])
   if p not in lookup:lookup[p]=len(vertices);vertices.append(p)
   ids.append(lookup[p])
  triangles.append(ids)
 vv=''.join(f'<vertex x="{x:.9f}" y="{y:.9f}" z="{z:.9f}"/>' for x,y,z in vertices);tt=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in triangles)
 return (f'<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="{ns}"><resources><object id="{i}" type="model"><mesh><vertices>{vv}</vertices><triangles>{tt}</triangles></mesh></object></resources></model>').encode(),count
cases=[('assembly-fit-candidate',[(8,'candidate-8.stl',lambda x,y,z:(x-8,y,z-8),'Lower clamshell'),(18,'candidate-18.stl',lambda x,y,z:(x-8,-y,42-z),'Upper clamshell'),(173,'candidate-173.stl',lambda x,y,z:(x-6.525,z-18.25,12-y),'Clip +Y'),(267,'candidate-267.stl',lambda x,y,z:(x-6.525,18.25-z,12+y),'Clip -Y')]),
('retention-coupon',[(8,'coupon-8.stl',lambda x,y,z:(x-8,y,z-8),'Lower receiver coupon'),(18,'coupon-18.stl',lambda x,y,z:(x-8,-y,27.6-z),'Upper receiver coupon'),(173,'candidate-173.stl',lambda x,y,z:(x-6.525,z-18.25,12-y),'Clip 0.26 mm - nominal'),(173,'nub-0.24-173.stl',lambda x,y,z:(x-6.525,z-18.25,12-y),'Clip 0.24 mm - looser'),(173,'nub-0.28-173.stl',lambda x,y,z:(x-6.525,z-18.25,12-y),'Clip 0.28 mm - tighter')])]
for name,parts in cases:
 data=template.copy();cfg=E.fromstring(data['Metadata/model_settings.config']);main=E.fromstring(data['3D/3dmodel.model']);records=[]
 for i,(bid,file,transform,title) in enumerate(parts,1):
  raw=(out/file).read_bytes();entry=f'3D/Objects/object_{i}.model';data[entry],count=mesh(raw,transform,i)
  obj=next(x for x in cfg.findall('object') if x.attrib['id']==str(100+i));next(m for m in obj.findall('metadata') if 'face_count' in m.attrib).set('face_count',str(count));obj.find('part/mesh_stat').set('face_count',str(count))
  for meta in obj.findall('.//metadata'):
   if meta.get('key')=='name':meta.set('value',title)
  if name=='retention-coupon':
   for meta in list(obj.findall('metadata')):
    if meta.get('key') not in ['name','extruder'] and 'face_count' not in meta.attrib:obj.remove(meta)
   if i==5:
    tr='1 0 0 0 1 0 0 0 1 220 115 0'
    # Existing hub placement leaves ample object spacing for a full clip.
    next(x for x in main.find('{'+ns+'}build') if x.get('objectid')=='105').set('transform',tr)
  records.append({'object_id':i,'body_id':bid,'file':file,'mesh_sha256':hashlib.sha256(data[entry]).hexdigest(),'source_sha256':hashlib.sha256(raw).hexdigest(),'triangles':count,'name':title})
 for meta in main.findall('{'+ns+'}metadata'):
  if meta.get('name')=='Title':meta.text='INJS2065 '+name+' - PETG fit test'
 next(m for m in cfg.find('plate').findall('metadata') if m.get('key')=='plater_name').set('value',name)
 main.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
 data['Metadata/model_settings.config']=E.tostring(cfg,encoding='utf-8',xml_declaration=True);data['3D/3dmodel.model']=E.tostring(main,encoding='utf-8',xml_declaration=True)
 settings=json.loads(data['Metadata/project_settings.config']);settings['layer_height']='0.16';settings['arc_fitting']='0';settings['brim_type']='no_brim';settings['enable_support']='0';data['Metadata/project_settings.config']=json.dumps(settings).encode()
 # Remove inherited thumbnails: they describe the old assembly, not these meshes.
 data={k:v for k,v in data.items() if not k.endswith('.png')}
 project=out/(name+'.3mf')
 with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED) as z:
  for k,v in data.items():z.writestr(k,v)
 d=out/(name+'-slice');d.mkdir(exist_ok=True)
 cmd=['C:/Program Files/Bambu Studio/bambu-studio.exe','--load-filaments','D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007/bambu-petg-basic-resolved.json','--slice','1','--outputdir',str(d),'--export-settings',str(d/'resolved-settings.json'),str(project)]
 p=subprocess.run(cmd,cwd=d,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=110);(d/'cli.log').write_bytes(p.stdout+p.stderr)
 result=json.loads((d/'result.json').read_text());assert p.returncode==0 and result['return_code']==0,result;assert not result['sliced_plates'][0]['warning_message'],result
 (out/(name+'-audit.json')).write_text(json.dumps({'parts':records,'project_sha256':hashlib.sha256(project.read_bytes()).hexdigest(),'gcode_sha256':hashlib.sha256((d/'plate_1.gcode').read_bytes()).hexdigest(),'native_result':result,'print_sent':False},indent=2));print(name,'PASS native PETG slice',flush=True)
