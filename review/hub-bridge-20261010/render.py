"""Render real native G-code centerlines without repeating the slices."""
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
source=(HERE/'test_bridge.py').read_text()
scope={'__file__':str(HERE/'test_bridge.py')}
exec(source[:source.index('baseline_gcode=')],scope)
paths=scope['paths'];OUT=scope['OUT']
sys.path.insert(0,'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/slicer-challenge-20261005/python-libs')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

fig,axes=plt.subplots(1,3,figsize=(12,4.8))
for ax,mode,title in zip(axes,('thin-flow-090','thick-flow-090','counterbore-partial'),
    ('Selected normal bridge\nFlow 0.90 / strand height 0.080 mm',
     'Thick bridge trial\nFlow 0.90 / strand height 0.379 mm',
     'Partial counterbore trial\nFirst interior fill at Z=3.88 mm')):
    q=paths(OUT/mode/'plate_1.gcode')
    z=3.88 if mode=='counterbore-partial' else 3.8
    feature='Internal solid infill' if mode=='counterbore-partial' else 'Bridge'
    segments=[p['points'] for p in q if p['feature']==feature and abs(p['z']-z)<1e-6]
    assert segments
    ax.add_collection(LineCollection(segments,colors='#ba6229',linewidths=1))
    ax.add_patch(plt.Circle((0,0),2.85,fill=False,color='#242f3c',linestyle='--'))
    ax.set(xlim=(-4,4),ylim=(-4,4),xlabel='Hub X (mm)',ylabel='Hub Y (mm)',title=title)
    ax.set_aspect('equal');ax.grid(alpha=.15)
fig.suptitle('Native hub roof toolpaths: tested bridge modes',fontsize=15)
fig.text(.5,.025,'Bambu Studio 02.08.02.61 / PETG Basic, 10 Oct 2026. Path centerlines, not deposited beads. Dashed circle: nominal 5.70 mm socket.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.16,1,.90))
fig.savefig(HERE/'bridge-trials.png',dpi=160)
