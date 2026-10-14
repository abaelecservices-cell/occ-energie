'use strict';
/* OCC ÉNERGIE — Cartographie du réseau électrique. Designed by Labidi El Fahli.
   Application consultative hors ligne : aucune commande, aucune connexion au réseau industriel. */
const D = window.OCC_DATA;
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
/* dossier des photos sources : par défaut à côté de l'application (../Plan électrique/), modifiable pour ce poste (Registre) */
const PHOTO_KEY = 'occE.photodir', PHOTO_DEF = '../Plan%20%C3%A9lectrique/';
let PHOTO_BASE = PHOTO_DEF;
try { PHOTO_BASE = localStorage.getItem(PHOTO_KEY) || PHOTO_DEF; } catch (e) {}

/* ======================================================================= modèle */
const NODE = {}, BOARD = {}, ADJ = {}, DOWN = {}, UP = {};
D.nodes.forEach(n => NODE[n.id] = n);
D.boards.forEach(b => BOARD[b.id] = b);
D.edges.forEach(e => {
  (ADJ[e.a] = ADJ[e.a] || []).push(e.b); (ADJ[e.b] = ADJ[e.b] || []).push(e.a);
  (DOWN[e.a] = DOWN[e.a] || []).push(e); (UP[e.b] = UP[e.b] || []).push(e);
});
const SW = new Set(['cb', 'sw', 'cpl', 'dep']);
const DEPS_BY_BOARD = {};
D.nodes.filter(n => n.t === 'dep').forEach(n => (DEPS_BY_BOARD[n.board] = DEPS_BY_BOARD[n.board] || []).push(n));
const TYPE = { src: 'Source', cb: 'Disjoncteur', sw: 'Interrupteur', cpl: 'Couplage', bus: 'Jeu de barres', tr: 'Transformateur', dep: 'Départ', load: 'Récepteur', board: 'Tableau', issue: 'Incohérence', proc: 'Procédure' };
const CONF = { confirme: ['g', 'Confirmé'], probable: ['b', 'Probable'], a_verifier: ['a', 'À vérifier'], inconnu: ['', 'Non documenté'] };
const confPill = c => { const [k, t] = CONF[c] || CONF.inconnu; return `<span class="pill ${k}">${t}</span>`; };
const ND = '<span class="muted">Non documenté</span>';

/* ======================================================================= simulation */
/* La simulation est une HYPOTHÈSE de travail, jamais une observation : elle est mémorisée avec son heure et signalée sur toutes les vues
   tant qu'elle diffère de la configuration normale documentée. Les fiches de dépannage ne dépendent pas d'elle. */
const SIM_KEY = 'occE.sim.v1', SIMT_KEY = 'occE.sim.t';
let SIM = {}, SIMT = 0, SANDBOX = false, LAST_CONFLICT = [];
try { SIM = JSON.parse(localStorage.getItem(SIM_KEY) || '{}'); SIMT = +localStorage.getItem(SIMT_KEY) || 0; } catch (e) { SIM = {}; }
function defaultClosed(n) {
  if (n.t === 'src') return n.id !== 'GE1';
  if (n.open0) return false;
  if (n.id === 'PL_A04' || n.id === 'TS9_QS' || n.id === 'KV6_C') return false;
  if (n.t === 'cpl' && n.board && BOARD[n.board] && BOARD[n.board].kind !== 'HTA') return false;
  return true;
}
const rawClosed = id => (id in SIM ? SIM[id] : defaultClosed(NODE[id]));
/* Permutation automatique de sources au poste de livraison (indication exploitant + unifilaire : « Décl. Manque 24VCC / Fermeture 24VCC ») :
   sur manque de tension CNR, la bobine à manque de tension ouvre l'arrivée CNR (B01) et l'arrivée EDF secours (A04) se ferme. */
const atsActive = () => !rawClosed('SRC_CNR') && rawClosed('SRC_EDF');
const isClosed = id => (id === 'PL_A04' && atsActive() ? true : id === 'PL_B01' && atsActive() ? false : rawClosed(id));
function saveSim() {
  if (SANDBOX) return;
  SIMT = Object.keys(SIM).length ? Date.now() : 0;
  try { localStorage.setItem(SIM_KEY, JSON.stringify(SIM)); localStorage.setItem(SIMT_KEY, String(SIMT)); } catch (e) {}
}
/* Règles appliquées en simulation (une fermeture est REFUSÉE si elle crée l'une de ces situations) :
   1. deux sources sur le même réseau : CNR et EDF ne peuvent jamais alimenter en même temps (indication exploitant), ni réseau + groupe électrogène ;
   2. deux transformateurs en parallèle sur un même jeu de barres (règle d'exploitation « jamais arrivée A, couplage et arrivée B fermés » —
      donnée par l'exploitant ; sur le TGBT 3 des clés Ronis sont dessinées mais le même dossier écrit « aucun verrouillage » : écart I-TGBT3-LOCK). */
const SRC_NAME = { SRC_CNR: 'CNR', SRC_EDF: 'EDF', GE1: 'groupe électrogène n°1' };
function conflicts() {
  const out = [];
  const reach = (start, stopTr) => { const seen = new Set([start]), q = [start];
    while (q.length) { const u = q.shift(); for (const v of nextOf(u)) { if (seen.has(v)) continue; const nv = NODE[v];
      if ((SW.has(nv.t) || nv.t === 'src') && !isClosed(v)) continue; if (stopTr && nv.t === 'tr') continue; seen.add(v); q.push(v); } }
    return seen; };
  // 2 bis. chaque TGBT est scindé en deux demi-jeux de barres, chacun alimenté par son transformateur ; le couplage ne se ferme
  //    qu'après ouverture de l'arrivée qui alimentait le demi-jeu de barres (règle exploitant) : jamais arrivée A + couplage + arrivée B fermés,
  //    que les transformateurs soient sous tension ou non (sinon le transformateur hors service serait réalimenté par le côté BT)
  D.boards.forEach(b => { const qa = NODE[b.id + '_QA'], qb = NODE[b.id + '_QB'], qc = NODE[b.id + '_QC'];
    if (qa && qb && qc && isClosed(qa.id) && isClosed(qb.id) && isClosed(qc.id)) out.push({ kind: 'cpl', txt: `${b.name} : le couplage ne se ferme qu’après avoir ouvert l’arrivée qui alimentait le demi-tableau (jamais arrivée A, couplage et arrivée B fermés ensemble).` }); });
  // 3. interverrouillages par clé documentés appareil par appareil (ex. by-pass total onduleur / arrivée générale onduleur)
  D.nodes.forEach(n => { if (n.excl && isClosed(n.id) && isClosed(n.excl)) out.push({ kind: 'key', txt: `Interverrouillage par clé : « ${short(n)} » et « ${short(NODE[n.excl])} » ne peuvent pas être fermés en même temps.` }); });
  const srcs = D.nodes.filter(n => n.t === 'src' && isClosed(n.id));
  const bySrc = srcs.map(s => [s.id, reach(s.id, false)]);
  for (let i = 0; i < bySrc.length; i++) for (let j = i + 1; j < bySrc.length; j++) {
    const shared = [...bySrc[i][1]].find(x => bySrc[j][1].has(x) && NODE[x].t === 'bus');
    if (shared) out.push({ kind: 'src', txt: `Interverrouillage : ${SRC_NAME[bySrc[i][0]] || bySrc[i][0]} et ${SRC_NAME[bySrc[j][0]] || bySrc[j][0]} ne peuvent pas alimenter le réseau en même temps (jeu de barres commun : ${short(NODE[shared])}).` });
  }
  const trs = D.nodes.filter(n => n.t === 'tr' && LIVE_TMP.has(n.id));
  const byTr = trs.map(t => [t.id, reach(t.id, true)]);
  const seenPair = new Set();
  for (let i = 0; i < byTr.length; i++) for (let j = i + 1; j < byTr.length; j++) {
    const shared = [...byTr[i][1]].find(x => x !== byTr[i][0] && byTr[j][1].has(x) && NODE[x].t === 'bus');
    if (shared && !seenPair.has(shared)) { seenPair.add(shared); out.push({ kind: 'tr', txt: `Interverrouillage 2 sur 3 : ${short(NODE[byTr[i][0]])} et ${short(NODE[byTr[j][0]])} seraient en parallèle sur ${short(NODE[shared])}. Ouvrir d’abord une arrivée.` }); }
  }
  return out;
}
let LIVE_TMP = new Set();
function setSw(id, v) {
  const had = id in SIM, old = SIM[id];
  if (v === defaultClosed(NODE[id])) delete SIM[id]; else SIM[id] = v;
  LIVE_TMP = energize();
  if (v) { const c = conflicts(); LAST_CONFLICT = c; if (c.length) { if (had) SIM[id] = old; else delete SIM[id]; LIVE_TMP = energize(); LIVE = LIVE_TMP; if (!SANDBOX) { toast('⛔ Fermeture refusée'); refusal(id, c); } return false; } }
  saveSim(); LIVE = LIVE_TMP; return true;
}
function refusal(id, c) {
  openSheet(`<span class="pill r">Simulation</span><h2>Fermeture refusée : ${esc(short(NODE[id]))}</h2>`,
    `<div class="banner danger">⛔<div>${c.map(x => esc(x.txt)).join('<br>')}</div></div>
     <p class="small">Règles appliquées par le simulateur : jamais deux sources en même temps (CNR / EDF / groupe). Règle d’exploitation : chaque TGBT est scindé en deux, chaque moitié alimentée par son transformateur ; le couplage ne se ferme qu’après avoir ouvert l’arrivée qui alimentait la moitié à réalimenter (jamais arrivée A, couplage et arrivée B fermés ensemble).</p>`);
}
function resetSim() { SIM = {}; saveSim(); LIVE = LIVE_TMP = energize(); }
/* bandeau commun : une simulation modifiée est toujours signalée, avec son heure */
function simNotice() {
  const n = Object.keys(SIM).length; if (!n) return '';
  const t = SIMT ? new Date(SIMT).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—';
  return `<div class="banner sim simnote noprint">🧪<div class="grow"><b>Simulation en cours</b> — ${n} appareil(s) modifié(s), dernière modification le ${esc(t)}. Les couleurs vert / rouge montrent cette hypothèse, <b>pas l’état réel</b> de l’installation.</div><button class="btn ghost mini" id="simreset">Revenir à la configuration normale</button></div>`;
}
// propagation dans le sens amont → aval ; seuls les couplages sont traversés dans les deux sens
function nextOf(u) {
  const out = (DOWN[u] || []).map(e => e.b);
  (UP[u] || []).forEach(e => { if (NODE[e.a].t === 'cpl' || NODE[u].t === 'cpl') out.push(e.a); });
  return out;
}
function energize() {
  const live = new Set(), q = [];
  D.nodes.forEach(n => { if (n.t === 'src' && isClosed(n.id)) { live.add(n.id); q.push(n.id); } });
  while (q.length) {
    const u = q.shift();
    for (const v of nextOf(u)) {
      if (live.has(v)) continue;
      const nv = NODE[v];
      if ((SW.has(nv.t) || nv.t === 'src') && !isClosed(v)) continue;
      live.add(v); q.push(v);
    }
  }
  return live;
}
let LIVE = energize(); LIVE_TMP = LIVE;
// état mémorisé incohérent avec les interverrouillages (ancienne version) -> remise à l'hypothèse initiale
if (conflicts().length) { SIM = {}; saveSim(); LIVE = LIVE_TMP = energize(); }
const isLive = id => LIVE.has(id);
function interlock(boardId) {
  const qa = NODE[boardId + '_QA'], qb = NODE[boardId + '_QB'], qc = NODE[boardId + '_QC'];
  if (!qa || !qb || !qc) return null;
  const b = BOARD[boardId], n = [qa, qb, qc].filter(x => isClosed(x.id)).length;
  const ronis = b.coupler && b.coupler.rule && /1-1-0/.test(b.coupler.rule);
  if (n === 3) return { lvl: 'danger', txt: 'Configuration INTERDITE par la règle d’exploitation : trois appareils fermés = transformateurs en parallèle.' + (ronis ? ' Clés Ronis dessinées sur le plan (présence à vérifier).' : '') };
  if (b.coupler.status !== 'documente' && isClosed(qc.id)) return { lvl: 'sim', txt: 'Couplage non documenté : configuration non vérifiée.' };
  return null;
}

/* ======================================================================= utilitaires modèle */
const boardOf = n => n && n.board ? BOARD[n.board] : null;
function busOf(id) { const u = (UP[id] || [])[0]; return u ? u.a : null; }
function locChain(locId) { const out = []; let l = locId; while (l && D.loc[l]) { out.unshift({ id: l, ...D.loc[l] }); l = D.loc[l].parent; } return out; }
function short(n) {
  if (!n) return '';
  if (n.t === 'bus') return n.label.replace(/ — jeu de barres.*$/, '').replace(/ — demi-JdB /, ' ');
  if (n.t === 'src') return n.label.split(' — ')[0];
  let l = n.label; if (l.length > 46) l = l.slice(0, 44) + '…';
  return l;
}
function colOf(n) { if (!n.case) return null; const m = String(n.case).match(/^(\d+)[-+](\d+)/); return m ? { col: m[1], pos: m[2] } : null; }
function facadeHas(fid, id) {
  const f = D.facades[fid]; if (!f) return false;
  if (f.cells) return f.cells.some(c => c.node === id);
  return f.cols.some(c => c.units.some(u => u.dep === id || u.node === id));
}
function facadeFor(id) {
  const n = NODE[id]; if (!n) return null;
  const b = boardOf(n);
  if (b && b.facade && facadeHas(b.facade, id)) return b.facade;
  for (const fid in D.facades) if (facadeHas(fid, id)) return fid;
  return null;
}
function upPaths(id, max = 12) {
  const res = [], path = [id], seen = new Set([id]);
  (function rec(u, depth) {
    if (res.length >= max || depth > 45) return;
    const n = NODE[u];
    if (n.t === 'src') { res.push(path.slice()); return; }
    const ups = (UP[u] || []).map(e => e.a);
    (DOWN[u] || []).forEach(e => { if (NODE[e.b].t === 'cpl') ups.push(e.b); });
    if (n.t === 'cpl') (DOWN[u] || []).forEach(e => ups.push(e.b));
    for (const v of ups) {
      if (seen.has(v)) continue;
      seen.add(v); path.push(v); rec(v, depth + 1); path.pop(); seen.delete(v);
    }
  })(id, 0);
  return res.sort((a, b) => a.length - b.length);
}
// normal = true : configuration normale documentée (parcours de dépannage) ; sinon état de la simulation
function pathHTML(p, startIdx = 1, normal = false) {
  const nodes = p.slice(startIdx).reverse();
  const cl = id => normal ? defaultClosed(NODE[id]) : isClosed(id);
  return `<div class="path">${nodes.map(id => { const n = NODE[id]; const st = SW.has(n.t) && !cl(id) ? 'off' : (normal || isLive(id) ? 'on' : 'off');
    return `<span class="n ${st}" data-open="${id}" title="${esc(n.label)}">${esc(short(n))}${SW.has(n.t) && !cl(id) ? ' ◌' : ''}</span>`; }).join('<i>→</i>')}</div>`;
}
function pathVia(p) {
  const v = p.filter(id => NODE[id].t === 'cpl' || NODE[id].role === 'arrivee' || NODE[id].t === 'tr').map(id => short(NODE[id]));
  const src = NODE[p[p.length - 1]];
  return `${esc(src.label)}${v.length ? ' — via ' + esc(v.reverse().join(' › ')) : ''}`;
}
function downstream(id, lim = 400) {
  const out = [], seen = new Set([id]), q = [id];
  while (q.length && out.length < lim) {
    const u = q.shift();
    for (const e of DOWN[u] || []) {
      if (seen.has(e.b)) continue; const nb = NODE[e.b];
      if (nb.t === 'cpl') continue;
      seen.add(e.b); out.push(e.b); q.push(e.b);
    }
  }
  return out;
}

/* ======================================================================= recherche */
const norm = s => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const SYN = {
  transfo: ['tr', 'transformateur', 'transformer'], transformateur: ['tr', 'transfo'], transformer: ['tr', 'transfo'], tr: ['transfo', 'transformateur'],
  disj: ['disjoncteur', 'dj', 'breaker'], disjoncteur: ['disj', 'dj'], breaker: ['disjoncteur', 'disj'],
  pompe: ['ppe', 'pump'], ppe: ['pompe'], pump: ['pompe', 'ppe'], eclairage: ['ecl', 'lighting'], ecl: ['eclairage'], lighting: ['eclairage', 'ecl'],
  couplage: ['coupler', 'cpl', 'tie'], coupler: ['couplage'], tie: ['couplage'], compresseur: ['compressor'], compressor: ['compresseur'],
  ventilateur: ['fan', 'ventilo'], fan: ['ventilateur', 'ventilo'], condensateur: ['condensateurs', 'capacitor', 'condo', 'cond'], capacitor: ['condensateur'],
  arrivee: ['incomer', 'provient'], incomer: ['arrivee'], onduleur: ['ups'], ups: ['onduleur'], chaudiere: ['boiler'], boiler: ['chaudiere'],
  secheur: ['dryer'], dryer: ['secheur'], agitateur: ['mixer'], mixer: ['agitateur'], four: ['furnace'], furnace: ['four'], etuve: ['oven', 'etuves'], oven: ['etuve'],
  frigo: ['chiller', 'froid'], chiller: ['frigo'], substation: ['sous station', 'ss'], heater: ['rechauffeur'], rechauffeur: ['heater'],
  extracteur: ['extraction'], extraction: ['extracteur'], prise: ['pc', 'ps'], lumiere: ['eclairage'],
};
const TW = { board: 70, src: 55, tr: 50, bus: 42, cpl: 36, cb: 32, sw: 30, dep: 22, load: 12, proc: 14, issue: 6 };
const IDX = [];
function addRec(kind, id, label, extra, t) {
  const text = norm(label + ' ' + (extra || ''));
  IDX.push({ kind, id, t, label, n: text, w: text.split(' '), c: text.replace(/ /g, ''), ln: norm(label) });
}
D.boards.forEach(b => addRec('board', b.id, b.name, [b.id, b.kind, 'tableau', (b.halves || []).map(h => h.label).join(' '), b.sap].join(' '), 'board'));
D.nodes.forEach(n => {
  const b = boardOf(n);
  const extra = [b ? b.name : '', n.case ? 'case ' + n.case : '', n.model, n.xl ? n.xl.label : '', n.alias, n.kva, n.cell, n.keys, n.rep,
    n.t === 'tr' ? 'transformateur transfo' : '', n.t === 'cpl' ? 'couplage' : '', n.role === 'arrivee' ? 'arrivee' : ''].join(' ');
  addRec('node', n.id, n.label, extra, n.t);
});
D.issues.forEach(i => addRec('issue', i.id, i.title, i.text, 'issue'));
D.procs.forEach(p => addRec('proc', p.id, p.title, (p.but || []).join(' '), 'proc'));
function tokMatch(rec, t) {
  const alts = [t, ...(SYN[t] || [])];
  let best = 0;
  for (const a of alts) {
    if (a.includes(' ')) { if (rec.n.includes(a)) best = Math.max(best, 2); continue; }
    for (const w of rec.w) { if (w === a) { best = Math.max(best, 3); break; } if (w.startsWith(a)) best = Math.max(best, 2); }
    if (!best && a.length >= 3 && rec.c.includes(a)) best = 1;
    if (!best && /\d/.test(a) && a.length >= 2 && rec.c.includes(a)) best = 1;
  }
  return best;
}
function search(q, lim = 40) {
  const qn = norm(q); if (!qn) return [];
  const toks = qn.split(' '), qc = qn.replace(/ /g, '');
  const out = [];
  for (const r of IDX) {
    let s = 0, ok = true;
    for (const t of toks) { const m = tokMatch(r, t); if (!m) { if (!r.c.includes(qc)) { ok = false; break; } } s += m; }
    if (!ok) continue;
    if (r.c.includes(qc)) s += 4;
    if (r.ln === qn) s += 8; else if (r.ln.startsWith(qn)) s += 4; else if (r.ln.replace(/ /g, '').startsWith(qc)) s += 3;
    s += (TW[r.t] || 10) / 10 - Math.min(r.label.length, 120) / 120;
    out.push({ r, s });
  }
  return out.sort((a, b) => b.s - a.s).slice(0, lim).map(x => x.r);
}
function hl(label, q) {
  const toks = norm(q).split(' ').filter(t => t.length > 0);
  let h = esc(label);
  const plain = norm(label);
  toks.forEach(t => {
    const re = new RegExp('(' + t.split('').map(ch => ch.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '[\\u0300-\\u036f]?').join('') + ')', 'gi');
    if (plain.includes(t)) h = h.replace(re, '<mark>$1</mark>');
  });
  return h;
}
function recContext(r) {
  if (r.kind === 'board') { const b = BOARD[r.id]; const L = locChain(b.loc).slice(1).map(l => l.name).join(' › '); return `${b.kind}${L ? ' · ' + L : ''}`; }
  if (r.kind === 'issue') return 'Incohérence documentaire';
  if (r.kind === 'proc') return 'Procédure / règle de manœuvre';
  const n = NODE[r.id], b = boardOf(n), bits = [];
  const bus = n.t === 'dep' ? NODE[busOf(n.id)] : null;
  const h = bus && b && b.halves && b.halves.length > 1 ? b.halves.find(x => x.id === bus.id) : null;
  if (h) bits.push(h.label); else if (b) bits.push(b.name);
  if (n.case) bits.push('case ' + n.case);
  if (n.xl) bits.push('Excel ' + n.xl.ref.split('› ').pop());
  return bits.join(' · ');
}

