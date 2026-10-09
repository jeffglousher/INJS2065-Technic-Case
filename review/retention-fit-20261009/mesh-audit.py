from pathlib import Path
import sys,json,zipfile,xml.etree.ElementTree as E
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import numpy as np
out=Path(__file__).parent;ns={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};rows=[]
for name in ['assembly-fit-candidate','retention-coupon']:
 with zipfile.ZipFile(out/(name+'.3mf')) as z:
  for i in range(1,6):
   tree=E.fromstring(z.read(f'3D/Objects/object_{i}.model'));v=np.array([[float(e.get(k)) for k in ['x','y','z']] for e in tree.findall('.//c:vertex',ns)]);t=np.array([[int(e.get(k)) for k in ['v1','v2','v3']] for e in tree.findall('.//c:triangle',ns)]);
   _,inv=np.unique(np.round(v,5),axis=0,return_inverse=True);welded=inv[t];edges=np.sort(np.concatenate([welded[:,[0,1]],welded[:,[1,2]],welded[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True);assert np.all(counts==2),(name,i,'not manifold');xyz=v[t];vol=np.einsum('ij,ij->i',xyz[:,0],np.cross(xyz[:,1],xyz[:,2])).sum()/6;assert vol>0
   # Vertex adjacency detects disconnected bodies without depending on face order.
   adjacent={}
   for a,b in edges:
    adjacent.setdefault(int(a),set()).add(int(b));adjacent.setdefault(int(b),set()).add(int(a))
   seen=set();components=0
   for a in adjacent:
    if a in seen:continue
    components+=1;todo=[a];seen.add(a)
    while todo:
     q=todo.pop()
     for b in adjacent[q]:
      if b not in seen:seen.add(b);todo.append(b)
   assert components==1,(name,i,components)
   rows.append({'project':name,'object':i,'triangles':len(t),'volume_mm3':float(vol),'closed_manifold_at_1e_5_mm':True,'components':components,'bounds_local_mm':[v.min(axis=0).tolist(),v.max(axis=0).tolist()]})
(out/'mesh-audit.json').write_text(json.dumps(rows,indent=2));print('PASS ten project meshes: closed, connected and positive volume.')
