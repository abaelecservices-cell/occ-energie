/* ======================================================================= arborescence du réseau
   CNR (normal) / EDF (secours) → poste de livraison → sous-station → tableau 20 kV → transformateurs → TGBT (½ A / ½ B) → TS → coffrets.
   Construite à partir des liaisons documentées du modèle (aucune liaison supposée). */
const tDot = id => { const v = BOARD[id] ? refLive(id) : NODE[id] ? (SW.has(NODE[id].t) && !isClosed(id) ? false : isLive(id)) : null; return `<span class="dot ${v === null ? 'unk' : v ? 'on' : 'off'}"></span>`; };
// « couplage Couplage TGBT 1 » -> « Couplage TGBT 1 » : le mot générique n'est ajouté que s'il ne commence pas déjà le nom
const tnm = (w, x) => { const l = dn(x); return new RegExp('^' + w, 'i').test(l) ? l : `${w} ${l}`; };
const tLoc = b => { const l = locChain(b.loc); return l.length > 1 ? l[l.length - 1].name : ''; };
// tableaux / transformateurs alimentés directement par les appareils du tableau bid
function arbreKids(bid, path) {
  const res = new Map();
  const get = (k, o) => { if (!res.has(k)) res.set(k, Object.assign({ via: [], tr: [] }, o)); return res.get(k); };
  D.nodes.filter(n => n.board === bid).forEach(n => (DOWN[n.id] || []).forEach(e => {
    const m = NODE[e.b]; if (!m) return;
    if (m.t === 'tr') {
      const to = (DOWN[m.id] || []).map(x => NODE[x.b]).find(x => x && x.board && x.board !== bid);
      if (to && path.includes(to.board)) return;
      get(to ? 'B:' + to.board : 'T:' + m.id, { board: to ? to.board : null }).tr.push({ tr: m, cell: n, to });
      return;
    }
    if (m.board && m.board !== bid && !path.includes(m.board)) get('B:' + m.board, { board: m.board }).via.push({ from: n, to: m });
  }));
  return [...res.values()].sort((a, b) => (a.board ? BOARD[a.board].name : 'zz').localeCompare(b.board ? BOARD[b.board].name : 'zz', 'fr', { numeric: true }));
}
function tVia(k) {
  const tr = k.tr.map(t => `<a href="#" data-open="${t.tr.id}">${esc(dn(t.tr))}${t.tr.kva ? ' ' + esc(t.tr.kva) : ''}</a>`);
  const dv = k.via.map(v => `<a href="#" data-open="${v.from.id}">${esc(dn(v.from))}</a>${v.from.case ? ' (' + esc(v.from.case) + ')' : ''}`);
  return tr.length ? `par ${tr.join(' · ')}` : dv.length ? `par ${[...new Set(dv)].slice(0, 3).join(' · ')}${dv.length > 3 ? '…' : ''}` : '';
}
function tHead(bid, via, icon) {
  const b = BOARD[bid], nd = (DEPS_BY_BOARD[bid] || []).length;
  return `${tDot(bid)}<span class="ticon">${icon}</span><a class="tname" href="#" data-go="#/b/${bid}">${esc(b.name)}</a>
    <span class="tmeta">${esc([tLoc(b), nd ? nd + ' départs' : ''].filter(Boolean).join(' · '))}${via ? ' — ' + via : ''}</span>
    ${(() => { const pl = planFor(bid); return pl && pl !== window.__planCur && pl !== 'PLAN_PDL' ? `<a class="tact" href="#" data-go="#/plans/${pl}/${bid}" title="Plan du local">📍</a>` : ''; })()}
    <a class="tact" href="#" data-go="#/courant/${bid}" title="Remettre le courant">⚡</a>`;
}
function tIcon(b) { return b.kind === 'HTA' ? '⚡' : b.kind === 'TGBT' ? '▦' : b.kind === 'Coffret' ? '▫' : '▭'; }
// Afficher tous les départs dans l'arborescence, sans en déduire une position en façade.
function arbreDepLeaves(bid, bus, includeUnassigned = false) {
  const ds = (DEPS_BY_BOARD[bid] || []).filter(d => {
    const db = busOf(d.id);
    return includeUnassigned ? db !== bus.sa && db !== bus.sb : !bus || db === bus;
  });
  if (!ds.length) return '';
  return `<details class="tnode tdeps" data-n="${esc(norm('depart departs '+BOARD[bid].name))}"><summary><span class="ticon">≡</span><b>Départs documentés (${ds.length})</b><span class="tmeta">repères cliquables · positions physiques non présumées</span></summary><div class="tkids">${ds.sort((a,b)=>dn(a).localeCompare(dn(b),'fr',{numeric:true})).map(d => `<div class="tnode tleaf" data-n="${esc(norm(d.label + ' ' + (d.case||'')))}">${tDot(d.id)}<span class="ticon">↳</span><a class="tname" data-open="${esc(d.id)}" href="#">${esc(dn(d))}</a><span class="tmeta">${d.case?'case '+esc(d.case)+' · ':''}${confPill(d.conf)} · <a href="#" data-go="#/b/${bid}/f/${d.id}">Façade</a></span></div>`).join('')}</div></details>`;
}
function arbreBoard(bid, depth, path, via) {
  const b = BOARD[bid], p2 = path.concat(bid), kids = arbreKids(bid, p2);
  const head = tHead(bid, via, tIcon(b));
  const data = `data-n="${esc(norm(b.name + ' ' + (b.alias || '')))}"`;
  if (!kids.length && !(DEPS_BY_BOARD[bid] || []).length) return `<div class="tnode tleaf" ${data}>${head}</div>`;
  const render = k => k.board ? arbreBoard(k.board, depth + 1, p2, tVia(k))
    : k.tr.map(t => `<div class="tnode tleaf" data-n="${esc(norm(t.tr.label))}">${tDot(t.tr.id)}<span class="ticon">◎</span><a class="tname" href="#" data-open="${t.tr.id}">${esc(dn(t.tr))}</a><span class="tmeta">${esc(t.tr.kva || '')} — ${esc(tnm('cellule', t.cell))}</span></div>`).join('');
  let inner;
  const s = srcSet(bid);
  if (s) {  // TGBT scindé : chaque moitié sous son transformateur
    const half = k => { const v = k.via[0]; const bu = v ? busOf(v.from.id) : null; return bu === s.ba ? 'A' : bu === s.bb ? 'B' : '?'; };
    const grp = { A: [], B: [], '?': [] }; kids.forEach(k => grp[half(k)].push(k));
    const hl = (h, lab, tr) => `<details class="tnode thalf" ${depth < 4 ? 'open' : ''} data-n="${esc(norm(lab))}"><summary>${tDot(h === 'A' ? s.ba : s.bb)}<span class="ticon">½</span><b>${esc(lab)}</b><span class="tmeta">sur ${esc(dn(tr))}${tr.kva ? ' ' + esc(tr.kva) : ''} · ${(DEPS_BY_BOARD[bid] || []).filter(d => busOf(d.id) === (h === 'A' ? s.ba : s.bb)).length} départs</span></summary><div class="tkids">${grp[h].map(render).join('') + arbreDepLeaves(bid, h === 'A' ? s.ba : s.bb) || '<div class="tnode tleaf tmeta">Aucun tableau ni départ documenté</div>'}</div></details>`;
    inner = hl('A', s.la, s.sa) + `<div class="tcpl">⇄ ${esc(tnm('couplage', s.qc))} —${isClosed(s.qc.id) ? 'fermé' : 'ouvert'} (simulation)</div>` + hl('B', s.lb, s.sb) + grp['?'].map(render).join('') + arbreDepLeaves(bid, { sa: s.ba, sb: s.bb }, true);
  } else inner = kids.map(render).join('') + arbreDepLeaves(bid, null);
  return `<details class="tnode" ${depth < 3 ? 'open' : ''} ${data}><summary>${head}</summary><div class="tkids">${inner}</div></details>`;
}
// Inventaire exhaustif : les équipements non reliés à la racine restent affichés,
// sans transformer une hypothèse documentaire en liaison d'exploitation.
function arbreSansOrigine() {
  const seen = new Set(['PL20']);
  const visit = (bid, path) => {
    if (path.length > 24) return;
    for (const k of arbreKids(bid, path)) {
      if (!k.board || path.includes(k.board)) continue;
      seen.add(k.board);
      visit(k.board, path.concat(k.board));
    }
  };
  visit('PL20', ['PL20']);
  const missing = D.boards.filter(b => !seen.has(b.id))
    .sort((a, b) => a.name.localeCompare(b.name, 'fr', { numeric: true }));
  if (!missing.length) return '';
  return `<details class="tnode tss" open data-n="origine non documentee armoires non rattachees">
    <summary><span class="ticon">⚠️</span><b>Origine non documentée / hors parcours CNR–EDF (${missing.length})</b>
      <span class="tmeta">inventoriés, mais aucun chemin complet démontré depuis la racine</span></summary>
    <div class="tkids"><p class="small muted">Ces éléments restent consultables. Cette rubrique ne signifie
      pas qu'ils sont hors tension et ne peut pas servir de consigne de manœuvre.</p>
      ${missing.map(b => `<div class="tnode tleaf" data-n="${esc(norm(b.name + ' ' + (b.alias || '')))}">
        <span class="dot unk"></span><span class="ticon">${tIcon(b)}</span>
        <a class="tname" href="#" data-go="#/b/${b.id}">${esc(b.name)}</a>
        <span class="tmeta">${esc(tLoc(b))} · ${(DEPS_BY_BOARD[b.id] || []).length} départ(s) · amont à établir</span>
        ${arbreDepLeaves(b.id, null)}
      </div>`).join('')}
    </div></details>`;
}
function arbreHTML() {
  // racine : sources → poste de livraison ; puis les tableaux 20 kV regroupés par sous-station
  const pl = BOARD.PL20, plKids = arbreKids('PL20', ['PL20']);
  const bySS = {};
  plKids.forEach(k => { const b = BOARD[k.board]; const loc = locChain(b.loc).find(l => l.kind === 'poste') || { id: '?', name: 'Localisation non documentée' }; (bySS[loc.id] = bySS[loc.id] || { loc, kids: [] }).kids.push(k); });
  const ss = Object.values(bySS).map(g => `<details class="tnode tss" open data-n="${esc(norm(g.loc.name))}"><summary><span class="ticon">🏭</span><b>${esc(g.loc.name)}</b></summary><div class="tkids">${g.kids.map(k => arbreBoard(k.board, 2, ['PL20'], tVia(k))).join('')}</div></details>`).join('');
  const ge = D.nodes.filter(n => n.t === 'src' && !['SRC_CNR', 'SRC_EDF'].includes(n.id));
  return `<details class="tnode troot" open data-n="cnr edf sources"><summary>${tDot('SRC_CNR')}<span class="ticon">⚡</span><b>CNR</b><span class="tmeta">réseau normal</span>
      <span class="tsep">/</span>${tDot('SRC_EDF')}<b>EDF</b><span class="tmeta">secours — bascule automatique sur manque CNR, jamais les deux ensemble</span></summary>
    <div class="tkids"><details class="tnode" open data-n="${esc(norm(pl.name))}"><summary>${tHead('PL20', 'arrivées CNR (01) et EDF (04)', '⚡')}</summary><div class="tkids">${ss}</div></details></div></details>
    ${ge.map(g => { const to = (DOWN[g.id] || []).map(e => NODE[e.b]).find(x => x && x.board); return `<div class="tnode tleaf" data-n="${esc(norm(g.label))}">${tDot(g.id)}<span class="ticon">⚙</span><b>${esc(dn(g))}</b><span class="tmeta">${to ? '→ ' + esc(BOARD[to.board].name) + ' (' + esc(dn(to)) + ')' : ''} — logique de permutation non documentée</span></div>`; }).join('')}
    ${arbreSansOrigine()}`;
}
function bindArbre(host) {
  const q = $('#tq'); if (!q) return;
  q.oninput = () => {
    const v = norm(q.value), nodes = $$('.tnode', host);
    nodes.forEach(n => { n.style.display = ''; });
    if (!v) return;
    // un nœud reste visible s'il correspond ou si un descendant correspond ; les ancêtres d'une correspondance sont dépliés
    const match = n => (n.dataset.n || '').includes(v);
    [...nodes].reverse().forEach(n => { const sub = $$('.tnode', n).some(c => c.style.display !== 'none'); n.style.display = match(n) || sub ? '' : 'none'; if (sub && n.tagName === 'DETAILS') n.open = true; });
    nodes.forEach(n => { if (match(n)) $$('.tnode', n).forEach(c => { c.style.display = ''; }); });
  };
  $('#topen').onclick = () => $$('details.tnode', host).forEach(d => d.open = true);
  $('#tclose').onclick = () => $$('details.tnode', host).forEach((d, i) => d.open = d.classList.contains('troot') || d.classList.contains('tss'));
}