/* ======================================================================= rendu : composants */
const ICON = {
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 11 12 4l9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/></svg>',
  net: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v5M5 7h14M5 7v4M12 7v4M19 7v4"/><circle cx="5" cy="14" r="3"/><circle cx="12" cy="14" r="3"/><circle cx="19" cy="14" r="3"/><path d="M5 17v4M12 17v4M19 17v4"/></svg>',
  boards: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="18" rx="1.5"/><rect x="14" y="3" width="7" height="18" rx="1.5"/><path d="M5.5 8h2M5.5 12h2M16.5 8h2M16.5 12h2"/></svg>',
  diag: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>',
  maint: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/></svg>',
  reg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 12h7M9 16h7"/></svg>',
  theme: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></svg>',
  close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>',
};
ICON.plan = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 5l6-2 6 2 6-2v16l-6 2-6-2-6 2z"/><path d="M9 3v16M15 5v16"/></svg>';
const TABS = [['home', 'Accueil', '#/'], ['diag', 'Dépannage', '#/courant'], ['plan', 'Plans', '#/plans'], ['boards', 'Tableaux', '#/tableaux'], ['net', 'Réseau', '#/reseau'], ['maint', 'Entretien', '#/entretien']];
function shell() {
  document.body.innerHTML = `
  <header id="top">
    <a class="brand glass" href="#/"><span class="logo">OCC</span><span><b>OCC ÉNERGIE</b><small>Cartographie du réseau électrique</small></span></a>
    <div id="searchwrap"><span class="ico">${ICON.search}</span>
      <input id="search" class="glass" type="search" autocomplete="off" spellcheck="false" placeholder="Départ, repère, tableau, transfo… (ex. Étuve 2, 7K121, TR 6A)">
      <button id="clear" aria-label="Effacer">✕</button><div id="results" class="glass" role="listbox"></div></div>
    <div class="topact"><a class="iconbtn glass" href="#/registre" title="Registre et contrôle qualité" style="color:var(--ink)">${ICON.reg}</a><button class="iconbtn glass" id="themebtn" title="Thème clair / sombre">${ICON.theme}</button></div>
  </header>
  <main id="view"></main>
  <nav id="tabs" class="glass">${TABS.map(([k, l, h]) => `<a href="${h}" data-tab="${k}">${ICON[k]}<span>${l}</span></a>`).join('')}</nav>
  <div id="scrim"></div>
  <aside id="sheet" class="glass" aria-hidden="true"><div class="grab"></div><div class="hd"><div style="flex:1;min-width:0" id="sheethd"></div>
    <button class="iconbtn" id="sheetclose" style="background:var(--line)" aria-label="Fermer">${ICON.close}</button></div><div class="bd" id="sheetbd"></div></aside>`;
  bindSearch();
  $('#scrim').onclick = closeSheet; $('#sheetclose').onclick = closeSheet;
  $('#themebtn').onclick = () => {
    const r = document.documentElement, cur = r.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    r.dataset.theme = cur === 'dark' ? 'light' : 'dark'; try { localStorage.setItem('occE.theme', r.dataset.theme); } catch (e) {}
  };
  try { const t = localStorage.getItem('occE.theme'); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
  document.addEventListener('click', e => {
    const o = e.target.closest('[data-open]'); if (o) { e.preventDefault(); openEntity(o.dataset.open); return; }
    const g = e.target.closest('[data-go]'); if (g) { e.preventDefault(); closeSheet(); location.hash = g.dataset.go; route(false); }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSheet(); if (e.key === '/' && document.activeElement !== $('#search')) { e.preventDefault(); $('#search').focus(); } });
}
function toast(msg) { const t = document.createElement('div'); t.className = 'toast glass'; t.textContent = msg; document.body.appendChild(t); setTimeout(() => t.remove(), 2200); }
const footer = () => `<footer>OCC ÉNERGIE — Cartographie du réseau électrique · v${esc(D.meta.version)} · consultation hors ligne<br><b>Designed by Labidi El Fahli</b></footer>`;

/* --------------------------------------------------------------- barre de recherche */
let SEL = -1, RES = [];
function bindSearch() {
  const inp = $('#search'), box = $('#results'), clr = $('#clear');
  const render = () => {
    const q = inp.value; clr.style.display = q ? 'block' : 'none';
    if (!q.trim()) { box.classList.remove('open'); return; }
    RES = search(q, 30); SEL = RES.length ? 0 : -1;
    box.innerHTML = RES.length ? RES.map((r, i) => `<div class="res ${i === SEL ? 'sel' : ''}" data-i="${i}">
        <span class="dot ${r.kind === 'node' ? (SW.has(r.t) && !isClosed(r.id) ? 'off' : isLive(r.id) ? 'on' : 'off') : 'unk'}"></span>
        <div style="flex:1;min-width:0"><div class="t">${hl(r.label, q)}</div><div class="p">${esc(recContext(r))}</div></div>
        <span class="pill">${TYPE[r.t] || TYPE[r.kind] || r.t}</span></div>`).join('')
      : `<div class="empty">Aucun résultat pour « ${esc(q)} ».<br><span class="small">Essayez un repère (7K121), un tableau (TGBT 2), un transformateur (TR 6A).</span></div>`;
    box.classList.add('open');
  };
  inp.addEventListener('input', render);
  inp.addEventListener('focus', () => { if (inp.value.trim()) render(); });
  inp.addEventListener('keydown', e => {
    if (!RES.length) return;
    if (e.key === 'ArrowDown') { SEL = Math.min(RES.length - 1, SEL + 1); e.preventDefault(); }
    else if (e.key === 'ArrowUp') { SEL = Math.max(0, SEL - 1); e.preventDefault(); }
    else if (e.key === 'Enter') { pick(RES[SEL]); e.preventDefault(); return; } else return;
    $$('.res', box).forEach((el, i) => el.classList.toggle('sel', i === SEL));
    const s = $('.res.sel', box); if (s) s.scrollIntoView({ block: 'nearest' });
  });
  box.addEventListener('click', e => { const el = e.target.closest('.res'); if (el) pick(RES[+el.dataset.i]); });
  clr.onclick = () => { inp.value = ''; render(); inp.focus(); };
  document.addEventListener('click', e => { if (!e.target.closest('#searchwrap')) box.classList.remove('open'); });
}
function pick(r) {
  if (!r) return; $('#results').classList.remove('open'); $('#search').blur();
  if (r.kind === 'board') { location.hash = '#/b/' + r.id; return; }
  openEntity(r.kind === 'node' ? r.id : r.kind + ':' + r.id);
}

/* --------------------------------------------------------------- fiche */
function openSheet(hd, bd) {
  $('#sheethd').innerHTML = hd; $('#sheetbd').innerHTML = bd; $('#sheetbd').scrollTop = 0;
  $('#sheet').classList.add('open'); $('#scrim').classList.add('open'); $('#sheet').setAttribute('aria-hidden', 'false');
}
function closeSheet() { $('#sheet').classList.remove('open'); $('#scrim').classList.remove('open'); $('#sheet').setAttribute('aria-hidden', 'true'); }
function photoLinks(list) {
  if (!list || !list.length) return '<span class="muted">Aucune photo référencée.</span>';
  return list.map(p => { const m = p.match(/^(.*?\.pdf)\s*(p[\d-]+)?/i); const f = m ? m[1].trim() : p; const pg = m && m[2] ? m[2].replace(/^p(\d+).*/, '$1') : '';
    const real = (D.photofiles || {})[f.normalize('NFC')];   // nom exact sur le disque (é composé ou décomposé)
    return `<div class="li" style="cursor:default"><span>📷</span><div class="grow"><div>${esc(p)}</div><div class="src">Photo non embarquée (règle : façades vectorielles). ${real || !D.photofiles ? `<a href="${PHOTO_BASE}${encodeURIComponent(real || f)}${pg ? '#page=' + pg : ''}" target="_blank" rel="noopener">Ouvrir la source${pg ? ' p. ' + pg : ''}</a>` : '<b>fichier introuvable dans le dossier des photos</b>'}</div></div></div>`; }).join('');
}
function crumbsFor(n) {
  const b = boardOf(n), parts = [];
  if (b) {
    locChain(b.loc).forEach(l => parts.push(`<a data-go="#/">${esc(l.name)}</a>`));
    if (!b.loc) parts.push(`<a data-go="#/registre">Localisation non documentée</a>`);
    parts.push(`<a data-go="#/b/${b.id}">${esc(b.name)}</a>`);
    if (n.half && b.halves && b.halves.length > 1) { const h = b.halves.find(h => h.id === b.id + n.half || h.id === b.id + '_' + n.half || h.id === n.half); if (h) parts.push(`<a data-go="#/b/${b.id}">${esc(h.label)}</a>`); }
    const c = colOf(n); if (c) { parts.push(`<a data-go="#/b/${b.id}/f/${n.id}">Colonne ${c.col}</a>`); parts.push(`<a data-go="#/b/${b.id}/f/${n.id}">Case ${esc(n.case)}</a>`); }
  }
  return `<div class="crumbs">${parts.join('<i>›</i>')}</div>`;
}
function sourcesBlock(id) {
  const paths = upPaths(id);
  if (!paths.length) return `<div class="blk"><h4>Sources d’alimentation</h4><p class="muted">Aucun chemin amont documenté jusqu’à une source.</p></div>`;
  const live = paths.filter(p => p.every(x => !SW.has(NODE[x].t) || isClosed(x) || x === id));
  const n = NODE[id], b = boardOf(n);
  let head = '';
  if (b && NODE[b.id + '_QA'] && NODE[b.id + '_QB'] && (UP[b.id + '_QA'] || []).length && (UP[b.id + '_QB'] || []).length) {
    const qa = NODE[b.id + '_QA'], qb = NODE[b.id + '_QB'], qc = NODE[b.id + '_QC'];
    const tra = (UP[qa.id] || [])[0], trb = (UP[qb.id] || [])[0];
    head = `<div class="kv"><dt>Arrivée 1</dt><dd><a data-open="${qa.id}" href="#">${esc(qa.label)}</a> ${confPill(qa.conf)}<br><span class="small">Transformateur : <a data-open="${tra.a}" href="#">${esc(NODE[tra.a].label)}</a> ${NODE[tra.a].kva ? '· ' + esc(NODE[tra.a].kva) : ''}</span></dd>
      <dt>Arrivée 2</dt><dd><a data-open="${qb.id}" href="#">${esc(qb.label)}</a> ${confPill(qb.conf)}<br><span class="small">Transformateur : <a data-open="${trb.a}" href="#">${esc(NODE[trb.a].label)}</a> ${NODE[trb.a].kva ? '· ' + esc(NODE[trb.a].kva) : ''}</span></dd>
      ${qc ? `<dt>Couplage</dt><dd><a data-open="${qc.id}" href="#">${esc(qc.label)}</a> ${confPill(qc.conf)}${couplerHTML(b)}</dd>` : ''}
      <dt>Config. simulée</dt><dd>${[[qa, 'Arrivée 1'], [qc, 'Couplage'], [qb, 'Arrivée 2']].filter(x => x[0]).map(([x, l]) => `${l} : <b>${isClosed(x.id) ? 'fermé' : 'ouvert'}</b>`).join(' · ')} — <a href="#" data-go="#/b/${b.id}">changer</a></dd></div>`;
  }
  return `<div class="blk"><h4>Sources d’alimentation (${paths.length} chemin${paths.length > 1 ? 's' : ''} documenté${paths.length > 1 ? 's' : ''})</h4>${head}
    <p class="small muted">Chemins amont présents dans les documents, du plus court au plus long. En vert : alimenté dans la configuration simulée. ◌ = appareil ouvert en simulation.</p>
    ${paths.map((p, i) => `<details ${i < 2 ? 'open' : ''}><summary class="small"><b>${i + 1}.</b> ${pathVia(p)} ${live.includes(p) ? '<span class="pill g">chemin fermé</span>' : '<span class="pill">chemin ouvert</span>'}</summary>${pathHTML(p)}</details>`).join('')}</div>`;
}
function sameFeedBlock(id) {
  const n = NODE[id]; const bus = n.t === 'bus' ? id : busOf(id); if (!bus) return '';
  const sib = (DOWN[bus] || []).map(e => NODE[e.b]).filter(x => x.t === 'dep' && x.id !== id);
  const busN = NODE[bus], b = boardOf(busN);
  let other = '';
  if (b && b.halves && b.halves.length === 2) {
    const ob = b.halves.find(h => h.id !== bus); if (ob && NODE[ob.id]) {
      const os = (DOWN[ob.id] || []).map(e => NODE[e.b]).filter(x => x.t === 'dep');
      other = `<h4 style="margin-top:12px">Autre demi-jeu de barres : ${esc(ob.label)} (${os.length})</h4><div class="list">${os.slice(0, 40).map(liNode).join('')}</div>`;
    }
  }
  return `<div class="blk"><h4>Même alimentation — ${esc(short(busN))} (${sib.length} autre${sib.length > 1 ? 's' : ''} départ${sib.length > 1 ? 's' : ''})</h4>
    <div class="list">${sib.slice(0, 60).map(liNode).join('') || '<span class="muted">Aucun autre départ documenté.</span>'}</div>${other}</div>`;
}
function liNode(x) {
  const st = SW.has(x.t) && !isClosed(x.id) ? 'off' : isLive(x.id) ? 'on' : 'off';
  return `<div class="li" data-open="${x.id}"><span class="dot ${st}"></span><div class="grow"><div>${esc(x.label)}</div><div class="src">${esc([x.case ? 'case ' + x.case : '', x.model || '', x.feeds && BOARD[x.feeds] ? '→ ' + BOARD[x.feeds].name : ''].filter(Boolean).join(' · '))}</div></div>${x.conf !== 'confirme' ? confPill(x.conf) : ''}</div>`;
}
function openEntity(key) {
  if (key.startsWith('issue:')) { const i = D.issues.find(x => x.id === key.slice(6)); return openSheet(`<span class="pill a">Incohérence · ${esc(i.sev)}</span><h2>${esc(i.title)}</h2>`, issueBody(i)); }
  if (key.startsWith('proc:')) { const p = D.procs.find(x => x.id === key.slice(5)); return openSheet(`<span class="pill b">Procédure</span><h2>${esc(p.title)}</h2>`, procBody(p)); }
  if (BOARD[key]) { closeSheet(); location.hash = '#/b/' + key; return; }
  const n = NODE[key]; if (!n) return;
  const b = boardOf(n), fid = facadeFor(n.id);
  // l'essentiel en haut (où, quel appareil, quoi faire) ; le reste replié dans « Plus d'informations »
  const hd = `<div class="row"><span class="pill k">${TYPE[n.t] || n.t}</span>${n.conf !== 'confirme' ? confPill(n.conf) : ''}</div><h2>${esc(dn(n) || n.label)}</h2>${crumbsFor(n)}`;
  const kv = [];
  const add = (k, v) => kv.push(`<dt>${k}</dt><dd>${v}</dd>`);
  if (n.case || n.cell) add('Case', esc(n.case || n.cell));
  if (n.model) add('Appareil', esc(n.model));
  if (n.ir) add('Réglage', esc(n.ir));
  if (n.t === 'tr') { add('Puissance', n.kva ? esc(n.kva) : ND); if (n.cooling) add('Surveillance', esc(n.cooling));
    const vent = D.nodes.filter(x => x.aux === n.id); if (vent.length) add('Ventilation', vent.map(v => `<a data-open="${v.id}" href="#">${esc(dn(v))}</a> · ${esc(boardOf(v).name)} case ${esc(v.case)}`).join('<br>')); }
  if (n.aux && NODE[n.aux]) add('Sert à', `auxiliaire de <a data-open="${n.aux}" href="#">${esc(dn(NODE[n.aux]))}</a>`);
  if (n.feeds && BOARD[n.feeds]) add('Alimente', `<a data-go="#/b/${n.feeds}" href="#">${esc(BOARD[n.feeds].name)}</a>`);
  const more = [];
  const addm = (k, v) => more.push(`<dt>${k}</dt><dd>${v}</dd>`);
  addm('Libellé complet', esc(n.label));
  if (n.t === 'tr') { addm('Tensions', esc(n.u || '')); addm('Ucc', esc(n.ucc || '')); }
  if (n.prot) addm('Protection', esc(n.prot));
  if (n.keys) addm('Clés / repères', esc(n.keys));
  if (n.meter) addm('Centrale de mesure', 'n° ' + esc(n.meter));
  if (n.xl) addm('Classeur', `${esc(n.xl.label)}<div class="src">${esc(n.xl.ref)}</div>`);
  addm('Source documentaire', `<span class="small">${esc(n.src || 'Non documenté')}</span>`);
  if (n.note) addm('Remarque', `<span class="small">${esc(n.note)}</span>`);
  addm('État simulé', `${isLive(n.id) ? 'alimenté' : 'non alimenté'}${SW.has(n.t) ? ' · ' + (isClosed(n.id) ? 'fermé' : 'ouvert') : ''} <span class="small muted">(hypothèse, pas une observation)</span>`);
  const iss = D.issues.filter(i => issueActive(i) && (i.ents.includes(n.id) || (b && i.ents.includes(b.id))));
  const procs = D.procs.filter(p => p.ents.includes(n.id));
  const plan = (() => { const r = planFor(n.id) ? n.id : n.board && planFor(n.board) ? n.board : null; return r ? `<button class="btn ghost" data-go="#/plans/${planFor(r)}/${r}">Voir sur le plan</button>` : ''; })();
  const btns = `<div class="row" style="margin:10px 0">
    ${n.t !== 'src' ? `<button class="btn" data-go="#/courant/${n.id}">⚡ Remettre le courant</button>` : ''}
    ${fid ? `<button class="btn ghost" data-go="#/b/${boardForFacade(fid)}/f/${n.id}">Voir sur la façade</button>` : ''}${parcoursContext(n.id).zone ? `<button class="btn ghost" data-go="#/site/${n.id}">📍 Localiser dans l'usine</button>` : ''}${plan}</div>`;
  const ds = n.t === 'tr' || n.t === 'bus' || n.t === 'src' || n.role === 'arrivee' || n.t === 'cpl' ? downstream(n.id).map(x => NODE[x]).filter(x => x.t === 'dep') : [];
  const bd = `${btns}${kv.length ? `<dl class="kv">${kv.join('')}</dl>` : ''}
    ${iss.length ? `<div class="banner sim">⚠️<div class="small">${iss.map(i => `<a href="#" data-open="issue:${i.id}">${esc(i.title)}</a>`).join('<br>')}</div></div>` : ''}
    <details class="blk"><summary><b>Plus d’informations</b></summary>
      <dl class="kv" style="margin-top:8px">${more.join('')}</dl>
      ${obsHTML(n.obs)}
      ${uniBlock(n)}
      ${n.t !== 'src' ? sourcesBlock(n.id) : ''}
      ${n.t === 'dep' || n.t === 'bus' ? sameFeedBlock(n.id) : ''}
      ${ds.length ? `<div class="blk"><h4>Alimente ${ds.length} départ(s)</h4>${groupByBus(ds)}</div>` : ''}
      ${procs.length ? `<div class="blk"><h4>Procédures</h4>${procs.map(p => `<div class="li" data-open="proc:${p.id}"><span>📘</span><div class="grow">${esc(p.title)}<div class="src">${esc(p.status)}</div></div></div>`).join('')}</div>` : ''}
      <div class="row" style="margin-top:10px"><button class="btn ghost" data-go="#/reseau/${n.id}">Voir sur le réseau</button><button class="btn ghost" id="phbtn">Voir la photo</button>
        ${SW.has(n.t) ? `<button class="btn ghost" id="tgl">${isClosed(n.id) ? 'Simuler ouvert' : 'Simuler fermé'}</button>` : ''}<button class="btn ghost" data-go="#/entretien/${n.id}">Journal</button></div>
      <div id="phbox"></div></details>`;
  openSheet(hd, bd);
  $('#phbtn').onclick = () => { $('#phbox').innerHTML = `<div class="blk"><h4>Photos sources (${b ? esc(b.name) : ''})</h4>${photoLinks(b ? b.photos : [])}</div>`; };
  const t = $('#tgl'); if (t) t.onclick = () => { if (setSw(n.id, !isClosed(n.id))) { openEntity(n.id); rerender(); } };
}
/* relevés documentaires (photo ou document) : affichés comme tels, jamais comme un état vérifié sur le terrain */
function obsHTML(obs) {
  if (!obs || !obs.length) return '';
  return `<div class="blk"><h4>Relevés sur documents</h4>${obs.map(o => `<div class="li" style="cursor:default"><span>${o.kind === 'document' ? '📄' : '📷'}</span><div class="grow small">${esc(o.t)}<div class="src">${esc(o.src)} · relu le ${esc(o.d)} · <span class="pill ${o.kind === 'document' ? 'b' : 'a'}">${o.kind === 'document' ? 'lu sur document' : 'lu sur photo — non vérifié sur le terrain'}</span></div></div></div>`).join('')}</div>`;
}
/* règle de couplage en trois champs distincts : règle d'exploitation, verrouillage physique, alarme */
function couplerHTML(b) {
  const c = b.coupler || {}; if (!c.op && !c.lock && !c.alarm && !c.rule) return '';
  const row = (k, v) => v ? `<dt>${k}</dt><dd class="small">${esc(v)}</dd>` : '';
  return `<dl class="kv">${row('Règle d’exploitation', c.op)}${row('Verrouillage physique', c.lock || (c.rule && !/Ronis/i.test(c.rule) ? c.rule : 'Non documenté — à vérifier sur place.'))}${row('Alarme', c.alarm)}${c.rule && /Ronis/i.test(c.rule) && !c.lock ? row('Clés dessinées', c.rule) : ''}</dl>`;
}
/* Bloc « Données unifilaire » : relevé détaillé de l'unifilaire R112529 rév. H (cellule, TC, relais, câble, clés ; transformateur) */
const KEYST = { '●': ['k', 'prisonnière'], '○': ['g', 'libre'], 'Ø': ['', 'absente'] };
function keyPill(k) { const [c, t] = KEYST[k.st] || ['', k.st]; return `<span class="pill ${c}" title="État dessiné sur le plan : clé ${t}">${esc(k.st)} ${t}</span>`; }
function uniBlock(n) {
  const u = n.uni; if (!u) return '';
  const row = (k, v) => v ? `<dt>${k}</dt><dd>${esc(v)}</dd>` : '';
  let h = '';
  if (n.t === 'tr') {
    h = `<dl class="kv">${row('Couplage', u.coupl)}${row('Neutre', u.neutre)}${row('Ucc', u.ucc || n.ucc)}${row('Surveillance', u.surv)}${row('Raccordement HTA', u.fix)}${row('Disjoncteur BT', u.bt)}${row('Clé disjoncteur BT', u.btkeys)}${row('Clés transformateur', u.tkeys)}${row('Destination écrite sur le plan', u.dest)}</dl>`;
  } else {
    h = `<dl class="kv">${row('N° de schéma', u.sch ? 'Sch. ' + u.sch : '')}${row('Repère', u.rep)}${row('Cellule', u.cell)}${row('Appareil', u.device)}${row('Transformateurs de courant', u.tc)}${row('Relais', u.relay)}${row('Réglages', u.settings)}${row('Câble', u.cable)}</dl>`;
    if (u.keys && u.keys.length) h += `<h4 style="margin-top:10px">Clés d’interverrouillage dessinées</h4><div class="tablewrap"><table><tr><th>Clé</th><th>Code</th><th>Emplacement</th><th>État dessiné</th></tr>${u.keys.map(k => `<tr><td><b>${esc(k.name)}</b></td><td class="mono">${esc(k.code || '—')}</td><td class="small">${esc(k.where)}</td><td>${keyPill(k)}</td></tr>`).join('')}</table></div>
      <p class="src">${esc(D.keylegend || '')}</p>`;
  }
  return `<div class="blk"><h4>Données unifilaire (R112529 rév. H — lecture détaillée)</h4>${h}<p class="small muted" style="margin:6px 0 0">Ces clés décrivent l’interverrouillage mécanique prévu par le constructeur ; elles ne constituent pas une procédure de consignation.</p></div>`;
}
function keysSection() {
  const cells = D.nodes.filter(n => n.uni && n.uni.keys && n.uni.keys.length);
  return `<h2>Clés d’interverrouillage HTA (unifilaire)</h2>
  <div class="card glass"><p class="small">${esc(D.keyseries || '')}</p><p class="src">${esc(D.keylegend || '')}</p>
  <div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(260px,1fr));margin:10px 0">${(D.keyboxes || []).map(b => `<div class="blk" style="margin:0"><h4>${esc(b.title)}</h4><div class="small muted">${esc(b.where)}</div><div class="row" style="margin-top:6px">${b.keys.map(([k, s]) => `<span class="mono">${esc(k)}</span>${keyPill({ st: s })}`).join(' ')}</div></div>`).join('')}</div>
  <div class="tablewrap"><table><tr><th>Cellule</th><th>Sch.</th><th>Clés (code)</th></tr>${cells.map(n => `<tr data-open="${n.id}" style="cursor:pointer"><td><b>${esc(short(n))}</b><div class="src">${esc(boardOf(n) ? boardOf(n).name : '')}</div></td><td class="mono">${esc(n.uni.sch || '—')}</td><td class="small">${n.uni.keys.map(k => `${esc(k.name)}${k.code ? ' <span class="mono">(' + esc(k.code) + ')</span>' : ''} ${esc(k.st)}`).join(' · ')}</td></tr>`).join('')}</table></div></div>`;
}
function boardForFacade(fid) { for (const b of D.boards) if (b.facade === fid) return b.id; return fid; }
function groupByBus(list) {
  const g = {}; list.forEach(x => { const bu = busOf(x.id) || '?'; (g[bu] = g[bu] || []).push(x); });
  return Object.entries(g).map(([bu, xs]) => `<details><summary class="small"><b>${esc(NODE[bu] ? short(NODE[bu]) : bu)}</b> — ${xs.length} départ(s)</summary><div class="list">${xs.map(liNode).join('')}</div></details>`).join('');
}
function issueBody(i) {
  return `<div class="row"><span class="pill ${issueActive(i) ? 'a' : 'g'}">${issueActive(i) ? 'Écart actif — à trancher' : 'Résolu'}</span></div><p>${esc(i.text)}</p><div class="blk"><h4>Documents</h4>${i.refs.map(r => `<div class="small">• ${esc(r)}</div>`).join('') || '<span class="muted">—</span>'}</div>
    <div class="blk"><h4>Éléments concernés</h4><div class="list">${i.ents.map(e => NODE[e] ? liNode(NODE[e]) : BOARD[e] ? `<div class="li" data-go="#/b/${e}"><span>▦</span><div class="grow">${esc(BOARD[e].name)}</div></div>` : '').join('')}</div></div>`;
}
function procBody(p) {
  return `<div class="banner ${p.steps.length ? 'info' : 'sim'}">${p.steps.length ? '📘' : '⏳'}<div><b>${esc(p.status)}</b><div class="src">${esc(p.src || 'Aucun document')}</div></div></div>
   ${p.but.length ? `<div class="blk"><h4>${p.steps.length ? 'But du verrouillage' : 'Règle documentée'}</h4>${p.but.map(x => `<div class="small" style="margin:4px 0">• ${esc(x)}</div>`).join('')}</div>` : ''}
   ${p.steps.length ? `<div class="blk"><h4>Fonctionnement (texte du document constructeur)</h4><ol class="small" style="padding-left:18px">${p.steps.map(s => `<li style="margin:5px 0">${esc(s)}</li>`).join('')}</ol></div>` : ''}
   ${p.warn ? `<div class="banner danger">⚠️<div class="small">${esc(p.warn)}</div></div>` : ''}
   ${!p.steps.length && !p.but.length ? '<p class="muted">Emplacement réservé : la procédure validée par les responsables électriques habilités sera intégrée ici. L’application ne génère aucune séquence de manœuvre.</p>' : ''}
   <p class="small muted">Rappel : toute consignation se conforme à la NF C 18-510 et aux instructions permanentes de sécurité du site, par du personnel habilité.</p>`;
}

/* ======================================================================= visionneuse SVG (zoom / déplacement / pincement) */
function mountViewer(host, svg, { onClick, focus, legend, native } = {}) {
  // native : unités SVG par pixel d'image ; ajoute le bouton « 1:1 » (détail natif : 1 pixel d'image = 1 pixel d'écran)
  host.innerHTML = `<div class="viewer glass">${svg}<div class="vtools"><button class="glass" data-z="in" aria-label="Zoom avant">+</button><button class="glass" data-z="out" aria-label="Zoom arrière">−</button><button class="glass" data-z="fit" aria-label="Vue complète" title="Vue complète" style="font-size:15px">⤢</button>${native ? '<button class="glass" data-z="native" aria-label="Détail natif" title="Détail natif (1 pixel d’image = 1 pixel d’écran)" style="font-size:11px;font-weight:800">1:1</button>' : ''}</div>${legend ? `<div class="legend glass">${legend}</div>` : ''}</div>`;
  const wrap = $('.viewer', host), el = $('svg', wrap);
  const vb0 = el.viewBox.baseVal; const init = { x: vb0.x, y: vb0.y, w: vb0.width, h: vb0.height };
  let v = { ...init };
  const apply = () => el.setAttribute('viewBox', `${v.x} ${v.y} ${v.w} ${v.h}`);
  const scale = () => { const r = el.getBoundingClientRect(); return Math.max(v.w / r.width, v.h / r.height); };
  const toSvg = (cx, cy) => { const r = el.getBoundingClientRect(), s = scale(); const ox = (r.width * s - v.w) / 2, oy = (r.height * s - v.h) / 2; return { x: v.x + (cx - r.left) * s - ox, y: v.y + (cy - r.top) * s - oy }; };
  const zoomAt = (f, cx, cy) => { const p = toSvg(cx, cy); const nw = Math.min(init.w * 3, Math.max(init.w / 40, v.w / f)); const k = nw / v.w; v = { x: p.x - (p.x - v.x) * k, y: p.y - (p.y - v.y) * k, w: nw, h: v.h * k }; apply(); };
  const pts = new Map(); let moved = 0, last = null, pinch = null;
  el.addEventListener('pointerdown', e => { el.setPointerCapture(e.pointerId); pts.set(e.pointerId, { x: e.clientX, y: e.clientY }); moved = 0; last = { x: e.clientX, y: e.clientY };
    if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = { d: Math.hypot(a.x - b.x, a.y - b.y) }; } });
  el.addEventListener('pointermove', e => { if (!pts.has(e.pointerId)) return; pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pts.size === 2 && pinch) { const [a, b] = [...pts.values()]; const d = Math.hypot(a.x - b.x, a.y - b.y); zoomAt(d / pinch.d, (a.x + b.x) / 2, (a.y + b.y) / 2); pinch.d = d; moved += 10; return; }
    const s = scale(); const dx = e.clientX - last.x, dy = e.clientY - last.y; moved += Math.abs(dx) + Math.abs(dy); v.x -= dx * s; v.y -= dy * s; last = { x: e.clientX, y: e.clientY }; apply(); });
  const up = e => { pts.delete(e.pointerId); if (pts.size < 2) pinch = null;
    if (e.type === 'pointerup' && moved < 6 && onClick) { const t = document.elementFromPoint(e.clientX, e.clientY); const g = t && t.closest('[data-id]'); if (g) onClick(g.dataset.id, g); } };
  el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
  el.addEventListener('wheel', e => { e.preventDefault(); zoomAt(e.deltaY < 0 ? 1.18 : 1 / 1.18, e.clientX, e.clientY); }, { passive: false });
  $$('.vtools button', wrap).forEach(b => b.onclick = () => { const r = el.getBoundingClientRect();
    if (b.dataset.z === 'fit') { v = { ...init }; apply(); }
    else if (b.dataset.z === 'native') { const cx = v.x + v.w / 2, cy = v.y + v.h / 2, w = r.width * native, h = r.height * native; v = { x: cx - w / 2, y: cy - h / 2, w, h }; apply(); }
    else zoomAt(b.dataset.z === 'in' ? 1.4 : 1 / 1.4, r.left + r.width / 2, r.top + r.height / 2); });
  const focusOn = id => { const g = el.querySelector(`[data-id="${CSS.escape(id)}"]`); if (!g) return false; $$('.flash', el).forEach(x => x.classList.remove('flash')); g.classList.add('flash');
    const bb = g.getBBox(); const w = Math.max(bb.width * 3.2, init.w / 6), h = Math.max(bb.height * 3.2, init.h / 6); v = { x: bb.x + bb.width / 2 - w / 2, y: bb.y + bb.height / 2 - h / 2, w, h }; apply(); return true; };
  if (focus) requestAnimationFrame(() => focusOn(focus));
  return { focusOn, reset: () => { v = { ...init }; apply(); } };
}

