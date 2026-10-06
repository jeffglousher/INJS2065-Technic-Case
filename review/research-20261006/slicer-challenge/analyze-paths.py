import json, math, re, sys, pickle
from pathlib import Path
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'python-libs'))

def parse(path):
    x=y=z=e=0.; relative=True; feature=''; width=.42; layer=0.; height=.16; active=False
    out=[]
    for num,line in enumerate(path.read_text().splitlines(),1):
        if line.startswith('; CHANGE_LAYER'): active=True
        if line.startswith('; Z_HEIGHT:'): layer=float(line.split(':')[1])
        if line.startswith('; LAYER_HEIGHT:'): height=float(line.split(':')[1])
        if line.startswith('; FEATURE:'): feature=line.split(':',1)[1].strip()
        if line.startswith('; LINE_WIDTH:'): width=float(line.split(':')[1])
        cmd=line.split(';')[0].strip()
        if cmd=='M83': relative=True
        if cmd=='M82': relative=False
        vals={k:float(v) for k,v in re.findall(r'([XYZEIJ])(-?\d*\.?\d+)',cmd)}
        if cmd.startswith('G92'):
            e=vals.get('E',e); continue
        op=cmd.split(' ')[0]
        if op not in ('G0','G1','G2','G3'):continue
        nx=vals.get('X',x);ny=vals.get('Y',y);nz=vals.get('Z',z)
        de=vals.get('E',0) if relative else vals.get('E',e)-e
        pts=[(x,y),(nx,ny)]
        if op in ('G2','G3') and ('I' in vals or 'J' in vals):
            cx=x+vals.get('I',0);cy=y+vals.get('J',0);r=math.hypot(x-cx,y-cy)
            a=math.atan2(y-cy,x-cx);b=math.atan2(ny-cy,nx-cx)
            sweep=(b-a)%(2*math.pi) if op=='G3' else -((a-b)%(2*math.pi))
            if abs(sweep)<1e-8:sweep=2*math.pi*(1 if op=='G3' else -1)
            n=max(2,math.ceil(abs(sweep)*r/.005))
            pts=[(cx+r*math.cos(a+sweep*i/n),cy+r*math.sin(a+sweep*i/n)) for i in range(n+1)]
        if active and de>0 and math.hypot(nx-x,ny-y)>1e-6 and abs(nz-layer)<.002:
            for p,q in zip(pts,pts[1:]):out.append(dict(a=p,b=q,z=layer,h=height,w=width,f=feature,line=num))
        x,y,z=nx,ny,nz
        e=e+de if relative else vals.get('E',e)
    return out

def apex(paths,cx,top):
    # Centerline extrema in 1.2 mm around each corner, restricted to its outside edge.
    vals=[q[1] for p in paths if p['f']=='Outer wall' for q in (p['a'],p['b'])
          if abs(q[0]-cx)<=.6 and ((q[1]>133.8) if top else (q[1]<122.2))]
    return (max(vals) if top else min(vals)) if vals else None

allpaths={};metrics={}
for case in json.loads((ROOT/'cases.json').read_text()):
    name=case['name'];ps=parse(ROOT/name/'plate_1.gcode');allpaths[name]=ps
    layers=sorted(set(p['z'] for p in ps));counts={f:sum(math.dist(p['a'],p['b']) for p in ps if p['f']==f) for f in set(p['f'] for p in ps)}
    m={'feature_length_mm':counts,'layers':len(layers)}
    if 'shell' not in name:
        peaks=[]
        for z in layers:
            pp=[p for p in ps if p['z']==z]
            if z<1.4:continue
            tops=[apex(pp,c,True) for c in (120.625,138.325)]
            bots=[apex(pp,c,False) for c in (117.675,135.375)]
            rt=apex(pp,126.525,True); rb=apex(pp,123.575,False)
            peaks.append({'z':z,'top_centerline_y':tops,'bottom_centerline_y':bots,
                          'nub_vs_plain_corner_mm':[v-rt if v is not None and rt is not None else None for v in tops]+[rb-v if v is not None and rb is not None else None for v in bots]})
        m['detent_layers']=peaks
        m['max_nub_vs_plain_corner_mm']=[max((p['nub_vs_plain_corner_mm'][i] or 0) for p in peaks) for i in range(4)]
    metrics[name]=m
(ROOT/'toolpath-metrics.json').write_text(json.dumps(metrics,indent=2))
(ROOT/'parsed-paths.pkl').write_bytes(pickle.dumps(allpaths))
print(json.dumps({n:{k:v for k,v in m.items() if k not in ('detent_layers','feature_length_mm')} for n,m in metrics.items()},indent=2))

if '--plot' in sys.argv:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    colors={'Outer wall':'#e8702a','Inner wall':'#cfaa11','Gap infill':'#616773','Top surface':'#cd3357','Internal solid infill':'#8855bb','Bridge':'#238cc4','Overhang wall':'#39a8a1'}
    fig,axes=plt.subplots(2,3,figsize=(15,9),layout='constrained')
    for ax,name in zip(axes.flat, list(allpaths)[:6]):
        ps=allpaths[name];zs=sorted(set(p['z'] for p in ps));z=min(zs,key=lambda v:abs(v-next(p['h']/2 for p in ps if p['z']==v)-2.2))
        for p in ps:
            if p['z']!=z:continue
            if max(p['a'][0],p['b'][0])<119.35 or min(p['a'][0],p['b'][0])>121.9:continue
            if max(p['a'][1],p['b'][1])<132.4:continue
            ax.plot([p['a'][0]-120.625,p['b'][0]-120.625],[p['a'][1]-134.6539618524,p['b'][1]-134.6539618524],color=colors.get(p['f'],'#637c84'),lw=2)
        ax.axhline(0,color='black',ls=':',lw=1,label='CAD plain ridge apex')
        ax.axhline(.2,color='black',ls='--',lw=1,label='CAD nub apex')
        ax.set(xlim=(-1.25,1.25),ylim=(-1.9,.35),aspect='equal',title=f'{name}\nLayer top Z={z:.2f} mm',xlabel='Across nub center (mm)',ylabel='From plain CAD apex (mm)')
        ax.grid(alpha=.15)
    fig.suptitle('Actual extrusion centerlines at the rounded detent\nCenterlines exclude bead width; they are not measurements of the printed surface.',fontsize=14)
    fig.savefig(ROOT/'detent-toolpath-comparison.png',dpi=160)
    plt.close(fig)
