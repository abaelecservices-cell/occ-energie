/* ======================================================================= fiches de dépannage — PROJETS à valider
   Deux sortes de fiches :
   - fiches de manœuvre (départ déclenché, couplage, retour à la normale) : rédigées automatiquement à partir de la topologie documentée
     (unifilaire, classeur, plans Schneider, photos) et de la règle d'exploitation donnée par l'exploitant (jamais CNR + EDF ;
     jamais arrivée A · couplage · arrivée B fermés ensemble). Elles restent des PROJETS tant qu'elles ne sont pas inscrites dans
     validations.json, pour CET équipement et CETTE version de la fiche (empreinte du texte) ;
   - fiches de contrôle (tableau entièrement coupé, cellule HTA, défaut d'isolement, température transformateur, commande impossible) :
     aucune ouverture ni fermeture n'y est rédigée, seulement des observations à faire.
   La cause d'un symptôme est présentée comme une hypothèse tant que les observations ne la prouvent pas. Texte volontairement court. */
const VALID = D.validations || {};
// nom court d'un appareil : sans parenthèses ni complément « — … » (ex. « Arrivée TGBT 6A (TR 6A — M32H1) » -> « Arrivée TGBT 6A »)
const dn = x => { const p = (x.label || '').replace(/\s*\([^)]*\)/g, '').split(' — ').map(s => s.trim()); return p[0].length <= 3 && p[1] ? p[0] + ' ' + p[1] : p[0]; };
const tagOf = x => x.case ? `case ${x.case}` : x.uni && x.uni.rep ? `repère ${x.uni.rep}` : x.rep ? `repère ${x.rep}` : '';
const dev = x => `<b>${esc(dn(x))}</b>${tagOf(x) ? ` <span class="pill">${esc(tagOf(x))}</span>` : ''}`;
const isCond = x => /condensat|varset|varlogic/i.test(x.label) || /^COND/.test(x.feeds || '');
const depsOn = bus => (DOWN[bus] || []).map(e => NODE[e.b]).filter(x => x.t === 'dep');
const cellOf = tr => tr && tr.t === 'tr' ? NODE[((UP[tr.id] || [])[0] || {}).a] : null;
const isHTA = n => !!(n && n.board && BOARD[n.board] && BOARD[n.board].kind === 'HTA');
function srcSet(bid) {
  const qa = NODE[bid + '_QA'], qb = NODE[bid + '_QB'], qc = NODE[bid + '_QC'], b = BOARD[bid];
  if (!b || !qa || !qb || !qc || !(UP[qa.id] || []).length || !(UP[qb.id] || []).length) return null;
  const busQ = q => (DOWN[q.id] || []).map(e => e.b).find(x => NODE[x].t === 'bus');
  const ba = busQ(qa), bb = busQ(qb); if (!ba || !bb || ba === bb) return null;
  // le couplage doit relier directement les deux demi-jeux de barres (sinon : répartition des départs non documentée, ex. TS 12)
  const cu = (UP[qc.id] || []).map(e => e.a), cd = (DOWN[qc.id] || []).map(e => e.b);
  if (!((cu.includes(ba) && cd.includes(bb)) || (cu.includes(bb) && cd.includes(ba)))) return null;
  const lab = h => ((b.halves || []).find(x => x.id === h) || {}).label || short(NODE[h]);
  const rule = (b.coupler && b.coupler.rule) || '';
  return { b, qa, qb, qc, ba, bb, la: lab(ba), lb: lab(bb), sa: NODE[UP[qa.id][0].a], sb: NODE[UP[qb.id][0].a], ronis: /Ronis|1-1-0/i.test(rule), qs: NODE[bid + '_QS'] };
}
// demi-TGBT alimenté par un transformateur : { bid, h }
function halfOfTr(tr) {
  const q = (DOWN[tr.id] || []).map(e => NODE[e.b]).find(x => x.board && srcSet(x.board));
  if (!q) return null; const s = srcSet(q.board); return { bid: q.board, h: q.id === s.qa.id ? 'A' : 'B', s };
}
const trOfCell = c => (DOWN[c.id] || []).map(e => NODE[e.b]).find(x => x.t === 'tr');
function imax(src, q) {
  if (src.t === 'tr' && src.kva) { const p = parseFloat(String(src.kva).replace(',', '.')); if (p) return `${dn(src)} ${src.kva} ≈ ${Math.round(p * 1000 / (Math.sqrt(3) * 400))} A`; }
  return q.ir ? `réglage ${q.ir}` : '';
}
/* mini-schéma d'un TGBT scindé en deux : TR A → arrivée A → ½ A ─ couplage ─ ½ B ← arrivée B ← TR B
   st = { ta, tb : transformateur sous tension ; qa, qc, qb : appareil fermé ; lock : 'A' | 'B' arrivée cadenassée } */
