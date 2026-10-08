import zipfile,json,hashlib,xml.etree.ElementTree as E
from pathlib import Path
root=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');source=root/'review/hub-friction-20261007/assembly-petg-friction-hub.3mf';out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/hub-quality-20261008')
out.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(source) as z:entries={n:z.read(n) for n in z.namelist()}
old=E.fromstring(entries['Metadata/model_settings.config']);new=E.fromstring(entries['Metadata/model_settings.config']);hub=next(o for o in new.findall('object') if next((m.attrib['value'] for m in o.findall('metadata') if m.attrib.get('key')=='name'),'')=='Output hub')
overrides={'wall_loops':'6','sparse_infill_density':'100','sparse_infill_pattern':'zig-zag','skeleton_infill_density':'100','skin_infill_density':'100','layer_height':'0.08','top_shell_layers':'12','bottom_shell_layers':'12','top_shell_thickness':'16','bottom_shell_thickness':'16','outer_wall_speed':'30','inner_wall_speed':'60','top_surface_speed':'30','internal_solid_infill_speed':'90','sparse_infill_speed':'90'}
for key,value in overrides.items():
 m=next((m for m in hub.findall('metadata') if m.attrib.get('key')==key),None)
 if m is None:m=E.SubElement(hub,'metadata',{'key':key})
 m.set('value',value)
assert len(new.findall('object'))==5
for before,after in zip(old.findall('object'),new.findall('object')):
 if after is hub:continue
 assert E.tostring(before)==E.tostring(after)
for child in list(hub):
 if child.tag=='metadata' and child.attrib.get('key') in overrides:
  hub.remove(child);hub.insert(0,child)
entries['Metadata/model_settings.config']=E.tostring(new,encoding='utf-8',xml_declaration=True)
target=out/'assembly-petg-hub-quality.3mf'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for n,data in entries.items():z.writestr(n,data)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(source) as a,zipfile.ZipFile(target) as b:
 assert a.namelist()==b.namelist()
 changed=[n for n in a.namelist() if a.read(n)!=b.read(n)];assert changed==['Metadata/model_settings.config'],changed
proof={'source_project_sha256':sha(source),'project_sha256':sha(target),'only_changed_zip_entry':changed,'only_changed_object_id':hub.attrib['id'],'only_changed_object_name':'Output hub','object_overrides':overrides,'global_settings_byte_identical':True,'all_geometry_entries_byte_identical':True,'other_four_object_configs_identical':True,'unchanged_support_and_orientation':True,'print_sent':False}
(out/'project-change.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(proof,indent=2))
manifest=json.loads((source.parent/'assembly-project.json').read_text())
manifest['project_sha256']=sha(target)
manifest['source_geometry_project']=str(source)
(out/'assembly-project.json').write_text(json.dumps(manifest,indent=2))
