# Projekt: Tagesdokumentation Überstunden & Rufdienst (Klinikum Freudenstadt)

## Kontext
Dr. Alexander Zabelyshenskiy (Oberarzt, Allgemein-, Viszeral- und Gefäßchirurgie,
Klinikum Landkreis Freudenstadt) muss täglich einen offiziellen Klinikum-Bogen
("Tagesdokumentation: Überstunden und Inanspruchnahme im Rufdienst") ausfüllen.
Das Original-PDF-Layout/der Text darf **nicht verändert** werden (offizielles
Dokument, Weiterleitung an Personalabteilung + Chefarzt-Unterschrift).

## Ziel
1. **Ausfüllbare PDF** (`Tagesdokumentation_Ueberstunden_Rufdienst_ausfuellbar.pdf`):
   Original-PDF + echte, interaktive AcroForm-Textfelder (keine reinen Text-Overlays).
   - Kopfteil fest ausgefüllt & schreibgeschützt: Name/Vorname, Personalnummer,
     Funktion/Position, Klinik/Abteilung (**ohne** "Klinikum Freudenstadt" im Wert,
     nur "Allgemein-, Viszeral- u. Gefäßchirurgie")
   - Datum, Dienstart sowie alle Zeiteinträge/Rufdienst-Zeilen/Zusammenfassung:
     leer, direkt klickbar ausfüllbar
   - Dienstart/Grund der Überstunden/Art der Inanspruchnahme: exakter Wortlaut
     aus der Original-Formular-Legende (nicht verändern!)

2. **HTML-Erfassungstool** (`tagesdokumentation_erfassung.html`):
   Eigenständige HTML-Datei mit eingebettetem Base64-PDF-Template + pdf-lib
   (CDN). Erfasst Tageswerte komfortabel im Browser, berechnet automatisch
   (Überstunden, Dauer je Rufdienst-Zeile, Summe, Anzahl Einsätze) und füllt
   beim Klick auf "PDF ausfüllen & herunterladen" die echten PDF-Formularfelder
   aus (per pdf-lib `form.getTextField(id).setText(...)`), dann Download.
   - Zusätzliches Feld "Zeitvorlage" (NICHT Teil des offiziellen Dienstart-Felds!)
     füllt bei Auswahl automatisch Dienstbeginn/planmäßiges Dienstende:
     - `amb2`: Mo, 07:10–16:05
     - `amb4`: 07:25–16:05
     - `ZD1`: Mo–Do, 11:00–18:00
     - `ZD2`: 11:00–18:00
     - `RBD`: nur Sa, 09:00–10:30 (danach zählt als RBA → Hinweis in Erläuterung)
     - `RBD2`: nur So/Feiertag, Arbeitszeit wie Sa
   - `FRN` (frei nach Dienst, nach Nachtoperation): Checkbox setzt Bemerkungstext
     "FRN – frei nach Dienst" in Erläuterung. **Normale Arbeitszeit wird trotzdem
     eingetragen** (kein Minusstunden-Abzug) – das ist Absicht, nicht korrigieren!
   - `RBA` = Aktivzeit (von/bis), `RBT` = Telefonat (von/bis) – das sind KEINE
     Dienstart-Optionen, sondern beschreiben Einsatzarten im Rufdienst
     (Abschnitt 2). Das Dropdown "Art der Inanspruchnahme" nutzt aber den
     offiziellen Formular-Wortlaut (telefonisch/Präsenz im Haus/Operation/Sonstiges).
   - Datum-Feld: Default = **gestriges Datum**, mit ‹ › Pfeilen zum Vor-/Zurückblättern

## Wichtige technische Learnings (nicht wiederholen!)
- **pypdf-Bug**: `TextStringObject` escaped bei `/DA`-Strings jedes
  Nicht-alphanumerische Zeichen als Oktal (`/` → `\057`). pdf-lib kann das beim
  Parsen des DA-Strings nicht auflösen ("No Tf operator found") bzw. rendert
  dann mit falscher/riesiger Schriftgröße. **Fix**: `/DA` als `ByteStringObject`
  (Hex-String) statt `TextStringObject` schreiben.
- **AcroForm braucht `/DR` (Default Resources) mit Font-Ressource `/Helv`**,
  sonst kann pdf-lib `setFontSize()` nicht anwenden.
- **Fehlendes `/BS` (Border Style, W:0) bei editierbaren Feldern**: Edge und
  PDF24 (beide nutzen die Rendering-Engine "pdfium") zeichnen dann einen
  sichtbaren Standard-Rahmen um jedes Feld, der versetzt zu den Tabellenlinien
  liegt ("alles verschoben"). Poppler zeigt diesen Fehler NICHT an – bei
  Sichtprüfung also nicht nur mit poppler/pdf2image testen, sondern wenn
  möglich auch mit einem pdfium-basierten Viewer. **Fix**: `/BS {W:0}` auf
  JEDES Feld setzen (nicht nur readonly-Felder), plus leeres `/MK`.
