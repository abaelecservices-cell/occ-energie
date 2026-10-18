function projectImportHTML(board) {
  const item=board?.projectImport;
  if(!item)return '';
  const additions=item.distribution.filter(row=>row.status!=='identique');
  const rows=item.distribution.map(row=>`<li><b>${esc(row.text)}</b><br><span class="src">${esc(row.sheet)} · ${esc(row.cell)} · ${row.status==='identique'?'déjà recoupé':'mention complémentaire'}${row.parent?' · rubrique '+esc(row.parent):''}</span></li>`).join('');
  return `<details class="card glass" style="margin:12px 0"><summary><b>Repères et informations complémentaires</b></summary>
    ${item.notes.map(note=>`<p>${esc(note.text)}<br><span class="src">${esc(note.source)} · information documentaire à recouper</span></p>`).join('')}
    ${additions.map(row=>`<p><b>Intitulé complémentaire :</b> ${esc(row.text)}<br><span class="src">${esc(row.source)} · ${esc(row.sheet)} · ${esc(row.cell)}. ${esc(row.basis)}</span></p>`).join('')}
    ${rows?`<details><summary>Repères du classeur (${item.distribution.length})</summary><p class="small">Mentions regroupées par onglet ; elles ne constituent pas un relevé des câbles.</p><ul>${rows}</ul></details>`:''}
    ${item.documentNames.length?`<details><summary>Références documentaires</summary><ul>${item.documentNames.map(name=>`<li>${esc(name)}</li>`).join('')}</ul></details>`:''}
    <a class="btn ghost" href="docs/facades-vectors/${encodeURIComponent(board.id)}.svg">Ouvrir l’armoire vectorielle</a>
  </details>`;
}
function projectImportBanner() {
  const info=D.projectImport;
  return info?`<div class="card glass"><h3>Armoires et arborescence</h3><p>${esc(info.scope)}</p><a class="btn ghost" href="docs/COMPLEMENTS-20261018.html">Armoires vectorielles et repères complémentaires</a></div>`:'';
}
