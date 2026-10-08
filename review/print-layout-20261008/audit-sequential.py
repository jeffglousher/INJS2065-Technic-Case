from pathlib import Path
import json,itertools,math,sys,zipfile,hashlib,xml.etree.ElementTree as E
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-layout-20261008');ns={};src=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/hub-quality-20261008/audit.py').read_text();exec(src.split('old=parse(oldpath);new=parse(newpath)')[0],ns)
for name in ['assembly-petg-sequential-no-brim','assembly-petg-sequential-clip-quality']:
 p=out/name/'plate_1.gcode';paths=ns['parse'](p);result=json.loads((out/(name+'-slice.json')).read_text());assert result['return_code']==0 and result['process_exit_code']==0;assert not result['sliced_plates'][0]['warning_message']
 assert hashlib.sha256(p.read_bytes()).hexdigest()==result['gcode_sha256']
 project=out/(name+'.3mf');assert hashlib.sha256(project.read_bytes()).hexdigest()==result['project_sha256']
 with zipfile.ZipFile(project) as z,zipfile.ZipFile('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/hub-quality-20261008/assembly-petg-hub-quality.3mf') as old:
  cfg=E.fromstring(z.read('Metadata/model_settings.config'))
  hub=next(o for o in cfg.findall('object') if o.attrib['id']=='105')
  hmeta={m.attrib['key']:m.attrib['value'] for m in hub.findall('metadata') if 'key' in m.attrib}
  assert hmeta['brim_type']=='no_brim' and float(hmeta['brim_width'])==0
  assert hmeta['enable_support']=='1'
  mesh_entries=[n for n in z.namelist() if n.startswith('3D/Objects/') and n.endswith('.model')]
  assert len(mesh_entries)==5
  assert all(z.read(n)==old.read(n) for n in mesh_entries)
 settings=json.loads((out/name/'resolved-settings.json').read_text());assert settings['print_sequence']=='by object'
 order=[]
 for q in paths:
  if not order or order[-1]!=q['obj']:order.append(q['obj'])
 assert len(order)==5 and len(set(order))==5,order
 centers={1:(50,55),2:(50,175),3:(150,55),4:(150,175),5:(220,115)}
 features={};layers={};speeds={};holes=[];support=[]
 for i in range(1,6):
  q=[q for q in paths if q['obj']==i and q['feature'] not in ['Support','Support interface','Skirt','Brim']];zs=sorted(set(q['z'] for q in q));step=.08 if i==5 or 'clip-quality' in name and i in [3,4] else .12
  assert zs[0]==.2 and all(abs(b-a-step)<1e-5 for a,b in zip(zs,zs[1:])),(name,i,zs)
  layers[str(i)]={'count':len(zs),'first_layer':.2,'main_layer':step};features[str(i)]={feat:sum(q['feature']==feat for q in q) for feat in set(q['feature'] for q in q)}
  speeds[str(i)]=max(q['speed'] for q in q if q['feature']=='Outer wall' and q['z']>.2)
  if i==5:assert features[str(i)].get('Sparse infill',0)==0
  if i in [3,4]:assert features[str(i)].get('Sparse infill',0)==0
  if 'clip-quality' in name and i in [3,4]:assert speeds[str(i)]<=25.001
 for q in paths:
  if q['feature'] in ['Support','Support interface']:support.extend(q['points'])
  if q['obj']!=5:continue
  for x,y in q['points']:
   x-=220;y-=115
   if 12.2<q['z']<15.55 and math.hypot(x,y)<2.55:holes.append(q['feature'])
   if .2<=q['z']<7.8 and (abs(x)<.675 and abs(y)<2.175 or abs(x)<2.175 and abs(y)<.675):holes.append(q['feature'])
 assert not holes
 bound=[[min(p[k] for p in support),max(p[k] for p in support)] for k in [0,1]];assert 200<bound[0][0]<bound[0][1]<242 and 90<bound[1][0]<bound[1][1]<140
 manifest=json.loads((out/(name+'-project.json')).read_text());gaps=[]
 for a,b in itertools.combinations(manifest['parts'],2):
  a=a['plate_bounds_mm'];b=b['plate_bounds_mm'];dx=max(0,a[0][0]-b[0][1],b[0][0]-a[0][1]);dy=max(0,a[1][0]-b[1][1],b[1][0]-a[1][1]);gaps.append(math.hypot(dx,dy))
 assert min(gaps)>60
 proof={'native_sequential_validation_passed':True,'print_sequence':'by object','actual_object_extrusion_order_labels':order,'one_contiguous_extrusion_group_per_object':True,'object_layer_heights_mm':layers,'feature_counts':features,'max_commanded_outer_wall_speeds_mm_s':speeds,'hub_support_bounds_mm':bound,'minimum_object_bbox_gap_mm':min(gaps),'profile_clearance_max_radius_mm':settings['extruder_clearance_max_radius'],'profile_height_to_rod_mm':settings['extruder_clearance_height_to_rod'],'sockets_interior_path_samples':0,'gcode_sha256':result['gcode_sha256'],'object_brim_requested':False,'tree_support_footings_retained':True,'print_sent':False}
 (out/(name+'-audit.json')).write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2),flush=True)
