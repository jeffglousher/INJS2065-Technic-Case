from pathlib import Path
import sys,json
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs');sys.path.insert(0,'C:/Users/jeffg/dev/garden-auger-technic/scripts')
import numpy as np
import raster_render as rr
from PIL import Image,ImageDraw,ImageFont
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/flat-clip-base-20261008');font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
def meshes(b):
 pts=np.array(b['mesh']['positions']).reshape(-1,3);inds=np.array(b['mesh']['indices']);res=[]
 for f in b['faces']:
  p=f.get('plane');floor=p and abs(p['normal'][1])>.99 and abs(abs(p['origin'][1])-10.55)<1e-5
  rim=p and abs(p['normal'][1])>.99 and abs(abs(p['origin'][1])-9.05)<1e-5
  color=(137,195,218) if floor else ((188,190,196) if rim else (225,155,94))
  res.append((color,pts[inds[f['first_index']:f['first_index']+f['index_count']].reshape(-1,3)].tolist()))
 return res
canvas=Image.new('RGB',(1400,640),'#f6f8fa');d=ImageDraw.Draw(canvas)
for idx,label in enumerate(['before','after']):
 s=json.loads((out/('before-scene.json' if idx==0 else 'candidate-scene.json')).read_text());b=next(b for b in s['bodies'] if b['id']==173)
 rr.render(meshes(b),[-7,-3,25],[-.85,10.5,21.15],[0,0,1],(700,540),out/(label+'-detail.png'),1200)
 canvas.paste(Image.open(out/(label+'-detail.png')),(700*idx,55));d.text((24+700*idx,15),'Before: relief enters the floor' if idx==0 else 'After: flat floor, relieved wall retained',font=font,fill='#18394a')
d.text((24,605),'Native CAD geometry. Blue: pocket floor; orange: walls and detent. Same camera in both views.',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20),fill='#18394a');canvas.save(out/'clip-floor-before-after.png')
s=json.loads((out/'candidate-scene.json').read_text());b=next(b for b in s['bodies'] if b['id']==173);rr.render(meshes(b),[-5,-35,38],[6.525,10,18.25],[0,0,1],(1200,800),out/'clip-iso.png',1450)
# Named views use the actual native resolved poses.
p=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/root-ramp-20261008/render-views.py');src=p.read_text().replace('/root-ramp-20261008','/flat-clip-base-20261008').replace('current root-bevel revision','flat clip-floor revision');exec(compile(src,str(p),'exec'))
