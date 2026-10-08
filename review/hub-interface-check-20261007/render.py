import json,sys,math
from pathlib import Path
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hub-interface-review-20261007')
def loops(edges):
 todo=[[list(p) for p in e['points']] for e in edges];result=[]
 while todo:
  pts=todo.pop(0)
  while math.dist(pts[0],pts[-1])>1e-6:
   for i,p in enumerate(todo):
    if math.dist(pts[-1],p[0])<1e-6:pts.extend(p[1:]);todo.pop(i);break
    if math.dist(pts[-1],p[-1])<1e-6:pts.extend(list(reversed(p))[1:]);todo.pop(i);break
   else:raise ValueError('Open native section')
  result.append(pts)
 return sorted(result,key=lambda ps:abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ps,ps[1:]))),reverse=True)
fig,axes=plt.subplots(1,2,figsize=(11,6.5),dpi=170)
for ax,name in zip(axes,['current-servo-mouth','auger-servo-mouth']):
 d=json.loads((r/(name+'.json')).read_text())
 for i,pts in enumerate(loops(d['section'])):
  x,y=zip(*pts);ax.fill(x,y,color='#b5cfde' if i==0 else 'white',edgecolor='#274d66',linewidth=1.8)
 ax.set_xlim(-3.7,3.7);ax.set_ylim(-3.7,3.7);ax.set_aspect('equal');ax.set_xticks([-3,0,3]);ax.set_yticks([-3,0,3]);ax.grid(alpha=.12);ax.set_xlabel('mm');ax.set_ylabel('mm')
axes[0].set_title('Current hub: four inward tabs',fontsize=13)
axes[0].annotate('Tabs reduce opening to 4.20 mm',xy=(2.1,0),xytext=(0,3.25),ha='center',fontsize=10,arrowprops={'arrowstyle':'->'})
axes[0].text(0,-3.4,'Nominal round recess: diameter 5.60 mm',ha='center',fontsize=10)
axes[1].set_title('Current garden auger: smooth round pilot',fontsize=13)
axes[1].text(0,0,'Diameter 5.70 mm\nDepth 3.70 mm',ha='center',va='center',fontsize=12)
axes[1].text(0,-3.4,'Direct to servo shaft; center screw required',ha='center',fontsize=10)
fig.suptitle('Servo-facing mouth comparison - native OCCT sections',fontsize=15)
fig.text(.5,.025,'Equal-scale mouth closeups. The auger dimensions remain a fit prototype, not a verified fit for the INJS2065 servo.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.15,1,.91));fig.savefig(r/'servo-mouth-comparison.png');plt.close(fig)
print('Saved mouth comparison')
