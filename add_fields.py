#!/usr/bin/env python3
"""Fügt echte, interaktive AcroForm-Textfelder zur Original-PDF hinzu,
ohne Layout/Text der Vorlage zu verändern. Kopfteil-Felder werden mit
festen Werten vorbefüllt (read-only), alle anderen Felder bleiben leer
und editierbar."""

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    DictionaryObject, NameObject, TextStringObject, ArrayObject,
    NumberObject, BooleanObject, FloatObject, IndirectObject, ByteStringObject
)

SRC = "/mnt/user-data/uploads/Tagesdokumentation_-_Überstunden_und_Inanspruchnahme_im_Rufdienst.pdf"
OUT = "/mnt/user-data/outputs/Tagesdokumentation_Ueberstunden_Rufdienst_ausfuellbar.pdf"

PAGE_H = 841.89  # PDF height (pt), y=0 unten

reader = PdfReader(SRC)
writer = PdfWriter()
writer.append(reader)
page = writer.pages[0]

if "/AcroForm" not in writer._root_object:
    helv_font = writer._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
        NameObject("/Encoding"): NameObject("/WinAnsiEncoding"),
    }))
    dr = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/Helv"): helv_font})
    })
    writer._root_object[NameObject("/AcroForm")] = writer._add_object(
        DictionaryObject({
            NameObject("/Fields"): ArrayObject(),
            NameObject("/NeedAppearances"): BooleanObject(True),
            NameObject("/DA"): ByteStringObject(b"/Helv 8 Tf 0 g"),
            NameObject("/DR"): dr,
        })
    )
acroform = writer._root_object["/AcroForm"]
acroform[NameObject("/NeedAppearances")] = BooleanObject(True)

if "/Annots" not in page:
    page[NameObject("/Annots")] = ArrayObject()

field_counter = [0]

def top_rect_to_pdf(x0, top, x1, bottom, pad=1.0, pad_top=2.3, pad_bottom=0.7):
    """Wandelt top-down Koordinaten (y=0 oben) in PDF-Rect (y=0 unten) um.
    pad_top/pad_bottom steuern die vertikale Zentrierung des Texts im Feld."""
    llx = x0 + pad
    urx = x1 - pad
    lly = PAGE_H - bottom + pad_bottom
    ury = PAGE_H - top - pad_top
    return [llx, lly, urx, ury]

def add_text_field(name, rect, value="", font_size=7, readonly=False, multiline=False):
    field_counter[0] += 1
    flags = 0
    if readonly:
        flags |= 1  # ReadOnly bit
    if multiline:
        flags |= (1 << 12)  # Multiline bit
    field = DictionaryObject({
        NameObject("/FT"): NameObject("/Tx"),
        NameObject("/T"): TextStringObject(name),
        NameObject("/V"): TextStringObject(value),
        NameObject("/DV"): TextStringObject(value),
        NameObject("/Rect"): ArrayObject([FloatObject(c) for c in rect]),
        NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/F"): NumberObject(4),  # Print flag
        NameObject("/Ff"): NumberObject(flags),
        NameObject("/DA"): ByteStringObject(f"/Helv {font_size} Tf 0 g".encode("latin-1")),
        NameObject("/P"): page.indirect_reference,
    })
    if readonly:
        field[NameObject("/BS")] = DictionaryObject({NameObject("/W"): NumberObject(0)})
    else:
        field[NameObject("/BS")] = DictionaryObject({NameObject("/W"): NumberObject(0)})
    field[NameObject("/MK")] = DictionaryObject({})
    ref = writer._add_object(field)
    page["/Annots"].append(ref)
    acroform["/Fields"].append(ref)
    return ref

# ---------------------------------------------------------------
# KOPFTEIL – feste Werte (read-only), aus Vorlage übernommen
# ---------------------------------------------------------------
HEADER = [
    # (name, x0, top, x1, bottom, value, readonly) - exakte Zellgrenzen aus Original-PDF
    ("name_vorname",   139.2, 86.9, 271.9, 104.8, "Zabelyshenskiy, Alexander", True),
    ("personalnummer", 139.2, 104.8, 271.9, 122.8, "421761", True),
    ("funktion",       139.2, 122.8, 271.9, 140.7, "Oberarzt", True),
    ("klinik_abteilung", 363.8, 104.8, 557.9, 122.8, "Allgemein-, Viszeral- u. Gefäßchirurgie", True),
    ("datum",          363.8, 86.9, 496.6, 104.8, "", False),
    ("dienstart",      363.8, 122.8, 557.9, 140.7, "", False),
]
for name, x0, top, x1, bottom, val, ro in HEADER:
    fs = 6.5 if name == "klinik_abteilung" else 8
    add_text_field(name, top_rect_to_pdf(x0, top, x1, bottom), val, font_size=fs, readonly=ro)

# ---------------------------------------------------------------
# ABSCHNITT 1 – Dienstzeit und Überstunden
# ---------------------------------------------------------------
S1 = [
    ("dienstbeginn",        36.8, 201.4, 139.3, 221.4),
    ("plan_dienstende",     139.3, 201.4, 205.6, 221.4),
    ("tats_dienstende",     205.6, 201.4, 272.0, 221.4),
    ("ueberstunden_std",    272.0, 201.4, 363.9, 221.4),
    ("grund_ueberstunden",  363.9, 201.4, 558.2, 221.4),
]
for name, x0, top, x1, bottom in S1:
    add_text_field(name, top_rect_to_pdf(x0, top, x1, bottom))

add_text_field("erlaeuterung", top_rect_to_pdf(139.2, 221.4, 558.2, 241.4))
add_text_field("angeordnet_durch", top_rect_to_pdf(139.2, 241.4, 558.2, 264.9))

# ---------------------------------------------------------------
# ABSCHNITT 2 – Inanspruchnahme im Rufdienst (8 Zeilen)
# ---------------------------------------------------------------
row_tops = [325.5, 344.8, 364.1, 383.4, 402.7, 422.0, 441.3, 460.6]
row_bottoms = [344.8, 364.1, 383.4, 402.7, 422.0, 441.3, 460.6, 479.9]

cols = [
    ("beginn", 72.9, 139.3),
    ("ende", 139.3, 205.6),
    ("dauer", 205.6, 272.0),
    ("art", 272.0, 363.9),
    ("grund_anlass", 363.9, 496.6),
    ("fallnr", 496.6, 558.2),
]

for i, (top, bottom) in enumerate(zip(row_tops, row_bottoms), start=1):
    for cname, x0, x1 in cols:
        add_text_field(f"rufdienst_{i}_{cname}", top_rect_to_pdf(x0, top, x1, bottom))

add_text_field("summe_inanspruchnahme", top_rect_to_pdf(205.6, 479.9, 400, 497.8))
add_text_field("anzahl_einsaetze", top_rect_to_pdf(500, 479.9, 558.2, 497.8))

# ---------------------------------------------------------------
# ABSCHNITT 3 – Zusammenfassung und Ausgleich
# ---------------------------------------------------------------
add_text_field("ueberstunden_gesamt", top_rect_to_pdf(205.6, 529.6, 271.9, 551.6))
add_text_field("ruhezeit_eingehalten", top_rect_to_pdf(496.6, 529.6, 557.8, 551.6))
add_text_field("gewuenschter_ausgleich", top_rect_to_pdf(205.6, 551.6, 363.9, 571.6))
add_text_field("geplanter_ausgleichstag", top_rect_to_pdf(496.6, 551.6, 557.8, 571.6))

with open(OUT, "wb") as f:
    writer.write(f)

print(f"Fertig: {field_counter[0]} Felder erstellt -> {OUT}")
