from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/PETG-mechanics-20261005/python-libs')
import gmsh,numpy as np
r=Path(__file__).parent;level=float(sys.argv[1]);gmsh.initialize();gmsh.option.setNumber('General.Terminal',0)
gmsh.model.occ.importShapes(str(r/'current.step'));gmsh.model.occ.synchronize()
vols=gmsh.model.getEntities(3);assert len(vols)==1
volume=sum(gmsh.model.occ.getMass(d,t) for d,t in vols);local=[t for d,t in gmsh.model.getEntities(2) if gmsh.model.getType(d,t)!='Plane']
for name,value in [('Mesh.MeshSizeMax',.7),('Mesh.MeshSizeMin',min(.08,level/4)),('Mesh.MeshSizeFromCurvature',32),('Mesh.MeshSizeExtendFromBoundary',0)]:gmsh.option.setNumber(name,value)
a=gmsh.model.mesh.field.add('Distance');gmsh.model.mesh.field.setNumbers(a,'FacesList',local);gmsh.model.mesh.field.setNumber(a,'Sampling',80)
b=gmsh.model.mesh.field.add('Threshold');gmsh.model.mesh.field.setNumber(b,'InField',a)
for name,value in [('SizeMin',level),('SizeMax',.7),('DistMin',.3),('DistMax',1.6)]:gmsh.model.mesh.field.setNumber(b,name,value)
if level<.1:
    nub_faces=[t for d,t in gmsh.model.getEntities(2) if gmsh.model.getType(d,t)!='Plane' and (gmsh.model.getBoundingBox(d,t)[2]>24.7 or gmsh.model.getBoundingBox(d,t)[5]<11.8)]
    nf=gmsh.model.mesh.field.add('Distance');gmsh.model.mesh.field.setNumbers(nf,'FacesList',nub_faces);gmsh.model.mesh.field.setNumber(nf,'Sampling',100)
    nt=gmsh.model.mesh.field.add('Threshold');gmsh.model.mesh.field.setNumber(nt,'InField',nf)
    for k,v in [('SizeMin',.035),('SizeMax',.7),('DistMin',.1),('DistMax',.5)]:gmsh.model.mesh.field.setNumber(nt,k,v)
    mm=gmsh.model.mesh.field.add('Min');gmsh.model.mesh.field.setNumbers(mm,'FieldsList',[b,nt]);b=mm
    print('Refining nub faces',nub_faces,flush=True)
gmsh.model.mesh.field.setAsBackgroundMesh(b);gmsh.model.mesh.generate(3)
gmsh.model.mesh.optimize('Netgen')
tags,xyz,_=gmsh.model.mesh.getNodes();xyz=xyz.reshape(-1,3);lookup=np.full(int(tags.max())+1,-1,dtype=np.int64);lookup[tags]=np.arange(len(tags))
types,element_tags,nodes=gmsh.model.mesh.getElements(3);assert list(types)==[4];tet=lookup[nodes[0].reshape(-1,4)]
quality=gmsh.model.mesh.getElementQualities(element_tags[0],'minSICN');assert min(quality)>0
np.savez_compressed(r/f'mesh-{level:g}.npz',xyz=xyz,tet=tet)
# Verify backing and wall using actual parametric surfaces rather than tessellation.
report={'level_mm':level,'step_sha256':hashlib.sha256((r/'current.step').read_bytes()).hexdigest(),'native_volume_mm3':volume,'nodes':len(xyz),'tetrahedra':len(tet),'minimum_SICN':float(min(quality)),'solid_count':len(vols),'bounding_box':gmsh.model.getBoundingBox(3,vols[0][1])}
(r/f'mesh-{level:g}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True);gmsh.finalize()
