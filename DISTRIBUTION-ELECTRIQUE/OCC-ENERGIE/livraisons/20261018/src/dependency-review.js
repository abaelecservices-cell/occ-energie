function dependencyInformation(board) {
  const review=D.dependencyReview;
  if(!review || !board)return '';
  const outgoing=review.departures.filter(row=>row.board===board.id);
  const incoming=review.departures.flatMap(row=>row.links.filter(link=>link.target===board.id).map(link=>({row,link})));
  const label=status=>({modele_documente:'liaison présente dans le modèle documentaire',a_recouper:'mention à recouper ; câble non établi',tableau_non_repertorie:'tableau cité sans fiche identifiée'})[status];
  const destination=link=>BOARD[link.target]?`<a href="#/b/${esc(link.target)}">${esc(BOARD[link.target].name)}</a>`:esc(link.target);
  const photographs=(D.photoReadingReview?.photographicDependencies || []).filter(row=>row.fromBoard===board.id || row.target===board.id);
  return `<details class="card glass" style="margin:12px 0"><summary><b>Croisement des dépendances — ${outgoing.length} départs</b></summary>
    <p class="small">Les mentions et repères partagés servent au recoupement. Seules les liaisons déjà documentées participent au réseau ; aucune dépendance n’est ajoutée par ressemblance de libellé.</p>
    ${photographs.length?`<h4>Repérages photographiques recoupés</h4><ul>${photographs.map(row=>`<li><a href="#/b/${esc(row.fromBoard)}">${esc(row.fromBoard)}</a> · ${esc(row.case)} → <a href="#/b/${esc(row.target)}">${esc(row.target)}</a><p>${esc(row.limit)}</p><span class="src">${esc(row.sources.join(' ; '))}</span></li>`).join('')}</ul>`:''}
    <h4>Amonts citant cette armoire</h4>${incoming.length?`<ul>${incoming.map(({row,link})=>`<li><a href="#/b/${esc(row.board)}">${esc(BOARD[row.board]?.name || row.board)}</a> — <a href="#" data-open="${esc(row.id)}">${esc(row.label)}</a>${row.case?' · case '+esc(row.case):''}<br><span class="src">${label(link.status)} · ${esc(row.source || row.xl?.ref || 'source à préciser')}</span></li>`).join('')}</ul>`:'<p>Aucun départ amont correspondant identifié dans ce croisement.</p>'}
    <details><summary>Départs et armoires aval</summary><ul>${outgoing.map(row=>`<li><a href="#" data-open="${esc(row.id)}">${esc(row.label)}</a>${row.case?' · case '+esc(row.case):''}${row.links.length?`<ul>${row.links.map(link=>`<li>${destination(link)} — ${label(link.status)}</li>`).join('')}</ul>`:''}<span class="src">${esc(row.xl?.ref || row.source || 'source à préciser')}</span></li>`).join('')}</ul></details>
  </details>`;
}
