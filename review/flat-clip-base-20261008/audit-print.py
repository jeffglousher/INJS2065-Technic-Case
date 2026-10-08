from pathlib import Path
import sys,json,zipfile,xml.etree.ElementTree as E,hashlib,itertools,math
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
repo=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/flat-clip-base-20261008');project=out/'flat-floor.3mf';ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
result=json.loads((out/'flat-floor-slice.json').read_text());assert result['return_code']==0 and result['process_exit_code']==0 and not result['sliced_plates'][0]['warning_message']
assert hashlib.sha256(project.read_bytes()).hexdigest()==result['project_sha256']
records=[]
with zipfile.ZipFile(project) as z,zipfile.ZipFile(repo/'review/root-ramp-20261008/assembly-petg-root-bevel.3mf') as old:
 assert z.read('Metadata/project_settings.config')==old.read('Metadata/project_settings.config')
 assert z.read('3D/3dmodel.model')==old.read('3D/3dmodel.model')
 for i in range(1,6):
  entry=f'3D/Objects/object_{i}.model';raw=z.read(entry)
  if i in [1,2,5]:assert raw==old.read(entry)
  doc=E.fromstring(raw);v=np.array([[float(e.attrib[k]) for k in ['x','y','z']] for e in doc.findall('.//m:vertex',ns)]);t=np.array([[int(e.attrib[k]) for k in ['v1','v2','v3']] for e in doc.findall('.//m:triangle',ns)])
  assert np.isfinite(v).all();w,idx=np.unique(np.round(v,5),axis=0,return_inverse=True);tri=idx[t];assert np.all(tri[:,0]!=tri[:,1]) and np.all(tri[:,1]!=tri[:,2]) and np.all(tri[:,2]!=tri[:,0])
  edges=np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]);ee,counts=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True);assert np.all(counts==2)
  forward=edges[edges[:,0]<edges[:,1]];assert len(forward)==len(ee) and len(np.unique(forward,axis=0))==len(ee)
  parent=list(range(len(w)))
  def find(k):
   while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
   return k
  for a,b in ee:parent[find(int(a))]=find(int(b))
  assert len({find(int(k)) for k in np.unique(tri)})==1
  xyz=v[t];vol=float(np.einsum('ij,ij->i',xyz[:,0],np.cross(xyz[:,1],xyz[:,2])).sum()/6);assert vol>0
  records.append({'object':i,'triangles':len(t),'closed':True,'consistent_winding':True,'connected_components':1,'volume_mm3':vol,'mesh_entry_sha256':hashlib.sha256(raw).hexdigest()})
 cfg=E.fromstring(z.read('Metadata/model_settings.config'));oldcfg=E.fromstring(old.read('Metadata/model_settings.config'))
 for i in range(1,6):
  a=cfg.findall('object')[i-1];b=oldcfg.findall('object')[i-1]
  for o in [a,b]:
   for md in o.findall('metadata'):
    if 'face_count' in md.attrib:md.set('face_count','0')
   o.find('part/mesh_stat').set('face_count','0')
  assert E.tostring(a)==E.tostring(b)
 settings=json.loads(z.read('Metadata/project_settings.config'));assert settings['print_sequence']=='by object'

source=(repo/'review/hub-quality-20261008/audit.py').read_text();n={};exec(source.split('old=parse(oldpath);new=parse(newpath)')[0],n)
after=n['parse'](out/'flat-floor-slice/plate_1.gcode')
assert hashlib.sha256((out/'flat-floor-slice/plate_1.gcode').read_bytes()).hexdigest()==result['gcode_sha256']
order=[]
for p in after:
 if not order or p['obj']!=order[-1]:order.append(p['obj'])
assert len(order)==5 and len(set(order))==5
assert not any(p['feature']=='Sparse infill' and p['obj'] in [3,4,5] for p in after)
proof={'project_sha256':result['project_sha256'],'gcode_sha256':result['gcode_sha256'],'meshes':records,'settings_and_placement_preserved':True,'shell_and_hub_mesh_entries_preserved':True,'sequential_object_order':order,'clips_slice_solid':True,'print_sent':False,'object_layer_heights_mm':{}}
for obj in range(1,6):
 zs=sorted(set(p['z'] for p in after if p['obj']==obj and p['feature'] not in ['Support','Support interface','Brim','Skirt']))
 expected=.08 if obj==5 else .12
 assert zs[0]==.2 and all(abs(b-a-expected)<1e-5 for a,b in zip(zs,zs[1:]))
 proof['object_layer_heights_mm'][str(obj)]={'first':.2,'main':expected,'layer_count':len(zs)}
assert not any(p['obj'] in [3,4] and p['feature'] in ['Support','Support interface'] for p in after)
assert not any(p['obj']==5 and p['feature']=='Brim' for p in after)
assert not any(p['obj']==5 and 12.2<p['z']<15.55 and math.hypot(x-220,y-115)<2.55 for p in after for x,y in p['points'])
assert not any(p['obj']==5 and .2<=p['z']<7.8 and (abs(x-220)<.675 and abs(y-115)<2.175 or abs(x-220)<2.175 and abs(y-115)<.675) for p in after for x,y in p['points'])
proof['sampled_hub_socket_interiors_clear']=True
for id in [173,267]:
 for y in [9.3,9.8,10.3]:
  def norm(s):return sorted(tuple(sorted((round(x,6),round(z,6)) for x,z in v['points'])) for v in s['section'])
  a=json.loads((out/f'before-{id}-y{y}.json').read_text());b=json.loads((out/f'after-{id}-y{y}.json').read_text());assert norm(a)==norm(b)
proof['six_native_wall_sections_unchanged_at_1e6_mm_rounding']=True
# Current native pocket floors contain no curved depression behind |Y|=10.55.
for id in [173,267]:
 sec=json.loads((out/f'after-{id}-y10.6.json').read_text());assert len(sec['section'])==22
proof['flat_floor_backing_sections_complete']=True
proof['estimate_seconds']=result['sliced_plates'][0]['total_predication'];proof['estimate_grams']=result['sliced_plates'][0]['filaments'][0]['total_used_g']
(out/'print-audit.json').write_text(json.dumps(proof,indent=2));print('PASS five closed connected meshes, preserved profiles/layout, native full slice, solid clips, six unchanged wall sections')
