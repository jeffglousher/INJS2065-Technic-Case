"""Illustrate the current saved 3MF placement with its matched native slice estimate."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'print/servo-holder.3mf'
OUT = ROOT / 'docs/images/print-plate.png'
receipt = json.loads((ROOT / 'docs/validation.json').read_text())
assert hashlib.sha256(PROJECT.read_bytes()).hexdigest() == receipt['project_sha256']
plate = receipt['native_slice']['sliced_plates'][0]
assert not plate['warning_message'] and len(plate['objects']) == 5
ns = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
prod = '{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
im = Image.new('RGB',(1300,990),'#f1f5f9')
d = ImageDraw.Draw(im)
bold = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',36)
font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',27)
small = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23)
d.text((40,25),'Five parts, one PETG plate',font=bold,fill='#233141')
seconds=plate['total_predication']; grams=plate['filaments'][0]['total_used_g']
d.text((40,80),f'Native estimate: {seconds/3600:.2f} h · {grams:.2f} g  |  X2D · 0.4 mm · PETG Basic',font=font,fill='#233141')
left,top,size=40,145,750
d.rectangle((left,top,left+size,top+size),fill='#303b46')
for i in range(0,257,16):
    a=left+i/256*size; b=top+i/256*size
    d.line((a,top,a,top+size),fill='#46535f')
    d.line((left,b,left+size,b),fill='#46535f')
colors=['#3f9aa2','#3f9aa2','#c24259','#c24259','#909eab']
names=['Lower shell','Upper shell','Clip +Y','Clip -Y','Output hub']
def transform(v,t):
    return tuple(sum(v[k]*t[k*3+j] for k in range(3))+t[9+j] for j in range(3))
with zipfile.ZipFile(PROJECT) as z:
    model=ET.fromstring(z.read('3D/3dmodel.model'))
    resources={n.get('id'):n for n in model.find(ns+'resources')}
    for i,item in enumerate(model.find(ns+'build')):
        obj=resources[item.get('objectid')]
        components=obj.find(ns+'components')
        assert len(components)==1, 'Unexpected printable components'
        component=components[0]
        path=component.get(prod+'path').lstrip('/')
        mesh=ET.fromstring(z.read(path))
        vertices=[tuple(float(v.get(a)) for a in ('x','y','z')) for v in mesh.iter(ns+'vertex')]
        identity=[1,0,0,0,1,0,0,0,1,0,0,0]
        ct=list(map(float,component.get('transform','').split())) or identity
        bt=list(map(float,item.get('transform','').split())) or identity
        points=[transform(transform(v,ct),bt) for v in vertices]
        faces=[tuple(int(f.get(a)) for a in ('v1','v2','v3')) for f in mesh.iter(ns+'triangle')]
        # Top view with painter sorting: higher faces cover lower surfaces.
        for face in sorted(faces,key=lambda f:sum(points[j][2] for j in f)):
            poly=[(left+points[j][0]/256*size,top+size-points[j][1]/256*size) for j in face]
            d.polygon(poly,fill=colors[i])
        cx=sum(v[0] for v in points)/len(points); cy=sum(v[1] for v in points)/len(points)
        # Number badges correspond to the labeled list outside the bed.
        x=left+cx/256*size; y=top+size-cy/256*size-42
        d.ellipse((x-17,y-17,x+17,y+17),fill='#f1f5f9',outline=colors[i],width=2)
        d.text((x,y),str(i+1),font=small,fill='#233141',anchor='mm')
for i,name in enumerate(names):
    y=215+i*105
    d.ellipse((835,y,861,y+26),fill=colors[i])
    d.text((880,y-7),f'{i+1}. {name}',font=font,fill='#233141')
d.text((835,790),'Print by object',font=font,fill='#233141')
d.text((835,835),'No supports or brims',font=font,fill='#233141')
d.text((40,930),'Saved 3MF placement, rendered from its meshes · Colors identify parts, not filament changes',font=small,fill='#5e7288')
OUT.parent.mkdir(parents=True,exist_ok=True)
im.save(OUT)
print('Rendered',OUT,flush=True)
