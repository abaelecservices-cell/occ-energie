'use strict';
const projectSearch=document.querySelector('#find');
const projectSections=[...document.querySelectorAll('main>section')];
const projectNormalize=value=>value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const projectIndex=projectSections.map(section=>({section,text:projectNormalize(section.textContent)}));
projectSearch.addEventListener('input',()=>{
  const tokens=projectNormalize(projectSearch.value).split(/\s+/).filter(Boolean);
  let count=0;
  for(const item of projectIndex){item.section.hidden=!tokens.every(token=>item.text.includes(token));if(!item.section.hidden)count++;}
  document.querySelector('#count').textContent=`${count} rubriques affichées`;
});
function showProjectAnchor(){
  const target=document.getElementById(decodeURIComponent(location.hash.slice(1)));
  if(target)target.scrollIntoView();
}
window.addEventListener('hashchange',showProjectAnchor);
showProjectAnchor();
