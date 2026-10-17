function equipmentAuditHTML(board) {
  const audit = board?.audit;
  if (!audit) return '';
  return `<section class="card glass small" style="margin:12px 0" aria-label="État de vérification documentaire">
    <b>Contrôle du ${esc(audit.date)} : ${esc(audit.label)}</b>
    <p>${esc(audit.locations)}</p>
    <details><summary>Résultats du contrôle et limites</summary>
      <p><b>Identité :</b> ${esc(audit.identity)}</p>
      <p><b>Façade :</b> ${esc(audit.facade)}</p>
      <p><b>Alimentation :</b> ${esc(audit.network)}</p>
      <p><b>Source de comparaison :</b> ${esc(audit.source)}</p>
      <ul>${audit.findings.map(item => `<li>${esc(item)}</li>`).join('')}</ul>
      <p>${esc(audit.browser)}</p>
    </details>
    <a href="docs/facades-vectors/${board.id}.svg" target="_blank" rel="noopener">Ouvrir la représentation vectorielle</a>
  </section>`;
}
