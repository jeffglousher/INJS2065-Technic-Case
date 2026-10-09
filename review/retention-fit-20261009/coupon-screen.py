"""Nominal paired printed bead screen; not a physical contact/strain model."""
from pathlib import Path
import sys,json
out=Path(__file__).resolve().parent
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/loose-fit-20261009/python-libs')
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
from shapely.geometry import LineString,box
from shapely.ops import unary_union
n={};exec(Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/hub-quality-20261008/audit.py').read_text().split('old=parse(oldpath);new=parse(newpath)')[0],n);ps=n['parse'](out/'retention-coupon-slice/plate_1.gcode');print('object ids',sorted(set(p['obj'] for p in ps)));(out/'coupon-paths.json').write_text(json.dumps(ps))
excluded={'Support','Support interface','Brim','Skirt'}
corners=[('upper-left',-.85,24.703961852410437,2),('upper-right',16.85,24.703961852410437,2),('lower-left',-3.8,11.796038147589564,1),('lower-right',13.9,11.796038147589564,1)]
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
for sign,clipid in [(1,3),(1,4),(1,5)]:
    clipps=[p for p in ps if p['obj']==clipid and p['feature'] not in excluded]
    for corner,cx,cz,shellid in corners:
        roi=box(cx-.64,cz+.12,cx+.64,cz+.6) if shellid==2 else box(cx-.64,cz-.6,cx+.64,cz-.12)
        shellps=[p for p in ps if p['obj']==shellid and p['feature'] not in excluded]
        for mag in [10.10,10.1424065573,10.18]:
            y=sign*mag
            cp=[p for p in clipps if 12-p['z']-1e-6<=mag<=12-p['z']+p['height']+1e-6]
            ct=lambda a:(a[0]-({3:143.475,4:143.475,5:213.475}[clipid]),a[1]-({3:36.75,4:156.75,5:96.75}[clipid]))
            a=nearby_buffer(cp,ct,roi).intersection(roi)
            polys=[]
            for top in sorted(set(p['z'] for p in shellps)):
                lp=[p for p in shellps if p['z']==top]
                lo,hi=(27.6-top,27.6-top+lp[0]['height']) if shellid==2 else (top+8-lp[0]['height'],top+8)
                if hi<roi.bounds[1] or lo>roi.bounds[3]:continue
                st=(lambda q:(q[0]-42,175-q[1])) if shellid==2 else (lambda q:(q[0]-42,q[1]-55))
                mat=nearby_buffer(lp,st,box(cx-1,y-.3,cx+1,y+.3))
                cross=mat.intersection(LineString([(cx-1,y),(cx+1,y)]))
                for l in lines(cross):polys.append(box(l.bounds[0],lo,l.bounds[2],hi))
            b=unary_union(polys).intersection(roi)
            assert not a.is_empty and not b.is_empty,(sign,corner,y)
            row={'clip_object':clipid,'nub_protrusion_mm':{3:.26,4:.24,5:.28}[clipid],'corner':corner,'Y_mm':y,'nominal_overlap_area_mm2':a.intersection(b).area,'surface_setback_sensitivity':[{'setback_per_surface_mm':d,'overlap_area_mm2':a.buffer(-d).intersection(b.buffer(-d)).area} for d in [.01,.02,.03,.04,.05]]}
            rows.append(row)
report={'method':'Three coupon clips and cropped receivers; actual native slice; both clips and both shells. Commanded-width capsules and constant layer slabs, local nub ROI. Surface erosion is a hypothetical sensitivity, not measured dimensional error.','results':rows}
(out/'coupon-corners.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'sampled_sections':len(rows),'nominal_overlap_area_range_mm2':[min(r['nominal_overlap_area_mm2'] for r in rows),max(r['nominal_overlap_area_mm2'] for r in rows)],'no_overlap_count_by_setback':{d:sum(r['surface_setback_sensitivity'][i]['overlap_area_mm2']<1e-12 for r in rows) for i,d in enumerate([.01,.02,.03,.04,.05])}},indent=2))
