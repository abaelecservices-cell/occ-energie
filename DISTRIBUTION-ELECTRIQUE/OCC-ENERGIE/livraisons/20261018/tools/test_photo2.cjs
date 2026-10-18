const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const base = JSON.parse(read('build/data.json'));
const data = JSON.parse(read('OCC_ENERGIE.html').match(/window\.OCC_DATA=([\s\S]*?);<\/script>/)[1]);
for (const key of ['edges', 'procs', 'validations']) {
  if (key in base) assert.deepEqual(data[key], base[key]);
}
assert.deepEqual(data.nodes.slice(0, base.nodes.length).map(n => n.id), base.nodes.map(n => n.id));
assert.equal(data.boards.filter(b => b.facade).length, 68);
assert.equal(data.boards.find(b => b.id === 'TS43').facadeMode, 'functional');
for (const id of ['TS28', 'TS24', 'ETUVE789', 'TS42']) {
  assert.equal(data.boards.find(b => b.id === id).facade, id);
  for (const col of data.facades[id].cols) {
    for (const unit of col.units) {
      assert.ok(unit.y >= 0 && unit.y + unit.h <= data.facades[id].height);
      if (unit.dep) assert.equal(data.nodes.find(n => n.id === unit.dep).board, id);
    }
  }
}
assert.ok(data.boards.find(b => b.id === 'PL20').obs.some(o => o.src.startsWith('photo.zip')));
const gallery = read('docs/PHOTOS-20261016.html');
assert.equal((gallery.match(/<figure>/g) || []).length, 248);
assert.ok(gallery.includes('id="TS40"'));
assert.ok(gallery.includes('id="FILIERE"'));
assert.equal((read('docs/INVENTAIRE-PHOTO-20261016.csv').trim().split(/\r?\n/)).length, 372);
console.log('PASS photo.zip: 248 images, 371 occurrences, 4 façades, 68 représentations, dont 6 listes documentaires après contrôle, topologie et identités préservées.');
