function planSVG(p, opts = {}) {
  const items = p.items, boxes = items.filter(i => i.k === 'box');
  let s = '', links = '', walls = '';
  const anchor = (a, b) => { const ax = a.x + a.w / 2, ay = a.y + a.h / 2, bx = b.x + b.w / 2, by = b.y + b.h / 2;
    if (Math.abs(by - ay) * a.w > Math.abs(bx - ax) * a.h) return [Math.max(a.x + 6, Math.min(a.x + a.w - 6, ax + (bx - ax) * .25)), by > ay ? a.y + a.h : a.y];
    return [bx > ax ? a.x + a.w : a.x, ay]; };
  // chaque TGBT est scindé en deux demi-jeux de barres, chacun alimenté par son transformateur : A | couplage | B
  // (côté A placé du côté du transformateur xA sur le plan)
  const split = {};
  boxes.forEach(b => {
    if (!b.ref || !BOARD[b.ref] || split[b.ref]) return; const s = srcSet(b.ref); if (!s) return;
    const trBox = id => boxes.find(x => x.ref === id), ta = trBox(s.sa.id), tb = trBox(s.sb.id);
    const aLeft = !(ta && tb) || ta.x + ta.w / 2 <= tb.x + tb.w / 2, g = Math.max(8, Math.min(14, b.w * .1)), hw = (b.w - g) / 2;
    split[b.ref] = { s, box: b, g, rA: { x: aLeft ? b.x : b.x + hw + g, y: b.y, w: hw, h: b.h, bus: s.ba }, rB: { x: aLeft ? b.x + hw + g : b.x, y: b.y, w: hw, h: b.h, bus: s.bb } };
  });
  const halfFor = (boardRef, otherRef) => {  // demi-tableau concerné par une liaison avec otherRef
    const sp = split[boardRef]; if (!sp) return null; const s = sp.s;
    if (otherRef === s.sa.id) return sp.rA; if (otherRef === s.sb.id) return sp.rB;
    const d = D.nodes.find(n => n.t === 'dep' && n.board === boardRef && (n.feeds === otherRef || (DOWN[n.id] || []).some(e => NODE[e.b].board === otherRef)));
    const bu = d && busOf(d.id); return bu === s.ba ? sp.rA : bu === s.bb ? sp.rB : null;
  };
  if (PLAN_LINKS) {
    const refd = boxes.filter(b => b.ref), done = new Set();
    refd.forEach(a => refd.forEach(b => {
      if (a === b || a.ref === b.ref) return; const k = a.ref + '>' + b.ref; if (done.has(k)) return;
      const hta = BOARD[a.ref] && BOARD[a.ref].kind === 'HTA';
      if ((PLAN_LINKS === 'bt' && hta) || (PLAN_LINKS === 'hta' && !hta)) return;
      if (!relation(a.ref, b.ref)) return; done.add(k);
      const A2 = halfFor(a.ref, b.ref) || a, B2 = halfFor(b.ref, a.ref) || b;
      const [x1, y1] = anchor(A2, B2), [x2, y2] = anchor(B2, A2);
      const la = A2.bus ? isLive(A2.bus) : refLive(a.ref), lb = B2.bus ? isLive(B2.bus) : refLive(b.ref), live = la !== false && lb !== false && (la || lb);
      const my = (y1 + y2) / 2;
      // 20 kV (tableau HTA → transfo) en violet épais, BT (transfo → TGBT / tableau) en vert ; rouge si coupé en simulation
      const col = !live ? '#e5484d' : hta ? '#7c5cff' : '#12b76a';
      links += `<path d="M${x1} ${y1}C${x1} ${my} ${x2} ${my} ${x2} ${y2}" fill="none" stroke="${col}" stroke-width="${hta ? 2.4 : 1.8}" opacity=".85" ${live ? 'class="flow" style="stroke-dasharray:6 5"' : 'stroke-dasharray="3 4"'} marker-end="url(#${hta ? 'ah' : 'ae'})"><title>${esc(a.t)} → ${esc(b.t)} (${hta ? '20 kV' : 'BT'} — liaison électrique documentée)</title></path>`;
    }));
    // arrivée 20 kV du poste de livraison CNR / EDF sur le tableau 20 kV de la sous-station
    boxes.filter(x => x.ref && BOARD[x.ref] && BOARD[x.ref].kind === 'HTA' && x.ref !== 'KV6').forEach(x => {
      // arrive par le bas du tableau (zone libre sur les plans), pour ne pas croiser les liaisons vers les transformateurs
      const live = refLive(x.ref) !== false, cx = x.x + x.w / 2, yb = x.y + x.h;
      links += `<g><path d="M${cx} ${yb + 50}V${yb + 2}" stroke="${live ? '#7c5cff' : '#e5484d'}" stroke-width="3" ${live ? 'class="flow" style="stroke-dasharray:6 5"' : ''} marker-end="url(#ah)"/>
        <text x="${cx}" y="${yb + 64}" font-size="10" font-weight="800" fill="#7c5cff" text-anchor="middle">20 kV ← poste de livraison CNR / EDF</text></g>`;
    });
  }
  const seg = it => { let x1 = it.x, y1 = it.y, x2 = it.x + it.w, y2 = it.y + it.h; if (it.fh) [x1, x2] = [x2, x1]; if (it.fv) [y1, y2] = [y2, y1]; return [x1, y1, x2, y2]; };
  items.forEach((it, idx) => {
    switch (it.k) {
      case 'title': s += `<text x="${it.x}" y="${it.y + 28}" font-size="24" font-weight="800" fill="currentColor">${esc(it.t)}</text>`; return;
      case 'label': s += `<text x="${it.x + it.w / 2}" y="${it.y + 11}" font-size="11" font-weight="700" letter-spacing="1.5" text-anchor="middle" fill="currentColor" opacity=".55">${esc(it.t)}</text>`; return;
      case 'entre': s += `<text transform="translate(${it.x + it.w / 2},${it.y + it.h / 2}) rotate(-90)" font-size="15" text-anchor="middle" font-weight="800" letter-spacing="2" fill="currentColor">ENTRÉE</text>`; return;
      case 'door': walls += `<rect x="${it.x - 1}" y="${it.y}" width="${Math.max(it.w, 3) + 2}" height="${it.h}" fill="#3b82f6"/><text x="${it.x + 10}" y="${it.y + it.h / 2}" font-size="8" fill="#3b82f6" font-weight="700">porte</text>`; return;
      case 'opening': walls += `<g><rect x="${it.x - 5}" y="${it.y}" width="10" height="${it.h}" fill="var(--bg)" opacity=".95"/><path d="M${it.x - 7} ${it.y}h14M${it.x - 7} ${it.y + it.h}h14" stroke="currentColor" stroke-width="2"/>
        <text x="${it.x + 9}" y="${it.y + it.h / 2 + 3}" font-size="8.5" fill="currentColor" font-weight="700">ouverture ≈ 1 m</text></g>`; return;
      case 'wall': { const [x1, y1, x2, y2] = seg(it); walls += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="currentColor" stroke-width="${it.partition ? 1.4 : 3}" ${it.partition ? 'stroke-dasharray="0"' : ''} stroke-linecap="square" opacity="${it.partition ? .7 : .85}"><title>${it.partition ? 'Cloison fine' : 'Mur'}</title></line>`; return; }
      // traits orange (face avant visible) et doubles flèches orange (vis-à-vis) : annotations de lecture du plan fournies par l'exploitant,
      // non affichées (demande utilisateur) ; les vis-à-vis restent exploités dans la fiche de chaque armoire (facingOf)
      case 'face': case 'vis': return;
      case 'box': {
        // pas de halo vert : cadre neutre ; rouge uniquement si coupé dans la simulation
        const lv = it.ref ? refLive(it.ref) : null;
        const fill = lv === false ? 'rgba(229,72,77,.12)' : 'rgba(127,140,133,.07)';
        const stroke = lv === false ? '#e5484d' : 'currentColor';
        const fs = Math.max(5.5, Math.min(11, it.w / 9, it.h / 3.2));
        const isTr = it.ref && NODE[it.ref] && NODE[it.ref].t === 'tr';
        const sp = it.ref && split[it.ref] && split[it.ref].box === it ? split[it.ref] : null;
        const txt = (r, t, f) => { const ls = wrapText(t, Math.max(4, Math.floor(r.w / (f * .58)))).slice(0, Math.max(1, Math.floor(r.h / (f * 1.15))));
          return ls.map((l, i) => `<text x="${r.x + r.w / 2}" y="${r.y + r.h / 2 + (i - (ls.length - 1) / 2) * f * 1.15 + f * .35}" font-size="${f}" text-anchor="middle" fill="currentColor" font-weight="${it.ref ? 700 : 500}">${esc(l)}</text>`).join(''); };
        let g;
        if (sp) {  // TGBT scindé : deux demi-jeux de barres et le couplage entre les deux
          const half = (r, lab) => { const on = isLive(r.bus); return `<rect x="${r.x}" y="${r.y}" width="${r.w}" height="${r.h}" rx="2.5" fill="${on ? 'rgba(127,140,133,.07)' : 'rgba(229,72,77,.12)'}" stroke="${on ? 'currentColor' : '#e5484d'}" stroke-width="2"/>${txt(r, lab, Math.max(5.5, Math.min(11, r.w / 7, r.h / 3.2)))}`; };
          const cx = Math.min(sp.rA.x, sp.rB.x) + sp.rA.w + sp.g / 2, cy = it.y + it.h / 2, q = Math.min(sp.g - 2, 9), closed = isClosed(sp.s.qc.id);
          g = `${half(sp.rA, sp.s.la)}${half(sp.rB, sp.s.lb)}
            <path d="M${cx - sp.g / 2} ${cy}H${cx + sp.g / 2}" stroke="currentColor" stroke-width="1.5" opacity=".7"/>
            <rect x="${cx - q / 2}" y="${cy - q / 2}" width="${q}" height="${q}" rx="1" fill="${closed ? 'currentColor' : 'var(--bg)'}" stroke="currentColor" stroke-width="1.3"><title>Couplage ${closed ? 'fermé' : 'ouvert'} (simulation)</title></rect>
            ${closed ? '' : `<path d="M${cx - q / 2 + 1.5} ${cy + q / 2 - 1.5}L${cx + q / 2 - 1.5} ${cy - q / 2 + 1.5}" stroke="currentColor" stroke-width="1.2"/>`}
            <text x="${cx}" y="${it.y + it.h + 9}" font-size="6.5" text-anchor="middle" fill="currentColor" opacity=".7">couplage</text>`;
        } else {
          g = `<rect x="${it.x}" y="${it.y}" width="${it.w}" height="${it.h}" rx="2.5" fill="${fill}" stroke="${stroke}" stroke-width="${it.ref ? 1.8 : 1.2}" ${it.conf && it.conf !== 'confirme' ? 'stroke-dasharray="5 3"' : ''} opacity="${it.ref ? .9 : .6}"/>
          ${isTr ? `<g opacity=".55" fill="none" stroke="${stroke}" stroke-width="1.6"><circle cx="${it.x + it.w - 12}" cy="${it.y + 10}" r="5"/><circle cx="${it.x + it.w - 12}" cy="${it.y + 17}" r="5"/></g>` : ''}
          ${txt(it, it.t, fs)}`;
        }
        s += it.ref ? `<g class="hit" data-id="${it.ref}" data-pi="${idx}"><title>${esc(it.t)}${it.note ? ' — ' + esc(it.note) : ''}</title>${g}<rect class="hl" x="${it.x - 3}" y="${it.y - 3}" width="${it.w + 6}" height="${it.h + 6}" rx="5"/></g>`
          : `<g data-pi="${idx}"><title>${esc(it.t)} — ${esc(it.note || '')}</title>${g}</g>`;
        return;
      }
    }
  });
  return `<svg viewBox="0 ${p.y0 || 40} ${p.w} ${p.h - (p.y0 || 40) + 10}" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system,Segoe UI,Arial,sans-serif">
    <defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L10 5L0 10z" fill="#7c5cff"/></marker><marker id="ae" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L10 5L0 10z" fill="#0a9f5a"/></marker></defs>${walls}${links}${s}</svg>`;
}
function facingAt(p, idx) {
  const a = p.items[idx]; const x = a.x + a.w / 2, y1 = Math.min(a.y, a.y + a.h), y2 = Math.max(a.y, a.y + a.h), xa = Math.min(a.x, a.x + a.w), xb = Math.max(a.x, a.x + a.w);
  const boxes = p.items.filter(i => i.k === 'box');
  const vert = Math.abs(a.h) >= Math.abs(a.w);
  let A, B;
  if (vert) {
    const col = boxes.filter(b => b.x - 4 <= x && x <= b.x + b.w + 4);
    A = col.filter(b => b.y + b.h <= y1 + 6).sort((m, n) => (n.y + n.h) - (m.y + m.h))[0];
    B = col.filter(b => b.y >= y2 - 6).sort((m, n) => m.y - n.y)[0];
  } else {
    const yy = a.y + a.h / 2, row = boxes.filter(b => b.y - 4 <= yy && yy <= b.y + b.h + 4);
    A = row.filter(b => b.x + b.w <= xa + 6).sort((m, n) => (n.x + n.w) - (m.x + m.w))[0];
    B = row.filter(b => b.x >= xb - 6).sort((m, n) => m.x - n.x)[0];
  }
  return [A, B].filter(Boolean);
}
// armoires situées en face d'un équipement du plan (d'après les doubles flèches du plan, non dessinées)
function facingOf(p, it) {
  const out = new Set();
  p.items.forEach((a, idx) => { if (a.k !== 'vis') return; const f = facingAt(p, idx); if (f.includes(it)) f.forEach(b => { if (b !== it && !(b.ref && b.ref === it.ref)) out.add(b); }); });
  return [...out];
}
function planItemHTML(it) {
  if (!it.ref) return `<div class="li"><span>▭</span><div class="grow"><b>${esc(it.t)}</b><div class="src">${esc(it.note || '')}</div></div></div>`;
  const b = BOARD[it.ref], n = NODE[it.ref], lv = refLive(it.ref);
  return `<div class="li" ${b ? `data-go="#/b/${it.ref}"` : `data-open="${it.ref}"`}><span class="dot ${lv === null ? 'unk' : lv ? 'on' : 'off'}"></span><div class="grow"><b>${esc(it.t)}</b><div class="src">→ ${esc(b ? b.name : n.label)}${b && b.facade ? ' · façade disponible' : ''}${it.note ? ' — ' + esc(it.note) : ''}</div></div>${confPill(it.conf)}</div>`;
}
/* Onglets : poste de livraison puis sous-stations. Les autres locaux (chaufferie, STEP) et les armoires du site n'ont pas d'onglet :
   ils sont rattachés au tableau qui les alimente (« Armoires alimentées depuis la sous-station »), leur plan reste accessible depuis là. */
const PLAN_TABS = [['PLAN_PDL', 'PDL CNR / EDF'], ['PLAN_SS1', 'Sous-station 1'], ['PLAN_SS2', 'Sous-station 2']];
function planSource(p) {  // plan secondaire : chaîne de tableaux depuis le dernier tableau situé en sous-station jusqu'au local
  for (const it of p.items.filter(i => i.ref && BOARD[i.ref])) {
    const h = (BOARD[it.ref].halves || []).find(x => NODE[x.id] && (UP[x.id] || []).length); if (!h) continue;
    const path = bestPath(h.id); if (!path) continue;
    const chain = [...new Set(path.slice().reverse().map(x => NODE[x].board).filter(Boolean))];
    let iTop = -1; chain.forEach((bid, i) => { if (['PLAN_SS1', 'PLAN_SS2'].includes(planFor(bid))) iTop = i; });
    if (iTop >= 0) return { tab: planFor(chain[iTop]), chain: chain.slice(iTop) };
  }
  return null;
}
function pdlSVG() {
  const f = D.facades.PL20, cells = f.cells, CW = 104, X0 = 84, Y0 = 170, n = cells.length;
  const col = id => (SW.has(NODE[id].t) && !isClosed(id) ? '#e5484d' : isLive(id) ? '#12b76a' : '#e5484d');
  const cx = id => { const i = cells.findIndex(c => c.node === id); return X0 + i * CW + CW / 2; };
  let s = `<text x="40" y="60" font-size="26" font-weight="800" fill="currentColor">POSTE DE LIVRAISON CNR / EDF</text>
    <rect x="${X0 - 24}" y="${Y0 - 24}" width="${n * CW + 48}" height="214" rx="10" fill="none" stroke="currentColor" stroke-width="3" opacity=".8"/>`;
  cells.forEach((c, i) => { const x = X0 + i * CW, nd = c.node && NODE[c.node];
    const lines = wrapText(c.label, 13).slice(0, 4);
    const g = `<rect x="${x + 4}" y="${Y0}" width="${CW - 8}" height="160" rx="6" fill="rgba(127,140,133,.08)" stroke="${nd ? col(nd.id) : 'currentColor'}" stroke-width="2"/>
      <text x="${x + CW / 2}" y="${Y0 + 22}" font-size="13" font-weight="800" text-anchor="middle" fill="currentColor">${esc(c.t)}</text>
      ${lines.map((l, k) => `<text x="${x + CW / 2}" y="${Y0 + 52 + k * 16}" font-size="11.5" text-anchor="middle" fill="currentColor">${esc(l)}</text>`).join('')}
      ${c.ref ? `<text x="${x + CW / 2}" y="${Y0 + 148}" font-size="10" text-anchor="middle" fill="currentColor" opacity=".6">${esc(c.ref)}</text>` : ''}`;
    s += nd ? `<g class="hit" data-id="${nd.id}"><title>${esc(nd.label)}</title>${g}<rect class="hl" x="${x}" y="${Y0 - 4}" width="${CW}" height="168" rx="8"/></g>` : g; });
  // arrivées réseau
  [['PL_B_ARR', 'SRC_CNR', 'Réseau CNR (normal)'], ['PL_A_ARR', 'SRC_EDF', 'Réseau EDF (secours)']].forEach(([id, src, lab]) => { if (!NODE[id]) return; const x = cx(id);
    s += `<g class="hit" data-id="${src}"><path d="M${x} 90V${Y0 - 2}" stroke="${col(src)}" stroke-width="5" ${isLive(src) ? 'class="flow" style="stroke-dasharray:8 6"' : ''}/><path d="M${x - 9} ${Y0 - 14}l9 12l9 -12" fill="none" stroke="${col(src)}" stroke-width="4"/>
      <text x="${x}" y="82" font-size="15" font-weight="800" text-anchor="middle" fill="currentColor">${esc(lab)}</text></g>`; });
  // départs vers les sous-stations (secours EDF : A04 → A1 / A3 ; normal CNR : B01 → A2 / A4)
  const SS = [['PLAN_SS1', 'Sous-station 1', 'Tableau 20 kV TR 7 / TR 9 / Boosting', 'SS2_20', 120], ['PLAN_SS2', 'Sous-station 2', 'Tableau 20 kV TR 1 à 6', 'SS1_20', 560]];
  SS.forEach(([pid, name, sub, bid, x]) => {
    s += `<g class="hit" data-id="${pid}"><rect x="${x}" y="470" width="320" height="96" rx="12" fill="rgba(124,92,255,.08)" stroke="#7c5cff" stroke-width="2.5"/>
      <text x="${x + 160}" y="506" font-size="19" font-weight="800" text-anchor="middle" fill="currentColor">${esc(name)}</text>
      <text x="${x + 160}" y="532" font-size="13" text-anchor="middle" fill="currentColor" opacity=".75">${esc(sub)}</text>
      <text x="${x + 160}" y="554" font-size="12" text-anchor="middle" fill="#7c5cff" font-weight="700">ouvrir le plan ›</text><rect class="hl" x="${x - 4}" y="466" width="328" height="104" rx="14"/></g>`;
    [['PL_B01', 'normale'], ['PL_A04', 'secours']].forEach(([cb, kind], k) => { if (!NODE[cb]) return; const x1 = cx(cb), x2 = x + 100 + k * 120;
      s += `<path d="M${x1} ${Y0 + 162}C${x1} 400 ${x2} 400 ${x2} 468" fill="none" stroke="${col(cb)}" stroke-width="3" ${isClosed(cb) && isLive(cb) ? 'class="flow" style="stroke-dasharray:8 6"' : 'stroke-dasharray="4 5"'}><title>Arrivée ${kind} ${name}</title></path>
        <text x="${x2}" y="458" font-size="11" text-anchor="middle" fill="currentColor" opacity=".7">arrivée ${kind}</text>`; });
  });
  s += `<text x="40" y="610" font-size="12" fill="currentColor" opacity=".6">Schéma de principe d’après l’unifilaire : aucun plan ni photo du poste de livraison. Jamais CNR et EDF fermés ensemble ; bascule automatique sur manque CNR.</text>`;
  return `<svg viewBox="0 0 1000 630" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system,Segoe UI,Arial,sans-serif">${s}</svg>`;
}
// armoires alimentées depuis un plan (sous-station), regroupées par tableau source ; arborescence repliable vers les locaux et armoires du site
function attachHTML(p) {
  const inPlan = [...new Set(p.items.filter(i => i.ref && BOARD[i.ref]).map(i => i.ref))];
  const groups = inPlan.map(bid => ({ bid, kids: arbreKids(bid, inPlan).filter(k => k.board) })).filter(g => g.kids.length)
    .sort((a, b) => BOARD[a.bid].name.localeCompare(BOARD[b.bid].name, 'fr', { numeric: true }));
  if (!groups.length) return '';
  return `<h2>Armoires alimentées depuis la ${esc(p.title.toLowerCase())}</h2>
    <p class="small muted" style="margin-top:-6px">Locaux et armoires du site rattachés à leur tableau source (chaufferie, STEP, ateliers…). 📍 ouvre le plan du local quand il existe.</p>
    ${groups.map(g => `<details class="card glass tree" style="margin-bottom:8px" open><summary><b>${esc(BOARD[g.bid].name)}</b> <span class="small muted">alimente ${g.kids.length} armoire${g.kids.length > 1 ? 's' : ''}</span></summary>
      <div class="tkids" style="margin-top:6px">${g.kids.map(k => arbreBoard(k.board, 3, inPlan.concat(g.bid), tVia(k))).join('')}</div></details>`).join('')}`;
}
function vPlans(pid, focus, selected) {
  if (pid === 'PLAN_SS1G' || pid === 'PLAN_SS1D') pid = 'PLAN_SS1';
  if (!pid || pid === 'PLAN_PDL') {
    VIEW().innerHTML = `<h1 style="margin-top:14px">Plans d’implantation</h1>
    <div class="seg glass" style="margin-bottom:10px">${PLAN_TABS.map(([id, t]) => `<button data-p="${id}" class="${id === 'PLAN_PDL' ? 'on' : ''}">${esc(t)}</button>`).join('')}</div>
    <div id="pv"></div>${footer()}`;
    $$$('[data-p]').forEach(b => b.onclick = () => location.hash = '#/plans/' + b.dataset.p);
    window.__planCur = 'PLAN_PDL';
    mountViewer($('#pv'), pdlSVG(), { focus, legend: '<span style="color:#12b76a">━ sous tension</span><span style="color:#e5484d">┅ ouvert / hors tension (simulation)</span><span>Touchez une cellule ou une sous-station</span>',
      onClick: id => { if (id.startsWith('PLAN_')) location.hash = '#/plans/' + id; else openEntity(id); } });
    return;
  }
  const p = D.plans.find(x => x.id === pid) || D.plans.find(x => x.id === 'PLAN_SS2');
  const loc = D.loc[p.loc], top = PLAN_TABS.some(([id]) => id === p.id), src = top ? null : planSource(p);
  window.__planCur = p.id;
  VIEW().innerHTML = `<h1 style="margin-top:14px">Plans d’implantation</h1>
  <div class="seg glass" style="margin-bottom:10px">${PLAN_TABS.map(([id, t]) => `<button data-p="${id}" class="${id === p.id || (src && src.tab === id) ? 'on' : ''}">${esc(t)}</button>`).join('')}</div>
  ${src ? `<div class="crumbs" style="margin:0 0 10px"><a data-go="#/plans/${src.tab}">${esc(PLAN_TABS.find(t => t[0] === src.tab)[1])}</a>${src.chain.map(bid => `<i>›</i><a data-go="#/b/${bid}">${esc(BOARD[bid].name)}</a>`).join('')}<i>›</i><a>${esc(p.title)}</a></div>` : ''}
  <div class="row" style="margin-bottom:8px"><div class="seg glass"><button id="lk1" class="${PLAN_LINKS ? 'on' : ''}">Liaisons 20 kV → transfos → TGBT</button><button id="lk0" class="${PLAN_LINKS ? '' : 'on'}">Implantation seule</button></div></div>
  <div class="row small" style="margin-bottom:10px;gap:16px"><span><b style="color:#7c5cff">━▸</b> 20 kV : tableau 20 kV → transformateur</span><span><b style="color:#12b76a">┈▸</b> BT : transformateur → TGBT → tableaux</span><span><b style="color:#e5484d">┈</b> coupé (simulation)</span></div>
  ${parcoursPlanActions(focus, selected)}
  <div id="pv"></div>
  ${top ? attachHTML(p) : ''}
  <details class="card glass" style="margin-top:14px"><summary><b>Équipements du plan et remarques</b></summary>
    ${p.note ? `<p class="small">${esc(p.note)}</p>` : ''}${loc && loc.note ? `<p class="small">⚠️ ${esc(loc.note)}</p>` : ''}
    <div class="list">${p.items.filter(i => i.k === 'box').sort((a, b) => (b.ref ? 1 : 0) - (a.ref ? 1 : 0)).map(planItemHTML).join('')}</div>
    <p class="src">Source : ${esc(p.src)} — redessiné en vectoriel, proportions du document, non coté. Les liaisons sont électriques, pas le tracé des câbles.</p></details>${footer()}`;
  $$$('[data-p]').forEach(b => b.onclick = () => location.hash = '#/plans/' + b.dataset.p);
  $('#lk1').onclick = () => { PLAN_LINKS = 'all'; vPlans(p.id); }; $('#lk0').onclick = () => { PLAN_LINKS = false; vPlans(p.id); };
  mountViewer($('#pv'), planSVG(p), {
    focus, legend: '<span>TGBT 1A ▢ TGBT 1B : demi-tableaux et couplage (▢ ouvert · ■ fermé)</span><span style="color:#e5484d">■ coupé (simulation)</span><span>┅ emplacement probable</span>',
    onClick: (id, g) => {
      const it = p.items[+g.dataset.pi], vis = facingOf(p, it);
      const visHTML = vis.length ? `<div class="blk"><h4>En face, de l’autre côté de l’allée</h4><div class="list">${vis.map(planItemHTML).join('')}</div></div>` : '';
      if (BOARD[id]) { openSheet(`<span class="pill k">${esc(BOARD[id].kind)}</span>${confPill(it.conf)}<h2>${esc(BOARD[id].name)}</h2><div class="src">Sur le plan : « ${esc(it.t)} »${it.note ? ' — ' + esc(it.note) : ''}</div>`,
        `<div class="row" style="margin:10px 0"><button class="btn" data-go="#/b/${id}">Ouvrir le tableau${BOARD[id].facade ? ' et sa façade' : ''}</button><button class="btn" data-go="#/courant/${id}">⚡ Remettre le courant</button></div>${visHTML}${(BOARD[id].halves || []).filter(h => NODE[h.id]).map(h => `<div class="blk"><h4>${esc(h.label)}</h4>${sourcesBlock(h.id)}</div>`).join('')}`); }
      else openEntity(id);
    }
  });
}
