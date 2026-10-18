function pl20FacadeSVG(f) {
  const widths = [1000, 500, 500, 750, 750, 500, 500, 1000];
  const total = widths.reduce((sum, width) => sum + width, 0);
  const rect = (x,y,w,h,fill,extra='') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="#82867e" stroke-width="3" ${extra}/>`;
  const text = (x,y,value,size=19,color='#242925') => `<text x="${x}" y="${y}" text-anchor="middle" font-family="Arial,sans-serif" font-size="${size}" fill="${color}">${esc(value)}</text>`;
  const circle = (x,y,r,fill) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="#444" stroke-width="3"/>`;
  const label = (x,y,w,value,fill='#303632',color='#fff') => rect(x,y,w,36,fill)+text(x+w/2,y+25,value,17,color);
  const window = (x,y,w=75,h=120) => rect(x,y,w,h,'#b9bcb5')+rect(x+8,y+8,w-16,h-16,'#343a37');
  const lock = (x,y) => `<path d="M${x} ${y}v-22a18 18 0 0 1 36 0v22" fill="none" stroke="#aaa" stroke-width="7"/>`+rect(x-5,y,46,48,'#8d8a7b','rx="5"');
  const relay = x => rect(x,55,170,215,'#a6a89d')+rect(x+20,80,130,160,'#252b2b')+rect(x+35,94,100,95,'#8993c4')+text(x+85,219,'◆ ◀ ● ▶',15,'#eee')+rect(x+205,75,225,170,'#303a34')+rect(x+220,103,130,38,'#48745d')+rect(x+220,163,130,67,'#ded17c');
  let body = '', x = 0;
  f.cells.forEach((cell,index) => {
    const w=widths[index], end=index===0 || index===7, top=end?0:440;
    let panel=rect(x,top,w,2200-top,'#e8e8dc');
    if(end) {
      panel+=rect(x+6,6,w*.65-9,426,'#e6e5d6')+rect(x+w*.65,6,w*.35-6,426,'#dedfd3')+relay(x+100);
      for(const bx of [x+140,x+270]) panel+=rect(bx-30,-35,60,38,'#42463e')+rect(bx-34,-115,68,88,'#b9292f','rx="25"');
      panel+=circle(x+440,300,5,'#bb3838')+circle(x+475,300,5,'#303b38');
    }
    const head=end?460:490;
    if(index===2 || index===5) panel+=label(x+30,head-55,w-60,index===2?'EDF SECOURS':'CNR NORMAL',index===2?'#272d29':'#b0e3a7',index===2?'#fff':'#1e663c');
    const heading=end?(index===0?'PROTECTION A — SECOURS':'PROTECTION B — NORMAL'):index===1?'COMPTAGE A — SECOURS':index===6?'COMPTAGE B — NORMAL':index===2?'ARRIVÉE A EDF':index===5?'ARRIVÉE B CNR':index===3?'CELLULE PARAFOUDRE A — SECOURS':'CELLULE PARAFOUDRE B — NORMAL';
    panel+=rect(x+12,head,w-24,300,index===2 || index===5?'#eee7a0':'#eeeee4')+label(x+28,head+18,w-56,heading);
    if(cell.t==='CM') panel+=rect(x+100,head+112,w-200,125,'#aaa99a')+rect(x+120,head+133,w-240,80,'#c7c7b8')+text(x+w/2,head+184,'COMPTAGE',18);
    if(end) {
      for(let i=0;i<3;i++) panel+=rect(x+65+i*92,head+128,65,110,'#e8e9df')+rect(x+78+i*92,head+145,40,56,'#a0a8a2');
      for(let i=0;i<6;i++) panel+=circle(x+w*.58+i*52,head+175,18,['#c74238','#c74238','#3b8a6a','#242c27','#242c27','#242c27'][i]);
    }
    const faceY=810, faceH=590;
    panel+=rect(x+15,faceY,w-30,faceH,'#303639')+rect(x+w-150,faceY+25,115,95,'#a6aa61');
    if(end) panel+=`<path d="M${x+w*.5} ${faceY}v${faceH}" stroke="#92988f" stroke-width="3"/>`;
    const mid=x+(end?w*.30:w*.48);
    panel+=`<path d="M${mid} ${faceY+150}v130m0 75v170M${mid} ${faceY+280}l50 65" stroke="#d7dfd8" stroke-width="5" fill="none"/>`;
    if(cell.t==='CM') panel+=circle(mid,faceY+478,22,'none')+circle(mid,faceY+510,22,'none');
    if(cell.t==='PF') panel+=rect(mid-14,faceY+410,28,55,'none')+text(mid,faceY+454,'ϟ',31,'#e6e7db');
    panel+=rect(x+w-155,faceY+260,125,270,'#95988f')+rect(x+w-128,faceY+300,25,85,'#303632');
    if(index===1 || index===2 || index===5 || index===6) panel+=lock(x+w-130,faceY+100)+lock(x+w-125,faceY+360);
    panel+=rect(x+12,1415,w-24,770,'#e6e7dd')+label(x+40,1600,210,'MERLIN GERIN SM6','#e5e7da','#252b27')+window(x+w-140,1635);
    if(cell.t!=='CM') panel+=window(x+w-140,1985,65,100);
    if(cell.t==='CM' || cell.t==='PF') panel+=rect(x+10,1800,w-20,35,'#f5f5e8');
    if(end) panel+=rect(x+50,1660,320,520,'#e4e4d5')+rect(x+75,1790,90,340,'#272f2c')+window(x+160,1850,150,200);
    panel+=text(x+w/2,2250,cell.label,19);
    body+=`<g class="hit" data-id="${cell.node}"><title>${esc(NODE[cell.node]?.label || cell.label)}</title>${panel}<rect class="hl" x="${x}" y="${top}" width="${w}" height="${2200-top}" fill="none"/><rect x="${x}" y="${top}" width="${w}" height="${2200-top}" fill="transparent" stroke="none"/></g>`;
    x+=w;
  });
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -300 ${total+80} 2650" role="img" aria-label="Poste de livraison relevé photographique"><title>Poste de livraison — façade EDF secours / CNR normal</title>${rect(-40,-300,total+80,2650,'#eef1e9')}${text(total/2,-230,'POSTE DE LIVRAISON — EDF SECOURS / CNR NORMAL',38)}${text(total/2,-175,'Reconstitution depuis IMG_4334 à IMG_4381 — proportions indicatives, pas un plan coté',23)}${body}${text(total/2,2320,'Commandes et appareils représentés en position illustrative ; états réels et clés non déduits des photographies.',20)}</svg>`;
}
