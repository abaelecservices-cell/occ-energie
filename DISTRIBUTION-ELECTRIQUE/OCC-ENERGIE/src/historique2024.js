/* OCC Énergie — index du classeur 2024 / comparaison documentaire.
 * Couche historique indépendante : aucune arête, aucun appareillage et aucune règle
 * de simulation ne sont créés ou modifiés à partir des observations ci-dessous. */
let HX24_MODE = 'departs', HX24_BOARD = 'tous', HX24_QUERY = '';

function hx24Candidates(r) {
  const bid = 'TGBT' + r.tgbt, nodes = DEPS_BY_BOARD[bid] || [];
  const loc = n => colOf(n);
  const atCase = nodes.filter(n => {
    const c = loc(n);
    return c && +c.col === +r.colonne && +c.pos === +r.case;
  });
  const sameSide = atCase.filter(n => n.half === r.cote);
  if (sameSide.length) return { status: 'meme_case_et_cote', nodes: sameSide, detail: 'Même position documentaire' };
  if (atCase.length) return { status: 'cote_contradictoire', nodes: atCase, detail: 'Même colonne/case, mais côté différent' };

  // Rapprochement de repli : numéro TS strict (TS1 != TS10, TS42 != TS43).
  const code = String(r.ts || '').replace(/\s+/g, '').toUpperCase();
  if (/^TS\d+[AB]?$/.test(code)) {
    const tail = code.slice(2);
    const rx = new RegExp('(^|[^A-Z0-9])TS\\s*' + tail + '(?=$|[^A-Z0-9])', 'i');
    const related = nodes.filter(n => rx.test(String(n.label || '') + ' ' + String(n.rep || '')));
    if (related.length) return { status: 'ts_autre_case', nodes: related, detail: 'Même repère TS, autre position ou case absente' };
  }
  return { status: 'non_rapproche', nodes: [], detail: 'Aucune correspondance documentaire trouvée' };
}
function hx24Alerts(r) {
  const key = [r.tgbt, r.cote, r.colonne, r.case].join(':');
  const notes = {
    '2:B:6:36': 'Écart connu : l’index 2024 indique TS12 ; une photographie du TGBT 2 documentée au Registre montre « RÉSERVE » sur cette case. Destination actuelle à vérifier sur le terrain.',
    '2:B:2:36': 'L’index 2024 classe TS2A côté B ; le dossier technique du TGBT 2 positionne la case 2-36 côté A. Contradiction documentaire à signaler, sans changer la liaison.',
    '4:B:7:10': 'L’index 2024 indique TS24A des deux côtés du TGBT 4 (2-10 A et 7-10 B). Établir les deux destinations exactes avant tout regroupement.',
    '4:A:4:28': 'L’index 2024 situe TS42 côté A en 4-28 ; le modèle actuel comporte un départ en cette case mais rattaché au côté B. Ne pas déplacer de départ sans schéma et relevé confirmé.'
  };
  return notes[key] || '';
}
function hx24Card(r) {
  const result = hx24Candidates(r);
  const statusClass = result.status === 'meme_case_et_cote' ? 'b' :
    result.status === 'non_rapproche' ? 'r' : 'a';
  const links = result.nodes.map(n => '<a href="#" data-open="' + esc(n.id) + '">' +
    esc(short(n)) + '</a>' + (n.case ? ' <span class="muted">(' + esc(n.case) +
    ', côté ' + esc(n.half || '?') + ')</span>' : '')).join(' · ');
  const notice = hx24Alerts(r);
  return '<div class="li hx24entry" data-hx-board="' + esc(r.tgbt) +
    '" data-hx-q="' + esc(norm([r.ts,r.designation,r.lieu,r.tgbt,r.cote,r.colonne,r.case,
      ...result.nodes.map(n => n.label)].join(' '))) + '">' +
    '<div class="grow"><b>TGBT ' + r.tgbt + ' · ' + esc(r.cote) + ' · case ' +
    esc(r.colonne + '-' + r.case) + '</b> ' +
    '<span class="pill ' + statusClass + '">' + esc(result.detail) + '</span>' +
    '<div><b>2024 :</b> ' + esc(r.designation) +
    (r.ts ? ' <span class="muted">(' + esc(r.ts) + ')</span>' : '') + '</div>' +
    '<div class="small muted">Emplacement 2024 : ' + esc(r.lieu || 'Non renseigné') + '</div>' +
    '<div class="small"><b>Modèle de l’application :</b> ' +
    (links || '<span class="muted">Aucune correspondance démontrée</span>') + '</div>' +
    (notice ? '<p class="small" style="margin:5px 0 0"><span class="pill a">Écart connu</span> ' + esc(notice) + '</p>' : '') +
    '</div><a class="btn ghost mini" href="#/b/TGBT' + r.tgbt + '">Tableau →</a></div>';
}
function hx24Age(r, all) {
  const year = r.anneeMiseEnService2024;
  const dup = all.filter(x => x.equipement === r.equipement).length > 1;
  const anomaly = r.anomalieSaisie || dup;
  return '<div class="li hx24entry" data-hx-board="age" data-hx-q="' +
    esc(norm([r.equipement,r.sousStation2024,r.anneeBrute2024].join(' '))) + '">' +
    '<div class="grow"><b>' + esc(r.equipement) + '</b>' +
    '<div class="small muted">Sous-station selon le tableau 2024 : ' +
    esc(r.sousStation2024) + '</div>' +
    (dup ? '<div class="small">Référence dupliquée dans la source : identité exacte à vérifier.</div>' : '') +
    '</div><span class="pill ' + (anomaly ? 'a' : '') + '">' +
    (r.anomalieSaisie ? 'Année incohérente : ' + esc(r.anneeBrute2024) :
     year ? esc(year) : 'Année absente') + '</span></div>';
}
function vHistorique2024() {
  const h = D.historique2024;
  if (!h) { VIEW().innerHTML = '<h1>Référentiel 2024</h1><div class="banner danger">Référentiel historique absent de cette version.</div>'; return; }
  const depts = h.departIndex2024 || [], ages = h.ageEquipements2024 || [];
  const result = depts.map(hx24Candidates);
  const count = id => result.filter(x => x.status === id).length;
  VIEW().innerHTML = '<h1>Référentiel Excel 2024</h1>' +
    '<p class="sub">Comparaison historique avec le modèle électrique OCC Énergie. Aucun rapprochement ne vaut validation terrain.</p>' +
    '<div class="banner info">📚<div><b>Archive 2024, non état actuel de l’installation.</b> La concordance d’une case ne confirme pas son équipement ni son alimentation. Les divergences de côté, les réaffectations et les données manquantes sont conservées pour examen, sans consigne de manœuvre.</div></div>' +
    '<div class="row" style="margin:12px 0;gap:8px;flex-wrap:wrap">' +
    '<span class="pill">' + depts.length + ' départs 2024</span>' +
    '<span class="pill">' + count('meme_case_et_cote') + ' cases/côtés concordants</span>' +
    '<span class="pill a">' + count('cote_contradictoire') + ' côtés divergents</span>' +
    '<span class="pill a">' + count('ts_autre_case') + ' TS autre position</span>' +
    '<span class="pill r">' + count('non_rapproche') + ' sans correspondance</span>' +
    '<span class="pill">' + ages.length + ' historiques d’équipements</span></div>' +
    '<div class="row" style="margin:12px 0;gap:8px;flex-wrap:wrap">' +
    '<button class="btn ' + (HX24_MODE === 'departs' ? '' : 'ghost') + '" id="hx24-departs">Départs 2024</button>' +
    '<button class="btn ' + (HX24_MODE === 'ages' ? '' : 'ghost') + '" id="hx24-ages">Âge des équipements</button>' +
    '<a class="btn ghost" href="#/tableaux">Retour à l’arborescence</a></div>' +
    '<div class="row" style="margin:12px 0;gap:8px;flex-wrap:wrap">' +
    '<input class="f" id="hx24-query" type="search" value="' + esc(HX24_QUERY) +
    '" placeholder="Rechercher TS, équipement, case ou année…" style="flex:1;min-width:170px">' +
    (HX24_MODE === 'departs' ? '<select class="f" id="hx24-board"><option value="tous">Tous les TGBT</option>' +
      [1,2,4].map(n => '<option value="' + n + '"' + (HX24_BOARD === String(n) ? ' selected' : '') +
      '>TGBT ' + n + '</option>').join('') + '</select>' : '') + '</div>' +
    '<div class="list card glass" id="hx24-list">' +
    (HX24_MODE === 'departs' ? depts.map(hx24Card).join('') :
      ages.map(r => hx24Age(r, ages)).join('')) + '</div>' +
    '<p class="small muted">Sources : Distribution électrique 2024.xlsx › INDEX (lignes 5–40) et Age equipement (lignes 2–69). Les anomalies de saisie sont préservées. Le rapprochement de case est informatique ; les liaisons du graphe restent indépendantes.</p>';
  const filter = () => {
    const q = norm(HX24_QUERY);
    $$$('.hx24entry', $('#hx24-list')).forEach(el => {
      const right = HX24_MODE !== 'departs' || HX24_BOARD === 'tous' ||
        el.dataset.hxBoard === HX24_BOARD;
      el.style.display = right && (!q || el.dataset.hxQ.includes(q)) ? '' : 'none';
    });
  };
  $('#hx24-query').oninput = e => { HX24_QUERY = e.target.value; filter(); };
  if ($('#hx24-board')) $('#hx24-board').onchange = e => { HX24_BOARD = e.target.value; filter(); };
  $('#hx24-departs').onclick = () => { HX24_MODE = 'departs'; vHistorique2024(); };
  $('#hx24-ages').onclick = () => { HX24_MODE = 'ages'; vHistorique2024(); };
  filter();
}