- **Feldkoordinaten NIEMALS aus Textposition/Augenmaß schätzen** – das führt zu
  Versätzen zwischen Feld und tatsächlicher Zelle (z. B. Name/Personalnummer-Bug).
  **Fix**: `page.get_drawings()` (PyMuPDF) nutzen, um die echten Fill-Rechtecke
  und Trennlinien der Vorlage auszulesen, und Feldkoordinaten exakt daran
  ausrichten. Beispiel-Workflow:
  ```python
  import fitz
  doc = fitz.open(SRC)
  page = doc[0]
  for p in page.get_drawings():
      r = p['rect']
      print(r.x0, r.y0, r.x1, r.y1, 'FILL' if p.get('fill') else 'LINE')
  ```
  Damit lassen sich Zellgrenzen (farbige Fill-Rechtecke) UND Trennlinien
  (schmale Linien-Rechtecke) exakt bestimmen – zuverlässiger als
  `extract_form_structure.py`-Zeilenschätzungen oder Label-Textpositionen.
- Beim Erzeugen der Feld-Koordinaten immer die **Linien-/Zeilengrenzen aus
  `extract_form_structure.py` bzw. `page.search_for()` (PyMuPDF)** nur als
  groben Anhaltspunkt nehmen, NICHT als finale Wahrheit – siehe oben.
- Koordinatensystem in `add_fields.py`: top-down (y=0 oben), Konvertierung nach
  PDF-Standard (y=0 unten) über `top_rect_to_pdf()`, `PAGE_H = 841.89`.
- Kein Acrobat/pikepdf-Formularfeld-Ersteller in pypdf vorhanden – Felder werden
  manuell als `/Widget`-Annotation-Dictionaries gebaut (siehe `add_fields.py`).
- **Vor jeder Auslieferung**: mit `node` + `pdf-lib` testweise Felder befüllen
  und per `pdf2image` rendern (siehe `test_final2.pdf`-Workflow im Verlauf),
  UND den Nutzer explizit bitten, in Edge/PDF24 zu prüfen (pdfium-Rendering
  weicht von poppler ab).

## Status: verifiziert (Stand: aktueller Commit)
Alle Feldkoordinaten wurden gegen die exakten Vektor-Zellgrenzen der
Original-PDF geprüft (Kopfteil, Abschnitt 1, 2, 3). Kein bekannter
Layout-Bug mehr offen. Bei künftigen Änderungen an Koordinaten immer
`page.get_drawings()` verwenden (siehe oben), nicht schätzen.

## Dateien in diesem Repo
- `add_fields.py` – Python-Skript: nimmt Original-PDF, fügt 67 AcroForm-Felder
  hinzu, schreibt `Tagesdokumentation_Ueberstunden_Rufdienst_ausfuellbar.pdf`
- `build_html.py` – Python-Skript: baut `tagesdokumentation_erfassung.html`
  (bettet die ausgefüllte PDF als Base64 ein)
- `Tagesdokumentation_Ueberstunden_Rufdienst_ausfuellbar.pdf` – fertiges Ergebnis
- `tagesdokumentation_erfassung.html` – fertiges Ergebnis
- `Tagesdokumentation_Original.pdf` – unverändertes Original (Referenz)

## Offene Punkte / mögliche nächste Schritte
- Ruhezeit-Check (§ 5 ArbZG, 11 Std.) ist aktuell nur ein manuelles
  Ja/Nein-Dropdown, keine Automatik
- "Überstunden am Tag gesamt" übernimmt aktuell nur `ueberstunden_std`
  (Dienstzeit-Überstunden), keine Verrechnung mit Rufdienst-Summe – ggf. mit
  Nutzer klären, ob das so gewünscht ist

## Update (Redesign Dienstart + Cookies)
- **Zeitvorlage-Feld entfernt** (war redundant): Die Wochentags-Varianten sind jetzt
  direkt im offiziellen `dienstart`-Dropdown enthalten:
  - `Regeldienst (Montag)` → amb2 (07:10–16:05)
  - `Regeldienst` → amb4 (07:25–16:05)
  - `Rufdienst (Mo–Do)` → ZD1 (11:00–18:00)
  - `Rufdienst` → ZD2 (11:00–18:00)
  - `Rufdienst (Samstag)` → RBD (09:00–10:30, + Hinweis "RBA in Abschnitt 2 erfassen")
  - `Rufdienst (Sonntag/Feiertag)` → RBD2 (wie Samstag)
  Auswahl füllt automatisch Dienstbeginn/planmäßiges Dienstende via `data-start`/`data-end`
  Attributen auf den `<option>`-Elementen.
