"""Compare native slices after flipping only the output hub's placement."""
from pathlib import Path
import hashlib, json, math, re, subprocess, zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hub-orientation-20261010')
SOURCE = ROOT/'review/print-decision-20261009/assembly-petg-review.3mf'
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', NS)
ET.register_namespace('p', 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(SOURCE) as z:
    original = {n:z.read(n) for n in z.namelist()}
mesh = ET.fromstring(original['3D/Objects/object_5.model'])
vertices = [tuple(float(v.get(k)) for k in ('x','y','z')) for v in mesh.findall('.//{'+NS+'}vertex')]
height = max(v[2] for v in vertices)
results = {}
for mode, support in [('flipped-auto', '1'), ('flipped-no-support', '0')]:
    data = original.copy()
    main = ET.fromstring(data['3D/3dmodel.model'])
    cfg = ET.fromstring(data['Metadata/model_settings.config'])
    item = next(b for b in main.find('{'+NS+'}build') if b.get('objectid')=='105')
    assert item.get('transform') == '1 0 0 0 1 0 0 0 1 220 115 0'
    transform = f'1 0 0 0 -1 0 0 0 -1 220 115 {height:.9f}'
    item.set('transform', transform)
    for b in cfg.findall('assemble/assemble_item'):
        if b.get('object_id') == '105': b.set('transform', transform)
    hub = next(o for o in cfg.findall('object') if o.get('id')=='105')
    next(m for m in hub.findall('metadata') if m.get('key')=='enable_support').set('value', support)
    for m in cfg.findall('plate/metadata'):
        if m.get('key')=='plater_name':m.set('value','Full PETG assembly - servo socket down - '+mode)
    main.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
    data['3D/3dmodel.model'] = ET.tostring(main, encoding='utf-8',xml_declaration=True)
    data['Metadata/model_settings.config'] = ET.tostring(cfg, encoding='utf-8',xml_declaration=True)
    target = HERE/(mode+'.3mf')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in data.items():z.writestr(n,b)
    old_main = ET.fromstring(original['3D/3dmodel.model'])
    assert ET.tostring(main.find('{'+NS+'}resources')) == ET.tostring(old_main.find('{'+NS+'}resources'))
    assert all(ET.tostring(a)==ET.tostring(b) for a,b in zip(list(main.find('{'+NS+'}build'))[:4],list(old_main.find('{'+NS+'}build'))[:4]))
    old_cfg = ET.fromstring(original['Metadata/model_settings.config'])
    assert [ET.tostring(o) for o in cfg.findall('object')[:4]] == [ET.tostring(o) for o in old_cfg.findall('object')[:4]]
    assert all(b==original[n] for n,b in data.items() if n not in ('3D/3dmodel.model','Metadata/model_settings.config'))
    # Validate the entire settings tree after reversing just the approved edits.
    restored = ET.fromstring(data['Metadata/model_settings.config'])
    for b in restored.findall('assemble/assemble_item'):
        if b.get('object_id')=='105': b.set('transform','1 0 0 0 1 0 0 0 1 220 115 0')
    restored_hub = next(o for o in restored.findall('object') if o.get('id')=='105')
    for m in restored_hub.findall('metadata'):
        if m.get('key')=='enable_support': m.set('value','1')
    old_label = next(m.get('value') for m in old_cfg.findall('plate/metadata') if m.get('key')=='plater_name')
    for m in restored.findall('plate/metadata'):
        if m.get('key')=='plater_name': m.set('value',old_label)
    assert ET.tostring(restored)==ET.tostring(old_cfg)
    folder = OUT/mode;folder.mkdir(exist_ok=True)
    command = ['C:/Program Files/Bambu Studio/bambu-studio.exe','--load-filaments',
        'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007/bambu-petg-basic-resolved.json',
        '--slice','1','--outputdir',str(folder),str(target)]
    run = subprocess.run(command,cwd=folder,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=180)
    (folder/'cli.log').write_bytes(run.stdout+run.stderr)
    result = json.loads((folder/'result.json').read_text())
    assert run.returncode == result['return_code'] == 0
    assert len(result['sliced_plates'][0]['objects'])==5
    assert not result['sliced_plates'][0]['warning_message']
    results[mode] = {'project_sha256':sha(target),'gcode_sha256':sha(folder/'plate_1.gcode'),
        'source_project_sha256':sha(SOURCE),'prepared_by_script_sha256':sha(Path(__file__)),
        'canonical_sha256':sha(ROOT/'design/current.model.json'),'canonical_geometry_changed':False,
        'hub_transform':transform,'native_result':result,'meshes_unchanged':True,
        'other_four_placements_and_configs_unchanged':True,'print_sent':False}

def paths(path):
    pos=dict(X=0.,Y=0.,Z=0.,E=0.);relative_e=True;absolute=True;obj=None;feature='';width=0.;height=0.;out=[]
    for line in path.read_text().splitlines():
        if line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
        if line.startswith('; LINE_WIDTH:'):width=float(line.split(':',1)[1])
        if line.startswith('; LAYER_HEIGHT:'):height=float(line.split(':',1)[1])
        if line.startswith('; start printing object'):obj=int(line.rsplit(':',1)[1])
        if line.startswith('; stop printing object'):obj=None
        cmd=line.split(';',1)[0].strip()
        if cmd=='M83':relative_e=True
        if cmd=='M82':relative_e=False
        if cmd=='G90':absolute=True
        if cmd=='G91':absolute=False
        if not cmd.startswith(('G0 ','G1 ','G2 ','G3 ','G92 ')):continue
        vals={k:float(v) for k,v in re.findall(r'([XYZEIJF])([-+]?(?:\d+(?:\.\d*)?|\.\d+))',cmd)}
        previous=pos.copy()
        if cmd.startswith('G92 '):pos.update({k:v for k,v in vals.items() if k in pos});continue
        for k,v in vals.items():
            if k in pos:pos[k]=v if (k=='E' and not relative_e or k!='E' and absolute) else pos[k]+v
        extruded=vals.get('E',0) if relative_e else pos['E']-previous['E']
        if obj!=5 or extruded<=0 or not ('X' in vals or 'Y' in vals):continue
        points=[(previous['X']-220,previous['Y']-115),(pos['X']-220,pos['Y']-115)]
        if cmd.startswith(('G2 ','G3 ')):
            cx=previous['X']+vals.get('I',0);cy=previous['Y']+vals.get('J',0)
            r=math.hypot(previous['X']-cx,previous['Y']-cy)
            a=math.atan2(previous['Y']-cy,previous['X']-cx);b=math.atan2(pos['Y']-cy,pos['X']-cx)
            delta=(b-a)%(2*math.pi) if cmd.startswith('G3 ') else -((a-b)%(2*math.pi))
            if abs(delta)<1e-8:delta=(2*math.pi if cmd.startswith('G3 ') else -2*math.pi)
            count=max(2,math.ceil(abs(delta)/.025))
            points=[(cx+r*math.cos(a+delta*j/count)-220,cy+r*math.sin(a+delta*j/count)-115) for j in range(count+1)]
        out.append(dict(feature=feature,z=pos['Z'],width=width,height=height,e=extruded,points=points))
    return out

baseline = json.loads((SOURCE.parent/'package-audit.json').read_text())['native_result']
results['current']={'project_sha256':sha(SOURCE),'native_result':baseline,
    'gcode_sha256':sha(Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-decision-20261009/plate_1.gcode'))}
for mode in ('current','flipped-auto','flipped-no-support'):
    gcode = Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-decision-20261009/plate_1.gcode') if mode=='current' else OUT/mode/'plate_1.gcode'
    q=paths(gcode)
    assert q,mode
    support=sum(p['e'] for p in q if p['feature'] in ('Support','Support interface'))
    support_in_servo = [p for p in q if p['feature'] in ('Support','Support interface')
        and .25 < p['z'] < 3.40 and any(math.hypot(x,y)<2.55 for x,y in p['points'])] if mode!='current' else []
    bridge=[p for p in q if p['feature']=='Bridge']
    model=[p for p in q if p['feature'] not in ('Support','Support interface','Skirt','Brim')]
    # Socket interiors exclude the wall/chamfer and 0.30 mm near each closed floor.
    servo_range=(12.30,15.45) if mode=='current' else (.25,3.40)
    servo_hits=[p for p in model if servo_range[0]<p['z']<servo_range[1] and any(math.hypot(x,y)<2.55 for x,y in p['points'])]
    cross_range=(.25,7.70) if mode=='current' else (8.0,15.45)
    cross_hits=[p for p in model if cross_range[0]<p['z']<cross_range[1] and any((abs(x)<.70 and abs(y)<2.10) or (abs(y)<.70 and abs(x)<2.10) for x,y in p['points'])]
    plate=results[mode]['native_result']['sliced_plates'][0]
    results[mode]['toolpath_summary']={'hub_support_filament_mm':support,
        'hub_bridge_segments':len(bridge),'hub_bridge_z_mm':sorted(set(round(p['z'],3) for p in bridge)),
        'hub_sparse_infill_segments':sum(p['feature']=='Sparse infill' for p in model),
        'servo_socket_interior_support_centerline_hits':len(support_in_servo),
        'servo_socket_model_centerline_hits':len(servo_hits),'cross_socket_model_centerline_hits':len(cross_hits),
        'total_seconds':plate['total_predication'],'total_grams':plate['filaments'][0]['total_used_g'],
        'warning':plate['warning_message'],'first_layer_hub_z_mm':min(p['z'] for p in model),
        'socket_check_limit':'Interior centerline samples excluding walls/floors; not full swept-bead or physical fit proof.'}
    assert not servo_hits and not cross_hits,(mode,len(servo_hits),len(cross_hits))
    assert not results[mode]['toolpath_summary']['hub_sparse_infill_segments']
(HERE/'comparison.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({mode:r['toolpath_summary'] for mode,r in results.items()},indent=2))

# Genuine mesh sections and native toolpath centerlines, not illustrative CAD.
import sys
sys.path.insert(0, 'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

triangles = [tuple(int(t.get(k)) for k in ('v1','v2','v3')) for t in mesh.findall('.//{'+NS+'}triangle')]
section=[]
for t in triangles:
    points=[]
    for i,j in ((0,1),(1,2),(2,0)):
        a,b=vertices[t[i]],vertices[t[j]]
        if a[1]*b[1]<0:
            ratio=-a[1]/(b[1]-a[1]); points.append((a[0]+ratio*(b[0]-a[0]),a[2]+ratio*(b[2]-a[2])))
        elif abs(a[1])<1e-7: points.append((a[0],a[2]))
    unique=list(dict.fromkeys(points))
    if len(unique)==2: section.append(unique)
fig,axes=plt.subplots(1,3,figsize=(13,6),gridspec_kw={'width_ratios':[1,1,1.15]})
for ax,mode,title in zip(axes[:2],('current','flipped-no-support'),('Previous: Technic face down','Proposed: servo rim down')):
    q=paths(Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-decision-20261009/plate_1.gcode') if mode=='current' else OUT/mode/'plate_1.gcode')
    segs=section if mode=='current' else [[(x,height-z) for x,z in seg] for seg in section]
    ax.add_collection(LineCollection(segs,colors='#242f3c',linewidths=1.5,label='Actual mesh section, Y=0'))
    support_segments=[[(x,p['z']) for x,y in p['points']] for p in q if p['feature'] in ('Support','Support interface')]
    if support_segments: ax.add_collection(LineCollection(support_segments,colors='#20936b',linewidths=.4,alpha=.5,label='Support paths projected into XZ'))
    ax.axhline(0,color='#828b96',linewidth=2,label='Build plate')
    ax.set(xlim=(-10,10),ylim=(-.6,17),xlabel='Hub X (mm)',ylabel='Height above bed (mm)',title=title)
    ax.set_aspect('equal');ax.grid(alpha=.15)
    if mode!='current':
        ax.annotate('Socket roof bridge',xy=(0,3.8),xytext=(-9,6),arrowprops={'arrowstyle':'->'},fontsize=9)
        ax.text(0,14.0,'Technic\nsocket up',ha='center',fontsize=9)
        ax.annotate('Servo socket down',xy=(0,.5),xytext=(-9,1.7),fontsize=9)
ax=axes[2]
q=paths(OUT/'flipped-no-support'/'plate_1.gcode')
bridges=[p['points'] for p in q if p['feature']=='Bridge' and abs(p['z']-3.8)<1e-5]
ax.add_collection(LineCollection(bridges,colors='#ba6229',linewidths=1,label='Native bridge centerlines'))
ax.add_patch(plt.Circle((0,0),2.85,fill=False,color='#242f3c',linestyle='--',label='Nominal 5.70 mm socket'))
ax.set(xlim=(-4,4),ylim=(-4,4),xlabel='Hub X (mm)',ylabel='Hub Y (mm)',title='Flipped socket roof at Z=3.80 mm')
ax.set_aspect('equal');ax.grid(alpha=.15)
fig.suptitle('Output hub: unchanged geometry, less support',fontsize=16)
legend={}
for ax in axes:
    handles,labels=ax.get_legend_handles_labels()
    legend.update(zip(labels,handles))
fig.legend(legend.values(),legend.keys(),loc='lower center',bbox_to_anchor=(.5,.06),ncol=3,fontsize=8)
fig.text(.5,.015,'Source: saved 3MF mesh and Bambu native slices, 10 Oct 2026. Centerlines are not swept beads; bridge sag and printed fit remain untested.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.17,1,.94))
fig.savefig(HERE/'orientation-comparison.png',dpi=160)
