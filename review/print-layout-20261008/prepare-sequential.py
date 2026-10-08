from pathlib import Path
import zipfile,json,hashlib,xml.etree.ElementTree as E,math
root=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');out=Path('D:/noBS-CAD-Reviews/INJS2065-Technic-Case/print-layout-20261008');src=root/'review/hub-quality-20261008/assembly-petg-hub-quality.3mf'
with zipfile.ZipFile(src) as z:entries={n:z.read(n) for n in z.namelist()}
settings=json.loads(entries['Metadata/project_settings.config']);settings['print_sequence']='by object';entries['Metadata/project_settings.config']=json.dumps(settings,indent=2).encode()
config=E.fromstring(entries['Metadata/model_settings.config']);hub=next(o for o in config.findall('object') if o.attrib['id']=='105')
for k,v in [('brim_type','no_brim'),('brim_width','0')]:
 m=next(m for m in hub.findall('metadata') if m.attrib.get('key')==k);m.set('value',v)
positions={'101':(50,55),'102':(50,175),'103':(150,55),'104':(150,175),'105':(220,115)}
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};model=E.fromstring(entries['3D/3dmodel.model'])
# Preserve namespace spelling rather than rewrite production namespace aliases.
raw=entries['3D/3dmodel.model'].decode()
for item in model.findall('m:build/m:item',ns):
 old=item.attrib['transform'];cx,cy=positions[item.attrib['objectid']];new=f'1 0 0 0 1 0 0 0 1 {cx} {cy} 0';raw=raw.replace('transform="'+old+'" printable="1"','transform="'+new+'" printable="1"',1)
entries['3D/3dmodel.model']=raw.encode()
for a in config.findall('assemble/assemble_item'):
 cx,cy=positions[a.attrib['object_id']];a.set('transform',f'1 0 0 0 1 0 0 0 1 {cx} {cy} 0')
entries['Metadata/model_settings.config']=E.tostring(config,encoding='utf-8',xml_declaration=True)
# Baseline sequential project keeps clip settings; separate candidate tests finer clip layers/speeds.
for name,finer in [('assembly-petg-sequential-no-brim',False),('assembly-petg-sequential-clip-quality',True)]:
 data=entries.copy()
 if finer:
  cfg=E.fromstring(entries['Metadata/model_settings.config'])
  for o in cfg.findall('object'):
   if o.attrib['id'] not in ('103','104'):continue
   for key,val in {'layer_height':'0.08','outer_wall_speed':'25','inner_wall_speed':'40','top_surface_speed':'25','gap_infill_speed':'30','internal_solid_infill_speed':'60','top_shell_thickness':'3','bottom_shell_thickness':'3'}.items():E.SubElement(o,'metadata',{'key':key,'value':val})
  data['Metadata/model_settings.config']=E.tostring(cfg,encoding='utf-8',xml_declaration=True)
 target=out/(name+'.3mf')
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for n,b in data.items():z.writestr(n,b)
 manifest=json.loads((root/'review/hub-quality-20261008/assembly-project.json').read_text())
 oldpositions={'101':(80,100),'102':(140,100),'103':(80,150),'104':(130,150),'105':(190,100)}
 for i,p in enumerate(manifest['parts'],101):
  for k in [0,1]:p['plate_bounds_mm'][k]=[v+positions[str(i)][k]-oldpositions[str(i)][k] for v in p['plate_bounds_mm'][k]]
 manifest['project_sha256']=hashlib.sha256(target.read_bytes()).hexdigest();manifest['saved_settings']['print_sequence']='by object';manifest['project_settings_identical_to_reviewed_clip']=False;manifest['clip_quality_candidate']=finer;manifest['hub_brim_enabled']=False
 (out/(name+'-project.json')).write_text(json.dumps(manifest,indent=2))
 print(name,manifest['project_sha256'])
assert all(src.read_bytes()!=b'' for _ in [0])