/* ======================================================================= façades vectorielles */
const U = 27.5, FH = 2200; // 80 modules = 2200 mm
const STY = {
  okken_beige: { panel: '#e3d69c', shade: '#cfc184', grille: '#2b2b2b', line: '#1f9a54', ink: '#1e1e1e', brd: '#9b8f5c' },
  okken_blanc: { panel: '#efede6', shade: '#d6d3c9', grille: '#2b2d2f', line: '#24a35a', ink: '#1e1e1e', brd: '#a3a094' },
  prisma_beige: { panel: '#e4d7a6', shade: '#c9bb86', grille: '#4a4a44', line: '#2f2f2f', ink: '#1e1e1e', brd: '#a59769' },
  enclosure_blanc: { panel: '#f3f3f0', shade: '#cfd0cb', grille: '#3a3b3d', line: '#333', ink: '#1e1e1e', brd: '#a3a5a0', plain: true },
  armoire_grise: { panel: '#dcddd8', shade: '#bfc1bb', grille: '#4a4c4e', line: '#333', ink: '#1e1e1e', brd: '#94968f', plain: true },
  okken_blanc_noir: { panel: '#f4f4f2', shade: '#d4d4cf', grille: '#262626', line: '#1c1c1c', ink: '#1e1e1e', brd: '#a7a7a2' },
  okken_blanc_vert: { panel: '#f6f6f4', shade: '#d9d9d5', grille: '#1e1e1e', line: '#4b4b4b', ink: '#1e1e1e', brd: '#a7a7a2', band: '#3dcd58' },
};
const PLATE = { red: ['#d62828', '#fff'], green: ['#1e9e57', '#fff'], black: ['#141414', '#f2f2f2'], yellow: ['#f7d117', '#222'], white: ['#ffffff', '#222'], blue: ['#9fd3f5', '#123'] };
function plateSVG(x, y, w, h, label, color, fs = 20) {
  const [bg, fg] = PLATE[color] || PLATE.white;
  const lines = String(label || '').split(' / ').flatMap(l => wrapText(l, Math.max(6, Math.floor(w / (fs * 0.62)))));
  const lh = fs * 1.12, th = lines.length * lh, hh = Math.max(h, th + 10);
  return `<rect x="${x}" y="${y}" width="${w}" height="${hh}" rx="3" fill="${bg}" stroke="rgba(0,0,0,.25)"/>` +
    lines.map((l, i) => `<text x="${x + w / 2}" y="${y + (hh - th) / 2 + lh * (i + .8)}" font-size="${fs}" text-anchor="middle" fill="${fg}" font-weight="700" font-family="Arial Narrow,Arial,sans-serif" ${color === 'yellow' ? 'font-style="italic"' : ''}>${esc(l)}</text>`).join('');
}
function wrapText(s, n) { const w = String(s).split(' '), out = []; let cur = ''; w.forEach(x => { if ((cur + ' ' + x).trim().length > n && cur) { out.push(cur); cur = x; } else cur = (cur + ' ' + x).trim(); }); if (cur) out.push(cur); return out; }
const voyants = (cx, y, n = 3) => { const cols = ['#e5333a', '#16b36b', '#f5a524'].slice(0, n); const w = n * 34 + 10; return `<rect x="${cx - w / 2}" y="${y}" width="${w}" height="40" rx="5" fill="#1d1d1d"/>` + cols.map((c, i) => `<circle cx="${cx - w / 2 + 22 + i * 34}" cy="${y + 20}" r="13" fill="${c}" stroke="#000" stroke-width="2"/><circle cx="${cx - w / 2 + 18 + i * 34}" cy="${y + 15}" r="4" fill="rgba(255,255,255,.55)"/>`).join(''); };
const meterSVG = (x, y, w = 110, h = 96, blue = false) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" fill="#2d2f31"/><rect x="${x + 10}" y="${y + 10}" width="${w - 20}" height="${h - 34}" rx="2" fill="${blue ? '#9ec5ee' : '#a9b6a6'}"/>` +
  [0, 1, 2, 3].map(i => `<rect x="${x + 12 + i * (w - 24) / 4}" y="${y + h - 18}" width="${(w - 24) / 4 - 6}" height="8" rx="2" fill="#5d6064"/>`).join('');
