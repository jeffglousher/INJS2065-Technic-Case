from pathlib import Path
import json,struct,zipfile,xml.etree.ElementTree as E,subprocess,hashlib
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/flat-clip-base-20261008')
source=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/root-ramp-20261008/assembly-petg-root-bevel.3mf')
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
with zipfile.ZipFile(source) as z:original={n:z.read(n) for n in z.namelist()}
for name in ['flat-floor']:
 data=original.copy()
 for body,part in [(173,3),(267,4)]:
  raw=(out/f'{name}-{body}.stl').read_bytes();count=struct.unpack_from('<I',raw,80)[0];vertices=[];triangles=[];lookup={}
  for i in range(count):
   triangle=[]
   for j in range(3):
    x,y,z=struct.unpack_from('<fff',raw,84+i*50+12+j*12)
    p=(x-6.525,z-18.25,12-y) if body==173 else (x-6.525,18.25-z,12+y)
    if p not in lookup:lookup[p]=len(vertices);vertices.append(p)
    triangle.append(lookup[p])
   triangles.append(triangle)
  verts=''.join(f'<vertex x="{x:.9f}" y="{y:.9f}" z="{z:.9f}"/>' for x,y,z in vertices)
  tris=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in triangles)
  entry=f'3D/Objects/object_{part}.model'
  data[entry]=(f'<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="{ns}"><resources><object id="{part}" type="model"><mesh><vertices>{verts}</vertices><triangles>{tris}</triangles></mesh></object></resources></model>').encode()
  cfg=E.fromstring(data['Metadata/model_settings.config']);obj=next(o for o in cfg.findall('object') if o.attrib['id']==str(100+part));next(m for m in obj.findall('metadata') if 'face_count' in m.attrib).set('face_count',str(count));obj.find('part/mesh_stat').set('face_count',str(count));data['Metadata/model_settings.config']=E.tostring(cfg,encoding='utf-8',xml_declaration=True)
 target=out/(name+'.3mf')
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in data.items():z.writestr(n,b)
 d=out/(name+'-slice');d.mkdir(exist_ok=True)
 cmd=['C:/Program Files/Bambu Studio/bambu-studio.exe','--load-filaments','D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007/bambu-petg-basic-resolved.json','--slice','1','--outputdir',str(d),str(target)]
 p=subprocess.run(cmd,cwd=d,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=90)
 (d/'cli.log').write_bytes(p.stdout+p.stderr)
 r=json.loads((d/'result.json').read_text());r.update(process_exit_code=p.returncode,project_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),gcode_sha256=hashlib.sha256((d/'plate_1.gcode').read_bytes()).hexdigest())
 (out/(name+'-slice.json')).write_text(json.dumps(r,indent=2))
 assert p.returncode==0 and r['return_code']==0
 assert not r['sliced_plates'][0]['warning_message']
 print(name,'native slice passed',flush=True)
