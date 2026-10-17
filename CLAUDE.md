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
  Abruf-Limit: alle Geräte teilen den Team-Token (5000/h, auch Tagesdoku) → `lesen()` mit ETag
  (304 zählt nicht), `ladeAlles()` holt nur Dateien, die laut `baumHolen()` (ebenfalls ETag) existieren.
  Hochladen gesammelt (Wunsch): alle 120 s, beim Verlassen von Fenster/Tab oder per
  Klick auf die Wolke (`#status`), nie je Eingabe. Pinsel im Wunsch-Kalender;
  Teilzeit-Muster gelten nur an Werktagen (`teilzeitFrei()` → nie WE/Feiertag);
  `manuell` = Werktage frei außer Eintrag `da`. Bruch eines laufenden Blocks (anwesend an Block-frei, frei an
  Block-Arbeitstag, Dienst an Block-frei, nicht bei auto) beendet ihn am Vortag (`blockBruch()`). `da` hat keinen Chip (= weiße
  Kachel); an normalen Arbeitstagen entfernt der Pinsel „anwesend“ nur `frei`. `frei` = schraffiert
  ohne Chip (an Teilzeit-freien Tagen entfernt der Pinsel nur `da`). Typ `fza` = Freizeitausgleich (abwesend).
  Im Wunschkalender ist jede Abwesenheit (Urlaub, FB, FZA, frei) zusätzlich schraffiert.
  Rückgängig/Wiederholen (1.37, Kopf + Strg+Z/Y): max. 10 Schritte, Schritt = alle `aendern()` einer
  Aktion (Klick bzw. Pinselstrich); setzt per `diffPfade()` nur die geänderten Stellen zurück, über
  `aendern()` auf den frischen Stand – fremde Änderungen bleiben. Neues Muster beendet
  laufende am Vortag (Rückfrage). Datumsfelder, die render() auslösen: erst bei Blur/1,5 s Ruhe speichern. `PLAN_VERSION` bei
  jeder Änderung hochzählen; Klick auf die Version speichert und lädt ohne Cache neu.
  Plan als Liste oder Matrix (1 Zeile = 1 KW, `matrixHtml()`, nur > 760 px,
  Wahl in `planung_ansicht`); beide aus denselben Tagesdaten (`info`). Letzter
  Monat/Reiter je Gerät in `planung_monat`/`planung_tab` (Start/Update dort).
  Zoom −/+ im Kopf: CSS `zoom` auf `main` + `#dlg` (Kopf bleibt), Sticky-Abstände
  über `--z`, 70–200 %, je Gerät in `planung_zoom`. Plan-Leiste (Ansicht … Signieren, 1.90) klebend unter dem Kopf
  (`--kopfH`), seit 1.91 über volle Breite (vor `.planwrap`), Desktop bricht um, Handy einzeilig wischbar;
  Plan-Reiter breiter (`body.weit`, 1760 px); Sticky-Köpfe darunter addieren `--werkH` (ResizeObserver). „Automatisch verteilen“
  (`autoVerteilen()`): nur leere Tage, engster Tag zuerst, rote Tags tabu, Fairness
  über 3 Vormonate + Monat als Saldo Ist − Erwartung (`erwartung()`: je Tag teilen
  sich die Anwesenden den Dienst, Abwesende 0; Vormonate nur Tage mit Plan;
  `vorherAlle()`), WE/Feiertage ebenso, Folgetage; Einträge `auto:true` (gestrichelt),
  „Vorschlag verwerfen“ entfernt nur diese.
  Wochenende (1.93, `weBlock()` = Fr+Sa+So): Fr+So eine Person (Bonus „passt zu Fr/So“ +35), Sa eine andere
  (seit 1.94 Reihenfolge in `autoVerteilen()`: Tage mit nur 1 Kandidat → Fr+So als Paar (`kandFuer()`, gleiche Person mit
  bester Summe) → Sa → Feiertage → Rest; Dienst am Vor-/Folgetag = 'r', zwei Dienste in Folge verboten); Ziel 1–2 WE je Monat (`weImMonat()`, 3. WE −40);
  Seit 1.96 plant `autoVerteilen()` komplett im Speicher (`SIM` – `dienstVon()`/`diensteIm()` lesen ihn zuerst), Ziel je Person
  = `erwartung(ym).exp` + Rückstand Vormonate (±1), über dem Ziel stark abgewertet; danach `verbessern()`: Pakete
  (Fr+So zusammen) verschieben/tauschen, keine rote Regel (auch Nachbartage); seit 1.97 angenommen, wenn
  25·ΔJ + ΔKosten < 0 (J = Σ(Ist−Ziel)² + 2·Σ(WE−ZielWE)², Kosten = −(score+n·3) + 30 je weichem Verstoß über alle
  Dienste der beteiligten Personen im Monat – WE-Serie, weiches No-Go usw.); erst dann `einteilen()`. Keine Fair-Anzeige (Wunsch).
  WE-Fairness (1.95) je Block: Erwartung `expWeB` = je Samstag 2 Einsätze nach Arbeitsquote (auch bei Teilzeit-Muster),
  Saldo über 3 Vormonate + Monat × 25 in `autoVerteilen()` – Rückstand wird nachgeholt; Tages-WE-Fairness nur noch Feiertage Mo–Do;
  WE angrenzend an Urlaub tabu ('r', Nachbar-Arbeitstag über `werktagNeben()`), an Fortbildung −25.
  1.98: „3. WE im Monat“ zählt auch, wenn das WE schon eingeteilt ist (andere Blöcke ≥ 2); Dienst Mo–Do vor einem
  Abwesenheitstag (geht bis 7:30, wirkt wie Fr) = 'o' „vor Abwesenheit“ −25; drei Dienste jeden 2. Tag = 'o' −10;
  weicher Verstoß kostet in `verbessern()` 45.
  Typ `krank` (1.93, abwesend, keine Freigabe, TDA „KA*“).
  Matrix-Hinweise als Symbole neben dem Datum (! rot, ★ Kongress, i Gruppe), Text per Tooltip.
  Backup (Einstellungen): alle `plan/*.json` als eine JSON-Datei (`meta.app`='Dienstplanung',
  `files`), Einspielen ersetzt gleichnamige Dateien – in EINEM Commit über die
  Git-Data-API (Baum mit Inhalten → Commit → Ref), nicht Datei für Datei.
  Dienst löschen (1.60): Maus über Tag + Entf/Rücktaste (`planHover`), im Auswahl-Dialog Entf = Leeren,
  am Handy nach links wischen > 80 px (`dWisch`, `.dzelle` touch-action pan-y; Klick danach ignoriert).
  Personenauswahl beim Einteilen erscheint neben der Maus (`dialog(…, nahe)`, letzte
  Klickposition `klickXY`, im Fenster gehalten, Zoom berücksichtigt).
  Tooltips sofort über `#tip` (global: `title` wird beim Überfahren zu `data-tip`).
  Besetzung nur Vormittag / Nachmittag (vor/ab 11; `besRegel()` fasst alte 3-Fenster-
  Konfiguration zusammen), keine Dienstart (ZD1…)
  in der Oberfläche – Funktionen statt Abrechnungsart folgen später.
  Reiter Urlaub: durchgehend scrollend (lädt an den Enden je ein Jahr nach,
  `urlVon`/`urlBis`), Kopf = Monat in Bildschirmmitte; am Handy (Touch, 1.50): Wischen scrollt, Tippen = 1 Tag,
  Streichen erst nach 0,4 s Halten (`urlTouch`, Strich = 1 Rückgängig-Schritt); Pinsel (`#urlTab.malt`,
  gestrichelt) bleibt bis 3 s nach dem Loslassen aktiv (`urlMalModus()`), solange malt jede Berührung sofort.
  Touch-Listener hängen am berührten Element (`urlTouchHoeren()`) – render() löst es ab, Events bubbeln dann nicht mehr, Werkzeug als feste Leiste unten; Wunschdateien je Jahr über
  `git/trees` (`ladeJahr()`); Zähler = Urlaub an Werktagen vs. `cfg.urlaubPlan`
  (25) von `cfg.urlaubAnspruch` (31). Schnellwahl Dienst: 1. Buchstabe Nachname,
  ab 2. auch Initialen (Nachname+Vorname) oder Kürzel. Matrix zeigt Nachbarmonate
  blass + je eine angeschnittene Woche (Klick = Nachbarmonat); Monatswechsel im Plan
  nur über den Kopf (Doppelklick auf den Monat = aktueller Monat, 1.87), nicht per Scrollen. „Veröffentlichen“ heißt in der Oberfläche **Signieren** (Daten weiter `veroeffentlicht`), nur Planer
  oder `tagesdoku_admin` (`darfVeroeffentlichen()`), auch Zurücknehmen.
  Protokoll (1.51): Wunschdateien führen `log` [{am,von,tag,alt,neu}] wie die Dienstdatei – über
  `mitLog()` in `aendern()` (Codes `wCode()`: Typ + ✓ genehmigt + ! hart); Rückgängig setzt `log`
  nie zurück. Kopf-Knopf `#protoBtn`: Dialog „Offen“ (beantragt: Urlaub/FB/FZA, nur `darfVerwalten()`,
  Zähler-Badge, `todoLaden()` = aktuelles + nächstes Jahr) und „Protokoll“ (Striche ≤ 2 min
  zusammengefasst; vor 1.51 nur Eintragszeit `am` am Eintrag). Seit 1.67 lädt `protoLaden()` Wunschdateien
  Vorjahr–Folgejahr + Dienstdateien ±12 Monate; Filter `protoF` (`zeit` = geändert in den letzten 1/7/30 Tagen seit 1.68, Monat des betroffenen Tags, geändert von,
  betroffen = `betr`, Art `protoArt()`), max. 300 Zeilen. Dienst-`log` auf 2000 Einträge begrenzt.
  Rückmeldung (1.69, Kopf `#hilfeBtn` „@“): erst `appFoto()` (html2canvas-pro 1.5.11 von jsdelivr – 1.4.1 kann kein
  color-mix; `ignoreElements` #dlg/#tip/.toast), dann `meldeDialog()`; Häkchen „Screenshot anhängen“ Standard AUS
  (Wunsch, Vorschau erst nach Aktivieren). Ablage `plan/meldungen/<zeit>-<kürzel>.json` (+ `.jpg`) direkt per `gh('PUT')`;
  Admin-Gerät: öffnet direkt „Meldungen“ (ohne Screenshot, 1.70), Zähler `hilfeBadge()`, Bild über `ghRoh()`,
  Tippen = `bildGross()` (Ebene, Tippen = Originalgröße, statt Download), Status offen/erledigt.
  Test nur über http (file:// „tainted canvas“).
  Rechte (seit 1.31, nur Oberfläche – der Team-Token darf technisch alles): `darfVerwalten()`
  = Planer/Admin/niemand ist Planer; Einträge darf seit 1.67 jede:r für alle (`darfFuer()` = true, Genehmigtes nur Planer), Einstellungen
  ausgeblendet (`cfgSperren()`, Karte `.frei` ausgenommen). Person wechseln (Kopf `#ichBtn`, `#ichWechsel`)
  seit 1.61 nur auf dem Admin-Gerät (`adminGeraet()`), auch nicht der Planer. Seit 1.63 kommen die Rechte
  immer von der gewählten Person (`istAdmin()` nur ohne gewählte Person) – der Admin sieht genau ihre
  Ansicht, die Personenwahl bleibt sein Rückweg. Wünsche/Urlaub öffnen seit 1.65 immer mit der eigenen Person (`fuerK`/`urlK` = `ichK` beim Reiterwechsel; Doppelklick im Plan setzt danach); seit 1.66 sind dort alle Personen wählbar, fremde ohne `darfFuer()` nur ansehen (`#meinLesen`, Pinsel aus, rechte Spalte gesperrt). Kopf-Knopf `#ichBtn` seit 1.64 nur auf dem Admin-Gerät, seit 1.91 ganz ausgeblendet (Personenwahl nur noch in der Karte Zugang); „Angemeldet als“ für alle in der Karte Zugang. Ohne gewählte Person darf jedes Gerät einmal wählen.
  1.62: „Admin-Anmeldung“ in der Karte Zugang (Gist-Token, `GET /user` = Besitzer `TEAM_REPO`, setzt
  `tagesdoku_admin`) und „Repo und Token direkt“ im Erstlogin seit 1.71 nur über `…/plan/#admin` (`ADMIN_TUER`) oder
  seit 1.72 7 schnelle Tipps (4 s) auf das Kopf-Logo bzw. den Erstlogin-Titel (`fuenfTipps()`, auch für installierte App) –
  Notausgang: neuen GitHub-Token erzeugen; Nicht-Verwalter sehen in den Einstellungen nur die Karte `.frei` (Zugang).
  Lese-Zugänge (1.86, Rolle `sek` = Sekretariat, `pa` = PA, `LESER`/`istLeser()`): Konten in `cfg.personen`, aber
  nicht in `personen()` (keine Dienste/Besetzung; `konten()` für Personenwahl/Einladung). Nur Plan als Matrix/Woche
  (+ Zugang in Einstellungen), kein Urlaub-Reiter, kein Protokoll, `darfEinteilen()`/`darfVerwalten()` false;
  Sekretariat zusätzlich Wünsche, dort nur Chefarzt wählbar und `darfFuer()` nur für Rolle `chef`.
  Halber Tag weg (1.58, Typ `halb`, `zeit` 'vm'|'nm', `uhr` = freier Text): nicht `abw`, zählt nur im
  eigenen Besetzungsfenster (`halbWeg()` in `besetzung()`/`urlBesetzung()`); Pinsel „½ Tag“ im Urlaub-Reiter
  , in der Wunsch-Pinselleiste (1.84, mit vorm./nachm. + Uhrzeit `halbUhr`) und im Wunsch-Dialog nur beim Chef (`rolle` 'chef'), Anzeige bei allen (halb gefüllter Chip). Keine Freigabe.
  Urlaub, FB und FZA (`FREIGABE`/`pflicht()`, seit 1.52) = Antrag; Planer genehmigt je Monat im Urlaub-Reiter (`genehmigKnopf()`/`genehmigen()`,
  `ok:{von,am}` am Eintrag, genau der Stand beim Klick). Beantragt = gestrichelt; Genehmigtes
  ändert nur der Planer (`gesperrtFuer()`). Abwesend zählt er schon als Antrag.
  TDA-Ansicht (1.46, intern `kompakt`, dritte Wahl neben Liste/Matrix, `kompaktHtml()`): Monat wie TDA – Zeilen
  „Nachname, Vorname (Pers.-Nr.)“ (`p.pnr`, Team-Tabelle), Spalten Tage, Sa gelb, So/Feiertag grün;
  Codes ZD1/ZD2/RBD1/RBD2, U*, F0* (Bezeichnungen wie Original-TDA seit 1.92, `TDA_ABW`), FZA, 0 (frei/WE), Feiertag-Spalte türkis, Regeldienst Amb2 (Mo)/Amb4 (wie Tagesdoku `derive()`). Ohne Seitenleiste; Drucken = A4 quer.
  Seit 1.54 nur Planer/Admin (`darfVeroeffentlichen()`), Zeilen nach Nachname. Reine Ansicht (1.56): Klick
  auf ein Feld (`tdaWahl()`/`tdaSetzen()`) ändert nur echte Daten – Dienstcode → `einteilen()` (Vorgänger
  fällt auf Regeldienst zurück), U*/F0*/FZA → Wunsch-Eintrag als Antrag (1.57, nicht genehmigt; in TDA gestrichelt unterstrichen), Regeldienst (Amb2 Mo/Amb4
  Di–Fr, `tdaRegel()`) → anwesend (`da` an Teilzeit-freien Tagen), 0 → `frei`; WE/Feiertag nur Dienst/0.
  Keine eigenen TDA-Codes (die `tda`-Felder aus 1.54/1.55 in Dienstdateien werden ignoriert).
  Chef (1.59): kein Amb/Dienst – ganztags da = leer, halber Tag = „Vorm.“/„Nachm.“ (anwesende Hälfte, auch
  bei OA mit `halb`); Wahl U/Fo/FZA/ganztags/Vorm./Nachm./0 (Vorm. = `halb` mit `zeit:'nm'`).
  Woche (1.85, vierte Plan-Ansicht, alle, auch Handy, `wocheHtml()`): Sprechstunde/OP-Planung, nur Mo–Fr, je Tag
  die Anwesenden (nur Nachname ohne Kürzel seit 1.87, nach Nachname, Zusatz „ab 11“ = Dienst, „n. D.“ = nach Dienst, vorm./nachm. bei `halb`), Zahl
  vorm.|nachm. wie `urlBesetzung()`, „weg:“ + Termine; ab aktueller Woche (sonst Monatsbeginn) bis Ende Folgemonat,
  endlos scrollend (1.89, IntersectionObserver auf `#woMehr`, lädt je einen Monat nach, max. 24 Monate; `wocheMehr`, `wocheLaden()`); ≤ 760 px je Tag eine Zeile. Reine Ansicht.
  Seit 1.88 je Monat ein Abschnitt (`.wo-monat`, Wochen am Monatswechsel geteilt, Trennlinie), Kopf mit Monat +
  Wochentagen bleibt beim Scrollen oben (sticky unter dem App-Kopf über `--kopfH`, per ResizeObserver gemessen);
  keine KW-Zeilen, Kachel nur Tageszahl (am Handy „Mo 9.“, Wochentagszeile dort ausgeblendet).
  Wochenpläne drucken (1.45, `#wochenBtn`): alle Wochen des Monats, je Seite A4 quer (`wochenplanHtml()`,
  `body.wochendruck` blendet beim Druck alles außer `#wochendruck` aus).
  Einladung (seit 1.33, 72 h, ein Link je Person für alle Geräte; Gist `planung-einladung`, eigenes
  `gistsAufraeumen()`): PIN-verschlüsselt wie Tagesdoku mit
  `p` = Kürzel → Gerät fest dieser Person (`planung_ich`); Gist über `tagesdoku_teilen.gist`, sonst `#zugang2=`. QR aus `../app/qrcode.js`.
  Dienste einteilen/tauschen bleibt für alle offen (`darfEinteilen()`, `gruppen.oa.einteilen`).
  Design (1.39, zwischen alt und ruhig): Matrix-Dienst zart in Personenfarbe (`--f`, color-mix),
  ohne Farbstreifen, Kürzel farbig; Tage weiß, WE schlicht. FZA auch im Urlaub-Reiter (Chip + Pinsel). Icon `icon.svg`
  (+ PNG 180/192/512, `manifest.webmanifest`) – PNGs aus dem SVG per Playwright rendern. Kopf-Logo `logo.svg` = gleiches Motiv ohne Petrol-Kachel (Pfeile petrol).
  Termine (`cfg.termine` = `[{id, art: ferien|kongress|sonst|feiertag, name, tage[]}]`, alt:
  `von/bis`) tageweise pinselbar; Art `feiertag` (1.75, nur Planer) = arbeitsfrei wie gesetzlicher Feiertag
  (`ftExtra()` in `feiertag()`; alte `cfg.feiertage` werden beim Planer einmal dorthin verschoben, Einstellungen
  zeigen nur noch die automatischen BW-Feiertage). BW-Schulferien fest in `BW_FERIEN` bis Sommer 2030
  (laut Kultusministerium, Stand 10/2026; Herbst 2030 noch offen; `u` = ⚠ prüfen für spätere Drittquellen), immer über `werktagKern()` auf Mo–Fr gekürzt (offizielle
  Angaben enden oft am Samstag); weitere Jahre per ICS-Import (`#termIcs`, DTEND exklusiv, ebenfalls gekürzt);
  Regel-Typ `nachFreiWE` (1.79): kein Dienst am Montag (nur Arbeits-Montag, nicht Feiertag; Ferien egal – 1.81), wenn Sa+So kein eigener Dienst (`regelFreiWE()`, in `bewerte()` und
  Wunschkalender), weich/hart wie andere Regeln; `wt` fest 1. Gegenstück `prefNachFreiWE` (1.80): Montag nach freiem Wochenende bevorzugt (wie `pref`).
  Fortbildung (1.82) auch an Wochenenden/Feiertagen pinselbar, zählt dort im FB-Zähler und erscheint in TDA als „F0*“.
  Wunschkalender zeigt Termine seit 1.78 ebenso (Balken `terminBand()`, Name am 1. Tag/montags, Ferien hellblau).
  Doppelklick auf einen Termin rechts scrollt den Urlaub-Kalender zum ersten Tag (`urlZuTag()`, 1.77, Kachel blinkt).
  Winterferien legt jede Schule selbst fest → von Hand. Urlaub-Kacheln: Besetzung
  vorm.|nachm. (`urlBesetzung()`; Vortags-Dienst zählt als da, heutiger Dienst –
  auch noch offen – erst nachmittags),
  Tooltip = nur Anwesende (eine pro Zeile); Gruppenhinweise (`hinweise()`) seit 1.83 als „i“ (`.ur-hw`) + im Tooltip. Kongresse
  auch im Dienstplan; alle Termine dort als dezente Farbbalken oben (`terminBand()`).
  Diensthabender zählt ab 11 (Nachmittag), Vortags-
  Dienst = „fehlt evtl.“. Max. Dienste = 13 × Quote (TV-Ärzte/VKA, ungeprüft).
- `add_fields.py`, `build_html.py` (veraltet, erzeugt die heutige HTML nicht
  mehr), `make_icons.py` (App-Icon, Pillow).

## Daten & Speicher-Prinzipien (Dienstplanung, Stand 1.74)
- GitHub-Repo `tagesdoku-team` ist die Datenbank: eine JSON-Datei je Monat (Dienst) bzw. je Person und
  Monat (Wünsche), klein halten. Hochrechnung 5 Personen: ~0,5 MB/Jahr, ~70 Dateien/Jahr – GitHub-Grenzen
  (1 GB Repo, 1 MB je Datei über die Contents-API, 5000 Abrufe/h) bleiben weit weg.
- Ins Repo immer kompakt schreiben (`JSON.stringify(x)` ohne Einrückung), auch Backup-Einspielen.
- Laden nur, was gebraucht wird (Monatsfenster, `baumHolen()` + ETag); nie „alles laden“.
- Protokolle begrenzen (Wunsch-`log` 400, Dienst-`log` 2000 Einträge je Datei).
- Offline-Kopie in localStorage nur heute ±13 Monate + angezeigter Monat ±1, ohne Meldungen
  (`cacheSchreiben()`): localStorage (~5 MB) teilt sich die Domain mit der Tagesdoku.
- Eigenes Backend erst bei echten Rechten (heute nur Oberfläche, Team-Token darf alles), vielen
  gleichzeitigen Nutzern oder Server-Mitteilungen – nicht wegen der Datenmenge.
- Zukunft (geplant): Assistenten bekommen eine eigene Oberfläche (andere Rechte, Abläufe, Dienstarten),
  nutzen aber dasselbe Datenmodell im selben Repo, getrennt nach Gruppe (z. B. `plan/` = OA,
  weitere Gruppe in eigenem Ordner, gemeinsame Personen-/Termin-Daten). Daraus später: Wochenpläne/
  Anwesenheitslisten über alle Gruppen, Tagesdoku liest Dienste/Urlaub direkt statt Excel-Import.
  Neue Felder daher gruppenneutral benennen und Daten nie an eine Oberfläche koppeln.

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
  (`einstellungenGesetzt('pnr')` – die Personalnr. allein zählt nicht, „Verbinden“
  setzt sie selbst). Sonst kein Upload, gelbe Warnung (`syncLeer`) statt grüner
  Wolke. Meldungen zeigen Repo + Datei-Kennung (`syncOrt()`) zum Gerätevergleich.
- Seit 1.67 auch Admin-Backup im Team-Repo mit Personalnr. + Passwort (Pflicht für
  alle). Admin-QR trägt Team-Repo/-Token in die Sync-Felder ein; Admin mit eigenem
  Repo zog 1.67–1.70 einmal um (Code in 1.71 entfernt, alle Geräte umgezogen).
- Erste Verbindung ohne Basis: nur einseitige Einträge werden übernommen, Konflikt
  nur bei verschiedenen Werten auf beiden Seiten.
- `hasContent()` entscheidet, was als erfasst gilt; `persist()` und Export
  speichern nur solche Tage (`echteTage()`).
- Zeit-/Tagesrechnung über UTC-Tagesnummern (DST).
- `clipboard.writeText` synchron am Anfang des Klick-Handlers (iOS-Geste).
- Notausgang (eigenes `<script>` vor dem Hauptskript): bleibt die Version „v–“ und
  fliegt ein Fehler, wird der Chip zu „⚠️ Fehler – hier tippen“ (`notUpdate()`:
  `fetch(…, {cache:'reload'})`, SW-Update, neu laden). Update-Suche ebenfalls mit
  `cache:'reload'`.
- Service Worker (seit 1.71): alles cache-first, auch `index.html` (Start sofort,
  offline, schwaches WLAN); frisch nur bei `request.cache` 'reload'/'no-store' oder
  leerem Cache. Neue Version kommt über neuen SW (install lädt Shell mit
  `cache:'reload'`) bzw. `updateImHintergrund()` (max. 1×/24 h, `tagesdoku_update`),
  gilt ab nächstem Öffnen – kein automatisches Neuladen mehr. Sofort: Tipp auf
  Version. `api.github.com` nie über den SW. Playwright-Tests mit
  `serviceWorkers:'block'` sehen das nicht.
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
- „Link oder Code einfügen“ (`#zugangEinfuegen`, auch im Startdialog) per `prompt`,
  weil das Repo-Feld in der Nutzer-Ansicht ausgeblendet ist.
- Reset (`#resetAlles`, 2 Rückfragen): localStorage der ganzen Domain (auch
  Dienstplanung), sessionStorage, alle IndexedDBs, Caches, SW, Cookies; danach
  `setItem` stillgelegt und `resetLaeuft`, damit Verlassen der Seite nichts zurückschreibt.
- Timer-ID 1 ist frei: `HIST.timer = -1` beim Start (mit 1 löschte
  `clearTimeout` den ersten echten Timer).
  Standard ist die Nutzer-Ansicht: Repo, Token und „Zugang weitergeben“
  ausgeblendet (`zugangAnsicht()`), nur Personalnummer (`sync.kennung`, füllt
  leere Kopfdaten-`cfg.pnr`) + Passwort. Admin nur mit `tagesdoku_admin`='1'
  (Gerät): Migration = hat `tagesdoku_teilen` oder synct von Hand mit eigenem
  Repo (≠ `TEAM_REPO`); sonst „Admin-Anmeldung“ mit Gist-Token, geprüft über
  `GET /user` = Besitzer des Team-Repos (Knopf `#adminAuf` seit 1.72 nur über `#admin` in der Adresse oder 7 schnelle
  Tipps (4 s) auf die Überschrift, `ADMIN_TUER`). Oder per Admin-QR („Admin-Gerät
  hinzufügen“): PIN-verschlüsselt mit `g` (Gist-Token) und `admin:1`, nur als
  QR oder kopierter `#zugang2=`-Link (kein Gist; seit 1.68, für PC ohne Kamera), setzt Flag und `tagesdoku_teilen`, eigener Sync unberührt. Admin sieht den Token im Klartext,
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
