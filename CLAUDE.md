# Projekt: Tagesdokumentation Überstunden & Rufdienst (Klinikum Freudenstadt)

## Arbeitsweise: direkt auf main

**Nutzer-Vorgabe (15.09.2026): Änderungen gehen direkt auf `main`, kein
Feature-Branch, kein PR.** Grund: GitHub Pages liefert aus `main` aus, und
nur so ist der Stand sofort auf dem Telefon sichtbar.

Daraus folgt: `main` ist immer live. Vor jedem Push die App tatsächlich
rendern und prüfen (Playwright gegen `app/index.html` genügt, siehe die
Testläufe in der Versionshistorie unten) – ein kaputter Push ist hier kein
roter CI-Lauf, sondern eine kaputte App in der Hand.

Nach dem Push braucht Pages rund 30–60 Sekunden. Danach verifizieren, dass
die neue Versionsnummer wirklich ausgeliefert wird:

```
curl -s https://nomiknomik.github.io/tagesdokumentation-ueberstunden-rufdienst/app/index.html | grep APP_VERSION
```

**Service-Worker-Cache nicht vergessen:** bei jeder Änderung an `app/`
zusätzlich `CACHE` in `app/sw.js` hochzählen (`tagesdoku-vN`), sonst bekommen
installierte PWAs den alten Stand aus dem Cache serviert.

## Für Design-Arbeit an der PWA

Alles Visuelle steckt in `app/index.html`. Die Farb- und Maßtokens stehen
ganz oben im `:root`-Block (Zeile ~14) – Palette, Radien, Abstände,
Touch-Zielgröße, Buttonhöhe. Wer die Optik ändert, ändert am besten dort und
nicht in den einzelnen Regeln.

**Drei Stellen, an denen Layout und Logik verzahnt sind** – hier vor dem
Umbauen kurz nachlesen, sonst rechnet die App falsch oder verdeckt Inhalt:

1. **`syncHeaderPad()`** misst Header-, Nav- und Leistenhöhe und setzt daraus
   das Padding von `main`. Ändert sich eine dieser Höhen, muss die Funktion
   weiter stimmen. Sie reserviert bewusst die **aufgeklappte** Höhe der
   Verdienstleiste.
2. **Die Verdienstleiste** (`.geldbar`) klappt allein am Scrollstand auf
   (`geldBarPruefen()`). Kein zweiter Auf/Zu-Zustand – der würde sich mit dem
   Scrollen beißen.
3. **Der Block zwischen `>>>>> gehalt.js BEGINN` und `<<<<< gehalt.js ENDE`**
   ist fremder Code und wird nur als Ganzes ausgetauscht. Nichts darin
   umformatieren.

**Pflicht bei jeder Änderung an `app/`** (weil `main` live ist, siehe oben):
`APP_VERSION` in `app/index.html` **und** `CACHE` in `app/sw.js` hochzählen.
Ohne den Cache-Zähler bekommen installierte PWAs den alten Stand serviert.

**Vor dem Push tatsächlich rendern.** Playwright gegen `app/index.html`, auf
390 × 844 (Telefonbreite). Die bestehenden Testläufe prüfen nicht nur Zahlen,
sondern auch, dass nichts unter der Leiste verschwindet und die Tabs sauber
umschalten.

**Achtung, parallele Sessions:** an diesem Repo arbeiten mehrere Chats. Vor
dem Push `git pull --rebase`; bei einem Konflikt in der Zeile `APP_VERSION`
gewinnt die höhere Nummer, und der `CACHE`-Zähler muss dann über beide
hinausgehen. Das ist hier schon einmal passiert (v1.16.2 Icon gegen v1.17.0).

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

### PWA v1.15.0 – Verdienst als klebende Leiste unten (15.09.2026)

