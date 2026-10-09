from pathlib import Path
import sys,json,re
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from PIL import Image
out=Path(__file__).parent
src=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/revision-20261007/render.py').read_text();exec(src[src.index('def raster('):src.index('fig,axes=')])
scene=json.loads((out/'candidate-scene.json').read_text());byid={b['id']:b for b in scene['bodies']}
def coarse(i):
 m=byid[i]['mesh'];return np.array(m['positions']).reshape(-1,3)[np.array(m['indices']).reshape(-1,3)]
red=[.81,.30,.40];teal=[.28,.63,.65]
clip=coarse(173);lower=coarse(8);upper=coarse(18)
fine=np.array([tuple(map(float,m)) for m in re.findall(rb'\bvertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)',(out/'candidate-173.stl').read_bytes())]).reshape(-1,3,3)
roi=fine[(fine[:,:,0].min(axis=1)<2.5)&(fine[:,:,0].max(axis=1)>-4)&(fine[:,:,2].min(axis=1)<25.6)&(fine[:,:,2].max(axis=1)>20.5)]
fig,axs=plt.subplots(1,2,figsize=(12,5.4),facecolor='#f5f7fa');panel(axs[0],[(clip,red)],[6.525,10.5,18.25],31,'Retuned clip: pocket-side ISO');panel(axs[1],[(roi,red)],[-.85,10.5,23],7.8,'0.26 mm nub; full wall and flat floor retained')
fig.suptitle('Native CAD candidate: 0.10 mm inner hex clearance per flat',fontsize=14);fig.subplots_adjust(left=.01,right=.99,bottom=.03,top=.85);fig.savefig(out/'clip-and-corner.png',dpi=155);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,8),facecolor='#f5f7fa');panel(ax,[(lower+[0,0,-10],teal),(upper+[0,0,14],teal),(clip+[0,35,0],red),(coarse(267)+[0,-35,0],red)],[8,0,27],110,'Exploded inspection view',az=-40,el=25);fig.suptitle('Housing / clip fit candidate - display offsets only',fontsize=14);fig.subplots_adjust(left=.01,right=.99,bottom=.02,top=.9);fig.savefig(out/'exploded.png',dpi=155);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
for ax,y in zip(axs,[9.8,10.14240656]):
 for bid,col,label in [(173,'#be425e','Clip'),(18,'#218b83','Housing')]:
  s=json.loads((out/f'section-{bid}-{y}.json').read_text());parts=[[(p[0]+.85,p[1]-24.703961852410437) for p in c['points']] for c in s['section']];ax.add_collection(LineCollection(parts,colors=col,linewidths=2,label=label))
 ax.set(xlim=(-.58,.58),ylim=(.19,.55),aspect='equal',xlabel='X from nub axis (mm)',ylabel='Z from nub axis (mm)',title=f'Fresh OCCT section, Y={y:.4f} mm');ax.grid(alpha=.15);ax.legend(loc='lower right',fontsize=8)
fig.suptitle('Center clears the seat; retaining contact remains on diagonal flanks\n0.02 mm nominal inward clearance movement; elastic contact not solved',fontsize=12);fig.savefig(out/'sections.png',dpi=170);plt.close(fig)
print('Saved inspected native CAD images',flush=True)
