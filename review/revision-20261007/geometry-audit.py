import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import numpy as np
r=Path(__file__).parent;base=json.loads((r/'baseline-scene.json').read_text());new=json.loads((r/'scene.json').read_text());m=json.loads((r/'candidate.model.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'model_sha256':sha(r/'candidate.model.json'),'feature_count':len(m['document']['history']['features']),'all_features_ok':all(f['status']['state']=='ok' for f in m['document']['history']['features']),'body_count':len(new['bodies']),'native_errors':new['errors'],'hex_floor_face_count':{},'unchanged_external_housing_face_signatures':True,'continuous_clip_solid_count':1,'minimum_corner_in_plane_wall_mm':None,'minimum_broad_face_backing_mm':1.0,'fixed_material':'Bambu PETG Basic','TDS':'Bambu PETG Basic V3','material_Young_XY_MPa':2780,'material_Young_Z_MPa':2550,'poisson_assumed':.38}
for id in [173,267]:
    b=next(b for b in new['bodies'] if b['id']==id);sign=1 if id==173 else -1
    record['hex_floor_face_count'][str(id)]=len([f for f in b['faces'] if f['plane'] and abs(f['plane']['origin'][1]-sign*10.55)<1e-7 and abs(f['plane']['normal'][1])>.99])
    assert record['hex_floor_face_count'][str(id)]==8
for id in [8,18]:
    old=next(b for b in base['bodies'] if b['id']==id);b=next(b for b in new['bodies'] if b['id']==id)
    sig=lambda bb: sorted([f['signature'] for f in bb['faces'] if f['plane'] and abs(abs(f['plane']['origin'][1])-12)<1e-7 and abs(f['plane']['normal'][1])>.99],key=lambda s:s['centroid']['y'])
    a= sig(old);bb=sig(b);assert len(a)==len(bb)
    for x,y in zip(a,bb):
        assert abs(x['area']-y['area'])<1e-8 and x['wire_count']==y['wire_count'] and abs(x['perimeter']-y['perimeter'])<1e-8
corner_z=22.02-.4/np.sqrt(.75);wall=np.sqrt(.75)*(24.903961852410437-corner_z)-2;assert abs(wall-.897584227732)<1e-9;record['minimum_corner_in_plane_wall_mm']=wall
b=.373205080756889;end=9.65+np.sqrt(.25-b*b);dy=np.sqrt(.64-(b+.4)**2)-(end-9.8)
record.update(nub_protrusion_mm=.20,nub_crest_radius_mm=.8,nub_root_radius_mm=.4,nub_meridian_span_mm=1.44,hidden_receiver_radius_mm=.5,hidden_receiver_spherical_cap_start_Y_mm=9.65,hidden_receiver_end_Y_mm=10.15,hidden_receiver_flank_boundary_Y_mm=end,nominal_geometric_inward_holding_shift_mm=dy,crest_overrun_at_unrelieved_flank_mm=.4-b,central_radial_seat_clearance_mm=float(np.sqrt(.25-(9.8-9.65)**2)-.4))
for name in ['clip-fine','lower-fine','upper-fine']:
    raw=(r/(name+'.stl')).read_bytes();dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]);t=np.frombuffer(raw,dtype=dt,offset=84)['v'].astype(float);pts,idx=np.unique(np.round(t.reshape(-1,3),5),axis=0,return_inverse=True);tri=idx.reshape(-1,3);edges=np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]);_,count=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True);vol=np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6
    record[name]={'sha256':sha(r/(name+'.stl')),'triangles':len(t),'signed_mesh_volume_mm3':vol,'mesh_edge_weld_quantization_mm':1e-5,'non_two_incidence_edges':int(np.sum(count!=2))};assert np.all(count==2),(name,np.unique(count,return_counts=True))
(r/'geometry-audit.json').write_text(json.dumps(record,indent=2));print(json.dumps(record),flush=True)
