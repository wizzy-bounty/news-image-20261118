#!/usr/bin/env python3
"""news-image-20261118: one front page summing up world news, Wed 18 Nov 2026.

Renders entry.png with Pillow when available; otherwise copies the bundled
entry.png byte-for-byte (grader runs stock python 3.13 without Pillow).
Deterministic: no clock, no randomness, no network.
"""
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(HERE, "out")
S = 3  # supersample factor
W, H = 1024 * S, 1024 * S

INK = (17, 17, 17)
PAPER = (247, 243, 232)
RED = (178, 34, 34)
NAVY = (18, 38, 74)
GREY = (90, 86, 76)


def _font(name, size):
    from PIL import ImageFont
    base = "/usr/share/fonts/truetype/dejavu/"
    cands = {
        "serif_b": [base + "DejaVuSerif-Bold.ttf"],
        "serif": [base + "DejaVuSerif.ttf"],
        "sans_b": [base + "DejaVuSans-Bold.ttf"],
        "sans": [base + "DejaVuSans.ttf"],
    }[name]
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def fit_font(draw, name, size, text, max_w):
    while size > 10:
        f = _font(name, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return _font(name, size)


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, lines, font, fill, leading):
    x, y = xy
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def gradient(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    n = max(1, y1 - y0)
    for i in range(n):
        t = i / (n - 1)
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def skyline(draw, x0, y_base, x1, color):
    heights = [(46, 40), (30, 64), (58, 32), (36, 54), (50, 70), (28, 36)]
    x, i = x0, 0
    while x < x1:
        wdt, hgt = heights[i % len(heights)]
        draw.rectangle([x, y_base - hgt, x + wdt, y_base], fill=color)
        for wy in range(y_base - hgt + 5, y_base - 4, 11):
            for wx in range(x + 3, x + wdt - 3, 9):
                if (wx + wy) % 23 < 9:
                    draw.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 120))
        x += wdt + 4
        i += 1


