"""Verified quasistatic contact continuation, with a fully released holding solve.

Frictionless rigid native-exported housing; small-strain elastic clip. Surface
quadrature contacts, signed-gap complementarity and mesh Boolean intersections
are checked. This is a numerical experiment, not calibrated print qualification.
"""
import argparse, importlib.metadata, json, time, uuid, faulthandler
from types import SimpleNamespace
from pathlib import Path
from contact import ElasticMesh, SOURCE, OUTPUT, REPO, sha
import numpy as np
import osqp,trimesh,manifold3d
from scipy.sparse import csc_matrix,coo_matrix,vstack

GAP_TOL=2e-5
VOLUME_TOL=1e-7
QP_TOL=2e-7
RUN_ID=uuid.uuid4().hex[:12]

def solid(mesh):
    result=manifold3d.Manifold(manifold3d.Mesh64(
        np.ascontiguousarray(mesh.vertices,dtype=np.float64),
        np.ascontiguousarray(mesh.faces,dtype=np.uint64)))
    assert result.status()==manifold3d.Error.NoError
    return result

def rigid_rotation_check(x,u):
    """Bound the geometric error hidden by zero-energy infinitesimal rotation.

    Least-squares rotational displacement is compared to its exact Rodrigues
    rotation on every mesh node. The approximation error must be below the
    accepted contact gap, rather than an arbitrary angular threshold.
    """
    r=x-x.mean(axis=0);v=u-u.mean(axis=0)
    inertia=np.eye(3)*np.sum(r*r)-r.T@r
    omega=np.linalg.solve(inertia,np.cross(r,v).sum(axis=0))
    angle=float(np.linalg.norm(omega))
    if angle:
        axis=omega/angle
        exact=r*np.cos(angle)+np.cross(axis,r)*np.sin(angle)+np.outer(r@axis,axis)*(1-np.cos(angle))
    else:exact=r.copy()
    linear=r+np.cross(omega,r)
    error=float(np.linalg.norm(exact-linear,axis=1).max())
    result={'infinitesimal_rotation_rad_xyz':omega.tolist(),'angle_rad':angle,
        'maximum_linear_rotation_geometry_error_mm':error,
        'accepted_error_mm':GAP_TOL}
    assert error<GAP_TOL,f'Linear rotation approximation invalid: {result}'
    return result

