function documentEvidenceHTML(board) {
  if (!board) return '';
  const evidence = board.crossEvidence || [];
  const documents = board.sourceDocuments || [];
  const labels = board.labels2024 || [];
  const consumers = board.scanConsumers;
  const history = board.equipmentHistory || [];
  const imported = typeof projectImportHTML === 'function' ? projectImportHTML(board) : '';
  if (!evidence.length && !documents.length && !labels.length) return imported;
  return `${imported}<details class="card glass" style="margin:12px 0"><summary><b>Documents croisés et écarts (${documents.length} PDF)</b></summary>
    ${evidence.map(item => `<p><b>${item.kind === 'conflit' ? 'Écart documentaire' : 'Recoupement'} :</b> ${esc(item.text)}<br><span class="src">${esc(item.source)}</span></p>`).join('')}
    ${labels.length ? `<details><summary>Libellés du classeur 2024 (${labels.length})</summary><p class="small">Transcription des objets du schéma ; une mention ancienne ne remplace pas une plaque récente.</p><ul>${labels.map(label => `<li>${esc(label)}</li>`).join('')}</ul></details>` : ''}
    ${consumers ? `<details><summary>Consommateurs du scan (${consumers.items.length} entrées)</summary><p>${esc(consumers.source)} · ${esc(consumers.status)}</p><ul>${consumers.items.map(item => `<li>${esc(item)}</li>`).join('')}</ul></details>` : ''}
    ${history.length ? `<details><summary>Historique documentaire des équipements</summary><ul>${history.map(item => `<li>${esc(item.label)} : mise en service ${esc(item.commissioned || 'non renseignée')} ; dernière maintenance ${esc(item.maintenance || 'non renseignée')}<br><span class="src">${esc(item.source)}</span></li>`).join('')}</ul></details>` : ''}
    <ul>${documents.map(doc => `<li>${esc(doc.name)} · ${doc.pages} page(s)</li>`).join('')}</ul>
    <p>Les documents originaux sont conservés dans les archives du dossier livré.</p>
  </details>`;
}
function documentReviewBanner() {
  const review = D.documentReview;
  if (!review) return '';
  return `${typeof projectImportBanner === 'function' ? projectImportBanner() : ''}<details class="card glass" style="margin:12px 0"><summary><b>Recoupement documentaire et limites</b></summary>
    <p>${review.xlsmReferencesChecked} références du classeur XLSM recoupées ; ${review.xlsmDifferences} écart de transcription. ${review.catalog.length} PDF conservés dans le dossier livré.</p>
    <p>${esc(review.scope)}</p>
    <p><a href="docs/VECTORIELLES.html" target="_blank" rel="noopener">Représentations vectorielles des 68 équipements et limites documentaires</a></p>
    <ul>${D.boards.filter(board => (board.crossEvidence || []).some(item => item.kind === 'conflit')).map(board => `<li><a href="#/b/${board.id}">${esc(board.name)}</a> : contradiction entre sources</li>`).join('')}</ul>
    <a class="btn ghost" href="docs/COMPLEMENTS-20261018.html" target="_blank" rel="noopener">Consulter les armoires vectorielles et les repères</a>
  </details>`;
}
