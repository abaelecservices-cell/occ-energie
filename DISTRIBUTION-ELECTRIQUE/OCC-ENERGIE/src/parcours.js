/* Parcours documentaire continu : depart -> reseau -> zone -> plan -> facade.
   Les traits traces sont ceux reellement dessines par le schema.
   Aucune position, liaison ou configuration electrique n'est inferee comme certifiee. */

function parcoursContext(id) {
  const node = NODE[id] || null, board = BOARD[id] || boardOf(node);
  const locId = (board && board.loc) || (node && node.loc);
  const locs = locChain(locId);
  const place = locs.slice().reverse().find(l => l.bat !== undefined && l.bat !== null);
  const zone = place ? D.site.zones.find(z => String(z.n) === String(place.bat)) : null;
  const facade = node ? facadeFor(id) : null;
  const facadeBoard = facade ? boardForFacade(facade) : null;
  const plan = board ? planFor(board.id) : null;
  return { node, board, locs, place, zone, facade, facadeBoard, plan };
}

function parcoursPath(id) {
  if (!NODE[id]) return null;
  const path = bestPath(id);
  if (!path) return null;
  const chain = path.slice().reverse();
  const uncertain = {};
  chain.forEach((key, i) => {
    const n = NODE[key];
    const a = i ? chain[i - 1] : null;
    const edge = a && D.edges.find(e =>
      (e.a === a && e.b === key) || (e.b === a && e.a === key));
    uncertain[key] = !n || n.conf !== 'confirme' ||
      (i > 0 && (!edge || edge.conf !== 'confirme'));
  });
  return { chain, uncertain, alternatives: upPaths(id, 16).length };
}

function parcoursSummary(id) {
  const n = NODE[id], ctx = parcoursContext(id);
  const path = parcoursPath(id);
  const chain = path ? path.chain.map(key =>
    '<button type="button" class="trace-step ' +
    (path.uncertain[key] ? 'trace-doubt' : '') +
    '" data-open="' + esc(key) + '" title="' + esc(NODE[key].label) + '">' +
    esc(short(NODE[key])) + '</button>').join('<span class="trace-arrow">→</span>') :
    '<span class="muted">Pas de chemin complet jusqu’à une source dans le modèle.</span>';
  const doubtful = path && path.chain.some(key => path.uncertain[key]);
  const siteButton = ctx.zone ?
    '<button class="btn" type="button" data-go="#/site/' + esc(id) +
    '">📍 Localiser sur l’usine →</button>' :
    '<span class="pill a">Bâtiment non localisable avec les données actuelles</span>';
  const facadeButton = ctx.facade && ctx.facadeBoard ?
    '<button class="btn ghost" type="button" data-go="#/b/' + esc(ctx.facadeBoard) +
    '/f/' + esc(id) + '">▦ Voir la case sur la façade</button>' :
    '<span class="small muted">Case de façade non documentée.</span>';
  return '<section id="net-path" class="trace-summary" data-path-target="' + esc(id) + '">' +
    '<b>Chaîne d’alimentation documentaire</b> ' +
    (path && path.alternatives > 1 ? '<span class="pill a">Plusieurs parcours théoriques</span>' : '') +
    (doubtful ? '<span class="pill a">Certaines liaisons à confirmer</span>' : '') +
    '<div class="trace-steps">' + chain + '</div>' +
    '<div class="row" style="margin-top:10px">' + siteButton + facadeButton + '</div>' +
    '<p class="small muted" style="margin:8px 0 0">Trajet déduit des documents et du régime normal décrit, jamais de la position réelle des appareils. Les liaisons incertaines sont indiquées en pointillé orange.</p></section>';
}

function parcoursHighlight(id) {
  const svg = $('#hta svg');
  if (!svg) return;
  svg.querySelectorAll('.trace-node,.trace-wire,.trace-doubt').forEach(el => {
    el.classList.remove('trace-node', 'trace-wire', 'trace-doubt');
  });
  const path = parcoursPath(id);
  if (!path) return;
  path.chain.forEach(key => {
    svg.querySelectorAll('[data-id]').forEach(el => {
      if (el.dataset.id !== key) return;
      el.classList.add('trace-node');
      if (path.uncertain[key]) el.classList.add('trace-doubt');
    });
    svg.querySelectorAll('[data-wire-id]').forEach(el => {
      if (el.dataset.wireId !== key) return;
      el.classList.add('trace-wire');
      if (path.uncertain[key]) el.classList.add('trace-doubt');
    });
  });
}

