from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E,sys,math,itertools
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import numpy as np
repo=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-readiness-20261008');project=out/'assembly-petg-hub-quality.3mf';ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=json.loads((repo/'design/current.model.json').read_text())
with zipfile.ZipFile(repo/'design/current.nbcad') as z:
 names=z.namelist();native_name=next(n for n in names if n.endswith('model.json'));assert json.loads(z.read(native_name))==model
manifest=json.loads((out/'assembly-project.json').read_text());records=[]
with zipfile.ZipFile(project) as z:
 for i,p in enumerate(manifest['parts'],1):
  name=f'3D/Objects/object_{i}.model';raw=z.read(name);assert hashlib.sha256(raw).hexdigest()==p['mesh_entry_sha256']
  doc=E.fromstring(raw);v=np.array([[float(e.attrib[k]) for k in ['x','y','z']] for e in doc.findall('.//m:vertex',ns)]);t=np.array([[int(e.attrib[k]) for k in ['v1','v2','v3']] for e in doc.findall('.//m:triangle',ns)])
  assert len(t)==p['triangles'];assert np.isfinite(v).all();assert t.min()>=0 and t.max()<len(v)
  welded,idx=np.unique(np.round(v,5),axis=0,return_inverse=True);tri=idx[t];assert np.all(tri[:,0]!=tri[:,1]) and np.all(tri[:,1]!=tri[:,2]) and np.all(tri[:,2]!=tri[:,0])
  edges=np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]);ee,counts=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True);assert np.all(counts==2),(p['name'],int(np.sum(counts!=2)))
  # Matching forward/reverse directed edge counts establish consistent orientation.
  forward=edges[edges[:,0]<edges[:,1]];assert len(forward)==len(ee);assert len(np.unique(forward,axis=0))==len(ee)
  parent=list(range(len(welded)))
  def find(k):
   while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
   return k
  for a,b in ee:parent[find(int(a))]=find(int(b))
  components=len({find(int(k)) for k in np.unique(tri)});assert components==1
  xyz=v[t];vol=float(np.einsum('ij,ij->i',xyz[:,0],np.cross(xyz[:,1],xyz[:,2])).sum()/6);assert vol>0 and abs(vol-p['volume_mm3'])<.02
  records.append(dict(name=p['name'],triangles=len(t),closed_two_incidence_edges=True,consistent_winding=True,components=components,signed_volume_mm3=vol,plate_bounds_mm=p['plate_bounds_mm']))
 settings=json.loads(z.read('Metadata/project_settings.config'))
 bounds=[p['plate_bounds_mm'] for p in manifest['parts']];bed_margin=min(min(b[0][0],b[1][0],256-b[0][1],256-b[1][1]) for b in bounds)
 gaps=[]
 for a,b in itertools.combinations(bounds,2):
  dx=max(0,a[0][0]-b[0][1],b[0][0]-a[0][1]);dy=max(0,a[1][0]-b[1][1],b[1][0]-a[1][1]);gaps.append(math.hypot(dx,dy))
 assert min(gaps)>15 and bed_margin>20
# Parse the fresh G-code using the reviewed parser without its auditing/plot side effects.
source=(out/'audit.py').read_text();namespace={};exec(source.split('old=parse(oldpath);new=parse(newpath)')[0],namespace);paths=namespace['parse'](out/'slice-final/plate_1.gcode')
cross=[]
for p in paths:
 if p['obj']!=5 or not .2<=p['z']<7.8:continue
 for x,y in p['points']:
  x=abs(x-190);y=abs(y-100)
  if x<.675 and y<2.175 or x<2.175 and y<.675:cross.append((p['feature'],p['z'],x,y))
assert not cross,cross[:10]
resolved=json.loads((out/'slice-final/resolved-settings.json').read_text())
keys=['printer_settings_id','filament_settings_id','nozzle_diameter','nozzle_temperature','nozzle_temperature_initial_layer','textured_plate_temp','textured_plate_temp_initial_layer','curr_bed_type','filament_max_volumetric_speed','filament_flow_ratio','wall_generator','layer_height','initial_layer_print_height','enable_support']
report=dict(canonical_model_sha256=sha(repo/'design/current.model.json'),native_archive_payload_matches=True,project_sha256=sha(project),meshes=records,bed_edge_margin_without_supports_mm=bed_margin,min_object_bbox_gap_mm=min(gaps),technic_socket_interior_extrusion_samples_below_floor=0,technic_test='Hub label 5, Z 0.20 <= Z < 7.80 mm, cross eroded by 0.25 mm; includes support extrusion. Path samples only, not swept bead clearance.',resolved_settings={k:resolved.get(k) for k in keys},no_mesh_self_intersection_test=True,print_sent=False)
(out/'full-project-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
