/* ======================================================================= fiche détaillée (optionnelle, repliée derrière la fiche de manœuvre)
   De quoi dépend un élément, étage par étage : où se trouve chaque appareil et quoi y contrôler ; secours documentés ; aval ; clés ; procédures. */
/* La fiche détaillée part de la configuration NORMALE documentée (pas de l'état simulé) : une hypothèse de simulation
   ne doit jamais changer le chemin présenté au technicien. */
const closed0 = id => defaultClosed(NODE[id]);
function bestPath(id) {
  const ps = upPaths(id, 16);
  if (!ps.length) return null;
  const closed = p => p.every(x => !SW.has(NODE[x].t) || closed0(x) || x === id);
  // chemin d'alimentation normal : appareils fermés en configuration normale, le moins de couplages traversés, puis le plus court
  const ncpl = p => p.filter(x => NODE[x].t === 'cpl').length;
  const sorted = ps.slice().sort((a, b) => ncpl(a) - ncpl(b) || a.length - b.length);
  return sorted.find(closed) || sorted[0];
}
function whereText(n) {
  const b = boardOf(n); if (!b) return '';
  const loc = locChain(b.loc).slice(1).map(l => l.name).join(' › ');
  return [loc, b.name, n.case ? 'case ' + n.case : ''].filter(Boolean).join(' › ');
}
function checkText(n) {
  const u = n.uni || {};
  if (n.t === 'src') return n.id === 'SRC_CNR' ? 'Tension réseau CNR (source normale) : voyants de la cellule d’arrivée au poste de livraison.'
    : n.id === 'SRC_EDF' ? 'Tension réseau EDF (secours). Sur manque CNR, bascule automatique : CNR 01 s’ouvre, EDF 04 se ferme.'
    : 'Source autonome : état du groupe (logique de permutation à confirmer).';
  if (n.t === 'tr') return `Alarme ou déclenchement « ${u.surv || n.cooling || 'surveillance'} ». Défaut interne : pas de remise sous tension avant expertise.`;
  if (n.t === 'cpl' && n.board && BOARD[n.board] && BOARD[n.board].kind === 'HTA') return 'Couplage 20 kV : position.';
  if (n.t === 'cpl') return 'Couplage : ouvert en exploitation normale. Jamais 3 appareils fermés (arrivée A · couplage · arrivée B).';
  if (n.t === 'bus') return 'Tension (centrale de mesure, voyants)' + (boardOf(n) && boardOf(n).it ? ' ; contrôleur d’isolement (neutre IT).' : '.');
  if (u.relay) return `Position ; relais ${u.relay} : drapeau de déclenchement. Réglages : ${u.settings || 'non renseignés'}.`;
  if (n.board && BOARD[n.board] && BOARD[n.board].kind === 'HTA') return 'Interrupteur fermé, sectionneur de terre ouvert, présence tension.';
  if (n.role === 'arrivee') return `Position O / I, voyant de déclenchement${n.model ? ' (' + n.model + ')' : ''}.`;
  if (n.t === 'dep') return `Position O / I / déclenché${[n.model, n.ir].filter(Boolean).length ? ' — ' + [n.model, n.ir].filter(Boolean).join(' · ') : ''}.`;
  if (n.t === 'sw') return 'Position.';
  return '';
}
function stageOf(n) {
  if (n.t === 'src') return 'SRC';
  if (n.t === 'tr') return 'TR:' + n.id;
  return n.board || n.id;
}
function vFiche(id) {
  let n = NODE[id], b0 = null;
  if (!n && BOARD[id]) { b0 = BOARD[id]; const h = (b0.halves || []).find(h => NODE[h.id] && (UP[h.id] || []).length) || (b0.halves || [])[0]; n = h ? NODE[h.id] : null; }
  if (!n) { VIEW().innerHTML = `<h1>Fiche détaillée</h1><p class="muted">Élément introuvable.</p>${footer()}`; return; }
  const title = b0 ? b0.name : dn(n), path = bestPath(n.id);
  const evidence = b0?.supplyEvidence || BOARD[n.board]?.supplyEvidence;
  let chainHTML = evidence ? `<p><b>Origine indiquée par plaque :</b> ${esc(evidence.text)}</p><p class="src">${esc(evidence.src)} · raccordement à confirmer ; aucune liaison électrique ajoutée à la simulation.</p>` : '<p class="muted">Aucune alimentation amont documentée.</p>';
  if (path) {
    const seq = path.slice().reverse(), stages = [];
    seq.forEach(x => { const nx = NODE[x], k = stageOf(nx); if (!stages.length || stages[stages.length - 1].k !== k) stages.push({ k, items: [] }); stages[stages.length - 1].items.push(nx); });
    chainHTML = stages.map((s, i) => {
      const bb = s.items[0].board && BOARD[s.items[0].board];
      const head = s.k === 'SRC' ? 'Source' : s.k.startsWith('TR:') ? 'Transformateur' : bb ? bb.name : short(s.items[0]);
      const loc = bb ? locChain(bb.loc).slice(1).map(l => l.name).join(' › ') : '';
      const links = bb ? `${planFor(bb.id) ? `<a href="#" data-go="#/plans/${planFor(bb.id)}/${bb.id}">📍 plan</a>` : ''} ${bb.facade ? `<a href="#" data-go="#/b/${bb.id}">▦ façade</a>` : ''}` : '';
      return `<div class="fstage"><div class="fnum">${i + 1}</div><div class="grow"><div class="row" style="justify-content:space-between"><b>${esc(head)}</b><span class="small muted">${esc(loc)} ${links}</span></div>
        ${s.items.filter(x => x.t !== 'bus' || s.items.length === 1 || !(bb && bb.kind === 'HTA')).map(x => { const st = SW.has(x.t) && !closed0(x.id) ? 'off' : 'on';
          return `<div class="li" data-open="${x.id}" style="padding:6px 4px"><span class="dot ${st}"></span><div class="grow"><div>${dev(x)}${x.conf && x.conf !== 'confirme' ? ' ' + confPill(x.conf) : ''}</div><div class="small">${esc(checkText(x))}</div></div></div>`; }).join('')}</div></div>`;
    }).join('<div class="farrow">▼</div>');
  }
  if (path && evidence) chainHTML += `<p class="src">Plaque complémentaire : ${esc(evidence.text)} · ${esc(evidence.src)} · correspondance à confirmer.</p>`;
  if (n.documentaryOnly) chainHTML = `<p><b>Repère documentaire — raccordement à confirmer.</b></p><p>${esc(n.note || '')}</p><p class="src">${esc(n.src || '')}</p>`;
  const pk = (path || []).join('>'), seen = new Set();
  const altHTML = upPaths(n.id, 16).filter(p => p.join('>') !== pk && p.some(x => SW.has(NODE[x].t) && !closed0(x))).map(p => {
    const off = p.filter(x => SW.has(NODE[x].t) && !closed0(x)), k = off.join('|'); if (seen.has(k)) return ''; seen.add(k);
    const tr = p.map(x => NODE[x]).find(x => x.t === 'tr');
    return `<div class="li" style="cursor:default"><span>↺</span><div class="grow">Par ${off.map(x => `<a href="#" data-open="${x}">${esc(dn(NODE[x]))}</a>`).join(' + ')}${tr ? ` — depuis <b>${esc(dn(tr))}</b>` : ''} — ${esc(short(NODE[p[p.length - 1]]))}</div></div>`; }).filter(Boolean).slice(0, 6).join('');
  const ds = downstream(n.id).map(x => NODE[x]);
  const subBoards = [...new Set(ds.map(x => x.board).filter(bid => bid && bid !== n.board && BOARD[bid]))];
  const trs = path ? path.map(x => NODE[x]).filter(x => x.t === 'tr') : [];
  const keyHTML = (path || []).map(x => NODE[x]).filter(x => x.uni && x.uni.keys && x.uni.keys.length).map(c => `<div class="small" style="margin:4px 0"><b>${esc(dn(c))}</b> : ${c.uni.keys.map(k => `${esc(k.name)}${k.code ? ' (' + esc(k.code) + ')' : ''} — ${esc(k.where)}`).join(' · ')}</div>`).join('') +
    trs.filter(t => t.uni).map(t => `<div class="small" style="margin:4px 0"><b>${esc(dn(t))}</b> : ${t.uni.tkeys ? 'clés transformateur ' + esc(t.uni.tkeys) + ' · ' : ''}clé disjoncteur BT ${esc(t.uni.btkeys || '—')}</div>`).join('');
  const bus = n.t === 'bus' ? n.id : busOf(n.id), busBoard = bus && NODE[bus] && boardOf(NODE[bus]);
  const procs = D.procs.filter(p => (path || []).some(x => p.ents.includes(x)) || (busBoard && p.board === busBoard.id));
  VIEW().innerHTML = `<div class="fiche">
  <div class="row noprint" style="margin-top:10px"><button class="btn" data-go="#/courant/${id}">⚡ Fiche de dépannage</button><button class="btn ghost" onclick="window.print()">🖨️ Imprimer</button></div>
  <div class="fhead"><div><div class="small muted">FICHE DÉTAILLÉE</div><h1 style="margin:4px 0">${esc(title)}</h1><div class="small">${esc(whereText(n))}</div></div></div>
  ${n.photoReading?`<section class="card glass"><h3>Lecture photographique détaillée</h3><p>${esc(n.photoReading.label)}${n.photoReading.rep?' · '+esc(n.photoReading.rep):''}</p><p class="src">${esc(n.photoReading.src)}</p><p>Libellé historique conservé pour le recoupement.</p></section>`:''}
  ${n.rep||n.visibleMarking?`<p>Repère lu : ${esc(n.rep || 'non lisible')}${n.visibleMarking?' · marquage visible '+esc(n.visibleMarking):''}</p>`:''}
  ${typeof projectImportHTML === 'function' ? projectImportHTML(b0 || BOARD[n.board]) : ''}<h2>De quoi dépend-il ? (source → ${esc(title)})</h2><div class="card glass">${chainHTML}</div>
  <h2>Autres chemins présents dans les documents <span class="small muted">(théoriques : disponibilité, charge et conditions non vérifiées)</span></h2><div class="card glass">${altHTML || '<p class="muted small">Aucun autre chemin documenté.</p>'}</div>
  <h2>Ce qui dépend de lui</h2><div class="card glass">${subBoards.length ? `<p class="small">Tableaux en aval : ${subBoards.map(bid => `<a href="#" data-go="#/courant/${bid}">${esc(BOARD[bid].name)}</a>`).join(' · ')}</p>` : ''}<p class="small">${ds.filter(x => x.t === 'dep').length ? ds.filter(x => x.t === 'dep').length + ' départ(s) en aval.' : 'Récepteur final.'}</p></div>
  <h2>Clés d’interverrouillage</h2><div class="card glass">${keyHTML || '<p class="muted small">Aucune clé documentée.</p>'}<p class="src">${esc(D.keylegend || '')}</p></div>
  <h2>Procédures</h2><div class="card glass">${procs.map(p => `<div class="li" data-open="proc:${p.id}"><span>${p.steps.length ? '📘' : '⏳'}</span><div class="grow">${esc(p.title)}<div class="src">${esc(p.status)}</div></div></div>`).join('') || '<p class="muted small">Aucune procédure transmise.</p>'}
    <p class="src">Sources : ${esc([...new Set((path || []).map(x => NODE[x].src).filter(Boolean))].slice(0, 6).join(' · '))}</p></div>
  ${footer()}</div>`;
}
