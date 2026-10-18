const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const payload = read('OCC_ENERGIE.html').match(/window\.OCC_DATA=([\s\S]*?);<\/script>/);
assert.ok(payload, 'Le HTML livré doit embarquer ses données');
const data = JSON.parse(payload[1]);
const elements = {};
const document = {querySelector: selector => elements[selector] ||= {innerHTML:''}, querySelectorAll: () => []};
const context = vm.createContext({window:{OCC_DATA:data},localStorage:{getItem:()=>null},document});
vm.runInContext(read('src/app.js').split('/* ======================================================================= démarrage */')[0],context);
vm.runInContext(read('src/manoeuvres.js'),context);
vm.runInContext(read('src/fiche.js'),context);
const evaluate = code => vm.runInContext(code,context);
assert.ok(evaluate('search("TS 15 case 24").some(item => item.id === "D0387")'));
assert.ok(evaluate('recContext({kind:"node",id:"D0387"}).includes("case 24")'));
assert.ok(evaluate('whereText(NODE.D0387).includes("case 24")'));
assert.equal(evaluate('facadeFor("D0387")'), 'TS15');
assert.equal(evaluate('boardForFacade(facadeFor("D0336"))'), 'TS16');
assert.equal(evaluate('facadeFor("D0380")'), null, 'Un départ non localisé ne reçoit pas de position inventée');
for (const id of ['TS15','TS16','GORGE','VARIVOLT']) {
  assert.equal(evaluate(`BOARD.${id}.facade`),id);
  assert.ok(evaluate(`photoLinks(BOARD.${id}.photos)`).includes('href="docs/VECTORIELLES.html"') || evaluate(`photoLinks(BOARD.${id}.photos)`).includes('href="docs/facades-vectors/'));
}
evaluate('vReg()');
for (const id of ['TS8','COFAGIT']) {
  assert.equal(evaluate(`BOARD.${id}.facade`),id);
  assert.ok(evaluate(`photoLinks(BOARD.${id}.photos)`).includes(`href="docs/facades-vectors/${id}.svg"`));
}
assert.ok(elements['#view'].innerHTML.includes('cases TS15'));
assert.ok(elements['#view'].innerHTML.includes('TS16 : annotation TGBT 6 / TR7A'));
console.log('PASS: HTML livré, recherche, contexte des résultats, fiche détaillée, localisation des départs, sources photo et Registre.');

assert.ok(data.boards.find(b => b.id === "TS44").obs.some(o => o.t.includes("Q2-24 / 1-24")));
assert.equal(data.nodes.find(n => n.id === "D0207").case, "1-24");
for (const id of ["TS1", "PEG"]) assert.ok(evaluate(`photoLinks(BOARD.${id}.photos)`).includes(`facades-vectors/${id}.svg`));

for (const id of ["TS24", "TS28", "TS42", "PL20", "TGBT8", "TS7"]) assert.ok(evaluate(`photoLinks(BOARD.${id}.photos)`).includes(`facades-vectors/${id}.svg`));
assert.ok(!elements["#view"].innerHTML.includes("(aucune photo)"));

evaluate("vFiche(\"TS33\")");
assert.ok(elements["#view"].innerHTML.includes("1A26"));
assert.ok(elements["#view"].innerHTML.includes("raccordement à confirmer"));
