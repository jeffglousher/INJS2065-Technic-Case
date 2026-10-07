"""Read-only kinematic audit: native face planes + saved exact revolve profile.

The crest-centered slice misses the two diagonal flank contacts. This audit
checks those contacts separately; it is not an elastic or insertion simulation.
"""
import sys,json,math
from pathlib import Path
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
R=Path(__file__).parent
O=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/fit-review-20261007')
model=json.loads((O.parents[1]/'design/current.model.json').read_text())
scene=json.loads((R/'scene.json').read_text())
profile=next(s for s in model['sketches'] if s['feature_id']==755)
receiver=next(s for s in model['sketches'] if s['feature_id']==765)
entities={k:v for k,v in profile['snapshot']['entities']}
seat={k:v for k,v in receiver['snapshot']['entities']}
axis_z=next(r for r in model['revolves'] if r['feature_id']==756)['axis_origin']['y']
center_y=entities[34]['position']['x'];crest_z=entities[34]['position']['y']
arc=entities[32];arc_R=arc['radius'];arc_center_offset=arc['center']['y']-axis_z
seat_end=seat[2]['position']['x'];receiver_R=seat[4]['position']['y']-axis_z
crest_R=crest_z-axis_z
rows=[]
for name,x,z,body,sign in [('upper-left',-.85,axis_z,18,1),('upper-right',16.85,axis_z,18,1),('lower-left',-3.8,36.5-axis_z,8,-1),('lower-right',13.9,36.5-axis_z,8,-1)]:
    planes=[]
    for f in next(b for b in scene['bodies'] if b['id']==body)['faces']:
        if not f['plane'] or not f['signature']:continue
        p=f['plane'];c=f['signature']['centroid']
        if not p or c['y']<0 or abs(c['x']-x)>3 or abs(c['z']-z)>2:continue
        n=np.array(p['normal'])
        if abs(abs(n[2])-math.sqrt(3)/2)>1e-8 or abs(n[1])>1e-8:continue
        d=abs(np.dot(n,np.array(p['origin'])-np.array([x,center_y,z])))
        if .35<d<.40:planes.append((f['id'],float(d)))
    assert len(planes)==2,(name,planes)
    b=sum(d for _,d in planes)/2
    r_at_lip=arc_center_offset+math.sqrt(arc_R**2-(seat_end-center_y)**2)
    half_overrun=math.sqrt(arc_R**2-(b-arc_center_offset)**2)
    rows.append({'corner':name,'housing_body':body,'native_roof_face_ids':[i for i,_ in planes],
      'axis_mm':[x,center_y,z],'housing_flank_plane_distance_from_axis_mm':b,
      'crest_radial_radius_mm':crest_R,'receiver_radial_radius_mm':receiver_R,
      'radial_crest_to_seat_clearance_mm':receiver_R-crest_R,
      'radial_flank_excess_at_receiver_end_mm':r_at_lip-b,
      'radial_crest_excess_above_unrelieved_flank_mm':crest_R-b,
      'installed_rigid_envelope_inward_Y_shift_to_clear_end_mm':half_overrun-(seat_end-center_y)})
result={'reviewedAt':'2026-10-07','canonicalModelSha256':json.loads((R/'replay.json').read_text())['canonicalModelSha256'],
 'method':'Exact saved circular nub arc and native OCCT roof-face plane equations; kinematic local-envelope screening.',
 'seat_end_Y_mm':seat_end,'profile_arc_R_mm':arc_R,'profile_arc_center_offset_mm':arc_center_offset,'corners':rows,
 'limitations':['Rigid-envelope clearance shift is not a contact-solved elastic displacement or force.',
 'Center-crest gap does not mean no preload: two diagonal nub flanks overrun the receiver-end edge.',
 'Peak radial obstruction overrun is not inward Y travel and cannot be used as dynamic insertion deflection.',
 'No prescribed assembly path, friction, housing flexibility, large rotation, creep or time-dependent insertion has been solved.']}
(O/'contact-kinematics.json').write_text(json.dumps(result,indent=2))
dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
clip=np.frombuffer((R/'clip.stl').read_bytes(),dtype=dt,offset=84)['v'].astype(float)
housing=np.frombuffer((R/'housing.stl').read_bytes(),dtype=dt,offset=84)['v'].astype(float)
def section(tris,axis,value,other):
    out=[]
    for t in tris[(tris[:,:,axis].min(axis=1)<value)&(tris[:,:,axis].max(axis=1)>=value)]:
        ps=[]
        for a,b in zip(t,np.roll(t,-1,axis=0)):
            if (a[axis]<value<=b[axis])or(b[axis]<value<=a[axis]):ps.append((a+(b-a)*(value-a[axis])/(b[axis]-a[axis]))[other])
        if len(ps)==2:out.append(ps)
    return np.array(out)
fig,axes=plt.subplots(1,2,figsize=(12,4.0),layout='constrained')
ax=axes[0]
for key,t,col in [('Housing',housing,'#218b83'),('Clip',clip,'#be425e')]:
    seg=section(t,1,seat_end+.001,[0,2]);ax.add_collection(LineCollection(seg,colors=col,linewidths=2,label=key))
ax.set(xlim=(-1.36,-.34),ylim=(24.85,25.26),aspect='equal',xlabel='X across ridge (mm)',ylabel='Z installed height (mm)',title='XZ section just behind receiving seat\nY = 9.951 mm · contacts on two diagonal flanks')
ax.annotate('Crest clears the central roof',xy=(-.85,25.105),xytext=(-1.3,25.23),arrowprops={'arrowstyle':'->'},fontsize=9)
ax.annotate('Flank overlap',xy=(-.66,25.034),xytext=(-.62,24.87),arrowprops={'arrowstyle':'->'},fontsize=9)
ax=axes[1]
for key,t,col in [('Housing',housing,'#218b83'),('Clip',clip,'#be425e')]:
    seg=section(t,0,-.66,[1,2]);ax.add_collection(LineCollection(seg,colors=col,linewidths=2,label=key))
ax.set(xlim=(9.60,10.18),ylim=(24.955,25.11),aspect='equal',xlabel='Y across clip thickness (mm)',ylabel='Z installed height (mm)',title='YZ section through one loaded flank\nX = -0.660 mm · undeformed envelopes')
ax.axvline(seat_end,color='#778693',lw=1,ls='--')
ax.annotate('Receiver end',xy=(9.95,25.065),xytext=(9.63,25.091),arrowprops={'arrowstyle':'->'},fontsize=9)
ax.annotate('Small intentional overlap',xy=(9.96,25.025),xytext=(9.86,24.961),arrowprops={'arrowstyle':'->'},fontsize=9)
for ax in axes:ax.grid(alpha=.15);ax.legend(loc='lower left',fontsize=9)
fig.suptitle('Installed detent sanity check: center clearance + flank engagement\nExact-profile envelope shift to relieve flank overlap: 0.02730 mm inward in Y',fontsize=14)
fig.savefig(O/'flank-contact.png',dpi=180);plt.close(fig)
print(json.dumps(result,indent=2))
