import sys,pickle,struct,json,math
from pathlib import Path
R=Path(__file__).parent
sys.path.insert(0,str(R/'python-libs'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
paths=pickle.loads((R/'parsed-paths.pkl').read_bytes())
def mesh(name,upper):
    b=(R/name).read_bytes();n=struct.unpack_from('<I',b,80)[0];tri=[]
    for i in range(n):
        v=struct.unpack_from('<12f',b,84+50*i)[3:]
        t=[]
        for j in (0,3,6):
            x,y,z=v[j:j+3];t.append((x-8+128,(-y if upper else y)+128,42-z if upper else z-8))
        tri.append(t)
    return tri
def section(tris,z):
    out=[]
    for t in tris:
        ps=[]
        for a,b in zip(t,t[1:]+t[:1]):
            if (a[2]<z<=b[2]) or (b[2]<z<=a[2]):
                k=(z-a[2])/(b[2]-a[2]);ps.append((a[0]+k*(b[0]-a[0]),a[1]+k*(b[1]-a[1])))
        if len(ps)==2:out.append(ps)
    return out
fig,axes=plt.subplots(2,4,figsize=(16,8),layout='constrained');stats={}
for row,upper in enumerate((True,False)):
    name='petg-upper-shell-016' if upper else 'petg-lower-shell-016';ps=paths[name]
    tri=mesh('upper-shell-fine.stl' if upper else 'lower-shell-fine.stl',upper)
    cx=119.15 if upper else 116.2;cy=118.2 if upper else 137.8
    heights=(16.84,17.,17.16,17.32) if upper else (3.40,3.56,3.72,3.88)
    nearby=[p for p in ps if min(p['a'][0],p['b'][0])<cx+1 and max(p['a'][0],p['b'][0])>cx-1 and min(p['a'][1],p['b'][1])<cy+1 and max(p['a'][1],p['b'][1])>cy-1]
    seatpaths=[p for p in nearby if min(heights)-.01<=p['z']<=max(heights)+.01]
    stats[name]={'receiver_layer_features':sorted(set(p['f'] for p in seatpaths)),'bridge_segments_at_receiver_layers':sum(p['f']=='Bridge' for p in seatpaths),'total_bridge_length_mm':sum(math.dist(p['a'],p['b']) for p in ps if p['f']=='Bridge'),'longest_bridge_gcode_segment_mm':max((math.dist(p['a'],p['b']) for p in ps if p['f']=='Bridge'),default=0)}
    for ax,z in zip(axes[row],heights):
        sec=[[(a[0]-cx,a[1]-cy),(b[0]-cx,b[1]-cy)] for a,b in section(tri,z-.08) if min(a[0],b[0])<cx+1 and max(a[0],b[0])>cx-1 and min(a[1],b[1])<cy+1 and max(a[1],b[1])>cy-1]
        ax.add_collection(LineCollection(sec,colors='black',linewidths=1,linestyles='dotted'))
        for p in nearby:
            if abs(p['z']-z)>.001:continue
            color={'Outer wall':'#e8702a','Inner wall':'#cfaa11','Bridge':'#238cc4','Gap infill':'#616773'}.get(p['f'],'#8855bb')
            ax.plot([p['a'][0]-cx,p['b'][0]-cx],[p['a'][1]-cy,p['b'][1]-cy],color=color,lw=2)
        ax.set(xlim=(-.95,.95),ylim=(-1,1),aspect='equal',title=f'{"Upper" if upper else "Lower"} seat: layer top {z:.2f} mm',xlabel='Across receiver center (mm)',ylabel='Along clip insertion axis (mm)')
        ax.grid(alpha=.15)
fig.suptitle('Housing receiver toolpaths through neighboring layers\nDotted black: fine CAD mesh section at layer midplane. Orange/yellow: extrusion centerlines, excluding bead width.',fontsize=13)
fig.savefig(R/'housing-seat-toolpaths.png',dpi=160)
(R/'housing-path-check.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2))
