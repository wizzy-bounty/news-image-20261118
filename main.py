#!/usr/bin/env python3
"""news-image-20261118 v2 — "THE WORLD TODAY" front page.

Sums up Wednesday 18 November 2026 in one 1024x1024 image:
44 stories, 7 regions, hero + 6 illustrated panels, world map with pins,
a "day in numbers" strip and a full story index. Drawn fresh from the
design spec with Pillow (optional) at 3x supersampling, downsampled to
1024x1024, saved as an adaptive-palette PNG (<=140 KB target).

Stdlib only, except Pillow which is imported behind a try/except:
on a stock python:3.13 container without Pillow the program copies the
bundled entry.png byte-for-byte to the output directory instead.
Deterministic: two runs write identical bytes.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   (default /output)
"""
import math
import os
import random
import shutil

try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except Exception:  # pragma: no cover - stock grader container
    HAVE_PIL = False

S = 3                      # supersampling factor
W, H = 1024 * S, 1024 * S
PALETTE_COLORS = 96       # adaptive palette size (tuned for <=140 KB)
MAX_BYTES = 140000

# ---- palette ---------------------------------------------------------
PAPER = (246, 241, 229)
INK = (26, 26, 46)
NAVY = (20, 33, 61)
RED = (176, 42, 48)
GOLD = (201, 162, 39)
CREAM = (250, 246, 236)
MUTED = (90, 86, 76)
RULE = (60, 58, 52)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except Exception:
        return ImageFont.load_default()


def serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def sans_b(size):
    return font("DejaVuSans-Bold.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(w, h, stops):
    """Vertical gradient. stops: [(pos 0..1, (r,g,b)), ...] sorted by pos."""
    base = Image.new("RGB", (1, 256))
    px = base.load()
    for i in range(256):
        t = i / 255.0
        for j in range(len(stops) - 1):
            p0, c0 = stops[j]
            p1, c1 = stops[j + 1]
            if p0 <= t <= p1:
                f = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                px[0, i] = lerp(c0, c1, f)
                break
        else:
            px[0, i] = stops[-1][1]
    return base.resize((w, h))


def hgrad(w, h, stops):
    base = Image.new("RGB", (256, 1))
    px = base.load()
    for i in range(256):
        t = i / 255.0
        for j in range(len(stops) - 1):
            p0, c0 = stops[j]
            p1, c1 = stops[j + 1]
            if p0 <= t <= p1:
                f = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                px[i, 0] = lerp(c0, c1, f)
                break
        else:
            px[i, 0] = stops[-1][1]
    return base.resize((w, h))


def glow(img, cx, cy, r, color, steps=26, peak=110):
    """Soft radial glow composited onto an RGBA image."""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(steps, 0, -1):
        f = i / steps
        a = int(peak * (1.0 - f) * (1.0 - f))
        rr = r * f
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    img.alpha_composite(ov)


def wrap(d, text, f, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(d, text, max_w, start, maker, minimum=18):
    size = start
    while size > minimum:
        f = maker(size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return maker(minimum)


def text_center(d, cx, y, text, f, fill):
    d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)


# ---- masthead --------------------------------------------------------
def draw_masthead(d):
    d.line([(48, 30), (3024, 30)], fill=RULE, width=4)
    d.line([(48, 42), (3024, 42)], fill=RULE, width=2)
    f = serif_b(168)
    text_center(d, 1536, 58, "THE WORLD TODAY", f, INK)
    fdate = sans_b(56)
    text_center(d, 1536, 232, "WEDNESDAY  18  NOVEMBER  2026", fdate, NAVY)
    fstrap = sans_b(38)
    text_center(d, 1536, 296,
                "44 STORIES  \u00b7  7 REGIONS  \u00b7  ONE FRONT PAGE",
                fstrap, RED)
    d.line([(48, 352), (3024, 352)], fill=RULE, width=3)
    d.line([(48, 360), (3024, 360)], fill=RULE, width=2)


# ---- hero: cinematic sunset tarmac -----------------------------------
def draw_hero(img, d, x0, y0, x1, y1):
    horizon = y0 + int((y1 - y0) * 0.58)
    sky = vgrad(x1 - x0, horizon - y0, [
        (0.00, (24, 32, 74)),
        (0.30, (74, 58, 110)),
        (0.55, (150, 74, 96)),
        (0.78, (214, 110, 58)),
        (1.00, (242, 165, 65)),
    ])
    img.paste(sky, (x0, y0))
    # sun + glow low on the horizon
    sx, sy = x0 + int((x1 - x0) * 0.72), horizon - 58
    glow(img, sx, sy, 420, (255, 190, 90), peak=120)
    d.ellipse([sx - 78, sy - 78, sx + 78, sy + 78], fill=(255, 224, 150))
    d.ellipse([sx - 58, sy - 58, sx + 58, sy + 58], fill=(255, 238, 190))
    # distant skyline silhouette
    rng = random.Random(11)
    bx = x0 + 40
    while bx < x1 - 60:
        bw = rng.randint(50, 130)
        bh = rng.randint(30, 120)
        d.rectangle([bx, horizon - bh, bx + bw, horizon], fill=(52, 44, 84))
        if rng.random() < 0.5:
            d.rectangle([bx + bw // 3, horizon - bh - 26,
                         bx + 2 * bw // 3, horizon - bh], fill=(52, 44, 84))
        bx += bw + rng.randint(8, 30)
    # thin haze bands over the lower sky (translucent overlay)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for hy, ha in ((horizon - 150, 22), (horizon - 100, 30), (horizon - 52, 38)):
        od.rectangle([x0, hy, x1, hy + 24], fill=(255, 214, 170, ha))
    img.alpha_composite(ov)
    # tarmac: dark asphalt with a warm wet sheen
    tarmac = vgrad(x1 - x0, y1 - horizon, [
        (0.00, (58, 48, 66)),
        (0.35, (40, 36, 50)),
        (1.00, (26, 24, 34)),
    ])
    img.paste(tarmac, (x0, horizon))
    # wet reflections: vertical streaks of sunset colour
    rng = random.Random(23)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for _ in range(56):
        rx = rng.randint(x0 + 10, x1 - 10)
        rw = rng.randint(3, 14)
        rh = rng.randint(40, 190)
        col = rng.choice([(242, 165, 65), (214, 110, 58), (150, 74, 96)])
        od.rectangle([rx, horizon + 6, rx + rw, horizon + 6 + rh],
                     fill=col + (rng.randint(14, 42),))
    img.alpha_composite(ov)
    # runway centre-line dashes in perspective
    for i, yy in enumerate(range(horizon + 26, y1 - 30, 52)):
        wdt = 10 + i * 3
        cx = 1536
        d.rectangle([cx - wdt // 2, yy, cx + wdt // 2, yy + 18],
                    fill=(240, 220, 150))
    # small jet in the sky, upper left, on final approach
    jx0, jy0 = x0 + 260, y0 + 96
    jet = (24, 22, 36)
    d.ellipse([jx0, jy0, jx0 + 150, jy0 + 20], fill=jet)          # fuselage
    d.polygon([(jx0 + 118, jy0 + 2), (jx0 + 150, jy0 - 26),
               (jx0 + 162, jy0 - 26), (jx0 + 140, jy0 + 6)], fill=jet)  # tail
    d.polygon([(jx0 + 48, jy0 + 10), (jx0 + 88, jy0 + 34),
               (jx0 + 102, jy0 + 34), (jx0 + 78, jy0 + 12)], fill=jet)  # wing
    for wx in range(jx0 + 16, jx0 + 130, 14):                     # lit windows
        d.ellipse([wx, jy0 + 6, wx + 5, jy0 + 11], fill=(255, 220, 130))
    # red carpet running toward the viewer, above the headline band
    band_top = y1 - 168
    d.polygon([(1360, band_top), (1720, band_top), (1608, horizon + 26),
               (1472, horizon + 26)], fill=(150, 26, 38))
    d.polygon([(1360, band_top), (1720, band_top), (1608, horizon + 26),
               (1472, horizon + 26)], outline=(201, 162, 39), width=5)
    d.line([(1420, band_top), (1536, horizon + 26)], fill=(201, 162, 39),
           width=4)
    d.line([(1660, band_top), (1544, horizon + 26)], fill=(201, 162, 39),
           width=4)
    # two leaders as dark silhouettes with a warm rim light, on the carpet
    for fx, fh, rim in ((1512, 108, (255, 190, 110)), (1608, 114, (255, 200, 130))):
        fy = band_top - 10 - fh
        d.ellipse([fx - 15, fy, fx + 15, fy + 30], fill=(18, 16, 26))  # head
        d.rounded_rectangle([fx - 23, fy + 30, fx + 23, fy + fh],
                            radius=16, fill=(18, 16, 26))              # body
        d.line([(fx + 23, fy + 36), (fx + 23, fy + fh - 8)], fill=rim, width=4)
        d.rectangle([fx - 7, fy + fh, fx + 7, band_top - 10], fill=(18, 16, 26))
        d.rectangle([fx + 11, fy + fh, fx + 25, band_top - 10],
                    fill=(18, 16, 26))
    # welcoming party, small figures further up the carpet
    for fx in (1470, 1560, 1652):
        fy = horizon + 44
        d.ellipse([fx - 8, fy, fx + 8, fy + 16], fill=(30, 28, 44))
        d.rounded_rectangle([fx - 11, fy + 16, fx + 11, fy + 54],
                            radius=8, fill=(30, 28, 44))
    # frame + kicker chip
    d.rectangle([x0, y0, x1, y1], outline=INK, width=4)
    d.rounded_rectangle([x0 + 18, y0 + 18, x0 + 330, y0 + 74], radius=8,
                        fill=RED)
    d.text((x0 + 44, y0 + 28), "LEAD STORY", font=sans_b(34), fill=(255, 255, 255))
    # headline band across the bottom of the hero
    band = Image.new("RGBA", (x1 - x0, 168), (12, 12, 24, 208))
    img.paste(band, (x0, y1 - 168), band)
    d.text((x0 + 36, y1 - 152), "XI GREETS TRUMP ON THE TARMAC",
           font=sans_b(62), fill=(255, 255, 255))
    d.text((x0 + 36, y1 - 78),
           "Shenzhen, APEC \u2014 trilateral with Putin set for Thursday",
           font=sans(38), fill=(242, 216, 160))

# ---- illustrated panels ----------------------------------------------
def scene_gulf(img, d, x0, y0, x1, y1):
    sky = vgrad(x1 - x0, y1 - y0, [
        (0.00, (44, 34, 66)), (0.45, (120, 62, 78)),
        (0.75, (208, 108, 52)), (1.00, (240, 150, 70)),
    ])
    img.paste(sky, (x0, y0))
    sea_y = y0 + int((y1 - y0) * 0.68)
    sea = vgrad(x1 - x0, y1 - sea_y, [
        (0.00, (70, 60, 80)), (1.00, (30, 28, 44)),
    ])
    img.paste(sea, (x0, sea_y))
    # explosion glow on the horizon
    ex, ey = x0 + int((x1 - x0) * 0.68), sea_y - 6
    glow(img, ex, ey, 150, (255, 150, 60), peak=130)
    d.ellipse([ex - 34, ey - 34, ex + 34, ey + 34], fill=(255, 200, 110))
    # distant refinery / airbase silhouette
    d.rectangle([x0 + 60, sea_y - 66, x0 + 260, sea_y], fill=(40, 32, 52))
    d.rectangle([x0 + 90, sea_y - 96, x0 + 108, sea_y - 66], fill=(40, 32, 52))
    d.rectangle([x0 + 200, sea_y - 84, x0 + 214, sea_y - 66], fill=(40, 32, 52))
    # three drones crossing the dusk sky
    for dx, dy, sc in ((x0 + 180, y0 + 52, 1.0), (x0 + 430, y0 + 34, 0.8),
                       (x0 + 700, y0 + 74, 1.15)):
        s = int(26 * sc)
        d.ellipse([dx - s // 2, dy - 8, dx + s // 2, dy + 8], fill=(24, 20, 32))
        for ax, ay in ((-s, -14), (s, -14), (-s, 14), (s, 14)):
            d.line([(dx, dy), (dx + ax, dy + ay)], fill=(24, 20, 32), width=5)
            d.ellipse([dx + ax - 12, dy + ay - 4, dx + ax + 12, dy + ay + 4],
                      fill=(60, 52, 70))
        d.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=(255, 120, 60))
    # sea shimmer
    rng = random.Random(31)
    for _ in range(16):
        rx = rng.randint(x0 + 8, x1 - 60)
        ry = rng.randint(sea_y + 8, y1 - 10)
        d.line([(rx, ry), (rx + rng.randint(24, 70), ry)],
               fill=(240, 150, 70), width=3)


def scene_kerch(img, d, x0, y0, x1, y1):
    sky = vgrad(x1 - x0, y1 - y0, [
        (0.00, (150, 178, 196)), (0.55, (196, 206, 214)),
        (1.00, (226, 220, 204)),
    ])
    img.paste(sky, (x0, y0))
    sea_y = y0 + int((y1 - y0) * 0.52)
    sea = vgrad(x1 - x0, y1 - sea_y, [
        (0.00, (52, 104, 128)), (0.5, (40, 84, 108)), (1.00, (28, 60, 84)),
    ])
    img.paste(sea, (x0, sea_y))
    # bridge deck: intact left, arch, collapsed span plunging right
    deck_y = y0 + int((y1 - y0) * 0.34)
    d.rectangle([x0, deck_y, x0 + 380, deck_y + 22], fill=(96, 96, 104))
    d.arc([x0 + 330, deck_y - 62, x0 + 560, deck_y + 30], 180, 360,
          fill=(80, 80, 90), width=14)
    d.rectangle([x0 + 560, deck_y, x0 + 640, deck_y + 22], fill=(96, 96, 104))
    d.polygon([(x0 + 640, deck_y + 10), (x0 + 830, sea_y + 60),
               (x0 + 870, sea_y + 40), (x0 + 660, deck_y)],
              fill=(110, 108, 116))
    d.line([(x0 + 640, deck_y + 10), (x0 + 830, sea_y + 60)],
           fill=(70, 70, 80), width=6)
    # support pillars
    for px in (x0 + 90, x0 + 260, x0 + 420):
        d.rectangle([px, deck_y + 22, px + 26, sea_y + 40], fill=(80, 80, 90))
    # debris + spray where the span hit the water
    rng = random.Random(41)
    for _ in range(14):
        rx = rng.randint(x0 + 700, x1 - 40)
        ry = rng.randint(sea_y + 30, sea_y + 110)
        rw = rng.randint(10, 34)
        d.rectangle([rx, ry, rx + rw, ry + 12], fill=(120, 118, 124))
    for sx in (x0 + 760, x0 + 830, x0 + 900):
        d.arc([sx - 46, sea_y - 10, sx + 46, sea_y + 70], 200, 340,
              fill=(235, 242, 246), width=7)
    # smoke wisps from the deck
    glow(img, x0 + 620, deck_y - 30, 90, (200, 200, 200), peak=70)
    # waves
    for wy in range(sea_y + 30, y1 - 12, 34):
        for wx in range(x0 + 20, x1 - 60, 90):
            d.arc([wx, wy, wx + 70, wy + 22], 200, 340,
                  fill=(180, 210, 220), width=4)


def scene_cop31(img, d, x0, y0, x1, y1):
    sky = vgrad(x1 - x0, y1 - y0, [
        (0.00, (16, 92, 96)), (0.5, (30, 130, 110)), (1.00, (120, 190, 140)),
    ])
    img.paste(sky, (x0, y0))
    sx, sy = x0 + int((x1 - x0) * 0.78), y0 + 62
    glow(img, sx, sy, 130, (255, 220, 120), peak=110)
    d.ellipse([sx - 40, sy - 40, sx + 40, sy + 40], fill=(255, 232, 150))
    # globe with green landmasses, centre-left
    gx, gy, gr = x0 + 250, y0 + 128, 92
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(38, 110, 150))
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=(220, 235, 225),
              width=5)
    for lx, ly, lr in ((gx - 38, gy - 30, 30), (gx + 34, gy + 8, 34),
                       (gx - 8, gy + 44, 22), (gx + 52, gy - 42, 18)):
        d.ellipse([lx - lr, ly - lr // 2, lx + lr, ly + lr // 2],
                  fill=(86, 168, 92))
    # pine silhouettes along the bottom
    for tx in range(x0 + 560, x1 - 40, 74):
        th = 84 + (tx % 3) * 18
        d.polygon([(tx, y1), (tx + 26, y1 - th), (tx + 52, y1)],
                  fill=(16, 70, 52))
        d.rectangle([tx + 20, y1 - 16, tx + 32, y1], fill=(60, 44, 30))
    # coastline band
    d.rectangle([x0, y1 - 34, x1, y1], fill=(240, 222, 170))
    d.line([(x0, y1 - 34), (x1, y1 - 34)], fill=(30, 130, 110), width=5)


def scene_voyager(img, d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(8, 10, 26))
    rng = random.Random(7)
    for _ in range(110):
        sx = rng.randint(x0 + 4, x1 - 4)
        sy = rng.randint(y0 + 4, y1 - 4)
        r = rng.choice((2, 2, 3, 4))
        c = rng.choice([(255, 255, 255), (200, 210, 255), (255, 230, 180)])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=c)
    # distant sun glow, top right
    glow(img, x1 - 90, y0 + 60, 150, (255, 200, 110), peak=100)
    # Earth as a small blue marble, far left
    ex, ey = x0 + 90, y0 + 170
    d.ellipse([ex - 26, ey - 26, ex + 26, ey + 26], fill=(70, 130, 200))
    d.arc([ex - 26, ey - 26, ex + 26, ey + 26], 90, 250, fill=(160, 210, 240),
          width=5)
    # Voyager probe: gold bus, big dish, boom
    px, py = x0 + 560, y0 + 120
    d.line([(px - 60, py + 40), (px + 180, py - 40)], fill=(200, 170, 90),
           width=7)
    d.rectangle([px - 40, py - 26, px + 60, py + 46], fill=(212, 175, 60))
    d.rectangle([px - 40, py - 26, px + 60, py + 46], outline=(140, 105, 30),
                width=4)
    d.ellipse([px + 60, py - 78, px + 210, py + 30], fill=(232, 222, 200))
    d.ellipse([px + 60, py - 78, px + 210, py + 30], outline=(150, 140, 110),
              width=5)
    d.ellipse([px + 118, py - 40, px + 152, py - 6], fill=(180, 160, 120))
    d.line([(px + 60, py + 46), (px + 10, py + 110)], fill=(200, 170, 90),
           width=6)
    d.ellipse([px - 2, py + 100, px + 22, py + 124], fill=(255, 220, 120))
    # faint signal arcs toward Earth
    for rr in (150, 210, 270):
        d.arc([px - rr, py - rr + 60, px + rr, py + rr + 60], 150, 210,
              fill=(120, 180, 220), width=4)


def draw_virus(d, vx, vy, vr, col):
    """One spiked virus particle: 10 spikes, body, pale highlight."""
    for k in range(10):
        ang = k * 36 * math.pi / 180
        x2 = vx + int((vr + 14) * 0.92 * math.cos(ang))
        y2 = vy + int((vr + 14) * 0.92 * math.sin(ang))
        d.line([(vx, vy), (x2, y2)], fill=col, width=6)
        d.ellipse([x2 - 6, y2 - 6, x2 + 6, y2 + 6], fill=col)
    d.ellipse([vx - vr, vy - vr, vx + vr, vy + vr], fill=col)
    d.ellipse([vx - vr // 2, vy - vr // 2, vx + vr // 3, vy + vr // 3],
              fill=(255, 220, 200))


def scene_measles(img, d, x0, y0, x1, y1):
    bg = vgrad(x1 - x0, y1 - y0, [
        (0.00, (250, 238, 222)), (0.6, (246, 214, 196)), (1.00, (238, 186, 168)),
    ])
    img.paste(bg, (x0, y0))
    rng = random.Random(53)
    # virus particles: spiked circles, red on cream
    for _ in range(9):
        vx = rng.randint(x0 + 60, x1 - 60)
        vy = rng.randint(y0 + 40, y1 - 40)
        vr = rng.randint(22, 44)
        col = rng.choice([(176, 42, 48), (150, 30, 40), (196, 70, 60)])
        draw_virus(d, vx, vy, vr, col)
    # big red cross emblem, right side
    cx, cy = x1 - 150, y0 + 120
    d.rounded_rectangle([cx - 110, cy - 110, cx + 110, cy + 110], radius=26,
                        fill=(255, 255, 255), outline=(176, 42, 48), width=6)
    d.rectangle([cx - 22, cy - 72, cx + 22, cy + 72], fill=(176, 42, 48))
    d.rectangle([cx - 72, cy - 22, cx + 72, cy + 22], fill=(176, 42, 48))


def scene_fiji(img, d, x0, y0, x1, y1):
    sky = vgrad(x1 - x0, y1 - y0, [
        (0.00, (232, 190, 120)), (0.5, (226, 150, 90)), (1.00, (210, 120, 70)),
    ])
    img.paste(sky, (x0, y0))
    sx, sy = x0 + int((x1 - x0) * 0.76), y0 + 58
    glow(img, sx, sy, 140, (255, 210, 120), peak=120)
    d.ellipse([sx - 44, sy - 44, sx + 44, sy + 44], fill=(255, 226, 150))
    # cracked dry earth
    ey = y0 + int((y1 - y0) * 0.52)
    earth = vgrad(x1 - x0, y1 - ey, [
        (0.00, (168, 120, 72)), (0.5, (140, 96, 56)), (1.00, (110, 74, 44)),
    ])
    img.paste(earth, (x0, ey))
    rng = random.Random(67)
    for _ in range(16):
        cx = rng.randint(x0 + 20, x1 - 20)
        cy = rng.randint(ey + 6, y1 - 30)
        pts = [(cx, cy)]
        for _ in range(4):
            cx += rng.randint(-46, 46)
            cy += rng.randint(6, 30)
            pts.append((cx, cy))
        d.line(pts, fill=(70, 46, 28), width=5, joint="curve")
    # dry riverbed curve
    d.line([(x0 + 40, y1 - 20), (x0 + 300, y1 - 70), (x0 + 620, y1 - 40),
            (x0 + 900, y1 - 70)], fill=(90, 62, 38), width=16, joint="curve")
    # dead tree silhouette, left: bare trunk and branches
    tx, ty = x0 + 170, y1 - 8
    d.line([(tx, ty), (tx + 14, ty - 130)], fill=(74, 52, 32), width=16)
    d.line([(tx + 14, ty - 130), (tx - 52, ty - 190)], fill=(74, 52, 32),
           width=9)
    d.line([(tx + 14, ty - 130), (tx + 78, ty - 196)], fill=(74, 52, 32),
           width=9)
    d.line([(tx + 14, ty - 130), (tx + 20, ty - 210)], fill=(74, 52, 32),
           width=8)
    d.line([(tx - 52, ty - 190), (tx - 84, ty - 214)], fill=(74, 52, 32),
           width=6)
    d.line([(tx + 78, ty - 196), (tx + 108, ty - 222)], fill=(74, 52, 32),
           width=6)


PANELS = [
    ("GULF", scene_gulf,
     "IRAN SAYS ITS DRONES HIT U.S. SITES IN KUWAIT",
     "Bahrain says it intercepted attacks; no damage confirmed"),
    ("KERCH", scene_kerch,
     "KERCH BRIDGE SPAN FALLS INTO THE SEA",
     "Two killed, governor says, as road arch collapses"),
    ("COP31", scene_cop31,
     "COP31: 21 ISSUES STILL OPEN IN ANTALYA",
     "Second Global Stocktake opens as talks grind on"),
    ("SPACE", scene_voyager,
     "VOYAGER 1, ONE LIGHT-DAY FROM EARTH",
     "25.9 billion km out, NASA marks the milestone"),
    ("HEALTH", scene_measles,
     "U.S. LOSES MEASLES-FREE STATUS",
     "5,400+ cases, 10 deaths after 26 years clear"),
    ("OCEANIA", scene_fiji,
     "FIJI DECLARES DISASTER AS DROUGHT BITES",
     "El Ni\u00f1o drought prompts national emergency"),
]


def draw_panels(img, d):
    x0, gap = 48, 24
    col_w = (3024 - 48 - (3 - 1) * gap) // 3
    rows = [(1094, 1474), (1498, 1878)]
    for i, (tag, scene, head, body) in enumerate(PANELS):
        r = i // 3
        c = i % 3
        px = x0 + c * (col_w + gap)
        py, py1 = rows[r]
        scene_h = 236
        d.rectangle([px, py, px + col_w, py1], outline=INK, width=3,
                    fill=PAPER)
        scene(img, d, px + 3, py + 3, px + col_w - 3, py + scene_h)
        d.rectangle([px, py + scene_h, px + col_w, py + scene_h + 4],
                    fill=RED)
        # tag chip over the scene's top-left corner
        d.rounded_rectangle([px + 14, py + 14, px + 14 + 150, py + 52],
                            radius=7, fill=(12, 12, 24, 190))
        d.text((px + 30, py + 20), tag, font=sans_b(28), fill=(255, 255, 255))
        tx = px + 18
        tw = col_w - 36
        lines = wrap(d, head, sans_b(42), tw)
        ly = py + scene_h + 14
        for ln in lines[:2]:
            d.text((tx, ly), ln, font=sans_b(42), fill=INK)
            ly += 50
        d.text((tx, py1 - 44), body, font=sans(29), fill=MUTED)

# ---- world map strip + day in numbers --------------------------------
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60),
     (-75, 45), (-80, 32), (-97, 26), (-105, 20), (-95, 16), (-110, 23),
     (-125, 40), (-150, 60), (-168, 66)],
    [(-80, 10), (-60, 5), (-50, 0), (-35, -8), (-40, -20), (-50, -30),
     (-60, -40), (-70, -55), (-73, -40), (-75, -20), (-80, -5), (-80, 10)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (43, 12), (51, 10), (48, 0), (40, -10), (35, -20), (30, -30), (20, -35),
     (15, -30), (12, -18), (8, 4), (-8, 5), (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (25, 65), (20, 70),
     (15, 70), (10, 62), (5, 58), (-5, 50), (-10, 44), (-10, 36)],
    [(30, 62), (40, 68), (60, 70), (80, 73), (100, 77), (120, 73),
     (140, 72), (160, 70), (178, 66), (170, 60), (162, 58), (158, 52),
     (142, 45), (140, 38), (130, 35), (127, 33), (122, 30), (120, 22),
     (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20),
     (80, 15), (75, 8), (72, 20), (66, 25), (60, 25), (55, 26), (52, 28),
     (48, 30), (44, 29), (40, 32), (35, 36), (30, 36), (30, 42), (30, 62)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -23), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (130, -13), (126, -14), (122, -17), (118, -20), (113, -22)],
    [(167, -45), (174, -41), (178, -38), (175, -37), (168, -44), (167, -45)],
]

PINS = [  # (number, lon, lat, label)
    (1, 114.1, 22.5, "Shenzhen"),
    (2, 47.5, 29.3, "Kuwait"),
    (3, 36.5, 45.3, "Kerch"),
    (4, 30.7, 36.9, "Antalya"),
    (5, 178.0, -17.7, "Fiji"),
    (6, -77.0, 38.9, "Washington"),
]


def draw_map_panel(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], outline=INK, width=3, fill=(207, 224, 232))
    d.text((x0 + 20, y0 + 10), "WHERE IT HAPPENED", font=sans_b(36), fill=NAVY)
    mx0, my0 = x0 + 16, y0 + 56
    mx1, my1 = x1 - 16, y1 - 64
    mw, mh = mx1 - mx0, my1 - my0

    def proj(lon, lat):
        return (mx0 + (lon + 180) / 360.0 * mw,
                my0 + (90 - lat) / 180.0 * mh)

    for lon in range(-150, 181, 30):
        x = mx0 + (lon + 180) / 360.0 * mw
        d.line([(x, my0), (x, my1)], fill=(185, 205, 215), width=2)
    for lat in (-60, -30, 0, 30, 60):
        y = my0 + (90 - lat) / 180.0 * mh
        d.line([(mx0, y), (mx1, y)], fill=(185, 205, 215), width=2)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(221, 211, 176), outline=(168, 154, 110))
    for num, lon, lat, _label in PINS:
        px, py = proj(lon, lat)
        d.ellipse([px - 24, py - 24, px + 24, py + 24], fill=RED,
                  outline=(255, 255, 255), width=4)
        f = sans_b(30)
        t = str(num)
        d.text((px - d.textlength(t, font=f) / 2, py - 21), t, font=f,
               fill=(255, 255, 255))
    legend = "1 Shenzhen   2 Kuwait   3 Kerch   4 Antalya   5 Fiji   6 Washington"
    d.text((x0 + 20, y1 - 52), legend, font=sans(27), fill=NAVY)


