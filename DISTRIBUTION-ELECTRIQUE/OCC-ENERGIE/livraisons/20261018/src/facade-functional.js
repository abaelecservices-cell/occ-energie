function functionalFacadeSVG(f) {
  const units = f.cols.flatMap(column => column.units).filter(unit => unit.dep || unit.node);
  const width = 1500, rowHeight = 120, top = 250;
  const height = top + Math.max(1, units.length) * rowHeight + 100;
  const text = (x,y,value,size=25) => `<text x="${x}" y="${y}" font-family="Arial,sans-serif" font-size="${size}" fill="#23362b">${esc(value)}</text>`;
  const rows = units.map((unit,index) => {
    const id = unit.dep || unit.node, node = NODE[id], y = top + index * rowHeight;
    const title = node?.label || unit.label || id;
    return `<g class="hit" data-id="${id}"><title>${esc(title)}</title><rect x="20" y="${y}" width="1460" height="105" rx="10" fill="#e6eee7" stroke="#a6b5a8"/>${text(45,y+36,title.slice(0,95))}${text(45,y+76,'Repère documentaire : '+id+' — emplacement physique non établi',19)}<rect class="hl" x="20" y="${y}" width="1460" height="105" fill="none"/></g>`;
  }).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Liste documentaire sans implantation physique"><rect width="${width}" height="${height}" fill="#f1f5ef"/>${text(25,55,f.title || 'Équipement',32)}${text(25,112,'LISTE DOCUMENTAIRE — AUCUNE IMPLANTATION PHYSIQUE',27)}${text(25,160,'Les blocs ci-dessous ne représentent ni des portes, ni des tiroirs, ni leur position.',22)}${rows || text(25,top+50,'Aucun appareil détaillé dans les documents attribués.')} ${text(25,height-30,'Ouvrir les documents sources pour les informations disponibles.',20)}</svg>`;
}