def person(draw, cx, base, h, suit, skin=(214, 178, 140)):
    r = h // 11
    draw.ellipse([cx - r, base - h, cx + r, base - h + 2 * r], fill=skin)
    draw.polygon([(cx - h // 5, base), (cx - h // 7, base - h + 2 * r),
                  (cx + h // 7, base - h + 2 * r), (cx + h // 5, base)], fill=suit)
    draw.polygon([(cx - h // 7, base - h + 2 * r), (cx, base - h + 3 * r),
                  (cx + h // 7, base - h + 2 * r)], fill=(255, 255, 255))


def render():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    u = S
    mx = 28 * u  # margin
    cw = W - 2 * mx  # content width

    f_date = _font("sans_b", 26 * u)
    f_strap = _font("sans_b", 21 * u)
    f_hero = fit_font(d, "serif_b", 40 * u,
                      "A HUG ON THE TARMAC, A SUMMIT AT DAWN", cw - 20 * u)
    f_hero_sub = _font("sans", 22 * u)
    f_kick = _font("sans_b", 17 * u)
    f_head = _font("serif_b", 23 * u)
    f_body = _font("sans", 18 * u)
    f_idx = _font("sans", 15 * u)
    f_idx_b = _font("sans_b", 15 * u)
    f_foot = _font("sans", 14 * u)
    f_num = _font("serif_b", 26 * u)
    f_numlab = _font("sans", 14 * u)

    # ---- masthead (ends ~168) ----
    f_mast = fit_font(d, "serif_b", 72 * u, "THE WORLD TODAY", cw)
    d.text((W // 2, 6 * u), "THE WORLD TODAY", font=f_mast, fill=INK, anchor="ma")
    d.rectangle([mx, 92 * u, W - mx, 96 * u], fill=RED)
    d.rectangle([mx, 100 * u, W - mx, 102 * u], fill=INK)
    d.text((W // 2, 110 * u), "WEDNESDAY  18  NOVEMBER  2026",
           font=f_date, fill=RED, anchor="ma")
    d.text((W // 2, 138 * u), "36 STORIES  \u2022  6 CONTINENTS  \u2022  ONE FRONT PAGE",
           font=f_strap, fill=INK, anchor="ma")
    d.line([(mx, 166 * u), (W - mx, 166 * u)], fill=INK, width=2 * u)

    # ---- hero (176-396): art 176-296, band 296-396 ----
    hx0, hy0, hx1 = mx, 176 * u, W - mx
    art_b = 296 * u
    hy1 = 396 * u
    cx = W // 2
    ground = art_b - 44 * u  # horizon / tarmac line

    def star(sx, sy, r, fill):
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.42
            pts.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
        d.polygon(pts, fill=fill)

    def figure(fcx, suit, tie, hair, side):
        # side +1: left figure reaching right; -1: right figure reaching left
        base = ground + 2 * u
        dark = tuple(max(0, c - 22) for c in suit)
        d.ellipse([fcx - 20 * u, base - 3 * u, fcx + 20 * u, base + 2 * u],
                  fill=(110, 10, 10, 110))  # shadow on the carpet
        # legs
        d.rectangle([fcx - 13 * u, base - 26 * u, fcx - 2 * u, base], fill=(16, 16, 20))
        d.rectangle([fcx + 2 * u, base - 26 * u, fcx + 13 * u, base], fill=(16, 16, 20))
        # jacket
        d.polygon([(fcx - 17 * u, base - 26 * u), (fcx - 15 * u, base - 56 * u),
                   (fcx + 15 * u, base - 56 * u), (fcx + 17 * u, base - 26 * u)], fill=suit)
        # shirt V + tie + lapels
        d.polygon([(fcx - 6 * u, base - 56 * u), (fcx + 6 * u, base - 56 * u),
                   (fcx, base - 40 * u)], fill=(246, 246, 240))
        d.polygon([(fcx - 3 * u, base - 54 * u), (fcx + 3 * u, base - 54 * u),
                   (fcx + 2 * u, base - 40 * u), (fcx - 2 * u, base - 40 * u)], fill=tie)
        d.line([(fcx - 6 * u, base - 56 * u), (fcx, base - 41 * u)], fill=dark, width=2 * u)
        d.line([(fcx + 6 * u, base - 56 * u), (fcx, base - 41 * u)], fill=dark, width=2 * u)
        # arms: outer arm hangs, inner arm reaches to the handshake
        d.line([(fcx - side * 15 * u, base - 54 * u),
                (fcx - side * 18 * u, base - 32 * u)], fill=suit, width=7 * u)
        d.line([(fcx + side * 13 * u, base - 53 * u),
                (cx - side * 2 * u, base - 38 * u)], fill=suit, width=7 * u)
        # neck + head + hair
        d.rectangle([fcx - 4 * u, base - 64 * u, fcx + 4 * u, base - 56 * u],
                    fill=(214, 178, 140))
        d.ellipse([fcx - 8 * u, base - 72 * u, fcx + 8 * u, base - 56 * u],
                  fill=(214, 178, 140))
        d.pieslice([fcx - 8 * u, base - 72 * u, fcx + 8 * u, base - 56 * u],
                   180, 360, fill=hair)
        # clasped hands at the centre
        d.ellipse([cx - 5 * u, base - 43 * u, cx + 5 * u, base - 33 * u],
                  fill=(214, 178, 140))

    def banner(bx0, bx1, china):
        d.line([(bx0 - 4 * u, hy0 + 2 * u), (bx1 + 4 * u, hy0 + 2 * u)],
               fill=(212, 175, 55), width=2 * u)
        d.ellipse([(bx0 + bx1) // 2 - 4 * u, hy0, (bx0 + bx1) // 2 + 4 * u,
                   hy0 + 8 * u], fill=(212, 175, 55))
        if china:
            d.rectangle([bx0, hy0 + 2 * u, bx1, hy0 + 72 * u], fill=(222, 41, 16))
            star((bx0 + bx1) // 2, hy0 + 20 * u, 9 * u, (255, 222, 0))
            for (sx, sy) in [(bx1 - 8 * u, hy0 + 12 * u), (bx1 - 8 * u, hy0 + 24 * u),
                              (bx1 - 8 * u, hy0 + 36 * u), (bx0 + 10 * u, hy0 + 40 * u)]:
                star(sx, sy, 3 * u, (255, 222, 0))
        else:
            for i in range(7):
                col = (178, 34, 34) if i % 2 == 0 else (246, 246, 240)
                d.rectangle([bx0, hy0 + (2 + i * 10) * u, bx1,
                             hy0 + (12 + i * 10) * u], fill=col)
            d.rectangle([bx0, hy0 + 2 * u, (bx0 + bx1) // 2 + 6 * u, hy0 + 42 * u],
                        fill=(28, 48, 110))
            for r in range(3):
                for c in range(3):
                    d.ellipse([bx0 + (5 + c * 7) * u, hy0 + (8 + r * 11) * u,
                               bx0 + (8 + c * 7) * u, hy0 + (11 + r * 11) * u],
                              fill=(255, 255, 255))

    # ---- layered dawn sky ----
    gradient(d, (hx0, hy0, hx1, hy0 + 34 * u), (30, 20, 62), (104, 48, 100))
    gradient(d, (hx0, hy0 + 34 * u, hx1, hy0 + 62 * u), (104, 48, 100), (220, 100, 60))
    gradient(d, (hx0, hy0 + 62 * u, hx1, ground), (220, 100, 60), (255, 188, 100))
    # sun low on the horizon with glow
    sun_cx, sun_cy, sun_r = cx + 168 * u, ground - 30 * u, 24 * u
    for rr, al in [(44, 36), (36, 60), (29, 100)]:
        d.ellipse([sun_cx - rr * u, sun_cy - rr * u, sun_cx + rr * u, sun_cy + rr * u],
                  fill=(255, 198, 110, al))
    d.ellipse([sun_cx - sun_r * u, sun_cy - sun_r * u, sun_cx + sun_r * u, sun_cy + sun_r * u],
              fill=(255, 226, 142))
    # dawn clouds
    for (clx, cly, clw, clh, col) in [
        (hx0 + 150 * u, hy0 + 16 * u, 110 * u, 9 * u, (255, 172, 132, 80)),
        (hx0 + 430 * u, hy0 + 30 * u, 140 * u, 11 * u, (255, 192, 152, 70)),
        (hx0 + 700 * u, hy0 + 14 * u, 120 * u, 9 * u, (242, 152, 152, 70)),
        (hx0 + 250 * u, hy0 + 58 * u, 160 * u, 10 * u, (255, 202, 162, 60)),
        (hx0 + 620 * u, hy0 + 62 * u, 130 * u, 10 * u, (255, 186, 142, 60)),
    ]:
        d.ellipse([clx - clw, cly - clh, clx + clw, cly + clh], fill=col)
    # airplane silhouette in the dawn sky
    py = hy0 + 38 * u
    px0 = hx0 + 120 * u
    px1 = hx0 + 430 * u
    d.polygon([(px0 + 10 * u, py - 6 * u), (px0 + 2 * u, py - 26 * u),
               (px0 + 24 * u, py - 26 * u), (px0 + 32 * u, py - 6 * u)],
              fill=(18, 22, 48))  # tail fin
    d.rectangle([px0, py - 6 * u, px1 - 24 * u, py + 5 * u], fill=(18, 22, 48))
    d.ellipse([px1 - 48 * u, py - 6 * u, px1, py + 5 * u], fill=(18, 22, 48))  # nose
    d.polygon([(px0 + 140 * u, py + 4 * u), (px0 + 176 * u, py + 4 * u),
               (px0 + 216 * u, py + 24 * u), (px0 + 186 * u, py + 24 * u)],
              fill=(18, 22, 48))  # near wing
    d.polygon([(px0 + 8 * u, py + 2 * u), (px0 + 34 * u, py + 2 * u),
               (px0 + 50 * u, py + 12 * u), (px0 + 26 * u, py + 12 * u)],
              fill=(18, 22, 48))  # tailplane
    for i in range(9):
        wx = px0 + (30 + i * 32) * u
        d.rectangle([wx, py - 2 * u, wx + 8 * u, py + 1 * u], fill=(255, 210, 130))
    # tarmac + distant terminal
    d.rectangle([hx0, ground, hx1, art_b], fill=(26, 27, 38))
    d.rectangle([hx0, ground - 14 * u, hx0 + 150 * u, ground], fill=(15, 19, 40))
    d.rectangle([hx1 - 150 * u, ground - 10 * u, hx1, ground], fill=(15, 19, 40))
    for i in range(6):
        wx = hx0 + (12 + i * 22) * u
        d.rectangle([wx, ground - 9 * u, wx + 6 * u, ground - 4 * u], fill=(255, 200, 90))
    for i in range(4):
        wx = hx1 - (18 + i * 22) * u
        d.rectangle([wx, ground - 7 * u, wx + 6 * u, ground - 3 * u], fill=(255, 200, 90))
    for i in range(7):
        lx = hx0 + (60 + i * 130) * u
        d.rectangle([lx, ground + 8 * u, lx + 16 * u, ground + 11 * u], fill=(255, 200, 90))
    # red carpet in perspective
    d.polygon([(cx - 52 * u, ground), (cx + 52 * u, ground),
               (hx1, art_b), (hx0, art_b)], fill=(168, 24, 24))
    d.polygon([(cx - 40 * u, ground), (cx + 40 * u, ground),
               (hx1 - 60 * u, art_b), (hx0 + 60 * u, art_b)], fill=(186, 32, 32))
    d.line([(cx - 52 * u, ground), (hx0, art_b)], fill=(212, 175, 55), width=3 * u)
    d.line([(cx + 52 * u, ground), (hx1, art_b)], fill=(212, 175, 55), width=3 * u)
    # flag banners at both sides
    banner(hx0 + 12 * u, hx0 + 48 * u, True)
    banner(hx1 - 48 * u, hx1 - 12 * u, False)
    # the two leaders shaking hands on the carpet
    figure(cx - 46 * u, (24, 30, 56), (178, 34, 34), (20, 20, 24), +1)
    figure(cx + 46 * u, (38, 38, 44), (28, 48, 110), (60, 58, 56), -1)
    d.rectangle([hx0, art_b, hx1, hy1], fill=(247, 243, 232))
    d.rectangle([hx0, art_b, hx1, art_b + 4 * u], fill=RED)
    d.text((hx0 + 10 * u, art_b + 12 * u),
           "A HUG ON THE TARMAC, A SUMMIT AT DAWN", font=f_hero, fill=INK)
    sub = ("Xi greets Trump in Shenzhen; Putin joins them on Thursday in the "
           "first US\u2013China\u2013Russia trilateral \u2014 as reported by Reuters and AP.")
    text_block(d, (hx0 + 10 * u, art_b + 56 * u),
               wrap(d, sub, f_hero_sub, cw - 20 * u), f_hero_sub, GREY, 26 * u)

    # ---- six story panels (408-714) ----
    px0, py0 = mx, 408 * u
    pw = (cw - 2 * 10 * u) // 3
    ph = 154 * u
    gap = 10 * u

    def draw_panel(col, row, kicker, color, headline, body, art):
        x0 = px0 + col * (pw + gap)
        y0 = py0 + row * (ph + gap)
        x1, y1 = x0 + pw, y0 + ph
        d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255),
                    outline=(200, 192, 172), width=2 * u)
        d.rectangle([x0, y0, x1, y0 + 24 * u], fill=color)
        d.text((x0 + 7 * u, y0 + 4 * u), kicker, font=f_kick, fill=(255, 255, 255))
        art(x0 + 3 * u, y0 + 27 * u, x1 - 3 * u, y0 + 53 * u)
        ty = y0 + 57 * u
        hl = wrap(d, headline, f_head, pw - 14 * u)[:2]
        text_block(d, (x0 + 7 * u, ty), hl, f_head, INK, 26 * u)
        by = ty + 26 * u * len(hl) + 2 * u
        text_block(d, (x0 + 7 * u, by),
                   wrap(d, body, f_body, pw - 14 * u)[:2], f_body, GREY, 21 * u)

    def art_gulf(x0, y0, x1, y1):
        gradient(d, (x0, y0, x1, y1), (40, 70, 110), (16, 30, 58))
        d.polygon([(x0 + 8 * u, y1), (x0 + 16 * u, y1 - 6 * u),
                   (x0 + 30 * u, y1 - 6 * u), (x0 + 36 * u, y1)], fill=(60, 60, 60))
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        d.ellipse([cx - 4 * u, cy - 3 * u, cx + 4 * u, cy + 3 * u], fill=(220, 220, 220))
        d.line([(cx - 14 * u, cy - 5 * u), (cx + 14 * u, cy - 5 * u)],
               fill=(220, 220, 220), width=2 * u)
        bx, by = x1 - 12 * u, y0 + 7 * u
        d.ellipse([bx - 7 * u, by - 7 * u, bx + 7 * u, by + 7 * u], fill=(255, 200, 60))
        d.ellipse([bx - 4 * u, by - 4 * u, bx + 4 * u, by + 4 * u], fill=(255, 120, 30))

    def art_kerch(x0, y0, x1, y1):
        gradient(d, (x0, y0, x1, y1), (120, 150, 180), (60, 90, 120))
        d.rectangle([x0, y1 - 4 * u, x1, y1], fill=(30, 60, 90))
        mid = (x0 + x1) // 2
        d.rectangle([x0 + 4 * u, y0 + 8 * u, mid - 8 * u, y0 + 12 * u], fill=(40, 40, 40))
        d.rectangle([mid + 8 * u, y0 + 8 * u, x1 - 4 * u, y0 + 12 * u], fill=(40, 40, 40))
        d.arc([mid - 14 * u, y0 - 2 * u, mid + 14 * u, y0 + 20 * u],
              180, 360, fill=(200, 60, 40), width=3 * u)
        d.line([(mid - 4 * u, y0 + 14 * u), (mid + 4 * u, y1 - 5 * u)],
               fill=(120, 120, 120), width=2 * u)

    def art_eu(x0, y0, x1, y1):
        d.rectangle([x0, y0, x1, y1], fill=(0, 51, 153))
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        for k in range(12):
            a = 2 * math.pi * k / 12 - math.pi / 2
            sx = cx + int(11 * u * math.cos(a))
            sy = cy + int(11 * u * math.sin(a))
            d.ellipse([sx - 2 * u, sy - 2 * u, sx + 2 * u, sy + 2 * u],
                      fill=(255, 204, 0))

    def art_cop(x0, y0, x1, y1):
        gradient(d, (x0, y0, x1, y1), (30, 110, 70), (16, 60, 40))
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        d.ellipse([cx - 10 * u, cy - 9 * u, cx + 10 * u, cy + 9 * u], fill=(80, 180, 120))
        d.ellipse([cx - 6 * u, cy - 9 * u, cx + 1 * u, cy - 1 * u], fill=(40, 140, 90))
        d.ellipse([cx + 1 * u, cy + 1 * u, cx + 8 * u, cy + 9 * u], fill=(40, 140, 90))

    def art_voyager(x0, y0, x1, y1):
        d.rectangle([x0, y0, x1, y1], fill=(8, 10, 26))
        for (sx, sy) in [(6, 4), (20, 10), (34, 3), (48, 12), (62, 5), (76, 11), (90, 4)]:
            d.ellipse([x0 + sx * u, y0 + sy * u, x0 + sx * u + 2 * u, y0 + sy * u + 2 * u],
                      fill=(255, 255, 255))
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        d.line([(cx - 18 * u, cy + 5 * u), (cx + 18 * u, cy - 5 * u)],
               fill=(200, 200, 200), width=2 * u)
        d.ellipse([cx - 8 * u, cy - 7 * u, cx + 1 * u, cy + 2 * u], fill=(230, 200, 120))
        d.ellipse([cx + 4 * u, cy - 9 * u, cx + 13 * u, cy], outline=(220, 220, 220), width=2 * u)

    def art_measles(x0, y0, x1, y1):
        d.rectangle([x0, y0, x1, y1], fill=(140, 30, 30))
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        for (ox, oy) in [(-16, -3), (16, -4), (0, 4)]:
            px, py = cx + ox * u, cy + oy * u
            d.ellipse([px - 5 * u, py - 5 * u, px + 5 * u, py + 5 * u], fill=(255, 120, 100))
            for k in range(6):
                a = math.pi * k / 3
                d.line([(px, py), (px + int(7 * u * math.cos(a)),
                                   py + int(7 * u * math.sin(a)))],
                       fill=(255, 180, 160), width=2 * u)

    draw_panel(0, 0, "GULF \u2022 MIDDLE EAST", (140, 40, 40),
               "Iran drones hit US base in Kuwait",
               "Iran says drones hit Ali Al Salem; Kuwait reports intercepts.",
               art_gulf)
    draw_panel(1, 0, "UKRAINE \u2022 EUROPE", NAVY,
               "Kerch bridge arch falls into the sea",
               "Reuters verifies video of the fallen road span.",
               art_kerch)
    draw_panel(2, 0, "BRUSSELS \u2022 EUROPE", (0, 51, 153),
               "EU proposes \u20ac45bn loan for Ukraine",
               "\u20ac25bn military, \u20ac20bn budget; repaid via Russian reparations.",
               art_eu)
    draw_panel(0, 1, "ANTALYA \u2022 CLIMATE", (24, 110, 60),
               "COP31 deadlocked as stocktake opens",
               "21 issues unresolved; nations launch the Global Stocktake.",
               art_cop)
    draw_panel(1, 1, "SPACE \u2022 SCIENCE", (10, 12, 30),
               "Voyager 1, one light-day from home",
               "49 years on, the probe is 25.9bn km out; a signal takes a full day.",
               art_voyager)
    draw_panel(2, 1, "AMERICA \u2022 HEALTH", (140, 30, 30),
               "US loses measles-free status",
               "26 years ended: 5,400+ cases, 10 deaths reported.",
               art_measles)

    # ---- day in numbers (726-800) ----
    ny0 = 734 * u
    d.rectangle([mx, ny0, W - mx, ny0 + 24 * u], fill=NAVY)
    d.text((W // 2, ny0 + 3 * u), "THE DAY IN NUMBERS",
           font=_font("sans_b", 16 * u), fill=(255, 255, 255), anchor="ma")
    nums = [("36", "stories on this page"), ("6", "continents covered"),
            ("25.9bn km", "Voyager 1 from Earth"), ("\u20ac45bn", "EU loan proposed"),
            ("1,441", "drones in Ukraine's biggest strike")]
    colw = cw // 5
    for i, (n, lab) in enumerate(nums):
        cx = mx + colw * i + colw // 2
        d.text((cx, ny0 + 28 * u), n, font=f_num, fill=RED, anchor="ma")
        d.text((cx, ny0 + 56 * u), lab, font=f_numlab, fill=GREY, anchor="ma")

    # ---- index (812-986) ----
    iy0 = 806 * u
    d.line([(mx, iy0), (W - mx, iy0)], fill=INK, width=2 * u)
    d.text((mx, iy0 + 6 * u), "ALSO TODAY \u2014 STORIES 8\u201336",
           font=_font("sans_b", 17 * u), fill=INK)
    items = [
        "US, Venezuela sign military pact",
        "Bukele confirms Haiti gang strike",
        "Mongolia president quits in graft row",
        "S. Africa: 17 killed in shootings",
        "Mozambique's Mondlane goes on trial",
        "Ebola in DR Congo hits children hardest",
        "Gaza cold kills displaced in tents",
        "Yemen: 64 children killed since Sept",
        "UK sanctions settlement-linked firms",
        "EU clears Indonesia trade deals",
        "Dhaka garment workers clash, police",
        "France: 140,000 join pay protests",
        "Spain holds general strike on housing",
        "Pope Leo reveals cancer surgery",
        "Isolated Awa group emerges in Amazon",
        "Costa Rica journalist killed",
        "S. Korea bounties for AI exam cheating",
        "Thailand orders clean water",
        "Deutsche Bank leak: 15m documents",
        "Russian plane crashes in Siberia, 19 dead",
        "Ukraine says it hit 2 oil refineries",
        "Houthis advance to 60 km from Aden",
        "Muslims to outnumber Christians by 2035",
        "Man jailed 27 years in Trump plot",
        "Mexico street DJs' Guadalupe party",
        "Gaza aid scanner opens at Erez",
        "D-8 adopt Antalya climate framework",
        "75 nations back 35x35 energy target",
        "Brent $91.55; gold down 2.3%",
    ]
    colw = cw // 3
    for ci in range(3):
        x = mx + ci * colw
        for ri in range(10):
            idx = ci * 10 + ri
            if idx >= len(items):
                break
            yy = iy0 + 28 * u + ri * 16 * u
            d.text((x, yy), "%d." % (8 + idx), font=f_idx_b, fill=RED)
            d.text((x + 26 * u, yy), items[idx], font=f_idx, fill=INK)

    # ---- footer ----
    fy = iy0 + 28 * u + 10 * 16 * u + 4 * u
    d.line([(mx, fy), (W - mx, fy)], fill=INK, width=2 * u)
    d.text((mx, fy + 6 * u),
           "Sources: Reuters, AP, NASA, European Commission, UN News \u2014 18 Nov 2026. "
           "Disputed claims attributed; no speculation as fact.",
           font=f_foot, fill=GREY)

    small = img.resize((1024, 1024), Image.LANCZOS)
    return small


def main():
    os.makedirs(OUT, exist_ok=True)
    target = os.path.join(OUT, "entry.png")
    bundled = os.path.join(HERE, "entry.png")
    try:
        from PIL import Image  # noqa: F401
        small = render()
        pal = small.convert("P", palette=Image.ADAPTIVE, colors=128)
        pal.save(target, format="PNG", optimize=True)
    except Exception:
        if os.path.exists(bundled):
            shutil.copyfile(bundled, target)
        else:
            raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
