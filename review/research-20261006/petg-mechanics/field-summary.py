import sys,json
from pathlib import Path
r=Path(__file__).parent;sys.path.insert(0,str(r/'python-libs'))
import numpy as np
f=np.load(r/'field-0.12-normal-floor.npz');x=f['xyz'];tet=f['tet'];u=f['u']*f['scale'];c=x[tet].mean(axis=1);e=f['principal_abs']*f['scale']
out={}
for name,m in [('relief', (abs(c[:,0]+.85)<1.8)&(c[:,2]>20.4)&(c[:,2]<23.7)),('ridge',(abs(c[:,0]+.85)<1.2)&(c[:,2]>23.7)&(c[:,2]<24.7)),('nub',(abs(c[:,0]+.85)<.5)&(c[:,2]>24.7))]:
    out[name]=dict(max_principal_strain=float(e[m].max()),p95=float(np.quantile(e[m],.95)),location=c[m][e[m].argmax()].tolist())
out['points']=[]
for p in [[-.85,9.8,25.1],[-.85,9.8,24.6],[-.85,9.8,24],[-.85,11.5,22.02]]:
    i=np.argmin(np.linalg.norm(x-np.array(p),axis=1));out['points'].append(dict(requested=p,node=x[i].tolist(),inward_displacement=float(-u[i,1])))
print(json.dumps(out,indent=2));(r/'field-summary.json').write_text(json.dumps(out,indent=2))
