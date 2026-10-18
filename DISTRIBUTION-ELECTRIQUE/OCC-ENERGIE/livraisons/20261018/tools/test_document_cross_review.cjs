const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const data = JSON.parse(read('OCC_ENERGIE.html').match(/window\.OCC_DATA=([\s\S]*?);<\/script>/)[1]);
const base = JSON.parse(read('build/data.json'));
assert.deepEqual(data.edges, base.edges, 'Le rapprochement documentaire ne crée aucun câble');
assert.deepEqual(data.procs, base.procs, 'Les procédures ne sont pas réécrites');
assert.equal(data.documentReview.xlsmReferencesChecked, 371);
assert.equal(data.documentReview.xlsmDifferences, 0);
assert.equal(data.documentReview.catalog.length, 76);
assert.equal(data.documentReview.catalog.reduce((sum, doc) => sum + doc.pages, 0), 868);
for (const doc of data.documentReview.catalog) {
  const hash = crypto.createHash('sha256').update(fs.readFileSync(path.join(root, doc.href))).digest('hex');
  assert.equal(hash, doc.sha256, doc.name);
}
const context = vm.createContext({window:{OCC_DATA:data},localStorage:{getItem:()=>null}});
vm.runInContext(read('src/app.js').split('/* ======================================================================= démarrage */')[0], context);
vm.runInContext(read('src/document-evidence.js'), context);
for (const id of ['TGBT1','TGBT2','TGBT4','TGBT5','TGBT6','TS33','TS34','TS9']) {
  const html = vm.runInContext(`documentEvidenceHTML(BOARD['${id}'])`, context);
  assert.ok(html.includes('Écart documentaire'), id);
  assert.ok(!html.includes('undefined') && !html.includes('NaN'), id);
}
for (const id of ['TS2','TS7','TS8','TS9','TS17','TS40']) {
  assert.ok(data.boards.find(board => board.id === id).scanConsumers.items.length, id);
}
assert.equal(data.documentReview.unassignedSources.length, 3);
assert.ok(vm.runInContext("search('7PM043', 100).some(hit => hit.kind === 'board' && hit.id === 'TS9')", context));
for (const id of ['TS33','TS34']) assert.equal(data.boards.find(board => board.id === id).supplyEvidence.board, null);
assert.ok(vm.runInContext('documentReviewBanner()', context).includes('76 PDF'));
assert.ok(data.boards.find(board => board.id === 'ARM110').sourceDocuments.some(doc => doc.name.includes('110v')));
assert.ok(read('docs/PHOTOTHEQUE-MODULE.html').includes('266 fichiers'));
assert.ok(read('src/app.js').includes("b.documentaryOnly ? 'raccordement non établi'"));
assert.ok(read('src/app.js').includes("b.documentaryOnly ? 'unk' : isLive(h.id)"));
console.log('PASS documents : 371 références, 76 PDF identiques aux sources, 868 pages, écarts et consommateurs visibles, topologie préservée.');
