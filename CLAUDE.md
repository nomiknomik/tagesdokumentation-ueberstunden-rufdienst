# Arbeitsnotizen (privates Hilfsprojekt)

Öffentliches Repo, nur wegen GitHub Pages. **Keine personenbezogenen Daten
committen**: keine Namen, Personalnummern, E-Mail-Adressen, Gehalts- oder
Kontostände, Backups, Dienstpläne. Beispiele immer mit Platzhaltern
(„Mustermann", „123456"). Der ausführliche Entwicklungsverlauf steht in der
Git-Historie der Commit-Nachrichten, nicht hier.

## Arbeitsweise
- Direkt auf `main` (Pages liefert aus `main`, `main` ist live). Kein PR.
  Gilt auch, wenn die Sitzung einen `claude/…`-Branch vorgibt: immer gleich
  auf `main` pushen.
- Vor dem Push `git pull --rebase`; bei Konflikt in `APP_VERSION` gewinnt die
  höhere Nummer, `CACHE` muss über beide hinausgehen.
- Vor dem Push rendern: Playwright gegen `app/index.html` bei 390 × 844.
  Chromium liegt unter `/opt/pw-browsers/chromium`. Kontext mit
  `serviceWorkers:'block'`, Dialoge mit `page.on('dialog', d => d.accept())`.
  cdnjs ist gesperrt: `page.route('**/pdf-lib*.js', …)` mit lokaler
  `npm i pdf-lib`-Datei beantworten.
- Nach dem Push (30–60 s) prüfen:
  `curl -s https://nomiknomik.github.io/tagesdokumentation-ueberstunden-rufdienst/app/index.html | grep APP_VERSION`