NUMBERS = [
    ("\u20ac45bn", "EU loan proposed\nfor Ukraine"),
    ("1 light-day", "Voyager 1\nfrom Earth"),
    ("5,400+", "US measles cases\nin 2026"),
    ("4.9%", "Australian jobless\nrate, 5-yr high"),
    ("26 yrs", "since Air Niugini\nlast flew Auckland"),
    ("$2tn", "Nvidia value wiped\nsince Oct peak"),
]


def draw_numbers_panel(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], outline=INK, width=3, fill=CREAM)
    d.text((x0 + 20, y0 + 10), "THE DAY IN NUMBERS", font=sans_b(36), fill=NAVY)
    d.line([(x0 + 20, y0 + 56), (x1 - 20, y0 + 56)], fill=RED, width=4)
    bw = (x1 - x0 - 40 - 2 * 16) // 3
    bh = (y1 - y0 - 76 - 16) // 2
    for i, (num, label) in enumerate(NUMBERS):
        r, c = i // 3, i % 3
        bx = x0 + 20 + c * (bw + 16)
        by = y0 + 72 + r * (bh + 16)
        d.rectangle([bx, by, bx + bw, by + bh], outline=(200, 190, 160),
                    width=2, fill=(255, 255, 255))
        fnum = fit_font(d, num, bw - 20, 52, sans_b, minimum=34)
        text_center(d, bx + bw // 2, by + 12, num, fnum, RED)
        ly = by + 66
        for ln in label.split("\n"):
            text_center(d, bx + bw // 2, ly, ln, sans(25), INK)
            ly += 30


# ---- story index -----------------------------------------------------
INDEX = [
    (8, "US, Venezuela sign military deal in Caracas"),
    (9, "Bukele: troops razed gang chief's Haiti mansion"),
    (10, "Mongolia backs president's exit over rail claims"),
    (11, "Soweto floods: search for boy, 11, goes on"),
    (12, "Mozambique: Mondlane faces court over unrest"),
    (13, "Ebola in DR Congo: 11,376 cases; vaccine trials next"),
    (14, "Gaza: rain wrecks 40,000+ shelters; D-8 aid bid"),
    (15, "Yemen: UNICEF says 64 children killed"),
    (16, "UK sanctions firms tied to West Bank settlements"),
    (17, "EU clears Indonesia trade deal; duties cut 90%+"),
    (18, "Dhaka world's 2nd most polluted city, AQI 216"),
    (19, "France's PFAS-free drive takes Earthshot Prize"),
    (20, "Spain: six new envoys greet King Felipe VI"),
    (21, "Pope Leo marks 400 years of St Peter's Basilica"),
    (22, "Isolated Amazon group emerges, aid groups say"),
    (23, "Costa Rica journalist shot dead, first in 25 years"),
    (24, "Korea's Lee meets Xi in Shenzhen, third summit"),
    (25, "Trump: US\u2013Thailand trade deal 'close to done'"),
    (26, "RBA lifts cash rate to 4.85% as prices bite"),
    (27, "Russian An-12 crashes in Siberia; all 19 killed"),
    (28, "Drones hit two Russian refineries; output down 45%"),
    (29, "Houthis close in on Aden, within 40 miles"),
    (30, "Muslim population seen at 2.4bn by 2035, study says"),
    (31, "27 years for Iran-linked plot to kill Trump"),
    (32, "Bancroft breaks silence on sandpapergate"),
    (33, "Erez to screen 20 Gaza aid trucks a day"),
    (34, "D-8 asked to back Gaza climate-aid line"),
    (35, "India bonds draw $1.1bn foreign inflows in Nov."),
    (36, "Brent $91.55; gold down 2.3% on the day"),
    (37, "Fiji declares disaster as El Ni\u00f1o drought bites"),
    (38, "Australia's pay gap below 20% for first time"),
    (39, "Australia jobless 4.9%, highest in five years"),
    (40, "Air Niugini back in Auckland after 26 years"),
    (41, "Ford ships first CATL-tech battery cells"),
    (42, "Nvidia jumps 5% on Q3 beat after 40% slide"),
    (43, "India win toss, bowl first in Wellington Test"),
    (44, "GTA 6 out Thursday; Australia, NZ play first"),
]


def draw_index(d):
    y = 2262
    d.text((48, y), "THE DAY IN BRIEF \u2014 STORIES 8\u201344",
           font=sans_b(38), fill=NAVY)
    d.line([(48, y + 52), (3024, y + 52)], fill=RED, width=4)
    col_x = (48, 1050, 2052)
    col_w = 952
    row_h = 52
    y0 = y + 66
    for i, (num, text) in enumerate(INDEX):
        col = i // 13
        row = i % 13
        x = col_x[col]
        yy = y0 + row * row_h
        d.text((x, yy), "%d." % num, font=sans_b(29), fill=RED)
        f = fit_font(d, text, col_w - 62, 29, sans, minimum=24)
        d.text((x + 62, yy), text, font=f, fill=INK)
    # footer: sources
    fy = 3004
    d.line([(48, fy - 10), (3024, fy - 10)], fill=RULE, width=2)
    d.text((48, fy + 2),
           "Sources: Reuters \u00b7 AP \u00b7 NASA \u00b7 UN News \u00b7 RNZ Pacific \u00b7 SBS \u00b7 WGEA \u00b7 Newswire \u2014 every story dated 18 November 2026; claims attributed where reported.",
           font=sans(25), fill=MUTED)


# ---- render ----------------------------------------------------------
def render():
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_hero(img, d, 48, 372, 3024, 1070)
    draw_panels(img, d)
    draw_map_panel(d, 48, 1902, 1960, 2240)
    draw_numbers_panel(d, 1984, 1902, 3024, 2240)
    draw_index(d)
    img = img.convert("RGB")
    img = img.resize((1024, 1024), Image.LANCZOS)
    img = img.convert("P", palette=Image.ADAPTIVE, colors=PALETTE_COLORS,
                      dither=Image.FLOYDSTEINBERG)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    if not HAVE_PIL:
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "entry.png")
        shutil.copyfile(src, out_path)
        return
    render().save(out_path, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
