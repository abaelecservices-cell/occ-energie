/* OCC Énergie — compléments documentaires SAP / terrain.
   Cette vue ne crée jamais de nœud électrique ni de liaison de puissance.
   Les éléments SAP sont des références de maintenance, pas des départs validés. */
let OC_SECTION = 'manques', OC_QUERY = '';

function vComplements(selection) {
  const data = D.referentielSAP;
  if (!data) {
    VIEW().innerHTML = '<h1>Compléments OCC Énergie</h1><div class="banner danger">Référentiel SAP non intégré à cette version.</div>';
    return;
  }
  if (selection) { OC_SECTION = 'sap'; OC_QUERY = String(selection); }
  const escaped = x => esc(x == null ? '' : x);
  const headline = (str, cls = '') => '<span class="pill ' + cls + '">' + escaped(str) + '</span>';
  const classes = { nouveau_repere: ['À rapprocher', 'a'], facade_a_qualifier: ['Façade à qualifier', 'a'],
    alias_a_confirmer: ['Alias à confirmer', 'r'], deja_documente: ['Documenté (réception)', 'b'] };
  const catalog = () => data.tableaux.map(t => {
    const [text, cls] = classes[t.statut] || ['Non validé', 'a'];
    const hay = norm([t.sap, t.repere, t.libelle, t.note, text].join(' '));
    return '<div class="li oc-row" data-oc="' + escaped(hay) + '">' +
      '<div class="grow"><b>' + escaped(t.repere) + '</b> — ' + escaped(t.libelle) +
      '<div class="small muted">SAP ' + escaped(t.sap) + ' · ' + escaped(t.source_page) + '</div>' +
      '<div class="small">' + escaped(t.note) + '</div></div>' + headline(text, cls) + '</div>';
  }).join('');
  const tasks = () => data.complements.map(c => {
    const hay = norm([c.id, c.priorite, c.ensemble, c.objectif, c.preuve, c.photo].join(' '));
    return '<details class="card glass oc-row" data-oc="' + escaped(hay) + '" style="margin-bottom:8px;padding:12px">' +
      '<summary><span class="pill ' + (c.priorite === 'A' ? 'r' : 'a') + '">' +
      escaped(c.priorite + ' · ' + c.id) + '</span> <b>' + escaped(c.ensemble) +
      '</b><div class="small muted" style="margin:5px 0 0">' + escaped(c.objectif) + '</div></summary>' +
      '<div class="small" style="margin-top:10px"><b>Preuve attendue :</b> ' + escaped(c.preuve) +
      '<p><b>Photo :</b> ' + escaped(c.photo) + '</p>' +
      '<p class="muted">Statut : liaison ou correspondance non certifiée ; ne pas utiliser pour une manœuvre.</p></div></details>';
  }).join('');
  const faces = () => data.facades_a_qualifier.map(f => {
    const hay = norm([f.repere, f.libelle, f.note].join(' '));
    return '<div class="li oc-row" data-oc="' + escaped(hay) + '">' +
      '<div class="grow"><b>' + escaped(f.repere) + '</b> — ' + escaped(f.libelle) +
      '<div class="small muted">' + escaped(f.note) + '</div></div>' + headline('Vérifier archives', 'a') + '</div>';
  }).join('');
  const sectionButton = (id, label, count) =>
    '<button class="btn ' + (OC_SECTION === id ? '' : 'ghost') + '" data-oc-tab="' + id + '">' +
    escaped(label) + ' (' + count + ')</button>';
  VIEW().innerHTML = '<h1>Compléments OCC Énergie</h1>' +
    '<p class="sub">Références SAP et informations manquantes, intégrées à l’application existante.</p>' +
    '<div class="banner info">📋<div><b>Référentiel documentaire — non validé électriquement.</b> ' +
      'Un repère SAP ne prouve ni l’identité physique exacte, ni l’alimentation, ni l’état d’un appareil. ' +
      'Aucune liaison électrique, façade fictive ou consigne de manœuvre n’est créée.</div></div>' +
    '<div class="row" style="flex-wrap:wrap;gap:8px;margin:12px 0">' +
      sectionButton('manques', 'Liaisons à qualifier', data.complements.length) +
      sectionButton('sap', 'Index SAP', data.tableaux.length) +
      sectionButton('facades', 'Façades à vérifier', data.facades_a_qualifier.length) +
    '</div>' +
    '<input class="f" id="oc-query" type="search" value="' + escaped(OC_QUERY) +
    '" placeholder="Rechercher : TS24, 101490, groupe, 20 kV..." style="width:100%;margin-bottom:12px">' +
    (OC_SECTION === 'sap' ? '<div class="list card glass">' + catalog() + '</div>' :
      OC_SECTION === 'facades' ? '<div class="list card glass">' + faces() + '</div>' : tasks()) +
    '<p class="small muted">Sources : SAP distrib. élec. (pages 4–5), classeur 2024 et relevés du 15–16 octobre 2026. ' +
      'Règle : rechercher les photos déjà reçues avant de refaire une prise de vue. ' +
      'Une preuve électrique contradictoire reste à vérifier sur le terrain ou sur un schéma à jour.</p>' +
    '<div class="row"><a class="btn ghost" href="#/tableaux">← Revenir aux tableaux</a>' +
      '<a class="btn ghost" href="#/registre">Registre des écarts</a></div>' + footer();
  const apply = () => {
    const q = norm(OC_QUERY);
    $$('.oc-row', VIEW()).forEach(el => { el.style.display = !q || el.dataset.oc.includes(q) ? '' : 'none'; });
  };
  $('#oc-query').oninput = e => { OC_QUERY = e.target.value; apply(); };
  $$('[data-oc-tab]', VIEW()).forEach(b => b.onclick = () => {
    OC_SECTION = b.dataset.ocTab;
    OC_QUERY = '';
    vComplements();
  });
  apply();
}
