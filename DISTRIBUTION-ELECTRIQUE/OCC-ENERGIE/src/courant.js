/* ======================================================================= ⚡ Dépannage — parcours guidé en 3 touches
   1. quel équipement ? (tableau, départ, transformateur, cellule)  2. que constatez-vous ?  3. fiche (statut en tête) + détails repliés.
   Le parcours ne dépend pas de l'état simulé : il part de la configuration normale documentée. */
function vCourant(id, sit) {
  if (!id) return courantChoose();
  if (!NODE[id] && !BOARD[id]) return courantChoose();
  const sits = situations(id);
  const n = NODE[id], b = BOARD[id] || (n && boardOf(n));
  const name = BOARD[id] ? BOARD[id].name : dn(n);
  const where = [b && locChain(b.loc).slice(1).map(l => l.name).join(' · '), !BOARD[id] && b ? b.name : '', n && n.case ? 'case ' + n.case : ''].filter(Boolean).join(' · ');
  const chosen = sit ? sits.find(s => s.sit === sit) : sits.length === 1 ? sits[0] : null;
  if (!chosen) {
    const pl = b && planFor(b.id), fid = n && facadeFor(n.id);
    const whereBtn = fid ? `#/b/${boardForFacade(fid)}/f/${n.id}` : pl ? `#/plans/${pl}/${b.id}` : b ? `#/b/${b.id}` : null;
    VIEW().innerHTML = `<div class="crumbs" style="margin-top:12px"><a data-go="#/courant">⚡ Dépannage</a><i>›</i><a>${esc(name)}</a></div>
    <h1 style="margin-bottom:2px">${esc(name)}</h1><div class="moloc">📍 ${esc(where || 'Localisation non documentée')}${n ? ` <span class="pill">${esc(TYPE[n.t] || '')}</span>` : ''}</div>
    <div class="row quick" style="margin:10px 0 4px">${whereBtn ? `<button class="btn ghost" data-go="${whereBtn}">📍 Où il se trouve</button>` : ''}<button class="btn ghost" id="caval">⬇ Ce qu’il alimente</button><button class="btn ghost" data-go="#/details/${id}">📄 Fiche détaillée</button></div>
    ${(() => { const s = b && srcSet(b.id); return s ? `<div class="synrow" style="justify-content:flex-start">${synMini(s, { ta: true, tb: true, qa: true, qb: true, qc: false }, `En temps normal : ${esc(b.name)} est scindé en deux — ${esc(s.la)} sur ${esc(dn(s.sa))}, ${esc(s.lb)} sur ${esc(dn(s.sb))}, couplage ouvert`)}</div>` : ''; })()}
    <h2>Que constatez-vous ?</h2>
    ${sits.length ? `<div class="choices">${sits.map(s => `<button class="choice glass ${s.minor ? 'minor' : ''}" data-go="#/courant/${id}/${s.sit}"><b>${esc(s.t)}</b><span>${esc(s.d)}</span></button>`).join('')}</div>`
      : '<div class="card glass"><p>Aucune fiche possible : l’alimentation de cet élément n’est pas documentée.</p></div>'}
    ${courantDetails(id)}${footer()}`;
    $('#caval').onclick = () => courantAval(id);
    return;
  }
  const mo = chosen.mo();
  VIEW().innerHTML = `<div class="crumbs noprint" style="margin-top:12px"><a data-go="#/courant">⚡ Dépannage</a><i>›</i><a data-go="#/courant/${id}">${esc(name)}</a><i>›</i><a>${esc(chosen.t)}</a></div>
    ${moSheetHTML(mo)}
    ${courantDetails(mo.at ? mo.at.id : id)}${footer()}`;
  $('[data-mosim]').forEach(x => x.onclick = () => moSim(mo));
}
/* ce qu'alimente un équipement ou un tableau (aval documenté) */
function courantAval(id) {
  const roots = BOARD[id] ? (BOARD[id].halves || []).map(h => h.id).filter(h => NODE[h]) : [id];
  const ds = [...new Set(roots.flatMap(r => downstream(r)))].map(x => NODE[x]);
  const boards = [...new Set(ds.map(x => x.board).filter(x => x && x !== id && BOARD[x] && x !== (NODE[id] || {}).board))];
  const deps = ds.filter(x => x.t === 'dep'), loads = ds.filter(x => x.t === 'load');
  openSheet(`<span class="pill k">Aval documenté</span><h2>${esc(BOARD[id] ? BOARD[id].name : dn(NODE[id]))} alimente</h2>`,
    `${boards.length ? `<div class="blk"><h4>Tableaux en aval (${boards.length})</h4><div class="list">${boards.map(x => `<div class="li" data-go="#/courant/${x}"><span>▦</span><div class="grow">${esc(BOARD[x].name)}</div><span>›</span></div>`).join('')}</div></div>` : ''}
     ${deps.length ? `<div class="blk"><h4>Départs (${deps.length})</h4>${groupByBus(deps)}</div>` : ''}
     ${loads.length ? `<div class="blk"><h4>Récepteurs</h4><div class="list">${loads.map(liNode).join('')}</div></div>` : ''}
     ${!boards.length && !deps.length && !loads.length ? '<p class="muted">Aucun aval documenté (récepteur final ou liaison inconnue).</p>' : ''}
     <p class="small muted">Liaisons tirées des documents (unifilaire, classeur, plans, plaques) ; une liaison non documentée n’apparaît pas.</p>`);
}
function courantChoose() {
  const tg = D.boards.filter(b => b.kind === 'TGBT').sort((a, b) => a.name.localeCompare(b.name, 'fr', { numeric: true }));
  const hta = D.boards.filter(b => b.kind === 'HTA');
  const ts = D.boards.filter(b => b.kind !== 'TGBT' && b.kind !== 'HTA' && (situations(b.id).length)).sort((a, b) => a.name.localeCompare(b.name, 'fr', { numeric: true }));
  VIEW().innerHTML = `<h1 style="margin-top:14px">⚡ Dépannage</h1>
  <p class="sub">Quel équipement pose problème ? Tableau, départ, machine, transformateur ou cellule 20 kV.</p>
  <input class="f big" id="cq" type="search" autocomplete="off" placeholder="ex. Étuve 2, TR 6A, cellule TR 3B, 7K121, TS 44">
  <div id="cres" class="list" style="margin-top:8px"></div>
  <h2>TGBT</h2><div class="tiles">${tg.map(b => `<button class="tile glass" data-go="#/courant/${b.id}"><b>${esc(b.name)}</b><span>${esc((locChain(b.loc).slice(-1)[0] || {}).name || '')}</span></button>`).join('')}</div>
  <details class="card glass" style="margin-top:14px"><summary><b>Tableaux 20 kV / 6 kV</b> <span class="pill">${hta.length}</span></summary><div class="tiles" style="margin-top:10px">${hta.map(b => `<button class="tile glass" data-go="#/courant/${b.id}"><b>${esc(b.name)}</b></button>`).join('')}</div></details>
  <details class="card glass" style="margin-top:10px"><summary><b>Autres tableaux</b> <span class="pill">${ts.length}</span></summary><div class="tiles" style="margin-top:10px">${ts.map(b => `<button class="tile glass" data-go="#/courant/${b.id}"><b>${esc(b.name)}</b></button>`).join('')}</div></details>
  ${footer()}`;
  const inp = $('#cq'), box = $('#cres');
  inp.oninput = () => {
    const q = inp.value.trim(); if (!q) { box.innerHTML = ''; return; }
    let r = search(q, 16).filter(x => x.kind === 'board' || (x.kind === 'node' && NODE[x.id] && NODE[x.id].t !== 'src'));
    const ex = exactMatches(r, q); r = [...ex, ...r.filter(x => !ex.includes(x))].slice(0, 12);   // repère exact en premier
    box.innerHTML = (r.length > 1 && ex.length !== 1 ? '<p class="small muted" style="margin:0 0 6px">Plusieurs équipements correspondent : choisissez le bon.</p>' : '') +
      (r.map(x => { const nn = NODE[x.id], bb = x.kind === 'board' ? BOARD[x.id] : boardOf(nn);
      return `<div class="li glass" style="border-radius:14px;margin-bottom:6px" data-go="#/courant/${x.id}"><span class="pill ${ex.includes(x) ? 'g' : ''}">${esc(x.kind === 'board' ? 'Tableau' : TYPE[nn.t] || '')}</span><div class="grow"><b>${esc(x.kind === 'board' ? bb.name : dn(nn) || nn.label)}</b><div class="src">${esc([x.kind === 'board' ? '' : bb && bb.name, nn && nn.case ? 'case ' + nn.case : '', nn && nn.rep ? 'repère ' + nn.rep : ''].filter(Boolean).join(' · '))}</div></div><span>›</span></div>`; }).join('') || '<p class="muted">Aucun résultat.</p>');
  };
  inp.focus();
}
/* détails techniques repliés : chaîne d'alimentation complète + accès aux informations détaillées */
function courantDetails(id) {
  const p = NODE[id] ? bestPath(id) : (() => { const b = BOARD[id], h = b && (b.halves || []).find(x => NODE[x.id] && (UP[x.id] || []).length); return h ? bestPath(h.id) : null; })();
  return `<details class="card glass noprint" style="margin-top:16px"><summary><b>Détails techniques</b> <span class="small muted">chaîne d’alimentation, clés, sources</span></summary>
    ${p ? `<div class="small muted" style="margin:8px 0 4px">Chaîne d’alimentation normale (de la source à l’élément)</div>${pathHTML(p, 0, true)}` : '<p class="muted small">Alimentation amont non documentée.</p>'}
    <div class="row" style="margin-top:10px"><button class="btn ghost" data-go="#/details/${id}">Fiche détaillée (étage par étage, clés, procédures)</button><button class="btn ghost" data-go="#/depannage/${id}">Diagnostic documentaire</button>${NODE[id] ? `<button class="btn ghost" data-open="${id}">Fiche de l’appareil</button>` : `<button class="btn ghost" data-go="#/b/${id}">Tableau et façade</button>`}</div></details>`;
}
