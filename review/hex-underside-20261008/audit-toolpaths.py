from pathlib import Path
import sys,json
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hex-underside-20261008')
ns={};source=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/hub-quality-20261008/audit.py').read_text();exec(source.split('old=parse(oldpath);new=parse(newpath)')[0],ns)
files={'before':Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-layout-20261008/assembly-petg-sequential-no-brim/plate_1.gcode'), 'equal-bevel':out/'equal-bevel-slice/plate_1.gcode','angled-bevel':out/'angled-bevel-slice/plate_1.gcode'}
fig,axes=plt.subplots(1,3,figsize=(13,5.8),dpi=160);report={}
for ax,(name,path) in zip(axes,files.items()):
 paths=ns['parse'](path)
 q=[p for p in paths if p['obj']==1 and p['feature']=='Outer wall' and 5.5<p['z']<6.5 and any(36.3<x<40.1 and 44.1<y<46.30 for x,y in p['points'])]
 zs=sorted(set(p['z'] for p in q));assert zs
 bounds=[]
 for z in zs:
  pts=[(x,y) for p in q if p['z']==z for x,y in p['points'] if 36.3<x<40.1 and 44.1<y<46.30]
  bounds.append({'z_mm':z,'frontmost_wall_centerline_y_mm':min(y for x,y in pts),'post_width_at_front_mm':max(x for x,y in pts if y==min(v for u,v in pts))-min(x for x,y in pts if y==min(v for u,v in pts))})
 report[name]={'first_post_outer_wall_z_mm':zs[0],'first_post_outer_wall_profile':bounds,'first_commanded_wall_width_mm':q[0]['width']}
 for i,z in enumerate(zs[:3]):
  seg=[[(a[0]-38.2,a[1]-46.15),(b[0]-38.2,b[1]-46.15)] for p in paths if p['obj']==1 and p['z']==z and p['feature']=='Outer wall' for a,b in zip(p['points'],p['points'][1:])]
  ax.add_collection(LineCollection(seg,colors=['#ba3552','#3686aa','#b89a3c'][i],linewidths=1.5,label=f'Z={z:.2f} mm'))
 ax.axhline(0,color='#555',linestyle='--',linewidth=.8,label='Housing wall datum');ax.set(xlim=(-1,1),ylim=(-1.95,.4),aspect='equal',xlabel='X from post center (mm)',ylabel='Y from root (mm)',title=name);ax.grid(alpha=.15);ax.legend(fontsize=8,loc='upper right')
fig.suptitle('Actual X2D 0.4 mm / PETG toolpaths: first outer walls on one hex post')
fig.tight_layout(rect=(0,0,1,.93));fig.savefig(out/'first-post-toolpaths.png',bbox_inches='tight');plt.close(fig)
report['first_post_outer_wall_z_unchanged']=len(set(r['first_post_outer_wall_z_mm'] for r in report.values()))==1
report['first_post_front_centerline_y_unchanged']=len(set(r['first_post_outer_wall_profile'][0]['frontmost_wall_centerline_y_mm'] for r in list(report.values())[:3]))==1
(out/'toolpath-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
