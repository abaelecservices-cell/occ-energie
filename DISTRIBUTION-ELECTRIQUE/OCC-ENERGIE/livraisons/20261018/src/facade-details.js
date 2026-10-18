function facadeDetailSVG(unit, x, y, width, height) {
  const cx = x + width * (unit.x || .5);
  const rect = (a,b,w,h,fill) => `<rect x="${a}" y="${b}" width="${w}" height="${h}" fill="${fill}" stroke="#777" stroke-width="2"/>`;
  const lamp = (a,b,color) => `<circle cx="${a}" cy="${b}" r="14" fill="${color}" stroke="#333" stroke-width="3"/>`;
  if (unit.k === 'drive') {
    const w = Math.min(width * .19, 125), h = Math.max(140, height * .9);
    return rect(cx-w/2,y,w,h,'#303b36')+rect(cx-w*.35,y+15,w*.7,h*.3,'#a6bca6')+
      Array.from({length:9},(_,i)=>rect(cx-w*.3+(i%3)*w*.22,y+h*.48+Math.floor(i/3)*h*.14,w*.15,h*.09,'#c5cbbf')).join('');
  }
  if (unit.k === 'display-small') {
    const w = Math.min(width * .2, 150), h = Math.max(80, Math.min(height, 150));
    return rect(cx-w/2,y,w,h,'#292f30')+rect(cx-w*.35,y+12,w*.7,h*.5,'#a1b8bc');
  }
  if (unit.k === 'lever') return `<circle cx="${x+130}" cy="${y+height*.45}" r="28" fill="#8e8169" stroke="#443f36" stroke-width="4"/><path d="M${x+110} ${y+height*.55}l105-60" stroke="#b2a18a" stroke-width="19" stroke-linecap="round"/>`+lamp(x+width*.54,y+height*.35,'#51a08b')+rect(x+width*.55,y+height*.65,width*.37,28,'#303a36')+`<text x="${x+width*.74}" y="${y+height*.65+19}" font-size="12" fill="#fff" text-anchor="middle">${esc((unit.label || '').slice(0,34))}</text>`;
  if (unit.k === 'fan') return `<circle cx="${cx}" cy="${y+height*.45}" r="${Math.min(width*.2,height*.42)}" fill="#858e86" stroke="#454d46" stroke-width="7"/><path d="M${cx-40} ${y+height*.45}h80m-40-40v80" stroke="#d1d5ca" stroke-width="9"/>`;
  if (unit.k === 'warning') return `<path d="M${cx} ${y}l45 78h-90z" fill="#f2d43d" stroke="#222" stroke-width="4"/><text x="${cx}" y="${y+61}" font-size="52" text-anchor="middle" fill="#222">ϟ</text>`;
  if (unit.k === 'signal-column') return ['#43a889','#303b34','#b94e45'].map((color,i)=>lamp(cx,y+18+i*45,color)).join('');
  if (unit.k === 'isolator') return rect(cx-43,y,86,86,'#e2c83c')+`<circle cx="${cx}" cy="${y+43}" r="30" fill="#292e29"/><path d="M${cx-20} ${y+58}l40-30" stroke="#bbb" stroke-width="13"/>`;
  if (unit.k === 'mesh') {
    const w=width-30,h=Math.max(60,height*.9),left=x+15;
    return rect(left,y,w,h,'#8f9691')+Array.from({length:Math.floor(w/20)},(_,i)=>`<path d="M${left+10+i*20} ${y}v${h}" stroke="#464f47" stroke-width="4"/>`).join('')+Array.from({length:Math.floor(h/20)},(_,i)=>`<path d="M${left} ${y+10+i*20}h${w}" stroke="#464f47" stroke-width="4"/>`).join('');
  }
  return '';
}
