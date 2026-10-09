from pathlib import Path
import sys,json,math
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
repo=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/loose-fit-20261009');n={};exec((repo/'review/hub-quality-20261008/audit.py').read_text().split('old=parse(oldpath);new=parse(newpath)')[0],n)
cases=[('printed-0.16',Path('C:/Users/jeffg/AppData/Local/Temp/bamboo_model/Thu_Oct_08/08_54_00#7056#69/Metadata/.7056.0.gcode'),183),('reviewed-0.12',Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/flat-clip-base-20261008/flat-floor-slice/plate_1.gcode'),3)]
report={}
for name,path,oid in cases:
 ps=n['parse'](path);print(name,'ids',sorted(set(p['obj'] for p in ps)));rows=[]
 for corner,cx,cz,sign in [('upper-left',-.85,24.703961852410437,1),('upper-right',16.85,24.703961852410437,1),('lower-left',-3.8,11.796038147589564,-1),('lower-right',13.9,11.796038147589564,-1)]:
  ll=[]
  for top in sorted(set(p['z'] for p in ps if p['obj']==oid)):
   paths=[p for p in ps if p['obj']==oid and p['z']==top and p['feature'] in ['Outer wall','Overhang wall']];loc=[]
   for p in paths:
    for xx,yy in p['points']:
     dx=xx-143.475-cx;dz=sign*(yy-36.75-cz)
     if abs(dx)<.6 and .1<dz<.65:loc.append((dx,dz,p['width'],p['height']))
   if not loc:continue
   h=loc[0][3];ys=[12-top,12-top+h]
   if min(ys)>10.15 or max(ys)<9.4:continue
   excess=[max(.5*side*dx+math.sqrt(3)/2*dz+w/2 for dx,dz,w,h in loc)-.373205080756889 for side in [-1,1]]
   ll.append({'top':top,'height':h,'Y_slab':ys,'flank_excess_mm':excess,'covers_flank_boundary':ys[0]<=9.982743096<=ys[1]})
  rows.append({'corner':corner,'layers':ll})
 report[name]=rows
 (out/(name+'-paths.json')).write_text(json.dumps(ps))
 print(name,[{'corner':r['corner'],'boundary':next(l for l in r['layers'] if l['covers_flank_boundary'])} for r in rows])
(out/'nub-toolpaths.json').write_text(json.dumps(report,indent=2))
