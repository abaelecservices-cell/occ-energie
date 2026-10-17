const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const data = JSON.parse(read('OCC_ENERGIE.html').match(/window\.OCC_DATA=([\s\S]*?);<\/script>/)[1]);
const context = vm.createContext({window: {OCC_DATA: data}, localStorage: {getItem: () => null}});
vm.runInContext(read('src/app.js').split('/* ======================================================================= démarrage */')[0], context);
for (const file of ['plans.js', 'manoeuvres.js', 'arbre.js', 'arbre-info.js']) vm.runInContext(read('src/' + file), context);
const tree = vm.runInContext('arbreHTML()', context);
for (const board of data.boards) {
  assert.ok(tree.includes(`data-go="#/b/${board.id}"`), board.id);
  assert.ok(data.facades[board.facade], board.id);
}
for (const node of data.nodes.filter(n => n.board && n.t !== 'bus')) {
  assert.ok(tree.includes(`data-open="${node.id}"`), node.id);
}
assert.ok(tree.includes('1A26') && tree.includes('6-28'));
assert.ok(tree.includes('Schéma fonctionnel'));
assert.ok(tree.includes('raccordement à confirmer'));
assert.ok(!tree.includes('undefined') && !tree.includes('NaN'));
for (const id of ['TS33', 'TS34', 'TS37', 'TS40', 'TS45', 'TS47']) {
  assert.ok(!data.edges.some(e => e.a === id + '_J' || e.b === id + '_J'));
}
console.log('PASS arborescence: 68 équipements, tous les appareils visibles, origines documentaires sans arête simulée.');
