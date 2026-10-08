import json,sys,math,struct
from pathlib import Path
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
r=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hub-friction-20261007')
raw=(r/'hub-fine.stl').read_bytes();dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]);t=np.frombuffer(raw,dtype=dt,offset=84)['v'].astype(float);t[:,:,1]*=-1;t[:,:,2]=42-t[:,:,2]
sys.path.insert(0,'C:/Users/jeffg/dev/garden-auger-technic/scripts')
from raster_render import render
render([((190,211,226),t.tolist())],(26,-34,36),(0,0,7.85),(0,0,1),(650,800),r/'hub-iso.png',scale=2000)
fig=plt.figure(figsize=(11,7),dpi=170);a=fig.add_subplot(121);a.imshow(plt.imread(r/'hub-iso.png'));a.set_axis_off();a.set_title('Servo-facing socket / print orientation')
b=fig.add_subplot(122);d=json.loads((r/'hub-axial.json').read_text());todo=[e['points'] for e in d['section']];loops=[]
while todo:
 ps=todo.pop(0)
 while math.dist(ps[0],ps[-1])>1e-6:
  for i,q in enumerate(todo):
   if math.dist(ps[-1],q[0])<1e-6:ps+=q[1:];todo.pop(i);break
   if math.dist(ps[-1],q[-1])<1e-6:ps+=list(reversed(q))[1:];todo.pop(i);break
  else:raise ValueError('Open section')
 loops.append(ps)
for ps in loops:
 x,z=zip(*ps);b.fill(x,[42-v for v in z],facecolor='#abc8dc',edgecolor='#274d66',linewidth=1.6)
b.set_aspect('equal');b.set_xlim(-7,7);b.set_ylim(-.4,17.4);b.set_xlabel('X (mm)');b.set_ylabel('Height above bed (mm)');b.set_title('Native OCCT axial section');b.grid(alpha=.15)
b.annotate('Smooth diameter 5.70 mm',xy=(2.85,14),xytext=(0,16.8),ha='center',arrowprops={'arrowstyle':'->'},fontsize=10)
b.annotate('',xy=(4.5,15.7),xytext=(4.5,12),arrowprops={'arrowstyle':'<->'});b.text(4.7,13.85,'3.70 mm',fontsize=9,rotation=90,va='center')
b.text(0,10,'4.00 mm\nsolid web',ha='center',va='center',fontsize=10);b.text(0,4,'Axle socket',ha='center',va='center',fontsize=10)
fig.suptitle('Updated compact hub - friction-fit servo socket',fontsize=16);fig.text(.5,.045,'Diameter 5.70 / depth 3.70 / 0.15 mm entry chamfer. No tabs, separate horn or center-screw passage.',ha='center',fontsize=10);fig.tight_layout(rect=(0,.10,1,.93));fig.savefig(r/'hub-friction-views.png');plt.close(fig)
print('Saved updated hub views')
