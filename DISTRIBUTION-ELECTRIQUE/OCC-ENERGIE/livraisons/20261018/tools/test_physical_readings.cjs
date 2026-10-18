const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const data=JSON.parse(read('OCC_ENERGIE.html').match(/window\.OCC_DATA=([\s\S]*?);<\/script>/)[1]);
const base=JSON.parse(read('build/data.json'));
const context=vm.createContext({window:{OCC_DATA:data},localStorage:{getItem:()=>null}});
vm.runInContext(read('src/app.js').split('/* ======================================================================= démarrage */')[0],context);
for(const name of ['physical-parts','physical-cabinet'])vm.runInContext(read('src/'+name+'.js'),context);
for(const [board,doors] of [['TS9',8],['TS15',6],['PEG',2]]){
 const profile=data.facades[board].physical;
 assert.ok(profile,board);
 assert.equal(profile.leaves.filter(x=>!x.fixed).length,doors,board);
 const svg=vm.runInContext(`facadeSVG('${board}',{})`,context);
 assert.ok(!/NaN|undefined|<image\b|data:image\//.test(svg),board);
 for(const match of svg.matchAll(/data-id="([^"]+)"/g))assert.ok(data.nodes.some(n=>n.id===match[1]),match[1]);
}
assert.equal(data.facades.TS15.physical.parts.filter(p=>p.kind==='breaker').length,7);
assert.equal(data.facades.TS9.physical.parts.filter(p=>p.kind==='breaker').length,4);
assert.equal(data.facades.PEG.physical.parts.filter(p=>p.kind==='drive').length,2);
const extra=data.nodes.filter(n=>n.id.startsWith('PHOTO_'));
assert.equal(extra.length,JSON.parse(read('build/photo-readings.json')).nodes.length);
for(const node of extra){
 assert.equal(node.documentaryOnly,true);
 assert.equal(node.readingConfidence,'lisible');
 assert.ok(!data.edges.some(edge=>Object.values(edge).includes(node.id)),node.id);
}
assert.deepEqual(data.edges,base.edges,'Les relevés ne doivent pas inventer de liaisons électriques');
assert.equal(data.dependencyReview.departures.length,data.nodes.filter(n=>n.t==='dep').length);
console.log(`PASS : géométrie explicite TS9/TS15/PEG, ${extra.length} mentions sourcées sans liaison déduite, index couvrant tous les départs. Contrôle structurel uniquement.`);
