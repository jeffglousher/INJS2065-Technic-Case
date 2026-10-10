"""Actual native CAD and support footprints; no invented deformed geometry."""
from pathlib import Path
import json,sys
ROOT=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case')
SOURCE=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/retention-fit-20261009')
OUT=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/contact-fix-20261009')
sys.path[:0]=['D:/noBS-CAD-Reviews/INJS2065-Technic-Case/loose-fit-20261009/python-libs',
    'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs']
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
from PIL import Image
from shapely.geometry import Polygon
from shapely.ops import unary_union
scene=json.loads((SOURCE/'candidate-scene.json').read_text());byid={b['id']:b for b in scene['bodies']}
renderer=(ROOT/'review/revision-20261007/render.py').read_text()
exec(renderer[renderer.index('def raster('):renderer.index('fig,axes=')])

def triangles(bid):
    m=byid[bid]['mesh'];return np.array(m['positions']).reshape(-1,3)[np.array(m['indices']).reshape(-1,3)]

def floor(bid):
    b=byid[bid];m=b['mesh'];v=np.array(m['positions']).reshape(-1,3);ix=np.array(m['indices'])
    parts=[]
    for f in b['faces']:
        p=f.get('plane')
        if p and abs(p['normal'][1])>.99 and abs(p['origin'][1]-10.55)<1e-5:
            for t in ix[f['first_index']:f['first_index']+f['index_count']].reshape(-1,3):parts.append(Polygon(v[t][:,[0,2]]))
    return unary_union(parts)

def fill(ax,g,color):
    if g.geom_type!='Polygon':
        for p in g.geoms:fill(ax,p,color)
        return
    ax.add_patch(Patch(np.array(g.exterior.coords),facecolor=color,edgecolor='none'))
    for ring in g.interiors:ax.add_patch(Patch(np.array(ring.coords),facecolor='white',edgecolor='none'))

clip=floor(173);posts=unary_union([floor(8),floor(18)])
fig,ax=plt.subplots(figsize=(10,5.4),layout='constrained')
fill(ax,clip,'#e7b474');fill(ax,clip.intersection(posts),'#78b5b0')
ax.set(xlim=(-8,21),ylim=(10.5,26),aspect='equal',xlabel='X (mm)',ylabel='Z (mm)',
    title='Pocket floor at Y = 10.55 mm: actual housing support')
ax.text(.02,.03,'Teal: housing material beneath floor\nOrange: air-facing floor; it must remain free',transform=ax.transAxes,
    bbox={'facecolor':'white','edgecolor':'none','alpha':.9},fontsize=10)
ax.grid(alpha=.15);fig.savefig(OUT/'support-footprint.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,7),facecolor='#f5f7fa')
panel(ax,[(triangles(8),[.28,.63,.65]),(triangles(18)+[0,0,14],[.28,.63,.65]),
    (triangles(173)+[0,24,0],[.81,.30,.40]),(triangles(267)+[0,-24,0],[.81,.30,.40])],
    [8,0,25],90,'Complete receivers and nominal clips; exploded display only',az=-40,el=25)
fig.suptitle('Registered retention test: original shell geometry and locators preserved',fontsize=13)
fig.subplots_adjust(left=.01,right=.99,bottom=.02,top=.88);fig.savefig(OUT/'registered-receivers.png',dpi=160);plt.close(fig)
print('Saved native support and registered-receiver figures',flush=True)
