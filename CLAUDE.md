# Projekt: Tagesdokumentation Überstunden & Rufdienst (Klinikum Freudenstadt)

## Versionsnummer im Footer
`tagesdokumentation_erfassung.html` hat im Footer eine Versionsnummer
(„vX.Y · Alexander Zabelyshenskiy"), identisch in `build_html.py` gepflegt.
**Bei jeder inhaltlichen Änderung an HTML/JS (nicht bei reinen Doku-Änderungen)
die Versionsnummer in BEIDEN Dateien hochzählen** (Bugfix → Patch, z.B. 1.5→1.6;
neues Feature → Minor, z.B. 1.6→1.7).

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

## Zwei parallele Dateien – IMMER BEIDE pflegen! (nur für gemeinsame Logik)
- `tagesdokumentation_erfassung.html` (Root) – Desktop-Tool, wird per GitHub
  Pages unter `https://nomiknomik.github.io/tagesdokumentation-ueberstunden-rufdienst/tagesdokumentation_erfassung.html`
  ausgeliefert. Hat eigene Kopie der Dienstart-Optionsliste (`DIENSTART_OPTIONS`).
- `app/index.html` – PWA-Variante (separates Manifest/Service Worker), hat
  EIGENE, unabhängige Kopie der gleichen Logik (`DUTY`-Objekt mit
  `amb2`/`amb4`/`ZD1`/`ZD2`/`RBD`/`RBD2`).
  Änderungen an Dienstart-Labels, Zeiten, Minusstunden-Berechnung etc. (also
  Logik, die es in BEIDEN Tools gibt) müssen in BEIDEN Dateien parallel
  gemacht werden – es gibt keine gemeinsame JS-Datei/kein Include.
- **WICHTIG (seit PWA-Redesign-Session 13.09.2026)**: Die PWA hat inzwischen
  viele Features, die es im Desktop-Tool NICHT gibt und die auch NICHT dort
  nachgezogen werden müssen: Kommen/Gehen-Zeitstempel-Button, Dienstplan-
  Import (.xls/.xlsx), Team-/Kollegen-Übersicht ("wer hat wann Dienst"),
  Verlauf ("Erfasste Tage"), das komplette visuelle Design (Farben/Icons/
  Layout), Monatsgruppierung. Diese sind PWA-exklusiv – die "IMMER BEIDE
  pflegen"-Regel gilt nur für die tatsächlich geteilte fachliche Logik
  (Dienstart-Zeiten, Überstunden-/Minusstunden-Berechnung, FRN-Verhalten),
  nicht für PWA-only UI/UX-Arbeit.

## PWA (app/index.html) – Stand nach Redesign-Session (13.09.2026)
Ausgangslage war ein Wunsch nach "schönerem Layout". Verlauf zur
Nachvollziehbarkeit für künftige Sessions:
1. Erster Versuch: Emoji-Icons + dunkles Petrol-Theme nach einem groben
   ChatGPT-Mockup-Bild → Nutzer-Feedback: "hast alles nachgezeichnet, kannst
   du aber sehr schlecht" (Emoji als Icon-Ersatz wirkt billig).
2. Nutzer hat daraufhin ChatGPT einen sehr detaillierten UI/UX-Redesign-Prompt
   entlocken lassen (Design-Tokens, Spacing-System, explizit KEIN Emoji/PNG,
   KEIN Telefon-Icon für Rufdienst, echte SVG-Icons, Ruhezeit-Status als
   Badge, kompakte Einsatz-Liste). Danach komplett neu umgesetzt:
   - **Eigenes kleines inline-SVG-Icon-Set** (Lucide/Feather-Stil): `ICONS`-
     Objekt + `icon(name)`-Helper in `<script>`. Statische Platzhalter im
     HTML als `<span data-icon="clock"></span>` werden beim Laden per
     `document.querySelectorAll('[data-icon]')` einmalig durch echtes
     `<svg>` ersetzt (spart, das SVG-Markup in jedem Card-Header zu
     duplizieren). Neues Icon hinzufügen = Eintrag in `ICONS` + `data-icon`-
     Attribut setzen.
   - **Design-Tokens als CSS Custom Properties** in `:root` (Farben, Radien,
     Spacing) – dadurch ließ sich der komplette spätere Theme-Wechsel
     (dunkel → hell) fast nur über die `:root`-Werte erledigen.
   - **Rufdienst-Einsätze**: kompakte Zeilen (Zeit/Dauer/Art-Badge/Chevron),
     Antippen klappt die volle Bearbeitungsmaske auf (`expanded`-Set in JS,
     Reset bei Tageswechsel über `lastRenderedDay`-Tracking). Alle Felder
     (Beginn/Ende/Art/Grund/Fallnummer) bleiben erhalten, nur die Darstellung
     ist neu.
   - **Ruhezeit-Status**: rein visuelles Badge (`renderRuhezeitStatus()`),
     das nur den Wert des bestehenden ja/nein-Dropdowns farbig darstellt –
     KEINE neue Berechnungslogik (der offene Punkt "Ruhezeit-Automatik" von
     weiter oben ist weiterhin NICHT umgesetzt).
3. Live-Test auf iPhone deckte zwei echte Bugs auf:
   - `header{position:sticky}` hat auf dem Gerät nicht zuverlässig oben
     fixiert → Statusleiste überlappte Karteninhalt beim Scrollen. **Fix**:
     `position:fixed` (wie die Bottom-Nav), `main`-Padding-Top wird per JS
     (`syncHeaderPad()`) anhand der echten Header-Höhe gesetzt, nicht fest
     verdrahtet.
   - `input[type=time/date]` hatte eigenen Rahmen+Hintergrund UND das
     native iOS-Zeit-Widget zeigt selbst eine abgerundete Kapsel →
     "Doppelkapsel"-Optik. **Fix**: `border-color:transparent;
     background:transparent` für diese Input-Typen, nur das native Widget
     bleibt sichtbar.
   - Dienstplan-Listen (Meine Dienste/Team/Erfasste Tage) waren eine lange
     flache Liste → jetzt über `renderGroupedList()` nach Monat gruppiert
     (natives `<details>`/`<summary>`, kein extra JS-Toggle nötig, CSS
     rotiert das Chevron-Icon über `.monthgroup[open] summary .ic`).
4. Nutzer-Feedback zum dunklen Theme: "zu dunkel und zu trivial" → auf
   Nachfrage explizit **helles "Warm & Ruhig"-Theme** (Creme/Weiß, warme
   Brauntöne) gewählt, nicht das neutral-graue "Minimalistisch". Umgesetzt
   rein über die `:root`-Tokens plus:
   - `apple-mobile-web-app-status-bar-style` von `black-translucent` auf
     `default` (sonst wäre die Uhrzeit-Anzeige auf hellem Grund unsichtbar).
   - Tag-Badges (telefonisch/Präsenz/Operation/Sonstiges) von hell-auf-dunkel
     auf dunkel-auf-hell gedreht (sonst unlesbar auf Weiß).
   - Gegen "trivial": dezente Farbverläufe + farbige Schatten auf den drei
     Haupt-Buttons (Gehen/PDF/Einsatz starten), aktiver Bottom-Nav-Tab als
     Farbpille statt nur Textfarbwechsel.
5. **Service-Worker-Falle (nicht wiederholen!)**: Nach den beiden letzten
   Theme-Commits vergessen, `CACHE`-Version in `app/sw.js` hochzuzählen →
   installierte PWA hat trotz gepushtem Code weiter die alte gecachte
   `index.html` ausgeliefert ("online, aber nicht sichtbar"-Verwirrung).
   **Strukturell gefixt**: `index.html` wird jetzt **network-first** geladen
   (Cache nur Offline-Fallback), alle anderen Assets (PDF, Icons, CDN-Libs)
   bleiben cache-first. Dadurch muss die `CACHE`-Konstante bei reinen
   `index.html`-Änderungen NICHT mehr manuell hochgezählt werden – nur noch,
   wenn sich `sw.js` selbst oder die SHELL-Liste ändert.
   **Zweiter Teil derselben Falle**: Auch mit network-first blieb ein Bugfix
   (PDF-Button hinter Bottom-Nav) auf dem Gerät unsichtbar, obwohl der Code
   per GitHub-API nachweislich korrekt auf `main` war – Ursache war der
   Service-Worker-**Update-Mechanismus** selbst: `register('sw.js')` ohne
   explizites `reg.update()` unterliegt dem Browser-Throttle, und selbst
   eine erfolgreich installierte neue SW-Version hat die Seite nicht
   automatisch neu geladen. **Fix**: `reg.update()` nach der Registrierung
   explizit aufrufen, plus `location.reload()` bei `controllerchange` bzw.
   wenn die neu installierte SW den Status `activated` erreicht (siehe
   Ende von `app/index.html`, Abschnitt "Start"). Zuverlässigster manueller
   Workaround bei Verdacht auf Cache-Trägheit: Home-Screen-Icon löschen und
   über Safari neu "Zum Home-Bildschirm hinzufügen" (komplett frische
   Installation ohne alten Service Worker).

### PWA-Versionsanzeige + Bottom-Padding (13.09.2026)
- `app/index.html` hat jetzt `APP_VERSION`/`APP_BUILD` (JS-Konstanten am Anfang
  des "Start"-Blocks). Angezeigt als Chip im Header (`#appVersion`) und in der
  Einstellungen-Karte "App-Version" (`#verNum`/`#verDate`), plus Button
  "Nach Update suchen" (`#checkUpdate`): lädt `index.html?cb=…` mit
  `cache:'no-store'`, vergleicht die `APP_VERSION` aus dem Quelltext mit der
  laufenden und lädt bei Abweichung nach `reg.update()` neu.
  **Bei jeder inhaltlichen PWA-Änderung `APP_VERSION`/`APP_BUILD` hochzählen** –
  sonst zeigt die App eine falsche Aktualität an.
- **Bottom-Padding-Falle (gelöst)**: `html,body{height:100%}` + `padding-bottom`
  auf `body` funktionierte auf iOS nicht – bei fester Body-Höhe liegt das
  Padding am 100%-Rand, überlaufender Inhalt (PDF-Button, "Diesen Tag
  zurücksetzen") ragte darunter und verschwand hinter der fixen Bottom-Nav.
  **Fix**: nur noch `html{height:100%}`, unteres Padding auf `main`
  (`calc(96px + env(safe-area-inset-bottom))`), `syncHeaderPad()` setzt
  `main.style.paddingBottom` anhand der gemessenen Nav-Höhe (nicht mehr `body`).

### PWA: Backup-Import, Monatsgruppen, Kalender-Export (13.09.2026, v1.8.0)
- **JSON-Backup laden**: Einstellungen → Daten → „Backup aus JSON laden"
  (`#importDataBtn` → verstecktes `#importData`). Liest `{cfg, plan, days}`,
  fragt mit Anzahl Plantage/erfasster Tage nach und **ersetzt** danach `plan`
  und `days` (cfg wird gemerged), schreibt in localStorage und rendert neu.
- **Monatsgruppen bleiben zugeklappt**: `renderGroupedList()` öffnet nicht mehr
  automatisch den ersten Monat. Der Auf-/Zuklapp-Zustand wird je Container in
  `tagesdoku_open_groups` (localStorage, `openGroups`) gemerkt und beim Rendern
  wiederhergestellt – überlebt Re-Render und App-Neustart.
- **Kalender-Export (.ics)**: Dienstplan → „Dienste in den Kalender"
  (`#icsBtn`, `buildIcs()`). Exportiert genau die Einträge der Karte „Meine
  Dienste" (`myDutyKeys()` – Rufdienste + Abwesenheiten, keine Regeldienste)
  als **Ganztages-VEVENTs** (`DTSTART;VALUE=DATE`, `DTEND` = Folgetag), die
  Soll-Dienstzeit aus `DUTY` steht in `DESCRIPTION`. Ausgabe über
  `navigator.share({files})` (iOS: Teilen → Kalender), sonst Blob-Download.
  UIDs sind stabil (`tagesdoku-<datum>-<code>@klf`), ein erneuter Import legt
  dieselben Termine also nicht doppelt an.

### PWA v1.9.0 – Wortlaut-Angleich an das Desktop-Tool + Tag-Ansicht (13.09.2026)
- **Desktop-Wortlaut ist führend**: `DUTY`-Labels, `ART_OPTS` und die neue
  `GRUND_OPTS` in `app/index.html` entsprechen jetzt exakt
  `DIENSTART_OPTIONS`/`artOptions`/`grundOptions` in
  `tagesdokumentation_erfassung.html` (inkl. Kürzel: „Regeldienst (Montag,
  AMB2)", „telefonisch (RBT)", „Präsenz im Haus (RBA)", „Operation /
  Eingriff"). `DUTY` kennt zusätzlich `FRN`, `BD`, `SPD`, `SONST`;
  `DIENSTART_BY_FUNKTION` blendet die Auswahl je Funktion ein (Oberarzt vs.
  Assistenzarzt/PA) wie im Desktop-Tool.
  Intern bleiben die Codes (`ZD1` …) als gespeicherter Wert – nur die Labels
  wurden angeglichen, deshalb war keine Datenmigration nötig. Alte
  Einsatz-Werte werden über `ART_LEGACY`/`migrateArt()` gehoben, abweichende
  Altwerte bleiben über `optsWith()` als Zusatz-Option erhalten.
- **Dienstart manuell überschreibbar**: Eine Auswahl im Dropdown setzt
  `day().dienstart_manuell = true`; `renderDay()` leitet die Dienstart dann
  nicht mehr aus dem importierten Plan ab. Unter dem Feld steht ein Hinweis
  mit dem Plan-Wert und dem Link „Wieder aus Dienstplan übernehmen"
  (`#dienstartHint` / `#dienstartReset`).
- **Grund der Überstunden** ist jetzt ein Dropdown (vorher Freitext),
  **Grund/Anlass** je Einsatz ebenfalls – beide mit `GRUND_OPTS`.
- **Tag-Ansicht umgestellt**: Karte „Rufdienst-Einsätze" steht vor
  „Kommen/Gehen". Die beiden Buttons „Einsatz jetzt starten"/„jetzt" sind zu
  EINEM Stempel-Button `#btnEinsatz` verschmolzen: grün „Einsatz starten",
  nach dem Start rot „Einsatz beenden (läuft seit hh:mm)"
  (`offenerEinsatz()` = letzter Einsatz mit Beginn ohne Ende,
  `renderEinsatzBtn()`). Nachtragen von Hand über den Ghost-Button darunter.
  Beginn/Ende/Dauer eines Einsatzes liegen über `.grid3` in einer Zeile.

### PWA v1.10.0 – Kalender monatsweise + Telefonat-Button (13.09.2026)
- **Kalender-Export je Monat statt alles auf einmal**: Der globale Button ist
  weg; `renderGroupedList()` hat jetzt einen optionalen `footerFn`-Parameter,
  über den `renderPlanList()` in JEDE Monatsgruppe einen Button
  `data-ics="<YYYY-MM>"` setzt. Ein delegierter Click-Handler auf `#planList`
  filtert `myDutyKeys()` auf diesen Monat und erzeugt `Dienste_<YYYY-MM>.ics`.
- **Vorbelegung „Einsatz starten" (v1.10.1)**: ein per Stempel-Button
  gestarteter Einsatz bekommt sofort `art:'Präsenz im Haus (RBA)'` und
  `grund_anlass:'Notfall / Notoperation'` (beides im Formular änderbar).
  „Nachtragen" bleibt bewusst leer, „Telefonat" setzt RBT.
- **Telefonat-Button** (`#btnTelefonat`) in der Einsatz-Karte: legt sofort
  einen fertigen Einsatz an mit `art:'telefonisch (RBT)'`,
  `grund_anlass:'Notfall / Notoperation'`, `ende` = jetzt, `beginn` = jetzt
  minus 5 Minuten (Dauer 0.08 h). Der Eintrag gilt als abgeschlossen und
  bleibt zugeklappt (kein `expanded.add`); dasselbe beim Beenden eines
  laufenden Einsatzes (`expanded.delete(i)`). Aufgeklappt wird nur der
  gerade GESTARTETE Einsatz, damit Fallnummer o.ä. ergänzt werden kann.

### PWA v1.12.0 – Diensttausch direkt in „wer hat wann Dienst" (13.09.2026)
- Speicher `swap` (`localStorage: tagesdoku_swap`) hält jetzt den **Namen des
  Diensthabenden** je Tag (`{"JJJJ-MM-TT": "Nachname"}`), nicht mehr eine
  Dienstart (v1.11.0-Altwerte werden beim Laden verworfen). `derive()` legt
  den Namen über `plan[k].oa` und leitet daraus wie gewohnt ab (Wochentag/
  Feiertag → ZD1/ZD2/RBD/RBD2), ergänzt um `swapped:true` und den Zusatz
  „· Dienst getauscht" in `info`. Helfer: `oaOf(k)`.
- Die separate Karte „Diensttausch" ist wieder entfernt. Stattdessen ist in
  der Karte „Rufdienst – wer hat wann Dienst" **jede Tageszeile antippbar**
  (`teamRow()`, `teamOpen`): aufgeklappt erscheinen ein Select mit allen im
  Plan vorkommenden Namen (`bekannteNamen()`) plus „– niemand –", der Button
  „Ich übernehme" und – bei bereits getauschten Tagen – „Tausch zurücknehmen"
  samt Hinweis, wer laut Excel eingetragen war. Auswahl wirkt sofort
  (`setSwap()`), die Zeile klappt danach zu und ist mit „· getauscht" und
  farbigem Tag markiert.
- Entspricht die Auswahl wieder dem Excel-Wert, wird der Tausch automatisch
  gelöscht statt gespeichert.
- **v1.12.1**: Die Box „Aktueller Dienst" zeigt bei einem Tausch nicht mehr den
  Excel-Namen, sondern eine farbige Notiz „Getauscht: Rufdienst hat <Name>
  (laut Plan: <Original>)"; ohne Tausch bleibt es bei „Rufdienst lt. Plan: …".
- Wirkung wie zuvor: Karte „Meine Dienste", monatsweiser Kalender-Export,
  Box „Aktueller Dienst" und die Dienstart-Ableitung im Tagesbogen (nur wenn
  dort nicht `dienstart_manuell` gesetzt ist). `swap` liegt im JSON-Backup und
  wird von „Alle Pläne löschen" mit geleert.

### PWA v1.12.2 – „Diesen Tag zurücksetzen" wirkt jetzt auch im Verlauf
- Zwei Ursachen: (1) `resetTag` hat nach `delete days[cur]` weder gespeichert
  noch `renderHistory()` aufgerufen, (2) `renderDay()` legt den Tag sofort neu
  an und trägt die Soll-Zeiten aus dem Dienstplan ein – der alte Verlaufsfilter
  (`d.dienstbeginn || …`) hat das als „erfasst" gewertet.
- **Fix**: neuer Helfer `hasContent(k)` entscheidet, ob ein Tag im Verlauf
  erscheint: Ist-Dienstende, Einsätze, FRN, `dienstart_manuell`, ausgefüllte
  Text-/Auswahlfelder ODER Dienstbeginn/Plan-Ende, die von den Soll-Zeiten der
  abgeleiteten Dienstart abweichen. Bloßes Anschauen eines Tages legt damit
  keinen Verlaufseintrag mehr an. `resetTag` speichert jetzt und rendert den
  Verlauf neu.

### PWA v1.13.0 – Monats-Sammel-PDF, Prüfhinweise, Tages-Kontext (15.09.2026)
Nach einer Verbesserungsrunde mit dem Nutzer umgesetzt (bewusst NICHT umgesetzt:
Kommen-Stempel, Verrechnung Rufdienst in „Überstunden gesamt", Liste offener
Tage, Dark Mode, Kennzahl-Kacheln, Default-Datum „gestern" – jeweils vom
Nutzer abgelehnt; die Überstunden sind im Klinik-System über die Dienstart
bereits hinterlegt, erfasst wird nur zusätzliche Aktivzeit).
- **Ruhezeit**: `blank()` setzt `ruhezeit_eingehalten:'ja'` – im Haus immer
  eingehalten, Dropdown bleibt änderbar.
- **Rechnen ohne DOM**: neue Funktion `calcFor(k)` liefert `{ue, summe, anzahl,
  dauern}` für einen beliebigen Tag; `calc()` schreibt davon nur noch in die
  Felder. Voraussetzung für den Monats-Export.
- **PDF-Erzeugung refaktoriert**: `loadTemplate()` (Vorlage einmal laden),
  `buildTagesPdf(k, flatten)` (ein Blatt für einen beliebigen Tag),
  `teilePdf(bytes, name)` (Share bzw. Download).
- **Monats-Sammel-PDF**: Button „Monat als Sammel-PDF" in jeder Monatsgruppe
  von „Erfasste Tage" (`data-monthpdf`, `monatsPdf()`): alle Tage mit
  `hasContent()` werden **geflattet** (`form.flatten()`) und per `copyPages()`
  zu EINER Datei `Tagesdokumentation_<JJJJ-MM>.pdf` zusammengefügt – ein Blatt
  je Tag. Flatten ist nötig, weil sonst 67 gleichnamige Formularfelder je Seite
  kollidieren. Das Einzel-PDF bleibt unverändert ausfüllbar.
- **Plausibilitätsprüfung** `pruefeTag(k)`: Einsatz ohne Ende/Beginn, Dauer
  > 12 h, Operation ohne Fallnummer, fehlende Art, Überschneidungen, > 8
  Einsätze, FRN ohne Kommentar. Wird vor Einzel- UND Sammel-PDF als
  `confirm()` gezeigt und blockiert nichts.
- **Live-Timer**: `renderEinsatzBtn()` startet bei laufendem Einsatz ein
  `setInterval` (`timerId`, `laufzeitText()`) und zeigt „läuft seit hh:mm ·
  00:12:45"; an anderen Tagen nur „offen seit hh:mm" (kein Timer).
- **Tages-Kontext** `renderDayContext()`: Zeile „Dienstag, 15.09.2026 · Heute"
  (auch „Gestern"/„Feiertag") plus **Wochenstreifen** Mo–So (`#weekStrip`):
  aktiver Tag gefüllt, grüner Punkt = erfasst (`hasContent`), Rahmen = eigener
  Dienst; Antippen wechselt den Tag. Der „Heute"-Button wird nur noch
  eingeblendet, wenn man nicht auf heute steht.
- **Aktionsleiste** `#actionbar`: „PDF erzeugen" sitzt jetzt fest über der
  Bottom-Nav (nur im Tag-Tab sichtbar). `syncHeaderPad()` rechnet die Höhe der
  Leiste ins `main`-Padding ein; `bar.style.bottom` = Nav-Höhe.

### PWA v1.13.1 – Ruhezeit-Vorbelegung zählte als Eingabe (15.09.2026)
- Bug aus v1.13.0: `blank()` setzt `ruhezeit_eingehalten:'ja'`, und `hasContent()`
  wertete jedes ausgefüllte Feld dieser Liste als Eingabe → jeder Tag, den man
  seit v1.13.0 nur angetippt hatte, stand unter „Erfasste Tage" (im Backup des
  Nutzers genau 14.09. und 15.09.).
- **Fix**: `ruhezeit_eingehalten` zählt nur noch, wenn der Wert vom Default `'ja'`
  abweicht. Zusätzlich räumt die App leere Tagesgerüste aktiv weg: beim
  Tageswechsel (`renderDay()`, alter Tag ohne `hasContent`) und einmalig beim
  Start – dadurch verschwinden auch die Altlasten früherer Versionen aus
  `localStorage` (im Test: 16 gespeicherte Tage → 1).

### PWA v1.13.2 – Zurückgesetzter Tag ist wieder ein unberührter Tag
- `persist()` speichert nur noch Tage mit `hasContent()` (das In-Memory-Objekt
  `days` bleibt unverändert, gefiltert wird beim Schreiben). Ein per „Diesen Tag
  zurücksetzen" geleerter Tag hinterlässt damit KEINEN Eintrag mehr im
  localStorage – er wird danach exakt wie ein nie geöffneter Tag behandelt:
  Dienstart/Zeiten wieder aus dem Dienstplan abgeleitet, kein
  `dienstart_manuell`, kein Verlaufseintrag, kein Punkt im Wochenstreifen.
- Der Diensttausch (`swap`) bleibt davon unberührt – er gehört zum Dienstplan,
  nicht zu den Eingaben im Tab „Tag".

### PWA v1.14.0 – Gehalt: Tagesverdienst + Monatsvorschau (15.09.2026)

Neu, **PWA-exklusiv** (nicht ins Desktop-Tool nachziehen – kein geteilter
Fachlogik-Anteil, siehe „Zwei parallele Dateien"):

- **Karte „Verdienst an diesem Tag"** unten im Tag-Tab: rechnet aus den
  eingetragenen Daten live Brutto und geschätztes Netto, mit Aufschlüsselung
  je Lohnart plus Tagesanteil der Grundvergütung.
- **Neuer Tab „Gehalt"**: monatsweise Aufstellung je Lohnart (Menge, Betrag),
  Brutto/Netto gesamt, Hinweis auf die **Zwei-Monats-Verzögerung**
  (Leistungsmonat → Abrechnungsmonat), Tagesliste und Export als Text zum
  Abgleich mit dem Papier-Zettel.
- **Netto-Schätzung** in den Einstellungen: beliebig viele Referenzmonate
  (Brutto/Netto aus alten Abrechnungen). Ab zwei Monaten wird per linearer
  Regression der **Grenzfaktor** bestimmt (was von einem zusätzlich
  verdienten Euro bleibt – der relevante Wert für Zuschläge); ein Monat
  liefert nur den Durchschnittsfaktor. Beides von Hand überschreibbar.

Die Formeln stammen aus dem Analyse-Repo
`nomiknomik/tagesdokumentation-gehaltsberechnung` – dort zuerst `STAND.md`
lesen (Übergabestand und offene Punkte), dann `BERECHNUNG.md` (kurz) bzw.
`FORMELN.md` (ausführlich).

**Arbeitsteilung:** Die Herleitung der noch offenen Formeln läuft im Raw-Chat
weiter, weil die Rohdaten (`data/raw/`) per `.gitignore` außerhalb von Git
liegen und in einer Web-Session gar nicht vorhanden sind. Hier wird an der
App weitergearbeitet. Kommt aus der Formelsuche ein Ergebnis, ist hier nur
`gehaltMengen()` anzupassen und das `unsicher:true`-Flag der betroffenen
Lohnart zu entfernen.

Kernpunkte für die Wartung:

- **Zwei Stundensätze**: der eigene (56,46 € / ab 06/2026 57,59 €) gilt nur
  für LA 734 und die Pauschalen 796/797; alle Zeit**zuschläge** (731, 735,
  737, 752, 790, 791) bemessen sich am **Referenzstundensatz 60,94 €**
  (Tabellenentgelt Stufe 3, §8 Abs. 1 Satz 2 TVöD). Im Code: `TARIF[].std`
  vs. `TARIF[].ref`, Zuschläge als Prozentsätze in `LOHNART`.
  ⚠️ `ref` ab 06/2026 (62,16 €) ist hochgerechnet, nicht belegt –
  `refGeschaetzt:true` blendet dafür einen Hinweis ein.
- **Mitternachts-Aufteilung** (`teileAnMitternacht`) ist der Kern: ein
  Einsatz 18:00–02:52 ist 6,0 h am Starttag und 2,87 h am Folgetag. Ohne das
  stimmt kein einziger Zuschlag.
- **Rundung** nach §8 Abs. 3: Präsenz-Einsätze einzeln auf volle Stunde auf,
  Telefonate als Tagessumme einmal (`einsatzDauern`). Diese Rundung zählt
  fürs Entgelt (734/735), **nicht** für die Zeitfenster-Zuordnung von
  790/791/752 – die rechnen mit roher Uhrzeit.
- **731, 737 und 752 sind noch nicht auf allen Vergleichsmonaten bestätigt**
  und in der App mit `*` markiert (`LOHNART[].unsicher`). Sobald die
  Variantensuche im Analyse-Repo (`src/hypothesen.py`) einen Treffer liefert,
  hier `gehaltMengen()` nachziehen und das Flag entfernen.
- **DST-Falle umgangen**: alle Tages-/Zeitrechnungen laufen über UTC-Tages-
  nummern (`tagNr`/`nrIso`) und Minuten seit Mitternacht, nicht über lokale
  `Date`-Arithmetik – sonst hätten die Umstellungstage 23 bzw. 25 Stunden.
- **Fallstrick beim Formular-Rendering** (hier schon einmal reingelaufen):
  In den Netto-Referenzzeilen darf das `change`-Event NICHT die ganze Liste
  neu bauen. Beim Wechsel von Brutto nach Netto feuert zuerst `change` auf
  dem Brutto-Feld – ein `innerHTML`-Neuaufbau ersetzt dann das Netto-Feld
  mitten im Tippen und die Eingabe geht verloren. Nur
  `nettoInfoAktualisieren()` aufrufen, Rebuild ausschließlich bei
  Hinzufügen/Löschen.

Nebenbei repariert: das `phone`-Icon hatte einen ungültigen SVG-Pfad
(`a2 0 0 1` statt `a2 2 0 0 1`) und wurde vom Browser verworfen.

### Offene Punkte PWA (Stand 13.09.2026)
- Ruhezeit-Check weiterhin nur Badge über manuelles Dropdown, keine
  Automatik (siehe oben, gilt für Desktop-Tool genauso).
- Figma-Anbindung (MCP-Connector „Figma" bzw. Plugin „figma" mit
  `figma-design-to-code`) wurde besprochen, aber vom Nutzer noch nicht
  aktiviert/verbunden – falls gewünscht: claude.ai → Connector-Einstellungen.
- Rufdienst-Einsatz-Darstellung ist eine vereinfachte Umsetzung der
  ChatGPT-Spec (kompakte Zeile + Aufklapp-Formular), nicht das exakt
  pixelgenaue "OnCallEntry"-Kartendesign aus dem Prompt.
- **Git-Workflow-Standing-Instruction**: Nutzer hat explizit gesagt „immer
  automatisch mergen" – jeder fertige/getestete Stand auf
  `claude/peaceful-cerf-3v8uke` wird ohne Rückfrage per Fast-Forward-Merge
  nach `main` gepusht (kein PR-Workflow für dieses Repo).

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
2. ~~**Minusstunden-Logik**~~ – erledigt (11.09.2026): `recalcDuty()`/`calc()`
   haben bei negativer Differenz pauschal 24h addiert (Mitternacht-Wrap-Annahme
   für den regulären Dienst), dadurch kam bei frühem Dienstende ein falscher
   großer positiver Wert raus statt Minusstunden. Fix in BEIDEN Dateien
   (Desktop `tagesdokumentation_erfassung.html`/`build_html.py` + PWA
   `app/index.html`): kein `+24`-Wrap mehr bei `tats_dienstende < plan_dienstende`.
   Hinweis: Falls der reguläre Dienst je über Mitternacht gehen sollte, würde
   das jetzt fälschlich negativ berechnet – bisher kein bekannter Anwendungsfall.
3. **Dienstart-Label "Regeldienst (AMB4)"**: Am 11.09.2026 umbenannt in
   "Regeldienst (Di–Fr, AMB4)" (Desktop-Tool) bzw. "Regeldienst (Di–Fr)"
   (PWA) – bereits erledigt und gepusht (Desktop-Commit `5af1987b`,
   PWA-Commit `03d5d531`).
