import sys,json,hashlib
from pathlib import Path
r=Path(__file__).parent
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
sys.path.insert(0,str(r/'python-libs'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
f=np.load(r/'field-0.09-normal-floor.npz');x=f['xyz'];tet=f['tet'];u=f['u']*f['scale']
xp=x[tet];up=u[tet];cut=-.85
mask=(xp[:,:,0].min(1)<=cut+1e-9)&(xp[:,:,0].max(1)>=cut-1e-9)&(xp[:,:,2].max(1)>20)&(xp[:,:,2].min(1)<25.3)
polys=[];values=[]
for xx,uu in zip(xp[mask],up[mask]):
    ps=[];vs=[]
    for a in range(4):
        if abs(xx[a,0]-cut)<1e-9:ps.append(xx[a,1:]);vs.append(-uu[a,1]*1000)
    for a,b in [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]:
        if (xx[a,0]-cut)*(xx[b,0]-cut)<0:
            t=(cut-xx[a,0])/(xx[b,0]-xx[a,0]);ps.append((xx[a]+t*(xx[b]-xx[a]))[1:]);vs.append(-(uu[a]+t*(uu[b]-uu[a]))[1]*1000)
    if len(ps)<3:continue
    _,unique=np.unique(np.round(np.array(ps),9),axis=0,return_index=True)
    ps=np.array(ps)[unique];vs=np.array(vs)[unique]
    if len(ps)<3:continue
    ps=np.array(ps);c=ps.mean(0);order=np.argsort(np.arctan2(ps[:,1]-c[1],ps[:,0]-c[0]));polys.append(ps[order]);values.append(np.mean(vs))
fig,(ax,bx)=plt.subplots(1,2,figsize=(12,7.8),gridspec_kw={'width_ratios':[1.05,1]})
fig.subplots_adjust(left=.07,right=.97,top=.84,bottom=.25,wspace=.36)
pc=PolyCollection(polys,array=np.array(values),cmap='viridis',edgecolors='face',linewidths=.15,clim=(0,30));ax.add_collection(pc)
ax.set(xlim=(8.7,12.35),ylim=(20,25.45),xlabel='Across clip thickness Y (mm)',ylabel='Height along clip Z (mm)',title='Actual upper-left corner section\nCalculated inward movement at nominal travel')
ax.set_aspect('equal');ax.invert_xaxis()
cb=fig.colorbar(pc,cax=fig.add_axes([.11,.115,.29,.025]),orientation='horizontal');cb.set_label('Calculated inward displacement (µm)',fontsize=9)
ax.annotate('Nub travel ≈27 µm',xy=(9.8,25.05),xytext=(11.6,25.1),arrowprops=dict(arrowstyle='->',color='#202830'),fontsize=9)
ax.annotate('Backing minimum: 1.00 mm',xy=(11.5,22.02),xytext=(11.9,23.5),arrowprops=dict(arrowstyle='->',color='#202830'),fontsize=9,ha='left')
ax.annotate('Real crease at floor\n44° normal change',xy=(10.55,20.90757),xytext=(9.1,20.15),arrowprops=dict(arrowstyle='->',color='#202830'),fontsize=9,ha='right')
reports=[json.loads((r/f'fem-{lev}.json').read_text()) for lev in [.35,.2,.12,.09]]
fine=reports[-1]['results'];k=np.array([v['preload_force_N_per_nub']/v['preload_mm'] for v in fine]);delta=np.linspace(0,.05,100)
bx.fill_between(delta*1000,delta*k.min()*1120/1460,delta*k.max()*1790/1460,color='#dce4ea',label='Material sensitivity: 1.12–1.79 GPa surrogate')
for v,color in zip(fine,['#156b98','#aa5519']):
    bx.plot(delta*1000,delta*v['preload_force_N_per_nub']/v['preload_mm'],color=color,label='Sliding floor support' if v['support']=='normal-floor' else 'Fixed floor support')
bx.axvline(27.30182,color='#65717b',ls='--',lw=1)
bx.scatter([27.30182]*2,[v['preload_force_N_per_nub'] for v in fine],c=['#156b98','#aa5519'],zorder=5)
bx.annotate('Nominal residual travel\n≈4.4–4.5 N per nub',xy=(27.3,4.5),xytext=(3,7.5),arrowprops=dict(arrowstyle='->',color='#202830'),fontsize=10)
bx.set(xlabel='Imposed inward nub travel (µm)',ylabel='Force per nub (N)',title='Travel sensitivity of the current corner\nFour nubs loaded together; housing held rigid',xlim=(0,50),ylim=(0,11));bx.grid(alpha=.2);bx.legend(loc='upper left',bbox_to_anchor=(0,-.18),fontsize=8,frameon=False)
fig.suptitle('Bambu PETG Basic: corner flex screening',fontsize=17)
fig.text(.51,.025,'E = 1.46 GPa; assumed ν = 0.38. Linear solid model, 208,626 tetrahedra.\nForce changed 1.6% on final refinement. Not an insertion-force, creep or fatigue prediction.',ha='center',fontsize=9)
fig.savefig(r/'petg-corner-mechanics.png',dpi=180,bbox_inches='tight')
result=dict(material='Bambu PETG Basic',youngs_modulus_MPa=1460,modulus_source='Bambu Technical Data Sheet V2.0, XY tensile modulus; specimens annealed and dried at 65 C for 8 h',source_url='https://www.additive-x.com/shop/media/mageplaza/product_attachments/attachment_file/b/a/bambu_petg_basic_technical_data_sheet_18.pdf',poisson_assumed=.38,dimensions_mm=dict(in_plane_min_wall=.8975842277326658,minimum_Y_backing=1.,full_Y_thickness=2.95,spherical_relief_radius=1.6,nub_radial_height=.20),preload_geometric_travel_mm=.02730182005407089,force_N_per_nub_at_nominal=[v['preload_force_N_per_nub'] for v in fine],peak_linear_principal_strain_at_nominal=[v['maximum_principal_strain_at_preload'] for v in fine],final_force_refinement_relative=[abs(fine[i]['preload_force_N_per_nub']/reports[-2]['results'][i]['preload_force_N_per_nub']-1) for i in range(2)],limitations=['Floor surfaces constrained; real unilateral contact, flexible housing, friction and load direction are not solved.','Linear isotropic continuum approximates printed material. No toolpath-resolved voids, creep, yielding or fatigue.','0.0273 mm is geometric residual travel, not a measured installed deflection.','0.20 mm radial nub rise is not inward travel. Peak insertion travel remains unverified.','Sharp edges and the prescribed finite nub load patch affect local peak strains; peak strain is a screening flag, not a validated allowable.'],canonical_geometry_changed=False,source_sha256=hashlib.sha256(Path('C:/Users/jeffg/dev/INJS2065-Technic-Case/design/current.model.json').read_bytes()).hexdigest(),step_sha256=hashlib.sha256((r/'current.step').read_bytes()).hexdigest(),recommendation='Keep about 0.9 mm minimum in-plane wall and 1.0 mm minimum backing for now. Prefer a longer, tapered interior flex region and tangent blends at relief-to-floor/wall junctions; preserve full walls and nub envelope. Evaluate a roughly 0.4–0.6 mm blend locally rather than assuming a round cutter makes a smooth junction. Recalculate and reslice before claiming reliability.')
(r/'mechanics-review.json').write_text(json.dumps(result,indent=2))
