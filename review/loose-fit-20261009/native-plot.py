from pathlib import Path
import json,sys
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/loose-fit-20261009');fig,axs=plt.subplots(1,2,figsize=(10,5),dpi=180,layout='constrained');cx=-.85;cz=24.703961852410437
for ax,y in zip(axs,[9.8,9.98]):
 for id,col,label in [(173,'#bb4564','Clip'),(18,'#217e9e','Housing')]:
  s=json.loads((out/f'body-{id}-y{y}.json').read_text());segs=[[(a[0]-cx,a[1]-cz),(b[0]-cx,b[1]-cz)] for c in s['section'] for a,b in zip(c['points'],c['points'][1:])];ax.add_collection(LineCollection(segs,colors=col,linewidths=2,label=label))
 ax.set(xlim=(-.58,.58),ylim=(.17,.59),aspect='equal',xlabel='X from detent axis (mm)',ylabel='Z from detent axis (mm)',title=f'Native OCCT section, Y={y:.3f} mm');ax.grid(alpha=.12);ax.legend(loc='lower right',fontsize=8)
axs[0].annotate('Crest clearance: 0.077 mm',(.01,.43),(-.48,.54),arrowprops={'arrowstyle':'->'},fontsize=9)
axs[1].annotate('Retention depends on the flanks',(-.2,.365),(-.55,.2),arrowprops={'arrowstyle':'->'},fontsize=9)
fig.suptitle('Current installed detent: center clearance and minute flank contacts\nFresh native sections; undeformed CAD, not a mechanical contact solution',fontsize=13);fig.savefig(out/'native-detent-diagnosis.png')
