function secondaryNetworkPanel(width, top) {
  const nodes = D.nodes.filter(n => n.stage === 'secondary');
  const columns = 4, cellWidth = (width - 100) / columns;
  let svg = `<text x="50" y="${top + 28}" fill="currentColor" font-size="18" font-weight="700">Transformateurs secondaires repérés au plan SS1</text>
    <text x="50" y="${top + 55}" fill="currentColor" font-size="13">Distincts des deux transformateurs HTA qui alimentent le TGBT8. Départs et caractéristiques restant à confirmer.</text>`;
  nodes.forEach((node, i) => {
    const x = 50 + (i % columns) * cellWidth, y = top + 80 + Math.floor(i / columns) * 116;
    svg += `<g class="hit" data-id="${node.id}"><rect x="${x}" y="${y}" width="${cellWidth - 16}" height="98" rx="10" fill="none" stroke="currentColor" stroke-dasharray="6 4"/>
      <text x="${x + 12}" y="${y + 26}" fill="currentColor" font-size="12" font-weight="700">${esc(node.label)}</text>
      <text x="${x + 12}" y="${y + 50}" fill="currentColor" font-size="11">${esc(BOARD[node.board].name)}</text>
      <text x="${x + 12}" y="${y + 74}" fill="currentColor" font-size="11">Repère documentaire — raccordement à confirmer</text></g>`;
  });
  return {svg, height: 90 + Math.ceil(nodes.length / columns) * 116};
}
