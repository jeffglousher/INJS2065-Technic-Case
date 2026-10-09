"""Read-only independent mechanical review receipts for commit 613402c.
Projects canonical geometry and housing post-tip triangles at Y=10.55.
Counts existing FEM constrained nodes outside actual post-tip support footprints.
No CAD state or FEM solve is altered. Writes receipt only beside this script.
"""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/loose-fit-20261009/python-libs')
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/PETG-mechanics-20261005/python-libs')
import numpy as np
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
source=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/retention-fit-20261009')
repo=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case')
scene_file=source/'candidate-scene.json'; field_file=source/'mesh-0.09.npz'
s=json.loads(scene_file.read_text())
def floors(body):
 m=body['mesh'];xyz=np.array(m['positions']).reshape(-1,3);ix=np.array(m['indices']);tri=[]
 for f in body['faces']:
  p=f.get('plane')
  if p and abs(p['normal'][1])>.99 and abs(p['origin'][1]-10.55)<1e-5:
   ids=ix[f['first_index']:f['first_index']+f['index_count']].reshape(-1,3)
   tri.extend(Polygon(xyz[t][:,[0,2]]) for t in ids)
 return unary_union(tri)
clip=floors(next(b for b in s['bodies'] if b['id']==173))
post=unary_union([floors(next(b for b in s['bodies'] if b['id']==i)) for i in [8,18]])
a=np.load(field_file);xyz,tet=a['xyz'],a['tet'];faces=np.concatenate([tet[:,i] for i in ([0,1,2],[0,1,3],[0,2,3],[1,2,3])]);_,first,count=np.unique(np.sort(faces,axis=1),axis=0,return_index=True,return_counts=True);boundary=faces[first[count==1]]
floor=np.unique(boundary[np.all(abs(xyz[boundary][:,:,1]-10.55)<1e-8,axis=1)])
in_post=np.array([post.buffer(1e-6).covers(Point(xyz[n,[0,2]])) for n in floor])
b=.373205080756889;rr=np.linspace(b,.46,100001)
d=9.8+np.sqrt(np.maximum(0,.64-(rr+.34)**2))-9.809663461670024-np.sqrt(.25-rr**2)
f=json.loads((repo/'review/retention-fit-20261009/patch-sensitivity-0.09.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'commit':'613402c','canonical_sha256':sha(repo/'design/current.model.json'),'scene_source':str(scene_file),'scene_sha256':sha(scene_file),'mesh_field_source':str(field_file),'mesh_field_sha256':sha(field_file),'support_plane_Y_mm':10.55,'fixed_floor_projected_area_mm2':clip.area,'post_tip_projected_area_mm2':post.area,'floor_post_intersection_area_mm2':clip.intersection(post).area,'unsupported_fixed_area_mm2':clip.difference(post).area,'unsupported_fixed_fraction':clip.difference(post).area/clip.area,'floor_nodes':len(floor),'nodes_on_actual_post_tips':int(in_post.sum()),'nodes_off_post_tips':int((~in_post).sum()),'post_node_containment_tolerance_mm':1e-6,'ideal_meridian_required_shift_max_mm':float(d.max()),'ideal_meridian_shift_max_at_radius_mm':float(rr[np.argmax(d)]),'ideal_meridian_sample_count':len(rr),'force_totals_from_existing_screen':[{'support':i['support'],'patch':i['patch_case'],'total_N':sum(i['forces_N_per_patch']),'peak_strain':i['metrics']['max_abs_principal_strain']} for i in f['results']],'interpretation':'Both existing FEM support cases constrain Y displacement on floor surface that includes material facing air. They do not bracket actual unilateral post-tip contacts; these values are not reliable physical preload/insertion estimates. This finding does not establish geometry failure or a corrected force. Area is from native-display triangle projections (not exact OCCT area); FEM node count uses the actual fine mesh. The meridian result independently confirms the idealized 0.020 mm seated-envelope shift, not a solved elastic displacement.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
# Independently cover all native housing material, including any other lands.
from shapely.geometry import LineString
from shapely.ops import polygonize
materials=[]
section_sources=[]
for body_id in [8,18]:
 section_file=repo/f'review/retention-fit-20261009/section-{body_id}-10.55.json'
 section_sources.append({'path':str(section_file),'sha256':sha(section_file)})
 section=json.loads(section_file.read_text())
 lines=[LineString([(round(p[0],7),round(p[1],7)) for p in item['points']]) for item in section['section']]
 polys=list(polygonize(unary_union(lines))); rings=[Polygon(poly.exterior) for poly in polys]
 selected=[poly for poly in polys if sum(ring.covers(poly.representative_point()) for ring in rings)%2==1]
 materials.append(unary_union(selected))
all_material=unary_union(materials)
result.update({'section_sources':section_sources,'all_housing_material_section_plane_Y_mm':10.55,'section_vertex_rounding_mm':1e-7,'section_material_union_area_mm2':all_material.area,'floor_overlap_all_housing_material_mm2':all_material.intersection(clip).area,'additional_floor_support_outside_post_tips_mm2':all_material.difference(post).intersection(clip).area,'section_material_parity_method':'Native OCCT contours polygonized after vertex rounding; polygons selected by odd containing exterior-ring count, excluding bore/hole polygons. Full union of both housing material sections at Y10.55, not only flat post-tip faces.'})
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print('Complete native housing section intersection with clip floor:',all_material.intersection(clip).area)
print('Additional supported area outside post tips:',all_material.difference(post).intersection(clip).area)