function synMini(s, st, caption) {
  const la = (st.ta && st.qa) || (st.qc && st.tb && st.qb), lb = (st.tb && st.qb) || (st.qc && st.ta && st.qa);
  const C = v => v ? '#12b76a' : '#e5484d', G = '#8a9690';
  const brk = (x, y, closed, live, vert = true) => closed
    ? `<rect x="${x - 8}" y="${y - 8}" width="16" height="16" rx="2" fill="${live ? '#12b76a' : '#e5484d'}"/>`
    : `<rect x="${x - 8}" y="${y - 8}" width="16" height="16" rx="2" fill="var(--bg)" stroke="${G}" stroke-width="2"/><path d="${vert ? `M${x - 5} ${y + 5}L${x + 5} ${y - 5}` : `M${x - 5} ${y - 5}L${x + 5} ${y + 5}`}" stroke="${G}" stroke-width="2"/>`;
  const tr = (x, on, name) => `<g><circle cx="${x}" cy="22" r="11" fill="none" stroke="${C(on)}" stroke-width="2.5"/><circle cx="${x}" cy="36" r="11" fill="none" stroke="${C(on)}" stroke-width="2.5"/>
    <text x="${x + (x < 150 ? -18 : 18)}" y="33" font-size="12" font-weight="800" text-anchor="${x < 150 ? 'end' : 'start'}" fill="currentColor">${esc(name)}</text>${on ? '' : `<text x="${x + (x < 150 ? -18 : 18)}" y="47" font-size="10" text-anchor="${x < 150 ? 'end' : 'start'}" fill="#e5484d" font-weight="700">hors service</text>`}</g>`;
  const feedA = st.ta && st.qa, feedB = st.tb && st.qb;
  return `<figure class="synmini"><svg viewBox="-48 0 396 150" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system,Segoe UI,Arial,sans-serif">
    ${tr(70, st.ta, dn(s.sa))}${tr(230, st.tb, dn(s.sb))}
    <path d="M70 47V72M70 88V108" stroke="${C(feedA)}" stroke-width="3"/><path d="M230 47V72M230 88V108" stroke="${C(feedB)}" stroke-width="3"/>
    ${brk(70, 80, st.qa, feedA)}${brk(230, 80, st.qb, feedB)}
    ${st.lock === 'A' ? '<text x="81" y="85" font-size="13">🔒</text>' : ''}${st.lock === 'B' ? '<text x="203" y="85" font-size="13">🔒</text>' : ''}
    <path d="M18 110H136" stroke="${C(la)}" stroke-width="7" stroke-linecap="round"/><path d="M164 110H282" stroke="${C(lb)}" stroke-width="7" stroke-linecap="round"/>
    <path d="M136 110H142M158 110H164" stroke="${st.qc ? C(la && lb) : G}" stroke-width="3"/>${brk(150, 110, st.qc, la && lb, false)}
    <text x="77" y="132" font-size="12" font-weight="800" text-anchor="middle" fill="currentColor">${esc(s.la)}</text><text x="223" y="132" font-size="12" font-weight="800" text-anchor="middle" fill="currentColor">${esc(s.lb)}</text>
    <text x="150" y="146" font-size="10" text-anchor="middle" fill="${G}">couplage ${st.qc ? 'fermé' : 'ouvert'}</text>
    <text x="56" y="84" font-size="9.5" fill="${G}" text-anchor="end">arrivée ${st.qa ? 'fermée' : 'ouverte'}</text><text x="244" y="84" font-size="9.5" fill="${G}">arrivée ${st.qb ? 'fermée' : 'ouverte'}</text>
  </svg><figcaption>${caption}</figcaption></figure>`;
}
const issueActive = i => (i.status || (/résolu/i.test(i.title) ? 'resolu' : 'actif')) !== 'resolu';
const issuesOn = ids => D.issues.filter(i => issueActive(i) && ids.some(e => i.ents.includes(e)));
const feederOf = bid => D.nodes.filter(d => d.t === 'dep' && d.feeds === bid);
const halfOf = (s, bus) => bus === s.ba ? 'A' : bus === s.bb ? 'B' : null;
const goBtn = (href, t) => `<a class="btn ghost mini noprint" data-go="${href}" href="#">${t}</a>`;
const ronisTxt = s => s.ronis ? ' — clés Ronis dessinées sur le plan (1-0-1 · 0-1-1 · 1-1-0), présence à vérifier' : '';