## Dateien
- `tagesdokumentation_erfassung.html` – Desktop-Tool für Kollegen, bettet das
  ausfüllbare PDF als Base64 ein (`PDF_B64`). Version im Footer („vX.Y"),
  bei jeder inhaltlichen Änderung hochzählen.
- `app/` – PWA (privat). Bei jeder Änderung `APP_VERSION` in `index.html`
  **und** `CACHE` in `sw.js` hochzählen.
- `Tagesdokumentation_Ueberstunden_Rufdienst_ausfuellbar.pdf` (auch in `app/`)
  – Original + 67 AcroForm-Felder. Kopfzeile Name/Personalnummer bleibt leer.
- `plan/` – Dienstplanung OA (Desktop, Wünsche auch am Handy), eigenständig, nur
  online. Daten im **Klartext** im privaten `tagesdoku-team`: `plan/config.json`
  (Team, Teams, Besetzung, Gruppenhinweise, Feiertage, Grenzen),
  `plan/wuensche/<Kürzel>/<JJJJ-MM>.json`, `plan/dienst/<JJJJ-MM>.json` (Plan,
  Protokoll, `veroeffentlicht.stand` für Tausch-Markierung). Zugang = Tagesdoku-
  Token (gleiche Domain, `tagesdoku_sync`/`tagesdoku_teilen`) oder Einladung
  (`planung_zugang`), Person in `planung_ich`. Schreiben über `aendern()`: Änderung
  als Funktion, auf frischen Repo-Stand neu angewandt (SHA-Konflikt → wiederholen).
  Hochladen gesammelt (Wunsch): alle 120 s, beim Verlassen von Fenster/Tab oder per
  Klick auf die Wolke (`#status`), nie je Eingabe. Pinsel im Wunsch-Kalender;
  Teilzeit-Muster `manuell` = Werktage frei außer Eintrag `da`. `PLAN_VERSION` bei
  jeder Änderung hochzählen; Klick auf die Version speichert und lädt ohne Cache neu.
  Plan als Liste oder Matrix (1 Zeile = 1 KW, `matrixHtml()`, nur > 760 px,
  Wahl in `planung_ansicht`); beide aus denselben Tagesdaten (`info`). Letzter
  Monat/Reiter je Gerät in `planung_monat`/`planung_tab` (Start/Update dort).
  Zoom −/+ im Kopf: CSS `zoom` auf `main` + `#dlg` (Kopf bleibt), Sticky-Abstände
  über `--z`, 70–200 %, je Gerät in `planung_zoom`. „Automatisch verteilen“
  (`autoVerteilen()`): nur leere Tage, engster Tag zuerst, rote Tags tabu, Fairness
  über 3 Vormonate + Monat als Saldo Ist − Erwartung (`erwartung()`: je Tag teilen
  sich die Anwesenden den Dienst, Abwesende 0; Vormonate nur Tage mit Plan;
  `vorherAlle()`), WE/Feiertage ebenso, Folgetage; Einträge `auto:true` (gestrichelt),
  „Vorschlag verwerfen“ entfernt nur diese.
  Matrix-Hinweise als Symbole neben dem Datum (! rot, ★ Kongress, i Gruppe), Text per Tooltip.
  Backup (Einstellungen): alle `plan/*.json` als eine JSON-Datei (`meta.app`='Dienstplanung',
  `files`), Einspielen ersetzt gleichnamige Dateien – in EINEM Commit über die
  Git-Data-API (Baum mit Inhalten → Commit → Ref), nicht Datei für Datei.
  Tooltips sofort über `#tip` (global: `title` wird beim Überfahren zu `data-tip`).
  Besetzung nur Vormittag / Nachmittag (vor/ab 11; `besRegel()` fasst alte 3-Fenster-
  Konfiguration zusammen), keine Dienstart (ZD1…)
  in der Oberfläche – Funktionen statt Abrechnungsart folgen später.
  Reiter Urlaub: durchgehend scrollend (lädt an den Enden je ein Jahr nach,
  `urlVon`/`urlBis`), Kopf = Monat in Bildschirmmitte; Wunschdateien je Jahr über
  `git/trees` (`ladeJahr()`); Zähler = Urlaub an Werktagen vs. `cfg.urlaubPlan`
  (25) von `cfg.urlaubAnspruch` (31). Schnellwahl Dienst: 1. Buchstabe Nachname,
  ab 2. auch Initialen (Nachname+Vorname) oder Kürzel. Matrix zeigt Nachbarmonate
  blass + je eine angeschnittene Woche (Klick = Nachbarmonat); Monatswechsel im Plan
  nur über den Kopf, nicht per Scrollen. Veröffentlichung zurücknehmen: Planer oder `tagesdoku_admin`.
  Termine (`cfg.termine` = `[{id, art: ferien|kongress|sonst, name, tage[]}]`, alt:
  `von/bis`) tageweise pinselbar; BW-Schulferien fest in `BW_FERIEN` (aus schulferien.org-
  ICS bis 01/2028), weitere Jahre per ICS-Import (`#termIcs`, DTEND exklusiv);
  Winterferien legt jede Schule selbst fest → von Hand. Urlaub-Kacheln: Besetzung
  vorm.|nachm. (`urlBesetzung()`; Vortags-Dienst zählt als da, heutiger Dienst –
  auch noch offen – erst nachmittags),
  Tooltip = nur Anwesende (eine pro Zeile). Kongresse
  auch im Dienstplan; alle Termine dort als dezente Farbbalken oben (`terminBand()`).
  Diensthabender zählt ab 11 (Nachmittag), Vortags-
  Dienst = „fehlt evtl.“. Max. Dienste = 13 × Quote (TV-Ärzte/VKA, ungeprüft).
- `add_fields.py`, `build_html.py` (veraltet, erzeugt die heutige HTML nicht
  mehr), `make_icons.py` (App-Icon, Pillow).

## Geteilte Logik (in BEIDEN Tools pflegen)
Dienstart-Labels und -Zeiten (`DIENSTART_OPTIONS` im Desktop-Tool, `DUTY` in
der PWA), Überstundenrechnung (Ist-Ende − Plan-Ende + Soll-Beginn − Beginn;
Ende vor dem Beginn zählt als Folgetag, +24 h), FRN-Verhalten. Alles andere in der PWA ist PWA-exklusiv.

## PDF-Fallen
- `/DA` als Hex-String schreiben: pypdf escaped sonst `/` als `\057`, pdf-lib
  scheitert daran. **pypdf nicht zum Umschreiben der fertigen PDF benutzen**
  (serialisiert `/DA` neu) – kleine Änderungen längengleich byteweise.
- AcroForm braucht `/DR` mit `/Helv`; jedes Feld `/BS {W:0}` + leeres `/MK`
  (sonst Rahmen in pdfium/Edge/PDF24).
- Feldkoordinaten nur aus `page.get_drawings()` (PyMuPDF), nie schätzen.
- pdf-lib zeichnet nur WinAnsi → Freitexte über `san()`.
- Nach Änderungen Nutzer bitten, in Edge/PDF24 zu prüfen.

## PWA-Fallen
- `syncHeaderPad()` misst Header/Nav/Leiste und reserviert die
  **aufgeklappte** Höhe der Verdienstleiste.
- Verdienstleiste klappt nur über den Scrollstand (`geldBarPruefen()`), kein
  zweiter Zustand.
- Block `>>>>> gehalt.js BEGINN` … `<<<<< gehalt.js ENDE` ist fremder Code
  (IIFE), nur als Ganzes austauschen. Der Adapter darunter übersetzt
  Feldnamen und datiert Nacht-Einsätze vor 06:00 einen Tag zurück.
- Überstundenkonto: pauschal 30 min Pause ab 6 h von Ist UND Soll – ändern
  nur, wenn LA 731 danach gleich bleibt.
- Ab 09/2026 werden Überstunden an Rufdienst-Beginntagen zum 734-Satz
  ausgezahlt (`ueAuszahlStd()`, Posten „ÜA“, außerhalb gehalt.js); 731 bleibt.
  Auf dem Konto bleiben sie, bis die TDA die Auszahlung bucht (`kontoFuer()`
  zeigt sie nur als „davon zur Auszahlung vorgesehen“; TDA 09/2026 bestätigt).
- Abwesenheit hängt nur an der Dienstart (`ABWESENHEIT`, `URLAUB` über
  `istUrlaubstag()`), nie an der FRN-Checkbox; ein Tag zählt nie doppelt.
- LA 031 Aufschlag Urlaub (`urlaubsaufschlag()`): variable Bezüge der
  Leistungsmonate **V−5…V−3** geteilt durch **71,5** (13 Wochen × 5,5 Tage),
  mal Urlaubstage. Genauigkeit rund ±1 %, ruht auf zwei Abrechnungen – Posten
  und Tagesnotiz bleiben mit `*` als Schätzung markiert. Fehlen die drei
  Vormonate in der Erfassung, gehen sie mit 0 € ein; dafür steht die
  ⚠️-Warnung in `#gmWarn`, die nicht entfernt werden darf.
- Grundgehalt nur aus den Einstellungen (`cfg.gehalt.verlauf` = `[{ab, grund}]`,
  `grundFuer(ym)`; ältester Betrag gilt auch rückwirkend), nie im Code.
  `gehaltSaetzeSetzen(ym)` setzt daraus 734/796/797 (÷ 173,92) ins
  `GEHALT.SAETZE_*`-Objekt des Monats – deshalb Euro nur über `euroFuer()`
  rechnen. Übrige Zuschläge bleiben tarifweit.
- Dienstplan-Import liest Spalten nach Überschrift (im Oktober-Plan fehlt
  „Urlaub“). Spalte Anwesenheit = Teilzeit: steht das eigene Kürzel im Monat
  dort, sind nur diese Wochentage Arbeitstage (`teilzeitMonat()`), Rest „frei“.
- Arbeitsquote (`quote` in `cfg.gehalt.verlauf`, `quoteFuer(ym)`, leer =
  100 %): Stundenentgelt = Grund ÷ (173,92 × Quote); Konto-Soll über
  `kontoMonat()` × Quote; Abwesenheitsgutschrift × Quote, außer in
  Teilzeit-Monaten über Spalte Anwesenheit (dort ganze Tage).
- Erster Start: `#startBox` fragt QR / Zugangsdaten / offline, Wahl in
  `tagesdoku_modus` (nur Gerät, nicht im Backup), änderbar über `#syncModus`.
  Bestehende Installationen mit Daten werden nicht gefragt.
- Einstellungs-Karten (`#cfg > .card`) sind ein Akkordeon (`karteAuf()`,
  Klasse `offen`), Start alle zu. Wer per Code in die Einstellungen springt,
  muss die Zielkarte mit `karteAuf(el)` öffnen.
- Erste Online-Sicherung auch ohne Tage, sobald Einstellungen gesetzt sind
  (`einstellungenGesetzt()`).
- `hasContent()` entscheidet, was als erfasst gilt; `persist()` und Export
  speichern nur solche Tage (`echteTage()`).
- Zeit-/Tagesrechnung über UTC-Tagesnummern (DST).
- `clipboard.writeText` synchron am Anfang des Klick-Handlers (iOS-Geste).
- Service Worker: `index.html` network-first, Rest cache-first, `api.github.com`
  nie über den SW. Neu laden nach SW-Wechsel nur bei Update, nie beim ersten Besuch
  (`ersterBesuch`) – sonst geht ein per Link geöffneter Einladungs-Code verloren.
  Playwright-Tests mit `serviceWorkers:'block'` sehen das nicht.
- Backup/Sync: `save()` setzt `tagesdoku_dirty`; Sync-Zugangsdaten
  (`tagesdoku_sync`) nur über `saveSync()`, nie im Backup. Online-Datei im
  privaten Repo, AES-GCM/PBKDF2, Abgleich über Datei-SHA. Dateiname
  `tagesdoku_<PBKDF2(Personalnr.\nPasswort)>.json` (`dateiErmitteln()`, `sync.datei`),
  keine Namen im Repo; alte `tagesdoku_backup[_<name>].json`, die eigene
  Vorgängerdatei (`sync.altDatei`) und das 1.51-Schema (nur Passwort) werden per
  Passwort-Probe gefunden und umbenannt – fremde Hash-Dateien nie proben.
  Passwort und PIN ohne Mindestlänge (Wunsch). Zugangs-Link und QR-Code
  (`#zugang2=`) sind mit PIN verschlüsselt (AES-GCM, PBKDF2 600k), die PIN steht
  nie im Code, Öffnen nur mit PIN-Eingabe. Gültig 24 h (`ZUGANG_GUELTIG`,
  `bis` im verschlüsselten Inhalt); Codes ohne `bis` und alte unverschlüsselte
  `#zugang=`-Links sind gesperrt. Reine App-Prüfung, der Token selbst bleibt gültig.
  Mit Gist-Token (nur Admin, `tagesdoku_teilen.gist`) liegt der verschlüsselte
  Code als geheimer Gist (`GIST_BESCHR`), der Link trägt nur `#einladung=<id>`;
  `gistsAufraeumen()` löscht beim Start Gists älter als 24 h. Laden: API, bei Fehler Rohdatei
  `gist.githubusercontent.com/<owner>/<id>/raw/einladung.txt` (API ohne Anmeldung
  ~60/h je IP, Klinik-WLAN). Fehler im PIN-Fenster anzeigen, nicht per Toast.
- Timer-ID 1 ist frei: `HIST.timer = -1` beim Start (mit 1 löschte
  `clearTimeout` den ersten echten Timer).
  Standard ist die Nutzer-Ansicht: Repo, Token und „Zugang weitergeben“
  ausgeblendet (`zugangAnsicht()`), nur Personalnummer (`sync.kennung`, füllt
  leere Kopfdaten-`cfg.pnr`) + Passwort. Admin nur mit `tagesdoku_admin`='1'
  (Gerät): Migration = hat `tagesdoku_teilen` oder synct von Hand mit eigenem
  Repo (≠ `TEAM_REPO`); sonst „Admin-Anmeldung“ mit Gist-Token, geprüft über
  `GET /user` = Besitzer des Team-Repos. Oder per Admin-QR („Admin-Gerät
  hinzufügen“): PIN-verschlüsselt mit `g` (Gist-Token) und `admin:1`, nur als
  QR (kein Link/Gist), setzt Flag und `tagesdoku_teilen`, eigener Sync unberührt. Admin sieht den Token im Klartext,
  PIN wird in `tagesdoku_teilen` gemerkt. Nur Anzeige – der Token liegt technisch im Browser. „Lokal geändert“
  heißt Prüfsumme ≠ `sync.hash` (Dirty-Flag allein ist nur ein Vorfilter).
  Haben beide Seiten geändert: Drei-Wege-Abgleich je Eintrag gegen die Basis
  (IndexedDB `kv/basis`), Rückfrage nur bei echten Kollisionen; vor jeder
  Übernahme bleibt eine Geräte-Kopie „-vorher“.
  Kopf-Symbol `#syncBtn` über `syncStatus()`; `save()` lädt nach 20 s Ruhe hoch.

## Bekannte Abweichungen App ↔ TDA (für Gehaltsabgleich)
- 09/2026, ein Wochenend-RBD: TDA hat alle Einsätze pauschal als 9005 „RB aktiv
  ausz." (Präsenz/RBA) gebucht, die App führt 6 davon als telefonisch (RBT).
  Bewusst so belassen. Zeiten und Dauer sind identisch, Summen sollten gleich
  sein; bei Abweichung im Gehalt zuerst hier prüfen.
