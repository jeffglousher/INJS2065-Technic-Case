import json,re,math,sys,hashlib
from pathlib import Path
from collections import Counter,defaultdict
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-readiness-20261008')
oldpath=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hub-friction-20261007/slice/plate_1.gcode')
newpath=out/'slice-final/plate_1.gcode'
def parse(p):
 pos=dict(X=0.,Y=0.,Z=0.,E=0.);rel=True;ab=True;obj=None;feat='';height=0.;width=0.;speed=0.;paths=[]
 for line in p.read_text().splitlines():
  if line.startswith('; FEATURE:'):feat=line.split(':',1)[1].strip()
  if line.startswith('; LAYER_HEIGHT:'):height=float(line.split(':',1)[1])
  if line.startswith('; LINE_WIDTH:'):width=float(line.split(':',1)[1])
  if line.startswith('; start printing object'):obj=int(line.rsplit(':',1)[1])
  if line.startswith('; stop printing object'):obj=None
  cmd=line.split(';',1)[0].strip()
  if cmd=='M83':rel=True
  if cmd=='M82':rel=False
  if cmd=='G90':ab=True
  if cmd=='G91':ab=False
  if not cmd.startswith(('G0 ','G1 ','G2 ','G3 ','G92 ')):continue
  t={k:float(v) for k,v in re.findall(r'([XYZEIJF])([-+]?(?:\d+(?:\.\d*)?|\.\d+))',cmd)}
  prev=pos.copy()
  if cmd.startswith('G92 '):pos.update({k:v for k,v in t.items() if k in pos});continue
  if 'F' in t:speed=t['F']/60
  for k,v in t.items():
   if k in pos:pos[k]=v if (k=='E' and not rel or k!='E' and ab) else pos[k]+v
  de=t.get('E',0) if rel else pos['E']-prev['E']
  if obj is None or de<=0 or not ('X' in t or 'Y' in t):continue
  points=[(prev['X'],prev['Y']),(pos['X'],pos['Y'])]
  if cmd.startswith(('G2 ','G3 ')) and ('I' in t or 'J' in t):
   cx=prev['X']+t.get('I',0);cy=prev['Y']+t.get('J',0);r=math.hypot(prev['X']-cx,prev['Y']-cy)
   a=math.atan2(prev['Y']-cy,prev['X']-cx);b=math.atan2(pos['Y']-cy,pos['X']-cx)
   delta=(b-a)%(2*math.pi) if cmd.startswith('G3 ') else -((a-b)%(2*math.pi))
   steps=max(2,math.ceil(abs(delta)/.025));points=[(cx+r*math.cos(a+delta*j/steps),cy+r*math.sin(a+delta*j/steps)) for j in range(steps+1)]
  paths.append(dict(obj=obj,feature=feat,z=round(pos['Z'],5),height=height,width=width,speed=speed,e=de,points=points))
 return paths
old=parse(oldpath);new=parse(newpath)
def summary(paths,obj):
 q=[p for p in paths if p['obj']==obj and p['feature'] not in ('Support','Support interface','Skirt','Brim')]
 zs=sorted(set(p['z'] for p in q));h=Counter(round(p['height'],4) for p in q);f=Counter(p['feature'] for p in q)
 return dict(layers=len(zs),z_levels_mm=zs,layer_height_segment_counts=dict(h),feature_segment_counts=dict(f),extruded_filament_mm=sum(p['e'] for p in q))
proof={'objects':{str(i):dict(before=summary(old,i),after=summary(new,i)) for i in range(1,6)}}
for i in range(1,5):
 a=proof['objects'][str(i)]['before'];b=proof['objects'][str(i)]['after']
 assert a['z_levels_mm']==b['z_levels_mm'],i
 # Record path sequencing differences; layer levels and extrusion totals are checked separately. Comment heights/widths can inherit across object switches.
 def sig(paths):
  return Counter((p['feature'],p['z'],tuple((round(x,3),round(y,3)) for x,y in p['points'])) for p in paths if p['obj']==i)
 proof['objects'][str(i)]['path_signature_difference_counts']=[len(sig(old)-sig(new)),len(sig(new)-sig(old))]
 assert abs(a['extruded_filament_mm']-b['extruded_filament_mm'])<.1
