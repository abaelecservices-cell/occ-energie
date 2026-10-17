/* ---------- Accueil : page de garde avec vue aérienne */
function zoneStatus(z) {
  if (!z.refs) return null;
  const st = z.refs.map(refLive).filter(x => x !== null);
  return st.length ? (st.every(Boolean) ? 'on' : st.some(Boolean) ? 'part' : 'off') : null;
}
function refLive(ref) {
  if (NODE[ref]) { if (!(UP[ref] || []).length && NODE[ref].t !== 'src') return null; return SW.has(NODE[ref].t) && !isClosed(ref) ? false : isLive(ref); }
  const b = BOARD[ref]; if (!b) return null;
  const hs = (b.halves || []).filter(h => NODE[h.id] && (UP[h.id] || []).length);
  if (hs.length) return hs.some(h => isLive(h.id));
  if ((b.halves || []).length) return null; // alimentation non documentée
  if (b.kind === 'HTA') { const bus = { SS1_20: 'SS1_BL', SS2_20: 'SS2_BL', KV6: 'KV6_BL', PL20: 'PL_B01' }[b.id]; return bus ? isLive(bus) : null; }
  return null;
}
function siteSVG(opts = {}) {
  const S = D.site, W = 1000, H = W / S.ratio;
  // repères : contour fin cliquable pour tous les bâtiments ; remplissage et étiquette uniquement pour les salles électriques
  // bâtiments : polygones (orthophoto IGN, repères reportés par recalage) ou rectangles (ancienne vue)
  const shapes = z => (z.polys || (z.parts || []).map(([x, y, w, h]) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]])).map(p => p.map(([x, y]) => [x * W, y * H]));
  const pts = P => P.map(p => p.join(',')).join(' ');
  // aucun remplissage ni halo : le bâtiment n'apparaît (contour + légende) qu'au passage de la souris ; un clic ouvre sa fiche
  const zs = S.zones.map(z => {
    const R = shapes(z), cx = z.cx * W, cy = z.cy * H;
    const txt = z.label || z.name;   // nom seul : les numéros sont la légende du PowerPoint, pas une information pour le technicien
    const lab = `<g class="zlab" style="pointer-events:none"><rect x="${cx - txt.length * 3.7 - 9}" y="${cy - 12}" width="${txt.length * 7.4 + 18}" height="24" rx="12" fill="rgba(10,20,15,.85)" stroke="#fff" stroke-width="1.2"/>
      <text x="${cx}" y="${cy + 4.5}" font-size="12.5" text-anchor="middle" fill="#fff" font-weight="800">${esc(txt)}</text></g>`;
    return `<g class="zone" role="button" tabindex="0" aria-label="${esc(txt)}" data-zone="${z.n}" data-id="Z${z.n}">${R.map(P => `<polygon class="zout" points="${pts(P)}" fill="transparent" stroke-width="2.5" stroke-linejoin="round"/>`).join('')}${lab}</g>`;
  }).join('');
  // liaisons 20 kV : poste de livraison CNR / EDF -> tableaux 20 kV des deux sous-stations (schéma de principe, pas le tracé des câbles)
  const Z = n => S.zones.find(z => z.n === n), pdl = Z(33);
  const links = pdl ? [[25, 'SS2_20'], [31, 'SS1_20']].map(([n, hta]) => { const z = Z(n); if (!z) return '';
    const x1 = pdl.cx * W, y1 = pdl.cy * H, x2 = z.cx * W, y2 = z.cy * H, live = refLive(hta) !== false, mx = (x1 + x2) / 2 + (y2 - y1) * .18, my = (y1 + y2) / 2 - (x2 - x1) * .18;
    return `<path d="M${x1} ${y1}Q${mx} ${my} ${x2} ${y2}" fill="none" stroke="${live ? '#ffd23f' : '#e5484d'}" stroke-width="3" stroke-dasharray="9 6" ${live ? 'class="flow"' : ''} opacity=".95"><title>Liaison 20 kV : poste de livraison → ${esc(z.label || z.name)} (schéma de principe)</title></path>
      <text x="${(x1 + x2) / 2 + (y2 - y1) * .1}" y="${(y1 + y2) / 2 - (x2 - x1) * .1}" font-size="12" font-weight="800" fill="#ffd23f" stroke="rgba(0,0,0,.7)" stroke-width="3" paint-order="stroke" text-anchor="middle">20 kV</text>`; }).join('') : '';
  // flèche du nord : vers le haut (image IGN brute) ou vers la gauche (vue tournée de 90° dans le sens antihoraire)
  const north = S.north ? `<g transform="translate(40,40)" style="pointer-events:none"><circle r="22" fill="rgba(0,0,0,.55)"/><g transform="rotate(${S.north === 'left' ? -90 : 0})"><path d="M0 -15L7 6L0 2L-7 6Z" fill="#fff"/></g><text x="${S.north === 'left' ? 9 : 0}" y="${S.north === 'left' ? 4 : 17}" font-size="10" fill="#fff" text-anchor="middle" font-weight="800">N</text></g>` : '';
  // fond : image unique, ou pyramide de tuiles (orthophoto IGN) — niveau de base toujours affiché, niveaux fins ajoutés au zoom par orthoTiles()
  const bg = S.tiles ? `<g class="otb">${tileImgs(S, S.maxLevel - 2)}</g><g class="oth"></g>` : `<image href="${S.img}" x="0" y="0" width="${W}" height="${H}" preserveAspectRatio="none"/>`;
  return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system,Segoe UI,Arial,sans-serif">${bg}<g class="olay">${zs}${links}${north}</g></svg>`;
}
/* ---------- tuiles de la vue aérienne (pyramide Deep Zoom : tuiles 512 px, recouvrement 1 px ; niveau maxLevel = pixels d'origine) */
function tileGeom(S, lv, c, r) {
  const u = 1000 / S.w, k = 2 ** (S.maxLevel - lv), lw = Math.ceil(S.w / k), lh = Math.ceil(S.h / k), T = S.tileSize, O = S.overlap;
  const x0 = Math.max(0, c * T - O), y0 = Math.max(0, r * T - O), x1 = Math.min(lw, (c + 1) * T + O), y1 = Math.min(lh, (r + 1) * T + O);
  return { x: x0 * k * u, y: y0 * k * u, w: (x1 - x0) * k * u, h: (y1 - y0) * k * u };
}
function tileImgs(S, lv, keys) {
  return (keys || Object.keys(S.tiles).filter(k => k.startsWith(lv + '/'))).map(key => { const [c, r] = key.split('/')[1].split('_').map(Number), g = tileGeom(S, lv, c, r);
    return `<image data-k="${key}" href="${S.tiles[key]}" x="${g.x}" y="${g.y}" width="${g.w}" height="${g.h}" preserveAspectRatio="none"/>`; }).join('');
}
// charge les tuiles du niveau adapté au zoom, seulement dans la zone visible (appelé à chaque changement de vue)
function orthoTiles(svg, S) {
  const hi = svg.querySelector('.oth'); if (!hi) return;
  const u = 1000 / S.w, T = S.tileSize, L = S.maxLevel;
  const update = () => {
    const vb = svg.viewBox.baseVal, r = svg.getBoundingClientRect(); if (!r.width) return;
    const devPerImgPx = Math.min(r.width / vb.width, r.height / vb.height) * u * (devicePixelRatio || 1);
    const lv = Math.min(L, L + Math.ceil(Math.log2(Math.max(devPerImgPx, 1e-6))));
    if (lv <= L - 2) { hi.innerHTML = ''; return; }                 // le niveau de base suffit
    const k = 2 ** (L - lv), lw = Math.ceil(S.w / k), lh = Math.ceil(S.h / k);
    const c0 = Math.max(0, Math.floor(vb.x / u / k / T)), c1 = Math.min(Math.ceil(lw / T) - 1, Math.floor((vb.x + vb.width) / u / k / T));
    const r0 = Math.max(0, Math.floor(vb.y / u / k / T)), r1 = Math.min(Math.ceil(lh / T) - 1, Math.floor((vb.y + vb.height) / u / k / T));
    const want = new Set(); for (let c = c0; c <= c1; c++) for (let rr = r0; rr <= r1; rr++) { const key = `${lv}/${c}_${rr}`; if (S.tiles[key]) want.add(key); }
    [...hi.children].forEach(im => { if (!want.has(im.dataset.k)) im.remove(); });
    const have = new Set([...hi.children].map(im => im.dataset.k));
    const add = [...want].filter(k2 => !have.has(k2));
    if (add.length) hi.insertAdjacentHTML('beforeend', tileImgs(S, lv, add));
    svg.dataset.level = lv;
  };
  new MutationObserver(update).observe(svg, { attributes: true, attributeFilter: ['viewBox'] });
  window.addEventListener('resize', update);
  requestAnimationFrame(update);
}
function openZone(n) {
  const z = D.site.zones.find(z => String(z.n) === String(n)); if (!z) return;
  const locs = Object.entries(D.loc).filter(([k, l]) => l.bat === z.n);
  const plans = locs.flatMap(([k, l]) => l.plan || []);
  openSheet(`${z.conf && z.conf !== 'confirme' ? confPill(z.conf) : ''}<h2>${esc(z.label || z.name)}</h2>`,
    `${plans.length ? `<div class="row" style="margin:10px 0">${[...new Set(plans)].map(p => `<button class="btn" data-go="#/plans/${p}">Plan : ${esc(D.plans.find(x => x.id === p).title)}</button>`).join('')}</div>` : ''}
     ${z.refs ? `<div class="list">${z.refs.map(r => BOARD[r] ? `<div class="li" data-go="#/b/${r}"><span class="dot ${refLive(r) ? 'on' : refLive(r) === null ? 'unk' : 'off'}"></span><div class="grow"><b>${esc(BOARD[r].name)}</b></div><a href="#" class="small" data-go="#/courant/${r}">⚡</a></div>` : liNode(NODE[r])).join('')}</div>`
      : '<p class="muted">Aucun tableau électrique dans ce bâtiment.</p>'}`);
}
function vHome() {
  const salles = D.site.zones.filter(z => z.label);
  const planOfZone = z => { if ((z.refs || []).includes('PL20')) return 'PLAN_PDL'; const l = Object.values(D.loc).find(l => l.bat === z.n && l.plan && l.plan.length); return l ? l.plan[0].replace(/^PLAN_SS1[GD]$/, 'PLAN_SS1') : null; };
  VIEW().innerHTML = `
  <a class="bigbtn" data-go="#/courant" style="margin-top:14px">⚡<div><b>Remettre le courant</b><span>Un départ ou un tableau est coupé : fiche de manœuvre en 3 touches</span></div></a>
  <div class="tiles" style="margin:12px 0">${salles.map(z => `<button class="tile glass" ${planOfZone(z) ? `data-go="#/plans/${planOfZone(z)}"` : `data-zone="${z.n}"`}><b>${esc(z.label)}</b><span>${(z.refs || []).length} tableau${(z.refs || []).length > 1 ? 'x' : ''}</span></button>`).join('')}
    <button class="tile glass" data-go="#/tableaux"><b>Tous les tableaux</b><span>${D.boards.length} tableaux</span></button></div>
  <div class="sitemap" style="--ar:${D.site.ratio}"><div id="aerial"></div>
    <div class="row small" style="margin-top:8px;gap:14px"><span class="muted">Passez sur un bâtiment pour voir son nom, touchez-le pour ses tableaux.</span><span><b style="color:#ffd23f">┅</b> liaison 20 kV</span>${D.site.attribution ? `<span class="muted" style="margin-left:auto;font-size:11px">${esc(D.site.attribution)}</span>` : ''}</div></div>
  ${footer()}`;
  const siteViewer = mountViewer($('#aerial'), siteSVG(), { site:true, onClick: id => openZone(id.slice(1)), native: D.site.w ? 1000 / D.site.w : null });
  addSiteFullscreen($('#aerial'),siteViewer);
  if (D.site.tiles) orthoTiles($('#aerial svg'), D.site);
  $$('.tile[data-zone]').forEach(b => b.onclick = () => openZone(b.dataset.zone));
}

