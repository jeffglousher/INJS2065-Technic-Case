import sys,json,time
from pathlib import Path
root=Path(__file__).parent
sys.path.insert(0,str(root/'python-libs'))
import gmsh,numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
level=float(sys.argv[1]) if len(sys.argv)>1 else .35
E=1460.; nu=.38
centers=np.array([[-.85,9.4,22.02],[16.85,9.4,22.02],[-3.8,9.4,14.48],[13.9,9.4,14.48]])
def elasticity(e,nu):
    lam=e*nu/((1+nu)*(1-2*nu)); mu=e/(2*(1+nu))
    d=np.zeros((6,6)); d[:3,:3]=lam; np.fill_diagonal(d[:3,:3],lam+2*mu); d[3:,3:]=np.eye(3)*mu
    return d
D=elasticity(E,nu)
def blocks(x):
    a=np.concatenate((np.ones((len(x),4,1)),x),axis=2)
    vol=np.abs(np.linalg.det(a))/6
    grad=np.linalg.inv(a)[:,1:,:].transpose(0,2,1)
    b=np.zeros((len(x),6,12))
    for i in range(4):
        gx,gy,gz=grad[:,i,:].T
        b[:,0,3*i]=gx;b[:,1,3*i+1]=gy;b[:,2,3*i+2]=gz
        b[:,3,3*i]=gy;b[:,3,3*i+1]=gx
        b[:,4,3*i+1]=gz;b[:,4,3*i+2]=gy
        b[:,5,3*i]=gz;b[:,5,3*i+2]=gx
    return vol,b
# Independent affine patch: uniform uniaxial tension must have sigma_x=E,
# all other stresses zero, for a unit axial strain with Poisson contraction.
tx=np.array([[[0,0,0],[2,0,0],[0,3,0],[0,0,4]]],float)
tv,tb=blocks(tx)
tu=(tx*np.array([1,-nu,-nu])).reshape(1,12)
ts=np.einsum('ij,njk,nk->ni',D,tb,tu)[0]
assert np.max(np.abs(ts-np.array([E,0,0,0,0,0])))<1e-9
assert abs(tv[0]-4)<1e-12
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0)
gmsh.model.occ.importShapes(str(root/'current.step'));gmsh.model.occ.synchronize()
floors=[];local=[]; spheres=[]
for d,t in gmsh.model.getEntities(2):
    bb=gmsh.model.getBoundingBox(d,t);typ=gmsh.model.getType(d,t)
    if abs(bb[1]-10.55)<1e-5 and abs(bb[4]-10.55)<1e-5:floors.append(t)
    if typ!='Plane':local.append(t)
    if typ=='Sphere':spheres.append(t)
# Report actual normal discontinuities at each spherical relief boundary.
joins=[]
for s in spheres:
    for d,e in gmsh.model.getBoundary([(2,s)],oriented=False):
        if d!=1:continue
        adj=gmsh.model.getAdjacencies(1,e)[0]
        bounds=gmsh.model.getParametrizationBounds(1,e)
        p=float((bounds[0][0]+bounds[1][0])/2)
        xyz=gmsh.model.getValue(1,e,[p])
        vals=[]
        for f in adj:
            uv=gmsh.model.getParametrization(2,int(f),xyz.tolist())
            n=gmsh.model.getNormal(int(f),uv).reshape(-1,3)[0];n=n/np.linalg.norm(n)
            vals.append((int(f),n))
        if len(vals)==2:
            angle=float(np.degrees(np.arccos(np.clip(np.dot(vals[0][1],vals[1][1]),-1,1))))
            joins.append(dict(sphere=s,edge=int(e),faces=[v[0] for v in vals],xyz=xyz.tolist(),normal_change_deg=angle))
(root/'relief-junctions.json').write_text(json.dumps(joins,indent=2))
gmsh.option.setNumber('Mesh.MeshSizeMax',.7)
gmsh.option.setNumber('Mesh.MeshSizeMin',min(.08,level/4))
gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',32 if level<.2 else 16)
gmsh.option.setNumber('Mesh.MeshSizeExtendFromBoundary',0)
distance=gmsh.model.mesh.field.add('Distance');gmsh.model.mesh.field.setNumbers(distance,'FacesList',local);gmsh.model.mesh.field.setNumber(distance,'Sampling',80)
threshold=gmsh.model.mesh.field.add('Threshold');gmsh.model.mesh.field.setNumber(threshold,'InField',distance)
for k,v in [('SizeMin',level),('SizeMax',.7),('DistMin',.3),('DistMax',1.6)]:gmsh.model.mesh.field.setNumber(threshold,k,v)
gmsh.model.mesh.field.setAsBackgroundMesh(threshold)
gmsh.model.mesh.generate(3)
tags,xyz,_=gmsh.model.mesh.getNodes(); xyz=xyz.reshape(-1,3)
lookup=np.full(int(tags.max())+1,-1,dtype=np.int64);lookup[tags]=np.arange(len(tags))
types,_,nodes=gmsh.model.mesh.getElements(3)
assert list(types)==[4],types
tet=lookup[nodes[0].reshape(-1,4)]
floor=np.unique(np.concatenate([lookup[gmsh.model.mesh.getNodes(2,t,includeBoundary=True)[0]] for t in floors]))
patches=[]
for corner,c in enumerate(centers):
    ids=[];weights=[]
    for d,t in gmsh.model.getEntities(2):
        typ=gmsh.model.getType(d,t)
        if typ not in ['Torus','Surface of Revolution']:continue
        et,_,en=gmsh.model.mesh.getElements(2,t)
        for ty,nn in zip(et,en):
            if ty!=2:continue
            tri=lookup[nn.reshape(-1,3)];px=xyz[tri];cent=px.mean(axis=1)
            mask=(abs(cent[:,0]-c[0])<.28)&(abs(cent[:,1]-9.8)<.28)
            mask&=(cent[:,2]>24.93) if corner<2 else (cent[:,2]<11.57)
            tri=tri[mask];px=px[mask]
            area=np.linalg.norm(np.cross(px[:,1]-px[:,0],px[:,2]-px[:,0]),axis=1)/2
            ids.extend(tri.ravel());weights.extend(np.repeat(area/3,3))
    w=np.zeros(len(tags));np.add.at(w,ids,weights);w/=w.sum();patches.append(w)
