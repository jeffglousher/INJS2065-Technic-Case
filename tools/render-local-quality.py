"""Plot actual XY extrusion paths at pin-arch and hex layers (Pillow required)."""
import argparse
import importlib.util
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

module_spec=importlib.util.spec_from_file_location('audit',Path(__file__).with_name('audit-local-quality.py'))
audit=importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(audit)


def points(s):
    if not s['arc']:
        return [s['a'],s['b']]
    c=s['arc_center'];a=s['a'];b=s['b']
    start=math.atan2(a[1]-c[1],a[0]-c[0]);end=math.atan2(b[1]-c[1],b[0]-c[0])
    delta=(end-start)%(2*math.pi)
    if s['clockwise']:
        delta=delta-2*math.pi if delta else -2*math.pi
    radius=math.hypot(a[0]-c[0],a[1]-c[1]);steps=max(2,min(250,math.ceil(abs(delta)*radius/.04)))
    return [[c[0]+radius*math.cos(start+delta*i/steps),c[1]+radius*math.sin(start+delta*i/steps)] for i in range(steps+1)]


def render(paths,output):
    im=Image.new('RGB',(1800,750),'#111923');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
    big=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',27)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
    d.text((30,18),'Actual toolpaths: upper shell +Y Technic rail',font=big,fill='white')
    d.text((30,58),'XY layer cuts from native Bambu G-code; commanded bead widths, not measured printed surfaces',font=font,fill='#acbccd')
    labels=['Previous: Classic / 0.16 mm','Classic with local quality','Final: Arachne with local quality']
    for column,path in enumerate(paths):
        rows=[s for s in audit.segments(path) if s['object']==2]
        d.text((30+600*column,101),labels[column],font=font,fill='white')
        for row,target in enumerate((14.2,19.5)):
            layers={s['z'] for s in rows if s['feature']=='Outer wall'}
            z=min(layers,key=lambda h:abs(h-target));selection=[s for s in rows if abs(s['z']-z)<1e-5]
            x0=30+column*600;y0=162+row*220;scale=14.2
            d.text((x0,y0-23),f'{"Pin-hole arch" if row==0 else "Hex transition"} | Z {z:.3f} mm',font=small,fill='#c8d8e8')
            panel=Image.new('RGB',(550,155),'#202c3b');p=ImageDraw.Draw(panel)
            for s in selection:
                pts=[((v[0]-50+19)*scale,(12.6-(v[1]-175))*scale+10) for v in points(s)]
                color='#e45eb4' if s['feature']=='Gap infill' else '#5ebbf5' if s['speed']<=30.01 else '#59cfaa' if s['speed']<=45.01 else '#f7b65d' if s['speed']<=80 else '#eb6b60'
                p.line(pts,fill=color,width=max(1,round(s['width']*scale)),joint='curve')
            boundary=(12.6-5.2)*scale+10
            for x in range(0,550,15):p.line((x,boundary,x+7,boundary),fill='#c1cad4',width=1)
            im.paste(panel,(x0,y0));d.rectangle((x0,y0,x0+550,y0+155),outline='#42566a')
    legends=[('#5ebbf5','<=30 mm/s'),('#59cfaa','30-45 mm/s'),('#f7b65d','45-80 mm/s'),('#eb6b60','>80 mm/s'),('#e45eb4','Gap fill')]
    for i,(color,label) in enumerate(legends):
        x=35+i*320;d.rectangle((x,645,x+23,665),fill=color);d.text((x+34,641),label,font=font,fill='white')
    d.text((30,687),'Dashed line: local speed-volume boundary at Y +5.2 mm. Each panel uses the nearest actual layer to its target.',font=small,fill='#acbccd')
    d.text((30,713),'No brims or supports. CAD geometry unchanged. Unsupported underside finish and mechanical fit still require printing.',font=small,fill='#acbccd')
    im.save(output)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('baseline',type=Path);p.add_argument('classic',type=Path);p.add_argument('final',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();render([a.baseline,a.classic,a.final],a.output)
