from pathlib import Path
import sys,json
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/flat-clip-base-20261008');fig,ax=plt.subplots(figsize=(8,6),dpi=180)
for name,color in [('before','#d89434'),('after','#147d99')]:
 s=json.loads((out/f'{name}-center-section.json').read_text())
 for p in s['section']:
  xx,zz=zip(*p['points']);ax.plot(xx,zz,color=color,lw=2 if name=='after' else 3,alpha=.85)
 ax.plot([],[],color=color,lw=2,label='Before: floor depression' if name=='before' else 'After: flat floor')
ax.axvline(10.55,color='#555',linestyle='--',lw=.8);ax.axvline(12,color='#888',linestyle=':',lw=.8)
ax.annotate('1.45 mm backing',(11.27,20),ha='center',rotation=90,color='#147d99');ax.annotate('',(10.55,20.4),(12,20.4),arrowprops={'arrowstyle':'<->','color':'#147d99'})
ax.set(xlim=(8.85,12.2),ylim=(19.3,23.85),aspect='equal',xlabel='Y through clip thickness (mm)',ylabel='Z along corner (mm)',title='Native CAD section through the upper detent center')
ax.legend(loc='lower left');ax.grid(alpha=.15);fig.tight_layout();fig.savefig(out/'clip-floor-section.png',bbox_inches='tight')
