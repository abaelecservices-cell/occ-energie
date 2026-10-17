const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const context=vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(root,'src/site-frame.js'),'utf8'),context);
for(const [width,height] of [[1920,1080],[2560,1440],[1366,768],[390,844],[844,390]]){
 const input={x:0,y:0,w:1000,h:760};
 const frame=context.siteFrameBounds(input,width/height);
 assert.ok(Math.abs(frame.w/frame.h-width/height)<1e-9,'Remplissage sans déformation');
 assert.ok(frame.x<=0&&frame.y<=0&&frame.x+frame.w>=1000-.00001&&frame.y+frame.h>=760-.00001);
 for(const factor of [.01,.1,1,3,20]){
  const view=context.constrainSiteFrame({x:-1000,y:10000,w:frame.w*factor},frame);
  assert.ok(view.w<=frame.w&&view.h<=frame.h+.00001,'Dézoom borné');
  assert.ok(view.x>=frame.x&&view.y>=frame.y,'Pas de vide au déplacement');
  assert.ok(view.x+view.w<=frame.x+frame.w+.00001&&view.y+view.h<=frame.y+frame.h+.00001);
 }
}
const app=fs.readFileSync(path.join(root,'src/app.js'),'utf8');
let handler,activated,pan,zoom,reset=0;
const element={setAttribute(){},addEventListener(name,callback){handler=callback;}};
context.bindSiteKeyboard(element,{activate:id=>activated=id,pan:(x,y)=>pan=[x,y],zoom:value=>zoom=value,reset:()=>reset++});
const key=(value,target=null)=>handler({key:value,target:{closest:()=>target},preventDefault(){}});
key('Enter',{dataset:{id:'Z33'}});assert.equal(activated,'Z33');
key('ArrowLeft');assert.deepEqual(pan,[-1,0]);key('-');assert.equal(zoom,-1);key('0');assert.equal(reset,1);
assert.ok(app.includes('site ? frame().w : init.w * 3'),'Autres visionneuses conservées');
const html=fs.readFileSync(path.join(root,'OCC_ENERGIE.html'),'utf8');
const data=JSON.parse(html.match(/window\.OCC_DATA=([\s\S]*?);<\/script>/)[1]);
const base=JSON.parse(fs.readFileSync(path.join(root,'build/data.json'),'utf8'));
assert.equal(data.site.w,1976);assert.equal(data.site.h,1358);
assert.ok(data.site.img.startsWith('data:image/webp;base64,'));
assert.equal(Object.keys(data.site.tiles).length,17,'Pyramide de détail complète');
for(const value of Object.values(data.site.tiles))assert.ok(value.startsWith('data:image/webp;base64,')||fs.existsSync(path.join(root,value)),'Tuile disponible hors ligne');
assert.equal(data.site.zones.length,base.site.zones.length);
for(const zone of data.site.zones){
 const old=base.site.zones.find(item=>item.n===zone.n);
 for(const field of ['name','refs','conf'])assert.deepEqual(zone[field],old[field]);
 for(const polygon of zone.polys||[])for(const [x,y] of polygon)assert.ok(x>=0&&x<=1&&y>=0&&y<=1);
}
assert.deepEqual(data.edges,base.edges);
assert.ok(data.site.attribution.includes('Airbus'));
assert.ok(app.includes('if(site){ v=frame();'),'Initialisation sur l’image entière');
const reference=fs.readFileSync(path.join(root,'assets/vue_aerienne/google-earth-pro-20261017/reference-utilisateur.png'));
const meta=JSON.parse(fs.readFileSync(path.join(root,'assets/vue_aerienne/google-earth-pro-20261017/metadata.json'),'utf8'));
assert.equal(require('node:crypto').createHash('sha256').update(reference).digest('hex'),meta.referenceSha256);
console.log('PASS vue usine : image utilisateur intacte, quatre bords visibles sur cinq formats, commandes clavier et zones conservées.');
