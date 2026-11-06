"""Audit and render the groove-review assembly without changing its geometry."""
from pathlib import Path
import collections
import hashlib
import importlib.util
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'review/readiness-20261106'
OUT.mkdir(exist_ok=True)

def module(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / 'tools' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

verify = module('verify-print')
audit = module('audit-local-quality')
render = module('render-review')
candidate = ROOT / 'review/grooves-20261105/assembly-uniform-shells.3mf'
names = ['Lower clamshell', 'Upper clamshell', 'Clip +Y', 'Clip -Y', 'Output hub']
checks = []
with zipfile.ZipFile(ROOT / 'print/assembly-petg.3mf') as old, zipfile.ZipFile(candidate) as new:
    cfg = ET.fromstring(new.read('Metadata/model_settings.config'))
    old_cfg = ET.fromstring(old.read('Metadata/model_settings.config'))
    model = ET.fromstring(new.read('3D/3dmodel.model'))
    settings = json.loads(new.read('Metadata/project_settings.config'))
    assert len(cfg.findall('object')) == len(model.find(verify.NS + 'build')) == 5
    assert not cfg.findall(".//part[@subtype='modifier_part']")
    assert len(model.find(verify.NS + 'resources')) == 5
    for a, b in zip(old_cfg.findall('object')[2:], cfg.findall('object')[2:]):
        assert ET.tostring(a) == ET.tostring(b), 'Clip/hub object settings changed'
    speeds = {'outer_wall_speed':'30','inner_wall_speed':'45','gap_infill_speed':'30',
              'internal_solid_infill_speed':'45','top_surface_speed':'30','small_perimeter_speed':'25'}
    for obj in cfg.findall('object')[:2]:
        assert all(verify.metadata(obj).get(k) == ','.join([v]*6) for k,v in speeds.items())
    assert ET.tostring(model.find(verify.NS + 'build')) == ET.tostring(ET.fromstring(old.read('3D/3dmodel.model')).find(verify.NS + 'build'))
    assert old.read('Metadata/layer_config_ranges.xml') == new.read('Metadata/layer_config_ranges.xml')
    assert old.read('Metadata/project_settings.config') == new.read('Metadata/project_settings.config')
    for i, name in enumerate(names, 1):
        raw = new.read(f'3D/Objects/object_{i}.model')
        assert old.read(f'3D/Objects/object_{i}.model') == raw
        check = verify.audit_mesh(raw, name)
        obj = cfg.findall('object')[i-1]
        assert verify.metadata(obj)['name'] == name
        assert not check['support_paint_counts']
        check['mesh_unchanged'] = True
        checks.append(check)
        vertices, faces = render.project_mesh(i)
        color = render.TEAL if i <= 2 else render.RED if i <= 4 else render.GREY
        render.render([((vertices, faces), color)], name, (1,-1,1.25), (560,400)).save(OUT / f'part-{i}.png')
        if i == 5:
            render.render([((vertices, faces), color)], 'Hub opposite end', (1,-1,-1.25), (560,400)).save(OUT / 'hub-opposite.png')
        print('PASS', name, flush=True)
    assert settings['printer_settings_id'] == 'Bambu Lab X2D 0.4 nozzle'
    assert settings['filament_type'] == ['PETG']
    assert settings['wall_generator'] == 'arachne'

slice_dir = OUT / 'native-slice'
slice_dir.mkdir(exist_ok=True)
with (OUT / 'slice.log').open('w') as log:
    subprocess.run(['C:/Program Files/Bambu Studio/bambu-studio.exe', '--slice', '1',
                    '--load-filaments', str(ROOT / 'print/bambu-petg-basic.json'),
                    '--outputdir', str(slice_dir), str(candidate)], stdout=log,
                   stderr=subprocess.STDOUT, check=True, timeout=180)
native = json.loads((slice_dir / 'result.json').read_text())
assert native['return_code'] == 0
plate = native['sliced_plates'][0]
assert len(plate['objects']) == 5 and not plate['warning_message']
stats, current = audit.audit(slice_dir / 'plate_1.gcode')
assert stats['supports_brims_skirts_absent']
assert {s['object'] for s in current} == {1,2,3,4,5}
assert not any(s['object'] in (3,4) and s['feature']=='Sparse infill' for s in current)
original = list(audit.segments(ROOT / 'review/grooves-20261105/original/plate_1.gcode'))
def signature(s):
    return (s['feature'],tuple(s['a']),tuple(s['b']),s['z'],s['width'],s['e'],s['arc'],tuple(s['arc_center'] or []))
for i in (3,4,5):
    assert collections.Counter(signature(s) for s in original if s['object']==i) == collections.Counter(signature(s) for s in current if s['object']==i)

# At each actual shell layer, check whether the old modifier boundary is crossed
# by an end-wall extrusion. Compare only layers where the corrected wall exists.
crossings = []
for obj, cy in ((1,55), (2,175)):
    for x in (30.21,69.79):
        for y in (cy-5.2,cy+5.2):
            def layers(rows):
                return {round(s['z'],5) for s in rows if s['object']==obj and s['feature']=='Outer wall'
                        and abs(s['a'][0]-x)<.002 and abs(s['b'][0]-x)<.002
                        and min(s['a'][1],s['b'][1])<y-.1 and max(s['a'][1],s['b'][1])>y+.1}
            before, after = layers(original), layers(current)
            assert after and not before-after, (obj,x,y)
            crossings.append({'object':obj,'x_mm':x,'y_mm':y,'continuous_layers_before':len(before),
                              'continuous_layers_after':len(after),'restored_layers':len(after-before)})

# Magnify one end-wall boundary using actual extruded paths and bead widths.
image = Image.new('RGB',(1120,430),'#f5f7fa')
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
for col,(label,rows) in enumerate((('Original: split end wall',original),('Revised: continuous end wall',current))):
    z = min({s['z'] for s in rows if s['object']==2}, key=lambda v:abs(v-2.0))
    draw.text((col*560+20,12),f'{label} | Z={z:.2f} mm',font=font,fill='#233141')
    # X 29.7..33.7, Y 168.0..171.8; pixel size 80 px/mm.
    panel = Image.new('RGB',(400,304),'#f5f7fa')
    pd = ImageDraw.Draw(panel)
    for s in rows:
        if s['object']!=2 or abs(s['z']-z)>.00001 or s['feature']=='Custom': continue
        if s['arc']: continue  # The magnified straight end wall contains no arcs.
        if min(s['a'][0],s['b'][0])>33.7 or max(s['a'][0],s['b'][0])<29.7: continue
        pts=[(40+(p[0]-29.7)*80,304-(p[1]-168)*80) for p in (s['a'],s['b'])]
        pd.line(pts,fill='#247783' if s['feature']=='Outer wall' else '#9bb9bd',width=max(1,round(s['width']*80)))
    image.paste(panel,(col*560+30,61))
    yy=365-(169.8-168)*80
    draw.line((col*560+30,yy,col*560+450,yy),fill='#ad5760',width=1)
    draw.text((col*560+20,390),'Red line: former modifier boundary, Y=169.8 mm',font=font,fill='#233141')
image.save(OUT / 'end-wall-paths.png')
result={'date':'2026-11-06','decision':'Proceed with a confirmation PETG print; mechanical acceptance remains pending',
        'candidate':str(candidate),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),
        'parts':checks,'modifiers_absent':True,'print_placements_and_layer_bands_unchanged':True,
        'native_slice':native,'toolpaths':stats,'end_wall_crossings':crossings,
        'clip_hub_extrusion_geometry_unchanged':True,'user_report':'Printed fit is reasonable; large end grooves reported',
        'remaining':['Confirm end finish in a repeat print','Inspect unsupported hex undersides',
                     'Check both clips seat, retain and resist permanent set','Check hub torque retention and bearing rotation',
                     'Repeat insertion cycles and a loaded holding dwell'],'print_sent':False}
(OUT / 'readiness.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PASS fresh native slice and restored end-wall continuity:',sum(c['restored_layers'] for c in crossings),'layer/boundary crossings',flush=True)
