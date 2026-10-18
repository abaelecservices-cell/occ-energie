function siteFrameBounds(image, ratio) {
  const width = Math.max(image.w, image.h * ratio);
  const height = width / ratio;
  return {x:image.x+(image.w-width)/2,y:image.y+(image.h-height)/2,w:width,h:height};
}
function constrainSiteFrame(view, frame) {
  const width = Math.min(frame.w, view.w), height = width * frame.h / frame.w;
  return {x:Math.max(frame.x,Math.min(view.x,frame.x+frame.w-width)),
    y:Math.max(frame.y,Math.min(view.y,frame.y+frame.h-height)),w:width,h:height};
}
function addSiteFullscreen(host, viewer) {
  host.querySelector('.viewer').insertAdjacentHTML('beforeend',`<span class="site-source">${esc(D.site.attribution || '')}</span>`);
  const controls = host.querySelector('.vtools');
  controls.insertAdjacentHTML('beforeend','<button class="glass" data-site-full aria-label="Afficher la vue usine en plein écran" aria-pressed="false" title="Plein écran">⛶</button>');
  const button = controls.querySelector('[data-site-full]');
  const exit = () => { host.classList.remove('site-fullscreen'); button.setAttribute('aria-pressed','false'); button.setAttribute('aria-label','Afficher la vue usine en plein écran'); viewer.reset(); button.focus(); };
  button.onclick = () => {
    const active = host.classList.toggle('site-fullscreen');
    button.setAttribute('aria-pressed',String(active)); button.setAttribute('aria-label',active?'Quitter le plein écran':'Afficher la vue usine en plein écran'); viewer.reset();
  };
  host.addEventListener('keydown',event=>{if(event.key==='Escape')exit();});
}
function bindSiteKeyboard(element, actions) {
  element.setAttribute('tabindex','0');
  element.setAttribute('role','group');
  element.setAttribute('aria-label','Vue aérienne de l’usine. Flèches pour déplacer, plus et moins pour zoomer, zéro pour la vue complète.');
  element.addEventListener('keydown',event=>{
    const keys={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]};
    const target=event.target.closest('[data-id]');
    if(target&&['Enter',' '].includes(event.key)){event.preventDefault();actions.activate(target.dataset.id);return;}
    if(keys[event.key]){event.preventDefault();actions.pan(...keys[event.key]);}
    else if(['+','=','-','0'].includes(event.key)){
      event.preventDefault(); if(event.key==='0')actions.reset(); else actions.zoom(event.key==='-'?-1:1);
    }
  });
}
