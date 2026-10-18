function physicalCabinetSVG(f) {
  const p=f.physical;
  const rectangle=(x,y,w,h,fill,extra='')=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${p.edge}" stroke-width="3" ${extra}/>`;
  let body=rectangle(0,0,p.width,p.height,p.frame);
  for(const leaf of p.leaves){
    body+=rectangle(leaf.x,leaf.y,leaf.w,leaf.h,leaf.fill || p.panel,leaf.fixed?'data-fixed-panel="true"':'data-physical-door="true"');
  }
  for(const lock of p.locks || [])body+=`<circle cx="${lock[0]}" cy="${lock[1]}" r="10" fill="#bec5c0" stroke="#4a514d" stroke-width="3"/><circle cx="${lock[0]}" cy="${lock[1]}" r="4" fill="#303a36"/>`;
  for(const part of p.parts){
    let drawing=physicalPartSVG(part);
    if(part.node)drawing=`<g class="hit" data-id="${esc(part.node)}"><title>${esc(NODE[part.node]?.label || part.node)}</title>${drawing}</g>`;
    body+=drawing;
  }
  return `<svg viewBox="-30 -110 ${p.width+60} ${p.height+170}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${esc(f.title)} — restitution des portes et commandes observées"><title>${esc(f.title)}</title><text x="0" y="-60" font-size="30" fill="currentColor" font-family="Arial,sans-serif">${esc(f.title)}</text>${body}<text x="0" y="${p.height+38}" font-size="16" fill="currentColor">${esc(p.caption)}</text></svg>`;
}
