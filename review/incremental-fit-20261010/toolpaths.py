from pathlib import Path
import ast,hashlib,json,math,re,sys,zipfile,xml.etree.ElementTree as E
import numpy as np
ROOT=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');OUT=Path(__file__).parent
source=(ROOT/'review/hub-quality-20261008/audit.py').read_text();tree=ast.parse(source);f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='parse');exec(compile(ast.get_source_segment(source,f),'<recorded-native-parser>','exec'))
ps=parse(OUT/'nub-28-slice/plate_1.gcode');assert sorted(set(p['obj'] for p in ps))==list(range(1,6))
excluded={'Brim','Skirt','Support','Support interface'};assert not any(p['feature'] in excluded for p in ps)
assert not any(p['feature']=='Sparse infill' and p['obj'] in [3,4,5] for p in ps)
bridges=[p for p in ps if p['obj']==5 and p['feature']=='Bridge'];assert bridges
assert sorted(set(round(p['z'],5) for p in bridges))==[3.8]
assert all(abs(p['height']-.08)<1e-5 and abs(p['speed']-25)<1e-4 for p in bridges)
objects={str(i):{'extrusion_segments':sum(p['obj']==i for p in ps),'roles':sorted(set(p['feature'] for p in ps if p['obj']==i)),'wall_widths_mm':sorted(set(p['width'] for p in ps if p['obj']==i and p['feature'] in ['Inner wall','Outer wall']))} for i in range(1,6)}
report={'objects':objects,'no_supports_brims_skirts':True,'clips_and_hub_slice_solid':True,'hub_bridge_z_mm':3.8,'hub_bridge_height_mm':.08,'hub_bridge_speed_mm_s':25,'source_gcode_sha256':hashlib.sha256((OUT/'nub-28-slice/plate_1.gcode').read_bytes()).hexdigest(),'path_centerlines_not_measured_beads':True,'print_sent':False}
(OUT/'toolpath-audit.json').write_text(json.dumps(report,indent=2))
print('PASS support-free five-part native toolpaths, solid clips/hub and preserved thin bridge settings.')
