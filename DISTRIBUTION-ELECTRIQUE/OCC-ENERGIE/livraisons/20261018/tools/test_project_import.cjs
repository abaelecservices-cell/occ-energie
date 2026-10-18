const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const read=file=>fs.readFileSync(path.join(root,file),'utf8');
const data=file=>JSON.parse(read(file).match(/window\.OCC_DATA=([\s\S]*?);<\/script>/)[1]);
const before=data('sources/projects/20261018/OCC_ENERGIE-avant-import.html');
const after=data('OCC_ENERGIE.html');
const catalog=JSON.parse(read('build/project-import-catalog.json'));
for(const key of ['nodes','edges','procs','facades','site','validations','issues'])assert.deepEqual(after[key],before[key],key);
assert.deepEqual(after.boards.map(b=>b.id),before.boards.map(b=>b.id));
for(const board of after.boards){
  const previous=before.boards.find(b=>b.id===board.id);
  for(const key of Object.keys(previous)){
    if(key==='photos')assert.ok(previous.photos.every(p=>board.photos.includes(p)));
    else assert.deepEqual(board[key],previous[key],`${board.id}.${key}`);
  }
}
assert.equal(catalog.distribution.length,438);
assert.equal(catalog.distribution.filter(r=>r.status==='identique').length,436);
assert.deepEqual(catalog.distribution.filter(r=>r.status==='nouveau').map(r=>r.cell),['H1','G1']);
assert.equal(catalog.summary.conflictingCells,0);
assert.equal(catalog.photos.length,267);
assert.equal(catalog.documents.length,35);
assert.equal(catalog.documents.reduce((sum,d)=>sum+d.pages.length,0),256);
assert.equal(catalog.rooms.length,5);
assert.equal(Object.keys(catalog.layouts).length,5);
const addition=catalog.photos.filter(p=>p.newToModule);
assert.equal(addition.length,1);assert.equal(addition[0].board,'TS8');assert.equal(addition[0].name,'IMG_3966.jpeg');
assert.equal(catalog.photos.filter(p=>p.groupCorrected).length,8);
const assets=[...catalog.photos,...catalog.documents.flatMap(d=>d.pages),catalog.unif,catalog.originalSiteImage,...Object.values(catalog.layouts)];
for(const asset of assets){
 const bytes=fs.readFileSync(path.join(root,asset.href));
 assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),asset.sha256);
}
const ctx=vm.createContext({D:after,esc:value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;'),encodeURIComponent});
vm.runInContext(read('src/project-import.js'),ctx);
assert.equal(ctx.projectImportHTML({id:'unknown'}),'');
const ts8=after.boards.find(b=>b.id==='TS8');
assert.ok(ctx.projectImportHTML(ts8).includes('facades-vectors/TS8.svg'));
assert.ok(ctx.projectImportBanner().includes('68 représentations vectorielles'));
assert.ok(ctx.projectImportHTML({...ts8,projectImport:{...ts8.projectImport,notes:[{text:'<script>',source:'source'}]}}).includes('&lt;script>'));
const html=read('docs/COMPLEMENTS-20261018.html');
for(const board of after.boards.filter(b=>b.projectImport))assert.ok(html.includes(`id="${board.id}"`));
assert.ok(html.includes('id="SANS-AFFECTATION"'));
assert.ok(!/<img\b|<image\b|data:image\/(?:jpeg|webp|png)/i.test(html));
assert.equal(after.projectImport.vectorOnly,true);
assert.ok(!Object.hasOwn(ts8.projectImport,'photos'));
assert.ok(!ctx.projectImportHTML(ts8).includes('photos-module'));
assert.ok(read('src/app.js').includes('b.crossEvidence, b.projectImport'));
assert.ok(after.boards.find(b=>b.id==='TGBT8').projectImport.distribution.some(r=>r.cell==='G1'));
console.log('PASS import projet : 267 photos, 256 pages, 438 références, médias intacts, classements préservés, réseau et vue usine inchangés.');
