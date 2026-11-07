"""Prepare experimental Bambu projects and check mesh contacts (no printer access).

Run after build-retention.mjs with uv run --with trimesh --with manifold3d
--with rtree --with scipy --with pillow python tools/prepare-retention.py.
"""
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT/'local/retention'
OUT = ROOT/'print/retention'
OUT.mkdir(exist_ok=True)
NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
P = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
ET.register_namespace('', NS)
ET.register_namespace('p', P)
tag = lambda name: '{'+NS+'}'+name
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/f'{name}.py')
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

verify=module('verify-print')
render=module('mesh-render')
verify.audit_project()

def native_meshes(path):
    with zipfile.ZipFile(path) as z:
        r=ET.fromstring(z.read('3D/3dmodel.model'))
    return {int(o.get('name').replace('Body','')):o.find(tag('mesh'))
            for o in r.findall('.//'+tag('object'))}

def tm(mesh):
    v=[[float(p.get(k)) for k in ('x','y','z')] for p in mesh.iter(tag('vertex'))]
    f=[[int(p.get(k)) for k in ('v1','v2','v3')] for p in mesh.iter(tag('triangle'))]
    return trimesh.Trimesh(v,f,process=True)

def placed(mesh, bid):
    mesh=copy.deepcopy(mesh)
    for p in mesh.iter(tag('vertex')):
        x,y,z=(float(p.get(k)) for k in ('x','y','z'))
        if bid==8: q=(x-8,y,z-8)
        elif bid==18:q=(x-8,-y,42-z)
        elif bid==173:q=(x-6.525,z-18.25,12-y)
        elif bid==267:q=(x-6.525,18.25-z,12+y)
        else:raise ValueError(bid)
        for k,v in zip(('x','y','z'),q):p.set(k,f'{v:.9f}')
    return mesh

with zipfile.ZipFile(ROOT/'print/servo-holder.3mf') as z:
    TEMPLATE={n:z.read(n) for n in z.namelist()}

def wrap(mesh, number):
    r=ET.Element(tag('model'),{'unit':'millimeter'})
    resources=ET.SubElement(r,tag('resources'))
    o=ET.SubElement(resources,tag('object'),{'id':str(number),'type':'model'})
    o.append(copy.deepcopy(mesh))
    ET.SubElement(r,tag('build'))
    return ET.tostring(r,encoding='utf-8',xml_declaration=True)

def project(path, rows):
    """Rows: name, mesh in print coordinates, source setting object, XY center."""
    data={k:v for k,v in TEMPLATE.items() if not k.startswith('3D/Objects/')}
    config=ET.fromstring(TEMPLATE['Metadata/model_settings.config'])
    source={i:copy.deepcopy(o) for i,o in enumerate(config.findall('object'),1)}
    for o in config.findall('object'):config.remove(o)
    plate=config.find('plate')
    for o in plate.findall('model_instance'):plate.remove(o)
    assemble=config.find('assemble');assemble.clear()
    main=ET.fromstring(TEMPLATE['3D/3dmodel.model'])
    resources=main.find(tag('resources'));resources.clear()
    build=main.find(tag('build'));build.clear()
    relns='{http://schemas.openxmlformats.org/package/2006/relationships}'
    relationships=ET.Element(relns+'Relationships')
    ranges=ET.Element('objects')
    original_ranges=ET.fromstring(TEMPLATE['Metadata/layer_config_ranges.xml'])
    checks=[]
    for i,(name,mesh,settings,(x,y)) in enumerate(rows,1):
        raw=wrap(mesh,i);data[f'3D/Objects/object_{i}.model']=raw
        checks.append(verify.audit_mesh(raw,name))
        oid=str(100+i);transform=f'1 0 0 0 1 0 0 0 1 {x} {y} 0'
        o=copy.deepcopy(source[settings]);o.set('id',oid)
        for md in o.findall('metadata'):
            if md.get('key')=='name':md.set('value',name)
            if md.get('face_count') is not None:md.set('face_count',str(checks[-1]['triangles']))
        part=o.find('part');part.set('id',str(i))
        part.find("metadata[@key='name']").set('value',name)
        part.find('mesh_stat').set('face_count',str(checks[-1]['triangles']))
        config.append(o)
        inst=ET.SubElement(plate,'model_instance')
        for key,value in [('object_id',oid),('instance_id','0'),('identify_id',str(i))]:ET.SubElement(inst,'metadata',{'key':key,'value':value})
        ET.SubElement(assemble,'assemble_item',{'object_id':oid,'instance_id':'0','transform':transform,'offset':'0 0 0'})
        obj=ET.SubElement(resources,tag('object'),{'id':oid,'type':'model'})
        components=ET.SubElement(obj,tag('components'))
        ET.SubElement(components,tag('component'),{'{'+P+'}path':f'/3D/Objects/object_{i}.model','objectid':str(i),'transform':'1 0 0 0 1 0 0 0 1 0 0 0'})
        ET.SubElement(build,tag('item'),{'objectid':oid,'transform':transform,'printable':'1'})
        ET.SubElement(relationships,relns+'Relationship',{'Target':f'/3D/Objects/object_{i}.model','Id':f'rel-{i}','Type':'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'})
        if settings in (1,2):
            r=copy.deepcopy(original_ranges.find(f"object[@id='{settings}']"));r.set('id',str(i));ranges.append(r)
    for file,tree in [('Metadata/model_settings.config',config),('3D/3dmodel.model',main),('3D/_rels/3dmodel.model.rels',relationships),('Metadata/layer_config_ranges.xml',ranges)]:
        # Bambu's relationship reader requires an unprefixed Relationships root.
        if file.endswith('.rels'):ET.register_namespace('',relns[1:-1])
        data[file]=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
        ET.register_namespace('',NS)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for name,raw in data.items():z.writestr(name,raw)
    return checks