function breakerSVG(kind, x, y, w, h) {
  // Masterpact NW / MTZ / NT, Compact NS / NSX — vue de face simplifiée par gamme
  if (kind === 'nw' || kind === 'nwc' || kind === 'nt') {
    const s = `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8" fill="#262626"/>` +
      `<rect x="${x + w * .06}" y="${y + h * .06}" width="${w * .88}" height="${h * .74}" rx="4" fill="#3b3b3d"/>` +
      `<rect x="${x + w * .1}" y="${y + h * .12}" width="${w * .16}" height="${h * .55}" rx="3" fill="#c9ccc8"/>` +
      `<rect x="${x + w * .12}" y="${y + h * .15}" width="${w * .12}" height="${h * .1}" fill="#6f8f6a"/>` +
      `<rect x="${x + w * .32}" y="${y + h * .1}" width="${w * .38}" height="${h * .6}" rx="3" fill="#2f2f30"/>` +
      `<circle cx="${x + w * .44}" cy="${y + h * .22}" r="${Math.min(w, h) * .055}" fill="#d62828"/><rect x="${x + w * .55}" y="${y + h * .17}" width="${w * .1}" height="${h * .1}" fill="#111" stroke="#666"/>` +
      `<rect x="${x + w * .4}" y="${y + h * .38}" width="${w * .26}" height="${h * .2}" fill="#f4f4f4"/><rect x="${x + w * .72}" y="${y + h * .1}" width="${w * .14}" height="${h * .6}" rx="3" fill="#2f2f30"/>` +
      `<rect x="${x + w * .06}" y="${y + h * .82}" width="${w * .88}" height="${h * .12}" rx="3" fill="#171717"/><circle cx="${x + w * .5}" cy="${y + h * .88}" r="${h * .035}" fill="#555"/>`;
    return kind === 'nwc' ? s + `<rect x="${x - 10}" y="${y - 10}" width="${w + 20}" height="${h + 20}" rx="18" fill="rgba(190,225,255,.22)" stroke="#9fb7c9" stroke-width="3"/>` : s;
  }
  if (kind === 'ns') return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" fill="#262626"/><rect x="${x + w * .1}" y="${y + h * .08}" width="${w * .8}" height="${h * .84}" rx="4" fill="#3a3a3c"/>` +
    `<rect x="${x + w * .18}" y="${y + h * .2}" width="${w * .28}" height="${h * .45}" fill="#c9ccc8"/><rect x="${x + w * .55}" y="${y + h * .22}" width="${w * .2}" height="${h * .52}" rx="4" fill="#111"/><rect x="${x + w * .58}" y="${y + h * .28}" width="${w * .14}" height="${h * .2}" fill="#d9d9d9"/>`;
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="5" fill="#2a2a2a"/><circle cx="${x + w / 2}" cy="${y + h / 2}" r="${Math.min(w, h) * .3}" fill="#151515" stroke="#555" stroke-width="3"/><rect x="${x + w / 2 - 6}" y="${y + h * .22}" width="12" height="${h * .56}" rx="4" fill="#cfcfcf"/>`;
}
function unitSVG(u, x, w, st, opts) {
  const y = u.y * U, h = u.h * U, cx = x + (u.x ? u.x * w : w / 2), id = u.dep || u.node;
  let s = '';
  const pw = Math.min(w * .8, 520);
  switch (u.k) {
    case 'nw': case 'nwc': case 'nt': case 'ns': case 'nsx': {
      const bw = { nw: .62, nwc: .62, nt: .5, ns: .46, nsx: .34 }[u.k] * w, plH = 2.6 * U;
      if (u.label) s += plateSVG(cx - pw / 2, y, pw, plH, u.label, u.plate || 'green', w < 400 ? 16 : 20);
      if (u.tr) s += `<g transform="translate(${x + 40},${y + 18})" stroke="${st.line}" stroke-width="6" fill="none"><path d="M0 22h26M0 34h14"/><circle cx="58" cy="28" r="20"/><circle cx="84" cy="28" r="20"/><path d="M104 28h26"/></g>`;
      const bh = Math.min(h - plH - 12, u.k === 'nsx' ? 4.6 * U : u.k === 'ns' ? 9 * U : 14 * U);
      s += breakerSVG(u.k, cx - bw / 2, y + plH + 10, bw, Math.max(bh, 2.5 * U));
      break;
    }
    case 'doorcell': {
      const lx = x + w * .38;
      if (u.voy) s += voyants(lx, y);
      if (u.meter) { s += meterSVG(lx - 55, y + 70, 110, 96, false); if (u.num) s += `<rect x="${lx - 92}" y="${y + 76}" width="30" height="30" fill="#f7d117"/><text x="${lx - 77}" y="${y + 98}" font-size="20" text-anchor="middle" font-weight="700">${esc(u.num)}</text>`; }
      s += plateSVG(x + w * .5, y + (u.meter ? 82 : 48), w * .46, 2.6 * U, u.label, u.plate || 'green', 15);
      break;
    }
    case 'meter': s += meterSVG(cx - 55, y, 110, Math.min(h, 4) * U * .9, false); if (u.num) s += `<rect x="${cx - 92}" y="${y + 6}" width="30" height="30" fill="#f7d117"/><text x="${cx - 77}" y="${y + 28}" font-size="20" text-anchor="middle" font-weight="700">${esc(u.num)}</text>`; break;
    case 'voy': s += voyants(cx, y); break;
    case 'voy2': s += voyants(cx, y, 2); break;
    case 'mod2': s += `<rect x="${cx - 52}" y="${y}" width="46" height="72" rx="4" fill="#f4f4f4" stroke="#999"/><rect x="${cx + 6}" y="${y}" width="46" height="72" rx="4" fill="#f4f4f4" stroke="#999"/>`; break;
    case 'imd': s += `<rect x="${cx - 160}" y="${y}" width="320" height="170" rx="8" fill="#d6d6d2" stroke="#999"/><rect x="${cx - 60}" y="${y + 18}" width="200" height="135" rx="6" fill="#2b2d30"/><rect x="${cx - 46}" y="${y + 32}" width="110" height="80" fill="#9ec5ee"/><text x="${cx + 9}" y="${y + 82}" font-size="26" text-anchor="middle" font-weight="700" fill="#123">IM400</text>` +
      `<rect x="${cx - 150}" y="${y + 30}" width="80" height="110" rx="4" fill="#3a3c3f"/>${[0, 1, 2].map(i => `<circle cx="${cx - 110}" cy="${y + 52 + i * 30}" r="7" fill="${i ? '#16b36b' : '#f5a524'}"/>`).join('')}`; break;
    case 'temp': s += `<rect x="${cx - 50}" y="${y}" width="100" height="90" rx="5" fill="#141414"/><text x="${cx}" y="${y + 50}" font-size="36" text-anchor="middle" fill="#ff3b30" font-family="monospace" font-weight="700">°C</text>`; break;
    case 'blank': if (u.label) s += `<rect x="${cx - 110}" y="${y}" width="220" height="34" fill="#fff" stroke="#aaa"/><text x="${cx}" y="${y + 23}" font-size="14" text-anchor="middle">${esc(u.label.slice(0, 26))}</text>`; break;
    case 'plate': s += plateSVG(u.x ? cx - 110 : x + 40, y, u.x ? 220 : Math.min(250, w * .5), h, u.label, u.plate || 'black', 15); break;
    case 'arc': { const aw = u.x ? w * .4 : 250, ax = u.x ? cx - aw / 2 : x + 40 + 260; s += `<rect x="${ax}" y="${y}" width="${aw}" height="${h}" fill="#fff" stroke="#888"/><rect x="${ax}" y="${y}" width="${aw}" height="${h * .3}" fill="#1e9e57"/><text x="${ax + aw / 2}" y="${y + h * .2}" font-size="16" text-anchor="middle" fill="#fff" font-weight="700">ATTENTION</text>` +
      wrapText(u.label.replace(/^ATTENTION\s*/, ''), Math.floor(aw / 9)).slice(0, 6).map((l, i) => `<text x="${ax + 8}" y="${y + h * .3 + 20 + i * 17}" font-size="13" fill="#222">${esc(l)}</text>`).join(''); break; }
    case 'drawer': {
      s += `<rect x="${x + 14}" y="${y + 6}" width="${w - 28}" height="${h - 12}" fill="none" stroke="${st.shade}" stroke-width="4"/>`;
      if (u.label) s += plateSVG(x + 30, y + 14, Math.min(260, w * .5), 60, u.label, u.plate || 'white', 15);
      const by = y + h * .45;
      s += `<rect x="${x + 30}" y="${by}" width="70" height="120" rx="5" fill="#1d1d1d"/><rect x="${x + 50}" y="${by + 40}" width="44" height="30" fill="#c0392b"/>` +
        `<rect x="${x + 130}" y="${by}" width="90" height="110" rx="6" fill="#2b2b2b"/><circle cx="${x + 175}" cy="${by + 55}" r="34" fill="#151515"/><rect x="${x + 150}" y="${by + 47}" width="58" height="16" rx="6" fill="#ddd" transform="rotate(-35 ${x + 175} ${by + 55})"/>` +
        `<circle cx="${x + 260}" cy="${by + 30}" r="17" fill="#16b36b" stroke="#000" stroke-width="3"/>` + (u.counter === false ? '' : `<circle cx="${x + 260}" cy="${by + 75}" r="17" fill="#e5333a" stroke="#000" stroke-width="3"/><rect x="${x + 300}" y="${by + 20}" width="80" height="70" fill="#fafafa" stroke="#555"/><text x="${x + 340}" y="${by + 62}" font-size="16" text-anchor="middle" font-family="monospace">0000h</text>`) +
        `<circle cx="${x + w - 120}" cy="${by + 55}" r="18" fill="#1d4ed8"/><text x="${x + w - 120}" y="${by + 62}" font-size="20" text-anchor="middle" fill="#fff" font-weight="700">R</text><rect x="${x + w - 80}" y="${by - 5}" width="50" height="130" rx="5" fill="#1d1d1d"/>`;
      break;
    }
    case 'window': s += `<rect x="${x + w * .18}" y="${y}" width="${w * .64}" height="${h}" rx="6" fill="#30363a" opacity=".9"/>${[0, 1, 2, 3].map(i => `<rect x="${x + w * .25 + i * w * .14}" y="${y + 20}" width="16" height="${h - 40}" fill="#b87333" opacity=".55"/>`).join('')}<text x="${x + w / 2}" y="${y + h / 2}" font-size="18" fill="#fff" text-anchor="middle">${esc(u.label || '')}</text>`; break;
    case 'ats': s += `<rect x="${cx - 100}" y="${y}" width="200" height="230" rx="8" fill="#26292c"/><circle cx="${cx}" cy="${y + 110}" r="34" fill="#444" stroke="#888" stroke-width="4"/><rect x="${cx - 90}" y="${y + 190}" width="85" height="26" fill="#2563eb"/><rect x="${cx + 5}" y="${y + 190}" width="85" height="26" fill="#2563eb"/><text x="${cx - 47}" y="${y + 208}" font-size="12" fill="#fff" text-anchor="middle">A↔FORÇAGE</text><text x="${cx + 47}" y="${y + 208}" font-size="12" fill="#fff" text-anchor="middle">A↔AUTO</text>`; break;
    case 'paper': s += `<rect x="${cx - 160}" y="${y}" width="320" height="${h}" fill="#fbfbfb" stroke="#bbb"/><rect x="${cx - 70}" y="${y + 20}" width="200" height="50" fill="#f7d117"/><text x="${cx}" y="${y + h - 14}" font-size="13" text-anchor="middle" fill="#555">consigne affichée</text>`; break;
    case 'bluetags': s += [0, 1, 2, 3, 4].map(i => `<rect x="${x + 40 + (i % 3) * 150}" y="${y + Math.floor(i / 3) * 40}" width="130" height="24" fill="#9fd3f5"/>`).join(''); break;
    case 'rot': { // Compact NS à commande rotative prolongée (poignée noire, plastron Okken)
      const plH = 2.6 * U, bw = Math.min(w * .5, 330), bh = Math.min(h - plH - 14, 300), bx = cx - bw / 2, by = y + plH + 10;
      if (u.label) s += plateSVG(cx - pw / 2, y, pw, plH, u.label, u.plate || 'green', w < 400 ? 16 : 19);
      s += `<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="6" fill="#262626"/><rect x="${bx + bw * .1}" y="${by + bh * .08}" width="${bw * .8}" height="${bh * .5}" rx="4" fill="#353537"/>
        <circle cx="${bx + bw * .38}" cy="${by + bh * .33}" r="${bh * .12}" fill="#151515" stroke="#555" stroke-width="3"/><rect x="${bx + bw * .38 - 8}" y="${by + bh * .33 - 8}" width="${bw * .38}" height="16" rx="7" fill="#1b1b1b" stroke="#777" transform="rotate(-25 ${bx + bw * .38} ${by + bh * .33})"/>
        <rect x="${bx + bw * .1}" y="${by + bh * .62}" width="${bw * .8}" height="${bh * .14}" fill="#3e3e40"/><rect x="${bx + bw * .1}" y="${by + bh * .8}" width="${bw * .8}" height="${bh * .14}" rx="3" fill="#111"/>`;
      break;
    }
    case 'imd2': { // module de mesure / contrôleur d'isolement en façade
      const bw = Math.min(w - 60, 360), bx = cx - bw / 2, bh = Math.max(h * .85, 90);
      s += `<rect x="${bx}" y="${y}" width="${bw}" height="${bh}" rx="8" fill="#2c2f33"/><rect x="${bx + 14}" y="${y + 12}" width="${bw * .42}" height="${bh - 40}" rx="3" fill="#9ec5ee"/>
        <rect x="${bx + bw * .52}" y="${y + 12}" width="${bw * .2}" height="${bh - 40}" rx="3" fill="#4b5056"/><rect x="${bx + bw * .76}" y="${y + 12}" width="${bw * .18}" height="${bh - 40}" rx="3" fill="#dfe3e6"/>
        <text x="${cx}" y="${y + bh - 10}" font-size="15" text-anchor="middle" fill="#e8eef2">${esc((u.label || '').slice(0, Math.floor(bw / 8.5)))}</text>`;
      break;
    }
    case 'rot2': { // tiroir Prisma : poignée rotative, plaque, voyant
      const hh = h - 10;
      s += `<rect x="${x + 14}" y="${y + 4}" width="${w - 28}" height="${hh}" fill="none" stroke="${st.shade}" stroke-width="3"/>
        <rect x="${x + 40}" y="${y + hh * .2}" width="46" height="${hh * .6}" rx="4" fill="#1d1d1d"/><rect x="${x + 50}" y="${y + hh * .3}" width="26" height="${hh * .25}" fill="#c0392b"/>
        <circle cx="${x + 140}" cy="${y + hh / 2 + 4}" r="${Math.min(30, hh * .32)}" fill="#2a2a2a"/><rect x="${x + 122}" y="${y + hh / 2}" width="36" height="9" rx="4" fill="#ddd" transform="rotate(-35 ${x + 140} ${y + hh / 2 + 4})"/>
        <circle cx="${x + 200}" cy="${y + hh / 2 + 4}" r="11" fill="#16b36b" stroke="#000" stroke-width="2"/>
        ${plateSVG(x + 230, y + hh * .25, Math.min(w - 290, 330), hh * .5, u.label || '', u.plate || 'black', 13)}`;
      break;
    }
    case 'hmi': { const bw = Math.min(w * .5, 360), bh = Math.max(h, 110) * .8;
      s += `<rect x="${cx - bw / 2}" y="${y}" width="${bw}" height="${bh}" rx="10" fill="#1f2326"/><rect x="${cx - bw / 2 + 18}" y="${y + 16}" width="${bw - 36}" height="${bh - 52}" rx="4" fill="#8fc3ef"/>
        <rect x="${cx - bw / 2 + 30}" y="${y + 28}" width="${bw * .5}" height="10" fill="#e9f3fb" opacity=".8"/><rect x="${cx - bw / 2 + 30}" y="${y + 46}" width="${bw * .35}" height="10" fill="#e9f3fb" opacity=".6"/>
        ${[0, 1, 2, 3].map(i => `<rect x="${cx - bw / 2 + 24 + i * (bw - 48) / 4}" y="${y + bh - 28}" width="${(bw - 48) / 4 - 8}" height="14" rx="3" fill="#2f6fb3"/>`).join('')}
        ${u.label ? `<text x="${cx}" y="${y + bh + 22}" font-size="16" text-anchor="middle" fill="#333">${esc(u.label)}</text>` : ''}`; break; }
    case 'grille': { const gw = Math.min(w * .62, 520), gx = cx - gw / 2, gh = h * .9;
      s += `<rect x="${gx}" y="${y}" width="${gw}" height="${gh}" rx="6" fill="#e9eae6" stroke="#9a9c98" stroke-width="3"/>` + Array.from({ length: Math.max(3, Math.floor(gh / 22)) }, (_, i) => `<rect x="${gx + 14}" y="${y + 12 + i * 22}" width="${gw - 28}" height="9" rx="3" fill="#a9aba6"/>`).join(''); break; }
    case 'handle': s += `<rect x="${cx - 16}" y="${y}" width="32" height="${Math.max(h, 110) * .8}" rx="10" fill="#2a2a2a"/><circle cx="${cx}" cy="${y + Math.max(h, 110) * .55}" r="7" fill="#888"/>`; break;
    case 'estop': s += `<circle cx="${cx}" cy="${y + 50}" r="58" fill="#f7d117" stroke="#c9a800" stroke-width="3"/><circle cx="${cx}" cy="${y + 50}" r="34" fill="#d62828" stroke="#8a1010" stroke-width="4"/><circle cx="${cx - 10}" cy="${y + 40}" r="9" fill="rgba(255,255,255,.45)"/>
      <text x="${cx}" y="${y + 126}" font-size="14" text-anchor="middle" fill="#333" font-weight="700">ARRÊT D’URGENCE</text>`; break;
    case 'gauge': s += `${u.label ? `<rect x="${cx - 70}" y="${y - 34}" width="140" height="26" fill="#222"/><text x="${cx}" y="${y - 15}" font-size="14" text-anchor="middle" fill="#fff" font-weight="700">${esc(u.label)}</text>` : ''}
      <rect x="${cx - 80}" y="${y}" width="160" height="160" rx="6" fill="#1d1d1d"/><rect x="${cx - 66}" y="${y + 14}" width="132" height="132" rx="4" fill="#f6f6f2"/>
      <path d="M${cx - 50} ${y + 112}A60 60 0 0 1 ${cx + 50} ${y + 112}" fill="none" stroke="#333" stroke-width="3"/><line x1="${cx}" y1="${y + 120}" x2="${cx + 34}" y2="${y + 60}" stroke="#c0392b" stroke-width="4"/><circle cx="${cx}" cy="${y + 120}" r="7" fill="#333"/>`; break;
    case 'varlogic': s += `<rect x="${cx - 75}" y="${y}" width="150" height="150" rx="8" fill="#2a2d30"/><rect x="${cx - 55}" y="${y + 22}" width="110" height="52" rx="3" fill="#b8c4b0"/><circle cx="${cx}" cy="${y + 112}" r="20" fill="#1c1c1c" stroke="#555" stroke-width="3"/><rect x="${cx + 40}" y="${y + 8}" width="24" height="14" fill="#1e9e57"/>`; break;
    case 'rotsec': s += `<rect x="${cx - 60}" y="${y}" width="120" height="140" rx="6" fill="#f7d117" stroke="#333" stroke-width="2"/><circle cx="${cx}" cy="${y + 70}" r="40" fill="#d62828"/><rect x="${cx - 10}" y="${y + 24}" width="20" height="92" rx="6" fill="#a11" transform="rotate(30 ${cx} ${y + 70})"/>
      ${u.label ? `<text x="${cx}" y="${y + 166}" font-size="14" text-anchor="middle" fill="#333">${esc(u.label)}</text>` : ''}`; break;
    case 'modrow': { const items = (u.label || '').split(' · '), rw = w - 80, iw = rw / Math.max(items.length, 1), rh = Math.max(h, 110);
      s += `<rect x="${x + 40}" y="${y}" width="${rw}" height="${rh}" rx="4" fill="#e7e8e4" stroke="#b9bab5"/><rect x="${x + 40}" y="${y + rh * .45}" width="${rw}" height="10" fill="#b5b7b2"/>` +
        items.map((it, i) => { const ix = x + 40 + i * iw; return `<rect x="${ix + 6}" y="${y + 6}" width="${iw - 12}" height="30" fill="#fff" stroke="#999"/><text x="${ix + iw / 2}" y="${y + 26}" font-size="${Math.min(14, (iw - 16) / Math.max(it.length, 1) * 1.7)}" text-anchor="middle" fill="#222">${esc(it)}</text>` +
          [0, 1, 2].map(k => `<rect x="${ix + iw / 2 - 45 + k * 32}" y="${y + rh * .35}" width="26" height="${rh * .5}" rx="3" fill="#f4f4f4" stroke="#777"/><rect x="${ix + iw / 2 - 40 + k * 32}" y="${y + rh * .5}" width="16" height="16" fill="#1e9e57"/>`).join(''); }).join(''); break; }
    case 'sel': s += [0, 1, 2].map(i => `<rect x="${cx - 160 + i * 110}" y="${y}" width="70" height="70" rx="6" fill="#f4f4f4" stroke="#888"/><circle cx="${cx - 125 + i * 110}" cy="${y + 35}" r="22" fill="#222"/><rect x="${cx - 129 + i * 110}" y="${y + 13}" width="8" height="44" rx="3" fill="#eee"/>`).join('') + voyants(cx + 40, y + 90, 2); break;
  }
  if (id) {
    let lv = opts.live ? (SW.has(NODE[id].t) && !isClosed(id) ? 'off' : isLive(id) ? 'on' : 'off') : null;
    if (lv === 'off' && !upPaths(id, 1).length) lv = 'unk'; // alimentation amont non documentée : ni vert ni rouge
    const bx = x + 8, by = y - 6, bw = w - 16, bh = Math.max(h, 2.6 * U) + 12;
    const tint = lv && lv !== 'unk' ? `<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="10" fill="${lv === 'on' ? 'rgba(18,183,106,.13)' : 'rgba(229,72,77,.16)'}"/>` : '';
    const dot = lv ? `<circle cx="${x + w - 30}" cy="${y + 14}" r="16" fill="${lv === 'on' ? '#12b76a' : lv === 'unk' ? '#9aa5a0' : '#e5484d'}" stroke="#fff" stroke-width="4"/>` : '';
    if (u.est) s += `<rect x="${x + 10}" y="${y - 2}" width="${w - 20}" height="${h + 2}" rx="6" fill="none" stroke="#3b82f6" stroke-width="3" stroke-dasharray="10 7"><title>Position estimée (ordre du classeur) — à confirmer sur site</title></rect>`;
    const tg = u.est ? '' : tagText(NODE[id]);
    if (tg && u.k !== 'plate') { const tw = Math.min(w - 90, tg.length * 11 + 24), ty = y + Math.max(h, 2.6 * U) - 2, mx = Math.floor(tw / 10.5);
      s += `<rect x="${x + w / 2 - tw / 2 + 20}" y="${ty - 26}" width="${tw}" height="30" rx="8" fill="rgba(255,255,255,.92)" stroke="#9aa"/><text class="tag" x="${x + w / 2 + 20}" y="${ty - 5}" font-size="18" text-anchor="middle" fill="#123" font-family="Consolas,Menlo,monospace">${esc(tg.length > mx ? tg.slice(0, mx - 1) + '…' : tg)}</text>`; }
    s = `<g class="hit" data-id="${id}"><title>${esc(NODE[id].label)}</title>${tint}${s}${dot}<rect class="hl" x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="10"/><rect x="${bx}" y="${by}" width="${bw}" height="${bh}" fill="transparent"/></g>`;
  }
  return s;
}
function facadeSVG(fid, opts = {}) {
  const f = D.facades[fid];
  if (f.cells) return f.style === 'sm6p' ? sm6pSVG(f, opts) : sm6SVG(f, opts);
  const st = STY[f.style] || STY.okken_blanc;
  const W = f.cols.reduce((a, c) => a + c.w, 0);
  let x = 0, body = '';
  f.cols.forEach(c => {
    const w = c.w;
    body += `<rect x="${x}" y="0" width="${w}" height="${FH}" fill="${st.panel}" stroke="${st.brd}" stroke-width="3"/>`;
    if (!st.plain) body += `<rect x="${x}" y="0" width="${w}" height="110" fill="${st.grille}"/>` + Array.from({ length: Math.floor(w / 18) }, (_, i) => `<rect x="${x + 9 + i * 18}" y="18" width="7" height="74" rx="2" fill="#4a4a4a"/>`).join('');
    if (st.band) body += `<rect x="${x}" y="110" width="${w}" height="56" fill="${st.band}"/>${w > 400 ? `<text x="${x + w - 30}" y="146" font-size="20" text-anchor="end" fill="#fff" font-weight="700">Schneider</text>` : ''}`;
    body += st.plain ? `<rect x="${x}" y="${FH - 70}" width="${w}" height="70" fill="${st.grille}"/>` : `<rect x="${x}" y="${FH - 95}" width="${w}" height="95" fill="${st.grille}"/>`;
    // portes
    let doors = c.doors;
    if (!doors) { const ys = c.units.map(u => u.y).sort((a, b) => a - b); doors = []; let prev = st.band ? 6.5 : 4.5; ys.forEach(y => { if (y - 1 > prev) doors.push([prev, y - 1]); prev = y - 1; }); doors.push([prev, 76.5]); }
    doors.forEach(([a, b]) => { const y0 = Math.max(a * U, st.band ? 170 : 112), y1 = Math.min(b * U, FH - 98); if (y1 - y0 < 30) return;
      body += `<rect x="${x + 8}" y="${y0 + 4}" width="${w - 16}" height="${y1 - y0 - 8}" rx="4" fill="${st.panel}" stroke="${st.shade}" stroke-width="3"/>`;
      if (w >= 240 && y1 - y0 > 160) body += `<rect x="${x + w - 44}" y="${y0 + (y1 - y0) / 2 - 38}" width="26" height="76" rx="6" fill="#2a2a2a"/><circle cx="${x + w - 31}" cy="${y0 + (y1 - y0) / 2 + 20}" r="6" fill="#777"/>`; });
    if (c.n) body += `<text x="${x + w - 26}" y="${st.band ? 222 : 190}" font-size="62" text-anchor="end" font-weight="800" fill="#1a1a1a">${esc(c.n)}</text>`;
    x += w;
  });
  body += synopticSVG(f, st, opts);
  x = 0;
  // vitres et étiquettes d'arc d'abord : les appareils et étiquettes de départ se dessinent par-dessus
  const order = u => (u.k === 'window' && !u.dep ? 0 : u.k === 'arc' ? 1 : 2);
  f.cols.forEach(c => { c.units.slice().sort((a, b) => order(a) - order(b)).forEach(u => body += unitSVG(u, x, c.w, st, opts)); x += c.w; });
  const title = f.title ? `<rect x="${W * .42}" y="${st.band ? 230 : 200}" width="${Math.min(560, W * .3)}" height="0" fill="none"/>` : '';
  return `<svg viewBox="-60 -140 ${W + 120} ${FH + 220}" xmlns="http://www.w3.org/2000/svg" font-family="Arial,Helvetica,sans-serif">
    <text x="0" y="-70" font-size="54" font-weight="800" fill="currentColor">${esc(f.title || '')}</text>
    <text x="0" y="-22" font-size="26" fill="currentColor" opacity=".6">${esc(f.brand || '')} — reconstruction vectorielle (non photographique)</text>
    ${body}${title}<rect x="0" y="0" width="${W}" height="${FH}" fill="none" stroke="#222" stroke-width="5"/></svg>`;
}
/* Synoptique de façade : reproduit les traits verts collés sur les portes (jeu de barres, descentes, départs ▶, arrivées ⊚, couplage)
   et les colore selon la simulation ; trait animé = passage du courant. */
function synopticSVG(f, st, opts) {
  const fid = Object.keys(D.facades).find(k => D.facades[k] === f), bid = boardForFacade(fid), b = BOARD[bid];
  if (!b || !b.halves || b.halves.length < 2 || b.kind === 'Condensateurs') return '';
  const busId = h => (b.halves.find(x => x.id.endsWith(h)) || {}).id;
  const BY = st.band ? 205 : 160, LW = 11;
  const unitHalf = u => { const n = NODE[u.dep || u.node]; if (!n) return null; if (n.t === 'cpl') return 'C'; const bu = busOf(n.id); if (bu && NODE[bu] && NODE[bu].t === 'bus') return bu.slice(-1); if (n.half) return String(n.half).slice(-1); return null; };
  let x = 0, prev = 'A';
  const cols = f.cols.map(c => { const hs = c.units.map(unitHalf).filter(h => h === 'A' || h === 'B');
    const hasC = c.units.some(u => unitHalf(u) === 'C');
    const half = hs.length ? (hs.filter(h => h === 'B').length > hs.length / 2 ? 'B' : 'A') : prev; prev = half;
    const r = { x, w: c.w, c, half, hasC }; x += c.w; return r; });
  const cpl = cols.find(c => c.hasC);
  const cplU = cpl ? cpl.c.units.find(u => unitHalf(u) === 'C') : null;
  const cplX = cpl ? cpl.x + cpl.w / 2 : null;
  const col = id => (SW.has(NODE[id].t) && !isClosed(id) ? false : isLive(id));
  const seg = (d, live) => `<path d="${d}" fill="none" stroke="${live ? '#12b76a' : '#e5484d'}" stroke-width="${LW}" stroke-linecap="round" stroke-linejoin="round" opacity=".95"/>` +
    (live && opts.live ? `<path d="${d}" fill="none" stroke="#eafff3" stroke-width="${LW * .45}" class="flow" opacity=".9"/>` : '');
  let s = '';
  ['A', 'B'].forEach(h => {
    const bus = busId(h); if (!bus || !NODE[bus]) return;
    const cs = cols.filter(c => c.half === h); if (!cs.length) return;
    let x0 = Math.min(...cs.map(c => c.x)) + 30, x1 = Math.max(...cs.map(c => c.x + c.w)) - 30;
    if (cpl) { if (h === 'A') x1 = Math.max(Math.min(x1, cplX - 60), cplX - 60); else x0 = Math.min(Math.max(x0, cplX + 60), cplX + 60); }
    const lv = isLive(bus);
    s += seg(`M${x0} ${BY}H${x1}`, lv);
    s += `<text x="${(h === 'A' ? x0 + 10 : x1 - 10)}" y="${BY - 18}" font-size="22" font-weight="800" text-anchor="${h === 'A' ? 'start' : 'end'}" fill="${lv ? '#0a8a50' : '#c4282e'}">${esc(NODE[bus].label.split(' — ')[0])} ${lv ? '— sous tension (simulé)' : '— hors tension (simulé)'}</text>`;
    cs.forEach(c => {
      const us = c.c.units.filter(u => (u.dep || u.node) && unitHalf(u) === h && NODE[u.dep || u.node].role !== 'arrivee');
      if (!us.length) return;
      const lx = c.hasC ? (h === 'A' ? cplX - 90 : cplX + 90) : c.x + 30, ys = us.map(u => (u.y + Math.min(u.h, 6) / 2) * U);
      s += seg(`M${lx} ${BY}V${Math.max(...ys)}`, lv);
      us.forEach((u, i) => { const id = u.dep || u.node, ul = lv && col(id), y = ys[i];
        s += seg(`M${lx} ${y}H${lx + 34}`, ul) + `<path d="M${lx + 34} ${y - 14}l22 14-22 14z" fill="${ul ? '#12b76a' : '#e5484d'}"/>`; });
    });
    cols.forEach(c => c.c.units.forEach(u => { const id = u.node; if (!id || !NODE[id] || NODE[id].role !== 'arrivee' || unitHalf(u) !== h) return;
      const ax = c.x + c.w / 2, ay = (u.y + 1) * U, ul = col(id), tr = NODE[(UP[id] || [])[0].a];
      s += seg(`M${ax} ${BY}V${ay}`, lv && ul) + `<g transform="translate(${ax + 30},${BY + 20})" fill="none" stroke="${isLive(tr.id) ? '#12b76a' : '#e5484d'}" stroke-width="6"><circle cx="20" cy="20" r="18"/><circle cx="48" cy="20" r="18"/></g>
        <text x="${ax + 120}" y="${BY + 50}" font-size="24" font-weight="800" fill="#1a1a1a">${esc(short(tr))}</text>`; }));
  });
  if (cplU) {
    const id = cplU.node || cplU.dep, cy = (cplU.y + 1) * U, ul = col(id), la = isLive(busId('A')), lb = isLive(busId('B'));
    s += seg(`M${cplX - 60} ${BY}H${cplX - 30}V${cy}`, la) + seg(`M${cplX + 30} ${cy}V${BY}H${cplX + 60}`, lb) +
      `<rect x="${cplX - 130}" y="${cy - 78}" width="260" height="34" rx="17" fill="${ul ? '#12b76a' : '#e5484d'}"/><text x="${cplX}" y="${cy - 54}" font-size="21" text-anchor="middle" font-weight="800" fill="#fff">COUPLAGE ${ul ? 'FERMÉ' : 'OUVERT'}</text>`;
  }
  return `<g>${s}</g>`;
}
function tagText(n) {
  if (!n) return '';
  const m = (n.model || '').replace(/Micrologic/i, 'µ').replace(/\s*\(probable[^)]*\)/, '').replace(/^Derrière porte$/, 'derrière porte');
  return [n.case ? 'Case ' + n.case : '', m, n.ir || '', n.meter ? 'PM n°' + n.meter : ''].filter(Boolean).join(' · ');
}
function sm6SVG(f, opts) {
  const CW = { DM1: 750, IM: 375, CM: 375, QM: 375, PF: 375, CPL: 750, CPL2: 375 };
  const H = 2050; let x = 0, body = '';
  f.cells.forEach(c => {
    const w = CW[c.t] || 375, n = c.node ? NODE[c.node] : null;
    const lv = n && opts.live ? (SW.has(n.t) && !isClosed(n.id) ? 'off' : isLive(n.id) ? 'on' : 'off') : null;
    const col = lv === 'on' ? '#16b36b' : lv === 'off' ? '#ff5a5f' : '#f2f2f2';
    let s = `<rect x="${x}" y="0" width="${w}" height="${H}" fill="#f1f1ef" stroke="#9a9a96" stroke-width="3"/>`;
    s += `<rect x="${x + 6}" y="6" width="${w - 12}" height="440" fill="#f6f6f4" stroke="#c9c9c4" stroke-width="2"/>`;
    if (c.t === 'DM1') s += `<rect x="${x + w / 2 - 110}" y="70" width="220" height="190" rx="8" fill="#2d3033"/><rect x="${x + w / 2 - 80}" y="95" width="160" height="80" fill="#8fb5a0"/><circle cx="${x + w / 2 - 60}" cy="225" r="10" fill="#16b36b"/><circle cx="${x + w / 2 - 25}" cy="225" r="10" fill="#e5333a"/>`;
    s += plateSVG(x + 20, 455, w - 40, 70, c.label, 'red', w > 500 ? 26 : 20);
    s += `<rect x="${x}" y="545" width="${w}" height="500" fill="#151515"/>`;
    const mx = x + w / 2;
    if (c.t === 'DM1' || c.t === 'QM' || c.t === 'IM') {
      s += `<path d="M${mx} 575V680" stroke="${col}" stroke-width="10"/>`;
      if (c.t === 'DM1') s += `<rect x="${mx - 40}" y="700" width="80" height="80" fill="${lv === 'off' ? 'none' : col}" stroke="${col}" stroke-width="10"/>${lv === 'off' ? `<path d="M${mx - 40} 780l80-80" stroke="${col}" stroke-width="8"/>` : ''}`;
      else s += `<path d="M${mx} 700l${lv === 'off' ? 60 : 0} ${lv === 'off' ? -50 : 0}" stroke="${col}" stroke-width="10"/><circle cx="${mx}" cy="690" r="12" fill="${col}"/><path d="M${mx} ${lv === 'off' ? 700 : 700}L${mx + (lv === 'off' ? 55 : 0)} 790" stroke="${col}" stroke-width="10"/>`;
      s += `<path d="M${mx} 790V1010" stroke="${col}" stroke-width="10"/>`;
      if (c.t === 'QM') s += `<rect x="${mx - 22}" y="840" width="44" height="110" fill="none" stroke="${col}" stroke-width="8"/>`;
      s += `<rect x="${mx + 90}" y="620" width="90" height="90" fill="#e2b714"/><circle cx="${mx + 135}" cy="665" r="18" fill="#3a3a3a"/>`;
    } else if (c.t === 'CPL' || c.t === 'CPL2') {
      s += c.t === 'CPL' ? `<path d="M${x + 60} 575V700M${x + 60} 700l60 ${lv === 'off' ? -50 : 0}M${x + 60} 700V1010H${x + w - 60}V575" stroke="${col}" stroke-width="10" fill="none"/><rect x="${x + w - 200}" y="620" width="90" height="90" fill="#e2b714"/>`
        : `<path d="M${mx} 575V1010" stroke="${col}" stroke-width="10"/>`;
    } else if (c.t === 'CM') s += `<path d="M${mx} 575V700" stroke="#f2f2f2" stroke-width="8"/><rect x="${mx - 18}" y="700" width="36" height="80" fill="none" stroke="#f2f2f2" stroke-width="6"/><circle cx="${mx - 25}" cy="860" r="45" fill="none" stroke="#f2f2f2" stroke-width="7"/><circle cx="${mx + 25}" cy="860" r="45" fill="none" stroke="#f2f2f2" stroke-width="7"/>`;
    else if (c.t === 'PF') s += `<path d="M${mx} 575V760" stroke="#f2f2f2" stroke-width="8"/><path d="M${mx - 25} 760h50l-25 50z" fill="#f2f2f2"/><path d="M${mx - 40} 900h80M${mx - 25} 920h50M${mx - 10} 940h20" stroke="#f2f2f2" stroke-width="7"/>`;
    s += `<rect x="${x + 6}" y="1055" width="${w - 12}" height="940" fill="#f4f4f2" stroke="#c9c9c4" stroke-width="2"/><rect x="${mx - 30}" y="1180" width="60" height="110" fill="#3b3f42"/><rect x="${mx - 30}" y="1350" width="60" height="110" fill="#3b3f42"/>`;
    s += `<text x="${mx}" y="1560" font-size="24" text-anchor="middle" fill="#0b8a4b" font-weight="700">SM6</text>`;
    if (n) { // repères de la cellule
      const tr = (DOWN[n.id] || []).map(e => NODE[e.b]).find(x => x.t === 'tr');
      const rel = (n.prot || '').match(/S20\d\d[^:]*|STRN[^—]*/); const ip = (n.prot || '').match(/I>\d+A/);
      const uu = n.uni || {}, tcs = (uu.tc || '').match(/^\d+(?:-\d+)?\/5/);
      const rows = [uu.sch && !/x/.test(uu.sch) ? 'Sch. ' + uu.sch : '', uu.rep ? 'Repère ' + uu.rep : (c.ref ? 'Repère ' + c.ref : ''), rel ? rel[0].trim() : (uu.relay && !/x/i.test(uu.relay) ? uu.relay : ''), ip ? ip[0] : '', tcs ? 'TC ' + tcs[0] + ' A' : '', tr ? short(tr) + (tr.kva ? ' · ' + tr.kva : '') : ''].filter(Boolean);
      const bw = w - 40;
      s += `<rect x="${x + 20}" y="1590" width="${bw}" height="${rows.length * 30 + 16}" rx="10" fill="#fff" stroke="#9aa"/>` + rows.map((r, i) => `<text class="tag" x="${mx}" y="${1620 + i * 30}" font-size="${w > 500 ? 20 : 15}" text-anchor="middle" fill="#123" font-family="Consolas,Menlo,monospace">${esc(r.length > bw / 9 ? r.slice(0, Math.floor(bw / 9)) + '…' : r)}</text>`).join('');
    } else s += `<text x="${mx}" y="1620" font-size="20" text-anchor="middle" fill="#666">${esc(c.ref || '')}</text>`;
    s += `<rect x="${x}" y="${H - 50}" width="${w}" height="50" fill="#2b2b2b"/>`;
    body += n ? `<g class="hit" data-id="${n.id}"><title>${esc(n.label)}</title>${s}<rect class="hl" x="${x + 4}" y="4" width="${w - 8}" height="${H - 8}" rx="8"/></g>` : s;
    x += w;
  });
  return `<svg viewBox="-60 -150 ${x + 120} ${H + 230}" xmlns="http://www.w3.org/2000/svg" font-family="Arial,Helvetica,sans-serif">
    <text x="0" y="-75" font-size="56" font-weight="800" fill="currentColor">${esc(f.title)}</text>
    <text x="0" y="-25" font-size="26" fill="currentColor" opacity=".6">Cellules SM6 — ordre selon l’unifilaire R112529 — reconstruction vectorielle</text>${body}</svg>`;
}

/* Cellules SM6 reconstruites sur photos (style « sm6p », données tools/hta_photo.py) :
   coffret BT + relais, bandeau (blanc / crème / liseré vert Schneider) avec plaque, indicateurs de présence tension, voyants ;
   bandeau noir de commande (synoptique coloré selon l'état simulé, cadenas jaune, serrure) ; compartiment câbles ; coffret au sol. */
function sm6pSVG(f, opts) {
  const H = 2240, BAND = { white: '#f3f3ef', cream: '#e9d79f', green: '#f3f3ef' };
  let x = 0, body = '';
  const items = (spec, x0, w, y) => {  // vN indicateurs, lN voyants, bN boutons, box coffret, arc étiquette risque d'arc
    let s = '', cx = x0 + 24;
    (spec || '').split(' ').filter(Boolean).forEach(tok => {
      const k = tok[0], n = +tok.slice(1) || 1;
      if (tok === 'box') { s += `<rect x="${x0 + w / 2 - 60}" y="${y - 40}" width="120" height="150" rx="6" fill="#222"/><rect x="${x0 + w / 2 - 44}" y="${y - 22}" width="88" height="70" rx="3" fill="#3d4246"/>`; return; }
      if (tok === 'arc') { s += `<rect x="${x0 + w / 2 - 80}" y="${y - 30}" width="160" height="120" fill="#fff" stroke="#999"/><rect x="${x0 + w / 2 - 80}" y="${y - 30}" width="160" height="34" fill="#e5333a"/><text x="${x0 + w / 2}" y="${y - 7}" font-size="17" text-anchor="middle" fill="#fff" font-weight="700">ATTENTION</text><text x="${x0 + w / 2}" y="${y + 24}" font-size="14" text-anchor="middle" fill="#333">Risque classe 4</text>`; return; }
      for (let i = 0; i < n; i++) {
        if (k === 'v') { s += `<rect x="${cx}" y="${y}" width="40" height="76" rx="4" fill="#d3e4ec" stroke="#8aa3ae"/><rect x="${cx + 8}" y="${y + 10}" width="24" height="12" fill="#5bb6d6"/>`; cx += 46; }
        if (k === 'l') { const c = ['#16b36b', '#e5333a', '#e5333a', '#16b36b'][i % 4]; s += `<circle cx="${cx + 18}" cy="${y + 38}" r="17" fill="${c}" stroke="#111" stroke-width="4"/>`; cx += 40; }
        if (k === 'b') { s += `<circle cx="${cx + 18}" cy="${y + 38}" r="16" fill="#1d1d1d"/>`; cx += 40; }
      }
      cx += 16;
    });
    return s;
  };
  const plate = (x0, w, y, text, pc, big) => {
    const lines = String(text || '').split('|'), fs = big ? 40 : (w > 300 ? 21 : 18), lh = fs * 1.2, ph = lines.length * lh + 16, pw = Math.min(w - 30, big ? w - 40 : Math.max(...lines.map(l => l.length)) * fs * .62 + 30);
    const [bg, fg] = pc === 'black' ? ['#151515', '#f2f2f2'] : pc === 'tag' ? ['#f7d117', '#222'] : ['#d62828', '#fff'];
    return `<rect x="${x0 + w / 2 - pw / 2}" y="${y}" width="${pw}" height="${ph}" rx="3" fill="${bg}"/>` + lines.map((l, i) => `<text x="${x0 + w / 2}" y="${y + 8 + lh * (i + .82)}" font-size="${fs}" text-anchor="middle" fill="${fg}" font-weight="700" font-family="Arial Narrow,Arial,sans-serif" ${pc === 'tag' ? 'font-style="italic"' : ''}>${esc(l)}</text>`).join('');
  };
  f.cells.forEach(c => {
    const w = c.w || 375, n = c.node ? NODE[c.node] : null;
    const lv = n && opts.live ? (SW.has(n.t) && !isClosed(n.id) ? 'off' : isLive(n.id) ? 'on' : 'off') : null;
    const col = lv === 'on' ? '#16b36b' : lv === 'off' ? '#ff5a5f' : '#e8e8e8';
    const halves = w >= 700 ? [[x, w / 2], [x + w / 2, w / 2]] : [[x, w]];
    let s = `<rect x="${x}" y="0" width="${w}" height="${H}" fill="none"/>`;
    // coffret BT haut
    const top = c.top === 'lv' ? 40 : c.top === 'mid' ? 330 : 400;
    s += `<rect x="${x + 4}" y="${top}" width="${w - 8}" height="${560 - top}" fill="#f2f2ee" stroke="#b8b8b2" stroke-width="3"/>`;
    if (c.top === 'lv') {
      const rx = x + w - 300 > x ? x + w / 2 - 40 : x + 40;
      s += `<rect x="${rx}" y="140" width="250" height="190" rx="8" fill="#2b2e31"/><rect x="${rx + 60}" y="165" width="120" height="80" fill="#9fb9a7"/>${[0, 1, 2, 3, 4].map(i => `<circle cx="${rx + 70 + i * 26}" cy="285" r="8" fill="#3f6fb5"/>`).join('')}<rect x="${rx + 150}" y="250" width="70" height="55" fill="#e8efe8"/>`;
      s += `<circle cx="${x + 70}" cy="200" r="20" fill="#1d1d1d"/>`;
      if (c.sel) s += `<rect x="${x + 50}" y="300" width="70" height="80" rx="5" fill="#26292c"/><rect x="${x + 80}" y="312" width="12" height="56" rx="5" fill="#ddd"/><rect x="${x + 40}" y="270" width="90" height="22" fill="#3b82f6"/>`;
    }
    // bandeau (plaque + appareils)
    halves.forEach(([hx, hw], i) => {
      const b = (c.band || ['white'])[i] || (c.band || ['white'])[0];
      s += `<rect x="${hx + 4}" y="560" width="${hw - 8}" height="320" fill="${BAND[b] || BAND.white}" stroke="#b8b8b2" stroke-width="3"/>`;
      if (b === 'green') s += `<rect x="${hx + 4}" y="560" width="${hw - 8}" height="34" fill="#1f9e4b"/>${i === 0 || halves.length === 1 ? `<text x="${hx + hw - 20}" y="586" font-size="20" text-anchor="end" fill="#fff" font-weight="700">Schneider</text>` : ''}`;
      if (c.mech !== 'panel') s += `<rect x="${hx + 30}" y="710" width="${hw - 60}" height="130" rx="6" fill="#fbfbf8" stroke="#cfcfc8"/>`;
    });
    if (c.mech === 'panel') {  // panneau / remontée de barres : grande plaque + éclair
      s += `<rect x="${x + 4}" y="560" width="${w - 8}" height="770" fill="#f3f3ef" stroke="#b8b8b2" stroke-width="3"/>` + plate(x, w, 640, c.plate, c.pc, true) +
        `<path d="M${x + w / 2 - 45} 900h90l-45 -78z" fill="#f7d117" stroke="#222" stroke-width="5"/><path d="M${x + w / 2 + 6} 840l-14 26h14l-12 26" stroke="#222" stroke-width="5" fill="none"/>`;
    } else {
      const [px, pw] = halves[0];
      s += plate(px, pw, (c.band || [])[0] === 'green' ? 606 : 590, c.plate, c.pc);
      s += items(c.L, halves[0][0] + 20, halves[0][1] - 40, 740);
      if (halves[1]) s += items(c.R, halves[1][0] + 20, halves[1][1] - 40, 740);
      if (c.keybox) s += `<rect x="${x + w * .25 - 110}" y="740" width="220" height="56" rx="6" fill="#b9bcbf" stroke="#777"/>${[0, 1, 2, 3, 4, 5].map(i => `<circle cx="${x + w * .25 - 85 + i * 34}" cy="768" r="11" fill="#555"/>`).join('')}<rect x="${x + w * .25 - 70}" y="800" width="16" height="44" rx="4" fill="#e5333a"/><rect x="${x + w * .25 - 30}" y="800" width="16" height="44" rx="4" fill="#f7d117"/><text x="${x + w * .25}" y="866" font-size="15" text-anchor="middle" fill="#333">${esc(c.keybox)}</text>`;
      // bandeau noir de commande
      s += `<rect x="${x + 2}" y="880" width="${w - 4}" height="450" fill="#1c1d1f"/>`;
      const mx = halves[0][0] + halves[0][1] * .42;
      const mimic = (mxx, kind) => {
        let m = `<rect x="${mxx - 90}" y="905" width="110" height="40" fill="#e9e9e4"/><rect x="${mxx - 90}" y="950" width="60" height="44" fill="#fff"/>`;
        m += `<path d="M${mxx} 960V1060" stroke="${col}" stroke-width="7"/>`;
        if (kind === 'dm1' || kind === 'im' || kind === 'cpl') m += lv === 'off' ? `<path d="M${mxx} 1060l46 -40" stroke="${col}" stroke-width="7"/>` : `<path d="M${mxx} 1060v60" stroke="${col}" stroke-width="7"/>`;
        m += `<path d="M${mxx} 1120V1290" stroke="${col}" stroke-width="7"/><path d="M${mxx - 34} 1040a34 34 0 0 1 34 -26M${mxx - 50} 1050h28M${mxx - 46} 1062h20" stroke="${col}" stroke-width="5" fill="none"/>`;
        if (kind === 'pfm') m += `<path d="M${mxx - 22} 1200h44l-22 34z" fill="none" stroke="${col}" stroke-width="5"/>`;
        m += `<rect x="${mxx + 40}" y="1110" width="74" height="170" rx="5" fill="#b9bcbf"/><rect x="${mxx + 58}" y="1150" width="20" height="64" rx="5" fill="#2a2a2a"/>`;
        return m;
      };
      if (c.mech === 'dm1' || c.mech === 'im' || c.mech === 'pfm' || c.mech === 'cpl') s += mimic(mx, c.mech);
      if (c.mech === 'cpl') s += `<path d="M${x + 20} 1290H${x + w - 20}" stroke="${col}" stroke-width="5" opacity=".7"/>`;
      if (c.mech === 'blank') s += `<path d="M${x + w / 2} 960V1290" stroke="#e8e8e8" stroke-width="5"/>`;
      if (c.lock) s += `<rect x="${halves[0][0] + halves[0][1] - 120}" y="905" width="92" height="92" rx="8" fill="rgba(232,210,26,.85)" stroke="#a89200" stroke-width="3"/><rect x="${halves[0][0] + halves[0][1] - 92}" y="925" width="36" height="52" rx="6" fill="#2a2a2a"/>`;
      if (c.key) s += `<rect x="${halves[0][0] + halves[0][1] - 128}" y="1008" width="100" height="30" fill="#3b82f6"/><text x="${halves[0][0] + halves[0][1] - 78}" y="1030" font-size="18" text-anchor="middle" fill="#fff" font-weight="700">${esc(c.key)}</text>`;
      if (halves[1] && c.mech === 'dm1') { const hx = halves[1][0], hw = halves[1][1];  // partie disjoncteur SF1
        s += `<path d="M${hx + 20} 1000H${hx + hw - 20}" stroke="#e8e8e8" stroke-width="5"/><rect x="${hx + hw / 2 - 40}" y="1180" width="80" height="30" rx="4" fill="#2c2c2c" stroke="#555"/>${[0, 1, 2].map(i => `<circle cx="${hx + hw / 2 - 20 + i * 20}" cy="1195" r="6" fill="${lv === 'on' ? '#16b36b' : '#e5333a'}"/>`).join('')}<path d="M${hx + hw / 2} 1210V1290" stroke="#e8e8e8" stroke-width="5"/>`; }
    }
    // compartiment câbles, marque, coffret au sol
    s += `<rect x="${x + 4}" y="1330" width="${w - 8}" height="870" fill="#f2f2ee" stroke="#b8b8b2" stroke-width="3"/>`;
    const lx = halves[0][0] + halves[0][1] / 2;
    s += `<rect x="${lx + 40}" y="1500" width="44" height="120" rx="3" fill="#3b3f42"/><rect x="${lx + 40}" y="1700" width="44" height="120" rx="3" fill="#3b3f42"/>`;
    s += c.brand === 'SE' ? `<text x="${lx - 30}" y="1470" font-size="26" text-anchor="middle" fill="#1f9e4b" font-weight="800">Schneider</text><text x="${lx - 30}" y="1498" font-size="18" text-anchor="middle" fill="#1f9e4b">SM6</text>`
      : `<rect x="${lx - 110}" y="1440" width="150" height="50" fill="#fff" stroke="#999"/><text x="${lx - 35}" y="1462" font-size="15" text-anchor="middle" fill="#333" font-weight="700">MERLIN GERIN</text><rect x="${lx - 110}" y="1470" width="150" height="20" fill="#f08a1c"/><text x="${lx - 35}" y="1486" font-size="15" text-anchor="middle" fill="#fff" font-weight="700">SM6</text>`;
    if (c.floor && halves[1]) { const hx = halves[1][0] + halves[1][1] / 2;
      s += `<rect x="${hx - 110}" y="1640" width="220" height="560" rx="6" fill="#fafaf8" stroke="#9a9a96" stroke-width="3"/><rect x="${hx - 45}" y="1800" width="90" height="250" rx="6" fill="#26292c"/><rect x="${hx - 10}" y="1760" width="20" height="120" rx="6" fill="#1d1d1d"/><circle cx="${hx}" cy="1960" r="12" fill="#e5333a"/>`; }
    s += `<rect x="${x}" y="2200" width="${w}" height="40" fill="#2b2b2b"/>`;
    if (c.est) s += `<rect x="${x + 10}" y="560" width="${w - 20}" height="320" fill="none" stroke="#3b82f6" stroke-width="6" stroke-dasharray="16 10"><title>Plaque illisible : position estimée d’après l’unifilaire</title></rect>`;
    if (c.conf === 'a_verifier') s += `<rect x="${x + 14}" y="570" width="120" height="30" rx="15" fill="#f5a524"/><text x="${x + 74}" y="591" font-size="16" text-anchor="middle" fill="#fff" font-weight="700">à vérifier</text>`;
    if (n) { // repères relevés sur l'unifilaire (sous la cellule)
      const u = n.uni || {}, tr = (DOWN[n.id] || []).map(e => NODE[e.b]).find(z => z.t === 'tr');
      const rows = [u.rep ? 'Repère ' + u.rep : '', u.relay && !/x/i.test(u.relay) ? u.relay : '', tr ? short(tr) + (tr.kva ? ' · ' + tr.kva : '') : ''].filter(Boolean);
      rows.forEach((r, i) => { s += `<text class="tag" x="${x + w / 2}" y="${2290 + i * 30}" font-size="${w > 500 ? 22 : 17}" text-anchor="middle" fill="currentColor" font-family="Consolas,Menlo,monospace">${esc(r.length > w / 10 ? r.slice(0, Math.floor(w / 10)) + '…' : r)}</text>`; });
      body += `<g class="hit" data-id="${n.id}"><title>${esc(n.label)}${c.note ? ' — ' + esc(c.note) : ''}</title>${s}<rect class="hl" x="${x + 4}" y="4" width="${w - 8}" height="${H - 8}" rx="8"/></g>`;
    } else body += `<g><title>${esc((c.plate || '').replace(/\|/g, ' '))}</title>${s}</g>`;
    x += w;
  });
  return `<svg viewBox="-60 -160 ${x + 120} ${H + 300}" xmlns="http://www.w3.org/2000/svg" font-family="Arial,Helvetica,sans-serif">
    <text x="0" y="-85" font-size="56" font-weight="800" fill="currentColor">${esc(f.title)}</text>
    <text x="0" y="-35" font-size="26" fill="currentColor" opacity=".6">Cellules SM6 reconstruites sur photos — touchez une cellule</text>${body}</svg>`;
}

/* ======================================================================= schéma HTA interactif */
const HTA_ROWS = [
  { b: 'PL20', title: 'POSTE DE LIVRAISON 20 kV', L: null, R: null },
  { b: 'SS1_20', title: 'SOUS-STATION 1 — 20 kV', L: 'SS1_BL', R: 'SS1_BR' },
  { b: 'SS2_20', title: 'SOUS-STATION 2 — 20 kV', L: 'SS2_BL', R: 'SS2_BR' },
  { b: 'KV6', title: 'SOUS-STATION 2 — 6 kV (FOUR N°2)', L: 'KV6_BL', R: 'KV6_BR' },
];
const lc = id => SW.has(NODE[id].t) && !isClosed(id) ? '#e5484d' : (isLive(id) ? '#12b76a' : '#e5484d');
function htaSVG() {
  const CW = 96; let y = 40, out = '', maxW = 0;
  HTA_ROWS.forEach(row => {
    const cells = D.facades[row.b].cells.filter(c => c.t !== 'CPL2');
    const W = cells.length * CW; maxW = Math.max(maxW, W);
    out += `<text x="0" y="${y}" font-size="17" font-weight="800" fill="currentColor" letter-spacing=".5">${row.title}</text>`;
    const by = y + 70;
    if (row.L) {
      const ci = cells.findIndex(c => c.t === 'CPL');
      // demi-jeux de barres réellement à gauche / à droite du couplage dans l'ordre de la façade (photos)
      const sideBus = list => { for (const c of list) { const n = c.node && NODE[c.node]; if (!n || n.t === 'cpl') continue;
        const b = (UP[n.id] || []).map(e => e.a).concat((DOWN[n.id] || []).map(e => e.b)).find(z => NODE[z] && NODE[z].t === 'bus' && NODE[z].board === row.b); if (b) return b; } return null; };
      const BL = sideBus(cells.slice(0, ci)) || row.L, BR = sideBus(cells.slice(ci + 1)) || row.R;
      out += `<path d="M10 ${by}H${ci * CW + 18}" stroke="${lc(BL)}" stroke-width="7" class="hit" data-id="${BL}"/><path d="M${ci * CW + 78} ${by}H${W - 10}" stroke="${lc(BR)}" stroke-width="7" class="hit" data-id="${BR}"/>`;
      out += `<g class="hit" data-id="${BL}"><rect x="10" y="${by - 12}" width="${ci * CW + 8}" height="24" fill="transparent"/></g><g class="hit" data-id="${BR}"><rect x="${ci * CW + 78}" y="${by - 12}" width="${W - ci * CW - 88}" height="24" fill="transparent"/></g>`;
    }
    cells.forEach((c, i) => {
      const cx = i * CW + CW / 2, n = c.node ? NODE[c.node] : null;
      if (c.t === 'CPL') {
        const op = !isClosed(n.id);
        out += `<g class="hit" data-id="${n.id}"><title>${esc(n.label)}</title><path d="M${cx - 30} ${by}h16" stroke="${lc(n.id)}" stroke-width="6"/><path d="M${cx - 14} ${by}l${op ? 26 : 28} ${op ? -20 : 0}" stroke="${lc(n.id)}" stroke-width="6"/><path d="M${cx + 14} ${by}h16" stroke="${lc(n.id)}" stroke-width="6"/>
          <text x="${cx}" y="${by + 32}" font-size="11" text-anchor="middle" fill="currentColor">${esc(c.label)}</text><rect class="hl" x="${cx - 40}" y="${by - 30}" width="80" height="70" rx="8"/><rect x="${cx - 40}" y="${by - 30}" width="80" height="70" fill="transparent"/></g>`;
        return;
      }
      if (!n) { // TT / parafoudres / interrupteurs non modélisés
        out += `<path d="M${cx} ${by}V${by + 40}" stroke="#9aa5a0" stroke-width="3"/><text x="${cx}" y="${by + 56}" font-size="10" text-anchor="middle" fill="currentColor" opacity=".6">${esc(c.label)}</text>`;
        return;
      }
      if (row.b === 'PL20') {
        const src = n.id === 'PL_A04' ? 'SRC_EDF' : 'SRC_CNR';
        out += `<g class="hit" data-id="${src}"><circle cx="${cx}" cy="${y + 40}" r="20" fill="none" stroke="${lc(src)}" stroke-width="5"/><text x="${cx}" y="${y + 46}" font-size="12" text-anchor="middle" font-weight="800" fill="currentColor">${src === 'SRC_EDF' ? 'EDF' : 'CNR'}</text><rect class="hl" x="${cx - 26}" y="${y + 14}" width="52" height="52" rx="26"/></g>`;
        out += `<path d="M${cx} ${y + 60}V${by + 4}" stroke="${lc(src)}" stroke-width="5"/>`;
        out += swSym(n.id, cx, by + 30, 'cb');
        out += `<path d="M${cx} ${by + 56}V${by + 90}" stroke="${lc(n.id)}" stroke-width="5"/><text x="${cx}" y="${by + 108}" font-size="11" text-anchor="middle" fill="currentColor">${src === 'SRC_EDF' ? 'SECOURS EDF → A1 · A3' : 'NORMAL CNR → A2 · A4'}</text>`;
        return;
      }
      const isArr = n.t === 'sw' || (n.id.startsWith('KV6_A'));
      if (isArr) {
        const upN = NODE[(UP[n.id] || [])[0].a];
        out += `<path d="M${cx} ${by}V${by - 22}" stroke="${lc(n.id)}" stroke-width="5"/>` + swSym(n.id, cx, by - 40, n.t === 'sw' ? 'sw' : 'cb') +
          `<path d="M${cx} ${by - 58}V${by - 75}" stroke="${lc(upN.id)}" stroke-width="5" stroke-dasharray="6 5"/><text x="${cx}" y="${by - 80}" font-size="10.5" text-anchor="middle" fill="currentColor" font-weight="700">← ${esc(short(upN).replace('Disjoncteur arrivée ', '').replace(/ \(cellule.*$/, ''))}</text>`;
        return;
      }
      out += `<path d="M${cx} ${by}V${by + 22}" stroke="${lc(n.id)}" stroke-width="5"/>` + swSym(n.id, cx, by + 40, n.t === 'dep' ? 'fuse' : 'cb');
      const tr = (DOWN[n.id] || []).map(e => NODE[e.b]).find(x => x.t === 'tr' || x.t === 'load');
      if (tr) {
        out += `<path d="M${cx} ${by + 58}V${by + 86}" stroke="${lc(tr.id)}" stroke-width="5"/>`;
        if (tr.t === 'tr') out += `<g class="hit" data-id="${tr.id}"><title>${esc(tr.label)}</title><circle cx="${cx}" cy="${by + 100}" r="15" fill="none" stroke="${lc(tr.id)}" stroke-width="4"/><circle cx="${cx}" cy="${by + 120}" r="15" fill="none" stroke="${lc(tr.id)}" stroke-width="4"/><rect class="hl" x="${cx - 22}" y="${by + 80}" width="44" height="60" rx="8"/></g>`;
        out += `<text x="${cx}" y="${by + (tr.t === 'tr' ? 156 : 100)}" font-size="12" text-anchor="middle" font-weight="800" fill="currentColor">${esc(short(tr).replace('Armoire SPANG ', 'SPANG ').slice(0, 16))}</text>`;
        if (tr.kva) out += `<text x="${cx}" y="${by + 170}" font-size="10" text-anchor="middle" fill="currentColor" opacity=".65">${esc(tr.kva)}</text>`;
        const dn = (DOWN[tr.id] || []).map(e => NODE[e.b])[0];
        if (dn) { const tgt = dn.board && BOARD[dn.board] ? BOARD[dn.board] : null; const lab = tgt ? (dn.half ? `${tgt.name.replace('TGBT ', 'TGBT ')}${dn.half}` : tgt.name) : short(dn);
          out += `<g class="hit" data-id="${dn.id}"><text x="${cx}" y="${by + 188}" font-size="10.5" text-anchor="middle" fill="${lc(dn.id)}" font-weight="700">→ ${esc(lab.slice(0, 16))}</text><rect x="${cx - 45}" y="${by + 176}" width="90" height="18" fill="transparent"/></g>`; }
      } else out += `<text x="${cx}" y="${by + 80}" font-size="10" text-anchor="middle" fill="currentColor">${esc(c.label)}</text>`;
    });
    y = by + (row.b === 'PL20' ? 150 : 230);
  });
  return `<svg viewBox="-20 0 ${maxW + 40} ${y}" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system,Segoe UI,Arial,sans-serif">${out}</svg>`;
}
function swSym(id, cx, cy, kind) {
  const n = NODE[id], c = lc(id), open = !isClosed(id);
  let g = '';
  if (kind === 'cb') g = `<rect x="${cx - 13}" y="${cy - 13}" width="26" height="26" rx="3" fill="${open ? 'none' : c}" stroke="${c}" stroke-width="4"/>${open ? `<path d="M${cx - 13} ${cy + 13}l26-26" stroke="${c}" stroke-width="3"/>` : ''}<path d="M${cx} ${cy - 13}v-5M${cx} ${cy + 13}v5" stroke="${c}" stroke-width="5"/>`;
  else if (kind === 'sw') g = `<path d="M${cx} ${cy - 18}v6M${cx} ${cy + 18}v-6" stroke="${c}" stroke-width="5"/><path d="M${cx} ${cy + 12}L${cx + (open ? 16 : 0)} ${cy - 12}" stroke="${c}" stroke-width="5"/><circle cx="${cx}" cy="${cy - 12}" r="4" fill="${c}"/>`;
  else g = `<rect x="${cx - 8}" y="${cy - 16}" width="16" height="32" fill="${open ? 'none' : c}" stroke="${c}" stroke-width="4"/>`;
  return `<g class="hit" data-id="${id}"><title>${esc(n.label)} — ${open ? 'ouvert' : 'fermé'} (simulation)</title>${g}<rect class="hl" x="${cx - 24}" y="${cy - 24}" width="48" height="48" rx="8"/><rect x="${cx - 24}" y="${cy - 24}" width="48" height="48" fill="transparent"/></g>`;
}
function tgbtMini(bid) {
  const b = BOARD[bid], qa = bid + '_QA', qb = bid + '_QB', qc = bid + '_QC', A = bid + 'A', B = bid + 'B';
  const tra = (UP[qa] || [])[0].a, trb = (UP[qb] || [])[0].a;
  const cnt = h => { const ds = (DOWN[h] || []).map(e => NODE[e.b]).filter(x => x.t === 'dep'); return [ds.filter(x => isLive(x.id) && isClosed(x.id)).length, ds.length]; };
  const [la, ta] = cnt(A), [lb, tb] = cnt(B), il = interlock(bid);
  return `<svg viewBox="0 0 420 150" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system,Segoe UI,Arial,sans-serif" style="width:100%;height:auto">
    <g class="hit" data-id="${tra}"><circle cx="60" cy="22" r="11" fill="none" stroke="${lc(tra)}" stroke-width="3"/><circle cx="60" cy="36" r="11" fill="none" stroke="${lc(tra)}" stroke-width="3"/><text x="80" y="34" font-size="12" font-weight="700" fill="currentColor">${esc(short(NODE[tra]))}</text></g>
    <g class="hit" data-id="${trb}"><circle cx="360" cy="22" r="11" fill="none" stroke="${lc(trb)}" stroke-width="3"/><circle cx="360" cy="36" r="11" fill="none" stroke="${lc(trb)}" stroke-width="3"/><text x="340" y="34" font-size="12" font-weight="700" text-anchor="end" fill="currentColor">${esc(short(NODE[trb]))}</text></g>
    <path d="M60 47V60" stroke="${lc(tra)}" stroke-width="4"/><path d="M360 47V60" stroke="${lc(trb)}" stroke-width="4"/>
    ${swSym(qa, 60, 74, 'cb')}${swSym(qb, 360, 74, 'cb')}
    <path d="M60 92V104" stroke="${lc(qa)}" stroke-width="4"/><path d="M360 92V104" stroke="${lc(qb)}" stroke-width="4"/>
    <g class="hit" data-id="${A}"><path d="M20 106H180" stroke="${lc(A)}" stroke-width="7"/><rect x="20" y="96" width="160" height="22" fill="transparent"/></g>
    <g class="hit" data-id="${B}"><path d="M240 106H400" stroke="${lc(B)}" stroke-width="7"/><rect x="240" y="96" width="160" height="22" fill="transparent"/></g>
    ${NODE[qc] ? swSymH(qc, 210, 106) : ''}
    <text x="100" y="134" font-size="12" text-anchor="middle" fill="currentColor"><tspan font-weight="800">${esc(NODE[A].label.split(' — ')[0])}</tspan> · ${la}/${ta} alim.</text>
    <text x="320" y="134" font-size="12" text-anchor="middle" fill="currentColor"><tspan font-weight="800">${esc(NODE[B].label.split(' — ')[0])}</tspan> · ${lb}/${tb} alim.</text>
    ${il ? `<text x="210" y="148" font-size="10.5" text-anchor="middle" fill="#e5484d" font-weight="700">⚠ ${il.lvl === 'danger' ? 'configuration non autorisée / non validée' : 'couplage non documenté'}</text>` : ''}</svg>`;
}
function swSymH(id, cx, cy) {
  const c = lc(id), open = !isClosed(id), n = NODE[id];
  return `<g class="hit" data-id="${id}"><title>${esc(n.label)} — ${open ? 'ouvert' : 'fermé'}</title><path d="M180 ${cy}H${cx - 12}M${cx + 12} ${cy}H240" stroke="${c}" stroke-width="5"/><rect x="${cx - 12}" y="${cy - 12}" width="24" height="24" rx="3" fill="${open ? 'none' : c}" stroke="${c}" stroke-width="4" ${n.conf !== 'confirme' ? 'stroke-dasharray="4 3"' : ''}/><text x="${cx}" y="${cy - 18}" font-size="10" text-anchor="middle" fill="currentColor">QC</text><rect class="hl" x="${cx - 22}" y="${cy - 30}" width="44" height="52" rx="8"/><rect x="${cx - 22}" y="${cy - 30}" width="44" height="52" fill="transparent"/></g>`;
}

/* ======================================================================= vues */
const VIEW = () => $('#view');
let CUR = { route: '', args: [] };
let LAST_ROUTED_HASH = null;
function setTab(k) { $$('#tabs a').forEach(a => a.classList.toggle('on', a.dataset.tab === k)); }
function rerender() { route(true); }
function route(keep) {
  LAST_ROUTED_HASH = location.hash;
  const h = location.hash.replace(/^#\/?/, ''); const [r, ...args] = h.split('/').map(decodeURIComponent);
  CUR = { route: r, args };
  const fn = { '': vHome, site: vSite, plans: vPlans, reseau: vNet, tableaux: vBoards, b: vBoard, courant: vCourant, fiche: vCourant, fiches: vCourant, details: vFiche, depannage: vDiag, entretien: vMaint, registre: vReg }[r] || vHome;
  setTab({ '': 'home', site: 'home', plans: 'plan', reseau: 'net', tableaux: 'boards', b: 'boards', courant: 'diag', fiche: 'diag', fiches: 'diag', details: 'diag', depannage: 'diag', entretien: 'maint', registre: 'reg' }[r] || 'home');
  const y = keep ? scrollY : 0; fn(...args);
  const sn = simNotice(); if (sn && !$('.simnote', VIEW())) { VIEW().insertAdjacentHTML('afterbegin', sn); $('#simreset').onclick = () => { resetSim(); rerender(); toast('Configuration normale rétablie'); }; }
  if (keep) scrollTo(0, y); else scrollTo(0, 0);
}
const simBanner = () => `<div class="banner sim">⚠️<div><b>Simulation documentaire.</b> Les états ouverts / fermés sont des hypothèses de travail, pas l’état réel de l’installation. <b>Aucune manœuvre ne doit en être déduite.</b> Toute manœuvre suit une procédure validée par les responsables électriques habilités.</div></div>` +
  (atsActive() ? `<div class="banner info" style="margin-top:8px">🔁<div><b>Permutation automatique active :</b> source CNR absente → la bobine à manque de tension a ouvert l’arrivée CNR (B01) et le <b>secours EDF (A04) a pris le relais</b> (simulation).</div></div>` : '');

/*PLANS*/
/* ---------- Réseau */
let SIMMODE = false, NETVIEW = 'full';
function netFocus(id) {
  // remonte jusqu'au premier élément dessiné sur le schéma complet (TGBT, transfo, cellule, ou tableau alimenté)
  let cur = id;
  for (let i = 0; i < 40 && cur; i++) {
    const n = NODE[cur];
    if (!n) return BOARD[cur] ? cur : null;
    if (['tr', 'src'].includes(n.t) || n.role === 'arrivee' || n.role === 'couplage' || (n.t === 'bus' && n.board && (BOARD[n.board].kind === 'TGBT' || BOARD[n.board].kind === 'HTA'))) return cur;
    if (n.board && BOARD[n.board] && BOARD[n.board].kind !== 'TGBT' && BOARD[n.board].kind !== 'HTA' && (UP[(BOARD[n.board].halves[0] || {}).id] || []).length) {
      const feeder = D.nodes.find(d => d.t === 'dep' && d.feeds === n.board); if (feeder) return n.board;
    }
    const u = (UP[cur] || [])[0]; cur = u ? u.a : null;
  }
  return null;
}

/* Recherche contextuelle sur l'unifilaire : reutilise l'index global sans modifier les donnees. */
const NET_FINDER = { query: '', selected: null };
function netFinderPanel() {
  return '<section class="card glass" style="padding:12px 14px;margin:12px 0" aria-label="Recherche sur le schema">' +
    '<label for="net-find" style="font-weight:700;display:block;margin-bottom:7px">Rechercher et localiser sur le schema</label>' +
    '<input id="net-find" class="f" type="search" autocomplete="off" style="width:100%;max-width:650px" ' +
    'placeholder="TR 1A, cellule, repere, TGBT, TS7..." aria-label="Rechercher un equipement sur le schema">' +
    '<div id="net-hits" class="list" style="margin-top:6px" role="listbox"></div>' +
    '<div id="net-doc" style="margin-top:8px" role="status" aria-live="polite"></div>' +
    '</section>';
}
function bindNetFinder(viewer) {
  const field = $('#net-find'), results = $('#net-hits'), detail = $('#net-doc');
  if (!field || !viewer) return;
  field.value = NET_FINDER.query;

  function infoFor(id) {
    const n = NODE[id], b = BOARD[id] || (n && boardOf(n));
    const locId = (b && b.loc) || (n && n.loc);
    const loc = locChain(locId).map(x => x.name).join(' / ') || 'Localisation non documentee';
    const conf = (b && b.loc_conf) || (n && n.conf) || 'inconnu';
    const keys = n && n.keys ? [String(n.keys)] :
      b ? D.nodes.filter(x => x.board === b.id && x.keys).slice(0, 8).map(x => short(x) + ' : ' + x.keys) : [];
    const title = b && !n ? b.name : n ? n.label : id;
    const related = D.issues.filter(i => issueActive(i) && (i.ents || []).some(e => e === id || (b && e === b.id))).slice(0, 4);
    const warning = related.length ? '<div class="banner danger" style="margin-top:8px">⚠️<div><b>Ecarts documentaires lies au repere :</b><br>' + related.map(i => '<a href="#" data-open="issue:' + esc(i.id) + '">' + esc(i.title) + '</a>').join('<br>') + '</div></div>' : '';
    const keyTxt = keys.length ? keys.map(x => '<div class="small">' + esc(x) + '</div>').join('') :
      '<span class="muted">Aucune cle associee a cette selection dans les donnees.</span>';
    detail.innerHTML = '<div class="card glass" style="padding:10px 12px">' +
      '<b>' + esc(title) + '</b> ' + confPill(n ? n.conf : conf) +
      '<div class="small" style="margin-top:7px"><b>Localisation documentaire :</b> ' + esc(loc) +
      (b && b.loc_conf && b.loc_conf !== 'confirme' ? ' (a confirmer)' : '') + '</div>' +
      '<div class="small" style="margin-top:5px"><b>Cles / reperes documentes :</b></div>' + keyTxt +
      warning + parcoursSummary(id) +
      '<div class="row" style="margin-top:8px"><button class="btn" type="button" data-open="' + esc(id) + '">Ouvrir la fiche</button>' +
      '<button class="btn ghost" type="button" data-go="#/plans">Ouvrir les plans de localisation</button></div>' +
      '<p class="small muted" style="margin:7px 0 0">Les cles et localisations proviennent des documents et ne constituent ni un relevé terrain ni une autorisation de manoeuvre.</p></div>';
  }
  function selectId(id) {
    NET_FINDER.selected = id;
    if (NETVIEW !== 'full' && NODE[id] && NODE[id].t === 'dep') { NETVIEW = 'full'; rerender(); return; }
    const target = NETVIEW === 'full' ? (BOARD[id] ? id : netFocus(id)) :
      (NODE[id] ? focusTarget(id) : null);
    if (!target || !viewer.focusOn(target)) {
      if (NETVIEW !== 'full') { NETVIEW = 'full'; rerender(); return; }
      toast('Selection documentee : cet equipement n est pas dessine directement sur le schema.');
    }
    infoFor(id);
    parcoursHighlight(id);
  }
  function renderHits() {
    NET_FINDER.query = field.value;
    const q = NET_FINDER.query.trim();
    if (!q) { results.innerHTML = ''; return; }
    const found = search(q, 70).filter(x => x.kind === 'node' || x.kind === 'board').slice(0, 12);
    results.innerHTML = found.length ? found.map(x =>
      '<button type="button" class="li" style="width:100%;text-align:left;cursor:pointer" data-net-id="' + esc(x.id) + '">' +
      '<span class="pill">' + esc(x.kind === 'board' ? 'Tableau' : (TYPE[x.t] || x.t)) + '</span>' +
      '<span class="grow"><b>' + esc(x.label) + '</b><span class="src" style="display:block">' + esc(recContext(x)) + '</span></span><span>⌖</span></button>').join('') :
      '<p class="small muted">Aucun element trouve dans le modele documente.</p>';
  }
  results.onclick = e => {
    const item = e.target.closest('[data-net-id]');
    if (item) selectId(item.dataset.netId);
  };
  field.addEventListener('input', renderHits);
  field.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const first = results.querySelector('[data-net-id]');
      if (first) { e.preventDefault(); selectId(first.dataset.netId); }
    }
  });
  renderHits();
  if (NET_FINDER.selected) infoFor(NET_FINDER.selected);
}

