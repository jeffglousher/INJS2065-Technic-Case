"""Render current native CAD meshes with an orthographic depth buffer (requires Pillow).

Usage: python tools/render-review.py --scene scene.json
The scene comes from solid_scene after loading design/current.model.json.
Print-project meshes supply the finer clip and housing detail. No geometry is edited.
"""
import argparse
from array import array
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BG = (245, 247, 250)
TEAL = (63, 154, 162)
RED = (194, 66, 89)
GREY = (144, 158, 171)
HARDWARE = (84, 98, 117)
NS = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def unit(a):
    length = math.sqrt(dot(a, a))
    return tuple(x/length for x in a)


def scene_mesh(body, offset=(0, 0, 0)):
    m = body['mesh']
    vertices = [tuple(m['positions'][i+j]+offset[j] for j in range(3)) for i in range(0, len(m['positions']), 3)]
    faces = [tuple(m['indices'][i:i+3]) for i in range(0, len(m['indices']), 3)]
    return vertices, faces


def project_mesh(number):
    with zipfile.ZipFile(ROOT/'print/assembly-petg.3mf') as z:
        r = ET.fromstring(z.read(f'3D/Objects/object_{number}.model'))
    vertices = [tuple(float(v.get(a)) for a in ('x', 'y', 'z')) for v in r.iter(NS+'vertex')]
    faces = [tuple(int(t.get(a)) for a in ('v1', 'v2', 'v3')) for t in r.iter(NS+'triangle')]
    return vertices, faces


def render(parts, title, direction, size=(820, 620)):
    w, h = size
    image = Image.new('RGB', size, BG)
    pixels = image.load()
    depth = array('f', [-math.inf]) * (w*h)
    view = unit(direction)
    right = unit(cross((0, 0, 1), view))
    up = cross(view, right)
    projected = []
    for (vertices, faces), color in parts:
        points = [(dot(p, right), dot(p, up), dot(p, view)) for p in vertices]
        projected.append((vertices, faces, color, points))
    all_points = [p for *_, points in projected for p in points]
    xmin, xmax = min(p[0] for p in all_points), max(p[0] for p in all_points)
    ymin, ymax = min(p[1] for p in all_points), max(p[1] for p in all_points)
    scale = min((w-80)/(xmax-xmin), (h-130)/(ymax-ymin))
    cx, cy = (xmin+xmax)/2, (ymin+ymax)/2
    light = unit((.4, -.6, 1))
    for vertices, faces, color, points in projected:
        screen = [(w/2+(x-cx)*scale, (h+45)/2-(y-cy)*scale, z) for x, y, z in points]
        for face in faces:
            a, b, c = (screen[i] for i in face)
            normal = cross(tuple(vertices[face[1]][i]-vertices[face[0]][i] for i in range(3)),
                           tuple(vertices[face[2]][i]-vertices[face[0]][i] for i in range(3)))
            length = math.sqrt(dot(normal, normal))
            if length < 1e-15:
                continue
            normal = tuple(x/length for x in normal)
            shade = .54 + .46*max(0, dot(normal, light))
            fill = tuple(int(v*shade) for v in color)
            denom = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(denom) < 1e-12:
                continue
            for y in range(max(55, int(min(a[1], b[1], c[1]))), min(h-25, math.ceil(max(a[1], b[1], c[1])))+1):
                for x in range(max(20, int(min(a[0], b[0], c[0]))), min(w-20, math.ceil(max(a[0], b[0], c[0])))+1):
                    u = ((b[1]-c[1])*(x+.5-c[0])+(c[0]-b[0])*(y+.5-c[1]))/denom
                    v = ((c[1]-a[1])*(x+.5-c[0])+(a[0]-c[0])*(y+.5-c[1]))/denom
                    if u >= -1e-8 and v >= -1e-8 and u+v <= 1+1e-8:
                        z = u*a[2]+v*b[2]+(1-u-v)*c[2]
                        index = y*w+x
                        if z > depth[index]:
                            depth[index] = z
                            pixels[x, y] = fill
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 23)
    draw = ImageDraw.Draw(image)
    draw.text((w/2, 12), title, fill=(35, 49, 65), font=font, anchor='mt')
    return image


def pair(left, right, output):
    result = Image.new('RGB', (left.width+right.width, left.height), BG)
    result.paste(left, (0, 0))
    result.paste(right, (left.width, 0))
    result.save(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', type=Path, required=True)
    args = parser.parse_args()
    scene = json.loads(args.scene.read_text())
    check = {b['id']: b for b in scene['bodies']}
    target = ROOT/'review/current'
    model = json.loads((ROOT/'design/current.model.json').read_text())
    colors = {1:HARDWARE, 8:TEAL, 18:TEAL, 53:HARDWARE, 54:GREY, 173:RED, 267:RED}
    assembled = [(scene_mesh(check[i]), color) for i, color in colors.items()]
    view = next(v for v in model['views'] if v['name'] == 'Exploded assembly')
    structure = model['assembly']['component_structure']
    definitions = {d['id']:d for d in structure['definitions']}
    occurrences = {o['id']:o for o in structure['occurrences']}
    offsets = {}
    for offset in view['occurrence_offsets']:
        if offset['rotation'] != [0,0,0,1]:
            raise ValueError('The assembly renderer requires translation-only display offsets')
        definition = definitions[occurrences[offset['occurrence_id']]['component_id']]
        for body_id in definition['body_ids']:
            offsets[body_id] = offset['translation']
    # Lift these reference-view parts clear of the upper shell so all seven parts are visible.
    offsets[53] = (0,0,44)
    offsets[54] = (0,0,60)
    exploded = [(scene_mesh(check[i], offsets[i]), color) for i, color in colors.items()]
    pair(render(assembled, 'Assembled servo holder', (1,-1,.8)),
         render(exploded, 'Exploded assembly - hardware included', (1,-1,.8)), target/'assembly.png')
    clip = project_mesh(3)
    pair(render([(clip, RED)], 'Clip pocket side - full walls and four nubs', (1,-1,1.8)),
         render([(clip, RED)], 'Clip rear / bed face - flat backing', (-1,1,-1.8)), target/'clip-front-back.png')
    pair(render([(project_mesh(1),TEAL)], 'Lower shell cavity and full hex posts', (1,-1,1.2)),
         render([(project_mesh(2),TEAL)], 'Upper shell cavity and full hex posts', (1,-1,1.2)), target/'clamshell-inside.png')
    print('Rendered current source meshes: assembly, clip front/rear, shell cavities. No solid edits.')


if __name__ == '__main__':
    main()
