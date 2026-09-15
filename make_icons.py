#!/usr/bin/env python3
"""Erzeugt app/icon-192.png und app/icon-512.png.

Motiv: heller, warmer Hintergrund (Theme-Token --color-background), darum ein
24-Stunden-Ring, dessen Segmente die Dienstarten einfaerben (Bereitschaft blass,
Regeldienst petrol, Aktivzeit gruen), in der Mitte eine weisse Uhr mit Zeigern
auf 16:05 (planmaessiges Dienstende). Gezeichnet wird 4x ueberabgetastet und
danach heruntergerechnet - PIL kennt kein Antialiasing beim Zeichnen.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math

FONT = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'

SS = 4  # Supersampling

# 24 Ringsegmente, Index = Stunde des Tages (0 Uhr oben)
NIGHT   = (183, 209, 213)   # Rufdienst-Bereitschaft nachts
DAWN    = (143, 189, 194)
DUTY    = (0, 99, 110)      # Regeldienst (--color-primary)
DUTY_L  = (10, 116, 128)    # --color-primary-light
ACTIVE  = (21, 143, 71)     # Aktivzeit/Einsatz (--color-success)
EVENING = (94, 155, 163)

SEGMENTS = (
    [NIGHT] * 6 + [DAWN] +                 # 00-06 Bereitschaft
    [DUTY] * 8 + [DUTY_L] +                # 07-15 Regeldienst
    [EVENING] * 2 +                        # 16-17
    [ACTIVE] * 4 +                         # 18-21 Einsatz im Rufdienst
    [EVENING, NIGHT]                       # 22-23
)
assert len(SEGMENTS) == 24

BG_TOP    = (255, 253, 248)
BG_BOTTOM = (240, 228, 208)
FACE      = (255, 255, 255)
TICK      = (214, 204, 190)
TICK_MAIN = (150, 138, 124)
HAND      = (31, 74, 79)
NUMBER    = (58, 50, 43)


def background(size):
    img = Image.new('RGB', (size, size))
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        # leicht diagonaler Verlauf: oben links am hellsten
        for x in range(size):
            u = min(1.0, (t * 0.75 + (x / (size - 1)) * 0.25))
            px[x, y] = tuple(
                round(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * u) for i in range(3)
            )
    return img


def make(size):
    S = size * SS
    img = background(S)
    c = S / 2

    R_OUT = 0.400 * S      # Ring aussen (bleibt in der maskable-Safe-Zone)
    R_IN = 0.306 * S       # Ring innen
    R_FACE = 0.288 * S     # weisse Zifferblattflaeche
    GAP = 2.4              # Grad Luft zwischen zwei Segmenten

    # knapper, weicher Schlagschatten unter dem Ring (nicht als Halo ringsum,
    # sonst wirkt der Hintergrund bei kleiner Darstellung schmutzig)
    shadow = Image.new('L', (S, S), 0)
    ImageDraw.Draw(shadow).ellipse(
        [c - R_OUT, c - R_OUT + 0.022 * S, c + R_OUT, c + R_OUT + 0.022 * S], fill=90)
    shadow = shadow.filter(ImageFilter.GaussianBlur(0.016 * S))
    ImageDraw.Draw(shadow).ellipse(
        [c - R_OUT, c - R_OUT, c + R_OUT, c + R_OUT], fill=0)
    shadow = shadow.filter(ImageFilter.GaussianBlur(0.008 * S))
    img = Image.composite(Image.new('RGB', (S, S), (126, 110, 92)), img, shadow)

    d = ImageDraw.Draw(img)

    # 24-Stunden-Ring
    for h, col in enumerate(SEGMENTS):
        a0 = -90 + h * 15 + GAP / 2
        a1 = -90 + (h + 1) * 15 - GAP / 2
        d.pieslice([c - R_OUT, c - R_OUT, c + R_OUT, c + R_OUT], a0, a1, fill=col)
    d.ellipse([c - R_IN, c - R_IN, c + R_IN, c + R_IN],
              fill=None, outline=None, width=0)
    # Ringinneres ausstanzen: Hintergrund an dieser Stelle wiederherstellen
    inner = background(S).crop((0, 0, S, S))
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).ellipse([c - R_IN, c - R_IN, c + R_IN, c + R_IN], fill=255)
    img.paste(inner, (0, 0), mask)
    d = ImageDraw.Draw(img)

    # Zifferblatt
    d.ellipse([c - R_FACE, c - R_FACE, c + R_FACE, c + R_FACE], fill=FACE)

    # Ziffern 12/3/6/9, dazwischen feine Striche
    f = ImageFont.truetype(FONT, int(0.105 * S))
    for i in range(12):
        ang = math.radians(-90 + i * 30)
        if i % 3 == 0:
            n = {0: '12', 3: '3', 6: '6', 9: '9'}[i]
            r = R_FACE * 0.68
            x, y = c + math.cos(ang) * r, c + math.sin(ang) * r
            bb = d.textbbox((0, 0), n, font=f, anchor='mm')
            d.text((x, y - (bb[1] + bb[3]) / 2 - (bb[1] + bb[3]) / 2 * 0), n,
                   font=f, fill=NUMBER, anchor='mm')
        else:
            r1, r2 = R_FACE * 0.86, R_FACE * 0.94
            d.line([c + math.cos(ang) * r1, c + math.sin(ang) * r1,
                    c + math.cos(ang) * r2, c + math.sin(ang) * r2],
                   fill=TICK, width=int(0.012 * S))

    def hand(angle_deg, length, width, tail, col):
        a = math.radians(angle_deg - 90)
        x1, y1 = c + math.cos(a) * length, c + math.sin(a) * length
        x0, y0 = c - math.cos(a) * tail, c - math.sin(a) * tail
        d.line([x0, y0, x1, y1], fill=col, width=int(width))
        for (x, y) in ((x0, y0), (x1, y1)):   # runde Enden
            d.ellipse([x - width / 2, y - width / 2, x + width / 2, y + width / 2], fill=col)

    # Zeigerstand 16:05 - planmaessiges Dienstende
    hh, mm = 16, 5
    hand((hh % 12 + mm / 60) * 30, 0.165 * S, 0.036 * S, 0.045 * S, HAND)
    hand(mm * 6, 0.235 * S, 0.026 * S, 0.045 * S, HAND)

    rc = 0.030 * S
    d.ellipse([c - rc, c - rc, c + rc, c + rc], fill=HAND)
    rc2 = 0.013 * S
    d.ellipse([c - rc2, c - rc2, c + rc2, c + rc2], fill=ACTIVE)

    return img.resize((size, size), Image.LANCZOS)


for s in (192, 512):
    make(s).save(f'app/icon-{s}.png')
    print(f'app/icon-{s}.png geschrieben')
