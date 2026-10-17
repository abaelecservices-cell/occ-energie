const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname,'..');
const read = file => fs.readFileSync(path.join(root,file),'utf8');
const data = JSON.parse(read('OCC_ENERGIE.html').match(/window\.OCC_DATA=([\s\S]*?);<\/script>/)[1]);
const context = vm.createContext({window:{OCC_DATA:data},localStorage:{getItem:()=>null}});
vm.runInContext(read('src/app.js').split('/* ======================================================================= démarrage */')[0],context);
vm.runInContext(read('src/tgbt8-facade.js'),context);
assert.deepEqual(data.facades.TGBT8.cols.map(c=>c.n),['3.1','4.1','3.2','Arrivée 1','Arrivée 2','Normal-secours','4.2','5','6']);
assert.equal(data.facades.TGBT8.cols[1].units[0].dep,'D0100');
assert.equal(data.facades.TGBT8.cols[2].units[0].dep,undefined);
for (const live of [false,true]) {
  const svg = vm.runInContext(`facadeSVG('TGBT8',{live:${live}})`,context);
  assert.ok(svg.includes('IMG_4400 à IMG_4417'));
  assert.equal((svg.match(/<ellipse /g)||[]).length,6,'Six ventilateurs sur les armoires de zones');
  for (const id of ['TGBT8_QA','TGBT8_QB','TGBT8_QC','D0105','D0100']) assert.ok(svg.includes(`data-id="${id}"`));
  assert.ok(!svg.includes('data-id="D0103"') && !svg.includes('data-id="D0104"'));
  assert.ok(svg.includes('CONTRÔLE') && svg.includes('NORMAL — SECOURS'));
  assert.ok(!svg.includes('undefined') && !svg.includes('NaN'));
}
assert.ok(read('OCC_ENERGIE.html').includes('function tgbt8FacadeSVG'));
console.log('PASS TGBT8 : rendu dédié, toiture, appareils interactifs, code embarqué et SVG normal/live.');
