import json,re,sys,zipfile,math,xml.etree.ElementTree as E
from collections import Counter
from pathlib import Path
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
out=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/assembly-print-20261007')
gcode=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/assembly-print-20261008/slice/plate_1.gcode')
pos={'X':0.,'Y':0.,'Z':0.,'E':0.};relative_e=True;absolute_xyz=True;feature='';obj=None;support=[];first=[];count=Counter()
for line in gcode.read_text().splitlines():
 if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
 if line.startswith('; start printing object'):obj=int(line.rsplit(':',1)[1])
 if line.startswith('; stop printing object'):obj=None
 cmd=line.split(';',1)[0].strip()
 if cmd=='M83':relative_e=True
 if cmd=='M82':relative_e=False
 if cmd=='G90':absolute_xyz=True
 if cmd=='G91':absolute_xyz=False
 if cmd.startswith(('G0 ','G1 ','G2 ','G3 ','G92 ')):
  tokens={k:float(v) for k,v in re.findall(r'([XYZEIJ])([-+]?(?:\d+(?:\.\d*)?|\.\d+))',cmd)}
  old=pos.copy()
  if cmd.startswith('G92 '):pos.update(tokens);continue
  for k,v in tokens.items():
   if k not in pos:continue
   pos[k]=v if k=='E' and not relative_e or k!='E' and absolute_xyz else pos[k]+v
  de=tokens.get('E',0) if relative_e else pos['E']-old['E']
  if obj is not None and de>0 and ('X' in tokens or 'Y' in tokens):
   count[obj]+=1
   path=[(old['X'],old['Y'],old['Z']),(pos['X'],pos['Y'],pos['Z'])]
   if cmd.startswith(('G2 ','G3 ')) and ('I' in tokens or 'J' in tokens):
    cx=old['X']+tokens.get('I',0);cy=old['Y']+tokens.get('J',0);rad=math.hypot(old['X']-cx,old['Y']-cy)
    a=math.atan2(old['Y']-cy,old['X']-cx);b=math.atan2(pos['Y']-cy,pos['X']-cx)
    delta=(b-a)%(2*math.pi) if cmd.startswith('G3 ') else -((a-b)%(2*math.pi))
    steps=max(2,math.ceil(abs(delta)/.03))
    path=[(cx+rad*math.cos(a+delta*j/steps),cy+rad*math.sin(a+delta*j/steps),pos['Z']) for j in range(steps+1)]
   if feature in ['Support','Support interface']:
    support.extend(path)
   if abs(pos['Z']-.2)<1e-5:first.extend([[(a[0],a[1]),(b[0],b[1])] for a,b in zip(path,path[1:])])
bounds=[[min(p[k] for p in support),max(p[k] for p in support)] for k in range(3)]
assert 170<bounds[0][0]<bounds[0][1]<210 and 80<bounds[1][0]<bounds[1][1]<120,bounds
assert len(count)==5,count
proof={'support_and_interface_extrusion_bounds_mm':bounds,'supports_confined_to_hub_region':True,'printed_object_count':len(count),'extrusion_segments_per_object':dict(count),'gcode_external_path':str(gcode),'print_sent':False}
(out/'toolpath-audit.json').write_text(json.dumps(proof,indent=2))
fig,ax=plt.subplots(figsize=(9,6),dpi=160)
ax.add_collection(LineCollection(first,colors='#196d87',linewidths=.35))
parts=json.loads((out/'assembly-project.json').read_text())['parts']
for p in parts:
 b=p['plate_bounds_mm'];ax.text(sum(b[0])/2,118 if p['body_id']==54 else b[1][1]+4,p['name'],ha='center',fontsize=10,color='#19354c')
ax.set_xlim(45,212);ax.set_ylim(78,169);ax.set_aspect('equal');ax.set_xlabel('Bed X (mm)');ax.set_ylabel('Bed Y (mm)');ax.set_title('Complete PETG print set — native Bambu first-layer toolpaths',pad=16)
fig.text(.5,.03,'X2D / 0.4 mm nozzle • Bambu PETG Basic • 0.12 mm layers • hub supports only',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.05,1,1));fig.savefig(out/'plate-layout.png');plt.close(fig)
print(json.dumps(proof,indent=2))
