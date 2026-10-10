from pathlib import Path
import ast,hashlib,json,math,re,sys
from collections import Counter
ROOT=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');OUT=Path(__file__).parent
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/loose-fit-20261009/python-libs')
from shapely.geometry import LineString,box
from shapely.ops import unary_union
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
s=(ROOT/'review/hub-quality-20261008/audit.py').read_text();n=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name=='parse');exec(compile(ast.get_source_segment(s,n),'<recorded-native-parser>','exec'))
baseline=parse(Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/incremental-fit-20261010/nub-28-slice/plate_1.gcode'))
roles={'Support','Support interface'};results={}
for tag in ['hex-support-gap-16','hex-support-gap-20']:
 ps=parse(OUT/tag/'plate_1.gcode');supports=[p for p in ps if p['feature'] in roles]
 assert supports and all(p['obj'] in [1,2] for p in supports)
 assert not any(p['feature'] in ['Brim','Skirt'] for p in ps)
 # Non-shell extrusion trajectories and settings are preserved; travel timing can differ.
 for i in [3,4,5]:
  signature=lambda paths:Counter((p['feature'],p['z'],tuple((round(x,4),round(y,4)) for x,y in p['points']),round(p['e'],6)) for p in paths if p['obj']==i)
  assert signature(ps)==signature(baseline),(tag,i)
 cells=[]
 for obj,cy,centers,base in [(1,55,[-11.8,-5.9,0,5.9],5.6744991167),(2,175,[-8.85,-2.95,2.95,8.85],19.1744991167)]:
  for cx in centers:
   for side in [-1,1]:
    # Only the projected post, excluding surrounding uncut perimeter.
    roi=box(50+cx-1.75,cy+min(side*8.85,side*10.55),50+cx+1.75,cy+max(side*8.85,side*10.55))
    q=[p for p in supports if p['obj']==obj and LineString(p['points']).intersects(roi)]
    assert q,(tag,obj,cx,side)
    face=[p for p in q if p['feature']=='Support interface'];assert face
    # Check interface exists directly below the initially printed tip strip.
    tiproi=box(50+cx-.35,cy+min(side*9.5,side*10.3),50+cx+.35,cy+max(side*9.5,side*10.3))
    early=[p for p in ps if p['obj']==obj and p['feature'] not in roles and base<=p['z']<base+.6 and LineString(p['points']).buffer(p['width']/2).intersects(tiproi)]
    assert early
    z=min(p['z'] for p in early);under=[p for p in face if p['z']<z and LineString(p['points']).buffer(p['width']/2).intersects(tiproi)]
    assert under,(tag,obj,cx,side)
    top=max(p['z'] for p in under)
    # Different XY paths on the sloping flanks can have different interface tops.
    # Subtracting an arbitrary highest interface from the first part layer is
    # not a pointwise physical gap measurement. Only record coverage here.
    cells.append({'shell_object':obj,'post_center_local_x':cx,'side':side,'interface_segments':len(face),'highest_interface_nozzle_z_in_tip_region':top,'first_sampled_tip_layer_z':z,'interface_present_below_first_sampled_tip_layer':True})
 report={'posts_with_local_interface':len(cells),'post_checks':cells,'support_segments':len(supports),'support_filament_mm':sum(p['e'] for p in supports),'supports_only_on_clamshells':True,'brims_skirts_absent':True,'clip_and_hub_extrusion_trajectories_unchanged':True,'nominal_commanded_beads_not_measured_print':True,'print_sent':False}
 results[tag]=report
 if tag=='hex-support-gap-20':selected=ps
results['baseline']={'supports':sum(p['feature'] in roles for p in baseline)}
(OUT/'toolpath-audit.json').write_text(json.dumps(results,indent=2)+'\n')
# Actual native toolpath cross projections; only a narrow strip through one post.
fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
colors={'Support':'#7a9bc7','Support interface':'#e09a23','Outer wall':'#be3855','Overhang wall':'#be3855','Inner wall':'#526a75'}
for row,(obj,cy,cx,base) in enumerate([(1,55,0,5.6744991167),(2,175,2.95,19.1744991167)]):
 for col,paths in enumerate([baseline,selected]):
  ax=axes[row,col]
  for role,color in colors.items():
   seg=[]
   for p in paths:
    if p['obj']!=obj or p['feature']!=role or not base-1.4<p['z']<base+1.3:continue
    for a,b in zip(p['points'],p['points'][1:]):
     clipped=LineString([a,b]).intersection(box(50+cx-.35,cy+8.4,50+cx+.35,cy+10.8))
     if clipped.is_empty:continue
     if clipped.geom_type=='LineString':
      pts=list(clipped.coords)
      seg.append([(pts[0][1]-cy,p['z']),(pts[-1][1]-cy,p['z'])])
     elif clipped.geom_type=='Point':
      seg.append([(clipped.x*0+clipped.y-cy-.015,p['z']),(clipped.y-cy+.015,p['z'])])
   if seg:ax.add_collection(LineCollection(seg,colors=color,linewidths=2,label=role))
  ax.set(xlim=(8.4,10.85),ylim=(base-1.3,base+1.2),xlabel='Outward Y from shell center (mm)',ylabel='Nozzle Z (mm)',title=f'{"Lower" if obj==1 else "Upper"} shell: {"unsupported" if col==0 else "local supports / 0.20 mm gap"}')
  ax.grid(alpha=.15);ax.legend(fontsize=7,loc='upper left')
fig.suptitle('Native Bambu toolpaths near post centers — geometry unchanged',fontsize=13)
fig.savefig(OUT/'hex-support-comparison.png',dpi=180);plt.close(fig)
print(json.dumps({k:{'posts':v.get('posts_with_local_interface'),'supports':v.get('support_segments')} for k,v in results.items()},indent=2))