Die Verdienstanzeige ist von einer Karte am Ende des Tag-Tabs zu einer
**klebenden Leiste** geworden, die dort sitzt, wo vorher „PDF erzeugen" war.
Der PDF-Button ist dafür in den normalen Seitenfluss gewandert (hinter die
Zusammenfassung, vor „Diesen Tag zurücksetzen") und behält seine ID, das
Klick-Handling bleibt unverändert.

Verhalten: kompakt ein Einzeiler (Label · Betrag · Netto · Chevron, Höhe wie
vorher der Button). Steht die Seite ganz unten, klappt die Leiste automatisch
komplett auf und zeigt die Aufschlüsselung. Tippen auf den Kopf scrollt ans
Seitenende bzw. wieder nach oben.

Drei Dinge, die beim Nachbauen leicht schiefgehen:

- **Kein eigener Auf/Zu-Zustand.** Das Aufklappen hängt allein am Scrollstand
  (`geldBarPruefen()`: `scrollHeight - scrollY - innerHeight <= 8`). Ein
  zusätzlicher Toggle-Zustand würde sich mit dem Scrollen beißen – deshalb
  scrollt der Tap auf den Kopf nur, statt selbst zu schalten.
- **`syncHeaderPad()` reserviert die AUFGEKLAPPTE Höhe**, nicht die aktuelle
  (`gbHead.offsetHeight + gbBody.scrollHeight`, gedeckelt auf 60 vh wie die
  CSS-`max-height`). Sonst verdeckt die Leiste genau dann Inhalt, wenn sie
  unten aufklappt. `gbBody.scrollHeight` liefert die Inhaltshöhe auch bei
  `max-height:0`.
- **`renderTagGeld()` läuft bei jedem Tastendruck** (via `calc()`) und ändert
  die Zeilenzahl, also auch die Leistenhöhe. Deshalb `syncHeaderPadSoon()`
  statt `syncHeaderPad()` – das bündelt die Layout-Messungen auf einen Frame.

Beim Messen im Test beachten: Smooth-Scroll und die `max-height`-Transition
laufen nacheinander, zusammen gut 750 ms. Wer früher misst, bekommt eine zu
kleine Leistenhöhe – das ist kein Bug.

### PWA v1.16.0 – gehalt.js als Rechenkern (15.09.2026)

Die selbstgebauten Formeln der v1.14.0 sind **komplett ersetzt** durch
`src/gehalt.js` aus dem Analyse-Repo (gegen die Python-Referenz geprüft:
110/110 Werte über 10 Monate). Das Modul steht **unverändert** zwischen den
Markern `>>>>> gehalt.js BEGINN` und `<<<<< gehalt.js ENDE` – beim
Aktualisieren nur diesen Bereich austauschen.

**Es liegt in einer IIFE.** Das Modul bringt eigene Bezeichner `iso()` und
`min()` mit, die es in `app/index.html` schon gibt; ohne Kapselung wäre das
ein Redeklarations-Fehler und die App stünde komplett still.

**Der App-Adapter darunter gehört uns** und ist nötig, weil das mitgelieferte
`eintraegeAusTagen()` nicht zu dieser PWA passt:

- Es liest `dienstende_ist` / `dienstende_plan`, die PWA speichert
  `tats_dienstende` / `plan_dienstende`. Ungeprüft übernommen entstünde
  **keine einzige Dienst-Zeile** – 731 wäre immer 0 und den Zuschlägen
  fehlte die Dienstzeit.
- `istStd` muss die **tariflich aufgerundete** Aktivzeit sein (Präsenz je
  Einsatz, Telefonate als Tagessumme). In der Quell-CSV steckt die Rundung
  schon drin, in unseren Tagesdaten nicht – `einsatzDauern()` macht das.

**Nachtverschiebung – die subtilste Stelle.** Der Rechenkern bucht
RB-Einsätze mit Beginn vor 06:00 einen Tag **weiter**, weil das Quellsystem
sie auf den Rufdienst-Beginntag schreibt und erst die Abrechnung sie auf den
echten Kalendertag zieht. Diese App speichert sie (per Zeitstempel) schon auf
dem echten Tag. Der Adapter datiert sie deshalb einen Tag **zurück**, damit
die Verschiebung des Moduls sie wieder genau dorthin bringt. Das stellt
nebenbei die Monatszuordnung von 734/735 richtig, die am unverschobenen
Datum hängt. Wer Nachteinsätze am Dienstbeginn-Tag erfasst, stellt das in den
Einstellungen um (`cfg.nachtBuchung`).

**Tageswerte sind Marginalbeiträge.** Der Überstundenzuschlag ist wochenweise
definiert (mit Blick in die Folgewoche) und lässt sich gar nicht tageweise
ausrechnen. `tagesAnteil()` bildet deshalb „Monat mit dem Tag" minus „Monat
ohne den Tag". Deshalb deckt `gehaltEintraege()` auch 10 Tage vor und 13 Tage
nach dem Monat ab – sonst fehlt der Wochenlogik ihr Kontext. Kosten: rund
1 ms je Neuberechnung der Leiste, 4 ms für die Monatsansicht.

**Was die App zusätzlich zum Modul leistet:** Grundvergütung (LA 050, folgt
nicht aus den Zeiten), die Einspringpauschale (LA 252, 50 €/Tag, manuelles
Feld je Monat in `extras` / `tagesdoku_extra`, wandert auch ins Backup), und
die Kennzeichnung unsicherer Posten:

- **731** ist als *geschätzt* markiert – die Formel trifft die **erfassten**
  Überstunden exakt, ausgezahlt wird durch Freizeitausgleich teils weniger.
- **753/754** sind als *bisher nur an einem Monat belegt* markiert.
- **031 Urlaubsaufschlag ist bewusst nicht drin.** Bei Urlaubstagen zeigt die
  App einen Hinweis statt einer Schätzung – im Tag-Tab und in der
  Monatsansicht. Achtung beim Ändern: Urlaubstage erzeugen **keine**
  Einträge, die Erkennung muss also über alle Kalendertage laufen, nicht nur
  über die mit Einträgen (genau dieser Fehler war schon einmal drin).

Der Nachtfenster-Wechsel (bis Feb 2026 21–6 Uhr, ab März 20–6) und die beiden
Satz-Stände (Wechsel zum Leistungsmonat Juni 2026) stecken im Modul und
werden über den Monat automatisch gewählt.

### PWA v1.16.1 – PDF-Knopf in den Header (15.09.2026)

„PDF erzeugen" ist kein Vollbreiten-Knopf mehr, sondern ein rundes Symbol
rechts oben im Header (44 px, also volles Touch-Ziel). Es gehört zum
Tagesbogen und wird auf den anderen Tabs ausgeblendet – `zeigePdfKnopf()`,
aufgerufen an denselben drei Stellen wie die Actionbar. Die ID `pdfBtn`
bleibt, das Klick-Handling ist unverändert.

**Zum Telefon-Icon**, falls es wieder auffällt: in Versionen vor 1.15.0 stand
links von „Telefonat" ein kommaähnliches Zeichen. Das war kein Text, sondern
der SVG-Pfad des `phone`-Icons: `a2 0 0 1` statt `a2 2 0 0 1` ist ein
ungültiger Arc-Befehl, der Browser bricht den Pfad an dieser Stelle ab und
zeichnet nur noch das vorangehende `M22 16.92v3` – einen kurzen senkrechten
Strich, der wie ein Komma aussieht. Seit 1.15.0 korrigiert. Wer so etwas
prüfen will: `svg.querySelector('path').getBBox()` – ein abgebrochener Pfad
hat Breite 0.

### PWA v1.17.0 – Überstundenkonto + Rechenkern aktualisiert (16.09.2026)

`gehalt.js` ist auf den Stand von `origin/main` des Analyse-Repos gebracht.
Die Änderung war **rein additiv** – `berechneMengen()` und `berechneEuro()`
sind unverändert, neu sind `monatssoll()` und `ueberstundenkonto()`.

**Neu: Überstundenkonto** als Karte im Gehalt-Tab. Eigenes Rechenwerk,
unabhängig von der Gehaltsprognose und besser belegt als LA 731 (6/6 Monate
exakt gegen die echten Kontostände). Der Nutzer trägt einmal Monat und Saldo
aus der Dienstübersicht ein (`cfg.konto`), die App schreibt ab da fort:

```
Soll = Arbeitstage (Mo–Fr ohne BW-Feiertag) × 8,00 h
Ist  = Σ Ist-Std der Zeitarten 1, 705, 707, 715, 957
```

**Die Pausenregel ist der heikle Teil.** Fürs Konto zählt die
Nettoarbeitszeit, die Tagesdaten der App enthalten aber Bruttospannen.
`pauseFuer()` zieht ab 6 Std pauschal 30 Minuten ab – **von Ist UND Soll**,
damit sich die Pause bei 731 heraus­kürzt und die gegen die Dienstübersichten
validierte Zahl unverändert bleibt.

Bewusst **nicht** gestaffelt: das ArbZG verlangt ab 9 Std 45 Minuten, aber ob
das Quellsystem das so bucht, ist unbelegt — und die Staffel kürzt sich bei
731 *nicht* heraus, sobald Ist und Soll in verschiedene Stufen fallen. Beim
Versuch verlor ein Tag 07:10–18:05 gegen Plan bis 16:05 genau 0,25 Std
Überstunden, 731 fiel von 2,00 auf 1,75. Die 30-Minuten-Stufe ist die einzige,
die durch Daten gedeckt ist: sie trifft sowohl die 8,17 Std der Zeiterfassung
(Regeldienst 07:25–16:05) als auch die 6,50 Std, die die Integrations-Spec
für ZD1 (11:00–18:00) nennt. **Wer hier etwas ändert, muss vorher prüfen, dass
731 gleich bleibt.**

**Abwesenheiten:** der Adapter erzeugt für Urlaub (705, aus `derive()` →
`abwesend`) und FRN (957) Zeilen mit der Nettozeit des Regeldienstes, den der
Tag sonst gehabt hätte. Fortbildung (707) und Krankheit (715) kennt die App
nicht – solche Tage fehlen im Ist und drücken den Saldo.

**Abdeckungswarnung:** ohne importierten Dienstplan hat der Monat fast keine
Zeilen und der Saldo sähe dramatisch negativ aus, obwohl nur Daten fehlen.
`kontoAbdeckung()` zählt deshalb die Arbeitstage mit und ohne Zeile und warnt
sichtbar. Beim Testen ohne Plan ist genau das zu sehen – das ist kein Bug.

**Bekannte Drift:** ein voll belegter Monat ergibt ~180 Std Ist gegen 176 Std
Soll, also rund +4,7 Std pro Monat. Das ist plausibel (der Dienstplan setzt
8,17–8,42 Std/Tag an, das Konto rechnet mit 8,00), aber nicht verifiziert.
Der erste Abgleich mit einem echten Kontostand zeigt, ob das Modell trägt;
dafür lässt sich der Startwert jederzeit neu setzen.

**Kennzeichnung angepasst:** 731 heißt jetzt „erfasste Überstunden – die
Auszahlung kann abweichen" (Formel gegen die Dienstübersichten bestätigt,
22/23 Wochen; in drei von sieben geprüften Monaten wurde weniger ausgezahlt).
Die Einspringpauschale ist im Quellsystem Zeitart 99 „Holen aus dem frei",
die im Export fehlt – deshalb weiterhin ein Handfeld.

