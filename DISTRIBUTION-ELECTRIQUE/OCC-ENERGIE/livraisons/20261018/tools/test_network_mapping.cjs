const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const data = JSON.parse(read('OCC_ENERGIE.html').match(/window\.OCC_DATA=([\s\S]*?);<\/script>/)[1]);
const context = vm.createContext({window:{OCC_DATA:data},localStorage:{getItem:()=>null}});
vm.runInContext(read('src/app.js').split('/* ======================================================================= démarrage */')[0], context);
for (const file of ['plans.js','plansvg.js','manoeuvres.js','net.js','network-secondary.js']) vm.runInContext(read('src/'+file), context);
const plan = data.plans.find(p => p.id === 'PLAN_SS1');
assert.equal(plan.items.find(i => i.t.includes('N3,1 creuset')).ref, 'TGBT8');
assert.equal(plan.items.find(i => i.t === 'Armoire gradathyr').ref, 'GRADATHYR');
for (const index of [1,2]) {
  assert.equal(plan.items.find(i => i.t === 'Boosting creuset '+index).ref, 'TR_BOOST_CREUSET_'+index);
}
for (const id of ['TR8A','TR8B']) assert.ok(data.edges.some(e => e.a === id && e.b.startsWith('TGBT8_Q')));
assert.equal(data.nodes.filter(n => n.stage === 'secondary').length, 11);
for (const node of data.nodes.filter(n => n.stage === 'secondary')) {
  assert.ok(plan.items.some(i => i.ref === node.id));
  assert.ok(!data.edges.some(e => e.a === node.id || e.b === node.id));
}
const svg = vm.runInContext('planSVG(D.plans.find(p=>p.id==="PLAN_SS1"))',context);
const network = vm.runInContext('fullNetSVG()',context);
for (const drawing of [svg,network]) assert.ok(!drawing.includes('undefined') && !drawing.includes('NaN'));
assert.ok(network.includes('Transformateurs secondaires repérés'));
assert.ok(network.includes('TR_BOOST_CREUSET_1'));
fs.writeFileSync(path.join(root,'docs/MAPPING-SS1.svg'),svg.replace(/(<svg[^>]*>)/,'$1<style>.hl{fill:none;stroke:none}svg{color:#16201b;--bg:#fff;--ink-3:#555;--glass-strong:#fff}</style>'));
fs.writeFileSync(path.join(root,'docs/RESEAU-HTA.svg'),network.replaceAll('var(--glass-strong)', '#fff').replace(/(<svg[^>]*>)/,'$1<style>.hl{fill:none;stroke:none}svg{color:#16201b;--bg:#fff;--ink-3:#555;--glass-strong:#fff}</style>'));
console.log('PASS mapping : TGBT8 N3,1, Gorge distinct, 11 transfos secondaires repérés, rendus SS1 et HTA cohérents.');
