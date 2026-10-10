from pathlib import Path
import ast,hashlib,json,math,shutil,sys,zipfile
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/loose-fit-20261009/python-libs')
from shapely.geometry import LineString
ROOT=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');OUT=Path(__file__).parent;HERE=ROOT/'review/incremental-fit-20261010'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=json.loads((ROOT/'design/current.model.json').read_text())
with zipfile.ZipFile(ROOT/'design/current.nbcad') as z:assert json.loads(z.read('model.json'))==model
reference=json.loads((ROOT/'review/incremental-fit.json').read_text());assert reference['canonicalModelSha256']==sha(ROOT/'design/current.model.json')
remaining={}
for tag,radius in [('baseline',4.075),('nub-28',4.175)]:
 s=json.loads((OUT/f'{tag}-shaft-opening.json').read_text());circles=[c for c in s['section'] if all(abs(math.hypot(*p)-radius)<.0011 for p in c['points'])]
 assert len(circles)==1,(tag,len(circles))
 bore=LineString(circles[0]['points']);others=[LineString(c['points']) for c in s['section'] if c not in circles and len(c['points'])>1]
 remaining[tag]=min(bore.distance(g) for g in others)
assert remaining['nub-28']>1.29,remaining
baseline=json.loads((OUT/'baseline.model.json').read_text());changes={}
allowed={'sketches':{755},'revolves':{756},'fillets':{782,783},'holes':{94}}
for key in ['sketches','extrudes','revolves','sweeps','lofts','ribs','fillets','chamfers','holes','datum_planes','body_features']:
 a={f['feature_id']:f for f in baseline[key]};b={f['feature_id']:f for f in model[key]}
 added=set(b)-set(a);removed=set(a)-set(b);changed={i for i in set(a)&set(b) if a[i]!=b[i]}
 assert not added,(key,added)
 assert all(786<=i<=801 for i in removed),(key,removed)
 assert changed<=allowed.get(key,set()),(key,changed)
 changes[key]={'removed_feature_ids':sorted(removed),'changed_feature_ids':sorted(changed)}
assert model['assembly']==baseline['assembly'] and model['views']==baseline['views']
report={'canonical_sha256':sha(ROOT/'design/current.model.json'),'native_container_sha256':sha(ROOT/'design/current.nbcad'),'native_payload_matches':True,'regression_reference_hash_matches':True,'shaft_aperture_section_radius_mm':4.175,'hub_journal_radius_mm':3.97,'radial_aperture_gap_mm':.205,'min_remaining_upper_wall_in_Z40_section_mm':remaining,'section_deflection_mm':.001,'native_binary_sha256':'f71488692f1aef0d75709638f5f5a773babadfd5462be7c7a8a9b35eb136a0cd','bambu_version':'02.08.02.61','print_sent':False}
report['native_definition_changes']=changes
(HERE/'final-check.json').write_text(json.dumps(report,indent=2)+'\n')
for name in ['registered.py','toolpaths.py','final-check.py','registered-receivers.3mf','registered-receivers-audit.json','toolpath-audit.json','render.py','hex-section.png']:
 shutil.copy2(OUT/name,HERE/name)
for tag in ['nub-28','nub-30','nub-30-relieved']:
 receipts=json.loads((OUT/f'{tag}-receipts.json').read_text())
 for r in receipts:
  if r['name']=='cad_load_project_model':r['args']={'model_json_sha256':hashlib.sha256(r['args']['model_json'].encode()).hexdigest(),'source_model_stored_externally':True}
 (HERE/f'{tag}-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
print(json.dumps(report,indent=2))
