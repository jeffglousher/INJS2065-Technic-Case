import sys, json
from pathlib import Path
root=Path(__file__).parent
sys.path.insert(0,str(root/'python-libs'))
import gmsh, numpy as np
gmsh.initialize()
gmsh.option.setNumber('General.Terminal',0)
gmsh.model.occ.importShapes(str(root/'current.step'))
gmsh.model.occ.synchronize()
surfaces=[]
for dim,tag in gmsh.model.getEntities(2):
    bb=gmsh.model.getBoundingBox(dim,tag)
    mass=gmsh.model.occ.getMass(dim,tag)
    typ=gmsh.model.getType(dim,tag)
    surfaces.append(dict(tag=tag,bbox=bb,area=mass,type=typ))
(root/'surface-inventory.json').write_text(json.dumps(surfaces,indent=2))
print(json.dumps(dict(volumes=[(t,gmsh.model.occ.getMass(d,t)) for d,t in gmsh.model.getEntities(3)],surfaces=len(surfaces),floor=[s for s in surfaces if abs(s['bbox'][1]-10.55)<1e-5 and abs(s['bbox'][4]-10.55)<1e-5]),indent=2),flush=True)
gmsh.finalize()
