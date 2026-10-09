from pathlib import Path
import sys,json,math
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs');sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/loose-fit-20261009/python-libs')
import numpy as np
from shapely.geometry import LineString,box,Point,Polygon
from shapely.ops import unary_union
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/loose-fit-20261009');results=[];fig,axs=plt.subplots(2,3,figsize=(13,8),dpi=180,layout='constrained')
cx=-.85;cz=24.703961852410437;roi=box(cx-.64,cz+.12,cx+.64,cz+.6)
def segs(p):return zip(p['points'],p['points'][1:])
def clip_section(ps,oid,y):
 selected=[p for p in ps if p['obj']==oid and p['feature'] not in ['Support','Support interface','Brim','Skirt'] and 12-p['z']-1e-6<=y<=12-p['z']+p['height']+1e-6]
 assert selected
 buf=[]
 for p in selected:
  for a,b in segs(p):
   a=(a[0]-143.475,a[1]-36.75);b=(b[0]-143.475,b[1]-36.75)
   if max(a[0],b[0])<cx-1 or min(a[0],b[0])>cx+1 or max(a[1],b[1])<cz-.3 or min(a[1],b[1])>cz+1:continue
   buf.append(LineString([a,b]).buffer(p['width']/2,quad_segs=12))
 return unary_union(buf).intersection(roi)
def housing_section(ps,oid,y):
 selected=[p for p in ps if p['obj']==oid and p['feature'] not in ['Support','Support interface','Brim','Skirt'] and 42-p['z']<=cz+1 and 42-p['z']+p['height']>=cz-.3];polys=[]
 for top in sorted(set(p['z'] for p in selected)):
  layer=[p for p in selected if p['z']==top];buf=[]
  for p in layer:
   for a,b in segs(p):
    a=(a[0]-42,175-a[1]);b=(b[0]-42,175-b[1])
    if max(a[0],b[0])<cx-1 or min(a[0],b[0])>cx+1 or max(a[1],b[1])<y-.3 or min(a[1],b[1])>y+.3:continue
    buf.append(LineString([a,b]).buffer(p['width']/2,quad_segs=12))
  mat=unary_union(buf);cross=mat.intersection(LineString([(cx-1,y),(cx+1,y)]))
  def lines(g):
   if g.geom_type=='LineString':return [g]
   if hasattr(g,'geoms'):return sum([lines(x) for x in g.geoms],[])
   return []
  for l in lines(cross):polys.append(box(l.bounds[0],42-top,l.bounds[2],42-top+layer[0]['height']))
 return unary_union(polys).intersection(roi)
def draw(ax,g,col,label):
 done=False
 for p in ([g] if g.geom_type=='Polygon' else getattr(g,'geoms',[])):
  if p.geom_type!='Polygon':continue
  xx,yy=p.exterior.xy;ax.fill(xx,yy,color=col,alpha=.6,label=label if not done else None);done=True
  for h in p.interiors:xx,yy=h.xy;ax.fill(xx,yy,color='white')
for row,(name,oids) in enumerate([('printed-0.16',(183,161)),('reviewed-0.12',(3,2))]):
 ps=json.loads((out/(name+'-paths.json')).read_text())
 for col,y in enumerate([9.98,10.015,10.06]):
  a=clip_section(ps,oids[0],y);b=housing_section(ps,oids[1],y);over=a.intersection(b);res={'case':name,'Y_mm':y,'minimum_nominal_bead_clearance_mm':a.distance(b),'nominal_overlap_area_mm2':over.area,'clip_area_mm2':a.area,'housing_area_mm2':b.area,'surface_setback_sensitivity':[{ 'setback_per_surface_mm':d,'overlap_area_mm2':a.buffer(-d).intersection(b.buffer(-d)).area,'clearance_mm':a.buffer(-d).distance(b.buffer(-d))} for d in [.01,.02,.03,.04,.05]]};results.append(res)
  ax=axs[row,col];draw(ax,a,'#bf536d','Clip beads');draw(ax,b,'#347d9f','Housing beads');ax.set(xlim=(cx-.64,cx+.64),ylim=(cz+.12,cz+.60),aspect='equal',xlabel='Assembly X (mm)',ylabel='Assembly Z (mm)',title=f'{name}, Y={y:.3f} mm\nNominal overlap={over.area:.6f} mm²');ax.grid(alpha=.12);ax.legend(fontsize=8)
fig.suptitle('Paired actual toolpaths at the upper-left nub — constant layer slabs, commanded-width capsules\nA geometric printing screen; not measured extrusion, deformation or retention force',fontsize=13);fig.savefig(out/'paired-toolpaths.png');(out/'paired-toolpaths.json').write_text(json.dumps({'method':'Nominal commanded-width capsules, constant layer slabs; local upper-left nub ROI. No physical extrusion/deformation/contact solve.','results':results},indent=2));print(json.dumps(results,indent=2))
