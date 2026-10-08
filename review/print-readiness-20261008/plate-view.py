from pathlib import Path
import json
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-readiness-20261008')
ns={};exec((out/'audit.py').read_text().split('old=parse(oldpath);new=parse(newpath)')[0],ns);paths=ns['parse'](out/'slice-final/plate_1.gcode')
import sys
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
fig,ax=plt.subplots(figsize=(9,6),dpi=170)
for obj in range(1,6):
 seg=[(a,b) for p in paths if p['obj']==obj and abs(p['z']-.2)<1e-5 for a,b in zip(p['points'],p['points'][1:])]
 ax.add_collection(LineCollection(seg,colors='#1c6582',linewidths=.5))
for p in json.loads((out/'assembly-project.json').read_text())['parts']:
 b=p['plate_bounds_mm'];ax.text((b[0][0]+b[0][1])/2,118 if p['body_id']==54 else b[1][1]+4,p['name'],ha='center',fontsize=10)
ax.set(xlim=(45,212),ylim=(78,170),aspect='equal',xlabel='Bed X (mm)',ylabel='Bed Y (mm)',title='Reviewed PETG assembly - actual first-layer toolpaths')
fig.text(.5,.035,'X2D / 0.4 mm | Bambu PETG Basic | Five printable parts | Hub supports only',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.06,1,1));fig.savefig(out/'plate-layout.png');plt.close(fig)
