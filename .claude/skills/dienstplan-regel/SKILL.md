---
name: dienstplan-regel
description: "[Version 1.1] Neue oder geänderte Regel, Gewichtung oder Formel in der automatischen Dienstverteilung (plan/index.html) einbauen – App-Bewertung (bewerte/verbessern) und Solver-Modell (mipModell) synchron halten und mit einem Backup abnehmen. Verwenden bei: neue Dienstregel, No-Go/Wunsch-Logik ändern, Punkte/Gewichte anpassen, Fairness-/Zielformel ändern, „Solver rechnet falsch“, „Modell prüfen“, Abweichung Solver ↔ Heuristik."
---

# Dienstplan-Regel einbauen (Version 1.1)

Die Verteilung hat **eine** Wahrheit: die Bewertung der App
(`bewerte()` je Dienst, `verbessern()` = J + kosten). Der Solver (`mipModell()`) ist
eine exakte lineare Kopie davon. Jede Änderung muss an beiden Stellen landen, sonst
optimiert der Solver still eine veraltete Regel.

## Ablauf

1. **Einordnen** (Fragen an den Nutzer nur, wenn unklar):
   - hart (nie) oder weich (Punkte)? Tag-Farbe `'r'` = hart, `'o'` = weich, `'g'` = Bonus.
   - Gilt sie je Dienst-Tag (→ `bewerte()`) oder je Person/Monat (→ `J` in `verbessern()`)?
   - Soll sie im Thermometer zählen (`zufriedenheit()`)?
2. **App-Bewertung**: in `bewerte(p, s)` Tag + `score` ergänzen. Kosten im Plan =
   **−3 × score** je Dienst (`kosten` in `verbessern()`; n- und „2. WE“-Anteil heben sich auf).
3. **Solver**: dieselbe Regel in `mipModell()` (gleiche Datei, nach `verbessern()`)
   – Muster unten. Danach Modellwert + `konst` == `verbessern([])` (Test A).
4. **Thermometer/Details**, falls gewünscht: `zufriedenheit()`, `detailHtml()`.
5. `PLAN_VERSION` +0.01, CLAUDE.md-Eintrag (eine Zeile, Version + Kernaussage).
6. **Abnahme** (Pflicht vor dem Push), siehe unten. Erst bei „Alles OK“ pushen.

## Einstellbare Gewichte (seit 2.24)

Punkte, die der Admin ändern darf, stehen in `GEW_STD` und werden **nur** über `gw('name')` gelesen – in `bewerte()`
(als `gw(..)/3` im score) und in `mipModell()` (direkt als Punkte). Neues einstellbares Gewicht: Eintrag in
`GEW_STD`/`GEW_MIN`/`GEW_MAX`, Zeile in `regelnRender()` mit `wert('name')`, beide Stellen über `gw()`.
Feste Regeln dort mit `fest('…')` aufführen, damit die Übersicht vollständig bleibt.
Test mit geänderten Gewichten: `GEWICHTE='{"nogo":200,"weGrenze":3}' node pruefen.mjs <backup>`.

## Bausteine in `mipModell()`

`X(k, s)` = Ausdruck „k hat Dienst an s“ (Variable an freien Tagen, sonst 0/1-Konstante,
auch Nachbarmonate). Ausdrücke kombiniert man mit `add([f, e], …)`, `L(c)`, `V(var)`.

| Regelart | Code |
|---|---|
| fester Abzug je Dienst-Tag (aus Daten bestimmbar) | im `kosten`-Block `sc -= Punkte` (wird zu `ziele_(x, -3*sc)`) |
| hart an einem Tag | `kandidat()` (Variable entsteht gar nicht) oder `zeile(x, '<=', 0)` |
| hart, zwei Tage zusammen verboten | `zeile(add([1, a], [1, b]), '<=', 1)` |
| weich: Strafe f, wenn **alle** Bedingungen zutreffen | `alleStrafe([x, a, b], f)` (f ≥ 0) |
| Bonus, wenn beide zutreffen | `ziele_(und(a, b), -f)` |
| Zählgrenze im Monat („mehr als G …“) | Summe als Ausdruck, `e = neu('e')`, `zeile(add([1, summe], [-40, V(e)]), '<=', G)`, dann `alleStrafe([x, V(e)], f)` – siehe `ab()` beim 3. WE |
| Abweichung vom Ziel je Person | `bandTerm(ausdruck, ziel, schritt, gewicht)` (konvex, stückweise linear; Schritt 1 oder 0,5) |
| Unterschreitung | `unterTerm(ausdruck, ziel)` |
| Serie über Wochen | Fenster wie bei `maxWeFolge`: **eine** Hilfsvariable je Tag mit mehreren Untergrenzen (nicht je Fenster – zählt sonst doppelt) |

Regeln:
- Nur lineare Formen; Produkte zweier Variablen immer über `und()`.
- Feste Tage sind Konstanten – Bausteine verrechnen sie selbst (`konst`), nichts extra tun.
- Bedingungen auf **Daten** (Abwesenheit, Feiertag, Wochentag, Einträge) in JS auswerten,
  nur Bedingungen auf **Dienste** als Variablen.
- Strafen, die `verbessern()` nicht kennt (z. B. Folgetag-Regel 900), bewusst dokumentieren;
  der Test lässt genau ±900-Vielfache zu.
- Zufall (`rausch` 0,004) nicht vergrößern: muss in Summe < kleinster Wertabstand (0,25) bleiben.

## Abnahme

Backup aus der App (Einstellungen → Backup) liegt beim Nutzer, **nie ins Repo**
(Personendaten). Einmalig `npm i` im Ordner `scripts/`, dann:

```
cd .claude/skills/dienstplan-regel/scripts && npm i --silent
node pruefen.mjs <pfad/backup.json> [2026-10,2026-11] [Zufallsfälle je Monat, Std. 3]
```

Prüft je Monat (ganz leer + Zufallsfälle mit 20–70 % festen Tagen):
- **A** Modellwert (HiGHS) = App-Wert → sonst Modell und `bewerte()` laufen auseinander.
- **B** Solver ≤ Heuristik, außer die Heuristik bricht eine rote Regel.
- **C** Solver-Plan ohne rote Regel (Hinweis, wenn feste Tage es erzwingen).
- **D** echte App `autoVerteilen()` liefert denselben Wert und „Rechnerisch bestmöglicher Plan“.

Exit-Code 1 bei FEHLER. Tabelle (Werte) dem Nutzer kurz berichten: vorher/nachher je Monat.
Bei Abweichung A: kleinen Fall suchen (`VORBEREITEN` mit hohem Anteil fester Tage),
`__verstoesse(plan)` und `__mod.lp` (LP-Text) vergleichen.

Zusätzlich wie immer: Render-Check (Playwright, 390 × 844 und Desktop) ohne Seitenfehler.
Screenshots/Ergebnisse nur im Scratchpad – sie enthalten Namen.
