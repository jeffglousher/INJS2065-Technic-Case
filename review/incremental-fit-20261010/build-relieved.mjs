import fs from 'node:fs/promises';import {spawnSync} from 'node:child_process';
const root='C:/Users/jeffg/dev/INJS2065-Technic-Case',out=new URL('./',import.meta.url);
let code=await fs.readFile(new URL('build.mjs',out),'utf8');
const historical=await fs.readFile(root+'/review/retention-fit-20261009/build.mjs','utf8');
const start=historical.indexOf(' await replace(765,766'),end=historical.indexOf(' for(const [body_id,feature_id]',start);
let edit=historical.slice(start,end).replaceAll('z+.5','z+.52').replaceAll('seatStart+.5','seatStart+.52').replaceAll('seatStart+.52/Math.sqrt(2)','seatStart+.52/Math.sqrt(2)').replaceAll('z+.52/Math.sqrt(2)','z+.52/Math.sqrt(2)');
code=code.replace(' for(const [body_id,feature_id]',edit+' for(const [body_id,feature_id]');
code=code.replace('Math.sqrt(.5**2-b**2),receiver','Math.sqrt(.52**2-b**2),receiver');
// The radius must be changed in every cap point and the documented envelope.
code=code.replace('seatStart+.5,inner_hex','seatStart+.52,inner_hex');
await fs.writeFile(new URL('build-relieved-native.mjs',out),code);
const r=spawnSync(process.execPath,[new URL('build-relieved-native.mjs',out).pathname.slice(1),'.30','.02','nub-30-relieved','D:/noBS-CAD-Reviews/INJS2065-Technic-Case/incremental-fit-20261010/base-unbeveled.model.json'],{stdio:'inherit',windowsHide:true});
if(r.status!==0)throw Error('Native build failed');
