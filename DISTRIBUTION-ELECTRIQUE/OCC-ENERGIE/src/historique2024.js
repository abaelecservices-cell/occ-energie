/* OCC Energie — referentiel documentaire 2024, consultatif et hors-ligne.
 * Aucune ligne historique n'est transformee en arete de reseau ou en consigne. */
let HX24_MODE = 'departs', HX24_BOARD = 'tous', HX24_QUERY = '';
function hx24Matches(r) {
  const bid = 'TGBT' + r.tgbt;
  const half = typeof srcSet === 'function' ? srcSet(bid) : null;
  const curr = (DEPS_BY_BOARD[bid] || []).filter(n => {
    const loc = colOf(n);
    if (!loc || +loc.col !== +r.colonne || +loc.pos !== +r.case) return false;
    if (!half) return true;
    const bus = busOf(n.id);
    if (bus === half.ba) return r.cote === 'A';
    if (bus === half.bb) return r.cote === 'B';
    return true; // cote non determine dans le modele : garder visible, sans certifier.
  });
  return curr;
}
function hx24Card(r) {
  const current = hx24Matches(r), boardId = 'TGBT' + r.tgbt;
  const links = current.map(n => '<a href="#" data-open="' + esc(n.id) + '">' +
    esc(short(n)) + '</a>' + (n.case ? ' <span class="muted">(' + esc(n.case) + ')</span>' : '')).join(' · ');
  return '<div class="li hx24entry" data-hx-board="' + r.tgbt + '" data-hx-q="' +
    esc(norm([r.ts, r.designation, r.lieu, r.tgbt, r.cote, r.colonne, r.case].join(' '))) + '">' +
    '<div class="grow"><b>TGBT ' + r.tgbt + ' · ' + esc(r.cote) + ' · case ' +
    esc(r.colonne + '-' + r.case) + '</b> ' +
    '<span class="pill ' + (current.length ? 'a' : '') + '">' +
    (current.length ? 'Case retrouvée' : 'Non rapprochée') + '</span>' +
    '<div>' + esc(r.designation) + (r.ts ? ' <span class="muted">(' + esc(r.ts) + ')</span>' : '') + '</div>' +
    '<div class="small muted">Lieu 2024 : ' + esc(r.lieu || 'Non renseigné') + '</div>' +
    '<div class="small">Modèle actuel : ' + (links || '<span class="muted">Aucun départ trouvé à cette position</span>') + '</div>' +
    '</div><a class="btn ghost mini" href="#/b/' + esc(boardId) + '">Tableau →</a></div>';
}
function hx24Age(r) {
  const an = r.anneeMiseEnService2024;
  return '<div class="li hx24entry" data-hx-board="age" data-hx-q="' +
    esc(norm([r.equipement, r.sousStation2024, r.anneeBrute2024].join(' '))) + '">' +
    '<div class="grow"><b>' + esc(r.equipement) + '</b>' +
    '<div class="small muted">Sous-station (appellation 2024) : ' + r.sousStation2024 + '</div></div>' +
    '<span class="pill ' + (r.anomalieSaisie ? 'r' : '') + '">' +
    (r.anomalieSaisie ? 'Saisie source : ' + esc(r.anneeBrute2024) :
     an ? esc(an) : 'Année absente') + '</span></div>';
}
function vHistorique2024() {
  const h = D.historique2024;
  if (!h) { VIEW().innerHTML = '<h1>Référentiel 2024</h1><div class="banner danger">Le référentiel historique 2024 n’a pas été intégré dans cette version.</div>'; return; }
  const depts = h.departIndex2024 || [], ages = h.ageEquipements2024 || [];
  const found = depts.filter(r => hx24Matches(r).length).length;
  VIEW().innerHTML = '<h1>Référentiel Excel 2024</h1>' +
    '<p class="sub">Croisement documentaire des anciens départs avec le graphe OCC Énergie actuel.</p>' +
    '<div class="banner info">📚<div><b>Source historique, non une photographie du réseau actuel.</b> Un numéro de case retrouvé prouve seulement qu’un repère concorde ; il ne certifie ni sa destination, ni une liaison électrique, ni l’état réel d’un appareil. Ne pas utiliser pour une manœuvre.</div></div>' +
    '<div class="row" style="margin:12px 0;gap:8px;flex-wrap:wrap">' +
    '<span class="pill">36 départs 2024</span><span class="pill">' + found + ' cases rapprochées par repère</span>' +
    '<span class="pill">' + ages.length + ' historiques d’équipements</span></div>' +
    '<div class="row" style="margin:12px 0;gap:8px;flex-wrap:wrap">' +
    '<button class="btn ' + (HX24_MODE === 'departs' ? '' : 'ghost') + '" id="hx24-departs">Départs 2024</button>' +
    '<button class="btn ' + (HX24_MODE === 'ages' ? '' : 'ghost') + '" id="hx24-ages">Âge des équipements</button>' +
    '<a class="btn ghost" href="#/tableaux">Retour à l’arborescence</a></div>' +
    '<div class="row" style="margin:12px 0;gap:8px;flex-wrap:wrap">' +
    '<input class="f" id="hx24-query" type="search" value="' + esc(HX24_QUERY) +
    '" placeholder="Rechercher TS, départ, local, année…" style="flex:1;min-width:170px">' +
    (HX24_MODE === 'departs' ? '<select class="f" id="hx24-board"><option value="tous">Tous les TGBT</option>' +
      [1,2,4].map(n => '<option value="' + n + '"' + (HX24_BOARD === String(n) ? ' selected' : '') +
      '>TGBT ' + n + '</option>').join('') + '</select>' : '') + '</div>' +
    '<div class="list card glass" id="hx24-list">' +
    (HX24_MODE === 'departs' ? depts.map(hx24Card).join('') : ages.map(hx24Age).join('')) + '</div>' +
    '<p class="small muted">Provenance : Distribution électrique 2024.xlsx, feuilles INDEX et Age equipement. Les années ou libellés erronés sont conservés tels que saisis pour assurer la traçabilité.</p>';
  const filter = () => {
    const q = norm(HX24_QUERY);
    $$('.hx24entry', $('#hx24-list')).forEach(el => {
      const goodBoard = HX24_MODE !== 'departs' || HX24_BOARD === 'tous' || el.dataset.hxBoard === HX24_BOARD;
      el.style.display = goodBoard && (!q || el.dataset.hxQ.includes(q)) ? '' : 'none';
    });
  };
  $('#hx24-query').oninput = e => { HX24_QUERY = e.target.value; filter(); };
  if ($('#hx24-board')) $('#hx24-board').onchange = e => { HX24_BOARD = e.target.value; filter(); };
  $('#hx24-departs').onclick = () => { HX24_MODE = 'departs'; vHistorique2024(); };
  $('#hx24-ages').onclick = () => { HX24_MODE = 'ages'; vHistorique2024(); };
  filter();
}