- **Cookie-Persistenz**: Alle editierbaren Felder (nicht: readonly/`.ro`/`.rowcalc`)
  werden bei jedem `input`/`change` in einem JSON-Cookie (`tagesdoku_formdata`,
  90 Tage) gespeichert und beim Laden der Seite automatisch wiederhergestellt
  (`loadFormFromCookie()`), inkl. Checkbox-Support (FRN).

## Zwei parallele Dateien – IMMER BEIDE pflegen!
- `tagesdokumentation_erfassung.html` (Root) – Desktop-Tool, wird per GitHub
  Pages unter `https://nomiknomik.github.io/tagesdokumentation-ueberstunden-rufdienst/tagesdokumentation_erfassung.html`
  ausgeliefert. Hat eigene Kopie der Dienstart-Optionsliste (`DIENSTART_OPTIONS`).
- `app/index.html` – PWA-Variante (separates Manifest/Service Worker), hat
  EIGENE, unabhängige Kopie der gleichen Logik (`amb2`/`amb4`/... Objekt).
  Änderungen an Dienstart-Labels, Zeiten, Cookie-Verhalten etc. müssen in
  BEIDEN Dateien parallel gemacht werden – es gibt keine gemeinsame
  JS-Datei/kein Include.

## GitHub-Push-Learning (Fehlerquelle!)
- Beim Batch-Push mehrerer Dateien per Shell-Loop mit `curl -d "{...}"` kann
  bei großen Dateien (hier: `app/index.html` mit eingebettetem Base64-PDF,
  >100 KB) die Fehlermeldung `curl: Argument list too long` auftreten. Die
  Shell bricht dabei NICHT den ganzen Loop ab, sondern nur den einzelnen
  Befehl – das kann dazu führen, dass eine Datei im Loop übersprungen wird,
  obwohl der Log scheinbar "OK" für eine andere Datei zeigt. **Fix**: Bei
  Dateien >~50 KB immer den Payload zuerst per `python3` in eine JSON-Datei
  schreiben (`base64.b64encode` + `json.dump`) und dann
  `curl --data @payload.json` verwenden, NIE `-d "$(base64 ...)"` inline.
  Nach jedem Push den Commit-Diff prüfen (`GET /commits/{sha}` → `files[]`),
  um zu verifizieren, welche Datei wirklich verändert wurde – nicht nur auf
  die "OK"-Ausgabe verlassen.
- GitHub Pages braucht nach einem Push ca. 30–60 Sekunden zum Neu-Deployen;
  ein sofortiger Fetch der Pages-URL kann noch den alten Stand zeigen.

## Offene, noch nicht umgesetzte Nutzer-Anforderungen (Stand 11.09.2026)
1. **Cookie-Speicherung einschränken**: Ab dem Feld "Dienstart" und allen
   darunterliegenden Feldern (Dienstzeit-Block, 8 Rufdienst-Zeilen,
   Zusammenfassung/Ausgleich) soll NICHT mehr automatisch in Cookies
   gespeichert werden – hat sich in der Praxis nicht bewährt (Grund: soll
   pro Tag neu/leer starten). Nur die Kopfdaten (Name, Personalnummer,
   Funktion, Klinik/Abteilung) sollen weiterhin persistiert werden.
   Betrifft `saveFormToCookie()`/`loadFormFromCookie()` in BEIDEN Dateien
   (Selektor `.block` müsste auf einen engeren Container eingeschränkt
   werden, der nur die Kopfdaten umfasst).
2. **Minusstunden-Logik**: Wenn tatsächliches Dienstende < geplantes
   Dienstende ist (d. h. früher gegangen als geplant), soll das Feld
   "Überstunden (Std.)" NEGATIV befüllt werden (Minusstunden), nicht nur
   bei Überschreitung positiv rechnen. Aktuelle Berechnung (Stand
   Screenshot-Beispiel: Beginn 07:25, geplant 16:05, tatsächlich 11:26 →
   müsste -4:39 Std. ergeben statt vermutlich 0 oder falschem Wert).
   Muss in der Überstunden-Berechnungsfunktion beider Dateien geprüft/
   korrigiert werden.
3. **Dienstart-Label "Regeldienst (AMB4)"**: Am 11.09.2026 umbenannt in
   "Regeldienst (Di–Fr, AMB4)" (Desktop-Tool) bzw. "Regeldienst (Di–Fr)"
   (PWA) – bereits erledigt und gepusht (Desktop-Commit `5af1987b`,
   PWA-Commit `03d5d531`).