### PWA v1.18.0 – Fortbildung und Krankheit (16.09.2026)

Die beiden Lücken im Überstundenkonto sind geschlossen. `FB` (Fortbildung,
Zeitart 707) und `KRANK` (715) sind neue Dienstarten **ohne** `start`/`end` –
dadurch erzeugen sie keine Dienstzeile und wirken nur im Konto. Zusammen mit
Urlaub (705, aus der Urlaubsspalte des Dienstplans) und FRN (957) deckt die
App jetzt alle Zeitarten ab, die der Rechenkern kennt.

Die Zuordnung steht in einer Tabelle:

```js
const ABWESENHEIT = {FRN:'957', FB:'707', KRANK:'715'};
```

**Zwei Fallen, die dabei aufgefallen sind:**

1. **Die FRN-Checkbox ist keine Abwesenheit.** Sie sitzt im Kommen/Gehen-Block
   und schreibt nur einen Vermerk in die Erläuterung („FRN – frei nach Dienst:
   Nachtoperation bis 03:40"), gehört also zu einem **gearbeiteten** Tag. In
   v1.17.0 wurde sie als 957 gewertet – ein solcher Tag bekam damit sowohl
   eine Dienstzeile als auch eine Abwesenheitszeile und zählte im Ist doppelt.
   Abwesenheit hängt jetzt ausschließlich an der **Dienstart**. Nicht wieder
   zusammenführen.
2. **Abwesenheitstage unterdrücken die Dienstzeile hart.** Wer eine Dienstart
   auf `KRANK` umstellt, hat oft noch alte Zeiten im Formular stehen
   (`dienstbeginn`, `tats_dienstende`). Ohne die Unterdrückung entstünde daraus
   eine Dienstzeile und der Tag zählte doppelt.

Abwesenheiten werden nur an Werktagen (Mo–Fr, kein BW-Feiertag) gebucht – an
einem freien Samstag gibt es nichts zu erfüllen – und mit der Nettozeit des
Regeldienstes, den der Tag sonst gehabt hätte (Mo 8,42 h, Di–Fr 8,17 h).

**Bewusste Abweichung vom Desktop-Tool:** `FB` und `KRANK` gibt es **nur in
der PWA**. Die „IMMER BEIDE pflegen"-Regel zielt auf geteilte fachliche Logik;
diese beiden Einträge existieren ausschließlich, um das PWA-exklusive
Überstundenkonto zu füttern, und wären im Desktop-Tool (das nur den
PDF-Bogen erzeugt) zwei verwirrende Optionen ohne Funktion. Wer das anders
sieht, ergänzt `DIENSTART_OPTIONS` in `tagesdokumentation_erfassung.html`.

### PWA v1.19.0 – Unterschriftsdatum + Begründung bei „Sonstiges" (16.09.2026)

Beides gab es im Desktop-Tool schon, die PWA hat nachgezogen.

**Heutiges Datum links unten bei „Datum, Unterschrift Ärztin/Arzt".** Dafür
gibt es **kein Formularfeld** – der Text wird mit `page.drawText()` direkt auf
die Seite gezeichnet, Position und Größe identisch zum Desktop-Tool
(`x:40, y:148, size:9`). Muss **vor** `form.flatten()` passieren; so wandert
er auch in die Monats-Sammel-PDF, die die Seiten kopiert.

**„Sonstiges (bitte erläutern)" blendet ein Begründungsfeld ein.** Das
Formular hat dafür nur die Erläuterung, und die steht im Desktop-Tool direkt
unter dem Grund, in der PWA aber weit unten in der Zusammenfassung. Deshalb
gibt es jetzt ein zweites Eingabefeld direkt unter dem Dropdown, das auf
**dasselbe** `d.erlaeuterung` schreibt. Drei Stellen halten die beiden
Ansichten synchron: das neue Feld, die Bindung in `FIELDS` und
`syncFrnText()` (das schreibt ebenfalls in die Erläuterung). Wer eine vierte
Schreibstelle ergänzt, muss dort mitziehen.

`pruefeTag()` warnt vor dem PDF, wenn „Sonstiges" gewählt, aber nichts
eingetragen ist – analog zum FRN-Kommentar.

**Zum Testen von PDF-Änderungen:** cdnjs ist aus der Web-Session heraus
gesperrt, `PDFLib` ist dort also undefiniert. Lösung im Test:
`page.route('**/pdf-lib*.js', …)` mit der lokal per npm installierten
`pdf-lib/dist/pdf-lib.min.js` beantworten. Das erzeugte PDF lässt sich dann
mit `pdfjs-dist` rendern und die Textpositionen prüfen – so wurde
verifiziert, dass das Datum wirklich über der Unterschriftszeile landet
(y=148 gegen „Datum, Unterschrift Ärztin / Arzt" bei y=136).

### PWA v1.19.1 – Backup-Dateiname mit Datum (17.09.2026)

Die Sicherung heißt jetzt `tagesdoku_backup_JJJJ-MM-TT.json` statt immer
gleich. ISO-Format bewusst: so sortieren sich mehrere Sicherungen im
Dateimanager von selbst richtig.

Dabei mitgenommen: der Export schrieb `days` **ungefiltert** raus und damit
auch das leere Tagesgerüst des gerade angeschauten Tages – eine Sicherung mit
einem erfassten Tag enthielt zwei Einträge. Export und `persist()` teilen sich
jetzt `echteTage()`, den Filter auf `hasContent()`.

**Zum Testen des Imports:** er fragt per `confirm()` nach. Playwright weist
Dialoge standardmäßig ab, der Import läuft dann still ins Leere und sieht wie
ein Bug aus. Im Test `page.on('dialog', d => d.accept())` setzen.

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

### PWA v1.16.2 – neues App-Icon (15.09.2026)
Das alte Icon war eine flache Teal-Kachel mit weissem Uhr-Umriss. Neu:
heller Creme-Hintergrund (wie `--color-background`), darum ein **24-Stunden-Ring**,
dessen Segmente die Dienstlage einfaerben (Bereitschaft blass-petrol,
Regeldienst petrol, Aktivzeit gruen), in der Mitte ein weisses Zifferblatt mit
Ziffern 12/3/6/9 und Zeigern auf 16:05 (planmaessiges Dienstende).
- Erzeugt von `make_icons.py` (Pillow, 4x Supersampling – PIL zeichnet ohne
  Antialiasing). Aendern heisst: Skript anpassen, `python3 make_icons.py`,
  nicht die PNGs von Hand bearbeiten.
- Farben/Zeigerstand stehen als Konstanten oben im Skript; die Segmentliste
  `SEGMENTS` hat genau 24 Eintraege (Index = Stunde, 0 Uhr oben).
- Ring-Aussendurchmesser bleibt bei 0,80 der Kantenlaenge, damit das Motiv in
  der maskable-Safe-Zone liegt (Android beschneidet auf einen Kreis).
- Icons stehen in der SHELL-Liste von `app/sw.js` und werden cache-first
  ausgeliefert: bei jedem Icon-Wechsel `CACHE` hochzaehlen (hier v11 → v12),
  sonst behalten installierte PWAs das alte Bild.

### PWA v1.20.0 – Tag-Tab kompakter, Einsatz-Buttons in einer Zeile (17.09.2026)

Erste Runde aus der Screenshot-Feedbackmappe des Nutzers (IMG_0556–0558).

- **Rote Tage**: `istRot(k)` (Sa/So/Feiertag) färbt Wochenstreifen und `#dayMeta`.
  Am aktiven Tag gewinnt das Weiß der Auswahlkachel.
- **Wochentag zweistellig**: `WDAY_KURZ` neben `WDAY`; `#dayMeta` zeigt „Do.
  17.09.2026 · Heute", die Dienst-Box „Do · …".
- **Dienst-Box von 3 auf 2 Zeilen** (121 px → 95 px, kein Umbruch mehr):
  Kopfzeile nur noch Wochentag + Dienstart bei 17 px statt 20 px, die zweite
  Zeile fasst Uhrzeit und Diensthabenden zusammen („11:00–18:00 · Plan: X").
  Die frühere `d.info`-Zeile entfällt und erscheint nur noch, wenn es keine
  Dienstart gibt.
- **Einsatz starten / Telefonat / „+" in einer Zeile** (`.stamprow`,
  `#einsatzRow`): grün / petrol / heller Icon-Button. Der frühere Untertitel
  „Beginn = aktuelle Uhrzeit" ist weg, das Icon ist ein Timer statt „+".
  Läuft ein Einsatz, bekommt die Zeile `.running` und der rote Stop-Button
  `flex:1.7`, damit „Einsatz beenden · seit 11:23 · 00:12:45" noch passt.
- **Gehen-Icon**: `logOut` statt `square`.
- **FRN-Checkbox rund**: `appearance:none` + `border-radius:50%` plus
  `::after`-Haken. Das native Kästchen ließ sich nicht rund bekommen – die
  vier Ecken blieben sichtbar.

### PWA v1.21.0 – Urlaub als Dienstart, ZD2 ist der Freitag (17.09.2026)

- **`ZD2` heißt jetzt „Rufdienst (Fr, ZD2)"** – `derive()` vergibt ZD2
  ohnehin nur am Freitag. Nachgezogen in `tagesdokumentation_erfassung.html`
  (geteilte Logik). **Nicht** in `build_html.py`: das Skript ist veraltet und
  erzeugt die heutige Erfassungsseite nicht mehr (dort stehen noch
  „Rufdienst (Werktag)"/„(Wochenende/Feiertag)"), ein Eingriff hätte dort
  nichts verbessert.
- **`URLAUB` als Dienstart** (ohne `start`/`end`, wie `FB`/`KRANK`), in allen
  drei Listen von `DIENSTART_BY_FUNKTION`. Zweck wie bei den anderen beiden:
  das Überstundenkonto füttern (Zeitart 705), wenn der Tag nicht (oder noch
  nicht) über die Urlaubsspalte des Dienstplans kommt.

**Die Doppelzählungs-Frage** (ausdrücklicher Nutzerwunsch: ein Tag darf nie
zweimal zählen, auch wenn er nach dem Excel-Import von Hand auf Urlaub
gestellt wird). Gelöst über eine erweiterte `istUrlaubstag()`:

```js
const istUrlaubstag = k => rufdienstCode(k) === 'URLAUB' ||
  (!(days[k] && days[k].dienstart_manuell) && derive(k).code === 'abwesend');
```

`URLAUB` steht bewusst **nicht** in `ABWESENHEIT` – sonst gäbe es zwei Wege
zur 705. Die Zuordnung darunter bleibt ein Ternär
(`istUrlaubstag(k) ? '705' : ABWESENHEIT[code]`), es entsteht also immer
genau eine Zeile. Getestet, jeweils eine Zeile:

| Fall | Ergebnis |
|---|---|
| Urlaub laut Excel (Mo) | 705, ist 8,42 h |
| Von Hand URLAUB an einem Regeldiensttag (Di) | 705, ist 8,17 h |
| Excel-Urlaub, von Hand auf Regeldienst gestellt | Zeitart 1, ist/soll 8,42 h |
| Wieder auf URLAUB | 705, ist 8,42 h |

Der dritte Fall ist nebenbei ein Bugfix: vorher hat der Excel-Urlaub die
manuelle Dienstart überstimmt und den Tag als 705 gebucht, obwohl gearbeitet
wurde.

Damit der Dienstplan-Urlaub auch sichtbar ist, belegt `renderDay()` die
Dienstart mit `URLAUB` vor, wenn `derive()` `abwesend` liefert (`abwesend`
ist kein `DUTY`-Code, das Dropdown stand sonst auf „– keine –"). Ohne
`dienstart_manuell` zählt das nicht als Eingabe, der Tag landet also nicht
im Verlauf. Die Dienst-Box sagt an solchen Tagen „Mo · Urlaub" statt
„Abwesend".

### PWA v1.22.0 – „wer hat wann Dienst" als Monatsraster (17.09.2026)

Die Karte war eine Liste aus 31 Zeilen („2026-10-01 · Donnerstag  [Name] ›"),
die man durchscrollen musste. Jetzt ist sie ein **7-Spalten-Monatsraster**
(`teamKalender(mk)`), eine Kachel je Kalendertag mit Tagesnummer und dem
Nachnamen auf zwei Buchstaben (`kurzName()`: „Zabelyshenskiy" → „Za").

- Gezeichnet werden **alle** Kalendertage, nicht nur die mit Plan-Eintrag –
  ein Kalender mit Löchern wäre keiner, und so lässt sich auch ein leerer Tag
  jemandem zuweisen. Die Zahl in der Monatsüberschrift bleibt die Zahl der
  Tage **mit** Eintrag.
- Kachel-Zustände: petrol gefüllt = eigener Dienst, oranger Rahmen =
  getauscht, rote Tagesnummer = Sa/So/Feiertag (`istRot()` aus v1.20.0),
  fette Nummer = heute, Outline = gerade geöffnet. Dazu eine kleine Legende.
- **Das Bearbeitungsfeld steht unter dem Raster**, nicht in der Zelle
  (`teamEdit(k)`, aus dem früheren `teamRow()` herausgelöst) – in eine
  44 px-Kachel passt kein Formular. Erneutes Antippen derselben Kachel
  schließt es wieder. `setSwap()` ist unverändert.
- Der zweizeilige Hinweis „Dienst getauscht? Tag antippen …" über der Karte
  ist weg (Nutzerwunsch).

**`renderGroupedList()` hat einen sechsten Parameter `bodyFn(mk, keys)`**, der
den Standard-Rumpf `<div class="list">…rowFn…</div>` ersetzt. Nur die
Team-Karte nutzt ihn; „Meine Dienste" und „Erfasste Tage" bleiben Listen
(dort hängen die .ics- und Sammel-PDF-Buttons am `footerFn`).

**Bewusste Umkehr gegenüber v1.8.0** („Monatsgruppen bleiben zugeklappt"):
solange der Nutzer in einem Container noch nie selbst auf- oder zugeklappt
hat, ist jetzt der **laufende Monat offen** und der Rest zu. Sobald
`openGroups[containerId]` existiert, gilt wieder ausschließlich sein
Zustand – auch eine leere Liste, also „alles zu", bleibt erhalten. Gilt für
alle drei Listen.

### PWA v1.23.0 – Monatsübersicht als eigene Tabelle (17.09.2026)

Neben „Sammel-PDF" (der amtliche Bogen, ein Blatt je Tag) steht in jeder
Monatsgruppe von „Erfasste Tage" jetzt ein zweiter Knopf **„Übersicht"**
(`data-monthtab` → `monatsTabellePdf(mk, info)`). Zweck laut Nutzer: Zeile für
Zeile gegen die TDA-Auswertung abgleichen. Deshalb steht **jeder Einsatz
einzeln** drin, und mehrere Blätter sind ausdrücklich in Ordnung.

Das ist ein **selbst gezeichnetes** PDF (`PDFDocument.create()`, Helvetica),
kein befülltes Formular – der amtliche Bogen hat für so eine Tabelle kein
Layout. Aufbau je Tag: eine fette Tageszeile (Datum · Dienstart · Dienstzeit ·
Überstunden · Grund) und darunter je Einsatz eine eingerückte graue Zeile
(Beginn–Ende · Art · Dauer · Anlass · Fall-Nr.). Am Ende eine Summenzeile
(Tage, Einsätze, Aktivzeit, Überstunden), auf jedem Blatt Kopf und
„Seite n von m".

Vier Dinge, die beim Nachbauen Ärger machen:

1. **Der Zebra-Streifen muss nach UNTEN wachsen.** Erste Fassung zeichnete
   `drawRectangle` ab `y` mit der Blockhöhe nach oben – das Rechteck des
   nächsten Tages hat damit die letzte Zeile des vorigen übermalt. Im
   Testlauf fehlten dadurch 10 von 28 Tagen im fertigen PDF, ohne dass ein
   Fehler geworfen wurde. Nur eine Sichtprüfung der gerenderten Seite fängt
   das; die Textextraktion allein hätte gereicht (`get_text()` zeigt
   übermalten Text nicht mehr), eine reine „PDF wurde erzeugt"-Prüfung nicht.
2. **pdf-lib zeichnet WinAnsi.** Alles außerhalb wirft beim `save()`. Die
   Freitexte (Grund, Fallnummer, Erläuterung) können aber alles enthalten,
   deshalb `san()`: Whitespace normalisieren und alles außerhalb von
   Latin-1 + den WinAnsi-Extras (`–`, `·`, `…`, typografische Anführungs-
   zeichen …) durch `?` ersetzen.
3. **Spaltentexte kürzen, nicht überlaufen lassen** – `fit()` schneidet mit
   `widthOfTextAtSize` auf die Spaltenbreite und hängt `…` an. Die
   Spaltenbreiten stehen als `TAB_SPALTEN` beieinander; sie müssen zusammen
   527 pt ergeben (A4 minus 2 × 34 pt Rand).
4. **Abwesenheitstage haben keine Dienstzeit.** `frei = istUrlaubstag(k) ||
   ABWESENHEIT[code]` unterdrückt Dienstzeit, Überstunden und Grund – sonst
   stehen dort Reste aus einem früheren Stand, und die Überstundensumme
   stimmt nicht (im Test 47,00 statt 35,50 h).

Eine Plausibilitätswarnung wie beim Sammel-PDF gibt es hier bewusst nicht:
die Übersicht dient dem Abgleich, da stört ein Dialog.

**Zum Testen** (cdnjs ist aus der Web-Session gesperrt, `PDFLib` also
undefiniert): `page.route('**/pdf-lib*.js', …)` mit der lokal per
`npm i pdf-lib` installierten `dist/pdf-lib.min.js` beantworten,
`teilePdf` im Seitenkontext durch einen Sammler ersetzen und die Bytes
per Base64 herausreichen. Gerendert wurde danach mit PyMuPDF
(`page.get_pixmap(dpi=120)`) – Playwright und Chromium liegen unter
`/opt/pw-browsers/chromium`, `playwright install` läuft hier nicht.

### PWA v1.23.1 – Lohnarten aufsteigend nach LA-Ziffer (17.09.2026)

`postenSortiert()` sortierte nach der festen Liste `LA_REIHE`
(`796,797,734,735,737,790,791,752,753,754,252,731` – gewachsen, nicht
begründet). Jetzt `sort((a,b) => a.la - b.la)`; `LA_REIHE` ist ersatzlos weg.
Die Aufstellung steht damit in derselben Reihenfolge wie die Abrechnung des
Klinikums: 050, 252, 731, 734, 735, 737, 752, 753, 754, 790, 791, 796, 797.

Die Grundvergütung (LA 050) ist kein Posten des Rechenkerns, sondern eine
eigene Zeile – in der Monatstabelle und im Textexport steht sie deshalb jetzt
**vor** den übrigen Zeilen statt dahinter, sonst bräche sie die Reihenfolge.
In der Verdienstleiste des Tag-Tabs bleibt sie unten als „Tagesanteil" vor
der Tagessumme: dort gibt es keine LA-Spalte, die Zeile ist Teil der
Summenbildung.

### PWA v1.24.0 – Sicherung mit Uhrzeit und Version (17.09.2026)

Dateiname jetzt `tagesdoku_backup_JJJJ-MM-TT_HH-MM_vX.Y.Z.json`. Datum bleibt
vorn (ISO, damit die Sortierung im Dateimanager stimmt), die Uhrzeit trennt
mehrere Sicherungen am selben Tag. **Bindestrich statt Doppelpunkt** – `:` ist
in Dateinamen unzulässig bzw. wird von macOS/iOS umgeschrieben.

Zusätzlich steht die Herkunft **in** der Datei, als erster Block:

```json
"meta": {"app":"Tagesdokumentation","version":"1.24.0",
         "build":"17.09.2026","erstellt":"2026-09-17T10:14:21.336Z"}
```

Der Import zeigt sie in der Rückfrage („Erstellt mit v1.24.0 am 17.9.2026,
10:14:21") und in der Erfolgsmeldung. Sicherungen **ohne** `meta` (alles vor
v1.24.0) laufen unverändert durch, die Herkunftszeile bleibt dann einfach
weg – der Import liest ohnehin nur die Schlüssel, die er kennt.

**Kompatibilität v1.19.1 → v1.24.0 geprüft** (echtes Backup des Nutzers,
153 Plantage, 20 erfasste Tage): dieselbe Datei in beide Versionen geladen,
Brutto je Monat auf den Cent gleich, Postenlisten und Mengen identisch,
Urlaubstage gleich, keine Fehler.

| Monat | v1.19.1 | v1.24.0 |
|---|---|---|
| 2026-06 | 3756,45 € | 3756,45 € |
| 2026-07 | 839,81 € | 839,81 € |
| 2026-08 | 829,57 € | 829,57 € |
| 2026-09 | 1095,23 € | 1095,23 € |
| 2026-10 | 1044,84 € | 1044,84 € |

Zwischen 1.19.1 und 1.24.0 hat sich **kein** Datenformat geändert; alle
Neuerungen (v1.20–v1.23) lesen dieselben Felder wie zuvor. Wer künftig etwas
am Format ändert, kann `meta.version` als Ansatzpunkt für eine Migration
nutzen – bisher braucht es keine.

### PWA v1.25.0 – Startet nachts auf dem Bogen des Vortags (18.09.2026)

Ein Anruf um 00:20 gehört auf das Blatt des Tages, an dem der Dienst begann –
sonst steht ein Dienst auf zwei Zetteln. Die App öffnet deshalb **vor 07:30
den Vortag**, ab 07:30 wieder den laufenden Tag:

```js
const START_UMSCHALT = 7*60 + 30;   // fruehester Dienstbeginn (Sa/So/Feiertag)
function startTag(){ … }            // liefert gestern oder heute
let cur = startTag();
```

Die Schwelle ist bewusst die früheste Dienstbeginnzeit (Wochenende/Feiertag
07:30), nicht die 11:00 der Werktage – ab 07:30 kann ein neuer Dienst laufen.

Für die **Gehaltsrechnung** ändert das nichts: der Adapter datiert
RB-Einsätze vor 06:00 ohnehin um (`cfg.nachtBuchung`, siehe v1.16.0), der
Einsatz zählt also weiterhin als 18.09. 00:20 für die Zuschläge, obwohl er
auf dem Bogen des 17.09. steht.

**Mitgezogen: der Live-Timer** in `renderEinsatzBtn()` hing an
`cur === iso(new Date())` und wäre nachts genau auf dem Bogen ausgefallen,
auf dem er gebraucht wird. Er hängt jetzt an `cur === startTag()`.
`laufzeitText()` rechnete schon über Mitternacht (negative Differenz + 24 h).

Getestet mit gefälschter Uhr (`page.clock.install`): 06:10, 07:29 → Vortag;
07:31, 09:00 → heute; 01.10. 02:20 → 30.09. (Monatswechsel). Ein um 00:20
gestempelter Einsatz landet im Tag 2026-09-17 und der Timer zählt hoch.

### PWA v1.26.0 / Desktop v1.7 – früher gekommen zählt als Überstunde (23.09.2026)

Überstunden = (Ist-Ende − Plan-Ende) **+ (Soll-Beginn − Dienstbeginn)**. Der
Soll-Beginn kommt aus der Dienstart (`DUTY[code].start` bzw. `data-start` der
Option im Desktop-Tool). Früher gekommen ist damit auch ohne Ist-Ende eine
Überstunde (09:30 statt 11:00 → 1,50 h), später gekommen wird negativ.
Ergebnis auf volle Minuten gerundet (`Math.round(ue*60)/60`), sonst bleibt
aus Fließkommaresten ein „0.00" in „Überstunden gesamt" stehen.
Gehaltsrechnung und Konto unverändert – der Adapter rechnete schon immer ab
`d.dienstbeginn`, nur das Formularfeld hatte ihn ignoriert. Der Verlauf nutzt
jetzt ebenfalls `calcFor()` statt einer eigenen Kopie der Formel.

### PWA v1.27.0 – Empfänger-Adresse für WeTransfer (23.09.2026)

Eine PWA kann weder eine bestimmte App ansteuern noch dem iOS-Teilen-Menü
einen Empfänger mitgeben. Deshalb: beim Erzeugen einer PDF (Einzel-PDF,
Sammel-PDF, Übersicht) kopiert `kopiereEmpfaenger()` die Adresse aus
`cfg.empfaenger` (Einstellungen → „PDF versenden", Default
`Alexander.Zabelyshenskiy@klf-net.de`, leer = nichts kopieren) in die
Zwischenablage und zeigt kurz einen `toast()`. In WeTransfer dann nur noch
„Einsetzen".

**Muss synchron am Anfang des Klick-Handlers stehen**: iOS erlaubt
`clipboard.writeText` nur innerhalb der Nutzergeste, nach dem `await` auf die
PDF-Erzeugung wäre sie verbraucht. Default per `??=`, damit ein bewusst
geleertes Feld leer bleibt.

**Zum Testen**: Playwright-Kontext mit `serviceWorkers:'block'` anlegen. Auf
`http://localhost` registriert sich sonst der Service Worker, das
`controllerchange` löst `location.reload()` aus, und der erste Klick geht ins
Leere – sieht aus wie ein Bug, ist aber nur das Testumfeld.
