// Test-Geruest: plan/index.html lokal in Chromium, GitHub-API aus einem Backup beantwortet (nichts wird geschrieben).
// Backup = Datei aus Einstellungen → Backup (meta.app 'Dienstplanung'). Enthaelt Personendaten: NIE ins Repo legen.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { chromium } from 'playwright-core';
const require = createRequire(import.meta.url);
export const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..');

export async function starten(backupPfad, monat, ich = ''){
  const files = JSON.parse(fs.readFileSync(backupPfad, 'utf8')).files;
  const srv = http.createServer((req, res) => {
    let p = decodeURIComponent(req.url.split('?')[0]);
    if(p.endsWith('/')) p += 'index.html';
    const f = path.join(REPO, p);
    if(!f.startsWith(REPO) || !fs.existsSync(f) || fs.statSync(f).isDirectory()){ res.statusCode = 404; return res.end(); }
    const typ = {'.html': 'text/html', '.js': 'text/javascript', '.wasm': 'application/wasm', '.svg': 'image/svg+xml'}[path.extname(f)];
    if(typ) res.setHeader('content-type', typ);
    res.end(fs.readFileSync(f));
  });
  await new Promise(r => srv.listen(0, r));
  const browser = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'});
  const ctx = await browser.newContext({serviceWorkers: 'block', viewport: {width: 1400, height: 900}});
  const erste = JSON.parse(JSON.stringify(files['plan/config.json'])).personen.find(p => p.rolle !== 'sek' && p.rolle !== 'pa');
  await ctx.addInitScript(([m, k]) => {
    localStorage.setItem('planung_zugang', JSON.stringify({repo: 'nomiknomik/tagesdoku-team', token: 'test'}));
    localStorage.setItem('planung_ich', JSON.stringify(k));
    localStorage.setItem('planung_monat', JSON.stringify(m));
    localStorage.setItem('planung_tab', JSON.stringify('plan'));
  }, [monat, ich || (erste && erste.k) || '']);
  const page = await ctx.newPage();
  page.on('dialog', d => d.accept());
  page.on('pageerror', e => console.error('Seitenfehler:', e.message));
  await page.route('**/*', async route => {
    const u = new URL(route.request().url());
    if(u.hostname === 'localhost') return route.continue();
    if(u.hostname !== 'api.github.com') return route.abort();
    const m = u.pathname.match(/\/contents\/(.+)$/);
    if(m && route.request().method() === 'GET'){
      const f = files[decodeURIComponent(m[1])];
      return f ? route.fulfill({status: 200, contentType: 'application/json',
        body: JSON.stringify({content: Buffer.from(JSON.stringify(f)).toString('base64'), sha: 'x'})}) : route.fulfill({status: 404, body: '{}'});
    }
    if(m) return route.fulfill({status: 409, body: '{}'});   // Schreiben immer abgelehnt
    if(/git\/trees/.test(u.pathname)) return route.fulfill({status: 200, contentType: 'application/json',
      body: JSON.stringify({tree: Object.keys(files).map(p => ({path: p}))})});
    return route.fulfill({status: 200, contentType: 'application/json', body: '{}'});
  });
  await page.goto(`http://localhost:${srv.address().port}/plan/`);
  await page.waitForFunction(() => typeof cfg !== 'undefined' && cfg.personen.length > 0, null, {timeout: 20000});
  await page.waitForTimeout(300);
  return {page, files, async stop(){ await browser.close(); srv.close(); }};
}

let highsP = null;
export async function loesen(lp, zeit = 60){
  highsP ||= require('highs')();
  return (await highsP).solve(lp, {time_limit: zeit, mip_rel_gap: 0, output_flag: false});
}

/* Im Browser: Monat vorbereiten (Kopie des Originals, optional teilweise geleert) und Hilfsfunktionen setzen */
export const VORBEREITEN = `async (m, anteilFest) => {
  ym = m; await ladeAlles();
  const pf = pfadDienst(m); window.__o ||= {};
  files[pf] ||= {data: {tage: {}}};
  __o[pf] ??= JSON.stringify(files[pf].data || {tage: {}});
  files[pf].data = JSON.parse(__o[pf]); files[pf].data.tage ||= {};
  if(anteilFest !== null) for(const s of Object.keys(files[pf].data.tage)) if(Math.random() >= anteilFest) delete files[pf].data.tage[s];
  const ps = diensttauglich(), Z = ziele(), ziel = {}, zw = {}, mehr = {};
  ps.forEach(p => { ziel[p.k] = Z[p.k].ziel; zw[p.k] = Z[p.k].zielWe; mehr[p.k] = {d: Z[p.k].e.expN !== undefined, w: Z[p.k].e.expWeBN !== undefined}; });
  const alle = Array.from({length: tageIm(m)}, (_, i) => ds(+m.slice(0, 4), +m.slice(5, 7), i + 1));
  const frei = alle.filter(s => !dienstVon(s));
  window.__c = {ps, ziel, zw, mehr, frei};
  window.__wert = plan => { SIM = {...plan}; const w = verbessern([], ps, ziel, zw, mehr); SIM = null; return w + frei.filter(s => !plan[s]).length * 1000; };
  /* rote Tags wie beim Einteilen (Tag kurz leer, erfasst auch die Folgetag-Regel), weiche wie in kosten (Tag belegt) */
  window.__verstoesse = plan => { SIM = {...plan}; const rot = [], weich = [];
    for(const s of alle){ const k = dienstVon(s); if(!k){ if(frei.includes(s)) rot.push(s.slice(8) + ' leer'); continue; }
      const p = person(k); if(!p) continue;
      SIM[s] = ''; bewerte(p, s).tags.filter(t => t[0] === 'r').forEach(t => rot.push(s.slice(8) + ' ' + k + ' ' + t[1])); SIM[s] = k;
      bewerte(p, s).tags.filter(t => t[0] === 'o').forEach(t => weich.push(s.slice(8) + ' ' + k + ' ' + t[1])); }
    SIM = null; return {rot, weich}; };
  return {frei: frei.length};
}`;
