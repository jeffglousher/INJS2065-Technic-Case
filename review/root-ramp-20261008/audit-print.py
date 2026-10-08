from pathlib import Path
import sys,json,zipfile,xml.etree.ElementTree as E,hashlib,itertools,math
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
repo=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/root-ramp-20261008');project=out/'root-ramp.3mf';ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
result=json.loads((out/'root-ramp-slice.json').read_text());assert result['return_code']==0 and result['process_exit_code']==0 and not result['sliced_plates'][0]['warning_message']
assert hashlib.sha256(project.read_bytes()).hexdigest()==result['project_sha256']
records=[]
with zipfile.ZipFile(project) as z,zipfile.ZipFile(repo/'review/print-layout-20261008/assembly-petg-sequential-no-brim.3mf') as old:
 assert z.read('Metadata/project_settings.config')==old.read('Metadata/project_settings.config')
 assert z.read('3D/3dmodel.model')==old.read('3D/3dmodel.model')
 for i in range(1,6):
  entry=f'3D/Objects/object_{i}.model';raw=z.read(entry)
  if i>=3:assert raw==old.read(entry)
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
 for i in range(3,6):assert E.tostring(cfg.findall('object')[i-1])==E.tostring(oldcfg.findall('object')[i-1])
 settings=json.loads(z.read('Metadata/project_settings.config'));assert settings['print_sequence']=='by object'
source=(repo/'review/hub-quality-20261008/audit.py').read_text();n={};exec(source.split('old=parse(oldpath);new=parse(newpath)')[0],n)
before=n['parse'](Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-layout-20261008/assembly-petg-sequential-no-brim/plate_1.gcode'));after=n['parse'](out/'root-ramp-slice/plate_1.gcode')
assert hashlib.sha256((out/'root-ramp-slice/plate_1.gcode').read_bytes()).hexdigest()==result['gcode_sha256']
order=[]
for p in after:
 if not order or p['obj']!=order[-1]:order.append(p['obj'])
assert len(order)==5 and len(set(order))==5
assert not any(p['feature']=='Sparse infill' and p['obj'] in [3,4,5] for p in after)
proof={'project_sha256':result['project_sha256'],'gcode_sha256':result['gcode_sha256'],'meshes':records,'settings_and_placement_preserved':True,'hub_and_clip_mesh_entries_preserved':True,'sequential_object_order':order,'post_first_layers':{},'print_sent':False}
proof['object_layer_heights_mm']={}
for obj in range(1,6):
 zs=sorted(set(p['z'] for p in after if p['obj']==obj and p['feature'] not in ['Support','Support interface','Brim','Skirt']))
 expected=.08 if obj==5 else .12
 assert zs[0]==.2 and all(abs(b-a-expected)<1e-5 for a,b in zip(zs,zs[1:]))
 proof['object_layer_heights_mm'][str(obj)]={'first':.2,'main':expected,'layer_count':len(zs)}
fig,axes=plt.subplots(1,2,figsize=(9,5.8),dpi=180)
for body,xc,root_y,z0 in [(1,38.2,46.15,5.6744991167),(2,41.15,166.15,19.1744991167)]:
 rows={}
 for name,paths in [('before',before),('after',after)]:
  p=[p for p in paths if p['obj']==body and p['feature']=='Outer wall' and z0-.1<p['z']<z0+1.5 and any(abs(x-xc)<.95 and root_y-1.95<y<root_y-.01 for x,y in p['points'])]
  zs=sorted(set(p['z'] for p in p));assert zs
  rows[name]=[]
  for z in zs[:6]:
   pts=[(x,y) for p in p if p['z']==z for x,y in p['points'] if abs(x-xc)<.95 and root_y-1.95<y<root_y-.01]
   rows[name].append({'print_z_mm':z,'maximum_outward_wall_centerline_reach_mm':root_y-min(y for x,y in pts)})
 proof['post_first_layers'][str(body)]=rows
 assert rows['after'][0]['maximum_outward_wall_centerline_reach_mm']<rows['before'][0]['maximum_outward_wall_centerline_reach_mm']*.5
 if body==1:
  for ax,(name,paths) in zip(axes,[('before',before),('after',after)]):
   for i,row in enumerate(rows[name][:3]):
    z=row['print_z_mm'];seg=[[(a[0]-xc,a[1]-root_y),(b[0]-xc,b[1]-root_y)] for p in paths if p['obj']==1 and p['z']==z and p['feature']=='Outer wall' for a,b in zip(p['points'],p['points'][1:])]
    ax.add_collection(LineCollection(seg,colors=['#b93450','#3386a1','#b79222'][i],linewidths=1.6,label=f'Z={z:.2f} mm'))
   ax.axhline(0,color='#666',linestyle='--',linewidth=.8);ax.set(xlim=(-1.05,1.05),ylim=(-1.85,.35),aspect='equal',xlabel='X from post center (mm)',ylabel='Outward Y from wall/root (mm)',title='Current' if name=='before' else 'Root bevel: progressive outward reach');ax.legend(fontsize=8);ax.grid(alpha=.15)
fig.suptitle('Actual PETG / X2D 0.4 mm toolpaths — first three post outer walls');fig.tight_layout(rect=(0,0,1,.94));fig.savefig(out/'root-bevel-toolpaths.png',bbox_inches='tight');plt.close(fig)
proof['all_16_post_first_extrusions']=[]
for obj,centers,cy,z0 in [(1,[-3.8,2.1,8,13.9],55,5.6744991167),(2,[-.85,5.05,10.95,16.85],175,19.1744991167)]:
 regions={name:[p for p in paths if p['obj']==obj and z0-.1<p['z']<z0+1.5 and p['feature'] not in ['Support','Support interface','Brim','Skirt']] for name,paths in [('before',before),('after',after)]}
 for x in centers:
  for sign in [-1,1]:
   xc=x+42;root_y=cy+sign*8.85;data={}
   for name,paths in regions.items():
    near=[p for p in paths if any(abs(px-xc)<.95 and .01<sign*(py-root_y)<1.95 for px,py in p['points'])];z=min(p['z'] for p in near)
    first=[p for p in near if p['z']==z];reach=max(sign*(py-root_y) for p in first for px,py in p['points'] if abs(px-xc)<.95 and .01<sign*(py-root_y)<1.95)
    data[name]={'first_extrusion_print_z_mm':z,'maximum_outward_centerline_reach_mm':reach,'features':sorted(set(p['feature'] for p in first))}
   assert data['after']['maximum_outward_centerline_reach_mm']<data['before']['maximum_outward_centerline_reach_mm']*.5
   proof['all_16_post_first_extrusions'].append({'object':obj,'world_post_center_x_mm':x,'print_side_y_sign':sign,**data})
# The sampled socket checks include hub support paths.
assert not any(p['obj']==5 and 12.2<p['z']<15.55 and math.hypot(x-220,y-115)<2.55 for p in after for x,y in p['points'])
assert not any(p['obj']==5 and .2<=p['z']<7.8 and (abs(x-220)<.675 and abs(y-115)<2.175 or abs(x-220)<2.175 and abs(y-115)<.675) for p in after for x,y in p['points'])
proof['sampled_hub_socket_interiors_clear']=True
(out/'print-audit.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof['post_first_layers'],indent=2))
