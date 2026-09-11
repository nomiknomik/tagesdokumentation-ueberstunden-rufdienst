import base64

with open("pdf_b64.txt") as f:
    b64 = f.read().strip()

html_template = r'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Tagesdokumentation – Überstunden &amp; Rufdienst</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js"></script>
<style>
  :root{
    --navy:#1f3864; --yellow:#fdf1cf; --grey:#e8e8e8; --border:#999;
  }
  *{box-sizing:border-box; font-family:Arial, Helvetica, sans-serif;}
  body{margin:0; padding:16px; background:#f2f2f2; color:#111;}
  .sheet{max-width:900px; margin:0 auto; background:#fff; border:1px solid #ccc;}
  .header{background:var(--navy); color:#fff; padding:10px 14px;}
  .header h1{margin:0; font-size:18px;}
  .header p{margin:4px 0 0; font-size:11px; font-style:italic; opacity:.9;}
  .block{padding:10px 14px;}
  table.grid{width:100%; border-collapse:collapse; margin-bottom:10px;}
  table.grid th{background:var(--navy); color:#fff; font-size:11px; padding:5px; border:1px solid #345; text-align:left;}
  table.grid td{border:1px solid var(--border); padding:2px; vertical-align:middle;}
  .label{font-weight:bold; font-size:12px; padding:4px 6px; white-space:nowrap;}
  input, select{width:100%; border:none; background:var(--yellow); padding:5px 4px; font-size:12px; line-height:1.3; height:26px; box-sizing:border-box; font-family:Arial, Helvetica, sans-serif;}
  input[type=date], input[type=time]{font-size:12px;}
  .date-wrap{display:flex; align-items:stretch; gap:2px;}
  .date-wrap input{flex:1;}
  .date-wrap button{width:26px; height:26px; padding:0; font-size:14px; line-height:1; background:var(--navy); color:#fff; border:none; border-radius:3px; cursor:pointer;}
  .date-wrap button:hover{background:#16294a;}
  input.ro{background:var(--grey);}
  input:focus, select:focus{outline:2px solid var(--navy);}
  .section-title{background:#dbe4f0; font-weight:bold; padding:5px 8px; font-size:13px; margin:10px 0 0;}
  .row-nr{text-align:center; font-size:12px; background:#f5f5f5;}
  .rowcalc{background:#f0f0f0 !important;}
  .footer{padding:14px; text-align:center;}
  button{background:var(--navy); color:#fff; border:none; padding:10px 22px; font-size:14px; border-radius:4px; cursor:pointer;}
  button:hover{background:#16294a;}
  small{color:#555;}
</style>
</head>
<body>
<div class="sheet">
  <div class="header">
    <h1>Tagesdokumentation: Überstunden und Inanspruchnahme im Rufdienst</h1>
    <p>Ärztlicher Dienst – pro Kalendertag ein Bogen. Gelbe Felder ausfüllen, graue Felder berechnen sich automatisch.</p>
  </div>

  <div class="block">
    <table class="grid">
      <tr>
        <td class="label" style="width:16%">Name, Vorname:</td>
        <td style="width:34%"><input class="ro" id="name_vorname" value="Zabelyshenskiy, Alexander" readonly></td>
        <td class="label" style="width:10%">Datum:</td>
        <td style="width:40%">
          <div class="date-wrap">
            <button type="button" id="datePrev" title="Vorheriger Tag">&#8249;</button>
            <input type="date" id="datum">
            <button type="button" id="dateNext" title="Nächster Tag">&#8250;</button>
          </div>
        </td>
      </tr>
      <tr>
        <td class="label">Personalnummer:</td>
        <td><input class="ro" id="personalnummer" value="421761" readonly></td>
        <td class="label">Klinik / Abteilung:</td>
        <td><input class="ro" id="klinik_abteilung" value="Allgemein-, Viszeral- u. Gefäßchirurgie" readonly></td>
      </tr>
      <tr>
        <td class="label">Funktion / Position:</td>
        <td><input class="ro" id="funktion" value="Oberarzt" readonly></td>
        <td class="label">Dienstart:</td>
        <td>
          <select id="dienstart">
            <option value=""></option>
            <option>Regeldienst</option>
            <option>Rufdienst (Werktag)</option>
            <option>Rufdienst (Wochenende/Feiertag)</option>
            <option>Bereitschaftsdienst</option>
            <option>Spätdienst</option>
            <option>Sonstiges</option>
          </select>
        </td>
      </tr>
      <tr>
        <td class="label">Zeitvorlage:</td>
        <td colspan="3">
          <select id="zeitvorlage">
            <option value="">– Schnellauswahl für Dienstbeginn/-ende –</option>
            <option value="amb2">amb2 (Mo, 07:10–16:05)</option>
            <option value="amb4">amb4 (07:25–16:05)</option>
            <option value="ZD1">ZD1 (Mo–Do, 11:00–18:00)</option>
            <option value="ZD2">ZD2 (11:00–18:00)</option>
            <option value="RBD">RBD (Sa, 09:00–10:30 + RBA)</option>
            <option value="RBD2">RBD2 (So/Feiertag, wie Sa)</option>
          </select>
        </td>
      </tr>
      <tr>
        <td class="label">FRN:</td>
        <td colspan="3" style="background:#f5f5f5;">
          <label style="font-weight:normal; font-size:12px;">
            <input type="checkbox" id="frn_check" style="width:auto; vertical-align:middle;">
            frei nach Dienst (Nachtoperation – normale Arbeitszeit trotzdem eintragen, kein Minusstunden-Abzug; wird als Bemerkung vermerkt)
          </label>
        </td>
      </tr>
    </table>

    <div class="section-title">1. Dienstzeit und Überstunden</div>
    <table class="grid">
      <tr>
        <th style="width:15%">Dienstbeginn (hh:mm)</th>
        <th style="width:15%">planmäßiges Dienstende</th>
        <th style="width:15%">tatsächliches Dienstende</th>
        <th style="width:15%">Überstunden (Std.)</th>
        <th style="width:40%">Grund der Überstunden</th>
      </tr>
      <tr>
        <td><input type="time" id="dienstbeginn"></td>
        <td><input type="time" id="plan_dienstende"></td>
        <td><input type="time" id="tats_dienstende"></td>
        <td><input class="rowcalc" id="ueberstunden_std" readonly></td>
        <td>
          <select id="grund_ueberstunden">
            <option value=""></option>
            <option>Notfall / Notoperation</option>
            <option>OP-Verlängerung</option>
            <option>Aufnahme / Ambulanz</option>
            <option>Konsil / Anforderung anderer Abteilung</option>
            <option>Personalausfall / Unterbesetzung</option>
            <option>Übergabe / Nachbereitung / Dokumentation</option>
            <option>Patienten-/Angehörigengespräch</option>
            <option>Angeordnete Zusatzaufgabe</option>
            <option>Sonstiges (bitte erläutern)</option>
        <td colspan="4"><input id="erlaeuterung"></td>
      </tr>
      <tr>
        <td class="label">Überstunden angeordnet<br>durch (Name, Funktion):</td>
        <td colspan="4"><input id="angeordnet_durch"></td>
      </tr>
    </table>

    <div class="section-title">2. Inanspruchnahme im Rufdienst (jeder Einsatz einzeln)</div>
    <table class="grid" id="rufdienst-table">
      <tr>
        <th style="width:4%">Nr.</th>
        <th style="width:12%">Beginn (hh:mm)</th>
        <th style="width:12%">Ende (hh:mm)</th>
        <th style="width:10%">Dauer (Std.)</th>
        <th style="width:20%">Art der Inanspruchnahme</th>
        <th style="width:32%">Grund / Anlass</th>
        <th style="width:10%">Fall-Nr. (optional)</th>
      </tr>
      <!--ROWS-->
    </table>
    <table class="grid">
      <tr>
        <td class="label" style="width:25%">Summe Inanspruchnahme (Std.):</td>
        <td style="width:25%"><input class="rowcalc" id="summe_inanspruchnahme" readonly></td>
        <td class="label" style="width:25%">Anzahl der Einsätze:</td>
        <td style="width:25%"><input class="rowcalc" id="anzahl_einsaetze" readonly></td>
      </tr>
    </table>

    <div class="section-title">3. Zusammenfassung und Ausgleich</div>
    <table class="grid">
      <tr>
        <td class="label" style="width:25%">Überstunden am Tag gesamt (Std.):</td>
        <td style="width:25%"><input class="rowcalc" id="ueberstunden_gesamt" readonly></td>
        <td class="label" style="width:25%">Ruhezeit von 11 Std. eingehalten (§ 5 ArbZG)?</td>
        <td style="width:25%">
          <select id="ruhezeit_eingehalten">
            <option value=""></option>
            <option>Ja</option>
            <option>Nein</option>
          </select>
        </td>
      </tr>
      <tr>
        <td class="label">Gewünschter Ausgleich:</td>
        <td><input id="gewuenschter_ausgleich"></td>
        <td class="label">geplanter Ausgleichstag:</td>
        <td><input type="date" id="geplanter_ausgleichstag"></td>
      </tr>
    </table>
  </div>

  <div class="footer">
    <button id="downloadBtn">PDF ausfüllen &amp; herunterladen</button>
    <p><small>Erzeugt das offizielle Formular als ausgefüllte PDF-Datei (Original-Layout unverändert).</small></p>
  </div>
</div>

<script>
const PDF_B64 = "__PDF_B64__";

// Rufdienst-Zeilen dynamisch erzeugen (1-8)
const tbody = document.getElementById('rufdienst-table');
const artOptions = ["", "telefonisch (von zu Hause)", "Präsenz im Haus", "Operation / Eingriff", "Sonstiges"];
for (let i = 1; i <= 8; i++) {
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td class="row-nr">${i}</td>
    <td><input type="time" id="rufdienst_${i}_beginn" class="rd-beginn" data-i="${i}"></td>
    <td><input type="time" id="rufdienst_${i}_ende" class="rd-ende" data-i="${i}"></td>
    <td><input class="rowcalc" id="rufdienst_${i}_dauer" readonly></td>
    <td><select id="rufdienst_${i}_art">${artOptions.map(o=>`<option>${o}</option>`).join('')}</select></td>
    <td><input id="rufdienst_${i}_grund_anlass"></td>
    <td><input id="rufdienst_${i}_fallnr"></td>
  `;
  tbody.appendChild(tr);
}

function timeToDec(t){
  if(!t) return null;
  const [h,m] = t.split(':').map(Number);
  return h + m/60;
}
function fmt(dec){
  if (dec === null || isNaN(dec)) return "";
  return dec.toFixed(2);
}

function recalcDuty(){
  const plan = timeToDec(document.getElementById('plan_dienstende').value);
  const tats = timeToDec(document.getElementById('tats_dienstende').value);
  let diff = null;
  if (plan !== null && tats !== null){
    diff = tats - plan;
  }
  document.getElementById('ueberstunden_std').value = diff !== null ? fmt(diff) : "";
  recalcTotal();
}

function recalcRow(i){
  const b = timeToDec(document.getElementById(`rufdienst_${i}_beginn`).value);
  const e = timeToDec(document.getElementById(`rufdienst_${i}_ende`).value);
  let dauer = null;
  if (b !== null && e !== null){
    dauer = e - b;
    if (dauer < 0) dauer += 24;
  }
  document.getElementById(`rufdienst_${i}_dauer`).value = dauer !== null ? fmt(dauer) : "";
  recalcSumme();
}

function recalcSumme(){
  let summe = 0, anzahl = 0;
  for (let i=1;i<=8;i++){
    const v = document.getElementById(`rufdienst_${i}_dauer`).value;
    if (v){ summe += parseFloat(v); anzahl++; }
  }
  document.getElementById('summe_inanspruchnahme').value = anzahl ? fmt(summe) : "";
  document.getElementById('anzahl_einsaetze').value = anzahl || "";
  recalcTotal();
}

function recalcTotal(){
  const ue = parseFloat(document.getElementById('ueberstunden_std').value) || 0;
  document.getElementById('ueberstunden_gesamt').value = ue ? fmt(ue) : "";
}

// Datum: Standard = gestern, mit Vor/Zurück-Pfeilen
function toISODate(d){
  const pad = n => String(n).padStart(2,'0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
}
const datumInput = document.getElementById('datum');
const yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);
datumInput.value = toISODate(yesterday);

function shiftDate(days){
  const cur = datumInput.value ? new Date(datumInput.value + 'T00:00:00') : new Date();
  cur.setDate(cur.getDate() + days);
  datumInput.value = toISODate(cur);
}
document.getElementById('datePrev').addEventListener('click', () => shiftDate(-1));
document.getElementById('dateNext').addEventListener('click', () => shiftDate(1));

document.getElementById('plan_dienstende').addEventListener('input', recalcDuty);
document.getElementById('tats_dienstende').addEventListener('input', recalcDuty);
document.querySelectorAll('.rd-beginn, .rd-ende').forEach(el=>{
  el.addEventListener('input', ()=>recalcRow(el.dataset.i));
});

// Feste Zeiten je Dienstart automatisch eintragen
const DIENSTART_ZEITEN = {
  "amb2": ["07:10", "16:05"],
  "amb4": ["07:25", "16:05"],
  "ZD1":  ["11:00", "18:00"],
  "ZD2":  ["11:00", "18:00"],
  "RBD":  ["09:00", "10:30"],
  "RBD2": ["09:00", "10:30"],
};
document.getElementById('zeitvorlage').addEventListener('change', (e) => {
  const zeiten = DIENSTART_ZEITEN[e.target.value];
  if (zeiten) {
    document.getElementById('dienstbeginn').value = zeiten[0];
    document.getElementById('plan_dienstende').value = zeiten[1];
    recalcDuty();
  }
  if (e.target.value === 'RBD' || e.target.value === 'RBD2') {
    const err = document.getElementById('erlaeuterung');
    if (!err.value.includes('darüber hinaus RBA')) {
      err.value = (err.value ? err.value + ' – ' : '') + 'darüber hinaus RBA in Abschnitt 2 erfassen';
    }
  }
});

// FRN-Hinweis in Erläuterung übernehmen
document.getElementById('frn_check').addEventListener('change', (e) => {
  const err = document.getElementById('erlaeuterung');
  const marker = 'FRN – frei nach Dienst';
  if (e.target.checked) {
    if (!err.value.includes(marker)) {
      err.value = (err.value ? err.value + ' – ' : '') + marker;
    }
  } else {
    err.value = err.value.replace(marker, '').replace(/^ – | – $/g, '').trim();
  }
});

document.getElementById('downloadBtn').addEventListener('click', async () => {
  try {
    const { PDFDocument } = PDFLib;
    const bytes = Uint8Array.from(atob(PDF_B64), c => c.charCodeAt(0));
    const pdfDoc = await PDFDocument.load(bytes);
    const form = pdfDoc.getForm();

    const fieldIds = [
      "name_vorname","personalnummer","funktion","klinik_abteilung","datum","dienstart",
      "dienstbeginn","plan_dienstende","tats_dienstende","ueberstunden_std","grund_ueberstunden",
      "erlaeuterung","angeordnet_durch",
      "summe_inanspruchnahme","anzahl_einsaetze",
      "ueberstunden_gesamt","ruhezeit_eingehalten","gewuenschter_ausgleich","geplanter_ausgleichstag"
    ];
    for (let i=1;i<=8;i++){
      ["beginn","ende","dauer","art","grund_anlass","fallnr"].forEach(c=>{
        fieldIds.push(`rufdienst_${i}_${c}`);
      });
    }

    fieldIds.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      let val = el.value || "";
      if (el.type === 'date' && val) {
        const [y,m,d] = val.split('-');
        val = `${d}.${m}.${y}`;
      }
      try {
        const field = form.getTextField(id);
        field.setFontSize(id === 'klinik_abteilung' ? 6.5 : 8);
        field.setText(val);
      } catch(e) { /* Feld nicht gefunden - ignorieren */ }
    });

    form.updateFieldAppearances();
    const outBytes = await pdfDoc.save();
    const blob = new Blob([outBytes], {type:'application/pdf'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const datum = document.getElementById('datum').value || 'ausgefuellt';
    a.href = url;
    a.download = `Tagesdokumentation_${datum}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    alert('Fehler beim Erzeugen der PDF: ' + err.message);
    console.error(err);
  }
});
</script>
</body>
</html>
'''

html = html_template.replace("__PDF_B64__", b64)
with open("/mnt/user-data/outputs/tagesdokumentation_erfassung.html", "w", encoding="utf-8") as f:
    f.write(html)

print("done", len(html))
