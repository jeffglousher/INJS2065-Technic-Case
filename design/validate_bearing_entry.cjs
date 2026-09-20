/** v16.25: outside (face) path blocked for bearing OD; insert path + pocket clear from split side. */
function bearingEntry(scene){
function clip(poly,k,v,sgn){const out=[];for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],da=sgn*(a[k]-v),db=sgn*(b[k]-v);if(da>=-1e-9)out.push(a);if((da>=0)!=(db>=0)){const t=da/(da-db);out.push(a.map((q,j)=>q+t*(b[j]-q)));}}return out;}
function dist(poly,x,z){let d=Infinity,pos=false,neg=false;for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],dx=b[0]-a[0],dz=b[2]-a[2],cross=dx*(z-a[2])-dz*(x-a[0]);if(cross>1e-9)pos=true;if(cross< -1e-9)neg=true;const den=dx*dx+dz*dz,t=den?Math.max(0,Math.min(1,((x-a[0])*dx+(z-a[2])*dz)/den)):0;d=Math.min(d,Math.hypot(x-a[0]-t*dx,z-a[2]-t*dz));}let area=0;for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length];area+=a[0]*b[2]-b[0]*a[2];}return Math.abs(area)>1e-9&&!(pos&&neg)?0:d;}
// Probe at bearing OD radius 6.0.
// Face band blocked; pocket clear; insert path mid (Z28–33) must also clear for upper-alone insert.
return [
  {x:0,z:0,y_span:[38.0,42.0],label:'outside_blocked',expected:'blocked'},
  {x:0,z:0,y_span:[34.4,37.9],label:'pocket_clear',expected:'clear'},
  {x:0,z:0,y_span:[28.0,33.5],label:'insert_path_clear',expected:'clear'},
].map((probe)=>{let minimum=Infinity,limitingBody=null;const [lo,hi]=probe.y_span;for(const b of scene.bodies){const p=b.mesh.positions,ix=b.mesh.indices;for(let i=0;i<ix.length;i+=3){let poly=ix.slice(i,i+3).map(j=>p.slice(j*3,j*3+3));poly=clip(clip(poly,1,lo,1),1,hi,-1);if(!poly.length)continue;const d=dist(poly,probe.x,probe.z)-6.0;if(d<minimum){minimum=d;limitingBody=b.id;}}}const pass=probe.expected==='blocked'?minimum<0:minimum>0.05;return {...probe,clearance_mm:minimum,limitingBody,pass};});
}
module.exports={bearingEntry};
// Input shell mesh coordinates permuted from [x,y,z] to [x,z,y].
