"""Uncropped mating test: complete current shells and both nominal clips.

Preserves all four mesh payloads and build transforms from the reviewed full
project. Removes the hub and its overrides; no canonical geometry is edited.
Native slicing does not send a print job.
"""
from pathlib import Path
import hashlib,json,subprocess,zipfile,xml.etree.ElementTree as E

ROOT=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case')
OUT=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/contact-fix-20261009')
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
E.register_namespace('',NS)
E.register_namespace('p','http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
SOURCE=ROOT/'review/retention-fit-20261009/assembly-fit-candidate.3mf'

with zipfile.ZipFile(SOURCE) as z:data={n:z.read(n) for n in z.namelist()}
main=E.fromstring(data['3D/3dmodel.model']);cfg=E.fromstring(data['Metadata/model_settings.config'])
for parent in [main.find('{'+NS+'}resources'),main.find('{'+NS+'}build')]:
    for item in list(parent):
        if item.get('id')=='105' or item.get('objectid')=='105':parent.remove(item)
for obj in list(cfg.findall('object')):
    if obj.get('id')=='105':cfg.remove(obj)
for assemble in cfg.findall('assemble'):
    for item in list(assemble):
        if item.get('object_id')=='105':assemble.remove(item)
for plate in cfg.findall('plate'):
    for instance in list(plate.findall('model_instance')):
        if any(m.get('key')=='object_id' and m.get('value')=='105' for m in instance.findall('metadata')):plate.remove(instance)
    for meta in plate.findall('metadata'):
        if meta.get('key')=='plater_name':meta.set('value','Registered full-shell retention test')
    sequence=next((m for m in plate.findall('metadata') if m.get('key')=='print_sequence'),None)
    if sequence is None:sequence=E.SubElement(plate,'metadata',{'key':'print_sequence'})
    sequence.set('value','by object')
for meta in main.findall('{'+NS+'}metadata'):
    if meta.get('name')=='Title':meta.text='INJS2065 registered full-shell retention test - nominal 0.26 mm clips'
main.set('xmlns:BambuStudio','http://schemas.bambulab.com/package/2021')
data['3D/3dmodel.model']=E.tostring(main,encoding='utf-8',xml_declaration=True)
data['Metadata/model_settings.config']=E.tostring(cfg,encoding='utf-8',xml_declaration=True)
data.pop('3D/Objects/object_5.model',None)
# Remove the stale package relationship for the deleted inner object, if present.
REL='http://schemas.openxmlformats.org/package/2006/relationships'
for name in list(data):
    if name.endswith('.rels'):
        rel=E.fromstring(data[name])
        changed=False
        for item in list(rel):
            if item.get('Target','').endswith('object_5.model'):rel.remove(item);changed=True
        if changed:
            E.register_namespace('',REL)
            data[name]=E.tostring(rel,encoding='utf-8',xml_declaration=True)
            E.register_namespace('',NS)
for name in list(data):
    if name.endswith('.png'):del data[name]
settings=json.loads(data['Metadata/project_settings.config'])
assert settings['layer_height']=='0.16' and settings['brim_type']=='no_brim' and settings['enable_support']=='0'
assert len(main.find('{'+NS+'}build'))==4 and len(cfg.findall('object'))==4
project=OUT/'registered-receivers.3mf'
with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED) as z:
    for name,raw in data.items():z.writestr(name,raw)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
with zipfile.ZipFile(SOURCE) as z:
    for i in range(1,5):
        name=f'3D/Objects/object_{i}.model';assert data[name]==z.read(name)
        old=E.fromstring(z.read('3D/3dmodel.model'))
        olditem=next(x for x in old.find('{'+NS+'}build') if x.get('objectid')==str(100+i))
        newitem=next(x for x in main.find('{'+NS+'}build') if x.get('objectid')==str(100+i))
        assert olditem.attrib==newitem.attrib
        records.append({'object':100+i,'mesh_sha256':hashlib.sha256(data[name]).hexdigest(),'build_transform_unchanged':True})
slice_dir=OUT/'registered-receivers-slice';slice_dir.mkdir(exist_ok=True)
cmd=['C:/Program Files/Bambu Studio/bambu-studio.exe','--load-filaments',
    'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/petg-basic-update-20261007/bambu-petg-basic-resolved.json',
    '--slice','1','--outputdir',str(slice_dir),'--export-settings',str(slice_dir/'resolved-settings.json'),str(project)]
p=subprocess.run(cmd,cwd=slice_dir,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=180)
(slice_dir/'cli.log').write_bytes(p.stdout+p.stderr)
result=json.loads((slice_dir/'result.json').read_text())
assert p.returncode==0 and result['return_code']==0,result
assert not result['sliced_plates'][0]['warning_message'],result
report={'canonical_geometry_changed':False,'cropped_receivers':False,'full_shell_locators_preserved':True,
    'source_project_sha256':sha(SOURCE),'project_sha256':sha(project),'unchanged_meshes':records,
    'native_result':result,'gcode_sha256':sha(slice_dir/'plate_1.gcode'),'print_sent':False}
(OUT/'registered-receivers-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(result),flush=True)
