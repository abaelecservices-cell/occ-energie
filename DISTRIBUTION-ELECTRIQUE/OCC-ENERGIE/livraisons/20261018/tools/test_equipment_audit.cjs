const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const data=JSON.parse(read('OCC_ENERGIE.html').match(/window\.OCC_DATA=([\s\S]*?);<\/script>/)[1]);
const base=JSON.parse(read('build/data.json'));
const context=vm.createContext({window:{OCC_DATA:data},localStorage:{getItem:()=>null}});
vm.runInContext(read('src/app.js').split('/* ======================================================================= démarrage */')[0],context);
for(const file of ['physical-parts','physical-cabinet','facade-details','facade-functional','pl20-facade','tgbt8-facade','equipment-audit']) vm.runInContext(read('src/'+file+'.js'),context);
assert.equal(data.boards.length,68);
let functional=0,hits=0;
for(const board of data.boards){
 assert.ok(board.audit,board.id);
 for(const field of ['identity','facade','locations','network','browser'])assert.ok(board.audit[field],board.id+':'+field);
 assert.ok(read('docs/CONTROLE-ARMOIRES.html').includes('id="'+board.id+'"'));
 for(const live of [false,true]){
  const svg=vm.runInContext(`facadeSVG(${JSON.stringify(board.facade)},{live:${live}})`,context);
  assert.ok(!/NaN|undefined/.test(svg),board.id);
  for(const match of svg.matchAll(/data-id="([^"]+)"/g)){
   assert.ok(data.nodes.some(node=>node.id===match[1]),board.id+':'+match[1]);hits++;
  }
 }
 if(data.facades[board.facade].mode==='functional'){
  functional++;assert.ok(read('docs/facades-vectors/'+board.id+'.svg').includes('LISTE DOCUMENTAIRE'));
 }
 assert.ok(vm.runInContext(`equipmentAuditHTML(window.OCC_DATA.boards.find(b=>b.id===${JSON.stringify(board.id)}))`,context).includes('facades-vectors/'+board.id+'.svg'));
}
assert.equal(functional,6);
for(const id of ['TS7','TS44','TS12']){
 const facade=data.facades[id];
 assert.ok(!facade.cols.flatMap(c=>c.units).some(u=>u.dep),id+': position supposée');
 assert.ok(data.nodes.filter(n=>n.board===id).length>0,id+': départs conservés');
}
assert.equal(data.facades.TS44.cols.length,6);
assert.equal(data.facades.COND4.cols.length,4);
assert.equal(data.facades.VENTIL.mode,'photo-partial');
assert.deepEqual(data.edges,base.edges);
assert.deepEqual(data.procs,base.procs);
console.log(`PASS audit : 68 fiches et SVG, ${hits} cibles contrôlées dans deux modes, 6 listes documentaires, topologie inchangée.`);
