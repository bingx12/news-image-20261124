#!/usr/bin/env python3
"""THE WORLD TODAY — front page for Tuesday 24 November 2026.

Pure-stdlib Python 3.13. Draws a 1024x1024 newspaper front page from
bitmap glyphs (font_data.py, DejaVu Sans Book + Bold at one 64px base
size, only the glyphs the page text uses) and writes /output/entry.png.
Deterministic: no time, no randomness, no network, fixed zlib level.
"""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import font_data

W = 1024
H = 1024

PAPER = (246, 241, 227)
INK = (23, 19, 12)
RED = (169, 35, 24)
BLUE = (30, 78, 140)
GREEN = (28, 122, 51)
GOLD = (185, 138, 29)
GREY = (107, 99, 85)
RULE = (201, 191, 166)
SOFT = (238, 231, 214)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:(yy * self.w + x1) * 3] = bytes(c) * (x1 - x0)

    def outline(self, x, y, w, h, c, t=2):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d - r * r) <= r * 2:
                        self.set(xx, yy, c)

    def ellipse_arc(self, cx, cy, rx, ry, c):
        for deg in range(0, 360):
            import math
            a = math.radians(deg)
            self.set(int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a)), c)


def glyph(font, ch):
    table = font_data.FONTS[font]
    if ch not in table:
        raise KeyError("missing glyph %r in %s" % (ch, font))
    return table[ch]


def adv_of(font, size, ch):
    return max(1, round(glyph(font, ch)[0] * size / font_data.BASE))


def text_w(font, size, text):
    return sum(adv_of(font, size, ch) for ch in text)


def draw_text(cv, x, baseline, text, font, size, color):
    pen = x
    for ch in text:
        adv, bx, by, w, h, bits = glyph(font, ch)
        if w and h:
            sc = size / font_data.BASE
            sw = max(1, int(round(w * sc)))
            sh = max(1, int(round(h * sc)))
            gx = pen + int(round(bx * sc))
            gy = baseline + int(round(by * sc))
            for dy in range(sh):
                sy = min(h - 1, int(dy / sc))
                row = bits
                for dx in range(sw):
                    sx = min(w - 1, int(dx / sc))
                    bit = (row[sy * w + sx >> 3] >> (7 - ((sy * w + sx) & 7))) & 1
                    if bit:
                        cv.set(gx + dx, gy + dy, color)
        pen += adv_of(font, size, ch)
    return pen


def draw_centered(cv, cx, baseline, text, font, size, color):
    draw_text(cv, cx - text_w(font, size, text) // 2, baseline, text,
              font, size, color)


