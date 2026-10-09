"""Nominal paired printed bead screen; not a physical contact/strain model."""
from pathlib import Path
import sys,json
out=Path(__file__).resolve().parent
sys.path.insert(0,str(out/'python-libs'))
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
from shapely.geometry import LineString,box
from shapely.ops import unary_union
ps=json.loads((out/'printed-0.16-paths.json').read_text())
excluded={'Support','Support interface','Brim','Skirt'}
corners=[('upper-left',-.85,24.703961852410437,161),('upper-right',16.85,24.703961852410437,161),('lower-left',-3.8,11.796038147589564,139),('lower-right',13.9,11.796038147589564,139)]
def nearby_buffer(paths,transform,roi):
    bufs=[];xmin,ymin,xmax,ymax=roi.bounds
    for p in paths:
        for aa,bb in zip(p['points'],p['points'][1:]):
            a,b=transform(aa),transform(bb);r=p['width']/2
            if max(a[0],b[0])+r<xmin or min(a[0],b[0])-r>xmax or max(a[1],b[1])+r<ymin or min(a[1],b[1])-r>ymax:continue
            bufs.append(LineString([a,b]).buffer(r,quad_segs=12))
    return unary_union(bufs)
def lines(g):
    if g.geom_type=='LineString':return [g]
    return [x for sub in getattr(g,'geoms',[]) for x in lines(sub)]
rows=[]
for sign,clipid in [(1,183),(-1,205)]:
    clipps=[p for p in ps if p['obj']==clipid and p['feature'] not in excluded]
    for corner,cx,cz,shellid in corners:
        roi=box(cx-.64,cz+.12,cx+.64,cz+.6) if shellid==161 else box(cx-.64,cz-.6,cx+.64,cz-.12)
        shellps=[p for p in ps if p['obj']==shellid and p['feature'] not in excluded]
        for mag in [9.98,10.015,10.06]:
            y=sign*mag
            cp=[p for p in clipps if 12-p['z']-1e-6<=mag<=12-p['z']+p['height']+1e-6]
            ct=lambda a:(a[0]-143.475,a[1]-36.75 if sign==1 else 193.25-a[1])
            a=nearby_buffer(cp,ct,roi).intersection(roi)
            polys=[]
            for top in sorted(set(p['z'] for p in shellps)):
                lp=[p for p in shellps if p['z']==top]
                lo,hi=(42-top,42-top+lp[0]['height']) if shellid==161 else (top+8-lp[0]['height'],top+8)
                if hi<roi.bounds[1] or lo>roi.bounds[3]:continue
                st=(lambda q:(q[0]-42,175-q[1])) if shellid==161 else (lambda q:(58-q[0],55-q[1]))
                mat=nearby_buffer(lp,st,box(cx-1,y-.3,cx+1,y+.3))
                cross=mat.intersection(LineString([(cx-1,y),(cx+1,y)]))
                for l in lines(cross):polys.append(box(l.bounds[0],lo,l.bounds[2],hi))
            b=unary_union(polys).intersection(roi)
            assert not a.is_empty and not b.is_empty,(sign,corner,y)
            row={'clip_body':173 if sign==1 else 267,'corner':corner,'Y_mm':y,'nominal_overlap_area_mm2':a.intersection(b).area,'surface_setback_sensitivity':[{'setback_per_surface_mm':d,'overlap_area_mm2':a.buffer(-d).intersection(b.buffer(-d)).area} for d in [.01,.02,.03,.04,.05]]}
            rows.append(row)
report={'method':'Actual cached job; both clips and both shells. Commanded-width capsules and constant layer slabs, local nub ROI. Surface erosion is a hypothetical sensitivity, not measured dimensional error.','results':rows}
(out/'all-corners.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'sampled_sections':len(rows),'nominal_overlap_area_range_mm2':[min(r['nominal_overlap_area_mm2'] for r in rows),max(r['nominal_overlap_area_mm2'] for r in rows)],'no_overlap_count_by_setback':{d:sum(r['surface_setback_sensitivity'][i]['overlap_area_mm2']<1e-12 for r in rows) for i,d in enumerate([.01,.02,.03,.04,.05])}},indent=2))
