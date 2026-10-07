"""Same-mesh linear PETG Basic V3 load-patch sensitivity, not contact FEA.

Usage: py -3 patch-sensitivity.py --source <archived PETG-mechanics directory>
Reuses its verified finest mesh. No CAD or historical evidence is modified.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--level',type=float,choices=[.09,.12],default=.09)
args=p.parse_args();src=args.source.resolve();out=Path(__file__).resolve().parent
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/PETG-mechanics-20261005/python-libs')
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
started=time.monotonic()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
geometry=json.loads((src/f'mesh-{args.level:g}.json').read_text())
field=src/f'mesh-{args.level:g}.npz'
a=np.load(field);xyz,tet=a['xyz'],a['tet'];N=len(xyz);seat_end=9.65+(0.5**2-0.373205080756889**2)**0.5;target=(0.8**2-(0.373205080756889+0.4)**2)**0.5-(seat_end-9.8)
E,nu=2780.,.38
lam=E*nu/((1+nu)*(1-2*nu));mu=E/(2*(1+nu))
D=np.zeros((6,6));D[:3,:3]=lam;np.fill_diagonal(D[:3,:3],lam+2*mu);D[3:,3:]=np.eye(3)*mu
def blocks(x):
    aa=np.concatenate((np.ones((len(x),4,1)),x),axis=2)
    volume=np.abs(np.linalg.det(aa))/6;grad=np.linalg.inv(aa)[:,1:,:].transpose(0,2,1)
    b=np.zeros((len(x),6,12))
    for i in range(4):
        gx,gy,gz=grad[:,i,:].T
        b[:,0,3*i]=gx;b[:,1,3*i+1]=gy;b[:,2,3*i+2]=gz
        b[:,3,3*i]=gy;b[:,3,3*i+1]=gx
        b[:,4,3*i+1]=gz;b[:,4,3*i+2]=gy
        b[:,5,3*i]=gz;b[:,5,3*i+2]=gx
    return volume,b
tx=np.array([[[0,0,0],[2,0,0],[0,3,0],[0,0,4]]],float)
v,b=blocks(tx);ts=D@b[0]@(tx*np.array([1,-nu,-nu])).ravel()
assert np.max(abs(ts-np.array([E,0,0,0,0,0])))<1e-9 and abs(v[0]-4)<1e-12
faces=np.concatenate([tet[:,ids] for ids in ([0,1,2],[0,1,3],[0,2,3],[1,2,3])])
_,first,count=np.unique(np.sort(faces,axis=1),axis=0,return_index=True,return_counts=True)
boundary=faces[first[count==1]];points=xyz[boundary];centroid=points.mean(axis=1)
floor=np.unique(boundary[np.all(abs(points[:,:,1]-10.55)<1e-8,axis=1)])
assert len(floor)>0
area=np.linalg.norm(np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0]),axis=1)/2
corners=[(-.85,24.703961852410437,1),(16.85,24.703961852410437,1),(-3.8,11.796038147589564,-1),(13.9,11.796038147589564,-1)]
scenarios=[('crest-broad',.28,.28,9.8),('flanks-wide',.10,.12,seat_end),('flanks-narrow',.06,.06,seat_end)]
weights=[];metadata=[]
for name,hx,hy,cy in scenarios:
    rows=[]
    for cx,cz,sign in corners:
        dy=points[:,:,1]-9.8
        profile=-.4+np.sqrt(np.maximum(0,.64-dy**2))
        radius=np.sqrt((points[:,:,0]-cx)**2+(points[:,:,2]-cz)**2)
        curved=np.all((abs(radius-profile)<1e-6)&(abs(dy)<=.48+1e-8),axis=1)
        mask=curved & (abs(centroid[:,1]-cy)<hy)
        if name=='crest-broad':mask &= abs(centroid[:,0]-cx)<hx
        else:mask &= abs(abs(centroid[:,0]-cx)-.19)<hx
        mask &= (centroid[:,2]>24.93) if sign>0 else (centroid[:,2]<11.57)
        tri=boundary[mask];w=np.zeros(N);np.add.at(w,tri.ravel(),np.repeat(area[mask]/3,3))
        patch_area=w.sum();assert patch_area>0,(name,cx)
        w/=patch_area;weights.append(w)
        rows.append({'area_mm2':float(patch_area),'nodes':int(np.count_nonzero(w)),'triangles':len(tri),'centroid_xyz_mm':(w@xyz).tolist(),'bounds_xyz_mm':[xyz[w>0].min(axis=0).tolist(),xyz[w>0].max(axis=0).tolist()]})
    metadata.append({'name':name,'selection_half_width_x_mm':hx,'selection_half_width_Y_mm':hy,'center_Y_mm':cy,'patches':rows})

print(json.dumps({'nodes':N,'tets':len(tet),'floor_nodes':len(floor),'patches':metadata}),flush=True)
ndof=3*N;dofs=(tet[:,:,None]*3+np.arange(3)).reshape(-1,12)
rows,cols,data=[],[],[];volumes=[]
for start in range(0,len(tet),10000):
    ids=tet[start:start+10000];v,b=blocks(xyz[ids]);assert np.all(v>1e-15);volumes.append(v)
    ke=np.einsum('nki,kl,nlj,n->nij',b,D,b,v,optimize=True);ix=dofs[start:start+10000]
    rows.append(np.repeat(ix,12,axis=1).ravel());cols.append(np.tile(ix,(1,12)).ravel());data.append(ke.ravel())
K=coo_matrix((np.concatenate(data),(np.concatenate(rows),np.concatenate(cols))),shape=(ndof,ndof)).tocsr()
del rows,cols,data,faces,points
volumes=np.concatenate(volumes);assert abs(volumes.sum()/geometry['native_volume_mm3']-1)<.001
loads=np.zeros((ndof,len(weights)))
for j,w in enumerate(weights):loads[1::3,j]=-w
def tensor(components,shear_factor):
    t=np.zeros((len(components),3,3));t[:,0,0]=components[:,0];t[:,1,1]=components[:,1];t[:,2,2]=components[:,2]
    t[:,0,1]=t[:,1,0]=components[:,3]*shear_factor;t[:,1,2]=t[:,2,1]=components[:,4]*shear_factor;t[:,0,2]=t[:,2,0]=components[:,5]*shear_factor
    return t
def metrics(u):
    ep,sp=[],[]
    for start in range(0,len(tet),10000):
        ids=tet[start:start+10000];_,b=blocks(xyz[ids]);e=np.einsum('nki,ni->nk',b,u[ids].reshape(-1,12));ep.append(e);sp.append(e@D)
    e,s=np.concatenate(ep),np.concatenate(sp)
    absolute=np.max(abs(np.linalg.eigvalsh(tensor(e,.5))),axis=1)
    principal=np.linalg.eigvalsh(tensor(s,1))
    vm=np.sqrt(.5*((s[:,0]-s[:,1])**2+(s[:,1]-s[:,2])**2+(s[:,2]-s[:,0])**2)+3*np.sum(s[:,3:]**2,axis=1))
    order=np.argsort(absolute);cw=np.cumsum(volumes[order])/volumes.sum()
    energy=.5*np.sum(e*s,axis=1)*volumes
    centers=xyz[tet].mean(axis=1);nub_zone=np.zeros(len(tet),dtype=bool)
    for cx,cz,sign in corners:nub_zone|=(abs(centers[:,0]-cx)<.5)&(abs(centers[:,1]-9.8)<.65)&(sign*(centers[:,2]-cz)>.15)
    return {'max_abs_principal_strain':float(absolute.max()),'volume_weighted_p99_abs_principal_strain':float(absolute[order[np.searchsorted(cw,.99)]]),'peak_strain_position_xyz_mm':xyz[tet[np.argmax(absolute)]].mean(axis=0).tolist(),'max_tensile_principal_stress_MPa':float(principal[:,-1].max()),'max_von_mises_stress_MPa':float(vm.max()),'volume_fraction_above_1pct_principal_strain':float(volumes[absolute>.01].sum()/volumes.sum()),'elastic_energy_share_in_geometric_nub_zone':float(energy[nub_zone].sum()/energy.sum()),'nub_zone_definition':'Element centroid within 0.5 mm in X, 0.65 mm in Y of nub axis, radial Z beyond 0.15 mm; descriptive region, not a strain acceptance criterion.'}
results=[]
for support in ['normal-floor','clamped-floor']:
    t0=time.monotonic()
    if support=='clamped-floor':fixed=(floor[:,None]*3+np.arange(3)).ravel()
    else:
        aa=floor[np.argmin(xyz[floor,0])];bb=floor[np.argmax(xyz[floor,0])]
        fixed=np.unique(np.r_[floor*3+1,aa*3,aa*3+2,bb*3+2])
    free=np.setdiff1d(np.arange(ndof),fixed);factor=splu(K[free][:,free].tocsc())
    U=np.zeros((ndof,len(weights)));U[free]=factor.solve(loads[free]);res=K@U-loads
    rel=[float(np.linalg.norm(res[free,j])/np.linalg.norm(loads[free,j])) for j in range(len(weights))]
    assert max(rel)<1e-8
    for j in range(len(weights)):
        rr=np.zeros(ndof);rr[fixed]=res[fixed,j]
        assert np.linalg.norm((rr+loads[:,j]).reshape(-1,3).sum(axis=0))<1e-8
        assert np.linalg.norm(np.cross(xyz,(rr+loads[:,j]).reshape(-1,3)).sum(axis=0))<1e-8
    for i,(name,*_) in enumerate(scenarios):
        ix=slice(4*i,4*i+4);L=loads[:,ix];u_basis=U[:,ix];C=L.T@u_basis
        assert np.max(abs(C-C.T))/np.max(abs(C))<1e-9 and np.min(np.linalg.eigvalsh(C))>0
        forces=np.linalg.solve(C,np.full(4,target));u=(u_basis@forces).reshape(-1,3)
        assert np.max(abs(L.T@u.ravel()-target))<1e-10
        reaction=K@u.ravel()-L@forces
        energy=float(.5*u.ravel()@(K@u.ravel()));work=float(.5*u.ravel()@(L@forces))
        assert abs(energy/work-1)<1e-8
        item={'support':support,'patch_case':name,'target_equal_patch_displacement_mm':target,'forces_N_per_patch':forces.tolist(),'stiffness_N_per_mm':(forces/target).tolist(),'compliance_mm_per_N':C.tolist(),'elastic_energy_Nmm':energy,'metrics':metrics(u),'relative_residual_max':max(rel)}
        results.append(item);print(json.dumps({k:v for k,v in item.items() if k!='compliance_mm_per_N'}),flush=True)
    print('support completed',support,time.monotonic()-t0,flush=True)
    del factor,U
report={'reviewed_at':'2026-10-07','study':'Revised CAD V3 PETG Basic axial load-patch screening','E_MPa':E,'poisson_assumed':nu,'level_mm':args.level,'seat_end_Y_mm':seat_end,'nominal_geometric_inward_shift_mm':target,'nodes':N,'tetrahedra':len(tet),'geometry_changed':True,'contact_solved':False,'step_sha256':sha(src/'current.step'),'mesh_field_sha256':sha(field),'script_sha256':sha(Path(__file__)),'mesh_volume_mm3':float(volumes.sum()),'affine_patch_check_passed':True,'patch_metadata':metadata,'results':results,'total_seconds':time.monotonic()-started,'limitations':['Finite assumed axial-pressure patches, not a unilateral contact solve or solved insertion path.','Finite flank patches extend beyond the nominal engagement band; true contact footprint remains unresolved.','Load-patch sensitivity and measured mesh-level changes, not local peak-strain convergence.','Bilateral floor supports and isotropic solid V3 coupon stiffness; no calibrated printed orthotropy, plasticity, friction, creep or fatigue.','Peak elastic stress is a model-validity warning, not a strength safety factor.']}
destination=out/f'patch-sensitivity-{args.level:g}.json'
destination.write_text(json.dumps(report,indent=2)+'\n')
print('Saved',destination,flush=True)
