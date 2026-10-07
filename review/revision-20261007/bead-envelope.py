"""Nominal bead-envelope audit of archived native PETG toolpaths.

Capsules of commanded width approximate lateral deposited geometry. They do not
measure printed dimensions or reproduce bead/flow physics. Source files stay read-only.
"""
import argparse,hashlib,json,math,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--toolpaths',type=Path);args=p.parse_args()
src=args.source.resolve();out=Path(__file__).resolve().parent
toolpaths=args.toolpaths.resolve() if args.toolpaths else src
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
audit=json.loads((src/'geometry-audit.json').read_text());seat_end=audit['hidden_receiver_flank_boundary_Y_mm']
def parse(path):
    x=y=z=e=0.;relative=True;role='';width=.42;layer=0.;height=.16;active=False;segments=[]
    for num,line in enumerate(path.read_text().splitlines(),1):
        if line.startswith('; CHANGE_LAYER'):active=True
        for prefix,key in [('; Z_HEIGHT:','layer'),('; LAYER_HEIGHT:','height'),('; LINE_WIDTH:','width')]:
            if line.startswith(prefix):
                value=float(line.split(':')[1])
                if key=='layer':layer=value
                elif key=='height':height=value
                else:width=value
        if line.startswith('; FEATURE:'):role=line.split(':',1)[1].strip()
        cmd=line.split(';')[0].strip()
        if cmd=='M83':relative=True
        if cmd=='M82':relative=False
        vals={k:float(v) for k,v in re.findall(r'([XYZEIJ])(-?\d*\.?\d+)',cmd)}
        if cmd.startswith('G92'):e=vals.get('E',e);continue
        op=cmd.split(' ')[0]
        if op not in ('G0','G1','G2','G3'):continue
        nx,ny,nz=vals.get('X',x),vals.get('Y',y),vals.get('Z',z)
        de=vals.get('E',0) if relative else vals.get('E',e)-e;ps=[(x,y),(nx,ny)]
        if op in ('G2','G3') and ('I' in vals or 'J' in vals):
            cx=x+vals.get('I',0);cy=y+vals.get('J',0);r=math.hypot(x-cx,y-cy)
            aa=math.atan2(y-cy,x-cx);bb=math.atan2(ny-cy,nx-cx)
            sweep=(bb-aa)%(2*math.pi) if op=='G3' else -((aa-bb)%(2*math.pi))
            if abs(sweep)<1e-8:sweep=2*math.pi*(1 if op=='G3' else -1)
            n=max(2,math.ceil(abs(sweep)*r/.005));ps=[(cx+r*math.cos(aa+sweep*i/n),cy+r*math.sin(aa+sweep*i/n)) for i in range(n+1)]
        if active and de>0 and math.hypot(nx-x,ny-y)>1e-6 and abs(nz-layer)<.002 and role in ('Outer wall','Overhang wall'):
            for a,b in zip(ps,ps[1:]):segments.append({'a':a,'b':b,'top':layer,'h':height,'w':width,'role':role,'line':num})
        x,y,z=nx,ny,nz;e=e+de if relative else vals.get('E',e)
    return segments
corners=[('upper-left',-.85,24.703961852410437,1),('upper-right',16.85,24.703961852410437,1),('lower-left',-3.8,11.796038147589564,-1),('lower-right',13.9,11.796038147589564,-1)]
b=.373205080756889;results=[]
for case in ('clip-fine',):
    path=toolpaths/case/'plate_1.gcode';ps=parse(path);corner_rows=[]
    for name,cx,cz,sign in corners:
        rows=[]
        for top,h in sorted(set((p['top'],p['h']) for p in ps)):
            # Layer in original CAD Y is [12-top, 12-top+h].
            yy=(12-top,12-top+h)
            if yy[0]>10.2 or yy[1]<9.4:continue
            local=[]
            for pp in ps:
                if pp['top']!=top:continue
                for q in (pp['a'],pp['b']):
                    dx=q[0]-121.475-cx;dz=sign*(q[1]-109.75-cz)
                    if abs(dx)<.60 and .10<dz<.65:local.append((dx,dz,pp['w'],pp['line'],pp['role']))
            if not local:continue
            supports=[max(.5*side*dx+math.sqrt(3)/2*dz+w/2 for dx,dz,w,_,_ in local) for side in (-1,1)]
            midpoint=sum(yy)/2;dy=midpoint-9.8
            cad_r=(-.4+math.sqrt(.64-dy**2)) if abs(dy)<=.48 else None
            rows.append({'layer_top_mm':top,'layer_height_mm':h,'original_CAD_Y_interval_mm':yy,'CAD_Y_midplane_mm':midpoint,'CAD_radial_envelope_at_midplane_mm':cad_r,'nominal_capsule_flank_support_mm':supports,'nominal_capsule_flank_excess_mm':[v-b for v in supports],'intersects_receiver_end':yy[0]<=seat_end<=yy[1],'roles':sorted(set(q[4] for q in local))})
        end_rows=[r for r in rows if r['intersects_receiver_end']];assert len(end_rows)==1,(case,name,end_rows)
        corner_rows.append({'corner':name,'layers':rows,'receiver_end_layer':end_rows[0]})
    settings_file=toolpaths/case/'resolved-settings.json'
    settings=json.loads(settings_file.read_text()) if settings_file.exists() else json.loads((src/'petg-settings.json').read_text())
    results.append({'case':case,'gcode_sha256':sha(path),'filament_preset':settings['filament_settings_id'][0],'corners':corner_rows})
report={'reviewed_at':'2026-10-07','source_mesh_sha256':sha(src/'clip-fine.stl'),'housing_flank_plane_distance_mm':b,'method':'Outer/overhang wall segment endpoint support plus half commanded line width. G2/G3 segmented at <=0.005 mm arc length. Layer slab assumed constant bead envelope. Compared with exact unsliced housing plane, not sliced housing.','results':results,'limitations':['Nominal capsule envelope, not physical extrusion or dimensional measurement.','Housing toolpath geometry is not included; this cannot establish actual mating preload.','Slicer centerline rounding, bead cross section, shrinkage, line-width interpretation, seams, extrusion compensation and flow can change the real contact.']}
(out/'bead-envelope.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({case['case']:[{'corner':c['corner'],'layer':c['receiver_end_layer']['layer_top_mm'],'excess_mm':c['receiver_end_layer']['nominal_capsule_flank_excess_mm']} for c in case['corners']] for case in results},indent=2))