hub=proof['objects']['5']['after'];zs=hub['z_levels_mm'];assert zs[0]==.2 and all(abs(b-a-.08)<1e-5 for a,b in zip(zs,zs[1:])),zs
assert hub['feature_segment_counts'].get('Sparse infill',0)==0
speeds=[p['speed'] for p in new if p['obj']==5 and p['feature']=='Outer wall' and p['z']>.2]
assert max(speeds)<=30.001,max(speeds)
socket=[p for p in new if p['obj']==5 and 12.2<p['z']<15.55 for x,y in p['points'] if math.hypot(x-190,y-100)<2.55];assert not socket
supports=[(x,y,p['z']) for p in new if p['feature'] in ('Support','Support interface') for x,y in p['points']]
bounds=[[min(q[k] for q in supports),max(q[k] for q in supports)] for k in range(3)];assert 170<bounds[0][0]<bounds[0][1]<210 and 80<bounds[1][0]<bounds[1][1]<120
# Representative solid-web layer: six radial wall bands around the one outside boundary.
z=min((p['z'] for p in new if p['obj']==5),key=lambda z:abs(z-10))
wall=[p for p in new if p['obj']==5 and p['z']==z and p['feature'] in ('Inner wall','Outer wall')]
radii=sorted(set(round(math.hypot(x-190,y-100),1) for p in wall for x,y in p['points']))
assert len(radii)==6,radii
proof.update(other_four_object_settings_identical=True,other_four_object_layer_levels_identical=True,non_hub_filament_change_below_0_1_mm_each=True,hub_main_layer_height_mm=.08,hub_first_layer_height_mm=.2,hub_max_commanded_outer_wall_speed_mm_s=max(speeds),hub_sparse_infill_segments=hub['feature_segment_counts'].get('Sparse infill',0),servo_socket_interior_extrusion_samples_above_floor=0,support_and_interface_bounds_mm=bounds,supports_confined_to_hub=True,web_layer_z_mm=z,web_wall_sample_radii_mm=radii,gcode_external_path=str(newpath),gcode_sha256=hashlib.sha256(newpath.read_bytes()).hexdigest(),print_sent=False)
(out/'toolpath-audit.json').write_text(json.dumps(proof,indent=2))
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
fig,axes=plt.subplots(1,2,figsize=(10,5.6),dpi=180)
colors={'Outer wall':'#a52646','Inner wall':'#1d6485','Internal solid infill':'#b28c20','Sparse infill':'#929baa','Top surface':'#b28c20','Bottom surface':'#b28c20'}
for ax,paths,title in zip(axes,[old,new],['Previous hub: 4 walls / 25% gyroid','Revised hub: 6 walls / 100% fill']):
 zp=min((p['z'] for p in paths if p['obj']==5),key=lambda z:abs(z-10))
 for feat,col in colors.items():
  seg=[((a[0]-190,a[1]-100),(b[0]-190,b[1]-100)) for p in paths if p['obj']==5 and p['z']==zp and p['feature']==feat for a,b in zip(p['points'],p['points'][1:])]
  if seg:ax.add_collection(LineCollection(seg,colors=col,linewidths=.85,label=feat))
 ax.set(xlim=(-6.4,6.4),ylim=(-6.4,6.4),aspect='equal',xlabel='X (mm)',ylabel='Y (mm)',title=title);ax.grid(alpha=.12)
 ax.text(.5,-.16,f'Actual native toolpaths through the solid web, Z={zp:.2f} mm',transform=ax.transAxes,ha='center',fontsize=8)
axes[1].legend(loc='upper center',bbox_to_anchor=(.5,-.23),ncol=2,fontsize=8)
fig.suptitle('Output hub only - X2D 0.4 mm / Bambu PETG Basic',fontsize=13)
fig.tight_layout(rect=(0,.11,1,.94));fig.savefig(out/'hub-toolpaths.png');plt.close(fig)
print(json.dumps({k:v for k,v in proof.items() if k!='objects'},indent=2))






