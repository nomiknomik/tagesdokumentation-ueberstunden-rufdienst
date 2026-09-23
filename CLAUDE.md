# Arbeitsnotizen (privates Hilfsprojekt)

Öffentliches Repo, nur wegen GitHub Pages. **Keine personenbezogenen Daten
committen**: keine Namen, Personalnummern, E-Mail-Adressen, Gehalts- oder
Kontostände, Backups, Dienstpläne. Beispiele immer mit Platzhaltern
(„Mustermann", „123456"). Der ausführliche Entwicklungsverlauf steht in der
Git-Historie der Commit-Nachrichten, nicht hier.

## Arbeitsweise
- Direkt auf `main` (Pages liefert aus `main`, `main` ist live). Kein PR.
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
- `add_fields.py`, `build_html.py` (veraltet, erzeugt die heutige HTML nicht
  mehr), `make_icons.py` (App-Icon, Pillow).

## Geteilte Logik (in BEIDEN Tools pflegen)
Dienstart-Labels und -Zeiten (`DIENSTART_OPTIONS` im Desktop-Tool, `DUTY` in
der PWA), Überstundenrechnung (Ist-Ende − Plan-Ende + Soll-Beginn − Beginn,
kein +24h-Wrap), FRN-Verhalten. Alles andere in der PWA ist PWA-exklusiv.

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
- Abwesenheit hängt nur an der Dienstart (`ABWESENHEIT`, `URLAUB` über
  `istUrlaubstag()`), nie an der FRN-Checkbox; ein Tag zählt nie doppelt.
- `hasContent()` entscheidet, was als erfasst gilt; `persist()` und Export
  speichern nur solche Tage (`echteTage()`).
- Zeit-/Tagesrechnung über UTC-Tagesnummern (DST).
- `clipboard.writeText` synchron am Anfang des Klick-Handlers (iOS-Geste).
- Service Worker: `index.html` network-first, Rest cache-first.
