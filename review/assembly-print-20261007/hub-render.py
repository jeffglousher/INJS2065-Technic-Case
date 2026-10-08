import json,sys,math
from pathlib import Path
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/assembly-print-20261008')
def loops(edges):
 todo=[[list(p) for p in e['points']] for e in edges];result=[]
 while todo:
  pts=todo.pop(0)
  while math.dist(pts[0],pts[-1])>1e-6:
   for i,p in enumerate(todo):
    if math.dist(pts[-1],p[0])<1e-6:pts.extend(p[1:]);todo.pop(i);break
    if math.dist(pts[-1],p[-1])<1e-6:pts.extend(list(reversed(p))[1:]);todo.pop(i);break
   else:raise ValueError('Native section edge chain not closed')
  result.append(pts)
 return sorted(result,key=lambda ps:abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ps,ps[1:]))),reverse=True)
fig,axes=plt.subplots(1,2,figsize=(11,7),dpi=160)
for ax,n in zip(axes,['hub-socket','hub-axial']):
 d=json.loads((out/(n+'.json')).read_text())
 for i,points in enumerate(loops(d['section'])):
  x,y=zip(*points);ax.fill(x,y,facecolor='#abc8db' if i==0 else 'white',edgecolor='#254e68',linewidth=1.6)
 ax.set_aspect('equal');ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.15)
axes[0].set_title('Axle socket section (world Z = 40 mm)');axes[0].set_xlim(-5,5);axes[0].set_ylim(-5,5);axes[0].set_xlabel('X (mm)');axes[0].set_ylabel('Y (mm)')
axes[0].annotate('Central cross-shaped socket',xy=(0,0),xytext=(0,4.5),ha='center',arrowprops={'arrowstyle':'->','color':'#254e68'},fontsize=10)
axes[0].text(0,-4.6,'4.85 mm span / 1.85 mm arm width',ha='center',fontsize=10)
a=axes[1];a.set_title('Axial section (world Y = 0 mm)');a.set_xlim(-7,7);a.set_ylim(25.4,43.7);a.set_xlabel('X (mm)');a.set_ylabel('World Z (mm)')
a.annotate('Axle socket\n8.0 mm deep',xy=(0,38),xytext=(0,43),ha='center',va='top',arrowprops={'arrowstyle':'->'},fontsize=10)
a.annotate('',xy=(0,34),xytext=(0,30.2),arrowprops={'arrowstyle':'<->','color':'#8d4319'})
a.text(.4,32.1,'3.8 mm web',ha='left',va='center',fontsize=10,color='#8d4319')
a.text(0,28.1,'Servo-side\nrecess',ha='center',va='center',fontsize=10)
fig.suptitle('Current output hub: separate blind sockets, solid web between',fontsize=14)
fig.text(.5,.035,'Native OCCT sections of unchanged body 54. CAD orientation shown; the print project flips Z42 onto the bed.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.07,1,.94));fig.savefig(out/'hub-socket-sections.png');plt.close(fig)
print('Saved native hub section image')