def housing_meshes():
    shells=[]
    for bid in [8,18]:
        mesh=trimesh.load_mesh(SOURCE/f'candidate-{bid}.stl',process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
        shells.append(mesh)
    return shells

def query(mesh,points):
    """Outside-positive gap; classify planar projections directly, ray-test edges.

    Uses the same documented sign convention as trimesh.signed_distance, without
    repeating the closest-triangle search. Unit checks compare the two methods.
    Capped far-outside gaps return zero normals and invalid triangle IDs; they
    are deliberately outside every sampling/contact selection threshold.
    """
    closest=[];distance=[];face_ids=[];gaps=[];planar_flags=[]
    for start in range(0,len(points),512):
        p=points[start:start+512]
        # Exact near-surface query, conservative positive gap outside the
        # contact search radius. The radius exceeds every contact/near cutoff.
        # This avoids enormous nearest-vertex bounding boxes for points in air.
        radius=.205
        candidates=[list(mesh.triangles_tree.intersection(np.r_[v-radius,v+radius])) for v in p]
        lengths=np.array([len(c) for c in candidates]);found=lengths>0
        q=p.copy();d=np.full(len(p),radius);tid=np.zeros(len(p),dtype=int)
        if found.any():
            owner=np.repeat(np.arange(len(p)),lengths);faces=np.concatenate([c for c in candidates if c]).astype(int)
            closest_candidates=trimesh.triangles.closest_point(mesh.triangles[faces],p[owner])
            squared=np.sum((closest_candidates-p[owner])**2,axis=1)
            offset=0
            for j in np.flatnonzero(found):
                n=lengths[j];k=offset+np.argmin(squared[offset:offset+n]);offset+=n
                near_distance=float(np.sqrt(squared[k]))
                if near_distance<radius:q[j]=closest_candidates[k];d[j]=near_distance;tid[j]=faces[k]
        far=d==radius
        # Deep inside points cannot be dismissed by a bounded outside search.
        inside_far=far & mesh.contains(p)
        if inside_far.any():
            qq,dd,tt=trimesh.proximity.closest_point(mesh,p[inside_far])
            q[inside_far]=qq;d[inside_far]=dd;tid[inside_far]=tt
        face_normal=mesh.face_normals[tid]
        signed_plane=np.einsum('ij,ij->i',p-q,face_normal)
        projected=p-signed_plane[:,None]*face_normal
        bary=trimesh.triangles.points_to_barycentric(mesh.triangles[tid],projected)
        direct=np.all((bary>=-1e-8)&(bary<=1+1e-8),axis=1)
        g=d.copy();g[direct]=np.copysign(d[direct],signed_plane[direct])
        check=(~direct)&(d>1e-8)&(~far|inside_far)
        if check.any():g[check]=np.where(mesh.contains(p[check]),-d[check],d[check])
        g[d<1e-8]=0
        g[far&~inside_far]=radius;tid[far&~inside_far]=-1
        planar_flags.append(direct & np.all(bary>1e-8,axis=1) & (~far|inside_far))
        closest.append(q);distance.append(d);face_ids.append(tid);gaps.append(g)
    q,d,tid,g=np.concatenate(closest),np.concatenate(distance),np.concatenate(face_ids),np.concatenate(gaps)
    n=mesh.face_normals[tid].copy();nonzero=d>1e-8
    n[nonzero]=(points[nonzero]-q[nonzero])/d[nonzero,None]*np.where(g[nonzero]>=0,1.,-1.)[:,None]
    planar=np.concatenate(planar_flags)
    # On a strictly interior orthogonal projection, the distance gradient is
    # exactly the plane normal, even inside. Avoid division-amplified roundoff.
    n[planar]=mesh.face_normals[tid[planar]]
    return n,g,tid

class Samples:
    def __init__(self,elastic,shells,approach,u,dense=1):
        sid=elastic.surface; vertices=elastic.xyz[sid]+u[sid]+[0,approach,0]
        vertex_queries=[query(shell,vertices) for shell in shells]
        near=np.zeros(elastic.n,dtype=bool)
        for n,g,t in vertex_queries:near[sid[g<.20]]=True
        faces=elastic.boundary[np.any(near[elastic.boundary],axis=1)]
        # Vertex rows plus edge midpoints and face interiors; refine near contacts.
        rows=[np.column_stack((sid,sid,sid))];weights=[np.tile([1.,0,0],(len(sid),1))]
        pattern=[]
        subdivisions=2*dense
        for a in range(subdivisions+1):
            for b in range(subdivisions+1-a):
                w=np.array([a,b,subdivisions-a-b],float)/subdivisions
                if w.max()<1:pattern.append(w)
        pattern.append(np.array([1/3,1/3,1/3]))
        for w in pattern:rows.append(faces);weights.append(np.tile(w,(len(faces),1)))
        self.ids=np.concatenate(rows);self.weights=np.concatenate(weights)
        coordinates=self.value(elastic.xyz)
        _,unique=np.unique(np.round(coordinates,9),axis=0,return_index=True)
        unique=np.sort(unique);self.ids=self.ids[unique];self.weights=self.weights[unique]
        self.surface_vertices=len(sid)
    def value(self,field):
        return np.einsum('ni,nij->nj',self.weights,field[self.ids])

def contact_matrix(ids,weights,normal,gap,current,ndof):
    count=len(ids)
    columns=(ids[:,:,None]*3+np.arange(3)).reshape(count,-1)
    values=(weights[:,:,None]*normal[:,None,:]).reshape(count,-1)
    C=coo_matrix((values.ravel(),(np.repeat(np.arange(count),9),columns.ravel())),shape=(count,ndof)).tocsc()
    lower=np.einsum('ij,ij->i',normal,current)-gap
    return C,lower

def irredundant_rows(ids,weights,normals,lower,owners):
    """Drop only inequalities algebraically implied by retained vertex rows.

    If n_sample equals its vertex normals, its row is their nonnegative
    barycentric combination. The combination of lower bounds must be at least
    the sample lower bound. Recheck this every QP; retain all geometry samples.
    """
    vertex={}
    for j,(nodes,w,owner) in enumerate(zip(ids,weights,owners)):
        nz=np.flatnonzero(w>0)
        if len(nz)==1 and abs(w[nz[0]]-1)<1e-15:vertex[(int(owner),int(nodes[nz[0]]))]=j
    keep=np.ones(len(ids),dtype=bool)
    for j,(nodes,w,owner) in enumerate(zip(ids,weights,owners)):
        nz=np.flatnonzero(w>0)
        if len(nz)<=1:continue
        vv=[vertex.get((int(owner),int(nodes[k]))) for k in nz]
        if any(v is None for v in vv):continue
        if np.max(abs(normals[vv]-normals[j]))>1e-12:continue
        if np.dot(w[nz],lower[vv])>=lower[j]-1e-10:keep[j]=False
    return keep

def boolean_check(elastic,shells,u,approach):
    tx=elastic.xyz[elastic.tet];before=np.linalg.det(tx[:,1:]-tx[:,:1])
    deformed=(elastic.xyz+u)[elastic.tet];after=np.linalg.det(deformed[:,1:]-deformed[:,:1])
    ratio=after/before;assert np.all(ratio>0),'Inverted deformed tetrahedron'
    surface=trimesh.Trimesh(vertices=elastic.xyz+u+[0,approach,0],faces=elastic.boundary,process=False)
    surface.remove_unreferenced_vertices();surface.fix_normals(multibody=True)
    assert surface.is_watertight and surface.is_winding_consistent and surface.volume>0
    overlaps=[]
    clip_solid=solid(surface)
    for shell in shells:
        intersection=clip_solid^solid(shell)
        assert intersection.status()==manifold3d.Error.NoError
        overlaps.append(float(max(0,intersection.volume())))
    return {'minimum_deformed_determinant_ratio':float(ratio.min()),
        'maximum_deformed_determinant_ratio':float(ratio.max()),
        'mesh_overlap_volume_mm3_by_shell':overlaps,'maximum_mesh_overlap_mm3':max(overlaps)}

def resultant(force,position):
    return {'force_N':force.sum(axis=0).tolist(),'moment_Nmm':np.cross(position,force).sum(axis=0).tolist()}

def solve(elastic,shells,approach,insertion,initial,centered=False,max_outer=16):
    print(f'Start contact pose: Y approach {approach:g}, insertion {insertion}, centered {centered}',flush=True)
    u=initial.copy();history=[];dense=1;checks=None
    warm=getattr(elastic,'warm_state',{})
    guides=elastic.guides if centered else csc_matrix((0,elastic.ndof));ng=guides.shape[0]
    samples=Samples(elastic,shells,approach,u,dense)
    positions=samples.value(elastic.xyz+u)+[0,approach,0]
    sets=[query(shell,positions) for shell in shells]
    for iteration in range(max_outer):
        current=samples.value(u);positions=samples.value(elastic.xyz)+current+[0,approach,0]
        ids=[];weights=[];normals=[];gaps=[];owners=[];tags=[];sample_ids=[]
        for owner,(normal,gap,tag) in enumerate(sets):
            chosen=np.flatnonzero(gap<.12)
            ids.append(samples.ids[chosen]);weights.append(samples.weights[chosen]);normals.append(normal[chosen]);gaps.append(gap[chosen]);owners.append(np.full(len(chosen),owner));tags.append(tag[chosen]);sample_ids.append(chosen)
        ids,weights,normal,gap=np.concatenate(ids),np.concatenate(weights),np.concatenate(normals),np.concatenate(gaps)
        owners,tags,sample_ids=np.concatenate(owners),np.concatenate(tags),np.concatenate(sample_ids)
        all_lower=np.einsum('ij,ij->i',normal,samples.value(u)[sample_ids])-gap
        keep=irredundant_rows(ids,weights,normal,all_lower,owners)
        omitted=int(np.count_nonzero(~keep))
        ids,weights,normal,gap,owners,tags,sample_ids=[a[keep] for a in [ids,weights,normal,gap,owners,tags,sample_ids]]
        C,lower=contact_matrix(ids,weights,normal,gap,samples.value(u)[sample_ids],elastic.ndof)
        matrices=[guides,C];lo=[np.zeros(ng),lower];hi=[np.zeros(ng),np.full(len(lower),np.inf)]
        if insertion:
            d=elastic.driver;driver=csc_matrix((np.ones(len(d)),(np.arange(len(d)),3*d+1)),shape=(len(d),elastic.ndof))
            matrices.append(driver);lo.append(np.zeros(len(d)));hi.append(np.zeros(len(d)))
        A=vstack(matrices,format='csc');l=np.concatenate(lo);h=np.concatenate(hi)
        print(f'QP assembly: {elastic.ndof} DOFs, {A.shape[0]} rows',flush=True)
        solver=osqp.OSQP();solver.setup(P=elastic.P,q=np.zeros(elastic.ndof),A=A,l=l,u=h,
            eps_abs=QP_TOL,eps_rel=QP_TOL,max_iter=30000,time_limit=300,rho=warm.get('rho',.015),polishing=True,verbose=True,check_termination=50)
        reference_points=samples.value(elastic.xyz)[sample_ids]
        warm_y=np.zeros(A.shape[0])
        if warm:
            old={(int(o),*np.round(p,9)):float(y) for o,p,y in zip(warm['owner'],warm['points'],warm['dual'])}
            warm_y[ng:ng+len(lower)]=[old.get((int(o),*np.round(p,9)),0.) for o,p in zip(owners,reference_points)]
            if len(warm['guide'])==ng:warm_y[:ng]=warm['guide']
            if insertion and len(warm['driver'])==len(elastic.driver):warm_y[ng+len(lower):]=warm['driver']
        solver.warm_start(x=u.ravel(),y=warm_y);print('QP solve',flush=True);r=solver.solve(raise_error=False)
        if r.info.status!='solved':
            failure={'accepted':False,'status':r.info.status,'run_id':RUN_ID,
                'approach_Y_mm':approach,'insertion':insertion,'centered':centered,
                'iteration':iteration,'qp_iterations':r.info.iter,
                'primal_residual':r.info.prim_res,'dual_residual':r.info.dual_res,
                'mesh':elastic.metadata,'contact_rows':len(lower),
                'canonical_sha256':sha(REPO/'design/current.model.json'),
                'solver_sha256':sha(Path(__file__)),
                'note':'Rejected solve; no physical preload or strain inference'}
            (OUTPUT/f'rejected-{RUN_ID}.json').write_text(json.dumps(failure,indent=2)+'\n')
            np.savez_compressed(OUTPUT/f'rejected-{RUN_ID}-seed-only.npz',xyz=elastic.xyz,tet=elastic.tet,u=r.x.reshape(-1,3))
            raise RuntimeError(f'QP not accepted: {r.info.status}')
        candidate=r.x.reshape(-1,3);change=float(np.linalg.norm(candidate-u,axis=1).max())
        warm={'owner':owners,'points':reference_points,'dual':r.y[ng:ng+len(lower)],
            'guide':r.y[:ng],'driver':r.y[ng+len(lower):],
            'rho':float(np.clip(r.info.rho_estimate,1e-5,1e2))}
        elastic.warm_state=warm
        checkpoint=f'trial-{RUN_ID}-{approach:g}-{int(insertion)}-{int(centered)}-{iteration}'
        np.savez_compressed(OUTPUT/f'{checkpoint}.npz',xyz=elastic.xyz,tet=elastic.tet,u=candidate,
            warm_owner=owners,warm_points=reference_points,warm_dual=warm['dual'],
            warm_guide=warm['guide'],warm_driver=warm['driver'],warm_rho=warm['rho'])
        (OUTPUT/f'{checkpoint}.json').write_text(json.dumps({'physical_result_accepted':False,
            'note':'QP checkpoint only; contact, deformed-solid and equilibrium checks still required',
            'solver_sha256':sha(Path(__file__)),'field_sha256':sha(OUTPUT/f'{checkpoint}.npz')},indent=2)+'\n')
        final_positions=samples.value(elastic.xyz+candidate)+[0,approach,0]
        final_sets=[query(shell,final_positions) for shell in shells]
        penetration=max(float(max(0,-g.min())) for n,g,t in final_sets)
        forces=-r.y[ng:ng+len(lower)]
        final_gap=np.concatenate([final_sets[owner][1][sample_ids[owners==owner]] for owner in range(len(shells))])
        complement=float(max(abs(forces*final_gap),default=0))
        history.append({'iteration':iteration,'samples':len(samples.ids),'contact_rows':len(lower),'subdivision_level':dense,
            'algebraically_redundant_rows_omitted':omitted,
            'change_mm':change,'max_sample_penetration_mm':penetration,'exact_gap_complementarity_Nmm':complement,
            'qp_iterations':r.info.iter,'qp_primal_residual':r.info.prim_res,'qp_dual_residual':r.info.dual_res})
        print(json.dumps({'approach':approach,'insertion':insertion,'centered':centered,**history[-1]}),flush=True)
        u=candidate;sets=final_sets
        if change<GAP_TOL and penetration<GAP_TOL and complement<1e-5:
            checks=boolean_check(elastic,shells,u,approach)
            if checks['maximum_mesh_overlap_mm3']<VOLUME_TOL:break
            print('Inter-sample intersection found; refining contact quadrature',checks,flush=True)
            dense*=2
            if dense>4:raise RuntimeError('Surface contact refinement did not resolve overlap')
            samples=Samples(elastic,shells,approach,u,dense)
            positions=samples.value(elastic.xyz+u)+[0,approach,0]
            sets=[query(shell,positions) for shell in shells]
    else:raise RuntimeError('Sequential contact failed convergence checks')
    assert min(forces,default=0)>-2e-5
    residual=elastic.K@u.ravel()+A.T@r.y
    assert np.max(abs(residual))<2e-5
    assert np.max(abs(guides@u.ravel()),initial=0)<2e-6
    if insertion:assert np.max(abs(u[elastic.driver,1]))<2e-6
    contact=(-C.T@r.y[ng:ng+len(lower)]).reshape(-1,3)
    guidance=(-guides.T@r.y[:ng]).reshape(-1,3)
    driving=np.zeros_like(contact)
    if insertion:driving[:,1]=(-matrices[-1].T@r.y[ng+len(lower):]).reshape(-1,3)[:,1]
    all_reaction=contact+guidance+driving
    assert np.linalg.norm(all_reaction.sum(axis=0))<2e-4
    assert np.linalg.norm(np.cross(elastic.xyz,all_reaction).sum(axis=0))<2e-3
    rotation=rigid_rotation_check(elastic.xyz,u)
    metrics=elastic.metrics(u);strains=metrics.pop('strain_field')
    world=elastic.xyz+u+[0,approach,0]
    row={'approach_Y_mm':approach,'outer_face_driver':insertion,'mean_rigid_guides':centered,
        'history':history,'checks':checks,'metrics':metrics,'rigid_rotation_check':rotation,
        'mean_displacement_xyz_mm':u.mean(axis=0).tolist(),
        'resultant_world_origin_mm':[0,0,0],
        'contact_resultant':resultant(contact,world),'guidance_resultant':resultant(guidance,world),
        'driver_resultant':resultant(driving,world),
        'reference_frame_equilibrium':resultant(all_reaction,elastic.xyz),
        'stationarity_infinity_N':float(abs(residual).max()),'contact_positive_reaction_check':True,
        'contact_active_quadrature_points':int(np.count_nonzero(forces>1e-5)),
        'housing_resultants':[]}
    for owner in range(len(shells)):
        mask=owners==owner;physical_force=forces[mask,None]*normal[mask]
        row['housing_resultants'].append(resultant(physical_force,final_positions[sample_ids[mask]]))
    tag=f'{RUN_ID}-{elastic.level:g}-{approach:g}-{int(insertion)}-{int(centered)}'
    row['field_file']=f'verified-{tag}.npz'
    final_normals=np.concatenate([final_sets[owner][0][sample_ids[owners==owner]] for owner in range(len(shells))])
    final_tags=np.concatenate([final_sets[owner][2][sample_ids[owners==owner]] for owner in range(len(shells))])
    row['maximum_force_weighted_normal_change_N']=float(np.linalg.norm(forces[:,None]*(final_normals-normal),axis=1).max(initial=0))
    assert row['maximum_force_weighted_normal_change_N']<2e-5,'Final contact normals disagree with solved reactions'
    np.savez_compressed(OUTPUT/f'verified-{tag}.npz',xyz=elastic.xyz,tet=elastic.tet,u=u,strain=strains,
        contact_node_ids=ids,contact_weights=weights,contact_normals=normal,contact_force=forces,
        contact_owner=owners,linearization_contact_triangle_id=tags,
        final_contact_normals=final_normals,final_contact_triangle_id=final_tags,final_contact_gaps=final_gap)
    row['field_sha256']=sha(OUTPUT/f'verified-{tag}.npz')
    (OUTPUT/f'verified-{tag}.json').write_text(json.dumps(row,indent=2)+'\n')
    return row,u

def checks():
    ids=np.array([[0,0,0],[1,1,1],[0,1,1],[0,1,1]])
    w=np.array([[1.,0,0],[1.,0,0],[.5,.5,0],[.5,.5,0]])
    nn=np.tile([0.,1.,0],(4,1));lo=np.array([.1,.3,.2,.21])
    assert np.array_equal(irredundant_rows(ids,w,nn,lo,np.zeros(4,int)),[True,True,False,True])
    # Integrated assembled contact row: prior displacement, penetration and release.
    for rest,old,expected in [(-.6,.4,.6),(.6,.4,0.)]:
        ids=np.array([[0,0,0]]);w=np.array([[1.,0,0]]);normal=np.array([[1.,0,0]])
        previous=np.array([[old,0,0]]);gap=np.array([rest+old])
        C,lower=contact_matrix(ids,w,normal,gap,previous,3)
        solver=osqp.OSQP();solver.setup(P=csc_matrix(np.eye(3)),q=np.zeros(3),A=C,l=lower,u=np.array([np.inf]),verbose=False,polishing=True,eps_abs=1e-10,eps_rel=1e-10)
        r=solver.solve();assert abs(r.x[0]-expected)<1e-8 and r.y[0]<=1e-8
        assert abs(r.y[0]*(rest+r.x[0]))<1e-8
    box=trimesh.creation.box(extents=[2,2,2]);rng=np.random.default_rng(513)
    points=rng.uniform(-1.5,1.5,(100,3));n,g,t=query(box,points)
    expected=-trimesh.proximity.signed_distance(box,points)
    assert np.max(abs(g-np.minimum(expected,.205)))<1e-8
    if trimesh.ray.has_embree:
        # Verify accelerated ray signs against the original double-precision
        # ray query away from its surface ambiguity band on actual receivers.
        for shell in housing_meshes():
            pp=rng.uniform(shell.bounds[0]-.5,shell.bounds[1]+.5,(100,3))
            _,d,_=trimesh.proximity.closest_point(shell,pp);pp=pp[d>.001]
            accelerated=shell.contains(pp)
            original=trimesh.ray.ray_triangle.RayMeshIntersector(shell).contains_points(pp)
            assert np.array_equal(accelerated,original)
            chosen=rng.choice(len(shell.faces),64,replace=False)
            near=shell.triangles_center[chosen]+rng.uniform(-.02,.02,(len(chosen),1))*shell.face_normals[chosen]
            _,fast,_=query(shell,near)
            full=-trimesh.proximity.signed_distance(shell,near)
            # Trimesh's full query may select a slightly farther near-tied
            # triangle by normal agreement; bound that difference below gap tol.
            assert np.max(abs(fast-np.minimum(full,.205)))<1e-6
    # Boolean check catches interior intersection with no inside cube vertices.
    a=trimesh.creation.box(extents=[4,.2,.2]);b=trimesh.creation.box(extents=[.2,4,.2])
    crossing=solid(a)^solid(b)
    assert crossing.status()==manifold3d.Error.NoError and abs(crossing.volume()-.008)<1e-10
    # Exercise the full production orientation + tetrahedron + Boolean path,
    # including optional dependencies, before starting an expensive solve.
    fixture=SimpleNamespace(xyz=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]],float),
        tet=np.array([[0,1,2,3]]),boundary=np.array([[0,1,2],[0,1,3],[0,2,3],[1,2,3]]))
    remote=trimesh.creation.box();remote.apply_translation([5,0,0])
    assert boolean_check(fixture,[remote],np.zeros((4,3)),0)['maximum_mesh_overlap_mm3']==0
    x=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]],float)
    assert rigid_rotation_check(x,np.cross([0,0,1e-4],x))['angle_rad']>0
    try:rigid_rotation_check(x,np.cross([0,0,.3],x))
    except AssertionError:pass
    else:raise AssertionError('Finite zero-energy rotation was incorrectly accepted')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--level',type=float,choices=[.09,.12],default=.12)
    p.add_argument('--path',type=float,nargs='*',default=[]);p.add_argument('--centered-static',action='store_true')
    p.add_argument('--initial-field',type=Path);p.add_argument('--checks-only',action='store_true')
    args=p.parse_args();checks()
    if args.checks_only:print('Contact, sign, Mesh64 Boolean and rotation checks passed');raise SystemExit(0)
    faulthandler.dump_traceback_later(60,repeat=True);start=time.monotonic()
    e=ElasticMesh(args.level);shells=housing_meshes();u=np.zeros((e.n,3));results=[]
    initial_provenance=None
    if args.initial_field:
        seed=np.load(args.initial_field)
        assert np.array_equal(seed['xyz'],e.xyz) and np.array_equal(seed['tet'],e.tet)
        u=seed['u'];assert u.shape==(e.n,3) and np.isfinite(u).all()
        initial_provenance={'path':str(args.initial_field),'sha256':sha(args.initial_field)}
        if 'warm_owner' in seed:
            assert len(seed['warm_owner'])==len(seed['warm_points'])==len(seed['warm_dual'])
            assert seed['warm_points'].shape==(len(seed['warm_owner']),3)
            assert np.isfinite(seed['warm_dual']).all()
            e.warm_state={'owner':seed['warm_owner'],'points':seed['warm_points'],'dual':seed['warm_dual'],
                'guide':seed['warm_guide'],'driver':seed['warm_driver'],'rho':float(seed['warm_rho'])}
    if args.path:
        assert args.path[0]>=3.2 and args.path[-1]==0 and all(0<a-b<=.05+1e-9 for a,b in zip(args.path,args.path[1:])),'Continuation step must be <= 0.05 mm; repeat with finer stations before interpreting a branch'
        for approach in args.path:
            row,u=solve(e,shells,approach,True,u,centered=True);results.append(row)
    row,u=solve(e,shells,0,False,u,centered=args.centered_static);results.append(row)
    report={'run_id':RUN_ID,'initial_field':initial_provenance,'canonical_sha256':sha(REPO/'design/current.model.json'),'solver_sha256':sha(Path(__file__)),
        'elastic_foundation_sha256':sha(Path(__file__).with_name('contact.py')),'mesh':e.metadata,
        'obstacle_stl_sha256':{str(bid):sha(SOURCE/f'candidate-{bid}.stl') for bid in [8,18]},
        'versions':{x:importlib.metadata.version(x) for x in ['numpy','scipy','osqp','trimesh','manifold3d','embreex','networkx']},
        'numerical_tolerances':{'gap_mm':GAP_TOL,'intersection_mm3':VOLUME_TOL,'qp_abs_rel':QP_TOL},
        'native_obstacle_linear_export_deflection_mm':.0005,'results':results,'seconds':time.monotonic()-start,
        'geometry_changed':False,'contact':'Sequential frictionless native-triangle obstacle contact with surface quadrature and rigid housings',
        'limitations':['Small-strain isotropic clip elasticity and rigid housings; no calibrated printed orthotropy, plasticity, friction, creep or fatigue.','Quasistatic displacement continuation is not a dynamic snap/inertial solution.','Insertion uses centered flat outer-face driving; holding may release all guidance.','Mesh Boolean checks validate triangulated geometry, not exact deformed OCCT solids.','Numerical gap tolerance is finer than native export deflection; not a physical tolerance bound.']}
    suffix='centered' if args.centered_static else ('path' if args.path else 'free')
    (OUTPUT/f'verified-contact-{args.level:g}-{suffix}.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Saved verified contact experiment',flush=True)
