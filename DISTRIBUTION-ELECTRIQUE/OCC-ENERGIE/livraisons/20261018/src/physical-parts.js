function physicalPartSVG(part) {
  const {x,y,w,h}=part, color=part.fill || '#262e2e';
  const rect=(a,b,c,d,fill,extra='')=>`<rect x="${a}" y="${b}" width="${c}" height="${d}" fill="${fill}" stroke="#656b66" stroke-width="2" ${extra}/>`;
  const circle=(a,b,r,fill)=>`<circle cx="${a}" cy="${b}" r="${r}" fill="${fill}" stroke="#464d48" stroke-width="2"/>`;
  const text=(label,a,b,size=18,fill='#202622')=>`<text x="${a}" y="${b}" font-family="Arial,sans-serif" font-size="${size}" fill="${fill}">${esc(label)}</text>`;
  if(part.kind==='plate'||part.kind==='note') {
    const lines=part.lines || [part.label || ''];
    return rect(x,y,w,h,part.fill || (part.kind==='note'?'#f3e24a':'#20282b'))+lines.map((line,index)=>text(line,x+8,y+(index+1)*h/(lines.length+1)+5,part.font || 18,part.kind==='note'?'#24291f':'#fff')).join('');
  }
  if(part.kind==='grille')return rect(x,y,w,h,part.fill || '#474b4b')+Array.from({length:Math.floor(w/9)},(_,i)=>`<path d="M${x+5+i*9} ${y+5}v${h-10}" stroke="#828785" stroke-width="3"/>`).join('');
  if(part.kind==='vent')return rect(x,y,w,h,'#d9dbd3','rx="8"')+Array.from({length:Math.floor(h/12)},(_,i)=>`<path d="M${x+9} ${y+9+i*12}h${w-18}" stroke="#656c68" stroke-width="6"/>`).join('');
  if(part.kind==='emergency')return circle(x,y,w,'#e9ce35')+circle(x,y,w*.65,'#c64636')+circle(x-3,y-3,w*.38,'#dc5c44');
  if(part.kind==='drive')return rect(x,y,w,h,'#409362','rx="7"')+rect(x+7,y+8,w-14,h-16,'#333a36')+rect(x+w*.15,y+h*.1,w*.7,h*.3,'#a5b0a0')+Array.from({length:8},(_,i)=>rect(x+w*(.15+(i%4)*.19),y+h*(.48+Math.floor(i/4)*.12),w*.12,h*.07,'#737c76')).join('')+circle(x+w*.5,y+h*.82,w*.17,'#202a24');
  if(part.kind==='compact')return rect(x,y,w,h,'#252f2c')+rect(x+w*.25,y+h*.1,w*.48,h*.76,'#277b49')+rect(x+w*.33,y+h*.42,w*.32,h*.35,'#141d1a')+rect(x+w*.05,y+h*.12,w*.16,h*.7,'#414a46')+rect(x+w*.8,y+h*.1,w*.15,h*.8,'#3c4540');
  if(part.kind==='masterpact')return rect(x,y,w,h,'#242c2b')+rect(x+15,y+15,w-30,h-65,'#3f4846')+rect(x+w*.08,y+h*.13,w*.18,h*.58,'#87918a')+rect(x+w*.31,y+h*.15,w*.37,h*.57,'#4d5653')+rect(x+w*.7,y+h*.12,w*.22,h*.62,'#303b37')+rect(x+w*.39,y+h*.22,w*.1,h*.07,'#a44838')+rect(x+w*.53,y+h*.22,w*.1,h*.07,'#18221d')+rect(x+w*.4,y+h*.4,w*.22,h*.03,'#bac5b6')+rect(x+15,y+h-45,w-30,30,'#1c2821')+circle(x+w*.2,y+h-29,9,'#b5b6a2')+circle(x+w*.83,y+h-29,9,'#777d72');
  if(part.kind==='mcb')return rect(x,y,w,h,'#e4e7de')+rect(x+2,y+8,w-4,4,'#319b6a')+rect(x+4,y+h*.6,w-8,h*.18,part.dark?'#252d2a':'#a4b1a5')+text(part.label || '',x+3,y+h*.45,Math.min(13,w/5));
  if(part.kind==='handle')return rect(x,y,w,h,'#262e30','rx="5"')+circle(x+w/2,y+h*.4,w*.18,'#8d9491');
  if(part.kind==='lamp')return circle(x,y,w,color)+circle(x-3,y-3,w*.35,'#d9f1df');
  if(part.kind==='meter')return rect(x,y,w,h,'#d3d8d4')+rect(x+8,y+8,w-16,h-16,'#f2f4e9')+`<path d="M${x+w*.2} ${y+h*.7}q${w*.3} ${-h*.7} ${w*.6} 0M${x+w*.5} ${y+h*.75}l${w*.15} ${-h*.4}" fill="none" stroke="#303b38" stroke-width="3"/>`;
  if(part.kind==='monitor')return rect(x,y,w,h,'#282e2c')+rect(x+9,y+9,w-18,h*.62,'#a3b1a6')+text(part.label || '',x+7,y+h-12,12,'#e6ebe2');
  if(part.kind==='isolator')return rect(x,y,w,h,'#313938')+circle(x+w/2,y+h/2,w*.32,'#171e21')+`<path d="M${x+w*.36} ${y+h*.68}l${w*.28} ${-h*.4}" stroke="#7b8581" stroke-width="12"/>`;
  if(part.kind==='breaker')return rect(x,y,w,h,'#212b2f')+rect(x+6,y+8,w*.42,h-16,'#3f4848')+rect(x+w*.49,y+h*.45,w*.43,h*.2,'#ae4f3a');
  if(part.kind==='buzzer')return circle(x,y,w,'#272d2c')+Array.from({length:5},(_,i)=>`<path d="M${x-w*.65} ${y-w*.6+i*w*.3}h${w*1.3}" stroke="#77817b" stroke-width="4"/>`).join('');
  if(part.kind==='text')return text(part.label,x,y,part.font || 22,part.fill);
  return rect(x,y,w,h,color);
}
