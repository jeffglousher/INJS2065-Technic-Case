import json,sys,math
from pathlib import Path
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs');import numpy as np
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-layout-20261008');scene=json.loads((out/'baseline-scene.json').read_text());records=[]
for bid in [8,18]:
 b=next(b for b in scene['bodies'] if b['id']==bid);v=np.array(b['mesh']['positions']).reshape(-1,3);idx=np.array(b['mesh']['indices']);flip=1 if bid==8 else -1
 for f in b['faces']:
  if f.get('plane') is None:continue
  tri=v[idx[f['first_index']:f['first_index']+f['index_count']].reshape(-1,3)];norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm=norm.sum(axis=0);length=np.linalg.norm(norm)
  if length<1e-12:continue
  norm/=length;nz=norm[2]*flip
  ctr=tri.reshape(-1,3).mean(axis=0)
  if nz<-.01 and 8.5<abs(ctr[1])<12.5 and 10<ctr[2]<28:
   lo=tri.reshape(-1,3).min(axis=0);hi=tri.reshape(-1,3).max(axis=0);angle=math.degrees(math.asin(min(1,-nz)))
   records.append({'body_id':bid,'face_id':f['id'],'face_key':f['key'],'normal':norm.tolist(),'overhang_from_vertical_deg':angle,'centroid':ctr.tolist(),'bounds':[lo.tolist(),hi.tolist()]})
(out/'hex-overhang-audit.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2)[:3400])