function vNet(focus) {
  if (focus && NODE[focus] && NODE[focus].t === 'dep') NETVIEW = 'full';
  VIEW().innerHTML = `<h1>Réseau HTA / BT</h1><p class="sub">Topologie selon l’unifilaire 20 kV (R112529 rév. H) et le classeur de distribution. Touchez un élément pour sa fiche.</p>
  ${simBanner()}
  <div class="row" style="margin:12px 0"><div class="seg glass"><button id="m0" class="${SIMMODE ? '' : 'on'}">Consultation</button><button id="m1" class="${SIMMODE ? 'on' : ''}">Mode simulation</button></div>
    <button class="btn ghost" id="rst">Réinitialiser l’hypothèse</button><button class="btn ghost" id="cnr">${rawClosed('SRC_CNR') ? 'Simuler une perte CNR' : 'Rétablir la CNR'}</button><span class="small muted">${Object.keys(SIM).length} modification(s) par rapport à l’hypothèse initiale</span></div>
  <div class="seg glass" style="margin-bottom:10px"><button id="v1" class="${NETVIEW === 'full' ? 'on' : ''}">Schéma complet : 20 kV → transfos → TGBT → tableaux</button><button id="v2" class="${NETVIEW === 'uni' ? 'on' : ''}">Ordre physique des cellules HTA (unifilaire)</button></div>
  <p class="small muted" style="margin:0 0 8px">${NETVIEW === 'full' ? 'Schéma de principe : le demi-jeu de barres 20 kV gauche (cellules TR xA) est dessiné au-dessus du droit (cellules TR xB) ; au croisement d’un trait vertical et du jeu de barres droit, il n’y a pas de liaison. En mode simulation, touchez un disjoncteur, une arrivée ou un couplage.' : 'Cellules dans l’ordre de l’unifilaire R112529 rév. H.'}</p>
  ${netFinderPanel()}
  <div id="hta"></div>
  <h2>Tableaux secondaires</h2><div class="grid">${D.boards.filter(b => b.kind !== 'TGBT' && b.kind !== 'HTA').map(b => { const hs = b.halves.filter(h => NODE[h.id]); return `<div class="li glass" style="border-radius:16px" data-go="#/b/${b.id}">${hs.map(h => `<span class="dot ${isLive(h.id) ? 'on' : 'off'}"></span>`).join('')}<div class="grow"><b>${esc(b.name)}</b><div class="src">${hs.map(h => esc(h.label.replace(b.name, '').replace(/^ — /, '') || 'JdB') + ' : ' + (isLive(h.id) ? 'alimenté' : 'non alimenté')).join(' · ')}</div></div></div>`; }).join('')}</div>
  ${footer()}`;
  const handler = id => { const n = NODE[id]; if (SIMMODE && n && (SW.has(n.t) || n.t === 'src')) { if (setSw(id, !isClosed(id))) { toast(`${short(n)} : ${isClosed(id) ? 'fermé' : 'ouvert'} (simulation)`); rerender(); } } else openEntity(id); };
  const selectedFocus = focus || NET_FINDER.selected;
  if (focus && NODE[focus]) NET_FINDER.selected = focus;
  const viewer = mountViewer($('#hta'), NETVIEW === 'full' ? fullNetSVG() : htaSVG(), { onClick: handler,
    focus: selectedFocus ? (NETVIEW === 'full' ? (BOARD[selectedFocus] ? selectedFocus : netFocus(selectedFocus)) : (NODE[selectedFocus] ? focusTarget(selectedFocus) : null)) : null,
    legend: '<span style="color:#12b76a">━ alimenté</span><span style="color:#e5484d">━ non alimenté</span><span>□ appareil ouvert · ■ fermé</span>' });
  bindNetFinder(viewer);
  if (NET_FINDER.selected) parcoursHighlight(NET_FINDER.selected);
  $('#v1').onclick = () => { NETVIEW = 'full'; rerender(); }; $('#v2').onclick = () => { NETVIEW = 'uni'; rerender(); };
  $('#m0').onclick = () => { SIMMODE = false; rerender(); }; $('#m1').onclick = () => { SIMMODE = true; rerender(); };
  $('#rst').onclick = () => { resetSim(); rerender(); };
  $('#cnr').onclick = () => { setSw('SRC_CNR', !rawClosed('SRC_CNR')); toast(rawClosed('SRC_CNR') ? 'CNR rétablie (retour sur CNR : mode réel à confirmer)' : 'Perte CNR → bascule automatique sur le secours EDF'); rerender(); };
}
function focusTarget(id) {
  // remonte jusqu'au premier élément dessiné sur le schéma HTA
  let cur = id; for (let i = 0; i < 40; i++) { const n = NODE[cur]; if (!n) break; if (n.board && BOARD[n.board] && BOARD[n.board].kind === 'HTA') return cur; if (n.t === 'tr') return cur; const u = (UP[cur] || [])[0]; if (!u) break; cur = u.a; }
  return null;
}

