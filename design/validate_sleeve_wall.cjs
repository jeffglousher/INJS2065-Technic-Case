/** v16.25: through-sleeve wall collapsed by Ø12.3 insert path; side bores are blind 8.2.
 *  Probe still reports midplane X hits at Z30 for documentation (expect cavity-dominated). */
function rayHits(body,axis,uval,vval){
 const dims=[0,1,2].filter(k=>k!==axis),p=body.mesh.positions,ix=body.mesh.indices,h=[];
 for(let i=0;i<ix.length;i+=3){const [a,b,c]=ix.slice(i,i+3).map(j=>p.slice(j*3,j*3+3)),[u,v]=dims;
 const d=(b[v]-c[v])*(a[u]-c[u])+(c[u]-b[u])*(a[v]-c[v]);if(Math.abs(d)<1e-10)continue;
 const q=((b[v]-c[v])*(uval-c[u])+(c[u]-b[u])*(vval-c[v]))/d;
 const r=((c[v]-a[v])*(uval-c[u])+(a[u]-c[u])*(vval-c[v]))/d;
 if(q>=-1e-8&&r>=-1e-8&&q+r<=1+1e-8)h.push(q*a[axis]+r*b[axis]+(1-q-r)*c[axis]);}
 return [...new Set(h.map(v=>+v.toFixed(5)))].sort((a,b)=>a-b);
}
function sleeveWall(scene){
 const b=scene.bodies.find(b=>b.name&&/clamshell_b|ClamshellB/i.test(b.name))||scene.bodies.find(b=>b.id===21);
 if(!b||!b.mesh) return {note:'no_clamshell_b_mesh',side_bore_mode:'blind_8.2',through_wall_applicable:false};
 const samples=[];for(let z=27.5;z<=32.5;z+=.025){const hits=rayHits(b,0,0,z).filter(x=>x>0);if(hits.length>=2)samples.push({z:+z.toFixed(3),hits:hits.slice(0,4),cavity:hits[0]});}
 return {section_y:0,sample_interval:.025,samples_count:samples.length,
  cavity_r_at_z30:(rayHits(b,0,0,30).filter(x=>x>0)[0]||null),
  side_bore_mode:'blind_8.2',through_wall_applicable:false,
  note:'Ø12.3 insert path; through-sleeve wall N/A — assembly-path tradeoff'};
}
module.exports={rayHits,sleeveWall};
