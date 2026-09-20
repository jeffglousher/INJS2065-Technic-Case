function rayHits(body,axis,uval,vval){
 const dims=[0,1,2].filter(k=>k!==axis),p=body.mesh.positions,ix=body.mesh.indices,h=[];
 for(let i=0;i<ix.length;i+=3){const [a,b,c]=ix.slice(i,i+3).map(j=>p.slice(j*3,j*3+3)),[u,v]=dims;
 const d=(b[v]-c[v])*(a[u]-c[u])+(c[u]-b[u])*(a[v]-c[v]);if(Math.abs(d)<1e-10)continue;
 const q=((b[v]-c[v])*(uval-c[u])+(c[u]-b[u])*(vval-c[v]))/d;
 const r=((c[v]-a[v])*(uval-c[u])+(a[u]-c[u])*(vval-c[v]))/d;
 if(q>=-1e-8&&r>=-1e-8&&q+r<=1+1e-8)h.push(q*a[axis]+r*b[axis]+(1-q-r)*c[axis]);}
 return [...new Set(h.map(v=>+v.toFixed(5)))].sort((a,b)=>a-b);
}
function sleeveWall(scene){const b=scene.bodies.find(b=>b.id===21),samples=[];for(let z=27.5;z<=32.5;z+=.025){const hits=rayHits(b,0,0,z).filter(x=>x>0);if(hits.length>=4)samples.push({z:+z.toFixed(3),wall:hits[1]-hits[0],cavity:hits[0],bore:hits[1]});}
 return {section_y:0,sample_interval:.025,samples_count:samples.length,minimum:samples.reduce((a,b)=>!a||b.wall<a.wall?b:a,null),at_z30:rayHits(b,0,0,30)};}
module.exports={rayHits,sleeveWall};
