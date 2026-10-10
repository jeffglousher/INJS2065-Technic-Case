import fs from 'node:fs/promises';import {spawnSync} from 'node:child_process';
const root='C:/Users/jeffg/dev/INJS2065-Technic-Case',out=new URL('./',import.meta.url);
// Reuse the previously validated native sketch edit/revolve and fillet-rebind
// operations. Keep the existing receiver unchanged to gain retaining margin.
let code=await fs.readFile(root+'/review/retention-fit-20261009/build.mjs','utf8');
code=code.replace("const out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/retention-fit-20261009';","const out='D:/noBS-CAD-Reviews/INJS2065-Technic-Case/incremental-fit-20261010';");
code=code.replace('const seatStart=9.8+Math.sqrt(R**2-(b+R-crest)**2)-holding-Math.sqrt(.5**2-b**2);','const seatStart=9.809663461670024;');
const start=code.indexOf(' await replace(765,766'),end=code.indexOf(' for(const [body_id,feature_id]',start);
if(start<0||end<start)throw Error('Unexpected source script');
code=code.slice(0,start)+code.slice(end);
code=code.replaceAll('features.length,390','features.length,374').replace('features:390','features:374');
code=code.replace('holding_clearance_movement_mm:holding','holding_clearance_movement_mm:9.8+Math.sqrt(R**2-(b+R-crest)**2)-seatStart-Math.sqrt(.5**2-b**2)');
await fs.writeFile(new URL('build.mjs',out),code);
for(const p of ['.28','.30']){
 const r=spawnSync(process.execPath,[new URL('build.mjs',out).pathname.slice(1),p,'.02','nub-'+p.slice(1),'D:/noBS-CAD-Reviews/INJS2065-Technic-Case/incremental-fit-20261010/base-unbeveled.model.json'],{stdio:'inherit',windowsHide:true});
 if(r.status!==0)throw Error('Native build failed');
}