/* ---------- Tableaux */
let BVIEW = 'arbre';
function vBoards() {
  window.__planCur = null;
  const fstat = b => b.facade ? '<span class="pill g">Façade</span>' : (b.photos && b.photos.length ? '<span class="pill a">Photos à refaire</span>' : '<span class="pill">Sans photo</span>');
  // regroupement par grand emplacement (poste, sous-station, chaufferie, STEP, site…)
  const top = b => { const l = locChain(b.loc); return l[1] || { id: 'ZZ', name: 'Localisation non documentée' }; };
  const groups = {}; D.boards.forEach(b => { const t = top(b); (groups[t.id] = groups[t.id] || { name: t.name, bs: [] }).bs.push(b); });
  const ordered = ['PL', 'SS2', 'SS1', 'CHAUF', 'STEP', 'TERRAIN', 'ZZ'].filter(k => groups[k]).concat(Object.keys(groups).filter(k => !['PL', 'SS2', 'SS1', 'CHAUF', 'STEP', 'TERRAIN', 'ZZ'].includes(k)));
  VIEW().innerHTML = `<h1 style="margin-top:14px">Tableaux</h1>
  <div class="seg glass" style="margin-bottom:12px"><button id="bv1" class="${BVIEW === 'arbre' ? 'on' : ''}">Arborescence : de la source au tableau</button><button id="bv2" class="${BVIEW === 'loc' ? 'on' : ''}">Par localisation</button></div>
  ${BVIEW === 'arbre' ? `<div class="row" style="margin-bottom:10px"><input class="f" id="tq" type="search" placeholder="Rechercher dans l’arborescence (TGBT 2, TS 44, étuve…)" style="flex:1;min-width:220px"><button class="btn ghost" id="topen">Tout déplier</button><button class="btn ghost" id="tclose">Replier</button></div>
    <div class="card glass tree" id="tree">${arbreHTML()}</div>
    <p class="small muted">Hiérarchie tirée des liaisons documentées (unifilaire, plans, classeur, photos). ● état simulé · ⚡ remettre le courant. Les tableaux dont l’alimentation n’est pas documentée n’apparaissent pas dans l’arborescence : voir « Par localisation ».</p>`
  : ordered.map(k => { const g = groups[k]; return `<h2>${esc(g.name)} <span class="pill">${g.bs.length}</span></h2><div class="grid">${g.bs.sort((a, b) => a.name.localeCompare(b.name, 'fr', { numeric: true })).map(b => {
    const nd = (DEPS_BY_BOARD[b.id] || []).length, sw = STY[b.style] ? STY[b.style].panel : /sm6/.test(b.style || '') ? '#f1f1ef' : 'var(--line)';
    return `<div class="bcard glass" data-go="#/b/${b.id}"><div class="sw" style="background:${sw};border:1px solid var(--line)"></div><div class="row" style="justify-content:space-between"><b>${esc(b.name)}</b><span class="pill">${esc(b.kind)}</span></div>
      <div class="row">${fstat(b)}${nd ? `<span class="pill b">${nd} départs</span>` : ''}${b.loc_conf && b.loc_conf !== 'confirme' && b.loc ? confPill(b.loc_conf) : ''}</div></div>`; }).join('')}</div>`; }).join('')}
  ${footer()}`;
  $('#bv1').onclick = () => { BVIEW = 'arbre'; vBoards(); }; $('#bv2').onclick = () => { BVIEW = 'loc'; vBoards(); };
  if (BVIEW === 'arbre') bindArbre($('#tree'));
}
let BTAB = 'f';
function vBoard(id, sub, target) {
  const b = BOARD[id]; if (!b) return vBoards();
  const selectedDeparture = target && NODE[target] && NODE[target].t === 'dep' &&
    (NODE[target].board === id || (facadeFor(target) &&
    boardForFacade(facadeFor(target)) === id)) ? NODE[target] : null;
  if (sub === 'f') BTAB = 'f';
  const hasSrc = !!(NODE[id + '_QA'] && NODE[id + '_QB'] && NODE[id + '_QC']);
  const deps = DEPS_BY_BOARD[id] || [];
  const iss = D.issues.filter(i => i.ents.includes(id) || deps.some(d => i.ents.includes(d.id)));
  const il = interlock(id);
  const loc = locChain(b.loc).map(l => `<a data-go="#/">${esc(l.name)}</a>`).join('<i>›</i>') || '<a data-go="#/registre">Localisation non documentée</a>';
  VIEW().innerHTML = `<div class="crumbs" style="margin-top:10px">${loc}<i>›</i><a>${esc(b.name)}</a></div>
  <h1>${esc(b.name)}</h1>
  <div class="row" style="margin-bottom:10px"><span class="pill k">${esc(b.kind)}</span>${b.loc && b.loc_conf !== 'confirme' ? confPill(b.loc_conf) : ''}${b.it ? `<span class="pill b">Neutre IT</span>` : ''}</div>
  <div class="row" style="margin:6px 0 10px"><button class="btn" data-go="#/courant/${id}">⚡ Remettre le courant</button>${planFor(id) ? `<button class="btn ghost" data-go="#/plans/${planFor(id)}/${id}${selectedDeparture ? '/' + selectedDeparture.id : ''}">📍 Voir sur le plan</button>` : ''}</div>
  ${selectedDeparture ? `<div id="facade-return" class="card glass" style="padding:12px;margin:8px 0">
    <b>Départ sélectionné : ${esc(selectedDeparture.label)}</b>
    ${selectedDeparture.case ? `<span class="pill">Case ${esc(selectedDeparture.case)}</span>` : ''}
    <div class="row" style="margin-top:8px">
      <button class="btn" id="facade-to-reseau" data-go="#/reseau/${esc(selectedDeparture.id)}">← Voir son alimentation sur le schéma</button>
      ${parcoursContext(selectedDeparture.id).zone ? `<button class="btn ghost" id="facade-to-site" data-go="#/site/${esc(selectedDeparture.id)}">📍 Retour au bâtiment</button>` : ''}
    </div>
    <p class="small muted" style="margin:6px 0 0">Liaison documentaire, non vérification de l’état réel du réseau.</p>
  </div>` : ''}
  ${hasSrc || b.alias || b.note || b.sap || b.obs || (D.insul || {})[id] ? `<details class="card glass" style="margin:12px 0"><summary><b>Plus d’informations</b> <span class="small muted">${hasSrc ? 'règle de couplage, simulation du choix de source, ' : ''}notes</span></summary>
    ${b.alias ? `<p class="small muted">${esc(b.alias)}</p>` : ''}${b.note ? `<p class="small">${esc(b.note)}</p>` : ''}${b.sap ? `<p class="small">SAP ${esc(b.sap)}</p>` : ''}
    ${b.it ? `<p class="small">Neutre IT — contrôle d’isolement : ${esc(b.it)}${(D.insul || {})[id] ? ` · <a href="#" data-go="#/courant/${id}/isol">table voie → départ</a>` : ''}</p>` : ''}
    ${hasSrc ? couplerHTML(b) : ''}${obsHTML(b.obs)}
    ${hasSrc ? `<div class="row" style="justify-content:space-between;margin-top:8px"><b>Choix de source — simulation</b><span class="small muted">QA ${isClosed(id + '_QA') ? 'F' : 'O'} · QC ${NODE[id + '_QC'] ? (isClosed(id + '_QC') ? 'F' : 'O') : '—'} · QB ${isClosed(id + '_QB') ? 'F' : 'O'}</span></div>
    <div class="seg glass" style="margin:10px 0" id="srcmode">${[['n', 'Normal (A + B, couplage ouvert)'], ['a', 'Transfo A seul'], ['b', 'Transfo B seul'], ['ca', 'Couplage fermé sur A'], ['cb', 'Couplage fermé sur B']].map(([k, l]) => `<button data-m="${k}" class="${srcMode(id) === k ? 'on' : ''}">${l}</button>`).join('')}</div>
    ${il ? `<div class="banner ${il.lvl}">⚠️<div>${esc(il.txt)}</div></div>` : ''}${simBanner()}
    <p class="small muted" style="margin-bottom:0">${transfoLoad(id)}</p>` : ''}</details>` : ''}
  <div class="seg glass" id="btabs">${[['f', 'Façade'], ['d', `Départs (${deps.length})`], ['s', 'Alimentation'], ['p', 'Photos'], ...(iss.length ? [['i', `Incohérences (${iss.length})`]] : [])].map(([k, l]) => `<button data-t="${k}" class="${BTAB === k ? 'on' : ''}">${l}</button>`).join('')}</div>
  <div id="bbody" style="margin-top:14px"></div>${footer()}`;
  $('#btabs button').forEach(x => x.onclick = () => { BTAB = x.dataset.t; vBoard(id, null, selectedDeparture ? selectedDeparture.id : null); });
  $('#srcmode button').forEach(x => x.onclick = () => { applyMode(id, x.dataset.m); vBoard(id, null, selectedDeparture ? selectedDeparture.id : null); });
  const body = $('#bbody');
  if (BTAB === 'f') {
    if (b.facade) {
      const f = D.facades[b.facade];
      body.innerHTML = `<div class="banner info" style="margin-bottom:10px">✏️<div class="small"><b>Reconstruction vectorielle</b> — ${esc(f.conf)}<br><span class="muted">Source : ${esc(f.src)}</span></div></div><div id="fv"></div>`;
      mountViewer($('#fv'), facadeSVG(b.facade, { live: true }), { onClick: openEntity, focus: target, legend: '<span>● vert : alimenté (simulé)</span><span>● rouge : non alimenté</span><span>Touchez un appareil</span>' });
      if (selectedDeparture) body.insertAdjacentHTML('afterbegin', '<div class="banner info" id="facade-target" style="margin-bottom:10px"><div><b>Départ ciblé : ' + esc(NODE[target].label) + '</b>' + (NODE[target].case ? '<div class="small">Case ' + esc(NODE[target].case) + '</div>' : '') + '<button class="btn ghost" style="margin-top:7px" data-open="' + esc(target) + '">Ouvrir la fiche du départ</button></div></div>');
    } else body.innerHTML = `<div class="card glass"><h3 style="margin-top:0">Façade non reconstruite</h3><p class="small">Aucune façade n’est dessinée pour ce tableau : soit les photographies n’ont pas encore été relevées, soit les étiquettes ne sont pas lisibles. Les appareils ne sont pas représentés par un symbole générique pour éviter toute confusion.</p><div>${photoLinks(b.photos)}</div></div>`;
  } else if (BTAB === 'd') {
    const halves = b.halves.length ? b.halves : [{ id: null, label: 'Départs' }];
    body.innerHTML = halves.map(h => { const ds = deps.filter(d => !h.id || busOf(d.id) === h.id); if (!ds.length) return ''; return `<div class="card glass" style="margin-bottom:12px"><div class="row" style="justify-content:space-between"><h3 style="margin:0">${esc(h.label)}</h3>${h.id && NODE[h.id] ? `<span class="pill ${isLive(h.id) ? 'g' : 'r'}">${isLive(h.id) ? 'alimenté' : 'non alimenté'} (simulé)</span>` : ''}</div><div class="list" style="margin-top:8px">${ds.map(liNode).join('')}</div></div>`; }).join('') || '<p class="muted">Aucun départ documenté.</p>';
  } else if (BTAB === 's') {
    const any = b.halves.find(h => NODE[h.id]);
    body.innerHTML = any ? b.halves.filter(h => NODE[h.id]).map(h => `<div class="card glass" style="margin-bottom:12px"><h3 style="margin-top:0">${esc(h.label)}</h3>${sourcesBlock(h.id)}</div>`).join('') : (b.kind === 'HTA' ? `<div class="card glass">${sourcesBlock(id === 'PL20' ? 'PL_B01' : id === 'SS1_20' ? 'SS1_BL' : id === 'SS2_20' ? 'SS2_BL' : 'KV6_BL')}</div>` : '<p class="muted">Non documenté.</p>');
  } else if (BTAB === 'p') {
    body.innerHTML = `<div class="card glass"><h3 style="margin-top:0">Photographies sources</h3>${photoLinks(b.photos)}<h3>Documents</h3>${(b.docs || []).map(d => `<div class="small">• ${esc(d)}</div>`).join('') || '<span class="muted">—</span>'}
      <h3>Procédures</h3>${D.procs.filter(p => p.board === id).map(p => `<div class="li" data-open="proc:${p.id}"><span>📘</span><div class="grow">${esc(p.title)}<div class="src">${esc(p.status)}</div></div></div>`).join('') || '<span class="muted">—</span>'}</div>`;
  } else body.innerHTML = iss.map(i => `<div class="li glass" style="border-radius:16px;margin-bottom:8px" data-open="issue:${i.id}"><span>⚠️</span><div class="grow"><b>${esc(i.title)}</b><div class="small">${esc(i.text)}</div></div></div>`).join('') || '<p class="muted">Aucune incohérence relevée pour ce tableau.</p>';
}
function srcMode(id) {
  const a = isClosed(id + '_QA'), b = isClosed(id + '_QB'), c = NODE[id + '_QC'] ? isClosed(id + '_QC') : false;
  if (a && b && !c) return 'n'; if (a && !b && !c) return 'a'; if (!a && b && !c) return 'b'; if (a && !b && c) return 'ca'; if (!a && b && c) return 'cb'; return '?';
}
function applyMode(id, m) {
  const set = { n: [1, 1, 0], a: [1, 0, 0], b: [0, 1, 0], ca: [1, 0, 1], cb: [0, 1, 1] }[m];
  const ids = [id + '_QA', id + '_QB', id + '_QC'];
  // ouvrir d'abord, fermer ensuite : on ne traverse jamais l'état interdit « 3 fermés »
  ids.forEach((x, i) => { if (NODE[x] && !set[i] && isClosed(x)) setSw(x, false); });
  ids.forEach((x, i) => { if (NODE[x] && set[i] && !isClosed(x)) setSw(x, true); });
}
function transfoLoad(id) {
  const ta = NODE[(UP[id + '_QA'] || [])[0].a], tb = NODE[(UP[id + '_QB'] || [])[0].a];
  return `Puissances : ${short(ta)} ${ta.kva || '?'} · ${short(tb)} ${tb.kva || '?'}. Charge réelle non documentée : une configuration « un seul transformateur » peut être limitée par la puissance disponible.`;
}

