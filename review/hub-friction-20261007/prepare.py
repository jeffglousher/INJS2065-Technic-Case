import hashlib,json,struct,zipfile,xml.etree.ElementTree as E,math
from pathlib import Path
r=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/revision-20261007')
o=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hub-friction-20261007')
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
pns='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
sha=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(r/'clip-fine.3mf') as z: settings=z.read('Metadata/project_settings.config'); content=z.read('[Content_Types].xml'); rootrel=z.read('_rels/.rels')
config=json.loads(settings)
assert config['printer_settings_id']=='Bambu Lab X2D 0.4 nozzle'
assert config['filament_settings_id']==['Bambu PETG Basic @BBL X2D 0.4 nozzle']
parts=[('Lower clamshell',8,'lower-fine',80,100),('Upper clamshell',18,'upper-fine',140,100),('Clip +Y',173,'clip-fine',80,150),('Clip -Y',267,'clip-minus',130,150),('Output hub',54,'hub',190,100)]
entries={'[Content_Types].xml':content,'_rels/.rels':rootrel,'Metadata/project_settings.config':settings}
model=E.Element('model',{'unit':'millimeter','xml:lang':'en-US','xmlns':ns,'xmlns:p':pns,'xmlns:BambuStudio':'http://schemas.bambulab.com/package/2021','requiredextensions':'p'})
E.SubElement(model,'metadata',{'name':'Application'}).text='BambuStudio-02.08.02.61'
E.SubElement(model,'metadata',{'name':'BambuStudio:3mfVersion'}).text='1'
E.SubElement(model,'metadata',{'name':'Title'}).text='INJS2065 PETG print set - friction hub'
resources=E.SubElement(model,'resources');build=E.SubElement(model,'build');mc=E.Element('config');plate=E.SubElement(mc,'plate')
def meta(parent,key,val):E.SubElement(parent,'metadata',{'key':key,'value':str(val)})
for k,v in [('plater_id',1),('plater_name','Complete PETG set'),('locked','false'),('filament_map_mode','Auto For Flush'),('filament_maps',1),('filament_volume_maps',0)]:meta(plate,k,v)
assemble=E.SubElement(mc,'assemble');rels=E.Element('Relationships',{'xmlns':'http://schemas.openxmlformats.org/package/2006/relationships'});records=[]
for i,(name,body,source,cx,cy) in enumerate(parts,1):
 if source in ['lower-fine','upper-fine','clip-fine']:
  path=r/(source+'.3mf')
  with zipfile.ZipFile(path) as z:meshbytes=z.read('3D/Objects/object_1.model')
  srcroot=E.fromstring(meshbytes);vv=[tuple(float(e.attrib[k]) for k in ['x','y','z']) for e in srcroot.findall('.//{'+ns+'}vertex')];tt=[tuple(int(e.attrib[k]) for k in ['v1','v2','v3']) for e in srcroot.findall('.//{'+ns+'}triangle')]
  meshhash=sha(meshbytes);srcsha=sha(path.read_bytes())
 else:
  path=o/(source+'.stl');raw=path.read_bytes();n=struct.unpack_from('<I',raw,80)[0];vv=[];tt=[];lookup={}
  for j in range(n):
   tri=[]
   for k in range(3):
    x,y,z=struct.unpack_from('<fff',raw,84+50*j+12+12*k)
    p=(x-6.525,18.25-z,12+y) if source=='clip-minus' else (x,-y,42-z)
    if p not in lookup:lookup[p]=len(vv);vv.append(p)
    tri.append(lookup[p])
   tt.append(tuple(tri))
  vertices=''.join(f'<vertex x="{x:.9f}" y="{y:.9f}" z="{z:.9f}"/>' for x,y,z in vv)
  triangles=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in tt)
  meshbytes=(f'<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="{ns}"><resources><object id="1" type="model"><mesh><vertices>{vertices}</vertices><triangles>{triangles}</triangles></mesh></object></resources></model>').encode()
  meshhash=sha(meshbytes);srcsha=sha(raw)
 meshbytes=meshbytes.replace(b'<object id="1"',f'<object id="{i}"'.encode(),1)
 meshhash=sha(meshbytes)
 entry=f'3D/Objects/object_{i}.model';entries[entry]=meshbytes
 oid=i+100;obj=E.SubElement(resources,'object',{'id':str(oid),'type':'model'});components=E.SubElement(obj,'components')
 E.SubElement(components,'component',{'p:path':'/'+entry,'objectid':str(i),'transform':'1 0 0 0 1 0 0 0 1 0 0 0'})
 transform=f'1 0 0 0 1 0 0 0 1 {cx} {cy} 0'
 E.SubElement(build,'item',{'objectid':str(oid),'transform':transform,'printable':'1'})
 E.SubElement(rels,'Relationship',{'Target':'/'+entry,'Id':f'rel-{i}','Type':'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'})
 obj=E.SubElement(mc,'object',{'id':str(oid)});meta(obj,'name',name);meta(obj,'extruder',1)
 if source=='hub':
  for k,v in [('enable_support',1),('support_type','tree(auto)'),('support_on_build_plate_only',1),('brim_type','outer_only'),('brim_width',5)]:meta(obj,k,v)
 E.SubElement(obj,'metadata',{'face_count':str(len(tt))});part=E.SubElement(obj,'part',{'id':str(i),'subtype':'normal_part'});meta(part,'name',name);meta(part,'matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1');E.SubElement(part,'mesh_stat',{'face_count':str(len(tt)),'edges_fixed':'0','degenerate_facets':'0','facets_removed':'0','facets_reversed':'0','backwards_edges':'0'})
 inst=E.SubElement(plate,'model_instance')
 for k,v in [('object_id',oid),('instance_id',0),('identify_id',i)]:meta(inst,k,v)
 E.SubElement(assemble,'assemble_item',{'object_id':str(oid),'instance_id':'0','transform':transform,'offset':'0 0 0'})
 bounds=[[min(p[k] for p in vv),max(p[k] for p in vv)] for k in range(3)]
 assert abs(bounds[2][0])<1e-6
 bounds[0]=[v+cx for v in bounds[0]];bounds[1]=[v+cy for v in bounds[1]]
 assert all(20<b<236 for arr in bounds[:2] for b in arr)
 signed=sum(vv[a][0]*(vv[b][1]*vv[c][2]-vv[b][2]*vv[c][1])+vv[a][1]*(vv[b][2]*vv[c][0]-vv[b][0]*vv[c][2])+vv[a][2]*(vv[b][0]*vv[c][1]-vv[b][1]*vv[c][0]) for a,b,c in tt)/6
 assert signed>0
 records.append({'name':name,'body_id':body,'source_sha256':srcsha,'mesh_entry_sha256':meshhash,'triangles':len(tt),'volume_mm3':signed,'plate_bounds_mm':bounds,'supports':source=='hub','orientation':'outer broad face down' if 'clip' in source else ('outside face down' if 'fine' in source else 'output face Z42 down')})
