from pathlib import Path
import sys,json
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hex-underside-20261008')
fig,axes=plt.subplots(1,2,figsize=(10,5.4),dpi=180)
for ax in axes:
 for name,color in [('before','#657887'),('angled-bevel','#c79214')]:
  section=json.loads((out/(name+'-section.json')).read_text())['section']
  seg=[((-a[0],a[1]),(-b[0],b[1])) for e in section for a,b in zip(e['points'],e['points'][1:])]
  ax.add_collection(LineCollection(seg,colors=color,linewidths=2,label=name))
 ax.set(aspect='equal',xlabel='Outward distance |Y| (mm)',ylabel='CAD Z (mm)');ax.grid(alpha=.17)
axes[0].set(xlim=(8.35,10.85),ylim=(13.3,18.15),title='Native OCCT section through post center')
axes[0].axvline(8.85,color='#777',linestyle=':',linewidth=.8);axes[0].text(8.87,17.96,'Wall/root',fontsize=8)
axes[0].annotate('1.70 mm projection',xy=(8.85,13.47),xytext=(10.55,13.47),arrowprops=dict(arrowstyle='<->'),ha='right',fontsize=8)
axes[0].legend(fontsize=8)
axes[1].set(xlim=(10.34,10.64),ylim=(13.61,14.03),title='Magnified 0.20 mm bevel at the tip')
axes[1].axhline(13.96,color='#ad3855',linestyle='--',linewidth=1,label='First wall layer, CAD Z13.96')
axes[1].annotate('0.109 mm retreat',xy=(10.441,13.675),xytext=(10.55,13.64),arrowprops=dict(arrowstyle='<->'),ha='center',fontsize=8)
axes[1].legend(fontsize=7,loc='upper left')
fig.suptitle('Measured trial: tiny bevel preserves fit, but leaves most of the cantilever underside')
fig.tight_layout(rect=(0,0,1,.93));fig.savefig(out/'native-section-comparison.png');plt.close(fig)