/* ---------- Dépannage */
const STOP = new Set(['perte', 'de', 'du', 'des', 'la', 'le', 'les', 'sur', 'alimentation', 'courant', 'tension', 'depart', 'plus', 'pas', 'defaut', 'declenchement', 'panne', 'coupure', 'au', 'a', 'en', 'il', 'n', 'y', 'ya', 'manque', 'disjonction', 'disjoncte', 'arret', 'probleme', 'l', 'd']);
function vDiag(pre) {
  VIEW().innerHTML = `<h1>Dépannage — aide au diagnostic</h1><p class="sub">Décrivez l’incident : l’application retrouve l’équipement et présente un diagnostic <b>documentaire</b> structuré.</p>
  <div class="banner danger" style="margin-bottom:12px">⛔<div><b>Les ordres de manœuvre des fiches de dépendance sont des projets rédigés d’après les documents</b> : ils ne sont utilisables qu’après validation et signature du chargé d’exploitation (mention « Validé »). Les possibilités affichées ici sont théoriques. Toute intervention : personnel habilité, NF C 18-510, procédures validées du site.</div></div>
  <a class="bigbtn" data-go="#/courant" style="margin-bottom:12px">⚡<div><b>Remettre le courant</b><span>Fiche de manœuvre en 3 touches</span></div></a>
  <div class="card glass"><input class="f" id="dq" placeholder="ex. Perte de courant sur le départ Étuve 2 · Perte alimentation TGBT 2 · Défaut d’isolement TGBT 4" value="${esc(pre && NODE[pre] ? dn(NODE[pre]) || NODE[pre].label : pre && BOARD[pre] ? BOARD[pre].name : '')}">
  <div class="row" style="margin-top:10px">${['Perte de courant sur le départ Étuve 2', 'Perte alimentation TGBT 2', 'Déclenchement TR 6A', 'Défaut d’isolement TGBT 4', 'Perte TS 9'].map(t => `<button class="chip" data-x="${esc(t)}">${esc(t)}</button>`).join('')}</div></div>
  <div id="dres"></div>${footer()}`;
  let first = !!pre;
  const run = () => {
    const q = $('#dq').value, toks = norm(q).split(' ').filter(t => t && !STOP.has(t));
    const insul = /isolement|insulation|terre/.test(norm(q));
    const qq = toks.filter(t => !['isolement', 'insulation', 'terre', 'd'].includes(t)).join(' ');
    // équipement choisi explicitement (#/depannage/<id>) : pas de nouvelle recherche
    if (first && (NODE[pre] || BOARD[pre])) { first = false; const rec = IDX.find(x => x.id === pre && (x.kind === 'node' || x.kind === 'board'));
      $('#dres').innerHTML = diagReport(rec, [], insul); return; }
    first = false;
    const r = search(qq || q, 8).filter(x => x.kind === 'node' || x.kind === 'board');
    if (!r.length) { $('#dres').innerHTML = `<p class="muted" style="margin-top:14px">Aucun équipement reconnu. Essayez un repère (7K121), un tableau (TGBT 2), un transformateur (TR 6A).</p>`; return; }
    // plusieurs équipements possibles et aucun repère exact : demander lequel, au lieu de choisir le premier
    const ex = exactMatches(r, qq || q);
    if (ex.length !== 1 && r.length > 1) { $('#dres').innerHTML = chooseHTML(ex.length ? ex : r, '#/depannage/'); return; }
    $('#dres').innerHTML = diagReport(ex[0] || r[0], r.filter(x => x !== (ex[0] || r[0])).slice(0, 5), insul);
  };
  $('#dq').addEventListener('keydown', e => { if (e.key === 'Enter') run(); });
  $('#dq').addEventListener('input', () => { clearTimeout(window.__dq); window.__dq = setTimeout(run, 250); });
  $$('[data-x]').forEach(b => b.onclick = () => { $('#dq').value = b.dataset.x; run(); });
  if (pre) run();
}
/* correspondance exacte : nom court, libellé, repère ou case identiques à la saisie */
function exactMatches(r, q) {
  const qn = norm(q), qc = qn.replace(/ /g, '');
  const eq = s => s && (norm(s) === qn || norm(s).replace(/ /g, '') === qc);
  return r.filter(x => { const n = NODE[x.id], b = BOARD[x.id];
    if (x.kind === 'board') return eq(b.name) || eq(b.id);
    return n && (eq(n.label) || eq(dn(n)) || eq(n.rep) || eq(n.case) || eq((n.uni || {}).rep)); });
}
function chooseHTML(r, base) {
  return `<div class="card glass" style="margin-top:12px"><h3 style="margin-top:0">Plusieurs équipements correspondent : lequel ?</h3><div class="list">${r.map(x => { const n = NODE[x.id], b = x.kind === 'board' ? BOARD[x.id] : boardOf(n);
    return `<div class="li" data-go="${base}${x.id}"><span class="pill">${TYPE[x.t] || TYPE[x.kind] || ''}</span><div class="grow"><b>${esc(x.kind === 'board' ? b.name : dn(n) || n.label)}</b><div class="src">${esc(recContext(x))}</div></div><span>›</span></div>`; }).join('')}</div></div>`;
}
function diagReport(top, alts, insul) {
  let id = top.kind === 'board' ? (NODE[top.id + 'A'] ? top.id + 'A' : ((BOARD[top.id].halves || []).find(h => NODE[h.id]) || {}).id
    || (D.nodes.find(x => x.board === top.id && x.t === 'bus') || D.nodes.find(x => x.board === top.id) || {}).id) : top.id;
  if (!NODE[id]) return '<p class="muted">Aucun appareil documenté pour ce tableau.</p>';
  if (top.kind !== 'node' && top.kind !== 'board') return `<p class="muted">Résultat de type ${esc(top.kind)} — ouvrez-le depuis la recherche.</p>`;
  const n = NODE[id] || NODE[top.id]; id = n.id;
  const b = boardOf(n) || BOARD[top.id];
  const isBoard = top.kind === 'board';
  const roots = isBoard ? (BOARD[top.id].halves || []).map(h => h.id).filter(h => NODE[h]) : [id];
  const seenP = new Set(), paths = [];
  roots.forEach(r => upPaths(r).forEach(p => { const k = p.slice(1).join('>'); if (!seenP.has(k)) { seenP.add(k); paths.push(p); } }));
  paths.sort((a, b) => a.length - b.length);
  const sec = (num, t, html) => `<div class="card glass" style="margin-top:12px"><h3 style="margin-top:0"><span class="pill k">${num}</span> ${t}</h3>${html}</div>`;
  const onPath = new Set(paths.flat());
  const prots = [...onPath].map(x => NODE[x]).filter(x => x.prot || (x.t === 'cb' && x.model) || x.t === 'cpl');
  const trs = [...onPath].map(x => NODE[x]).filter(x => x.t === 'tr');
  const bus = n.t === 'bus' ? id : busOf(id);
  const sib = bus ? (DOWN[bus] || []).map(e => NODE[e.b]).filter(x => x.t === 'dep' && x.id !== id) : [];
  const htaBus = [...onPath].map(x => NODE[x]).filter(x => x.t === 'bus' && x.board && BOARD[x.board].kind === 'HTA');
  const neighboursHTA = htaBus.map(hb => `<b>${esc(short(hb))}</b> alimente : ${(DOWN[hb.id] || []).map(e => NODE[e.b]).filter(x => x.t === 'cb').map(c => { const t = (DOWN[c.id] || []).map(e => NODE[e.b]).find(x => x.t === 'tr'); return t ? esc(short(t)) : esc(short(c)); }).join(', ')}`).join('<br>');
  const procs = D.procs.filter(p => (b && p.board === b.id) || p.ents.some(e => onPath.has(e)));
  const alt = [];
  paths.forEach(p => { const off = p.filter(x => SW.has(NODE[x].t) && !isClosed(x) && x !== id); if (off.length) alt.push({ p, off }); });
  const iss = D.issues.filter(i => issueActive(i) && i.ents.some(e => onPath.has(e) || e === id || (b && e === b.id)));
  return `${iss.length ? `<div class="banner danger" style="margin-top:12px">⚠️<div><b>Incohérences documentaires sur ce chemin — à lever avant toute intervention :</b><br>${iss.map(i => `<a href="#" data-open="issue:${i.id}">${esc(i.title)}</a>`).join(' · ')}</div></div>` : ''}
  ${sec(1, 'Équipement identifié', `<div class="li" data-open="${isBoard ? top.id : id}"><span class="dot ${isLive(id) ? 'on' : 'off'}"></span><div class="grow"><b>${esc(isBoard ? BOARD[top.id].name : n.label)}</b><div class="src">${esc(recContext(top))}</div></div>${confPill(n.conf)}</div>
    ${crumbsFor(n)}${alts.length ? `<details><summary class="small">Ce n’est pas le bon ? Autres correspondances (${alts.length})</summary>${alts.map(a => `<div class="li" data-go="#/depannage/${a.id}"><div class="grow">${esc(a.label)}<div class="src">${esc(recContext(a))}</div></div><span>›</span></div>`).join('')}</details>` : ''}
    <div class="row" style="margin-top:8px"><button class="btn" data-go="#/courant/${isBoard ? top.id : id}">⚡ Fiche de dépannage</button></div>`)}
  ${sec(2, 'Chemin électrique amont documenté', paths.length ? paths.slice(0, 6).map((p, i) => `<div class="small"><b>${i + 1}.</b> ${pathVia(p)}</div>${pathHTML(p, 0)}`).join('') : '<p class="muted">Aucun chemin documenté.</p>')}
  ${sec(3, 'Transformateurs et cellules HTA associés', trs.length ? trs.map(t => { const cell = NODE[(UP[t.id] || [])[0].a]; return `<div class="li" data-open="${t.id}"><span>⚡</span><div class="grow"><b>${esc(t.label)}</b> · ${esc(t.kva || '')} · ${esc(t.u || '')}<div class="src">${esc(cell.label)} — ${esc(cell.prot || '')}</div></div>${confPill(t.conf)}</div>`; }).join('') : '<p class="muted">Non documenté.</p>')}
  ${sec(4, 'Protections et couplages connus sur le chemin', prots.length ? `<div class="tablewrap"><table><tr><th>Appareil</th><th>Réglage / modèle</th><th>État simulé</th></tr>${prots.map(x => `<tr data-open="${x.id}" style="cursor:pointer"><td>${esc(x.label)}</td><td class="small">${esc(x.prot || x.model || (x.t === 'cpl' ? (boardOf(x) && boardOf(x).coupler.rule) || 'Règle non documentée' : ''))}</td><td>${isClosed(x.id) ? '<span class="pill g">fermé</span>' : '<span class="pill r">ouvert</span>'}</td></tr>`).join('')}</table></div>` : '<p class="muted">Non documenté.</p>')}
  ${sec(5, 'Équipements partageant la même alimentation', `${sib.length ? `<p class="small">Même jeu de barres (<b>${esc(short(NODE[bus]))}</b>) : ${sib.length} départ(s).</p><div class="list">${sib.slice(0, 25).map(liNode).join('')}</div>` : '<p class="muted small">Aucun autre départ documenté sur ce jeu de barres.</p>'}
     ${neighboursHTA ? `<p class="small" style="margin-top:10px">Même demi-jeu de barres HTA :<br>${neighboursHTA}</p>` : ''}`)}
  ${sec(6, 'Distinguer une perte locale d’une perte amont — éléments à observer', `<ol class="small" style="padding-left:18px;margin:0">
     <li>État des <b>autres départs du même jeu de barres</b> (liste ci-dessus) : s’ils sont alimentés, la cause est probablement <b>locale</b> au départ ou en aval.</li>
     <li>Si tout le jeu de barres est hors tension : signalisation de l’<b>arrivée</b> (déclencheur Micrologic, voyants, centrale de mesure) et du <b>couplage</b>.</li>
     <li>Si l’autre demi-jeu de barres est aussi hors tension : vérifier les <b>relais de la cellule HTA</b> du transformateur (réglages section 4) et la surveillance transformateur (sondes / DGPT2).</li>
     <li>Si plusieurs transformateurs d’un même demi-jeu de barres HTA sont hors tension : cause <b>amont HTA</b> (arrivée A1/A2/A3/A4, poste de livraison, source CNR / EDF).</li>
     <li>Coupure générale brève puis retour : vérifier si la <b>permutation automatique CNR → secours EDF</b> a fonctionné (bobine à manque de tension, position des disjoncteurs 01 et 04 au poste de livraison).</li>
     ${insul || (b && b.it) ? `<li><b>Réseau BT en neutre IT</b>${b && b.it ? ' (' + esc(b.it) + ')' : ''} : un 1er défaut d’isolement ne déclenche pas ; lire le contrôleur d’isolement et le localisateur de <b>ce</b> tableau. ${b && (D.insul || {})[b.id] ? `<a href="#" data-go="#/courant/${b.id}/isol">Table voie → départ de ce tableau</a>.${/seuil/i.test(D.insul[b.id].note || '') ? ' ' + esc(D.insul[b.id].note) : ''}` : 'Table voie → départ non disponible pour ce tableau (ne pas utiliser celle d’un autre tableau).'}</li>` : ''}
     </ol><p class="small muted">Ces éléments d’observation ne constituent pas une procédure ; l’intervention relève du chargé de consignation / chargé d’intervention habilité.</p>`)}
  ${sec(7, 'Chemins alternatifs présents dans le schéma (théoriques)', alt.length ? `<p class="small">Chemins documentés passant par au moins un appareil <b>ouvert dans l’hypothèse de simulation</b>. Leur disponibilité réelle (état, charge, interverrouillages, protections) n’est <b>pas</b> supposée.</p>${alt.slice(0, 5).map(a => `<div class="small">• via ${a.off.map(x => `<a href="#" data-open="${x}">${esc(short(NODE[x]))}</a>`).join(', ')} — ${esc(NODE[a.p[a.p.length - 1]].label)}</div>`).join('')}` : '<p class="muted small">Aucun chemin alternatif documenté (tous les chemins connus sont déjà fermés dans l’hypothèse, ou il n’en existe pas).</p>')}
  ${sec(8, 'Procédures et documents de manœuvre (avec leur statut)', procs.length ? procs.map(p => `<div class="li" data-open="proc:${p.id}"><span>${p.steps.length ? '📘' : '⏳'}</span><div class="grow">${esc(p.title)}<div class="src">${esc(p.status)}</div></div></div>`).join('') + '<p class="small muted">Aucune de ces pièces n’est une procédure validée du site tant que son statut ne l’indique pas.</p>' : '<p class="muted">Aucune procédure du site pour ce chemin.</p>')}`;
}

