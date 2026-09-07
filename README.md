# Tagesdokumentation Überstunden & Rufdienst

Ausfüllbare PDF-Version + HTML-Erfassungstool für den offiziellen
Klinikum-Freudenstadt-Bogen "Tagesdokumentation: Überstunden und
Inanspruchnahme im Rufdienst" (Ärztlicher Dienst).

## Inhalt

| Datei | Zweck |
|---|---|
| `Tagesdokumentation_Original.pdf` | Unverändertes Original (Referenz) |
| `Tagesdokumentation_Ueberstunden_Rufdienst_ausfuellbar.pdf` | Original + echte AcroForm-Eingabefelder, Kopfteil fest vorbefüllt |
| `tagesdokumentation_erfassung.html` | Eigenständiges HTML-Tool: Tageswerte eingeben → automatische Berechnung → PDF ausfüllen & herunterladen |
| `add_fields.py` | Erzeugt die ausfüllbare PDF aus dem Original |
| `build_html.py` | Erzeugt das HTML-Tool (inkl. eingebettetem PDF-Template) |
| `CLAUDE.md` | Projektkontext & technische Learnings für die Weiterarbeit in Claude-Chats |

## Nutzung

1. `tagesdokumentation_erfassung.html` im Browser öffnen
2. Datum (Default: gestern), Dienstzeiten, ggf. Rufdienst-Einsätze eintragen
3. "PDF ausfüllen & herunterladen" klicken → fertig ausgefüllte PDF wird heruntergeladen
4. Ausdrucken, unterschreiben, an Personalabteilung weiterleiten

## Weiterentwicklung

Details zu Feldnamen, Koordinatensystem und bereits gelösten Bugs (pypdf
Oktal-Escape-Problem, AcroForm `/DR`-Font-Ressource, Zeilen- vs.
Kopfzeilen-Koordinaten) siehe [`CLAUDE.md`](./CLAUDE.md).
