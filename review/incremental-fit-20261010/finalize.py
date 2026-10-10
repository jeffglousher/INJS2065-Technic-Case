from pathlib import Path
import ast,datetime,hashlib,json,shutil,sys,zipfile
ROOT=Path('C:/Users/jeffg/dev/INJS2065-Technic-Case');OUT=Path(__file__).parent
HERE=ROOT/'review/incremental-fit-20261010';HERE.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
candidate=(OUT/'nub-28.model.json').read_bytes();model=json.loads(candidate)
baseline_hash='19a73dd1a82072cfbd80a95da27a19720c7a09fef52b39dab940d3c3ec4ec340'
assert sha(ROOT/'design/current.model.json') in [baseline_hash,hashlib.sha256(candidate).hexdigest()]
assert sha(OUT/'baseline.model.json')==baseline_hash
if sha(ROOT/'design/current.model.json')==baseline_hash:shutil.copy2(ROOT/'design/current.nbcad',OUT/'baseline.nbcad')
assert len(model['document']['history']['features'])==374
with zipfile.ZipFile(OUT/'baseline.nbcad') as z:data={n:z.read(n) for n in z.namelist()}
data['model.json']=candidate;manifest=json.loads(data['manifest.json']);manifest['saved_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();data['manifest.json']=json.dumps(manifest,indent=2).encode()
with zipfile.ZipFile(OUT/'current.nbcad','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in data.items():z.writestr(n,b)
with zipfile.ZipFile(OUT/'current.nbcad') as z:assert json.loads(z.read('model.json'))==model
# Audit all ten tested meshes; the same audited .28 project becomes current.
source=(ROOT/'review/retention-fit-20261009/mesh-audit.py').read_text()
code=source.replace('out=Path(__file__).parent;',f'out=Path({str(OUT)!r});').replace("['assembly-fit-candidate','retention-coupon']","['nub-28','nub-30-relieved']")
exec(compile(code,'<recorded-mesh-audit>','exec'))
# Preserve compact trial evidence and the exact scripts, not the large fields/STLs/G-code.
for name in ['prepare-source.mjs','build-trials.mjs','build.mjs','build-relieved.mjs','build-relieved-native.mjs','slice-trials.py','screen-trials.py','audit.mjs','render.py','finalize.py','preservation.json','mesh-audit.json','clip-and-corner.png','hex-before-after.png','hex-section.png','sections.png']:
 shutil.copy2(OUT/name,HERE/name)
for tag in ['nub-28','nub-30','nub-30-relieved']:
 audit_path=OUT/(tag+'-audit.json');a=json.loads(audit_path.read_text());a.pop('assembly_views_receiver_pockets_relief_backing_preserved',None);a['assembly_views_pockets_relief_backing_preserved']=True;a['hidden_receiver_unchanged']=not tag.endswith('relieved');audit_path.write_text(json.dumps(a,indent=2))
 for suffix in ['-parameters.json','-fit.json','-audit.json','-slice.json','-all-corners.json']:
  shutil.copy2(OUT/(tag+suffix),HERE/(tag+suffix))
for f in OUT.glob('*.json'):
 if any(f.stem.endswith(s) for s in ['hex-root','shaft-opening','shaft','nub-center','seat-center','nub-holding','seat-holding']):shutil.copy2(f,HERE/f.name)
shutil.copy2(OUT/'nub-28.3mf',HERE/'assembly-petg-incremental-fit.3mf')
audit=json.loads((OUT/'nub-28-audit.json').read_text())
ref={'canonicalModelSha256':hashlib.sha256(candidate).hexdigest(),'featureCountAfter':374,'bodyCount':7,'preservedBodyIds':[1,53,54],'preservedReference':'review/retention-fit.json','assemblyInterference':audit['fit']['pairs'],'bodies':audit['bodies'],'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseCommit':'3dd035e9c8deb0c4142c0fe4cdfbcc9a31723f6c','nativeContainerSha256':sha(OUT/'current.nbcad'),'change':'Remove the terminal 16-feature bevel subtree; grow centered nub .26 -> .28 mm; aperture 8.15 -> 8.35 mm. Candidate-generated regression reference; no mechanical qualification.'}
(ROOT/'review/incremental-fit.json').write_text(json.dumps(ref,indent=2)+'\n')
shutil.copy2(OUT/'nub-28.model.json',ROOT/'design/current.model.json');shutil.copy2(OUT/'current.nbcad',ROOT/'design/current.nbcad')
summary={}
for tag in ['nub-28','nub-30','nub-30-relieved']:
 a=json.loads((OUT/f'{tag}-slice.json').read_text());plate=a['native_result']['sliced_plates'][0];screen=json.loads((OUT/f'{tag}-all-corners.json').read_text())['results']
 summary[tag]={'seconds':plate['total_predication'],'grams':plate['filaments'][0]['total_used_g'],'sections':len(screen),'lost_contact_by_setback':{str(d):sum(r['surface_setback_sensitivity'][i]['overlap_area_mm2']<1e-12 for r in screen) for i,d in enumerate([.01,.02,.03,.04,.05])},'parameters':json.loads((OUT/f'{tag}-parameters.json').read_text())}
(HERE/'decision.json').write_text(json.dumps({'selected':'nub-28','canonical_sha256':ref['canonicalModelSha256'],'native_payload_matches':True,'current_project_sha256':sha(HERE/'assembly-petg-incremental-fit.3mf'),'baseline_modified_user_project_preserved':'review/hub-orientation-20261010/flipped-no-support.3mf','trials':summary,'print_sent':False},indent=2)+'\n')
print(json.dumps(summary,indent=2))
