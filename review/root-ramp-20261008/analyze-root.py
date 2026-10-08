from pathlib import Path
import json,sys,math,hashlib
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
sys.path.insert(0,'C:/Users/jeffg/dev/garden-auger-technic/scripts')
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import raster_render as rr
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/root-ramp-20261008')
scenes={n:json.loads((out/(n+'-scene.json')).read_text()) for n in ['before','candidate']}
audit={'bodies':{},'all_original_bounding_boxes_preserved':True}
canvas=Image.new('RGB',(1200,670),'#f6f8fa');draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for j,(name,scene) in enumerate(scenes.items()):
 b=next(b for b in scene['bodies'] if b['id']==8);v=np.array(b['mesh']['positions']).reshape(-1,3);idx=np.array(b['mesh']['indices']);meshes=[]
 for f in b['faces']:
  tri=v[idx[f['first_index']:f['first_index']+f['index_count']].reshape(-1,3)];c=tri.reshape(-1,3).mean(axis=0);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]).sum(axis=0);length=np.linalg.norm(normal);color=(135,172,187)
  if length>1e-10:
   normal/=length;angle=math.degrees(math.asin(min(1,max(0,-normal[2]))))
   if -5.56<c[0]<-2.04 and -10.57<c[1]<-8.84 and 13<c[2]<16.1 and normal[2]<-.1:color=(222,171,45) if name=='candidate' and 54.9<angle<55.1 else (215,77,77)
  meshes.append((color,tri.tolist()))
 rr.render(meshes,eye=(-7.5,-23,9),target=(-3.8,-9.5,14.7),up=(0,0,1),size=(600,540),path=out/(name+'-closeup.png'),scale=1600)
 canvas.paste(Image.open(out/(name+'-closeup.png')),(j*600,65));draw.text((j*600+18,16),['Before: abrupt projecting underside','After: bevel starts at the wall/root'][j],font=font,fill='#173346')
draw.text((18,622),'Actual native CAD. Gold: full-depth root bevel, 55 degrees from the build direction.',font=font,fill='#173346');canvas.save(out/'root-bevel-closeup.png')
for bid in [8,18]:
 records={}
 for name,scene in scenes.items():
  b=next(b for b in scene['bodies'] if b['id']==bid);v=np.array(b['mesh']['positions']).reshape(-1,3);idx=np.array(b['mesh']['indices']);tri=v[idx.reshape(-1,3)];vol=np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6
  angles=[]
  for f in b['faces']:
   t=v[idx[f['first_index']:f['first_index']+f['index_count']].reshape(-1,3)];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]).sum(axis=0);ln=np.linalg.norm(normal)
   if ln<1e-10:continue
   normal/=ln;z=normal[2]*(1 if bid==8 else -1);angle=math.degrees(math.asin(min(1,max(0,-z))))
   if 54.9<angle<55.1:angles.append(angle)
  records[name]={'volume_mm3':float(vol),'bounds_mm':[v.min(axis=0).tolist(),v.max(axis=0).tolist()],'root_ramp_face_angles_deg':angles}
 assert np.allclose(records['before']['bounds_mm'],records['candidate']['bounds_mm'],atol=1e-5,rtol=0)
 assert len(records['candidate']['root_ramp_face_angles_deg'])==16
 records['removed_volume_mm3']=records['before']['volume_mm3']-records['candidate']['volume_mm3'];records['removed_volume_percent']=100*records['removed_volume_mm3']/records['before']['volume_mm3'];audit['bodies'][str(bid)]=records
audit['other_five_bodies_preserved']=all(next(b for b in scenes['before']['bodies'] if b['id']==bid)['mesh']==next(b for b in scenes['candidate']['bodies'] if b['id']==bid)['mesh'] for bid in [1,53,54,173,267]);assert audit['other_five_bodies_preserved']
(out/'geometry-audit.json').write_text(json.dumps(audit,indent=2))
before=json.loads(Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/hex-underside-20261008/before-section.json').read_text());after=json.loads((out/'lower-root-section.json').read_text())
fig,ax=plt.subplots(figsize=(7.5,5.3),dpi=180)
for name,s,c in [('Before',before,'#677d8c'),('Root bevel',after,'#c3951b')]:
 seg=[((-a[0],a[1]),(-b[0],b[1])) for e in s['section'] for a,b in zip(e['points'],e['points'][1:])];ax.add_collection(LineCollection(seg,colors=c,linewidths=2,label=name))
ax.set(xlim=(8.45,10.95),ylim=(13.25,18.1),aspect='equal',xlabel='Outward distance |Y| (mm)',ylabel='CAD Z (mm)',title='Native section through the hex post center')
ax.axvline(8.85,color='#666',linestyle=':',linewidth=.8);ax.text(8.88,17.99,'Wall/root',fontsize=9)
ax.annotate('Full 1.70 mm projection',xy=(8.85,13.4),xytext=(10.55,13.4),arrowprops=dict(arrowstyle='<->'),ha='right',fontsize=9)
ax.annotate('0.674 mm relief at mouth',xy=(10.55,14.02),xytext=(9.2,15.2),arrowprops=dict(arrowstyle='->'),fontsize=9);ax.legend(loc='upper right');ax.grid(alpha=.16);fig.tight_layout();fig.savefig(out/'root-bevel-section.png');plt.close(fig)
print(json.dumps(audit,indent=2))
