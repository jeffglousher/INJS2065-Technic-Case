"""Four-load-case compliance screening; no contact or assembly solution.

Adapted from the archived 2026-10-05 linear Tet4 assembly. Requires numpy,
scipy and gmsh in the selected interpreter or --source/python-libs. Input
STEP must be the archived current.step; outputs go beside this script.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--level", type=float, default=0.2)
args = parser.parse_args()
source = args.source.resolve()
out = Path(__file__).resolve().parent
sys.path.insert(0, str(source / "python-libs"))
import gmsh
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu

started = time.monotonic()
E, nu = 1460.0, 0.38
g_nominal = 0.02730182005407089
centers = np.array([[-.85,9.4,22.02],[16.85,9.4,22.02],[-3.8,9.4,14.48],[13.9,9.4,14.48]])

def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

step = source / "current.step"
assert hash_file(step) == "16fcea27f5cef85e050fe2aea1bd8deab5011b71e94501e7192e2e4fc7dcb79a"
lam = E * nu / ((1 + nu) * (1 - 2 * nu))
mu = E / (2 * (1 + nu))
D = np.zeros((6, 6))
D[:3, :3] = lam
np.fill_diagonal(D[:3, :3], lam + 2 * mu)
D[3:, 3:] = np.eye(3) * mu

def blocks(x):
    a = np.concatenate((np.ones((len(x), 4, 1)), x), axis=2)
    volume = np.abs(np.linalg.det(a)) / 6
    grad = np.linalg.inv(a)[:, 1:, :].transpose(0, 2, 1)
    b = np.zeros((len(x), 6, 12))
    for i in range(4):
        gx, gy, gz = grad[:, i, :].T
        b[:, 0, 3*i] = gx
        b[:, 1, 3*i+1] = gy
        b[:, 2, 3*i+2] = gz
        b[:, 3, 3*i] = gy
        b[:, 3, 3*i+1] = gx
        b[:, 4, 3*i+1] = gz
        b[:, 4, 3*i+2] = gy
        b[:, 5, 3*i] = gz
        b[:, 5, 3*i+2] = gx
    return volume, b

tx = np.array([[[0,0,0],[2,0,0],[0,3,0],[0,0,4]]], float)
tv, tb = blocks(tx)
tu = (tx * np.array([1, -nu, -nu])).reshape(1, 12)
ts = np.einsum('ij,njk,nk->ni', D, tb, tu)[0]
assert np.max(np.abs(ts - np.array([E,0,0,0,0,0]))) < 1e-9
assert abs(tv[0] - 4) < 1e-12

gmsh.initialize()
gmsh.option.setNumber('General.Terminal', 0)
try:
    gmsh.model.occ.importShapes(str(step))
    gmsh.model.occ.synchronize()
    occt_volume = sum(gmsh.model.occ.getMass(dim, tag) for dim, tag in gmsh.model.getEntities(3))
    floors, local = [], []
    for dim, tag in gmsh.model.getEntities(2):
        bb = gmsh.model.getBoundingBox(dim, tag)
        kind = gmsh.model.getType(dim, tag)
        if abs(bb[1] - 10.55) < 1e-5 and abs(bb[4] - 10.55) < 1e-5:
            floors.append(tag)
        if kind != 'Plane':
            local.append(tag)
    assert floors and local
    gmsh.option.setNumber('Mesh.MeshSizeMax', .7)
    gmsh.option.setNumber('Mesh.MeshSizeMin', min(.08, args.level/4))
    gmsh.option.setNumber('Mesh.MeshSizeFromCurvature', 32 if args.level < .2 else 16)
    gmsh.option.setNumber('Mesh.MeshSizeExtendFromBoundary', 0)
    distance = gmsh.model.mesh.field.add('Distance')
    gmsh.model.mesh.field.setNumbers(distance, 'FacesList', local)
    gmsh.model.mesh.field.setNumber(distance, 'Sampling', 80)
    threshold = gmsh.model.mesh.field.add('Threshold')
    gmsh.model.mesh.field.setNumber(threshold, 'InField', distance)
    for key, value in [('SizeMin', args.level), ('SizeMax', .7), ('DistMin', .3), ('DistMax', 1.6)]:
        gmsh.model.mesh.field.setNumber(threshold, key, value)
    gmsh.model.mesh.field.setAsBackgroundMesh(threshold)
    gmsh.model.mesh.generate(3)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    xyz = xyz.reshape(-1, 3)
    lookup = np.full(int(tags.max())+1, -1, dtype=np.int64)
    lookup[tags] = np.arange(len(tags))
    types, _, nodes = gmsh.model.mesh.getElements(3)
    assert list(types) == [4], types
    tet = lookup[nodes[0].reshape(-1, 4)]
    assert np.all(tet >= 0)
    floor = np.unique(np.concatenate([lookup[gmsh.model.mesh.getNodes(2, tag, includeBoundary=True)[0]] for tag in floors]))
    assert np.all(floor >= 0)
    qualities = gmsh.model.mesh.getElementQualities(gmsh.model.mesh.getElements(3)[1][0], 'minSICN')
    assert np.all(np.isfinite(qualities)) and np.min(qualities) > 0
    patches = []
    patch_metadata = []
    for corner, center in enumerate(centers):
        ids, weights = [], []
        for dim, tag in gmsh.model.getEntities(2):
            if gmsh.model.getType(dim, tag) not in ['Torus', 'Surface of Revolution']:
                continue
            element_types, _, element_nodes = gmsh.model.mesh.getElements(2, tag)
            for kind, nn in zip(element_types, element_nodes):
                if kind != 2:
                    continue
                tri = lookup[nn.reshape(-1, 3)]
                points = xyz[tri]
                centroid = points.mean(axis=1)
                mask = (abs(centroid[:,0]-center[0]) < .28) & (abs(centroid[:,1]-9.8) < .28)
                mask &= (centroid[:,2] > 24.93) if corner < 2 else (centroid[:,2] < 11.57)
                tri, points = tri[mask], points[mask]
                area = np.linalg.norm(np.cross(points[:,1]-points[:,0], points[:,2]-points[:,0]), axis=1)/2
                ids.extend(tri.ravel())
                weights.extend(np.repeat(area/3, 3))
        w = np.zeros(len(tags))
        np.add.at(w, ids, weights)
        assert w.sum() > 0
        patch_area = float(w.sum())
        w /= w.sum()
        patches.append(w)
        selected_xyz = xyz[w > 0]
        patch_metadata.append(dict(area_mm2=patch_area,area_weighted_centroid_xyz_mm=(w@xyz).tolist(),node_bounds_xyz_mm=[selected_xyz.min(axis=0).tolist(),selected_xyz.max(axis=0).tolist()]))
finally:
    gmsh.finalize()

ndof = 3 * len(tags)
dofs = (tet[:,:,None]*3 + np.arange(3)).reshape(-1,12)
rows, cols, data = [], [], []
total_volume = 0.0
for start in range(0, len(tet), 10000):
    ids = tet[start:start+10000]
    volume, b = blocks(xyz[ids])
    assert np.all(volume > 1e-15)
    total_volume += float(volume.sum())
    ke = np.einsum('nki,kl,nlj,n->nij', b, D, b, volume, optimize=True)
    index = dofs[start:start+10000]
    rows.append(np.repeat(index,12,axis=1).ravel())
    cols.append(np.tile(index,(1,12)).ravel())
    data.append(ke.ravel())
K = coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(ndof,ndof)).tocsr()
del rows, cols, data
volume_relative_error = abs(total_volume/occt_volume - 1)
assert np.isfinite(occt_volume) and occt_volume > 0 and volume_relative_error < .001
loads = np.zeros((ndof, 4))
for i, w in enumerate(patches):
    loads[1::3,i] = -w
results = []
for support in ['normal-floor', 'clamped-floor']:
    start = time.monotonic()
    if support == 'clamped-floor':
        fixed = (floor[:,None]*3 + np.arange(3)).ravel()
    else:
        anchor_a = floor[np.argmin(xyz[floor,0])]
        anchor_b = floor[np.argmax(xyz[floor,0])]
        fixed = np.unique(np.r_[floor*3+1,anchor_a*3,anchor_a*3+2,anchor_b*3+2])
    free = np.setdiff1d(np.arange(ndof), fixed)
    factor = splu(K[free][:,free].tocsc())
    u = np.zeros((ndof,4))
    u[free] = factor.solve(loads[free])
    C = loads.T @ u
    symmetry = float(np.max(abs(C-C.T))/np.max(abs(C)))
    eigen = np.linalg.eigvalsh((C+C.T)/2)
    residual = K @ u - loads
    relative_residuals = [float(np.linalg.norm(residual[free,j])/np.linalg.norm(loads[free,j])) for j in range(4)]
    reactions, reaction_moments, external_moments, energies = [], [], [], []
    for j in range(4):
        # Only constrained DOFs contribute support reaction; free residuals
        # are equilibrium error rather than an additional physical reaction.
        supported = np.zeros(ndof)
        supported[fixed] = residual[fixed,j]
        reaction_vector = supported.reshape(-1,3).sum(axis=0)
        applied_vector = loads[:,j].reshape(-1,3).sum(axis=0)
        reaction_moment = np.cross(xyz,supported.reshape(-1,3)).sum(axis=0)
        external_moment = np.cross(xyz,loads[:,j].reshape(-1,3)).sum(axis=0)
        assert np.linalg.norm(reaction_vector+applied_vector) < 1e-8
        assert np.linalg.norm(reaction_moment+external_moment) < 1e-8
        reactions.append(reaction_vector.tolist())
        reaction_moments.append(reaction_moment.tolist())
        external_moments.append(external_moment.tolist())
        internal_energy = float(.5*np.dot(u[:,j],K@u[:,j]))
        load_work = float(.5*np.dot(u[:,j],loads[:,j]))
        energy_error = abs(internal_energy/load_work-1)
        assert np.isfinite(internal_energy) and internal_energy > 0 and energy_error < 1e-9
        energies.append(dict(internal_Nmm=internal_energy,half_load_work_Nmm=load_work,relative_error=energy_error))
    simultaneous_displacements = C @ np.ones(4)
    independently_solved_sum = np.zeros(ndof)
    independently_solved_sum[free] = factor.solve(loads[free].sum(axis=1))
    simultaneously_recomputed = loads.T @ independently_solved_sum
    superposition_error = float(np.max(abs(simultaneously_recomputed-simultaneous_displacements)))
    # Linear algebra target illustration only: assumes four equal displacement
    # constraints on the prescribed patches. No gaps, unilateral contacts or
    # housing interface are solved by this equation.
    target_force = np.linalg.solve(C, np.full(4,g_nominal))
    diagonal_force = g_nominal / np.diag(C)
    equal_force = g_nominal / np.mean(simultaneous_displacements)
    unit_work = float(np.sum(C)/2)
    target_work = float(.5*np.dot(np.full(4,g_nominal),target_force))
    offdiag = C - np.diag(np.diag(C))
    item = dict(support=support,compliance_mm_per_N=C.tolist(),compliance_eigenvalues_mm_per_N=eigen.tolist(),reciprocity_relative_error=symmetry,free_equilibrium_relative_residuals=relative_residuals,unit_load_reactions_N=reactions,simultaneous_1N_per_patch_displacement_mm=simultaneous_displacements.tolist(),superposition_max_error_mm=superposition_error,off_diagonal_row_sum_relative_to_diagonal=(offdiag.sum(axis=1)/np.diag(C)).tolist(),isolated_single_patch_stiffness_N_per_mm=(1/np.diag(C)).tolist(),historical_equal_force_for_mean_target_N_per_patch=float(equal_force),illustrative_equal_displacement_target_mm=g_nominal,illustrative_equal_displacement_forces_N=target_force.tolist(),incorrect_independent_diagonal_forces_N=diagonal_force.tolist(),unit_equal_force_elastic_work_Nmm=unit_work,illustrative_equal_displacement_work_Nmm=target_work,seconds=time.monotonic()-start)
    assert np.all(np.isfinite(C)) and np.all(eigen > 0)
    assert symmetry < 1e-9 and max(relative_residuals) < 1e-8
    assert superposition_error < 1e-12
    assert all(abs(r[1]-1) < 1e-8 for r in reactions)
    item.update(unit_load_reaction_moments_Nmm_about_origin=reaction_moments,unit_load_external_moments_Nmm_about_origin=external_moments,unit_load_energy_checks=energies,independently_solved_simultaneous_displacements_mm=simultaneously_recomputed.tolist(),absolute_off_diagonal_row_sum_relative_to_diagonal=(abs(offdiag).sum(axis=1)/np.diag(C)).tolist())
    results.append(item)
    print(json.dumps(item),flush=True)
    del factor, u

report = dict(reviewed_at='2026-10-06',study='four single-patch linear Tet4 compliance',geometry_changed=False,contact_solved=False,E_MPa=E,poisson_assumed=nu,level_mm=args.level,nodes=len(tags),tetrahedra=len(tet),volume_mm3=total_volume,occt_imported_volume_mm3=occt_volume,mesh_volume_relative_error=volume_relative_error,min_SICN=float(np.min(qualities)),negative_quality_element_count=int(np.count_nonzero(qualities < 0)),patch_node_counts=[int(np.count_nonzero(w)) for w in patches],relief_reference_centers_xyz_mm=centers.tolist(),load_patch_metadata=patch_metadata,affine_patch_test_passed=True,step_sha256=hash_file(step),archival_fem_script_sha256=hash_file(source/'fem.py'),script_sha256=hash_file(Path(__file__)),numpy_version=np.__version__,gmsh_version=gmsh.__version__,python_version=sys.version,total_seconds=time.monotonic()-started,results=results,limitations=['Single mesh per report; compare reports for measured refinement differences.','Bilateral fixed-floor idealizations do not bound actual unilateral housing contact; finite normal-load patches, no friction.','Equal-displacement solution is illustrative linear algebra, not installed contact forces.','Isotropic V2 material surrogate; current V3 formulation and toolpath anisotropy uncalibrated.'])
destination = out / f'compliance-{args.level:g}.json'
destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(str(destination),flush=True)
