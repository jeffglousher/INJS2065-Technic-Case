"""Render the README gallery from the reviewed print meshes and reference hardware.

Run `node tools/export-gallery-scene.mjs` first, then
`uv run --with pillow python tools/render-readme.py`.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/images'
OUT.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('render', ROOT / 'tools/mesh-render.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
scene = json.loads((ROOT / 'local/readme-gallery-scene.json').read_text())
proof = json.loads((ROOT / 'local/readme-gallery-proof.json').read_text())
model = json.loads((ROOT / 'design/current.model.json').read_text())
candidate = ROOT / 'print/servo-holder.3mf'
receipt = json.loads((ROOT / 'docs/validation.json').read_text())
sha = lambda raw: hashlib.sha256(raw).hexdigest()
assert sha(candidate.read_bytes()) == receipt['project_sha256']
native = {b['id']: b for b in scene['bodies']}
reference = json.loads((ROOT / 'docs/model-reference.json').read_text())
assert sha((ROOT/'local/readme-gallery-scene.json').read_bytes()) == proof['scene_sha256']
assert proof['model_sha256'] == reference['canonicalModelSha256'] == sha((ROOT/'design/current.model.json').read_bytes())
assert proof['hardware_mesh_sha256'] == {str(b['id']):b['meshSha256'] for b in reference['bodies'] if b['id'] in (1,53)}
for bid in (1,53):
    assert bid in native

# Undo the manufacturing orientation/centering of the reviewed exported meshes.
# These are rigid display transforms; the five part payloads remain untouched.
transforms = {
    1:(8, lambda x,y,z:(x+8,y,z+8)),
    2:(18,lambda x,y,z:(x+8,-y,42-z)),
    3:(173,lambda x,y,z:(x+6.525,12-z,y+18.25)),
    4:(267,lambda x,y,z:(x+6.525,-12+z,18.25-y)),
    5:(54,lambda x,y,z:(x,-y,42-z)),
}
meshes = {bid:r.scene_mesh(native[bid]) for bid in (1,53)}
raw_parts = {}
mesh_hashes = {}
with zipfile.ZipFile(candidate) as z:
    for i,(bid,tf) in transforms.items():
        raw = z.read(f'3D/Objects/object_{i}.model')
        assert sha(raw) == receipt['parts'][i-1]['mesh_sha256']
        m = ET.fromstring(raw)
        vertices = [tuple(float(v.get(a)) for a in ('x','y','z')) for v in m.iter(r.NS+'vertex')]
        faces = [tuple(int(f.get(a)) for a in ('v1','v2','v3')) for f in m.iter(r.NS+'triangle')]
        raw_parts[i] = vertices,faces
        meshes[bid] = [tf(*v) for v in vertices],faces
        mesh_hashes[str(bid)] = sha(raw)
colors = {1:r.HARDWARE,8:r.TEAL,18:r.TEAL,53:r.HARDWARE,54:r.GREY,173:r.RED,267:r.RED}
ids = [8,18,1,53,54,173,267]
view = next(v for v in model['views'] if v['name']=='Exploded assembly')
structure = model['assembly']['component_structure']
definitions = {d['id']:d for d in structure['definitions']}
occurrences = {o['id']:o for o in structure['occurrences']}
offsets = {}
for row in view['occurrence_offsets']:
    assert row['rotation'] == [0,0,0,1]
    definition = definitions[occurrences[row['occurrence_id']]['component_id']]
    for bid in definition['body_ids']:
        offsets[bid] = row['translation']
offsets[53] = (0,0,44)
offsets[54] = (0,0,60)

def parts(amount=0):
    return [(([tuple(v[j]+amount*offsets.get(bid,(0,0,0))[j] for j in range(3))
               for v in meshes[bid][0]],meshes[bid][1]),colors[bid]) for bid in ids]

def save(name, image):
    image.save(OUT / name)
    print('Rendered',name,flush=True)

if '--animation-only' not in sys.argv:
    direction = (1,-1,.85)
    save('assembly.png',r.render(parts(),'INJS2065 servo holder',direction,(1100,800)))
    save('assembly-rear.png',r.render(parts(),'Rear and cable-side view',(-1,1,.65),(900,680)))
    save('underside.png',r.render(parts(),'Underside and servo opening',(1,-1,-.9),(900,680)))
    exploded = parts(1)
    base = r.render(exploded,'',direction,(900,920))
    image = Image.new('RGB',(1500,1000),r.BG)
    image.paste(base,(300,50))
    d = ImageDraw.Draw(image)
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',27)
    bold = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',38)
    d.text((48,25),'How it fits together',font=bold,fill=(35,49,65))
    camera = r.unit(direction)
    right = r.unit(r.cross((0,0,1),camera)); up = r.cross(camera,right)
    points=[(r.dot(v,right),r.dot(v,up)) for (vertices,_),_ in exploded for v in vertices]
    xlo,xhi=min(p[0] for p in points),max(p[0] for p in points)
    ylo,yhi=min(p[1] for p in points),max(p[1] for p in points)
    scale=min(820/(xhi-xlo),790/(yhi-ylo))
    def anchor(bid):
        vertices=meshes[bid][0]
        center=tuple((min(v[j] for v in vertices)+max(v[j] for v in vertices))/2+offsets[bid][j] for j in range(3))
        return (750+(r.dot(center,right)-(xlo+xhi)/2)*scale,
                50+965/2-(r.dot(center,up)-(ylo+yhi)/2)*scale)
    labels=[(54,'Output hub',1175,140),(53,'MR128 bearing',1175,260),
            (18,'Upper shell',48,200),(1,'INJS2065 servo',48,440),
            (267,'Clip -Y',48,690),(173,'Clip +Y',1175,650),(8,'Lower shell',1175,850)]
    for bid,text,x,y in labels:
        target=anchor(bid)
        d.text((x,y),text,font=font,fill=(35,49,65))
        start=(x+d.textlength(text,font=font)+8,y+38) if x<300 else (x,y+38)
        elbow=(420 if x<300 else 1140,y+38)
        d.line([start,elbow,target],fill=(94,114,136),width=2)
        d.ellipse((target[0]-4,target[1]-4,target[0]+4,target[1]+4),fill=(35,49,65))
    d.text((48,953),'Five printed parts + two purchased parts. Display offsets are not assembly clearances.',font=font,fill=(94,114,136))
    save('exploded.png',image)
    save('exploded-rear.png',r.render(exploded,'Exploded from the opposite side',(-1,1,.85),(1100,850)))
    r.pair(r.render([(raw_parts[1],r.TEAL)],'Lower shell interior',(1,-1,1.2),(700,540)),
           r.render([(raw_parts[2],r.TEAL)],'Upper shell interior',(1,-1,1.2),(700,540)),OUT/'shell-interiors.png')
    r.pair(r.render([(raw_parts[3],r.RED)],'Clip pockets and nubs',(1,-1,1.8),(700,540)),
           r.render([(raw_parts[3],r.RED)],'Clip rear and flat bed face',(-1,1,-1.8),(700,540)),OUT/'clip-detail.png')
    r.pair(r.render([(raw_parts[5],r.GREY)],'Servo friction-fit socket',(1,-1,1.25),(700,540)),
           r.render([(raw_parts[5],r.GREY)],'Technic cross socket',(1,-1,-1.25),(700,540)),OUT/'hub-detail.png')

# Match the auger README's animated hero. The whole assembly turns for inspection;
# this is a camera presentation, not a simulated servo or constrained mechanism.
frames=[]
for i in range(20):
    angle=2*math.pi*i/20
    pp=parts()
    all_vertices=[v for (vertices,_),_ in pp for v in vertices]
    lo=[min(v[j] for v in all_vertices) for j in range(3)]
    hi=[max(v[j] for v in all_vertices) for j in range(3)]
    center=[(a+b)/2 for a,b in zip(lo,hi)]
    radius=max(math.sqrt(sum((v[j]-center[j])**2 for j in range(3))) for v in all_vertices)
    camera=r.unit((math.cos(angle),math.sin(angle),.55))
    right=r.unit(r.cross((0,0,1),camera)); up=r.cross(camera,right)
    # Invisible view-aligned framing corners hold scale and center fixed.
    frame_bounds=[tuple(center[j]+radius*(a*right[j]+b*up[j]) for j in range(3)) for a,b in ((-1,-1),(1,1))]
    frame=r.render(pp+[((frame_bounds,[]),r.BG)],'',camera,(900,650))
    frames.append(frame)
    if i%5==0: print('Turntable frame',i+1,'/20',flush=True)
boxes=[ImageChops.difference(f,Image.new('RGB',f.size,r.BG)).getbbox() for f in frames]
crop=(max(0,min(b[0] for b in boxes)-24),max(0,min(b[1] for b in boxes)-24),
      min(frames[0].width,max(b[2] for b in boxes)+24),min(frames[0].height,max(b[3] for b in boxes)+24))
frames=[f.crop(crop).convert('P',palette=Image.Palette.ADAPTIVE,colors=128) for f in frames]
frames=frames[-3:]+frames[:-3]  # Start on the clip side; preserve the continuous orbit.
frames[0].save(OUT/'turntable.gif',save_all=True,append_images=frames[1:],duration=160,loop=0,disposal=2)
print('Rendered turntable.gif',flush=True)
subprocess.run([sys.executable,str(ROOT/'tools/render-print-plate.py')],check=True)
manifest={'model_sha256':sha((ROOT/'design/current.model.json').read_bytes()),
          'print_project':str(candidate.relative_to(ROOT)).replace('\\','/'),
          'print_project_sha256':sha(candidate.read_bytes()),'printable_mesh_sha256':mesh_hashes,
          'hardware_source':'Native reference bodies 1 and 53, checked against docs/model-reference.json',
          'hardware_mesh_sha256':proof['hardware_mesh_sha256'],
          'printable_display_transforms':'Rigid inverse manufacturing orientation/centering, not a new CAD export',
          'exploded_offsets':'Saved Exploded assembly translations; bearing +44 and hub +60 mm in Z for visibility',
          'animation':'Whole-assembly turntable; illustrative camera presentation, no mechanism solve',
          'files':{p.name:sha(p.read_bytes()) for p in sorted(OUT.iterdir()) if p.suffix in ('.png','.gif')},
          'geometry_changed':False,'print_sent':False}
(ROOT/'docs/gallery-sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
