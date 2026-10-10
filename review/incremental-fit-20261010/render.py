from pathlib import Path
import ast,json,re,sys
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
sys.path.insert(0,'C:/Users/jeffg/dev/garden-auger-technic/scripts')
import raster_render as rr
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from PIL import Image
ROOT=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');OUT=Path(__file__).parent
src=(ROOT/'review/revision-20261007/render.py').read_text();tree=ast.parse(src)
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name in ['raster','panel']:exec(compile(ast.get_source_segment(src,n),'<recorded-native-raster>','exec'))
before=json.loads((OUT/'baseline-scene.json').read_text());after=json.loads((OUT/'nub-28-scene.json').read_text())
def coarse(scene,i):
 m=next(b['mesh'] for b in scene['bodies'] if b['id']==i);return np.array(m['positions']).reshape(-1,3)[np.array(m['indices']).reshape(-1,3)]
def fine(i):return np.array([tuple(map(float,v)) for v in re.findall(rb'\bvertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)',(OUT/f'nub-28-{i}.stl').read_bytes())]).reshape(-1,3,3)
teal=[.28,.63,.65];red=[.81,.30,.40]
fig,axs=plt.subplots(1,2,figsize=(12,5.5),facecolor='#f5f7fa')
for ax,sc,tag,title in zip(axs,[before,after],['baseline','nub-28'],['Previous: underside bevel','Updated: full hex post underside']):
 b=next(b for b in sc['bodies'] if b['id']==8);v=np.array(b['mesh']['positions']).reshape(-1,3);idx=np.array(b['mesh']['indices']);meshes=[]
 for f in b['faces']:
  tri=v[idx[f['first_index']:f['first_index']+f['index_count']].reshape(-1,3)];center=tri.reshape(-1,3).mean(axis=0);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]).sum(axis=0);normal/=max(np.linalg.norm(normal),1e-12)
  color=(135,172,187)
  if -5.56<center[0]<-2.04 and -10.57<center[1]<-8.84 and 13<center[2]<16.1 and normal[2]<-.1:color=(222,171,45) if tag=='baseline' else (79,163,111)
  meshes.append((color,tri.tolist()))
 path=OUT/f'{tag}-post-iso.png';rr.render(meshes,eye=(-7.5,-23,9),target=(-3.8,-9.5,14.7),up=(0,0,1),size=(600,540),path=path,scale=1600)
 ax.imshow(Image.open(path));ax.axis('off');ax.set_title(title,fontsize=12)
fig.suptitle('Native CAD: bevel removed on all 16 locating posts',fontsize=14);fig.subplots_adjust(left=.01,right=.99,bottom=.03,top=.86);fig.savefig(OUT/'hex-before-after.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.5,5.2),layout='constrained')
for tag,col,label in [('baseline','#ab8426','Previous bevel'),('nub-28','#218b83','Restored full post')]:
 s=json.loads((OUT/f'{tag}-hex-root.json').read_text());segs=[[(-a[0],a[1]),(-b[0],b[1])] for c in s['section'] for a,b in zip(c['points'],c['points'][1:])];ax.add_collection(LineCollection(segs,colors=col,linewidths=2,label=label))
ax.set(xlim=(8.45,10.95),ylim=(13.25,18.1),aspect='equal',xlabel='Outward distance |Y| (mm)',ylabel='CAD Z (mm)',title='Native section: full underside restored across 1.70 mm projection')
ax.axvline(8.85,color='#777',linestyle=':',linewidth=.8);ax.text(8.88,17.93,'Wall / post root',fontsize=9);ax.legend(loc='upper right');ax.grid(alpha=.16)
ax.annotate('0.674 mm restored at mouth',xy=(10.55,13.99),xytext=(8.6,15.08),arrowprops=dict(arrowstyle='->'),fontsize=9)
fig.savefig(OUT/'hex-section.png',dpi=160);plt.close(fig)
clip=fine(173);roi=clip[(clip[:,:,0].min(axis=1)<2.5)&(clip[:,:,0].max(axis=1)>-4)&(clip[:,:,2].min(axis=1)<25.6)&(clip[:,:,2].max(axis=1)>20.5)]
fig,axs=plt.subplots(1,2,figsize=(12,5.5),facecolor='#f5f7fa')
panel(axs[0],[(clip,red)],[6.525,10.5,18.25],31,'Full clip: pocket-side ISO')
panel(axs[1],[(roi,red)],[-.85,10.5,23],7.8,'0.28 mm nub / rounded crest / full wall')
fig.suptitle('Native CAD: 0.02 mm larger nubs; corner wall and flat backing retained',fontsize=13);fig.subplots_adjust(left=.01,right=.99,bottom=.03,top=.85);fig.savefig(OUT/'clip-and-corner.png',dpi=160);plt.close(fig)
fig,axs=plt.subplots(1,3,figsize=(14,4.8),layout='constrained')
for ax,label in zip(axs[:2],['center','holding']):
 for tag,col in [('baseline','#697c87'),('nub-28','#c03f61')]:
  s=json.loads((OUT/f'{tag}-nub-{label}.json').read_text());ax.add_collection(LineCollection([[(p[0]+.85,p[1]-24.703961852410437) for p in c['points']] for c in s['section']],colors=col,linewidths=1.6,label='Previous clip' if tag=='baseline' else 'Updated clip'))
 s=json.loads((OUT/f'nub-28-seat-{label}.json').read_text());ax.add_collection(LineCollection([[(p[0]+.85,p[1]-24.703961852410437) for p in c['points']] for c in s['section']],colors='#218b83',linewidths=1.8,label='Unchanged hidden seat'))
 ax.set(xlim=(-.6,.6),ylim=(.13,.62),aspect='equal',xlabel='X from nub axis (mm)',ylabel='Z from nub axis (mm)',title='Nub midpoint' if label=='center' else 'Seated retaining flank');ax.grid(alpha=.15)
axs[0].legend(loc='upper left',fontsize=7)
for tag,col in [('baseline','#697c87'),('nub-28','#218b83')]:
 s=json.loads((OUT/f'{tag}-shaft-opening.json').read_text())
 loops=[c['points'] for c in s['section'] if all(np.hypot(p[0],p[1])<4.3 for p in c['points'])]
 axs[2].add_collection(LineCollection(loops,colors=col,linewidths=2,label='Previous aperture' if tag=='baseline' else 'Updated aperture'))
s=json.loads((OUT/'nub-28-shaft.json').read_text());axs[2].add_collection(LineCollection([c['points'] for c in s['section']],colors='#c03f61',linewidths=2,label='Unchanged shaft'))
axs[2].set(xlim=(3.65,4.35),ylim=(-.35,.35),aspect='equal',xlabel='CAD X (mm)',ylabel='CAD Y (mm)',title='Aperture radial gap: 0.105 -> 0.205 mm');axs[2].legend(loc='upper right',fontsize=7);axs[2].grid(alpha=.15)
fig.suptitle('Fresh OCCT sections: 0.020 mm crest relief / 0.0569 mm local rigid holding movement\nUndeformed geometry; elastic preload and strain are not solved',fontsize=12);fig.savefig(OUT/'sections.png',dpi=165);plt.close(fig)
print('Saved genuine CAD geometry figures')