gmsh.finalize()
ndof=3*len(tags);dofs=(tet[:,:,None]*3+np.arange(3)).reshape(-1,12)
rows=[];cols=[];data=[];totalvol=0
for start in range(0,len(tet),10000):
    ids=tet[start:start+10000];v,b=blocks(xyz[ids]);totalvol+=v.sum()
    ke=np.einsum('nki,kl,nlj,n->nij',b,D,b,v,optimize=True)
    ix=dofs[start:start+10000]
    rows.append(np.repeat(ix,12,axis=1).ravel());cols.append(np.tile(ix,(1,12)).ravel());data.append(ke.ravel())
K=coo_matrix((np.concatenate(data),(np.concatenate(rows),np.concatenate(cols))),shape=(ndof,ndof)).tocsr()
del rows,cols,data
force=np.zeros(ndof)
for w in patches:force[1::3]-=w
results=[]
print(json.dumps(dict(level=level,nodes=len(tags),tetrahedra=len(tet),mesh_volume=totalvol,patch_nodes=[int(np.count_nonzero(w)) for w in patches],junction_angle_range=[min(j['normal_change_deg'] for j in joins),max(j['normal_change_deg'] for j in joins)])),flush=True)
for support in ['normal-floor','clamped-floor']:
    if support=='clamped-floor':fixed=(floor[:,None]*3+np.arange(3)).ravel()
    else:
        a=floor[np.argmin(xyz[floor,0])];b=floor[np.argmax(xyz[floor,0])]
        fixed=np.unique(np.r_[floor*3+1,a*3,a*3+2,b*3+2])
    free=np.setdiff1d(np.arange(ndof),fixed)
    t0=time.time();u=np.zeros(ndof);u[free]=spsolve(K[free][:,free],force[free]);u=u.reshape(-1,3)
    reaction=(K@u.ravel()-force).reshape(-1,3)
    response=[float(-np.dot(w,u[:,1])) for w in patches]
    strain=[];stress=[]
    for start in range(0,len(tet),10000):
        ids=tet[start:start+10000];v,b=blocks(xyz[ids]);es=np.einsum('nki,ni->nk',b,u[ids].reshape(-1,12));ss=es@D
        strain.append(es);stress.append(ss)
    strain=np.concatenate(strain);stress=np.concatenate(stress)
    st=np.zeros((len(tet),3,3));st[:,0,0]=strain[:,0];st[:,1,1]=strain[:,1];st[:,2,2]=strain[:,2]
    st[:,0,1]=st[:,1,0]=strain[:,3]/2;st[:,1,2]=st[:,2,1]=strain[:,4]/2;st[:,0,2]=st[:,2,0]=strain[:,5]/2
    principal=np.linalg.eigvalsh(st);absolute=np.max(np.abs(principal),axis=1)
    preload=.02730182005407089;scale=preload/np.mean(response)
    item=dict(support=support,unit_force_N_per_nub=1,deflection_mm_per_N=response,stiffness_N_per_mm=[1/r for r in response],preload_mm=preload,preload_force_N_per_nub=scale,maximum_principal_strain_at_preload=float(absolute.max()*scale),p99_principal_strain_at_preload=float(np.quantile(absolute,.99)*scale),peak_position_mm=xyz[tet[np.argmax(absolute)]].mean(axis=0).tolist(),reaction_N=reaction.sum(axis=0).tolist(),relative_residual=float(np.linalg.norm((K@u.ravel()-force)[free])/np.linalg.norm(force[free])),solve_seconds=time.time()-t0)
    results.append(item);print(json.dumps(item),flush=True)
    np.savez_compressed(root/f'field-{level}-{support}.npz',xyz=xyz,tet=tet,u=u,principal_abs=absolute,scale=scale)
(root/f'fem-{level}.json').write_text(json.dumps(dict(E_MPa=E,poisson=nu,level=level,nodes=len(tags),elements=len(tet),mesh_volume_mm3=totalvol,affine_patch_test_passed=True,results=results),indent=2))