/* Vue aérienne ciblée. Seules les zones dotées d'un repère bat
   explicite dans le modèle peuvent être mises en évidence. */
function vSite(id) {
  const ctx = parcoursContext(id);
  if (!ctx.node && !ctx.board) { vHome(); return; }
  const name = ctx.node ? ctx.node.label : ctx.board.name;
  const where = ctx.locs.length ? ctx.locs.map(l => l.name).join(' › ') : 'Non documentée';
  const siteLabel = ctx.zone ? (ctx.zone.label || ctx.zone.name) : null;
  const conf = ctx.board ? (ctx.board.loc_conf || 'inconnu') : (ctx.node.conf || 'inconnu');
  const planButton = ctx.plan && ctx.board ?
    '<button class="btn" id="site-continue-plan" data-go="#/plans/' +
    esc(ctx.plan) + '/' + esc(ctx.board.id) + '/' + esc(id) +
    '">Voir l’implantation du tableau →</button>' :
    '<span class="pill a">Position sur plan de local non renseignée</span>';
  const faceButton = ctx.facade && ctx.facadeBoard ?
    '<button class="btn ghost" id="site-direct-facade" data-go="#/b/' +
    esc(ctx.facadeBoard) + '/f/' + esc(id) + '">Voir le départ sur la façade →</button>' :
    '<span class="small muted">Aucun départ exact identifié sur une façade.</span>';
  VIEW().innerHTML = '<h1>Implantation géographique — ' + esc(name) + '</h1>' +
    '<p class="sub">Localisation documentaire du départ sélectionné, sans changer de repère.</p>' +
    '<div class="card glass" style="margin:10px 0;padding:14px">' +
    '<b>' + esc(ctx.board ? ctx.board.name : name) + '</b> ' + confPill(conf) +
    '<div class="small" style="margin:8px 0">Localisation : ' + esc(where) + '</div>' +
    (siteLabel ? '<div class="small"><b>Bâtiment ciblé : ' + esc(siteLabel) + '</b> (repérage documentaire)</div>' :
      '<div class="banner info">Aucun bâtiment géolocalisé pour ce départ : la carte reste générale et aucun halo n’est ajouté.</div>') +
    '<div class="row" style="margin-top:10px">' +
    '<button class="btn ghost" data-go="#/reseau/' + esc(id) + '">← Retour au réseau</button>' +
    planButton + faceButton + '</div></div>' +
    '<div id="site-map" class="sitemap" style="--ar:' + esc(D.site.ratio) + '"></div>' +
    '<p class="small muted">La vue aérienne montre le bâtiment documenté, non le chemin physique des câbles. Cliquer sur un autre bâtiment ouvre sa fiche. Les positions restent à confirmer sur site.</p>' +
    footer();
  mountViewer($('#site-map'), siteSVG(), {
    focus: ctx.zone ? 'Z' + ctx.zone.n : null,
    onClick: key => { if (key && key.startsWith('Z')) openZone(key.slice(1)); },
    native: D.site.tiles ? 1000 / D.site.w : null
  });
  if (D.site.tiles) orthoTiles($('#site-map svg'), D.site);
}

function parcoursPlanActions(focus, selected) {
  const n = NODE[selected], b = BOARD[focus];
  if (!n || !b) return '';
  const facade = facadeFor(n.id), targetBoard = facade ? boardForFacade(facade) : null;
  const btn = targetBoard ?
    '<button id="plan-to-facade" class="btn" data-go="#/b/' + esc(targetBoard) + '/f/' +
    esc(n.id) + '">Ouvrir la façade et surligner le départ →</button>' :
    '<span class="pill a">Position exacte sur la façade non documentée</span>';
  return '<div class="card glass" id="plan-selected" style="padding:12px;margin:8px 0">' +
    '<b>Départ sélectionné : ' + esc(short(n)) + '</b><div class="small">' +
    esc(b.name) + (n.case ? ' · case ' + esc(n.case) : '') +
    '</div><div class="row" style="margin-top:8px">' + btn +
    '<button class="btn ghost" data-go="#/site/' + esc(n.id) +
    '">← Retour à la vue aérienne</button></div></div>';
}
