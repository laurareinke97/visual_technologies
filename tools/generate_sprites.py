"""Erzeugt die Sprite-Sheets (disc.png, bunny.png) komplett selbst mit Pillow.
Aufruf: python3 tools/generate_sprites.py   (aus dem Projektordner)"""
import math
from PIL import Image, ImageDraw, ImageFilter

SS = 4            # Supersampling für glatte Kanten
FRAME = 300       # Frame-Größe in Pixeln (final)
BIG = FRAME * SS

# ---------------------------------------------------------------- Scheibe
DISC_FRAMES, DISC_COLS = 24, 6          # 24 * 15° = 360°
PALETTE = ["#ff5a5f", "#ffb400", "#2ec4b6", "#3a86ff", "#8338ec", "#ff7bac"]

def disc_pattern():
    img = Image.new("RGBA", (BIG, BIG), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = BIG // 2
    R = int(BIG * 0.43)

    def box(r): return [c - r, c - r, c + r, c + r]
    d.ellipse(box(R), fill="#14202e")                       # Rand
    r1 = int(R * 0.93)
    for k in range(12):                                      # äußerer Kranz
        d.pieslice(box(r1), k * 30, (k + 1) * 30, fill=PALETTE[k % 6])
    r2 = int(R * 0.60)
    d.ellipse(box(r2 + 14), fill="#14202e")
    for k in range(8):                                       # innerer Kranz
        d.pieslice(box(r2), k * 45, (k + 1) * 45,
                   fill="#f4f1de" if k % 2 == 0 else "#1d3557")
    d.ellipse(box(int(R * 0.30)), fill="#14202e")
    d.ellipse(box(int(R * 0.26)), fill="#ffd166")
    d.ellipse(box(int(R * 0.10)), fill="#14202e")
    # Asymmetrische Marker, damit man die Drehung klar sieht
    def dot(angle, rad, size, fill):
        x = c + rad * math.cos(math.radians(angle))
        y = c + rad * math.sin(math.radians(angle))
        d.ellipse([x - size, y - size, x + size, y + size], fill=fill, outline="#14202e", width=8)
    dot(-90, R * 0.77, 38, "#ffffff")
    dot(-90 + 120, R * 0.77, 22, "#14202e")
    dot(-90 + 240, R * 0.77, 22, "#14202e")
    dot(-90 + 240, R * 0.45, 16, "#ff5a5f")
    dot(-90 + 100, R * 0.45, 16, "#3a86ff")
    # Pfeil am Rand
    tip = (c, c - R * 0.99)
    d.polygon([tip, (c - 46, c - R * 0.99 + 80), (c + 46, c - R * 0.99 + 80)], fill="#ffffff")
    return img

def soft_shadow(w, h, cx, cy, blur=18, alpha=90):
    s = Image.new("RGBA", (BIG, BIG), (0, 0, 0, 0))
    ImageDraw.Draw(s).ellipse([cx - w, cy - h, cx + w, cy + h], fill=(0, 0, 0, alpha))
    return s.filter(ImageFilter.GaussianBlur(blur * SS / 4))

def make_disc():
    pat = disc_pattern()
    rows = math.ceil(DISC_FRAMES / DISC_COLS)
    sheet = Image.new("RGBA", (FRAME * DISC_COLS, FRAME * rows), (0, 0, 0, 0))
    shadow = soft_shadow(int(BIG * 0.40), int(BIG * 0.06), BIG // 2, int(BIG * 0.93))
    for i in range(DISC_FRAMES):
        rot = pat.rotate(-i * 360 / DISC_FRAMES, resample=Image.BICUBIC)  # im Uhrzeigersinn
        fr = Image.alpha_composite(shadow.copy(), rot).resize((FRAME, FRAME), Image.LANCZOS)
        sheet.paste(fr, ((i % DISC_COLS) * FRAME, (i // DISC_COLS) * FRAME))
    sheet.save("img/disc.png", optimize=True)
    return DISC_FRAMES, DISC_COLS, rows

# ------------------------------------------------------------------- Hase
BUNNY_FRAMES, BUNNY_COLS = 12, 6
FUR, FUR_D, BELLY, PINK, LINE = "#e8dccb", "#c9b79f", "#fffaf0", "#f5a9b8", "#4a3b32"

def make_bunny_frame(t):
    img = Image.new("RGBA", (BIG, BIG), (0, 0, 0, 0))
    ground = BIG * 0.86
    h = math.sin(math.pi * t)               # 0 am Boden, 1 oben
    lift = h * 300
    sx = 1 + 0.10 * math.cos(2 * math.pi * t)   # gestaucht am Boden, gestreckt oben
    sy = 2 - sx
    cx = BIG * 0.46
    base = ground - lift

    def P(x, y): return (cx + x * sx, base - y * sy)

    def ell(x, y, rx, ry, ang=0):
        pts = []
        for k in range(72):
            a = 2 * math.pi * k / 72
            ex, ey = rx * math.cos(a), ry * math.sin(a)
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            pts.append(P(x + ex * ca - ey * sa, y + ex * sa + ey * ca))
        return pts

    d = ImageDraw.Draw(img)
    def shape(pts, fill, w=9):
        d.polygon(pts, fill=fill)
        d.line(pts + [pts[0]], fill=LINE, width=w, joint="curve")

    flop = math.sin(2 * math.pi * t)
    # Schatten
    shw = int(330 * (1 - 0.35 * h))
    sh = soft_shadow(shw, 38, int(cx), int(ground + 20), alpha=80)
    img.alpha_composite(sh)
    d = ImageDraw.Draw(img)

    shape(ell(-165, 190, 55, 55), BELLY)                          # Schwanz
    shape(ell(120, 400, 48, 125, -25 - 14 * flop), FUR_D)         # hinteres Ohr
    ext = 25 * h                                                  # Hinterfuß streckt sich
    shape(ell(-70 - ext, 35, 95, 32, -8 * h), FUR_D)              # Hinterfuß
    shape(ell(0, 175, 160, 135), FUR)                             # Körper
    shape(ell(40, 130, 100, 80), BELLY)                           # Bauch
    shape(ell(95 + ext, 28 + 30 * h, 48, 28), FUR_D)              # Vorderpfote
    shape(ell(150, 320, 100, 92), FUR)                            # Kopf
    shape(ell(185, 430, 48, 130, -10 - 14 * flop), FUR)           # vorderes Ohr
    d = ImageDraw.Draw(img)
    pts = ell(185, 425, 22, 95, -10 - 14 * flop)
    d.polygon(pts, fill=PINK)
    ex, ey = P(190, 345); d.ellipse([ex - 15, ey - 15, ex + 15, ey + 15], fill=LINE)
    d.ellipse([ex + 2, ey - 10, ex + 10, ey - 2], fill="white")
    cxn, cyn = P(238, 315); d.ellipse([cxn - 17, cyn - 13, cxn + 17, cyn + 13], fill=PINK, outline=LINE, width=6)
    bx, by = P(185, 300); d.ellipse([bx - 28, by - 14, bx + 28, by + 14], fill=(245, 169, 184, 140))
    return img.resize((FRAME, FRAME), Image.LANCZOS)

def make_bunny():
    rows = math.ceil(BUNNY_FRAMES / BUNNY_COLS)
    sheet = Image.new("RGBA", (FRAME * BUNNY_COLS, FRAME * rows), (0, 0, 0, 0))
    for i in range(BUNNY_FRAMES):
        sheet.paste(make_bunny_frame(i / BUNNY_FRAMES), ((i % BUNNY_COLS) * FRAME, (i // BUNNY_COLS) * FRAME))
    sheet.save("img/bunny.png", optimize=True)
    return BUNNY_FRAMES, BUNNY_COLS, rows

if __name__ == "__main__":
    print("disc  (frames, cols, rows):", make_disc())
    print("bunny (frames, cols, rows):", make_bunny())
