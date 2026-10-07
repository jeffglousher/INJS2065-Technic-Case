"""Render fresh native triangle exports and their undeformed installed sections."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from PIL import Image
R=Path(__file__).parent
O=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/fit-review-20261007')
O.mkdir(parents=True,exist_ok=True)
dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
def read(name):return np.frombuffer((R/name).read_bytes(),dtype=dt,offset=84)['v'].astype(float)
clip,housing=read('clip.stl'),read('housing.stl')
def raster(meshes,center,fov,az=-70,el=30):
    tri=np.concatenate([t for t,c in meshes]);base=np.concatenate([np.tile(c,(len(t),1)) for t,c in meshes])
    a,e=np.deg2rad([az,el]);cam=np.array([np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)])
    right=np.array([-np.sin(a),np.cos(a),0]);up=np.cross(cam,right)
    local=tri-center;p=np.stack([local@right,local@up,local@cam],axis=-1)
    width,height=1400,1050
    p[:,:,0]=(p[:,:,0]/fov+.5)*width;p[:,:,1]=(.5-p[:,:,1]/(fov*.75))*height
    lo=np.floor(p[:,:,:2].min(axis=1)).astype(int);hi=np.ceil(p[:,:,:2].max(axis=1)).astype(int)
    ids=np.where((hi[:,0]>=0)&(lo[:,0]<width)&(hi[:,1]>=0)&(lo[:,1]<height))[0]
    norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],1e-12)
    light=cam+np.array([0,0,.8 if el>0 else -.8]);light/=np.linalg.norm(light)
    colors=base*(.48+.52*np.maximum(0,norm@light))[:,None]
    im=np.full((height,width,3),[245,247,250],dtype=np.uint8);depth=np.full((height,width),-np.inf)
    for i in ids:
        a,b,c=p[i];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-10:continue
        x0,y0=np.maximum(lo[i],[0,0]);x1,y1=np.minimum(hi[i],[width-1,height-1])
        xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
        w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w2=1-w0-w1
        z=w0*a[2]+w1*b[2]+w2*c[2];old=depth[y0:y1+1,x0:x1+1]
        vis=(w0>=-1e-7)&(w1>=-1e-7)&(w2>=-1e-7)&(z>old)
        old[vis]=z[vis];im[y0:y1+1,x0:x1+1][vis]=(255*colors[i]).astype(np.uint8)
    return Image.fromarray(im).resize((700,525),Image.Resampling.LANCZOS)
def panel(ax,meshes,center,fov,title,az=-70,el=30):
    ax.imshow(raster(meshes,np.array(center),fov,az,el));ax.axis('off');ax.set_title(title,color='#263849',fontsize=12,pad=8)
fig,axes=plt.subplots(1,2,figsize=(13,5.7),facecolor='#f5f7fa')
panel(axes[0],[(clip,[.81,.3,.4])],[6.525,10.5,18.25],31,'Clip pocket-side ISO: two rows of four hexes')
panel(axes[1],[(housing,[.28,.63,.65])],[8,0,25],55,'Clamshell: uniform hex installation recesses',az=70,el=25)
fig.suptitle('Fresh native CAD replay · geometry unchanged · 7 October 2026',fontsize=15,color='#263849')
fig.subplots_adjust(left=.01,right=.99,bottom=.04,top=.86,wspace=.02);fig.savefig(O/'clip-housing-iso.png',dpi=160);plt.close(fig)
fig,axes=plt.subplots(2,2,figsize=(11,9),facecolor='#f5f7fa')
corners=[('Upper-left',-.85,23,30),('Upper-right',16.85,23,30),('Lower-left',-3.8,13.5,-30),('Lower-right',13.9,13.5,-30)]
for ax,(title,x,z,el) in zip(axes.flat,corners):panel(ax,[(clip,[.81,.3,.4])],[x,10.5,z],8.2,title+': nub + rounded inner relief',el=el)
fig.suptitle('Four detent corners · continuous walls · ~0.90 mm minimum wall',fontsize=15,color='#263849')
fig.text(.5,.025,'Actual mesh surfaces; adjacent hexes are cropped by the camera, not cut from the model.',ha='center',fontsize=10,color='#526575')
fig.subplots_adjust(left=.01,right=.99,bottom=.05,top=.89,wspace=.02,hspace=.12);fig.savefig(O/'detent-corners.png',dpi=160);plt.close(fig)
def section(tris,x):
    out=[]
    for t in tris[(tris[:,:,0].min(axis=1)<x)&(tris[:,:,0].max(axis=1)>=x)]:
        ps=[]
        for a,b in zip(t,np.roll(t,-1,axis=0)):
            if (a[0]<x<=b[0])or(b[0]<x<=a[0]):ps.append((a+(b-a)*(x-a[0])/(b[0]-a[0]))[1:])
        if len(ps)==2:out.append(ps)
    return np.array(out)
sections={}
fig,axes=plt.subplots(1,2,figsize=(12,7),layout='constrained')
for ax,(name,x,z,limits) in zip(axes,[('Upper-left',-.85,24.9,(20,26.3)),('Lower-left',-3.8,11.6,(10.2,16.6))]):
    for key,t,col in [('housing',housing,'#218b83'),('clip',clip,'#be425e')]:
        seg=section(t,x);sections[name+'-'+key]=seg.tolist();ax.add_collection(LineCollection(seg,colors=col,linewidths=1.6,label=key.title()))
    ax.set(xlim=(8.6,12.4),ylim=limits,aspect='equal',xlabel='Y: across clip thickness (mm)',ylabel='Z: installed height (mm)',title=f'{name} installed section · X = {x:.2f} mm')
    ax.grid(alpha=.2);ax.legend(loc='center left',fontsize=10)
fig.suptitle('Undeformed clip + housing · receiving seat and corner backing\nMesh sections from fresh native STL exports; no deflection drawn',fontsize=14)
fig.savefig(O/'installed-sections.png',dpi=170);plt.close(fig)
(R/'mesh-sections.json').write_text(json.dumps(sections))
provenance=json.loads((R/'replay.json').read_text());provenance['renderer']='Depth-tested native STL triangles; installed section segments interpolate those triangles. Not deformed/contact-solved geometry.'
(O/'provenance.json').write_text(json.dumps(provenance,indent=2))
print('Fresh images saved to',O)
