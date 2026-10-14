/* Schéma de principe complet : poste de livraison → tableaux 20 kV → cellules → transformateurs → TGBT (demi-JdB A / couplage / B) → tableaux alimentés.
   Les deux demi-jeux de barres 20 kV sont dessinés sur deux niveaux (gauche en haut, droit en bas) pour que chaque TGBT
   reçoive son transfo A et son transfo B sans croisement ; l'ordre physique des cellules reste visible sur la façade du tableau 20 kV. */
function fullNetSVG() {
  const BW = 320, M = 70;
  const tgbtPairs = n => ({ kind: 'pair', title: `TGBT ${n}`, board: `TGBT${n}`, qa: `TGBT${n}_QA`, qb: `TGBT${n}_QB`, qc: `TGBT${n}_QC`, ba: `TGBT${n}A`, bb: `TGBT${n}B` });
  const SECTIONS = [
    { title: 'SOUS-STATION 2 — Tableau 20 kV arrivée CNR / EDF (unifilaire « S/STATION 1 ») → TR 1 à 6 → TGBT 1 à 6', L: 'SS1_BL', R: 'SS1_BR', aL: 'SS1_A1', aR: 'SS1_A2', cpl: 'SS1_V500', board: 'SS1_20',
      blocks: [1, 2, 3, 4, 5, 6].map(tgbtPairs) },
    { title: 'SOUS-STATION 1 — Tableau 20 kV (unifilaire « S/STATION 2 ») → TR 7 / TR 9 / Boosting / Four 2 / électrodes', L: 'SS2_BL', R: 'SS2_BR', aL: 'SS2_A3', aR: 'SS2_A4', cpl: 'SS2_CPL', board: 'SS2_20',
      blocks: [tgbtPairs(7), tgbtPairs(9), Object.assign(tgbtPairs(8), { title: 'TGBT 8 — Boosting Four 1' }),
        { kind: 'pair', title: '6 kV Four 2', board: 'KV6', qa: 'KV6_A2', qb: 'KV6_A1', qc: 'KV6_C', ba: 'KV6_BL', bb: 'KV6_BR' },
        { kind: 'single2', title: 'Électrodes B&B', trs: ['AEF1-TRZ2', 'AEF1-TRZ1'] },
        { kind: 'single2', title: 'TR Hydrogène', trs: ['TR-HYD', null] }] },
  ];
  const W = M * 2 + 6 * BW;
  let o = '', y = 30;
  const col = id => lc(id);
  const L = (x1, y1, x2, y2, id, w = 4, extra = '') => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${id ? col(id) : '#9aa5a0'}" stroke-width="${w}" ${id ? 'data-wire-id="' + esc(id) + '"' : ''} ${extra}/>`;
  const hit = (id, inner, x, y, w, h) => `<g class="hit" data-id="${id}"><title>${esc(NODE[id].label)}</title>${inner}<rect class="hl" x="${x}" y="${y}" width="${w}" height="${h}" rx="7"/><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="transparent"/></g>`;
  const trSym = (id, cx, cy) => hit(id, `<circle cx="${cx}" cy="${cy}" r="13" fill="none" stroke="${col(id)}" stroke-width="3.5"/><circle cx="${cx}" cy="${cy + 17}" r="13" fill="none" stroke="${col(id)}" stroke-width="3.5"/>`, cx - 18, cy - 17, 36, 50);
  const label = (x, yy, t, fs = 11, w = 700, anchor = 'middle', fill = 'currentColor') => `<text x="${x}" y="${yy}" font-size="${fs}" font-weight="${w}" text-anchor="${anchor}" fill="${fill}">${esc(t)}</text>`;
  // ------------------------------------------------ poste de livraison
  const xE = W / 2 - 260, xC = W / 2 + 260;
  o += label(M, y, 'POSTE DE LIVRAISON 20 kV CNR / EDF', 15, 800, 'start');
  y += 30;
  o += hit('SRC_EDF', `<circle cx="${xE}" cy="${y + 18}" r="20" fill="none" stroke="${col('SRC_EDF')}" stroke-width="4"/>${label(xE, y + 23, 'EDF', 12, 800)}`, xE - 24, y - 4, 48, 46);
  o += hit('SRC_CNR', `<circle cx="${xC}" cy="${y + 18}" r="20" fill="none" stroke="${col('SRC_CNR')}" stroke-width="4"/>${label(xC, y + 23, 'CNR', 12, 800)}`, xC - 24, y - 4, 48, 46);
  o += label(xE, y + 58, 'secours', 10, 600) + label(xC, y + 58, 'normal', 10, 600);
  o += L(xE, y + 38, xE, y + 70, 'SRC_EDF') + L(xC, y + 38, xC, y + 70, 'SRC_CNR');
  o += swSym('PL_A04', xE, y + 88, 'cb') + swSym('PL_B01', xC, y + 88, 'cb');
  o += label(xE - 22, y + 92, 'A04', 10, 700, 'end') + label(xC + 22, y + 92, 'B01', 10, 700, 'start');
  o += `<g><path d="M${xE + 30} ${y + 88}H${xC - 30}" stroke="#e5484d" stroke-width="2" stroke-dasharray="6 5"/>
    <rect x="${W / 2 - 170}" y="${y + 74}" width="340" height="28" rx="14" fill="var(--glass-strong)" stroke="#e5484d"/>${label(W / 2, y + 92, 'Interverrouillage : jamais CNR et EDF ensemble · permutation auto sur manque CNR', 10, 700)}</g>`;
  const yPL = y + 106;
  y += 150;
  // ------------------------------------------------ sections
  SECTIONS.forEach((S, si) => {
    const y0 = y + 40, yL = y0 + 70, yR = yL + 46;
    o += label(M, y0, S.title, 14, 800, 'start');
    const xL0 = M - 20, xL1 = W - M - 30, xR0 = M + 70, xR1 = W - M + 20;
    // câbles depuis le poste de livraison (bords gauche / droit)
    const xa = M - 10, xb = W - M + 10;
    o += `<path d="M${xE} ${yPL}V${yPL + 14 + si * 10}H${M - 45 - si * 12}V${y0 + 22}H${xa}V${yL - 30}" fill="none" stroke="${col('PL_A04')}" data-wire-id="PL_A04" stroke-width="3" stroke-dasharray="8 5"/>`;
    o += `<path d="M${xC} ${yPL}V${yPL + 14 + si * 10}H${W - M + 45 + si * 12}V${y0 + 22}H${xb}V${yR - 30}" fill="none" stroke="${col('PL_B01')}" data-wire-id="PL_B01" stroke-width="3" stroke-dasharray="8 5"/>`;
    o += swSym(S.aL, xa, yL - 18, 'sw') + L(xa, yL - 3, xa, yL, S.aL, 4) + swSym(S.aR, xb, yR - 18, 'sw') + L(xb, yR - 3, xb, yR, S.aR, 4);
    o += label(xa + 16, yL - 34, short(NODE[S.aL]).replace(/ \(.*/, ''), 10, 700, 'start') + label(xb - 16, yR - 34, short(NODE[S.aR]).replace(/ \(.*/, ''), 10, 700, 'end');
    // jeux de barres 20 kV (gauche en haut, droit en bas) + couplage
    o += hit(S.L, `<line x1="${xL0}" y1="${yL}" x2="${xL1}" y2="${yL}" stroke="${col(S.L)}" stroke-width="7"/>`, xL0, yL - 8, xL1 - xL0, 16);
    o += hit(S.R, `<line x1="${xR0}" y1="${yR}" x2="${xR1}" y2="${yR}" stroke="${col(S.R)}" stroke-width="7"/>`, xR0, yR - 8, xR1 - xR0, 16);
    o += label(xL0 + 4, yL - 10, 'demi-JdB gauche 20 kV', 10, 700, 'start', col(S.L)) + label(xR1 - 4, yR + 20, 'demi-JdB droit 20 kV', 10, 700, 'end', col(S.R));
    const xc = xL1 - 10, cOpen = !isClosed(S.cpl);
    o += hit(S.cpl, `<path d="M${xc} ${yL}V${yL + 12}" stroke="${col(S.cpl)}" stroke-width="4"/><path d="M${xc} ${yL + 12}L${xc + (cOpen ? 14 : 0)} ${yR - 12}" stroke="${col(S.cpl)}" stroke-width="4"/><path d="M${xc} ${yR - 12}V${yR}" stroke="${col(S.cpl)}" stroke-width="4"/>`, xc - 16, yL, 32, yR - yL)
      + label(xc - 18, (yL + yR) / 2 + 4, short(NODE[S.cpl]).split(' — ')[0], 10, 700, 'end');
    // blocs
    S.blocks.forEach((B, bi) => {
      const cx = M + BW * bi + BW / 2, xA = cx - 80, xB = cx + 80;
      const yC = yR + 44, yT = yC + 56, yQ = yT + 86, yBus = yQ + 42;
      const trA = B.kind === 'pair' ? (UP[B.qa] || [])[0].a : B.trs[0], trB = B.kind === 'pair' ? (UP[B.qb] || [])[0].a : B.trs[1];
      [[trA, xA, S.L, yL], [trB, xB, S.R, yR]].forEach(([tr, x, bus, yb]) => {
        if (!tr) return;
        const cell = (UP[tr] || [])[0].a;
        if (yb === yL) o += `<line x1="${x}" y1="${yR}" x2="${x}" y2="${yR}" stroke="var(--bg)" stroke-width="12"/>`; // pas de liaison au croisement du JdB droit
        o += L(x, yb, x, yC - 14, cell, 4) + (yb === yL ? `<rect x="${x - 6}" y="${yR - 6}" width="12" height="12" fill="var(--bg)"/>` + L(x, yR - 9, x, yR + 9, cell, 4) : '');
        o += swSym(cell, x, yC, 'cb') + L(x, yC + 14, x, yT - 17, tr, 4) + trSym(tr, x, yT);
        const tn = NODE[tr];
        o += label(x + (x < cx ? -22 : 22), yT + 6, short(tn), 11, 800, x < cx ? 'end' : 'start') + label(x + (x < cx ? -22 : 22), yT + 20, tn.kva || '', 9, 500, x < cx ? 'end' : 'start');
      });
      if (B.kind === 'pair') {
        o += L(xA, yT + 30, xA, yQ - 14, trA, 4) + L(xB, yT + 30, xB, yQ - 14, trB, 4);
        o += swSym(B.qa, xA, yQ, 'cb') + swSym(B.qb, xB, yQ, 'cb') + L(xA, yQ + 14, xA, yBus, B.qa, 4) + L(xB, yQ + 14, xB, yBus, B.qb, 4);
        o += hit(B.ba, `<line x1="${cx - 135}" y1="${yBus}" x2="${cx - 22}" y2="${yBus}" stroke="${col(B.ba)}" stroke-width="7"/>`, cx - 135, yBus - 8, 113, 16);
        o += hit(B.bb, `<line x1="${cx + 22}" y1="${yBus}" x2="${cx + 135}" y2="${yBus}" stroke="${col(B.bb)}" stroke-width="7"/>`, cx + 22, yBus - 8, 113, 16);
        if (NODE[B.qc]) { const op = !isClosed(B.qc), c = col(B.qc);
          o += hit(B.qc, `<path d="M${cx - 22} ${yBus}h8M${cx + 14} ${yBus}h8" stroke="${c}" stroke-width="4"/><rect x="${cx - 12}" y="${yBus - 10}" width="24" height="20" rx="3" fill="${op ? 'none' : c}" stroke="${c}" stroke-width="3" ${NODE[B.qc].conf !== 'confirme' ? 'stroke-dasharray="3 2"' : ''}/>`, cx - 22, yBus - 14, 44, 28); }
        o += `<g class="hit" data-id="${B.board}">${label(cx, yBus + 26, B.title, 14, 800)}<rect x="${cx - 120}" y="${yBus + 12}" width="240" height="20" fill="transparent"/></g>`;
        o += label(cx - 80, yBus - 10, 'A', 10, 800, 'middle', col(B.ba)) + label(cx + 80, yBus - 10, 'B', 10, 800, 'middle', col(B.bb));
        // tableaux / récepteurs alimentés par chaque demi-JdB
        [[B.ba, cx - 78], [B.bb, cx + 78]].forEach(([bus, x0]) => {
          const ds = (DOWN[bus] || []).map(e => NODE[e.b]).filter(d => d.t === 'dep');
          const fed = []; ds.forEach(d => { if (d.feeds && BOARD[d.feeds]) fed.push({ id: d.feeds, dep: d, name: BOARD[d.feeds].name }); else (DOWN[d.id] || []).forEach(e => { const n = NODE[e.b]; if (n.t === 'load') fed.push({ id: n.id, dep: d, name: n.label, load: true }); }); });
          let yy = yBus + 50;
          o += label(x0, yy - 6, `${ds.length} départ${ds.length > 1 ? 's' : ''}`, 9, 600, 'middle', 'var(--ink-3)');
          if (fed.length) o += L(x0, yBus + 4, x0, yy + (fed.length - 1) * 24 + 2, bus, 2);
          fed.slice(0, 8).forEach((f, i) => { const yy2 = yy + 6 + i * 24, lv = isLive(f.dep.id) && isClosed(f.dep.id), cc = lv ? '#12b76a' : '#e5484d';
            const nm = f.name.replace(/ — .*/, '').slice(0, 22);
            o += `<g class="hit" data-id="${f.id}"><path d="M${x0} ${yy2}h8" stroke="${cc}" stroke-width="2"/><rect x="${x0 + 8}" y="${yy2 - 9}" width="${nm.length * 6.2 + 14}" height="18" rx="9" fill="${lv ? 'rgba(18,183,106,.14)' : 'rgba(229,72,77,.12)'}" stroke="${cc}"/>
              <text x="${x0 + 15}" y="${yy2 + 4}" font-size="10" font-weight="700" fill="currentColor">${esc(nm)}</text><title>${esc(f.name)} — via ${esc(f.dep.label)}</title></g>`; });
          if (fed.length > 8) o += label(x0 + 12, yy + 8 * 24 + 6, `+ ${fed.length - 8} autres`, 9, 600, 'start', 'var(--ink-3)');
        });
      } else {
        [[trA, xA], [trB, xB]].forEach(([tr, x]) => { if (!tr) return; const ld = (DOWN[tr] || []).map(e => NODE[e.b])[0]; if (!ld) return;
          o += L(x, yT + 30, x, yQ + 20, tr, 4) + hit(ld.id, `<rect x="${x - 60}" y="${yQ + 20}" width="120" height="30" rx="15" fill="${isLive(ld.id) ? 'rgba(18,183,106,.14)' : 'rgba(229,72,77,.12)'}" stroke="${col(ld.id)}"/>${label(x, yQ + 39, ld.label.replace(/ \(.*/, '').replace(' — utilisation aval non documentée', '').slice(0, 20), 10, 700)}`, x - 60, yQ + 20, 120, 30); });
        o += label(cx, yBus + 26, B.title, 14, 800);
      }
    });
    y = y0 + 70 + 46 + 44 + 56 + 86 + 42 + 50 + 8 * 24 + 40;
  });
  return `<svg viewBox="0 0 ${W} ${y}" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system,Segoe UI,Arial,sans-serif">${o}</svg>`;
}
