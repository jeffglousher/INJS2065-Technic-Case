from pathlib import Path
import sys,json,math
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
sys.path.insert(0,'C:/Users/jeffg/dev/garden-auger-technic/scripts')
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import raster_render as rr
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hex-underside-20261008')
scenes={n:json.loads((out/f'{n}-scene.json').read_text()) for n in ['before','equal-bevel','angled-bevel']}
report={'canonical_changed':False,'trials':{}}
canvas=Image.new('RGB',(1800,650),'#f6f8fa');draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
for j,(name,scene) in enumerate(scenes.items()):
 b=next(b for b in scene['bodies'] if b['id']==8);p=np.array(b['mesh']['positions']).reshape(-1,3);idx=np.array(b['mesh']['indices']);tris=p[idx.reshape(-1,3)]
 volume=np.sum(np.einsum('ij,ij->i',tris[:,0],np.cross(tris[:,1],tris[:,2])))/6
 mm=[];faces=[]
 for f in b['faces']:
  tri=p[idx[f['first_index']:f['first_index']+f['index_count']].reshape(-1,3)];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal=cross.sum(axis=0);length=np.linalg.norm(normal);ctr=tri.reshape(-1,3).mean(axis=0)
  color=(130,170,188)
  if length>1e-10:
   normal/=length;angle=math.degrees(math.asin(max(0,min(1,-normal[2]))))
   if normal[2]<-.1 and -5.56<ctr[0]<-2.04 and -10.56<ctr[1]<-8.84 and 13<ctr[2]<15.3:
    color=(218,84,84) if angle>50 else (228,178,55)
    faces.append({'key':f['key'],'angle_from_vertical_deg':angle,'area_mm2':float(np.linalg.norm(cross,axis=1).sum()/2),'centroid':ctr.tolist()})
  mm.append((color,tri.tolist()))
 rr.render(mm,eye=(-7.5,-23,9),target=(-3.8,-9.5,14.7),up=(0,0,1),size=(600,520),path=out/f'{name}-underside.png',scale=1600)
 canvas.paste(Image.open(out/f'{name}-underside.png'),(600*j,70))
 title=['Current underside','0.20 mm equal-distance bevel','0.20 mm angled bevel, one post'][j]
 draw.text((600*j+14,16),title,font=font,fill='#18394a')
 report['trials'][name]={'lower_volume_mm3':float(volume),'selected_post_underside_faces':faces}
draw.text((20,612),'Native CAD meshes, looking upward at the underside. Red: remaining 60-degree face. Gold: new bevel.',font=font,fill='#18394a')
canvas.save(out/'underside-trials.png')
old=report['trials']['before']['lower_volume_mm3']
for name in ['equal-bevel','angled-bevel']:
 r=report['trials'][name];r['removed_volume_mm3']=old-r['lower_volume_mm3'];r['removed_lower_shell_volume_percent']=100*r['removed_volume_mm3']/old
 before=json.loads(Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/print-layout.json').read_text())['assemblyInterference'];after=json.loads((out/(name+'-fit.json')).read_text())['pairs']
 assert len(before)==len(after)
 r['same_expected_pair_states']=all(a['interfering']==b['interfering'] and a['below_clearance']==b['below_clearance'] for a,b in zip(before,after))
 r['max_overlap_volume_difference_mm3']=max(abs(a['overlap_volume_mm3']-b['overlap_volume_mm3']) for a,b in zip(before,after))
 assert r['same_expected_pair_states'] and r['max_overlap_volume_difference_mm3']<1e-9
for bid in [1,53,54,173,267]:
 old=next(b for b in scenes['before']['bodies'] if b['id']==bid)
 assert all(old['mesh']==next(b for b in s['bodies'] if b['id']==bid)['mesh'] for s in scenes.values())
report['servo_bearing_hub_and_clips_unchanged']=True
report['angled_parameters']=json.loads((out/'angled-bevel-parameters.json').read_text())
(out/'geometry-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
