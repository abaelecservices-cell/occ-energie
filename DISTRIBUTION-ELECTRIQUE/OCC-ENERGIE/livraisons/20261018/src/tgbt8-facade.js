function tgbt8FacadeSVG(f) {
  const width = 720, height = 2200, total = f.cols.length * width;
  const rect = (x,y,w,h,fill,stroke='#7a7c74',extra='') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" ${extra}/>`;
  const text = (x,y,t,size=18,fill='#202720') => `<text x="${x}" y="${y}" font-size="${size}" text-anchor="middle" fill="${fill}" font-family="Arial,sans-serif">${esc(t)}</text>`;
  const lamp = (x,y,c) => `<circle cx="${x}" cy="${y}" r="15" fill="${c}" stroke="#555" stroke-width="3"/>`;
  const plate = (x,y,w,t) => rect(x,y,w,36,'#171c18')+text(x+w/2,y+24,t,16,'#fff');
  const grille = (x,y,w,h) => rect(x,y,w,h,'#d4d4c7')+Array.from({length:Math.floor(h/12)},(_,i)=>`<path d="M${x+9} ${y+8+i*12}h${w-18}" stroke="#77796f" stroke-width="5"/>`).join('');
  const handle = (x,y) => rect(x,y,22,130,'#252a27','#111','rx="7"')+`<circle cx="${x+11}" cy="${y+46}" r="6" fill="#aaa"/>`;
  const warning = (x,y) => `<path d="M${x} ${y}l34 60h-68z" fill="#f4df39" stroke="#303429" stroke-width="4"/>`+text(x,y+47,'ϟ',38);
  const hit = (id,x,y,w,h,s) => id ? `<g class="hit" data-id="${id}"><title>${esc(NODE[id]?.label || id)}</title>${s}${rect(x,y,w,h,'transparent','none')}</g>` : s;
  const screen = (x,y) => rect(x-20,y-24,200,165,'#d7d7cc')+rect(x,y,160,114,'#242b29')+rect(x+29,y+22,105,65,'#b8c2f1')+text(x+81,y+66,'POWER',14)+Array.from({length:5},(_,i)=>rect(x+16+i*26,y+96,16,7,'#929992')).join('');
  let body = '';
  f.cols.forEach((column,index) => {
    const x=index*width, grad=index<3 || index>5;
    body+=rect(x,0,width,height,'#dbdcd0','#74786d','stroke-width="3"')+grille(x+14,2040,width-28,135);
    if(grad) {
      body+=rect(x+18,18,width-36,2000,'#dfdfd3','#999d90','stroke-width="3"');
      body+=`<path d="M${x+230} -55v-65h270v65" fill="#aaa99d" stroke="#767970" stroke-width="5"/><ellipse cx="${x+365}" cy="-60" rx="135" ry="32" fill="#464c43"/><path d="M${x+250} -58v65h230v-65" fill="#545b50" stroke="#383f36" stroke-width="4"/>`;
      const label=column.units.find(unit=>unit.k==='plate');
      body+=plate(x+160,52,400,label?.label.replace('GRADATHYR / ','') || 'GRADATHYR')+warning(x+360,132);
      body+=screen(x+330,675)+handle(x+620,1120)+grille(x+160,1690,350,245);
      body+=lamp(x+235,865,'#e4aa36')+lamp(x+235,918,'#e4aa36')+lamp(x+235,971,'#e4aa36');
      body+=plate(x+175,824,115,'SOUS TENSION')+plate(x+175,881,115,'DÉFAUT')+plate(x+175,936,115,'THYRISTOR');
      body+=lamp(x+355,956,'#333b35')+lamp(x+430,956,'#333b35')+rect(x+506,920,52,52,'#efeee4')+lamp(x+532,946,'#28342b');
      body+=rect(x+315,1160,190,115,'#eee35f')+text(x+410,1200,'CONSIGNATION',15)+text(x+410,1230,'ÉNERGIE',15);
      body+=`<path d="M${x+415} 1480v58h-98" fill="none" stroke="#535b52" stroke-width="18" stroke-linecap="round"/>`;
      body=body.replace(/$/,hit(label?.dep,x+80,600,width-160,440,''));
    } else if(index===3 || index===4) {
      body+=rect(x+18,18,width-36,1080,'#dfdfd3')+rect(x+18,1110,width-36,910,'#dfdfd3');
      body+=plate(x+245,35,230,index===3?'ARRIVÉE 1':'ARRIVÉE 2')+warning(x+190,100);
      const id=index===3?'TGBT8_QB':'TGBT8_QA';
      body+=hit(id,x+210,280,320,520,breakerSVG('nw',x+210,280,320,520));
      body+=plate(x+220,830,270,index===3?'TRANSFO 8B':'ARRIVÉE 2')+lamp(x+295,900,'#69a38b')+lamp(x+352,900,'#b9483d')+handle(x+627,300);
      if(index===3) {
        body+=plate(x+245,1120,230,'CONTRÔLE')+rect(x+130,1230,110,130,'#f5f4eb')+rect(x+470,1230,110,130,'#f5f4eb');
        body+=text(x+185,1302,'V',56)+text(x+525,1302,'V',56)+rect(x+132,1570,130,170,'#323d37')+rect(x+457,1570,130,170,'#323d37');
        body+=lamp(x+360,1400,'#30372e')+lamp(x+360,1520,'#30372e');
      } else body+=plate(x+245,1120,230,'COUPLAGE')+hit('TGBT8_QC',x+215,1320,300,480,breakerSVG('nw',x+215,1320,300,480));
    } else {
      body+=rect(x+18,18,width-36,2000,'#dfdfd3')+plate(x+140,50,440,'PUISSANCE NORMAL — SECOURS GORGE')+warning(x+360,128)+handle(x+625,1070);
      body+=rect(x+200,620,360,310,'#dddcd1')+rect(x+220,660,135,218,'#252e29')+rect(x+390,660,135,218,'#252e29');
      for(let row=0;row<10;row++)body+=text(x+287,680+row*18,'ÉTAT / DÉFAUT',9,'#ddd')+text(x+457,680+row*18,'ÉTAT / DÉFAUT',9,'#ddd');
      body+=rect(x+160,1080,170,220,'#37443a')+rect(x+470,1080,125,170,'#abc5dc');
      for(let row=0;row<2;row++)for(let i=0;i<3;i++)body+=lamp(x+358+i*41,1110+row*65,['#e2b942','#5cbba4','#c65343'][i]);
    }
  });
  return `<svg viewBox="-35 -260 ${total+70} ${height+335}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Façade TGBT8 redessinée depuis les photos"><title>TGBT8 — Gradathyr N3,1 creuset</title>${text(total/2,-210,'TGBT8 — Gradathyr N3,1 creuset',44)}${text(total/2,-163,'Façade relevée sur IMG_4400 à IMG_4417 — ordre des zones recoupé avec les plaques agrandies',22)}${body}${text(total/2,2248,'Ventilateurs de toiture, écrans, commandes, arrivées, couplage et grilles reconstitués en SVG.',20)}</svg>`;
}