full={label:native_meshes(LOCAL/f'{label}-full.3mf') for label in ('control','A','B')}
coupon={label:native_meshes(LOCAL/f'{label}-coupon.3mf') for label in ('control','A','B')}
# Native tessellation differs from the prepared print. Record geometric differences
# instead of silently treating new triangulation hashes as equivalent.
replay=[]
for i,bid in ((1,8),(2,18),(3,173)):
    old=ET.fromstring(TEMPLATE[f'3D/Objects/object_{i}.model']).find('.//'+tag('mesh'))
    a,b=tm(placed(full['control'][bid],bid)),tm(old)
    difference=trimesh.boolean.difference([a,b],engine='manifold').volume+trimesh.boolean.difference([b,a],engine='manifold').volume
    # Fine tessellation across the large shell's many curved faces accumulates
    # volume difference. Check surface distance as well, including every vertex.
    verify.check(difference<2,f'Replay volume difference for {bid}: {difference} mm3')
    np.random.seed(917)
    distances=[]
    for subject,target in ((a,b),(b,a)):
        points=np.vstack([subject.vertices,trimesh.sample.sample_surface(subject,4000)[0]])
        _,distance,_=trimesh.proximity.closest_point(target,points)
        distances.append(float(distance.max()))
    verify.check(max(distances)<.005,f'Replay surface differs for {bid}: {distances}')
    replay.append({'body_id':bid,'symmetric_difference_mm3':difference,'reference_volume_mm3':b.volume,
                   'bidirectional_sampled_surface_max_mm':distances,'sampling':'Every mesh vertex plus 4000 surface samples each direction; not a certified Hausdorff bound.'})

contacts=[]
for label in ('control','A','B'):
    for clip_id in (173,267):
        clip=tm(full[label][clip_id])
        for bid in (8,18):
            overlap=trimesh.boolean.intersection([clip,tm(full[label][bid])],engine='manifold').volume
            verify.check(overlap<0.01,f'{label}: seated interference with {bid}: {overlap}')
            contacts.append({'variant':label,'clip':clip_id,'shell':bid,'seated_overlap_mm3':overlap})

# Geometric engagement/release probe on the actual hook end, not a strain model.
hook_region=trimesh.creation.box(bounds=[[5,7.94,18.99],[6.5,10.8,20.66]])
hook=trimesh.boolean.intersection([tm(full['A'][173]),hook_region],engine='manifold')
shell=tm(full['A'][18])
captured=hook.copy();captured.apply_translation([0,.25,0])
blocked=trimesh.boolean.intersection([captured,shell],engine='manifold').volume
verify.check(blocked>.02,'Hook does not catch during withdrawal')
release=[]
for travel in (0,.25,.5,1,2,3,4,5):
    moved=hook.copy();moved.apply_translation([0,travel,-.5])
    overlap=trimesh.boolean.intersection([moved,shell],engine='manifold').volume
    verify.check(overlap<.01,f'Hook release travel blocked at {travel}: {overlap}')
    release.append({'withdrawal_mm':travel,'overlap_mm3':overlap})

