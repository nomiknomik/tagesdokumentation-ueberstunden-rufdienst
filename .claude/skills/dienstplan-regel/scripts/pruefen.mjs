// Abnahme fuer Aenderungen an bewerte()/verbessern()/mipModell():
//   node pruefen.mjs <backup.json> [Monate, z. B. 2026-10,2026-11] [Zufallsfaelle je Monat, Standard 3]
// Je Monat: ganzer Monat leer + Zufallsfaelle (20-70 % der Tage fest). Prueft
//   A) Modellwert (HiGHS + konst) == App-Wert verbessern([])   -> sonst FEHLER (Modell und App weichen ab)
//   B) Solver nie schlechter als Heuristik, ausser die Heuristik bricht eine rote Regel  -> sonst FEHLER
//   C) Solver-Plan ohne rote Regel (ausser durch feste Tage erzwungen)                    -> Hinweis
//   D) echte App: autoVerteilen() mit Solver liefert denselben Wert, Toast „bestmöglich“  -> sonst FEHLER
// Ergebnis-Tabelle auf der Konsole, Exit-Code 1 bei FEHLER.
import { starten, loesen, VORBEREITEN } from './harness.mjs';
const [backup, monArg, nArg] = process.argv.slice(2);
if(!backup){ console.error('Aufruf: node pruefen.mjs <backup.json> [Monate] [Zufallsfaelle]'); process.exit(2); }
const h = await starten(backup, '2026-01');
/* GEWICHTE='{"nogo":200,...}' testet geänderte Regel-Gewichte (cfg.gewichte, s. GEW_STD in plan/index.html) */
if(process.env.GEWICHTE) h.files['plan/config.json'].gewichte = JSON.parse(process.env.GEWICHTE);
const MON = monArg ? monArg.split(',') : [...new Set(Object.keys(h.files).map(p => (p.match(/^plan\/dienst\/(\d{4}-\d{2})\.json$/) || [])[1]).filter(Boolean))].sort().slice(-5);
const N = +(nArg ?? 3);
let fehler = 0; const zeilen = [];
const heuristik = () => h.page.evaluate(async () => {
  const fest = {}, orig = window.einteilen, v = cfg.verfahren; window.einteilen = (s, k) => { fest[s] = k; };
  cfg.verfahren = 'heuristik'; window.AV_TEST = {zeit: 2000};
  try{ await autoVerteilen(); }finally{ window.einteilen = orig; cfg.verfahren = v; delete window.AV_TEST; }
  return {wert: __wert(fest), v: __verstoesse(fest)};
});
for(const m of MON) for(let i = 0; i <= N; i++){
  const anteil = i === 0 ? 0 : 0.2 + Math.random() * 0.5;
  const info = await h.page.evaluate(`(${VORBEREITEN})('${m}', ${anteil})`);
  if(!info.frei) continue;
  const mod = await h.page.evaluate(() => { const r = mipModell(__c.frei, __c.ps, __c.ziel, __c.zw, __c.mehr); window.__mod = r; return {lp: r.lp, konst: r.konst}; });
  const t0 = Date.now(), sol = await loesen(mod.lp), sek = (Date.now() - t0) / 1000;
  const r = await h.page.evaluate(cols => { const plan = __mod.lesen(cols); return {wert: __wert(plan), v: __verstoesse(plan)}; }, sol.Columns);
  const heu = await heuristik();
  const modell = sol.ObjectiveValue + mod.konst, folgetag = Math.round(r.wert - modell) === -900 * Math.round((r.wert - modell) / -900);
  const A = Math.abs(modell - r.wert) < 0.5 || (folgetag && Math.abs(modell - r.wert) >= 899);   // 900 = absichtlicher Folgetag-Verstoss (nicht in verbessern())
  const B = r.wert <= heu.wert + 0.5 || heu.v.rot.length > 0;
  const ok = sol.Status === 'Optimal' && A && B;
  if(!ok) fehler++;
  zeilen.push({Monat: m, fest: i === 0 ? '0 %' : Math.round(anteil * 100) + ' %', frei: info.frei, Status: sol.Status, s: +sek.toFixed(2),
    Modell: +modell.toFixed(2), App: r.wert, Heuristik: heu.wert, 'rot Solver': r.v.rot.length, 'weich Solver': r.v.weich.length,
    'rot Heur.': heu.v.rot.length, Urteil: ok ? 'OK' : !A ? 'FEHLER Modell≠App' : !B ? 'FEHLER Heuristik besser' : 'FEHLER ' + sol.Status});
  if(r.v.rot.length) console.log(`  Hinweis ${m}: Solver-Plan mit roter Regel (feste Tage?): ${r.v.rot.join('; ')}`);
  if(!B || !A) console.log(`  ${m}: Heuristik rot: ${heu.v.rot.join('; ') || '-'} | Solver weich: ${r.v.weich.join('; ') || '-'}`);
}
/* D) echte App mit Solver (ganzer Monat leer) */
for(const m of MON){
  const info = await h.page.evaluate(`(${VORBEREITEN})('${m}', 0)`);
  if(!info.frei) continue;
  const d = await h.page.evaluate(async () => { const fest = {}, orig = window.einteilen; window.einteilen = (s, k) => { fest[s] = k; };
    cfg.verfahren = 'mip'; const t0 = performance.now(); try{ await autoVerteilen(); }finally{ window.einteilen = orig; }
    return {wert: __wert(fest), s: (performance.now() - t0) / 1000, toast: (document.querySelector('.toast') || {}).textContent || ''}; });
  const soll = zeilen.find(z => z.Monat === m && z.fest === '0 %');
  const ok = /bestmöglich/.test(d.toast) && soll && Math.abs(d.wert - soll.App) < 0.5;
  if(!ok) fehler++;
  console.log(`App ${m}: ${d.wert} in ${d.s.toFixed(2)} s – ${ok ? 'OK' : 'FEHLER'} („${d.toast}“)`);
}
console.table(zeilen);
console.log(fehler ? `${fehler} FEHLER` : 'Alles OK');
await h.stop();
process.exit(fehler ? 1 : 0);