def wrap(font, size, text, max_w):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(font, size, trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(cv, x, y, text, font, size, color, max_w, leading):
    yy = y
    for ln in wrap(font, size, text, max_w):
        draw_text(cv, x, yy, ln, font, size, color)
        yy += leading
    return yy


def kicker(cv, x, y, text):
    draw_text(cv, x, y, text, "bold", 19, RED)
    cv.hline(x, y + 8, text_w("bold", 19, text), RED, 2)
    return y + 8


def headline(cv, x, y, text, size, max_w, leading):
    return para(cv, x, y, text, "bold", size, INK, max_w, leading)


def headline_lines(cv, x, y, lines, size, leading):
    yy = y
    for ln in lines:
        draw_text(cv, x, yy, ln, "bold", size, INK)
        yy += leading
    return yy


# ---------------------------------------------------------------- page

def build():
    cv = Canvas(W, H, PAPER)
    m = 36                      # margin
    right = W - m

    # --- masthead ---------------------------------------------------
    mast_size = 96
    while text_w("bold", mast_size, "THE WORLD TODAY") > right - m:
        mast_size -= 1
    draw_centered(cv, W // 2, 112, "THE WORLD TODAY", "bold", mast_size, INK)
    cv.hline(m, 132, right - m, INK, 4)
    cv.hline(m, 140, right - m, INK, 1)
    draw_text(cv, m, 168, "TUESDAY 24 NOVEMBER 2026", "bold", 22, INK)
    draw_text(cv, right - text_w("bold", 22, "EDITION No. 328"), 168,
              "EDITION No. 328", "bold", 22, INK)
    cv.hline(m, 180, right - m, INK, 2)

    # --- lead story -------------------------------------------------
    lx = m
    lw = 600                    # lead text column width
    ax = 668                    # lead art column x
    aw = right - ax
    kicker(cv, lx, 214, "MARKETS · TECHNOLOGY")
    y = headline(cv, lx, 292, "HUANG IS BACK", 66, lw, 72)
    y = para(cv, lx, 330,
             "Nvidia reinstates its founder as chief executive, 11 days "
             "after he quit — and the shares soar 31%.",
             "bold", 24, INK, lw, 31)
    para(cv, lx, 424,
         "The board voted unanimously on Monday, saying it had taken "
         "input from senior US officials and saw no national security "
         "risk. President Trump claimed credit: \"I made the deal.\" "
         "The Nasdaq jumped 6.9% and the S&P 500 rose 5%.",
         "book", 19, INK, lw, 25)
    # lead art: chip + rocketing chart
    cv.rect(ax, 212, aw, 288, SOFT)
    cv.outline(ax, 212, aw, 288, INK, 2)
    # chip
    cx0, cy0, cs = ax + 28, 244, 92
    cv.rect(cx0, cy0, cs, cs, BLUE)
    cv.rect(cx0 + 10, cy0 + 10, cs - 20, cs - 20, PAPER)
    cv.rect(cx0 + 30, cy0 + 30, cs - 60, cs - 60, BLUE)
    for i in range(5):
        px = cx0 + 14 + i * 17
        cv.rect(px, cy0 - 12, 6, 12, BLUE)
        cv.rect(px, cy0 + cs, 6, 12, BLUE)
        py = cy0 + 14 + i * 17
        cv.rect(cx0 - 12, py, 12, 6, BLUE)
        cv.rect(cx0 + cs, py, 12, 6, BLUE)
    nv = "NV"
    draw_text(cv, cx0 + (cs - text_w("bold", 22, nv)) // 2, cy0 + 58,
              nv, "bold", 22, PAPER)
    # chart line climbing to the top right
    pts = [(ax + 150, 420), (ax + 185, 400), (ax + 215, 408),
           (ax + 245, 372), (ax + 272, 380), (ax + 300, 330)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cv.line(x0, y0, x1, y1, GREEN, 4)
    # arrowhead
    cv.line(pts[-1][0], pts[-1][1], pts[-1][0] - 16, pts[-1][1] + 2, GREEN, 4)
    cv.line(pts[-1][0], pts[-1][1], pts[-1][0] - 4, pts[-1][1] + 16, GREEN, 4)
    draw_text(cv, ax + 150, 318, "+31%", "bold", 52, GREEN)
    draw_text(cv, ax + 28, 466, "Nvidia shares, Monday — the biggest",
              "book", 17, GREY)
    draw_text(cv, ax + 28, 488, "one-day gain in company history.",
              "book", 17, GREY)

    # --- divider ----------------------------------------------------
    cv.hline(m, 516, right - m, INK, 3)

    # --- row 2: two columns -----------------------------------------
    hw = (right - m - 32) // 2
    x1 = m
    x2 = m + hw + 32
    y0 = 548
    # A: Canada–Qatar
    kicker(cv, x1, y0, "DIPLOMACY")
    # two small flags right of the kicker
    fy = y0 - 24
    cv.rect(x1 + 220, fy, 56, 34, (255, 255, 255))
    cv.outline(x1 + 220, fy, 56, 34, INK, 2)
    cv.rect(x1 + 242, fy, 12, 34, RED)
    cv.rect(x1 + 292, fy, 56, 34, (139, 31, 76))
    cv.outline(x1 + 292, fy, 56, 34, INK, 2)
    y = headline_lines(cv, x1, y0 + 40,
                       ["CANADA AND QATAR SIGN", "INVESTMENT PACT"], 30, 36)
    para(cv, x1, y + 8,
         "Prime ministers Carney and Sheikh Mohammed bin Abdulrahman "
         "Al Thani sign a foreign-investment protection deal at the "
         "two countries' first strategic dialogue — a step towards "
         "unlocking Qatari investment pledged in January.",
         "book", 18, INK, hw, 24)
    # B: Zelenskiy
    kicker(cv, x2, y0, "EUROPE")
    # little dome right of the kicker
    dx, dy = x2 + 250, y0 + 2
    cv.line(dx, dy, dx + 20, dy - 20, INK, 3)
    cv.line(dx + 20, dy - 20, dx + 40, dy, INK, 3)
    cv.hline(dx - 4, dy, 48, INK, 3)
    for i in range(3):
        cv.vline(dx + 2 + i * 13, dy - 11, 11, INK, 3)
    y = headline_lines(cv, x2, y0 + 40,
                       ["ZELENSKIY ADDRESSES", "GERMAN PARLIAMENT"], 30, 36)
    para(cv, x2, y + 8,
         "Ukraine's president speaks to the Bundestag in Berlin, "
         "pressing allies for more air defences as Russia keeps "
         "striking Ukrainian cities and power plants.",
         "book", 18, INK, hw, 24)
    cv.vline(m + hw + 16, y0, 240, RULE, 1)

    # --- divider ----------------------------------------------------
    cv.hline(m, 800, right - m, INK, 2)

    # --- row 3: three columns ---------------------------------------
    col_w = 296
    gap = 32
    xs = [m, m + col_w + gap, m + 2 * (col_w + gap)]
    y0 = 832
    # C: Iran
    kicker(cv, xs[0], y0, "GULF")
    y = headline_lines(cv, xs[0], y0 + 34,
                       ["IRAN VOWS TO FIGHT", "US NAVAL BLOCKADE"], 22, 28)
    para(cv, xs[0], y + 6,
         "Tehran says it will use \"all available tools\" to confront "
         "the American blockade.",
         "book", 17, INK, col_w, 22)
    # D: Congo
    kicker(cv, xs[1], y0, "COMMODITIES")
    y = headline_lines(cv, xs[1], y0 + 34,
                       ["CONGO HALTS", "COBALT EXPORTS"], 22, 28)
    para(cv, xs[1], y + 6,
         "The world's top producer suspends all cobalt exports from "
         "30 November, to fight oversupply.",
         "book", 17, INK, col_w, 22)
    # E: WFP
    kicker(cv, xs[2], y0, "AID")
    y = headline_lines(cv, xs[2], y0 + 34,
                       ["WFP: FIGHTING PUTS", "7M MORE AT RISK"], 22, 28)
    para(cv, xs[2], y + 6,
         "The UN food agency warns battles are jeopardising aid for "
         "more than seven million more people.",
         "book", 17, INK, col_w, 22)
    for vx in (m + col_w + 16, m + 2 * col_w + gap + 16):
        cv.vline(vx, y0, 140, RULE, 1)

    # --- ALSO strip -------------------------------------------------
    cv.hline(m, 984, right - m, INK, 2)
    draw_text(cv, m, 1002,
              "ALSO: Kilauea erupts in Hawaii · Belgium strike grounds "
              "flights · Nigeria boat rescue · Kenya-DR Congo restore ties",
              "book", 15, INK)
    draw_centered(cv, W // 2, 1019,
                  "Sources: Reuters · BBC · AP · Al Jazeera",
                  "book", 12, GREY)
    return cv


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path = os.path.join(out_dir, "entry.png")
    cv = build()
    write_png(cv, path)
    print("wrote %s (%dx%d)" % (path, cv.w, cv.h))


if __name__ == "__main__":
    main()
