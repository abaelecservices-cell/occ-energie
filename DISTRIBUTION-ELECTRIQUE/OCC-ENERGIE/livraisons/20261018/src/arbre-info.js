function arbreInformation(board) {
  const items = D.nodes.filter(node => node.board === board.id && node.t !== 'bus');
  const fields = node => [
    ['Repère', node.rep], ['Case', node.case || node.cell], ['Appareil', node.model],
    ['Réglage', node.ir], ['Protection', node.prot], ['Puissance', node.kva],
    ['État documentaire', node.documentaryOnly ? 'Repère au plan ; raccordement à confirmer' : CONF[node.conf]?.[1]], ['Alimente', BOARD[node.feeds]?.name],
    ['Source', node.src], ['Classeur', node.xl?.ref], ['Remarque', node.note]
  ].filter(([, value]) => value).map(([label, value]) => `<div><b>${label} :</b> ${esc(value)}</div>`).join('');
  const evidence = board.supplyEvidence;
  const mode = D.facades[board.facade]?.mode;
  return `<div class="card glass small">
    ${mode === 'functional' ? '<p><b>Schéma fonctionnel : les positions physiques ne sont pas relevées.</b></p>' : ''}
    ${board.documentaryOnly ? '<p><b>Fiche documentaire : aucune liaison ajoutée à la simulation.</b></p>' : ''}
    ${evidence ? `<p><b>Alimentation indiquée :</b> ${esc(evidence.text)}<br><span class="src">${esc(evidence.src)} · indication documentaire, raccordement à confirmer</span></p>` : ''}
    ${typeof equipmentAuditHTML === 'function' ? equipmentAuditHTML(board) : ''}
    ${typeof documentEvidenceHTML === 'function' ? documentEvidenceHTML(board) : ''}
    ${board.note ? `<p>${esc(board.note)}</p>` : ''}
    ${(board.obs || []).map(o => `<p>${esc(o.t)}<br><span class="src">${esc(o.src)}${o.d ? ' · ' + esc(o.d) : ''}</span></p>`).join('')}
    ${items.length ? `<details><summary>Appareils et départs (${items.length})</summary><div class="list">${items.map(n => `<details class="card"><summary><a href="#" data-open="${esc(n.id)}">${esc(n.label)}</a>${n.case ? ' · case ' + esc(n.case) : ''}</summary>${fields(n)}</details>`).join('')}</div></details>` : '<p>Aucun départ détaillé dans les sources actuelles.</p>'}
    <details><summary>Références du relevé vectoriel</summary>${photoLinks(board.photos)}${(board.docs || []).map(d => `<p>${esc(d)}</p>`).join('')}</details>
  </div>`;
}
function arbreHTML() {
  ARBRE_SEEN.clear();
  ARBRE_SEEN.add('PL20');
  const connected = connectedArbreHTML();
  const remaining = D.boards.map(board => ARBRE_SEEN.has(board.id) ? '' : arbreBoard(board.id, 1, [], 'Origine non reliée au réseau documenté')).join('');
  return `<p class="small">${D.boards.length} équipements. Dépliez une armoire pour ses départs, cases, réglages, observations et sources. Les branches « plaque » sont documentaires ; elles ne certifient pas un câble et ne participent pas à la simulation.</p>${connected}${remaining ? `<details class="tnode" open><summary>Origines non établies dans le réseau</summary><div class="tkids">${remaining}</div></details>` : ''}`;
}
