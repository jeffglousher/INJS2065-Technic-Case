"""Summarize the checked PETG patch and nominal bead-envelope experiments."""
import sys,json,hashlib
from pathlib import Path
import argparse
p=argparse.ArgumentParser();p.add_argument('--python-libs',type=Path,required=True);args=p.parse_args()
sys.path.insert(0,str(args.python_libs))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent
fine=json.loads((R/'patch-sensitivity-0.09.json').read_text());coarse=json.loads((R/'patch-sensitivity-0.12.json').read_text());bead=json.loads((R/'bead-envelope.json').read_text())
summary=[]
for case in ['crest-broad','flanks-wide','flanks-narrow']:
    fs=[r for r in fine['results'] if r['patch_case']==case];cs=[r for r in coarse['results'] if r['patch_case']==case]
    row={'case':case,'V3_XY_isotropic_force_range_N':[min(min(r['forces_N_per_patch']) for r in fs),max(max(r['forces_N_per_patch']) for r in fs)],'finest_peak_strain_range_pct':[min(r['metrics']['max_abs_principal_strain'] for r in fs)*100,max(r['metrics']['max_abs_principal_strain'] for r in fs)*100],'last_mesh_peak_strain_relative_changes':[f['metrics']['max_abs_principal_strain']/c['metrics']['max_abs_principal_strain']-1 for f,c in zip(fs,cs)],'last_mesh_max_force_relative_change':max(max(abs(np.array(f['forces_N_per_patch'])/c['forces_N_per_patch']-1)) for f,c in zip(fs,cs))}
    summary.append(row)
envelopes=[]
for case in bead['results']:
    xs=[v*1000 for c in case['corners'] for v in c['receiver_end_layer']['nominal_capsule_flank_excess_mm']]
    envelopes.append({'case':case['case'],'nominal_clip_bead_flank_excess_range_um':[min(xs),max(xs)]})
report={'reviewed_at':'2026-10-07','canonical_geometry_unchanged':True,'main_material_case':'Current Bambu Lab PETG Basic TDS V3.0: isotropic surrogate E=2780 MPa; nu=0.38 assumed. Z E=2550 MPa is a separate scalar sensitivity, not an orthotropic bound.','static_patch_cases':summary,'nominal_bead_cases':envelopes,'CAD_radial_flank_overlap_um':7.742421174239,'holding_envelope_shift_mm':.02730182005407089,'source_sha256':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['patch-sensitivity-0.09.json','patch-sensitivity-0.12.json','bead-envelope.json']},'interpretation':'Axial reaction screening and patch sensitivity only. Narrow-patch elastic stresses exceed coupon strength; peak strains do not predict actual printed survival or contact pressure. Bead capsules are intended extrusion geometry, not printed measurements.'}
(R/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
fig,axes=plt.subplots(1,2,figsize=(12,5.8),layout='constrained')
x=np.arange(3);labels=['Broad crest','Wide flanks','Narrow flanks']
for support,color,marker in [('normal-floor','#196c96','o'),('clamped-floor','#a65f21','s')]:
    yy=[next(r for r in fine['results'] if r['support']==support and r['patch_case']==case)['metrics']['max_abs_principal_strain']*100 for case in ['crest-broad','flanks-wide','flanks-narrow']]
    axes[0].plot(x,yy,color=color,marker=marker,label=support)
    for xx,y in zip(x,yy):axes[0].annotate(f'{y:.2f}%',(xx,y),xytext=(0,8 if support=='clamped-floor' else -16),textcoords='offset points',ha='center',fontsize=9,color=color)
axes[0].set(xticks=x,xticklabels=labels,ylim=(0,9),ylabel='Peak absolute principal strain (%)',xlabel='Assumed pressure footprint',title='Linear screening: local peak depends on contact footprint\nEqual patch travel 0.02730 mm; E = 2780 MPa')
axes[0].legend(loc='upper left',fontsize=9);axes[0].grid(axis='y',alpha=.18)
for i,(case,color) in enumerate(zip(bead['results'],['#a65f21','#196c96'])):
    xx=[];yy=[]
    for j,c in enumerate(case['corners']):
        for k,v in enumerate(c['receiver_end_layer']['nominal_capsule_flank_excess_mm']):xx.append(j+(i-.5)*.16+(k-.5)*.045);yy.append(v*1000)
    axes[1].scatter(xx,yy,color=color,s=32,label=case['case'].replace('petg-classic-','Layer ').replace('016','0.16 mm').replace('012','0.12 mm'))
axes[1].axhline(7.742421174239,color='#526575',ls='--',lw=1,label='Unsliced CAD: 7.74 µm')
axes[1].set(xticks=np.arange(4),xticklabels=['Upper left','Upper right','Lower left','Lower right'],ylim=(0,13),ylabel='Nominal flank overrun vs CAD housing plane (µm)',xlabel='Corner (two flanks per corner)',title='Saved slicer paths + commanded bead width\nClip bead envelope; housing remains unsliced')
axes[1].legend(loc='upper left',fontsize=9);axes[1].grid(axis='y',alpha=.18)
fig.suptitle('Bambu PETG Basic: stiffness alone does not establish a reliable detent',fontsize=14)
fig.supxlabel('Left: elastic peaks exceed coupon strength and are not physical failure predictions. Right: nominal beads, not printed measurements.',fontsize=9)
fig.savefig(R/'petg-estimate-update.png',dpi=180)
print(json.dumps(report,indent=2))
