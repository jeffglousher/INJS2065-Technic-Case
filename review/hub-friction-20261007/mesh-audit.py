import json,struct,sys,hashlib,re
from pathlib import Path
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import numpy as np
r=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hub-friction-20261007')
raw=(r/'hub-fine.stl').read_bytes();n=struct.unpack_from('<I',raw,80)[0];dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]);t=np.frombuffer(raw,dtype=dt,offset=84)['v'].astype(float);pts,idx=np.unique(np.round(t.reshape(-1,3),5),axis=0,return_inverse=True);tri=idx.reshape(-1,3);edges=np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]);ee,counts=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True);assert np.all(counts==2)
parent=list(range(len(pts)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for a,b in ee:parent[find(int(a))]=find(int(b))
components=len({find(i) for i in range(len(pts))});assert components==1
vol=np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6;assert vol>0
step=(r/'hub.step').read_text();solids=step.count('MANIFOLD_SOLID_BREP(');assert solids==1
record={'triangles':n,'mesh_sha256':hashlib.sha256(raw).hexdigest(),'closed_two_incidence_edges':True,'connected_components':components,'signed_volume_mm3':vol,'mesh_edge_weld_quantization_mm':1e-5,'STEP_manifold_solids':solids,'step_sha256':hashlib.sha256((r/'hub.step').read_bytes()).hexdigest()}
(r/'mesh-audit.json').write_text(json.dumps(record,indent=2));print(record)