rows=[('1 Lower registered rail',placed(coupon['control'][8],8),1,(150,55)),
      ('2 Control upper rail',placed(coupon['control'][18],18),2,(50,175)),
      ('3 Latch upper rail A and B',placed(coupon['A'][18],18),2,(50,55)),
      ('4 Control clip',ET.fromstring(TEMPLATE['3D/Objects/object_3.model']).find('.//'+tag('mesh')),3,(50,55)),
      ('5 Latch A 1.2 mm tongue',placed(full['A'][173],173),3,(50,175)),
      ('6 Latch B 1.0 mm tongue',placed(full['B'][173],173),3,(150,55))]
receiver_checks=project(OUT/'coupons-receivers.3mf',rows[:3])
clip_checks=project(OUT/'coupons-clips.3mf',rows[3:])
candidate=[]
for i,bid in enumerate((8,18,173,267,54),1):
    original=ET.fromstring(TEMPLATE[f'3D/Objects/object_{i}.model']).find('.//'+tag('mesh'))
    mesh=placed(full['A'][bid],bid) if bid in (18,173,267) else original
    if bid==54:
        # The original hub's build transform flips it; bake that rigid transform.
        mesh=copy.deepcopy(mesh)
        for p in mesh.iter(tag('vertex')):
            p.set('y',str(-float(p.get('y'))));p.set('z',str(15.700000763-float(p.get('z'))))
    candidate.append((['Lower clamshell','Experimental upper','Latch A +Y','Latch A -Y','Output hub'][i-1],mesh,i,[(50,55),(50,175),(150,55),(150,175),(220,115)][i-1]))
fullchecks=project(OUT/'holder-latch-A.3mf',candidate)

model_path=ROOT/'design/retention/latch.model.json'
with zipfile.ZipFile(ROOT/'design/current.limo') as z:manifest=json.loads(z.read('manifest.json'))
manifest['model_schema_version']=json.loads(model_path.read_text())['schema_version']
manifest['saved_at']=datetime.now(timezone.utc).isoformat()
with zipfile.ZipFile(ROOT/'design/retention/latch.limo','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('manifest.json',json.dumps(manifest,indent=2));z.writestr('model.json',model_path.read_bytes())

def rendering(mesh):
    m=tm(mesh)
    return m.vertices.tolist(),m.faces.tolist()

images=ROOT/'docs/images'
parts=[(rendering(full['A'][bid]),render.TEAL if bid in (8,18) else render.RED) for bid in (8,18,173,267)]
render.render(parts,'Experimental latch A: shells and clips',(1,1,.7),(1000,740)).save(images/'retention-assembly.png')
parts=[(rendering(full['A'][173]),render.RED)]
render.pair(render.render(parts,'Latch A: inner hook',(1,-1,.5),(720,540)),
            render.render(parts,'Latch A: outer release slots',(-1,1,.5),(720,540)),images/'retention-clip.png')
plates=[]
for title,subset,color in [('Receiver plate',rows[:3],render.TEAL),('Clip plate: control, A, B',rows[3:],render.RED)]:
    parts=[]
    for _,mesh,_,(x,y) in subset:
        m=tm(mesh);m.apply_translation([x,y,0]);parts.append(((m.vertices.tolist(),m.faces.tolist()),color))
    plates.append(render.render(parts,title,(1,-1,2),(720,720)))
render.pair(*plates,images/'retention-coupons.png')

evidence={'status':'experimental; unprinted; fit screening only','source_model_sha256':sha(ROOT/'design/current.model.json'),
 'candidate_model_sha256':sha(model_path),'candidate_archive_sha256':sha(ROOT/'design/retention/latch.limo'),
 'replay_comparison':replay,'seated_contacts':contacts,
 'hook_withdrawal_0_25_mm_overlap_mm3':blocked,'hook_release_probe':release,
 'release_probe_note':'Rigid translation of isolated hook end by -0.5 Z; does not predict beam deflection, force, strain, fatigue or lifetime.',
 'coupon_crop':{'y_min_mm':7.6,'original_xyz_preserved':True,'stiffness_equivalence_established':False},
 'projects':{'receivers':{'path':'print/retention/coupons-receivers.3mf','sha256':sha(OUT/'coupons-receivers.3mf'),'parts':receiver_checks},
             'clips':{'path':'print/retention/coupons-clips.3mf','sha256':sha(OUT/'coupons-clips.3mf'),'parts':clip_checks},
             'holder':{'path':'print/retention/holder-latch-A.3mf','sha256':sha(OUT/'holder-latch-A.3mf'),'parts':fullchecks}},'print_sent':False}
(ROOT/'docs/retention-validation.json').write_text(json.dumps(evidence,indent=2)+'\n')
print('PASS: replay comparison, seated clearance, hook capture/release and eleven prepared meshes. Native slicing remains required.')