/* --- départ déclenché (aussi : tableau secondaire coupé -> son départ d'alimentation) */
function moTrip(d, forBoard) {
  const child = d.feeds && BOARD[d.feeds], bus = busOf(d.id), b = boardOf(d);
  return { key: `S1:${d.id}`, id: 'S1-' + d.id, sim: false, at: d,
    title: forBoard ? `${forBoard.name} coupé — remettre son alimentation` : `${dn(d)} coupé — remettre le départ`,
    stop: 'Court-circuit ou défaut d’isolement : ne pas réarmer avant d’avoir trouvé et réparé le défaut.',
    avant: [forBoard ? `${esc(b ? b.name : '')} a du courant (sinon, choisir ${esc(b ? b.name : 'le tableau amont')}).` : `Les autres départs de ${esc(bus ? short(NODE[bus]) : 'ce tableau')} ont du courant (sinon, le problème est en amont).`],
    steps: [
      { t: `Prévenir l’atelier${child ? ' (' + esc(child.name) + ')' : ''} et mettre les machines à l’arrêt.` },
      { t: `Au ${esc(b ? b.name : '')} : lire le défaut sur ${dev(d)} (surcharge, court-circuit, défaut terre).` },
      { t: 'Court-circuit ou défaut terre : consigner le départ et réparer. Surcharge : supprimer la cause.' },
      { t: `Réarmer puis fermer ${dev(d)}.`, sw: d.id, v: true },
      { t: `Vérifier que le courant est revenu${child ? ' sur ' + esc(child.name) : ''} et que le disjoncteur tient.` },
      { t: 'Rendre l’installation à l’atelier. Noter dans le journal.' }],
    hab: 'BE Manœuvre ou BR · consignation : BC' };
}
/* --- demi-jeu de barres coupé : réalimentation par le couplage */
function moCoupling(bid, lost) {
  const s = srcSet(bid); if (!s) return null;
  const A = lost === 'A', qL = A ? s.qa : s.qb, qH = A ? s.qb : s.qa, busL = A ? s.ba : s.bb, laL = A ? s.la : s.lb, laH = A ? s.lb : s.la, sL = A ? s.sa : s.sb, sH = A ? s.sb : s.sa;
  const deps = depsOn(busL), conds = deps.filter(isCond), cell = cellOf(sL), mx = imax(sH, qH);
  return { key: `S2:${bid}:${lost}`, id: `S2-${bid}-${lost}`, check: busL, at: qL, kind: 'mo',
    title: `${laL} coupé — réalimenter par le couplage`,
    stop: `Ne pas coupler si ${dn(qL)} a déclenché sur défaut (voyant court-circuit ou terre) : le défaut est sur ${laL}. Appeler le responsable.`,
    syn: [synMini(s, { ta: !A, tb: A, qa: true, qb: true, qc: false }, `Maintenant : ${esc(dn(sL))} hors service, ${esc(laL)} coupé`),
      synMini(s, { ...(A ? { ta: false, tb: true, qa: false, qb: true, lock: 'A' } : { ta: true, tb: false, qa: true, qb: false, lock: 'B' }), qc: true }, `Après : ${esc(dn(qL))} ouverte et cadenassée, couplage fermé — ${esc(dn(sH))} alimente les deux moitiés`)],
    avant: [`${esc(laH)} a du courant.`,
      `<b>Règle d’exploitation : le couplage ne se ferme qu’après avoir ouvert l’arrivée qui alimentait ${esc(laL)}</b> (${esc(dn(qL))}). Jamais arrivée A, couplage et arrivée B fermés ensemble${ronisTxt(s)}.`,
      `${esc(dn(sH))} va alimenter les deux moitiés${mx ? ' : ' + esc(mx) + ' maximum' : ''} → délester si besoin (charge réelle non documentée).`,
      'Verrouillages réels (clés, électriques) : les vérifier sur place.',
      ...(s.qs ? [`Ne pas toucher à ${esc(dn(s.qs))} (logique non documentée).`] : []),
      ...issuesOn([bid, s.qa.id, s.qb.id, s.sa.id, s.sb.id]).map(i => `⚠️ ${esc(i.title)} : vérifier l’étiquetage sur place.`)],
    steps: [
      { t: `Ouvrir et cadenasser ${dev(qL)} — l’arrivée qui alimentait ${esc(laL)}.`, sw: qL.id, v: false },
      { t: `Ouvrir les départs de ${esc(laL)} (${deps.length})${conds.length ? ', d’abord ' + conds.map(dev).join(', ') : ''}.`, many: deps.map(x => x.id), v: false },
      { t: `Vérifier : ${dev(qL)} <b>ouverte</b>, ${dev(qH)} fermée, ${dev(s.qc)} ouvert.` },
      { t: `Fermer ${dev(s.qc)} : ${esc(dn(sH))} alimente maintenant ${esc(laL)}.`, sw: s.qc.id, v: true },
      { t: `Vérifier la tension sur ${esc(laL)}.` },
      { t: `Refermer les départs un par un en surveillant le courant de ${dev(qH)}${mx ? ' (max ' + esc(mx.split('≈ ')[1] || mx) + ')' : ''}. Condensateurs en dernier.`, many: deps.map(x => x.id), v: true },
      { t: `Afficher « Secours : ${esc(dn(sL))} hors service, couplage fermé ». Prévenir le chargé d’exploitation${cell ? ` (consignation HTA de ${dev(cell)} si travaux)` : ''}.` }],
    setup: [[cell ? cell.id : sL.id, false]],
    hab: 'BE Manœuvre / BR · condamnation : BC · HTA : H' };
}
/* --- retour à la normale */
function moReturn(bid, lost) {
  const s = srcSet(bid); if (!s) return null;
  const A = lost === 'A', qL = A ? s.qa : s.qb, busL = A ? s.ba : s.bb, laL = A ? s.la : s.lb, sL = A ? s.sa : s.sb, cell = cellOf(sL);
  return { key: `S2R:${bid}:${lost}`, id: `S2R-${bid}-${lost}`, check: busL, at: qL, kind: 'mo',
    title: `${laL} — revenir sur ${dn(sL)}`,
    stop: `Ouvrir le couplage AVANT de refermer ${dn(qL)} : jamais arrivée A, couplage et arrivée B fermés ensemble. Le retour coupe brièvement ${laL}.`,
    syn: [synMini(s, { ta: true, tb: true, qa: !A, qb: A, qc: true, lock: lost }, `Maintenant : configuration secours, ${esc(dn(A ? s.sb : s.sa))} alimente les deux moitiés`),
      synMini(s, { ta: true, tb: true, qa: true, qb: true, qc: false }, `Après : chaque moitié sur son transformateur, couplage ouvert`)],
    avant: [`${esc(dn(sL))} réparé et remis sous tension${cell ? ' par le chargé d’exploitation (' + esc(dn(cell)) + ' fermée)' : ''}.`, `Prévenir les ateliers de ${esc(laL)}.`],
    steps: [
      { t: `Ouvrir les départs de ${esc(laL)}, condensateurs d’abord.`, many: depsOn(busL).map(x => x.id), v: false },
      { t: `Ouvrir ${dev(s.qc)} : ${esc(laL)} est hors tension.`, sw: s.qc.id, v: false },
      { t: `Couplage bien ouvert : décadenasser et fermer ${dev(qL)}.`, sw: qL.id, v: true },
      { t: `Vérifier la tension sur ${esc(laL)}.` },
      { t: 'Refermer les départs un par un, condensateurs en dernier.', many: depsOn(busL).map(x => x.id), v: true },
      { t: 'Retirer l’affiche « secours ». Noter dans le journal.' }],
    setup: [[qL.id, false], [s.qc.id, true], [cell ? cell.id : sL.id, true]],
    hab: 'BE Manœuvre / BR · levée de condamnation : BC' };
}
/* --- tableau entièrement coupé (les deux arrivées) : contrôles uniquement, cause à établir par les observations */
function moAll(bid) {
  const s = srcSet(bid), b = BOARD[bid];
  const cells = s ? [cellOf(s.sa), cellOf(s.sb)].filter(Boolean) : [];
  const hta = cells.length && boardOf(cells[0]);
  return { key: `S3:${bid}`, id: `S3-${bid}`, sim: false, at: s ? s.qa : null, kind: 'ctrl',
    title: `${b.name} entièrement coupé`,
    stop: 'Ne réarmer aucune arrivée déclenchée sur défaut. Aucune manœuvre HTA sans le chargé d’exploitation (habilitation H).',
    avant: ['Cause probable en amont (cellules HTA, tableau 20 kV ou poste de livraison) — <b>hypothèse à confirmer</b> par les observations ci-dessous.'],
    steps: [
      ...(s ? [{ t: `Lire l’état de ${dev(s.qa)} et ${dev(s.qb)} : <b>déclenchées</b> (voyant défaut, Micrologic) = défaut côté BT, ne pas réarmer, appeler le responsable ; <b>fermées ou ouvertes sans défaut</b> et sans tension = cause en amont.` }] : []),
      { t: 'Regarder si d’autres TGBT sont coupés. Plusieurs TGBT coupés = perte plus en amont (tableau 20 kV ou poste de livraison).' },
      { t: `Poste de livraison : la bascule CNR → EDF est automatique. Contrôler ${dev(NODE.PL_B01)} et ${dev(NODE.PL_A04)} — jamais les deux fermés.` },
      ...(cells.length ? [{ t: `${esc(hta ? hta.name : 'Tableau 20 kV')} : contrôler ${cells.map(dev).join(' et ')} (relais déclenché ?).` }] : []),
      { t: 'Appeler le chargé d’exploitation HTA.' },
      ...(s ? [{ t: `Quand la tension est revenue : contrôler ${dev(s.qa)} et ${dev(s.qb)} fermés, ${dev(s.qc)} ouvert.` }] : [])],
    hab: 'Contrôles : BE Vérification · HTA : H' };
}
/* --- tableau 20 kV / 6 kV coupé : contrôles uniquement (aucune séquence HTA rédigée) */
function moHTA(bid) {
  const b = BOARD[bid], arr = D.nodes.filter(n => n.board === bid && SW.has(n.t) && /^(Arrivée|Disjoncteur arrivée)/i.test(n.label)), cpl = D.nodes.filter(n => n.board === bid && n.t === 'cpl');
  const pl = bid === 'PL20';
  return { key: `S4:${bid}`, id: `S4-${bid}`, sim: false, at: arr[0] || cpl[0] || null, kind: 'ctrl',
    title: `${b.name} coupé`,
    stop: 'Manœuvres HTA réservées au chargé d’exploitation (habilitation H). Aucune séquence HTA n’est rédigée : la logique des clés n’est pas décrite sur l’unifilaire.',
    avant: [],
    steps: [
      ...(pl ? [{ t: 'Contrôler la présence de tension CNR et EDF (voyants des cellules d’arrivée).' },
        { t: `Sur manque CNR, la bascule vers EDF est automatique : contrôler ${dev(NODE.PL_B01)} et ${dev(NODE.PL_A04)} — jamais les deux fermés.` },
        { t: 'CNR et EDF absents : prévenir le distributeur.' }]
      : [{ t: 'Regarder si l’autre sous-station est aussi coupée : si oui, le défaut est probablement au poste de livraison.' },
        ...(arr.length ? [{ t: `Contrôler ${arr.map(dev).join(', ')}${cpl.length ? ' et ' + cpl.map(dev).join(', ') : ''}.` }] : []),
        { t: 'Contrôler les relais des cellules (drapeau de déclenchement).' }]),
      { t: 'Appeler le chargé d’exploitation HTA.' },
      { t: 'Quand le 20 kV est revenu : pour chaque TGBT, suivre la fiche « TGBT entièrement coupé ».' }],
    hab: 'Contrôles : BE Vérification · HTA : H' };
}
/* --- une seule cellule HTA ouverte ou déclenchée : son transformateur et ce qu'il alimente (le reste du tableau n'est pas concerné) */
function moCell(c) {
  const t = trOfCell(c), hf = t && halfOfTr(t), b = boardOf(c);
  const lost = hf ? (hf.h === 'A' ? hf.s.la : hf.s.lb) : null, other = hf ? (hf.h === 'A' ? hf.s.sb : hf.s.sa) : null;
  const aval = t ? [...new Set(downstream(t.id).map(x => NODE[x].board).filter(x => x && BOARD[x] && BOARD[x].kind !== 'HTA'))].map(x => BOARD[x].name) : [];
  return { key: `S5:${c.id}`, id: `S5-${c.id}`, sim: false, at: c, kind: 'ctrl',
    title: `${dn(c)} ouverte ou déclenchée`,
    stop: 'Manœuvres HTA réservées au chargé d’exploitation (habilitation H). Ne pas réenclencher une cellule déclenchée sur défaut.',
    avant: [`Les autres cellules de ${esc(b ? b.name : 'ce tableau')} ont du courant : seule cette cellule est concernée (sinon : fiche « tableau 20 kV coupé »).`,
      t ? `Hors tension en configuration normale : <b>${esc(dn(t))}</b>${t.kva ? ' (' + esc(t.kva) + ')' : ''}${lost ? ` → <b>${esc(lost)}</b>` : ''}${aval.length > 1 ? ` et ce qu’il alimente (${aval.length - 1} autre(s) tableau(x) : ${goBtn(`#/courant/${t.id}`, 'voir')})` : ''}.` : 'Transformateur alimenté : non documenté.'],
    steps: [
      { t: `Lire le relais de ${dev(c)} : drapeau, message, phase en défaut. Noter dans le journal.` },
      ...(t && t.cooling ? [{ t: `Regarder aussi la surveillance de ${esc(dn(t))} (${esc(t.cooling)}) : un déclenchement température ou gaz ouvre la cellule.` }] : []),
      { t: 'Appeler le chargé d’exploitation HTA : lui seul décide de la remise sous tension.' },
      ...(hf ? [{ t: `Côté BT : ${esc(lost)} est sans tension. Il peut être réalimenté par le couplage depuis ${esc(dn(other))} : ${goBtn(`#/courant/${hf.bid}/demi${hf.h}`, `fiche « ${esc(lost)} coupé »`)}` }] : [])],
    hab: 'Contrôles : BE Vérification · HTA : H' };
}
/* --- défaut d'isolement signalé (neutre IT) : lecture du contrôleur et table voie → départ propre au tableau */
function insulTable(bid) {
  const T = (D.insul || {})[bid]; if (!T || !T.groups.length) return '';
  return `<div class="moinsul">${T.groups.map(g => `<div><b>${esc(g.name)}</b><table class="small"><tr><th>Voie</th><th>Désignation</th><th>Départ</th></tr>${g.rows.map(r => `<tr><td class="mono">${esc(r.ch)}</td><td>${esc(r.txt)}</td><td>${r.node ? `<a href="#" data-open="${r.node}">${esc(dn(NODE[r.node]))}</a>` : '<span class="muted">—</span>'}</td></tr>`).join('')}</table></div>`).join('')}
    <p class="src">${esc(T.device)} — source : ${esc(T.src)}. ${esc(T.note || '')}</p></div>`;
}
function moInsul(bid) {
  const b = BOARD[bid], T = (D.insul || {})[bid], tab = insulTable(bid);
  return { key: `S6:${bid}`, id: `S6-${bid}`, sim: false, at: null, board: b, kind: 'ctrl',
    title: `${b.name} — défaut d’isolement signalé`,
    stop: 'Neutre IT : un 1er défaut ne coupe pas, mais un 2e défaut sur une autre phase fait déclencher. Rechercher le défaut sans attendre ; ne jamais neutraliser le contrôleur.',
    avant: [`Contrôleur du tableau : ${esc(T ? T.device : b.it || 'non documenté')}.`, ...(T && /seuil/i.test(T.note || '') ? [esc(T.note)] : [])],
    steps: [
      { t: 'Lire le contrôleur d’isolement : valeur (kΩ) et voie en alarme. Photographier l’écran.' },
      { t: tab ? 'Chercher la voie dans la table ci-dessous : elle donne le départ et la case.' : 'Table voie → départ <b>non disponible</b> pour ce tableau : relever l’étiquette « localisation défaut » sur place.' },
      { t: 'Prévenir l’atelier du départ concerné. La recherche (mise hors tension du départ) se fait selon la procédure du site.' },
      { t: 'Noter dans le journal : date, valeur, voie, départ.' }],
    extra: tab,
    hab: 'Contrôles : BE Vérification · recherche de défaut : BR / BC' };
}
/* --- alarme ou déclenchement température d'un transformateur */
function moTemp(t) {
  const hf = halfOfTr(t), vent = D.nodes.filter(x => x.aux === t.id), lost = hf ? (hf.h === 'A' ? hf.s.la : hf.s.lb) : null;
  return { key: `S7:${t.id}`, id: `S7-${t.id}`, sim: false, at: t, kind: 'ctrl',
    title: `${dn(t)} — alarme température`,
    stop: `Un déclenchement température met ${dn(t)} hors service${lost ? ' : ' + lost + ' sera coupé' : ''}. Ne pas remettre sous tension un transformateur déclenché sans avis du chargé d’exploitation.`,
    avant: [`Surveillance : ${esc(t.cooling || (t.uni && t.uni.surv) || 'non documentée')}. Les seuils d’un dessin ne sont pas les réglages actuels.`],
    steps: [
      { t: 'Lire le relais de température : alarme ou déclenchement, valeur affichée, sonde en cause.' },
      { t: vent.length ? `Vérifier que la ventilation fonctionne : ${vent.map(v => `${dev(v)} au ${esc(boardOf(v).name)}`).join(', ')}.` : 'Vérifier la ventilation du local et du transformateur (départ de ventilation non documenté).' },
      { t: 'Prévenir le chargé d’exploitation : un délestage éventuel est décidé par lui.' },
      ...(hf ? [{ t: `Si le transformateur a déclenché : ${goBtn(`#/courant/${hf.bid}/demi${hf.h}`, `fiche « ${esc(lost)} coupé »`)}` }] : []),
      { t: 'Noter dans le journal.' }],
    hab: 'Contrôles : BE Vérification' };
}
/* --- l'appareil ne se ferme pas / ne se réarme pas (commande impossible) : ce n'est pas une absence de tension */
function moCmd(n) {
  const hta = isHTA(n), b = boardOf(n), arm = BOARD.ARM110;
  return { key: `S8:${n.id}`, id: `S8-${n.id}`, sim: false, at: n, kind: 'ctrl',
    title: `${dn(n)} ne se ferme pas / ne se réarme pas`,
    stop: 'Ne jamais forcer un appareil ni neutraliser un verrouillage ou une condamnation.',
    avant: ['Commande impossible ≠ absence de tension : la puissance peut être présente.'],
    steps: [
      { t: `Regarder si ${dev(n)} est déclenché sur défaut (voyant, bouton de réarmement, message du déclencheur)${n.t === 'dep' ? ' : si oui → ' + goBtn(`#/courant/${n.id}/depart`, 'fiche « départ déclenché »') : ''}.` },
      { t: 'Vérifier la position (embroché / débroché, sectionné) et les condamnations (cadenas, clé prisonnière).' },
      { t: hta ? `Vérifier les auxiliaires : 110 V CC (armement) et 24 V CC (déclenchement / fermeture) selon l’unifilaire${arm ? ' — ' + goBtn(`#/b/${arm.id}`, esc(arm.name)) : ''}.`
        : `Vérifier l’alimentation de commande de l’appareil (non documentée dans l’application pour ${esc(b ? b.name : 'ce tableau')}).` },
      { t: `Notice de l’appareil${n.model ? ' : ' + esc(n.model) : ''}. Si la cause n’est pas trouvée, appeler le responsable.` }],
    hab: 'Contrôles : BE Vérification' };
}
/* --- situations proposées pour un élément / un tableau (symptômes observables) */
function situations(id) {
  const n = NODE[id], b0 = BOARD[id], out = [];
  const bus = n ? (n.t === 'bus' ? n.id : busOf(n.id)) : null;
  const bb = b0 || (bus && boardOf(NODE[bus])) || (n && boardOf(n));
  const isol = bb && ((D.insul || {})[bb.id] || bb.it) ? { sit: 'isol', t: 'Défaut d’isolement signalé', d: 'Le contrôleur d’isolement est en alarme : trouver la voie et le départ.', mo: () => moInsul(bb.id) } : null;
  if (n && n.t === 'tr') {  // transformateur : hors service, alarme température, retour
    const hf = halfOfTr(n);
    if (hf) { const L = hf.h === 'A' ? hf.s.la : hf.s.lb;
      out.push({ sit: 'demi' + hf.h, t: `${dn(n)} hors service : ${L} coupé`, d: `Réalimenter ${L} par le couplage depuis ${dn(hf.h === 'A' ? hf.s.sb : hf.s.sa)}.`, mo: () => moCoupling(hf.bid, hf.h) }); }
    out.push({ sit: 'temp', t: 'Alarme ou déclenchement température', d: 'Relais de température, ventilation.', mo: () => moTemp(n) });
    const c = cellOf(n); if (c) out.push({ sit: 'cellule', t: `${dn(c)} ouverte ou déclenchée`, d: 'Le transformateur n’est plus alimenté en 20 kV.', mo: () => moCell(c) });
    if (hf) out.push({ sit: 'retour' + hf.h, t: `${dn(n)} réparé : revenir à la normale`, d: `${hf.h === 'A' ? hf.s.la : hf.s.lb} de nouveau sur ${dn(n)}.`, minor: true, mo: () => moReturn(hf.bid, hf.h) });
    return out;
  }
  if (!bb) return out;
  if (bb.kind === 'HTA') {
    if (n && n.t === 'cb' && trOfCell(n)) out.push({ sit: 'cellule', t: `Seule ${dn(n)} est ouverte ou déclenchée`, d: 'Les autres cellules du tableau ont du courant.', mo: () => moCell(n) });
    out.push({ sit: 'hta', t: `Tout le ${bb.name} est coupé`, d: 'Contrôles et appel du chargé d’exploitation HTA.', minor: !!(n && n.t === 'cb' && trOfCell(n)), mo: () => moHTA(bb.id) });
    if (n && SW.has(n.t)) out.push({ sit: 'cmd', t: `${dn(n)} ne se ferme pas`, d: 'Commande impossible, tension présente.', minor: true, mo: () => moCmd(n) });
    return out;
  }
  const s = srcSet(bb.id), h = s && bus ? halfOf(s, bus) : null;
  if (n && n.t === 'dep') out.push({ sit: 'depart', t: 'Seul ce départ est coupé', d: 'Les autres départs du tableau ont du courant.', mo: () => moTrip(n) });
  if (s) {
    (h ? [h] : ['A', 'B']).forEach(x => out.push({ sit: 'demi' + x, t: `Tout le ${x === 'A' ? s.la : s.lb} est coupé`, d: `${x === 'A' ? s.lb : s.la} a du courant : ${dn(x === 'A' ? s.sb : s.sa)} peut réalimenter ${x === 'A' ? s.la : s.lb} par le couplage, après ouverture de ${dn(x === 'A' ? s.qa : s.qb)}.`, mo: () => moCoupling(bb.id, x) }));
    out.push({ sit: 'tout', t: `Tout le ${bb.name} est coupé`, d: `${s.la} et ${s.lb} sans tension : cause probablement en amont, à confirmer.`, mo: () => moAll(bb.id) });
  } else {
    feederOf(bb.id).forEach((f, i, all) => out.push({ sit: 'amont' + (all.length > 1 ? i : ''), t: `Tout le ${bb.name} est coupé${all.length > 1 ? ' — alimentation ' + dn(f) : ''}`, d: `Alimenté par ${dn(f)} au ${boardOf(f) ? boardOf(f).name : ''}.`, mo: () => moTrip(f, bb) }));
  }
  if (isol) out.push(isol);
  if (n && SW.has(n.t)) out.push({ sit: 'cmd', t: `${dn(n)} ne se ferme pas / ne se réarme pas`, d: 'Commande impossible : ce n’est pas forcément une absence de tension.', minor: true, mo: () => moCmd(n) });
  if (s) (h ? [h] : ['A', 'B']).forEach(x => out.push({ sit: 'retour' + x, t: `Revenir à la normale (${x === 'A' ? s.la : s.lb})`, d: 'Après réparation du transformateur.', minor: true, mo: () => moReturn(bb.id, x) }));
  return out;
}
/* --- empreinte d'une fiche : une validation n'est valable que pour la version exacte du texte validé */
function moHash(mo) {
  const txt = [mo.title, mo.stop, ...(mo.avant || []), ...mo.steps.map(s => s.t)].join('|').replace(/<[^>]+>/g, '');
  let h = 0x811c9dc5; for (let i = 0; i < txt.length; i++) { h ^= txt.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
  return h.toString(16).padStart(8, '0');
}
function moStatus(mo) {
  const v = VALID[mo.key], h = moHash(mo);
  if (v && v.empreinte === h) return { st: 'ok', v, h };
  if (v) return { st: 'old', v, h };
  return { st: mo.kind === 'ctrl' ? 'ctrl' : 'proj', h };
}
/* --- rendu de la fiche : statut et validité AVANT les étapes */
function moSheetHTML(mo) {
  const S = moStatus(mo), at = mo.at, b = (at && boardOf(at)) || mo.board || null;
  const loc = b ? locChain(b.loc).slice(1).map(l => l.name).join(' · ') : '';
  const fid = at && facadeFor(at.id), pl = b && planFor(b.id);
  const ref = `réf. ${mo.key} · empreinte ${S.h} · données v${D.meta.version} du ${D.meta.built}`;
  const status = S.st === 'ok' ? `<div class="mostatus ok">✅<div><b>VALIDÉE</b> par ${esc(S.v.par)}${S.v.fonction ? ' (' + esc(S.v.fonction) + ')' : ''} le ${esc(S.v.date)}${S.v.note ? ' — ' + esc(S.v.note) : ''}<div class="small">${esc(ref)}</div></div></div>`
    : S.st === 'old' ? `<div class="mostatus old">⚠️<div><b>VALIDATION CADUQUE</b> — la fiche a changé depuis sa validation par ${esc(S.v.par)} le ${esc(S.v.date)} (empreinte validée ${esc(S.v.empreinte || '—')}). À faire revalider avant usage.<div class="small">${esc(ref)}</div></div></div>`
    : S.st === 'ctrl' ? `<div class="mostatus ctrl">🔎<div><b>FICHE DE CONTRÔLE</b> — aucune ouverture ni fermeture n’y est rédigée : observer, noter, appeler. Rédigée d’après les documents, non validée par le site.<div class="small">${esc(ref)}</div></div></div>`
    : `<div class="mostatus proj">📝<div><b>PROJET NON VALIDÉ</b> — rédigé automatiquement d’après les documents (topologie et règle d’exploitation). Ne pas l’appliquer avant validation par le chargé d’exploitation.<div class="small">${esc(ref)}</div></div></div>`;
  return `<div class="mosheet" data-mo="${esc(mo.id)}">
    <div class="mohead"><div class="small muted">${mo.kind === 'ctrl' ? 'FICHE DE CONTRÔLE' : 'FICHE DE MANŒUVRE'}</div><h1>${esc(mo.title)}</h1>
      ${b ? `<div class="moloc">📍 ${esc(loc ? loc + ' · ' : '')}<b>${esc(b.name)}</b></div>` : ''}
      <div class="row noprint" style="margin-top:8px">${pl ? `<button class="btn ghost" data-go="#/plans/${pl}/${b.id}">Voir sur le plan</button>` : ''}${fid ? `<button class="btn ghost" data-go="#/b/${boardForFacade(fid)}/f/${at.id}">Voir sur la façade</button>` : ''}</div></div>
    ${status}
    <div class="mostop">⛔ <div><b>STOP</b> — ${esc(mo.stop)}</div></div>
    ${mo.syn ? `<div class="synrow">${mo.syn.join('<span class="synarrow">➜</span>')}</div>` : ''}
    ${mo.avant.length ? `<div class="moavant"><b>Avant de commencer</b><ul>${mo.avant.map(x => `<li>${x}</li>`).join('')}</ul></div>` : ''}
    <ol class="mosteps">${mo.steps.map((st, i) => `<li><label><input type="checkbox"><span class="num">${i + 1}</span><span class="txt">${st.t}</span></label></li>`).join('')}</ol>
    ${mo.extra || ''}
    <div class="mofoot small"><span>${esc(ref)}</span><span>Habilitation : ${esc(mo.hab)}</span></div>
    <div class="row noprint" style="margin-top:10px"><button class="btn" onclick="window.print()">🖨️ Imprimer</button>${mo.sim !== false ? `<button class="btn ghost" data-mosim="${esc(mo.id)}">▶ Tester dans le simulateur</button>` : ''}</div>
    ${mo.kind === 'ctrl' ? '' : '<div class="mosign"><div>Vérifié par : ____________________ Date : ________</div><div>Validé par le chargé d’exploitation : ____________________ Date : ________ Visa : ______</div></div>'}</div>`;
}
/* --- test d'une fiche dans le simulateur : sur une COPIE de l'état simulé (rien n'est mémorisé ni affiché ailleurs) ;
       le test s'arrête au premier refus d'un interverrouillage */
function moSim(mo) {
  const saved = JSON.stringify(SIM), log = [];
  SANDBOX = true; SIM = {}; LIVE = LIVE_TMP = energize();          // départ : configuration normale documentée
  const run = (id, v) => { if (!NODE[id] || isClosed(id) === v) return true; return setSw(id, v); };
  let ok = true, stopAt = null;
  (mo.setup || []).forEach(([id, v]) => { if (ok) ok = run(id, v); });
  for (let i = 0; i < mo.steps.length && ok; i++) {
    const s = mo.steps[i];
    if (s.sw) { const r = run(s.sw, s.v); log.push([r ? '✓' : '⛔', `${i + 1}. ${dn(NODE[s.sw])} ${s.v ? 'fermé' : 'ouvert'}${r ? '' : ' — refusé : ' + (LAST_CONFLICT[0] || {}).txt}`]); if (!r) { ok = false; stopAt = i + 1; } }
    if (ok && s.many && s.many.length) { const bad = s.many.filter(id => !run(id, s.v)).length; log.push([bad ? '⛔' : '✓', `${i + 1}. ${s.many.length} départ(s) ${s.v ? 'fermés' : 'ouverts'}`]); if (bad) { ok = false; stopAt = i + 1; } }
  }
  const res = mo.check ? isLive(mo.check) : null;
  SIM = JSON.parse(saved); SANDBOX = false; LIVE = LIVE_TMP = energize();
  openSheet(`<span class="pill k">Test dans le simulateur</span><h2>${esc(mo.title)}</h2>`,
    `<div class="banner ${ok && res !== false ? 'info' : 'danger'}">${ok && res !== false ? '✅' : '⛔'}<div>${ok ? 'Aucune manœuvre refusée par la règle d’exploitation ni par les verrouillages connus.' : `Test arrêté à l’étape ${stopAt} : manœuvre refusée.`}${mo.check && ok ? `<br>${esc(short(NODE[mo.check]))} : <b>${res ? 'sous tension' : 'hors tension'}</b> à la fin.` : ''}</div></div>
     <div class="list" style="margin-top:10px">${log.map(([k, t]) => `<div class="li" style="cursor:default"><span>${k}</span><div class="grow small">${esc(t)}</div></div>`).join('')}</div>
     <p class="small muted" style="margin-top:10px">Test réalisé sur une copie, à partir de la configuration normale documentée : l’état affiché dans les plans et les tableaux n’est pas modifié. Un test réussi ne valide pas la fiche.</p>`);
}