/* ---------- Plans d'implantation */
const SCHEME = { accent1: '#156082', accent2: '#E97132', accent6: '#4EA72E', tx1: 'currentColor', dk1: 'currentColor', style: 'currentColor' };
const lineColor = c => !c ? 'currentColor' : c.startsWith('#') ? c : SCHEME[c.replace('scheme:', '')] || 'currentColor';
let PLAN_LINKS = 'all';  // 'all' : chaîne complète 20 kV → transfos → TGBT ; false : implantation seule
function planFor(ref) {
  if (ref === 'PL20' || (NODE[ref] && NODE[ref].board === 'PL20')) return 'PLAN_PDL';   // poste de livraison : schéma de principe (aucun plan transmis)
  for (const p of D.plans) for (const it of p.items) if (it.ref === ref) return p.id; return null;
}
function planRefs(id) {
  // éléments d'un plan qui représentent cet équipement ou son tableau
  const n = NODE[id]; const out = [id]; if (n && n.board) out.push(n.board);
  return out;
}
function relation(a, b) {
  // liaison électrique documentée a -> b (sens amont -> aval)
  const na = NODE[a], nb = NODE[b], ba = BOARD[a], bb = BOARD[b];
  if (na && na.t === 'tr' && bb) return (DOWN[a] || []).some(e => NODE[e.b].board === b);
  if (na && na.t === 'tr' && nb) return (DOWN[a] || []).some(e => e.b === b);
  if (ba && nb && nb.t === 'tr') return (UP[b] || []).some(e => NODE[e.a].board === a);
  if (ba && bb && a !== b) return (DEPS_BY_BOARD[a] || []).some(d => d.feeds === b) || D.nodes.some(n => n.board === a && n.t === 'dep' && (DOWN[n.id] || []).some(e => NODE[e.b].board === b));
  if (ba && nb && (nb.t === 'load' || nb.t === 'dep')) return (DEPS_BY_BOARD[a] || []).some(d => (DOWN[d.id] || []).some(e => e.b === b)) || nb.board === a;
  if (na && na.t === 'src' && bb) return (DOWN[a] || []).some(e => NODE[e.b].board === b);
  return false;
}
/*PLANSVG*/