/* ---------- Entretien */
const GUIDES = [
  { k: 'SM6', t: 'Cellules HTA SM6 et disjoncteurs SF1', items: ['Inspection visuelle : propreté, traces d’échauffement ou d’effluves, état des voyants de présence tension.', 'Contrôle de la pression SF6 (indicateur) selon notice.', 'Manœuvres mécaniques à vide et vérification des verrouillages / clés (hors exploitation, selon procédure).', 'Contrôle des relais de protection (S20/S2036…) par injection secondaire — conserver les réglages relevés sur l’unifilaire.', 'Contrôle des batteries / alimentation auxiliaire 110 V CC et 24 V CC.'] },
  { k: 'TR', t: 'Transformateurs HTA/BT', items: ['Relevé des températures (sondes PT100 / relais) ou contrôle du DGPT2 (niveau, pression, gaz, température) selon le type.', 'Inspection des bornes et connexions HTA/BT, thermographie sous charge.', 'Nettoyage et dépoussiérage hors tension (transformateurs secs).', 'Pour les immergés : analyse d’huile périodique selon recommandations constructeur.'] },
  { k: 'TGBT', t: 'TGBT Okken / Prisma', items: ['Thermographie infrarouge des jeux de barres, connexions et départs en charge.', 'Contrôle des couples de serrage (hors tension).', 'Masterpact NW / MTZ : manœuvres, test du déclencheur Micrologic (valise), état des contacts et chambres de coupure selon notice.', 'Compact NS / NSX : manœuvres, essai de déclenchement, état des auxiliaires.', 'Vérification des voyants, centrales de mesure (PM8xx) et parafoudres (indicateur de fin de vie).'] },
  { k: 'IT', t: 'Contrôleurs d’isolement (neutre IT)', items: ['Lecture et consignation de la résistance d’isolement de chaque jeu de barres (IM400).', 'Test fonctionnel du contrôleur (bouton test) et des localisateurs IFL12.', 'Vérification des seuils (TGBT 1 : préalarme 30 kΩ, alarme 2 kΩ) et de la communication (PAS600).'] },
  { k: 'COND', t: 'Batteries de condensateurs', items: ['Contrôle visuel (gonflement, fuites), températures et ventilation.', 'Mesure des capacités et des courants par gradin, état des fusibles et contacteurs.', 'Lecture du régulateur varmétrique (cos φ, alarmes).'] },
  { k: 'REG', t: 'Cadre réglementaire', items: ['Vérification périodique des installations électriques par une personne ou un organisme qualifié (Code du travail, arrêté du 26 décembre 2011) et levée des observations.', 'Opérations sous NF C 18-510 : habilitations, consignation, mise en sécurité.'] },
];
const LOG_KEY = 'occE.log.v1';
const getLog = () => { try { return JSON.parse(localStorage.getItem(LOG_KEY) || '[]'); } catch (e) { return []; } };
const setLog = l => { try { localStorage.setItem(LOG_KEY, JSON.stringify(l)); return true; } catch (e) { return false; } };
function vMaint(pre) {
  const log = getLog();
  VIEW().innerHTML = `<h1>Entretien</h1><p class="sub">Gammes indicatives par type d’équipement et journal d’interventions local.</p>
  <div class="banner info">ℹ️<div class="small">Gammes <b>indicatives</b> : à adapter aux notices constructeur et au plan de maintenance du site. Le journal est enregistré <b>uniquement sur cet appareil</b> (stockage du navigateur) : exportez-le régulièrement.</div></div>
  <h2>Interventions documentées</h2>
  <div class="list card glass"><div class="li" data-go="#/b/TGBT1"><span>🧾</span><div class="grow"><b>06/11/2024 — TGBT 1A / 1B (SS1)</b><div class="small">Schneider WO-12101777 : remplacement XM300C + XD312 par 2 IM400C + 2 IFL12, communication RS485 / PAS600, essais OK.</div></div></div>
    <div class="li" data-go="#/b/TGBT2"><span>🧾</span><div class="grow"><b>15/10/2024 — TGBT 2</b><div class="small">Mise à jour plan TH112001 rév. F : ajout du départ Bâtiment Bronzini (case 7-53, NS1250N).</div></div></div></div>
  <h2>Journal</h2>
  <div class="card glass"><div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(200px,1fr))">
    <label class="small">Équipement<input class="f" id="le" list="lel" value="${esc(pre && NODE[pre] ? NODE[pre].label : '')}" placeholder="rechercher…"><datalist id="lel">${D.boards.map(b => `<option value="${esc(b.name)}">`).join('')}${D.nodes.filter(n => n.t !== 'bus').slice(0, 900).map(n => `<option value="${esc(n.label)}">`).join('')}</datalist></label>
    <label class="small">Date<input class="f" id="ld" type="date" value="${new Date().toISOString().slice(0, 10)}"></label>
    <label class="small">Type<select class="f" id="lt"><option>Préventif</option><option>Correctif</option><option>Constat / relevé</option><option>Thermographie</option><option>Contrôle réglementaire</option></select></label>
    <label class="small">Intervenant<input class="f" id="li" placeholder="Nom"></label></div>
    <label class="small">Observations<textarea class="f" id="lo" rows="3" placeholder="Constats, mesures, pièces…"></textarea></label>
    <div class="row" style="margin-top:10px"><button class="btn" id="ladd">Ajouter au journal</button><button class="btn ghost" id="lexp">Exporter (CSV)</button></div></div>
  <div class="card glass" style="margin-top:12px">${log.length ? `<div class="tablewrap"><table><tr><th>Date</th><th>Équipement</th><th>Type</th><th>Intervenant</th><th>Observations</th><th></th></tr>${log.map((l, i) => `<tr><td>${esc(l.d)}</td><td>${esc(l.e)}</td><td>${esc(l.t)}</td><td>${esc(l.i)}</td><td class="small">${esc(l.o)}</td><td><button class="btn ghost" data-del="${i}" style="padding:4px 10px">✕</button></td></tr>`).join('')}</table></div>` : '<p class="muted">Journal vide sur cet appareil.</p>'}</div>
  <h2>Gammes par type d’équipement</h2><div class="grid">${GUIDES.map(g => `<div class="card glass"><h3 style="margin-top:0">${esc(g.t)}</h3><ul class="small" style="padding-left:18px;margin:0">${g.items.map(i => `<li style="margin:5px 0">${esc(i)}</li>`).join('')}</ul></div>`).join('')}</div>
  ${footer()}`;
  $('#ladd').onclick = () => { const e = $('#le').value.trim(); if (!e) { toast('Indiquez un équipement'); return; } const l = getLog(); l.unshift({ e, d: $('#ld').value, t: $('#lt').value, i: $('#li').value, o: $('#lo').value }); if (setLog(l)) { toast('Intervention enregistrée'); vMaint(); } else toast('Stockage indisponible sur ce navigateur'); };
  $$('[data-del]').forEach(b => b.onclick = () => { const l = getLog(); l.splice(+b.dataset.del, 1); setLog(l); vMaint(); });
  $('#lexp').onclick = () => { const l = getLog(); const csv = 'Date;Équipement;Type;Intervenant;Observations\n' + l.map(x => [x.d, x.e, x.t, x.i, x.o].map(v => '"' + String(v || '').replace(/"/g, '""') + '"').join(';')).join('\n');
    const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv' })); a.download = 'journal_occ_energie.csv'; a.click(); };
}

/* ---------- Registre */
function vReg() {
  const crit = b => { const nd = (DEPS_BY_BOARD[b.id] || []).length; return [
    ['Topologie amont', b.kind === 'HTA' || (b.halves || []).some(h => NODE[h.id] && upPaths(h.id, 1).length) ? 1 : 0],
    ['Départs listés', nd ? 1 : 0], ['Façade', b.facade ? 1 : 0], ['Couplage', b.coupler.status === 'documente' || b.coupler.status === 'sans_objet' ? 1 : 0],
    ['Localisation', b.loc && b.loc_conf === 'confirme' ? 1 : b.loc ? .5 : 0], ['Photos', b.photos && b.photos.length ? 1 : 0]]; };
  const ok = v => v === 1 ? '<span class="pill g">✓</span>' : v ? '<span class="pill a">~</span>' : '<span class="pill r">✗</span>';
  VIEW().innerHTML = `<h1>Registre et contrôle qualité</h1><p class="sub">Traçabilité des sources, état d’avancement mesurable par tableau, incohérences et informations manquantes.</p>
  <h2>Légende de confiance</h2><div class="row">${Object.values(CONF).map(([k, t]) => `<span class="pill ${k}">${t}</span>`).join('')}<span class="small muted">Toute information porte sa source (document › repère) dans sa fiche.</span></div>
  <h2>Écarts documentaires <span class="pill a">${D.issues.filter(issueActive).length} actifs</span> <span class="pill">${D.issues.length - D.issues.filter(issueActive).length} résolus</span></h2>
  <div class="list card glass">${D.issues.slice().sort((a, b) => issueActive(b) - issueActive(a)).map(i => `<div class="li" data-open="issue:${i.id}"><span class="pill ${!issueActive(i) ? '' : i.sev === 'haute' ? 'r' : i.sev === 'moyenne' ? 'a' : ''}">${issueActive(i) ? esc(i.sev) : 'résolu'}</span><div class="grow"><b>${esc(i.title)}</b><div class="small muted">${esc(i.text.slice(0, 170))}…</div></div></div>`).join('')}</div>
  <h2>Avancement par tableau</h2><p class="small muted">Critères vérifiables, sans pourcentage global : ✓ documenté · ~ partiel/probable · ✗ manquant.</p>
  <div class="card glass tablewrap"><table><tr><th>Tableau</th>${crit(D.boards[0]).map(c => `<th>${c[0]}</th>`).join('')}<th>Départs</th></tr>
  ${D.boards.map(b => `<tr data-go="#/b/${b.id}" style="cursor:pointer"><td><b>${esc(b.name)}</b></td>${crit(b).map(c => `<td>${ok(c[1])}</td>`).join('')}<td>${(DEPS_BY_BOARD[b.id] || []).length}</td></tr>`).join('')}</table></div>
  ${keysSection()}
  <h2>Procédures</h2><div class="list card glass">${D.procs.map(p => `<div class="li" data-open="proc:${p.id}"><span>${p.steps.length || p.but.length ? '📘' : '⏳'}</span><div class="grow">${esc(p.title)}<div class="src">${esc(p.status)}</div></div></div>`).join('')}</div>
  <h2>Classeur Excel</h2><p class="small">Toutes les lignes non vides des onglets TR 1 à TR 9 sont rattachées à un tableau du modèle (${D.xl_left.length} ligne(s) non rattachée(s)). Onglet TR 3 absent du classeur.</p>
  <h2>Informations à fournir</h2><div class="card glass"><ol class="small" style="padding-left:18px;margin:0">
    <li>Procédures d’exploitation du site, validées : perte d’une cellule ou d’un transformateur, changement de source, groupe, onduleurs, retour à la normale (identité, conditions préalables, critères d’arrêt, validation).</li>
    <li>Réponses de l’exploitant : convention de la légende des clés ; retour sur CNR automatique ou manuel ; logique du groupe électrogène.</li>
    <li>Confirmation sur site du croisement TR 1A / TR 2A ↔ TGBT 1 / TGBT 2 et des serrures Ronis du TGBT 3 (écart I-TGBT3-LOCK).</li>
    <li>Photos du poste de livraison 20 kV (aucune photo) et dossiers ZIP 13 à 19 et 21 (TGBT 4 à 9).</li>
    <li>Relevés ciblés : tables « localisation défaut » des TGBT 5, 6, 7 ; cases B2/B3 du TGBT 9 ; plaque de l’onduleur 2 et départ QF4 ; source du 2e coffret ventilation Four ; plaque Spang Gorge ; petits départs Bronzini ; régulateurs des condensateurs ; OM 27 portes ouvertes.</li>
    <li>Exports PDF des 9 plans DWG « R122618 rev1 SS2 UPS distribution » (01, 02, 05, 10, 12, 13, 14, 15, 16).</li>
    <li>Charges mesurées datées et limites d’exploitation (une puissance en kVA n’est pas une réserve disponible).</li>
    <li>Schémas des auxiliaires 110 V CC / 24 V CC (diagnostic « ne s’arme pas / ne commande pas »).</li></ol></div>
  <h2>Dossier des photos sur ce poste</h2><div class="card glass"><p class="small">Les liens « Ouvrir la source » cherchent les PDF dans ce dossier. Par défaut : le dossier « Plan électrique » placé à côté du dossier de l’application. Réglage enregistré sur ce poste uniquement.</p>
    <div class="row"><input class="f" id="phdir" style="flex:1;min-width:240px" value="${esc(decodeURI(PHOTO_BASE))}"><button class="btn" id="phsave">Enregistrer</button><button class="btn ghost" id="phdef">Par défaut</button></div>
    <p class="small muted">Exemple : file:///C:/Users/…/DISTRIBUTION-ELECTRIQUE/Plan électrique/</p></div>
  ${footer()}`;
  const setDir = v => { PHOTO_BASE = v; try { if (v === PHOTO_DEF) localStorage.removeItem(PHOTO_KEY); else localStorage.setItem(PHOTO_KEY, v); } catch (e) {} toast('Dossier des photos enregistré'); vReg(); };
  $('#phsave').onclick = () => { let v = $('#phdir').value.trim().replace(/\\/g, '/'); if (!v) return; if (!v.endsWith('/')) v += '/'; if (/^[a-z]:\//i.test(v)) v = 'file:///' + v; setDir(encodeURI(v)); };
  $('#phdef').onclick = () => setDir(PHOTO_DEF);
}

/* ======================================================================= démarrage */
shell();
window.addEventListener('hashchange', () => { if (location.hash === LAST_ROUTED_HASH) return; closeSheet(); route(false); });
route(false);
