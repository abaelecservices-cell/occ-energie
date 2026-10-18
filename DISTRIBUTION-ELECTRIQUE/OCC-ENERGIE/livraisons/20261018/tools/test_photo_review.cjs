const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const data = JSON.parse(read('build/data.json'));
const review = JSON.parse(read('build/ts17-photo-review.json'));
const beforeNodes = JSON.stringify(data.nodes);
const beforeEdges = JSON.stringify(data.edges);
Object.assign(data.boards.find(board => board.id === 'TS17'), review.board);
for (const patch of review.boards || []) {
  Object.assign(data.boards.find(board => board.id === patch.id), patch);
}
data.facades.TS17 = review.facade;
assert.equal(JSON.stringify(data.nodes), beforeNodes);
assert.equal(JSON.stringify(data.edges), beforeEdges);
const completion = JSON.parse(read('build/photo-completion.json'));
for (const patch of completion.nodes) {
  assert.deepEqual(Object.keys(patch).sort(), ['case', 'id', 'src']);
  Object.assign(data.nodes.find(node => node.id === patch.id), patch);
}
for (const patch of completion.boards) {
  const {observations = [], ...fields} = patch;
  const board = data.boards.find(board => board.id === patch.id);
  Object.assign(board, fields);
  board.obs = [...(board.obs || []), ...observations];
}
Object.assign(data.facades, completion.facades);
assert.deepEqual(data.facades.TS17.cols.map(col => col.n),
  ['17A-1', '17A-2', '17A-3', '17A-4', '17B-1', '17B-2', '17B-3']);
for (const col of data.facades.TS17.cols) {
  for (const unit of col.units) {
    if (unit.dep) assert.ok(data.nodes.some(node => node.id === unit.dep && node.board === 'TS17'));
    assert.ok(unit.y >= 0 && unit.y + unit.h <= data.facades.TS17.height);
  }
}
const source = read('src/app.js').split('/* ======================================================================= démarrage */')[0];
const context = vm.createContext({window: {OCC_DATA: data}, localStorage: {getItem: () => null}});
vm.runInContext(source, context);
const svg = vm.runInContext('facadeSVG("TS17")', context);
assert.ok(svg.includes('17A-4') && svg.includes('17B-3'));
assert.ok(!svg.includes('undefined') && !svg.includes('NaN'));
assert.ok(svg.includes('Colonne et ordre relevés sur photo'));
const links = vm.runInContext('photoLinks(BOARD.TS17.photos)', context);
assert.ok(links.includes('docs/facades-vectors/TS17.svg'));
assert.ok(!/href="[^"]*PHOTOS/.test(links));
assert.ok(!links.includes('../Plan%20%C3%A9lectrique/docs/'));
assert.ok(links.includes('Ts17A.pdf'));
for (const [id, count] of [['TS15', 3], ['TS16', 2], ['GORGE', 4], ['VARIVOLT', 2], ['TS8', 4], ['COFAGIT', 1], ['TS1', 8], ['PEG', 2], ['TS28', 3], ['TS24', 5], ['ETUVE789', 1], ['TS42', 4]]) {
  assert.equal(data.facades[id].cols.length, count);
  const drawing = vm.runInContext(`facadeSVG("${id}")`, context);
  assert.ok(drawing.startsWith('<svg'));
  assert.ok(!drawing.includes('undefined') && !drawing.includes('NaN'));
  const simulation = vm.runInContext(`facadeSVG("${id}", {live:true})`, context);
  assert.ok(!simulation.includes('undefined') && !simulation.includes('NaN'));
  for (const col of data.facades[id].cols) {
    for (const unit of col.units) {
      if (unit.dep) assert.equal(data.nodes.find(node => node.id === unit.dep).board, id);
    }
  }
}
assert.equal(data.nodes.find(node => node.id === 'D0387').case, '24');
assert.equal(data.nodes.find(node => node.id === 'D0390').case, '42');
for (const id of ['TS15', 'TS16', 'COND6A']) {
  const localLinks = vm.runInContext(`photoLinks(BOARD.${id}.photos)`, context);
  assert.ok(localLinks.includes('href="docs/facades-vectors/') || localLinks.includes('href="docs/VECTORIELLES.html"'));
  assert.ok(!/href="[^"]*PHOTOS/.test(localLinks));
  assert.ok(!localLinks.includes('file introuvable'));
}
console.log('PASS: TS17 et 12 nouvelles façades (agitateur partiel), repères cohérents, SVG valides, liens locaux ; topologie préservée, 7 cases TS15 enrichies.');

assert.ok(data.boards.find(b => b.id === 'TS44').obs.some(o => o.t.includes('Q2-24 / 1-24')));
assert.equal(data.nodes.find(n => n.id === 'D0207').case, '1-24');
