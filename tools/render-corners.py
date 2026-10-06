"""Render four corner closeups from the fine STL exported by native CAD.

This renders the actual triangle geometry; it does not reconstruct the detents.
Example: py -3 tools/render-corners.py --mesh clip.stl --output-dir review/corners
"""
import argparse
import json
import hashlib
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--mesh', type=Path, required=True)
parser.add_argument('--output-dir', type=Path, required=True)
parser.add_argument('--python-libs', type=Path)
args = parser.parse_args()
if args.python_libs:
    sys.path.insert(0, str(args.python_libs))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

raw = args.mesh.read_bytes()
count = int.from_bytes(raw[80:84], 'little')
dtype = np.dtype([('normal', '<f4', 3), ('vertices', '<f4', (3, 3)), ('attribute', '<u2')])
triangles = np.frombuffer(raw, dtype=dtype, count=count, offset=84)['vertices'].astype(float)
assert len(raw) == 84 + count * 50
args.output_dir.mkdir(parents=True, exist_ok=True)

corners = [
    ('upper-left', 'Upper-left corner', -.85, 23.0, 30),
    ('upper-right', 'Upper-right corner', 16.85, 23.0, 30),
    ('lower-left', 'Lower-left corner', -3.8, 13.5, -30),
    ('lower-right', 'Lower-right corner', 13.9, 13.5, -30),
]

def draw(ax, cx, cz, elevation):
    # Orthographic depth rasterization avoids painter-order artifacts where a
    # large planar triangle overlaps many tiny rounded-pocket triangles.
    angle = np.deg2rad(-70)
    elev = np.deg2rad(elevation)
    toward_camera = np.array([np.cos(elev)*np.cos(angle), np.cos(elev)*np.sin(angle), np.sin(elev)])
    right = np.array([-np.sin(angle), np.cos(angle), 0])
    up = np.cross(toward_camera, right)
    tri = triangles
    local = tri - np.array([cx, 10.5, cz])
    projected = np.stack([local@right, local@up, local@toward_camera],axis=-1)
    width, height = 1600, 1280
    pixels = projected.copy()
    pixels[:,:,0] = (projected[:,:,0]/8.2+.5)*width
    pixels[:,:,1] = (.5-projected[:,:,1]/6.56)*height
    lo = np.floor(pixels[:,:,:2].min(axis=1)).astype(int)
    hi = np.ceil(pixels[:,:,:2].max(axis=1)).astype(int)
    candidates = np.where((hi[:,0]>=0)&(lo[:,0]<width)&(hi[:,1]>=0)&(lo[:,1]<height))[0]
    normals = np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1)[:,None], 1e-12)
    light = np.array([-.25, -.75, .61 if elevation > 0 else -.61])
    light /= np.linalg.norm(light)
    brightness = .48 + .52*np.maximum(0, normals @ light)
    colors = np.clip(np.array([.81, .30, .40])[None,:]*brightness[:,None], 0, 1)
    image = np.empty((height,width,3),dtype=np.uint8)
    image[:]=[244,246,248]
    depth=np.full((height,width),-np.inf)
    for index in candidates:
        a,b,c=pixels[index]
        denominator=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(denominator)<1e-10:continue
        x0,y0=np.maximum(lo[index],[0,0]);x1,y1=np.minimum(hi[index],[width-1,height-1])
        xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
        w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/denominator
        w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/denominator
        w2=1-w0-w1
        z=w0*a[2]+w1*b[2]+w2*c[2]
        old=depth[y0:y1+1,x0:x1+1]
        visible=(w0>=-1e-7)&(w1>=-1e-7)&(w2>=-1e-7)&(z>old)
        old[visible]=z[visible]
        image[y0:y1+1,x0:x1+1][visible]=(255*colors[index]).astype(np.uint8)
    image=Image.fromarray(image).resize((800,640),Image.Resampling.LANCZOS)
    ax.imshow(image)
    ax.set_axis_off()

fig = plt.figure(figsize=(12,10), facecolor='#f4f6f8')
for i,(name,title,cx,cz,elevation) in enumerate(corners):
    ax = fig.add_subplot(2,2,i+1,facecolor='#f4f6f8')
    draw(ax,cx,cz,elevation)
    ax.set_title(title, fontsize=14, color='#223242', pad=8)
fig.suptitle('Committed clip: rounded relief behind each detent\nMinimum corner wall ≈0.90 mm · Minimum backing 1.00 mm',fontsize=16,color='#223242',y=.97)
fig.text(.5,.035,'Pocket-side closeups from the verified CAD mesh. Adjacent cells are cropped by the viewport.',ha='center',fontsize=10,color='#526575')
fig.subplots_adjust(left=.02,right=.98,bottom=.07,top=.85,wspace=.02,hspace=.10)
fig.savefig(args.output_dir/'corner-closeups.png',dpi=180,facecolor=fig.get_facecolor())
plt.close(fig)
for name,title,cx,cz,elevation in corners:
    fig=plt.figure(figsize=(8,7),facecolor='#f4f6f8')
    ax=fig.add_subplot(facecolor='#f4f6f8')
    draw(ax,cx,cz,elevation)
    ax.set_title(title+' — pocket-side relief',fontsize=15,color='#223242')
    fig.subplots_adjust(left=0,right=1,bottom=0,top=.94)
    fig.savefig(args.output_dir/(name+'.png'),dpi=180,facecolor=fig.get_facecolor())
    plt.close(fig)
manifest={'source_mesh_sha256':hashlib.sha256(raw).hexdigest(),'triangles':count,'renderer':'Orthographic depth rasterization of native CAD STL triangles, 2x supersampling','geometry_modified':False,'views':[c[0] for c in corners]}
(args.output_dir/'render-provenance.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest))
