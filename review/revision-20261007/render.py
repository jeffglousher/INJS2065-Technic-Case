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
O=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/revision-20261007')
O.mkdir(parents=True,exist_ok=True)
dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')])
def read(name):return np.frombuffer((R/name).read_bytes(),dtype=dt,offset=84)['v'].astype(float)
clip,minus,lower,upper=read('clip.stl'),read('clip-minus.stl'),read('lower.stl'),read('upper.stl')
red=[.81,.30,.40];teal=[.28,.63,.65]
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
panel(axes[0],[(clip,red)],[6.525,10.5,18.25],31,'Updated clip: pocket-side ISO')
panel(axes[1],[(np.concatenate([lower,upper]),teal)],[8,0,25],55,'Clamshell: unchanged exterior hex mouths',az=70,el=25)
fig.suptitle('Revised native CAD surfaces - 7 October 2026',fontsize=15,color='#263849');fig.subplots_adjust(left=.01,right=.99,bottom=.04,top=.86,wspace=.02);fig.savefig(O/'clip-housing-iso.png',dpi=160);plt.close(fig)
fig,axes=plt.subplots(2,2,figsize=(11,9),facecolor='#f5f7fa')
for ax,(title,x,z,el) in zip(axes.flat,[('Upper-left',-.85,23,30),('Upper-right',16.85,23,30),('Lower-left',-3.8,13.5,-30),('Lower-right',13.9,13.5,-30)]):panel(ax,[(clip,red)],[x,10.5,z],8.2,title+': broad crest + blended relief',el=el)
fig.suptitle('Four corners: full walls, 0.898 mm minimum wall, 1.00 mm backing',fontsize=14,color='#263849');fig.text(.5,.025,'Native mesh surfaces; adjacent hexes are cropped by the camera.',ha='center',fontsize=10,color='#526575');fig.subplots_adjust(left=.01,right=.99,bottom=.05,top=.89,wspace=.02,hspace=.12);fig.savefig(O/'detent-corners.png',dpi=160);plt.close(fig)
# Explode along actual installation/separation axes solely for the display.
explode=[(lower+[0,0,-10],teal),(upper+[0,0,14],teal),(clip+[0,35,0],red),(minus+[0,-35,0],red)]
fig,ax=plt.subplots(figsize=(11,8.8),facecolor='#f5f7fa');panel(ax,explode,[8,0,27],110,'Exploded housing and clips',az=-40,el=25)
fig.suptitle('Exploded inspection view - original part orientations retained',fontsize=15,color='#263849');fig.text(.5,.03,'Display offsets only: lower Z -10 mm; upper Z +14 mm; clips Y +/-35 mm. Servo omitted for visibility.',ha='center',fontsize=10,color='#526575');fig.subplots_adjust(left=.01,right=.99,bottom=.05,top=.9);fig.savefig(O/'exploded.png',dpi=160);plt.close(fig)
# Native OCCT section contours and OCCT cutaway meshes.
def native(name):return json.loads((R/(name+'-native.json')).read_text())
def contours(ax,name,color,label):
    parts=native(name)['section'];segs=[p['points'] for p in parts]
    ax.add_collection(LineCollection(segs,colors=color,linewidths=1.7,label=label))
def cutaway(name):
    m=native(name)['cutaway'];return np.array(m['positions']).reshape(-1,3)[np.array(m['indices']).reshape(-1,3)]
fig,axes=plt.subplots(1,3,figsize=(16,7),layout='constrained')
contours(axes[0],'clip-center','#be425e','Clip');contours(axes[0],'housing-center','#218b83','Housing')
axes[0].set(xlim=(8.85,12.2),ylim=(21,25.4),aspect='equal',xlabel='Y through clip thickness (mm)',ylabel='Z installed height (mm)',title='Center section: relief + receiving cavity')
axes[0].annotate('1.00 mm backing',xy=(11.5,21.55812),xytext=(10,22.2),arrowprops={'arrowstyle':'->'},fontsize=10)
axes[0].annotate('0.077 mm radial crest clearance',xy=(9.8,25.15),xytext=(9.2,24.1),arrowprops={'arrowstyle':'->'},fontsize=9)
contours(axes[1],'clip-flank','#be425e','Clip');contours(axes[1],'housing-flank','#218b83','Housing')
axes[1].set(xlim=(9.7,10.2),ylim=(24.95,25.14),aspect='equal',xlabel='Y through clip thickness (mm)',ylabel='Z installed height (mm)',title='Flank section: small seated engagement')
axes[1].annotate('Rounded hidden seat',xy=(9.93,25.08),xytext=(9.715,25.12),arrowprops={'arrowstyle':'->'},fontsize=9)
axes[1].text(.03,.03,'Nominal local inward shift: 0.0226 mm\nUndeformed parts shown; contact not solved.',transform=axes[1].transAxes,fontsize=9,color='#526575')
for ax in axes[:2]:ax.grid(alpha=.2);ax.legend(loc='lower right',fontsize=9)
panel(axes[2],[(cutaway('clip-center'),red),(cutaway('housing-center'),teal)],[-.85,10.5,23],8.7,'OCCT cutaway ISO at nub center',az=-145,el=30)
fig.suptitle('Native OCCT sections and cutaway - center and loaded flank shown separately',fontsize=14);fig.savefig(O/'sections.png',dpi=170);plt.close(fig)
# Compare screening, with equal-displacement comparisons kept distinct.
old=json.loads(Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/review/petg-update-20261007/patch-sensitivity-0.09.json').read_text())
new=json.loads((R/'patch-sensitivity-0.09.json').read_text());angled=json.loads((R/'cap-normal-sensitivity-0.09.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(12,6.2));fig.subplots_adjust(bottom=.22,top=.86,left=.075,right=.98,wspace=.23);names=['Crest patch','Wide flanks','Narrow flanks']
for k,name in enumerate(['crest-broad','flanks-wide','flanks-narrow']):
    oo=[x for x in old['results'] if x['patch_case']==name];nn=[x for x in new['results'] if x['patch_case']==name]
    for vals,offset,col,label in [(oo,-.18,'#8495a7','Previous'),(nn,.18,'#be425e','Revised')]:
        force=[v for x in vals for v in x['forces_N_per_patch']];peak=[x['metrics']['max_abs_principal_strain']*100 for x in vals]
        for ax,metric in zip(axes,[force,peak]):ax.bar(k+offset,np.mean(metric),width=.3,color=col,label=label if k==0 else None);ax.plot([k+offset,k+offset],[min(metric),max(metric)],color='#253747',linewidth=1.5)
for ax in axes:ax.set_xticks(range(3),names);ax.grid(axis='y',alpha=.2);ax.legend();ax.set_xlabel('Assumed load footprint')
axes[0].set(ylabel='Axial reaction per nub (N)',title='Prescribed-displacement screening reaction')
axes[1].set(ylabel='Maximum absolute principal strain (%)',title='Local elastic peaks: unconverged screening')
fig.suptitle('PETG Basic V3: revised mesh and geometry compared with previous screening',fontsize=13)
fig.text(.5,.04,'Previous travel 0.0273 mm; revised travel 0.0226 mm. Lines show range across modeled supports/corners, not physical bounds.\nSeat-normal loading and point-anchor artifacts are reported separately. Neither insertion contact nor creep is solved.',ha='center',fontsize=9,color='#526575');fig.savefig(O/'strain-comparison.png',dpi=160,bbox_inches='tight');plt.close(fig)
print('Saved images to',O,flush=True)
