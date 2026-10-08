from pathlib import Path
import sys,json,math
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs');sys.path.insert(0,'C:/Users/jeffg/dev/garden-auger-technic/scripts')
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import raster_render as rr
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/root-ramp-20261008');s=json.loads((out/'candidate-scene.json').read_text());m=json.loads((out/'candidate.model.json').read_text());solutions=json.loads((out/'named-view-solutions.json').read_text());colors={1:(80,85,92),8:(140,178,190),18:(140,178,190),53:(196,200,204),54:(182,155,111),173:(182,65,90),267:(182,65,90)}
meshes={b['id']:np.array(b['mesh']['positions']).reshape(-1,3)[np.array(b['mesh']['indices']).reshape(-1,3)] for b in s['bodies']}
def matrix(q):
 x,y,z,w=q;return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for name,path in [('Assembled ISO','assembled'),('Exploded assembly','exploded'),('PETG print by object','print-layout')]:
 view=next(v for v in m['views'] if v['name']==name);camera=view['camera'];mm=[]
 for pose in solutions[name]['instance_body_poses']:
  if not pose['visible']:continue
  tri=meshes[pose['body_id']]@matrix(pose['rotation']).T+pose['translation'];mm.append((colors[pose['body_id']],tri.tolist()))
 if path=='print-layout':mm.insert(0,((63,70,78),[[(0,0,-.1),(256,0,-.1),(256,256,-.1)],[(0,0,-.1),(256,256,-.1),(0,256,-.1)]]))
 rr.render(mm,eye=camera['position'],target=camera['target'],up=camera['up'],size=(1100,760),path=out/(path+'-raw.png'),scale=1450)
 im=Image.open(out/(path+'-raw.png'));canvas=Image.new('RGB',(1100,850),'#f6f8fa');canvas.paste(im,(0,55));d=ImageDraw.Draw(canvas);d.text((24,15),name+' - saved native named view',font=font,fill='#18394a');d.text((24,815),'Saved display transforms; geometry shown is the current root-bevel revision.',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18),fill='#18394a');canvas.save(out/(path+'.png'))
print('Rendered saved native named-view solutions')