for a in records:
 for b in records:
  if a is b:continue
  # Keep at least 15 mm between object AABBs, including room for a 5 mm hub brim.
  gap=max(b['plate_bounds_mm'][k][0]-a['plate_bounds_mm'][k][1] for k in range(2))
  rgap=max(a['plate_bounds_mm'][k][0]-b['plate_bounds_mm'][k][1] for k in range(2))
  assert max(gap,rgap)>15,(a['name'],b['name'],gap,rgap)
entries['3D/3dmodel.model']=E.tostring(model,encoding='utf-8',xml_declaration=True)
entries['3D/_rels/3dmodel.model.rels']=E.tostring(rels,encoding='utf-8',xml_declaration=True)
entries['Metadata/model_settings.config']=E.tostring(mc,encoding='utf-8',xml_declaration=True)
project=o/'assembly-petg-friction-hub.3mf'
with zipfile.ZipFile(project,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for n,data in entries.items():z.writestr(n,data)
proof={'project_sha256':sha(project.read_bytes()),'source':json.loads((o/'source.json').read_text()),'parts':records,'saved_settings':{k:config[k] for k in ['printer_settings_id','filament_settings_id','layer_height','wall_loops','enable_support','sparse_infill_density']},'project_settings_identical_to_reviewed_clip':True,'hardware_not_printed':['servo','bearing'],'print_sent':False}
(o/'assembly-project.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(proof,indent=2))
