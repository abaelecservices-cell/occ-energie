const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const d=JSON.parse(read('OCC_ENERGIE.html').match(/window\.OCC_DATA=([\s\S]*?);<\/script>/)[1]);
const c=vm.createContext({window:{OCC_DATA:d},localStorage:{getItem:()=>null}});
vm.runInContext(read('src/app.js').split('/* ======================================================================= démarrage */')[0],c);
vm.runInContext(read('src/pl20-facade.js'),c);
assert.equal(d.facades.PL20.nophoto,false);
assert.ok(!d.boards.find(b=>b.id==='PL20').note.includes('Aucune photo'));
for(const live of [false,true]) {
 const svg=vm.runInContext(`facadeSVG('PL20',{live:${live}})`,c);
 const ids=[...svg.matchAll(/class="hit" data-id="(.*?)"/g)].map(m=>m[1]);
 assert.deepEqual(ids,['PL_A04','PL_A_TT','PL_A_ARR','PL_A_PF','PL_B_PF','PL_B_ARR','PL_B_TT','PL_B01']);
 assert.ok(svg.includes('EDF SECOURS')&&svg.includes('CNR NORMAL'));
 assert.ok(svg.includes('IMG_4334 à IMG_4381'));
 assert.equal((svg.match(/rx="25"/g)||[]).length,4,'Deux balises rouges par extrémité');
 assert.ok(!svg.includes('undefined')&&!svg.includes('NaN'));
}
const base=JSON.parse(read('build/data.json'));
assert.deepEqual(d.edges,base.edges);
assert.ok(read('OCC_ENERGIE.html').includes('function pl20FacadeSVG'));
console.log('PASS PL20 : façade dédiée embarquée, huit liens dans leur ordre, quatre balises, sources photo et topologie préservée.');
