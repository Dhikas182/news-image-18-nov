#!/usr/bin/env python3
"""The World Today - front page of Wednesday 18 November 2026.

A single deterministic program that draws a 1024x1024 newspaper front
page as a PNG, using only the Python standard library.  Every glyph is
drawn from a hand-written 5x7 bitmap font, every scene is drawn with
plain rectangles, lines, circles and polygons, and the PNG bytes are
assembled by hand, so running the program twice gives the same file.

Usage:
    python3 main.py [output-path]
If no path is given, the picture goes to $MAKEFUN_OUTPUT_DIR/entry.png
or to /output/entry.png.
"""

import math
import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

# --- Colours -------------------------------------------------------------
PAPER = (250, 243, 224)      # cream newsprint
WHITE = (255, 255, 255)
INK = (18, 18, 18)           # near-black
GREY = (105, 105, 105)       # captions and footer
RED = (198, 32, 32)          # section tags, bullets, accents
DARK = (38, 34, 42)          # skyline towers
SKY_TOP = (252, 186, 104)    # Shenzhen sunset, top band
SKY_MID = (247, 156, 70)     # Shenzhen sunset, middle band
SKY_LOW = (238, 128, 52)     # Shenzhen sunset, bottom band
TARMAC = (34, 34, 36)
PALE_BLUE = (192, 214, 236)
PALE_BLUE2 = (208, 226, 242)
SEA = (36, 108, 178)
NAVY = (13, 23, 54)
GOLD = (222, 172, 52)
GREEN = (112, 176, 96)
LIGHT_GREY = (229, 229, 229)
BLUE = (52, 96, 180)

# --- 5x7 bitmap font -----------------------------------------------------
# Each glyph is seven rows of five bits, written as strings of 0 and 1.
# Only capitals are stored; text is upper-cased before it is drawn.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "\u2022": ("00000", "01110", "11111", "11111", "01110", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
}

ADVANCE = 6  # font units from one glyph to the next


def text_width(text, scale):
    """Pixel width of text at the given scale."""
    if not text:
        return 0
    return len(text) * ADVANCE * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Canvas:
    """An RGB picture held as a flat bytearray."""

    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.buf = bytearray(background * (width * height))

    def px(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = colour[0]
            self.buf[i + 1] = colour[1]
            self.buf[i + 2] = colour[2]

    def rect(self, x, y, w, h, colour):
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, self.w)
        y1 = min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = colour[0]
                self.buf[i + 1] = colour[1]
                self.buf[i + 2] = colour[2]

    def hline(self, x, y, length, colour):
        self.rect(x, y, length, 1, colour)

    def vline(self, x, y, length, colour):
        self.rect(x, y, 1, length, colour)

    def line(self, x0, y0, x1, y1, colour):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.px(x, y, colour)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, colour):
        """Filled circle."""
        for dy in range(-r, r + 1):
            span = int(math.sqrt(max(r * r - dy * dy, 0)))
            self.rect(cx - span, cy + dy, span * 2 + 1, 1, colour)

    def ellipse(self, cx, cy, rx, ry, colour):
        """Filled ellipse."""
        for dy in range(-ry, ry + 1):
            frac = 1.0 - (dy * dy) / float(ry * ry)
            span = int(rx * math.sqrt(max(frac, 0.0)))
            self.rect(cx - span, cy + dy, span * 2 + 1, 1, colour)

    def ring(self, cx, cy, r, colour):
        """A thin circle outline, two pixels thick."""
        for dy in range(-r - 1, r + 2):
            for dx in range(-r - 1, r + 2):
                d = math.sqrt(dx * dx + dy * dy)
                if r - 1.0 <= d <= r + 0.5:
                    self.px(cx + dx, cy + dy, colour)

    def polygon(self, points, colour):
        """Scanline-filled polygon."""
        if len(points) < 3:
            return
        top = min(p[1] for p in points)
        bottom = max(p[1] for p in points)
        for y in range(top, bottom + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / float(y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                x_start = int(math.ceil(xs[k]))
                x_end = int(math.floor(xs[k + 1]))
                if x_end >= x_start:
                    self.rect(x_start, y, x_end - x_start + 1, 1, colour)

    def burst(self, cx, cy, outer, inner, colour, spikes=8):
        """A star burst: alternating long and short points."""
        points = []
        total = spikes * 2
        for i in range(total):
            radius = outer if i % 2 == 0 else inner
            angle = math.pi * i / spikes - math.pi / 2.0
            points.append((
                int(round(cx + radius * math.cos(angle))),
                int(round(cy + radius * math.sin(angle))),
            ))
        self.polygon(points, colour)

    def text(self, raw, x, y, scale, colour):
        """Draw text, upper-cased, at the given top-left corner."""
        s = raw.upper()
        for index, ch in enumerate(s):
            glyph = FONT.get(ch, FONT[" "])
            gx = x + index * ADVANCE * scale
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(gx + col * scale, y + row * scale,
                                  scale, scale, colour)

    def text_centred(self, raw, cx, y, scale, colour):
        x = cx - text_width(raw.upper(), scale) // 2
        self.text(raw, x, y, scale, colour)


def write_png(canvas, path):
    """Write the canvas as a 1024x1024 RGB PNG, filter byte 0 per row."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        start = y * stride
        raw += canvas.buf[start:start + stride]
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(png)
    return len(png)



# --- Scenes ----------------------------------------------------------------
# Every scene draws only inside its own box (sx, sy, sw, sh).  A dark
# label strip along the bottom of the taller scenes names the place.


def label_strip(cv, sx, sy, sw, sh, label):
    cv.rect(sx, sy + sh - 16, sw, 16, INK)
    cv.text_centred(label, sx + sw // 2, sy + sh - 14, 2, WHITE)


def scene_shenzhen(cv, sx, sy, sw, sh):
    # Three bands of orange sunset sky.
    cv.rect(sx, sy, sw, 60, SKY_TOP)
    cv.rect(sx, sy + 60, sw, 60, SKY_MID)
    cv.rect(sx, sy + 120, sw, sh - 120, SKY_LOW)
    # Low sun, top right.
    cv.circle(sx + sw - 72, sy + 34, 17, (244, 110, 36))
    # One white cloud, top left.
    cv.ellipse(sx + 96, sy + 30, 34, 10, WHITE)
    cv.ellipse(sx + 118, sy + 24, 22, 8, WHITE)
    tarmac_top = sy + sh - 36
    # Skyline of dark towers rising from the tarmac.
    towers = [
        (0, 52, 76), (58, 44, 106), (108, 58, 70), (172, 46, 136),
        (224, 62, 86), (292, 48, 116), (346, 58, 76), (410, 44, 96),
        (460, 56, 66), (522, 48, 90),
    ]
    for off, tw, th in towers:
        tx = sx + off
        cv.rect(tx, tarmac_top - th, tw, th, DARK)
    # Tall tower with a spire and a red beacon dot.
    tall_x = sx + 172
    cv.vline(tall_x + 22, tarmac_top - 136 - 18, 18, DARK)
    cv.circle(tall_x + 22, tarmac_top - 136 - 20, 3, RED)
    # A few small lit windows on the towers.
    for wx, wy in [(20, 84), (76, 56), (196, 96), (316, 66), (372, 88),
                   (432, 70), (484, 92), (544, 62)]:
        cv.rect(sx + wx, tarmac_top - wy, 3, 4, (255, 214, 110))
    # Dark tarmac band.
    cv.rect(sx, tarmac_top, sw, 36, TARMAC)
    # Small runway lights along the top of the tarmac.
    for lx in range(sx + 24, sx + sw - 16, 52):
        cv.circle(lx, tarmac_top + 5, 2, (255, 240, 170))
    # Red carpet strip, lower left.
    cv.rect(sx + 16, sy + sh - 27, 108, 6, RED)
    # White plane in the centre of the tarmac.
    cx = sx + sw // 2 + 28
    cy = tarmac_top + 10
    cv.ellipse(cx, cy, 58, 7, WHITE)
    cv.rect(cx - 56, cy - 6, 112, 12, WHITE)
    cv.polygon([(cx + 44, cy - 6), (cx + 58, cy - 24), (cx + 66, cy - 24),
                (cx + 60, cy - 6)], WHITE)
    cv.polygon([(cx - 12, cy + 6), (cx + 16, cy + 14), (cx + 32, cy + 14),
                (cx + 4, cy + 6)], (225, 225, 225))
    cv.rect(cx - 54, cy + 1, 108, 3, BLUE)
    # US flag on a pole, top left.
    cv.vline(sx + 22, sy + 18, 34, INK)
    for stripe in range(7):
        colour = RED if stripe % 2 == 0 else WHITE
        cv.rect(sx + 26, sy + 18 + stripe * 3, 36, 3, colour)
    cv.rect(sx + 26, sy + 18, 16, 11, (38, 62, 140))
    # Chinese flag on a pole, top right.
    cv.vline(sx + sw - 60, sy + 18, 34, INK)
    cv.rect(sx + sw - 56, sy + 18, 36, 22, (222, 32, 32))
    cv.burst(sx + sw - 48, sy + 26, 4, 2, (255, 214, 80), spikes=5)
    for dx, dy in [(10, 2), (12, 8), (8, 12)]:
        cv.circle(sx + sw - 48 + dx, sy + 18 + dy, 1, (255, 214, 80))
    label_strip(cv, sx, sy, sw, sh, "SHENZHEN, CHINA")


def scene_gulf(cv, sx, sy, sw, sh):
    # Pale sky, then sea from about 58% down.
    cv.rect(sx, sy, sw, 18, (216, 229, 236))
    cv.rect(sx, sy + 18, sw, 12, (202, 221, 234))
    sea_top = sy + 30
    cv.rect(sx, sea_top, sw, sh - 30, SEA)
    # Small pale sun.
    cv.circle(sx + sw - 64, sy + 10, 6, (255, 240, 180))
    # Black tanker hull across the sea, white superstructure, red funnel.
    cv.rect(sx + 10, sea_top, sw - 20, 9, (14, 14, 14))
    cv.rect(sx + 28, sea_top - 6, 8, 6, RED)
    cv.rect(sx + sw - 78, sea_top - 8, 28, 8, WHITE)
    cv.rect(sx + sw - 72, sea_top - 12, 6, 4, (14, 14, 14))
    # Orange fire burst at the bow, with a wisp of smoke.
    cv.burst(sx + sw - 18, sea_top + 4, 9, 4, (255, 140, 0))
    cv.burst(sx + sw - 18, sea_top + 4, 5, 2, (255, 214, 80))
    cv.circle(sx + sw - 26, sea_top - 8, 4, (170, 170, 170))
    cv.circle(sx + sw - 32, sea_top - 13, 3, (190, 190, 190))
    # White wave dashes on the sea.
    for wx, wy in [(44, 44), (120, 46), (196, 44), (260, 47)]:
        cv.rect(sx + wx, sy + wy, 18, 2, WHITE)


def scene_kerch(cv, sx, sy, sw, sh):
    # Pale blue sky, then sea from about 62% down.
    cv.rect(sx, sy, sw, 20, PALE_BLUE)
    cv.rect(sx, sy + 20, sw, 12, PALE_BLUE2)
    sea_top = sy + 32
    cv.rect(sx, sea_top, sw, sh - 32, SEA)
    # Small sun and a cloud.
    cv.circle(sx + 30, sy + 10, 5, (255, 236, 150))
    cv.ellipse(sx + 190, sy + 12, 20, 5, WHITE)
    # Bridge deck with a break at about 55% of the width.
    break_x = sx + int(sw * 0.55)
    deck_y = sy + 24
    cv.rect(sx + 6, deck_y, break_x - 9 - (sx + 6), 5, (28, 28, 28))
    cv.rect(break_x + 9, deck_y, sx + sw - 6 - (break_x + 9), 5,
            (28, 28, 28))
    # One pylon and a small grey arch over the left span.
    cv.rect(sx + 58, sy + 8, 5, 16, (90, 90, 90))
    cv.line(sx + 78, deck_y, sx + 102, sy + 9, (120, 120, 120))
    cv.line(sx + 102, sy + 9, sx + 126, deck_y, (120, 120, 120))
    # A dark slab tipped down into the water at the break.
    cv.polygon([(break_x - 9, deck_y + 5), (break_x + 2, deck_y + 5),
                (break_x - 2, sy + 46), (break_x - 12, sy + 46)],
               (22, 22, 22))
    # Two white splash circles below the break.
    cv.circle(break_x + 5, sy + 40, 4, WHITE)
    cv.circle(break_x + 17, sy + 44, 3, WHITE)
    # Orange explosion burst at the break.
    cv.burst(break_x, deck_y, 11, 5, (255, 140, 0))
    cv.burst(break_x, deck_y, 6, 3, (255, 214, 80))


def scene_capitol(cv, sx, sy, sw, sh):
    # Pale blue sky bands and a green lawn at the bottom.
    cv.rect(sx, sy, sw, 70, PALE_BLUE)
    cv.rect(sx, sy + 70, sw, 62, PALE_BLUE2)
    cv.rect(sx, sy + 132, sw, sh - 132, GREEN)
    cx = sx + sw // 2
    # Gold stars in the sky.
    for gx, gy in [(32, 22), (sw - 42, 32), (sw - 74, 18), (58, 44)]:
        cv.circle(sx + gx, sy + gy, 2, GOLD)
    # White Capitol: base block, a row of columns, and the dome.
    cv.rect(sx + 52, sy + 78, 200, 54, WHITE)
    cv.hline(sx + 52, sy + 78, 200, (200, 200, 200))
    for col in range(6):
        col_x = sx + 66 + col * 30
        cv.rect(col_x, sy + 88, 9, 44, (228, 228, 220))
    cv.ellipse(cx, sy + 52, 36, 28, WHITE)
    cv.rect(cx - 8, sy + 20, 16, 10, WHITE)
    cv.vline(cx, sy + 8, 12, GOLD)
    cv.circle(cx, sy + 16, 3, GOLD)
    # Blue ballot box at the front left, with a white check mark.
    cv.rect(sx + 14, sy + 102, 34, 30, (36, 82, 172))
    cv.rect(sx + 20, sy + 102, 22, 4, INK)
    cv.line(sx + 20, sy + 118, sx + 26, sy + 126, WHITE)
    cv.line(sx + 26, sy + 126, sx + 40, sy + 110, WHITE)
    cv.line(sx + 20, sy + 119, sx + 26, sy + 127, WHITE)
    cv.line(sx + 26, sy + 127, sx + 40, sy + 111, WHITE)
    label_strip(cv, sx, sy, sw, sh, "WASHINGTON, DC")


def scene_voyager(cv, sx, sy, sw, sh):
    # Dark navy starfield, stars placed by a fixed arithmetic pattern.
    cv.rect(sx, sy, sw, sh, NAVY)
    for i in range(30):
        star_x = sx + (i * 47 + 13) % sw
        star_y = sy + (i * 29 + 7) % (sh - 22)
        cv.circle(star_x, star_y, 1, WHITE if i % 3 else (190, 190, 210))
    # Small gold sun at the left, with a tiny blue Earth beside it.
    cv.circle(sx + 28, sy + 38, 9, GOLD)
    cv.circle(sx + 52, sy + 48, 4, (80, 140, 225))
    # Dotted pale signal line from Earth to the gold probe at the right.
    start_x, start_y = sx + 58, sy + 47
    end_x, end_y = sx + sw - 82, sy + 40
    for step in range(13):
        t = step / 12.0
        dot_x = int(start_x + t * (end_x - start_x))
        dot_y = int(start_y + t * (end_y - start_y))
        cv.circle(dot_x, dot_y, 1, (205, 205, 225))
    # Gold probe with a white dish ring, a boom and an antenna.
    probe_x = sx + sw - 78
    probe_y = sy + 34
    cv.rect(probe_x, probe_y, 28, 14, GOLD)
    cv.line(probe_x, probe_y + 7, probe_x - 10, probe_y + 7, (200, 200, 200))
    cv.ring(probe_x - 14, probe_y + 7, 10, WHITE)
    cv.line(probe_x + 14, probe_y, probe_x + 26, sy + 22, GOLD)
    cv.circle(probe_x + 26, sy + 22, 2, WHITE)
    # A fainter, smaller probe lower down.
    small_x = sx + sw - 118
    small_y = sy + 92
    cv.circle(small_x, small_y, 5, (170, 135, 45))
    cv.ring(small_x - 10, small_y, 6, (150, 150, 160))
    cv.line(small_x - 5, small_y, small_x - 10, small_y, (150, 150, 160))
    label_strip(cv, sx, sy, sw, sh, "INTERSTELLAR SPACE")


def scene_health(cv, sx, sy, sw, sh):
    # Light grey background.
    cv.rect(sx, sy, sw, sh, LIGHT_GREY)
    # White clinic building on the left, red cross sign on its roof.
    cv.rect(sx + 16, sy + 58, 130, 62, WHITE)
    cv.rect(sx + 66, sy + 36, 24, 24, WHITE)
    cv.rect(sx + 75, sy + 39, 6, 18, RED)
    cv.rect(sx + 69, sy + 45, 18, 6, RED)
    for wx in (30, 66, 102):
        cv.rect(sx + wx, sy + 72, 16, 12, (120, 170, 220))
        cv.rect(sx + wx, sy + 92, 16, 12, (120, 170, 220))
    cv.rect(sx + 66, sy + 102, 18, 18, (45, 45, 45))
    # Rising red bar chart on the right, with a black trend arrow.
    base_y = sy + 118
    heights = [18, 32, 48, 66]
    for i, bh in enumerate(heights):
        bar_x = sx + 170 + i * 26
        cv.rect(bar_x, base_y - bh, 18, bh, (205, 42, 42))
    cv.line(sx + 168, sy + 106, sx + 262, sy + 44, INK)
    cv.polygon([(sx + 262, sy + 44), (sx + 250, sy + 44),
                (sx + 262, sy + 56)], INK)
    # Small red virus dots above the chart: a circle with short spikes.
    for vx, vy in [(200, 28), (240, 18), (264, 36)]:
        cv.burst(sx + vx, sy + vy, 7, 3, RED, spikes=6)
        cv.circle(sx + vx, sy + vy, 3, (235, 70, 70))
    label_strip(cv, sx, sy, sw, sh, "USA AND DR CONGO")



# --- Page assembly ---------------------------------------------------------


def card_border(cv, x, y, w, h):
    """A white card with a 2px near-black rule border."""
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 2, INK)
    cv.rect(x, y + h - 2, w, 2, INK)
    cv.rect(x, y, 2, h, INK)
    cv.rect(x + w - 2, y, 2, h, INK)


def draw_panel(cv, x, y, w, h, scene, scene_h, tag, headline, captions,
               fact=None, lead=False):
    card_border(cv, x, y, w, h)
    scene(cv, x + 10, y + 8, w - 20, scene_h)
    cy = y + 8 + scene_h + 7
    cv.text(tag, x + 10, cy, 2, RED)
    cy += 17
    head_scale = 4 if lead else 3
    for line in headline:
        cv.text(line, x + 10, cy, head_scale, INK)
        cy += 7 * head_scale + 1
    cy += 2
    for line in captions:
        cv.text(line, x + 10, cy, 2, GREY)
        cy += 16
    if fact:
        cv.hline(x + 10, cy, w - 20, (170, 170, 170))
        cy += 6
        cv.text(fact, x + 10, cy, 2, GREY)


def build_page():
    cv = Canvas(WIDTH, HEIGHT, PAPER)
    # Masthead.
    cv.text_centred("THE WORLD TODAY", WIDTH // 2, 18, 8, INK)
    cv.text_centred("WEDNESDAY 18 NOVEMBER 2026", WIDTH // 2, 84, 3, RED)
    cv.hline(14, 112, 996, INK)
    cv.hline(14, 116, 996, INK)

    # Row A: the lead story, with two small panels beside it.
    draw_panel(cv, 14, 130, 626, 326, scene_shenzhen, 180,
               "SHENZHEN - DIPLOMACY",
               ["XI GREETS TRUMP", "IN SHENZHEN"],
               ["APEC OPENS; THREE-WAY TALKS THURSDAY",
                "XI AND PUTIN MET FIRST IN SHENZHEN"],
               lead=True)
    draw_panel(cv, 652, 130, 358, 157, scene_gulf, 52,
               "THE GULF",
               ["IRAN HITS KUWAIT", "AND BAHRAIN"],
               ["US STRUCK QESHM FIRST"])
    draw_panel(cv, 652, 299, 358, 157, scene_kerch, 52,
               "WAR IN UKRAINE",
               ["KERCH BRIDGE HIT", "FOR SECOND DAY"],
               ["SPAN FALLS; KYIV HIT BACK"])

    # Row B: three panels.
    draw_panel(cv, 14, 468, 324, 318, scene_capitol, 160,
               "WASHINGTON - POLITICS",
               ["PELTOLA WINS", "ALASKA SENATE"],
               ["DEMOCRATS TAKE 56-44", "FIRST ALASKA NATIVE"],
               fact="AP CALLED IT TUESDAY NIGHT")
    draw_panel(cv, 350, 468, 324, 318, scene_voyager, 156,
               "SPACE",
               ["VOYAGER 1", "ONE LIGHT-DAY"],
               ["16.1 BILLION MILES OUT", "SIGNALS NOW TAKE A DAY"],
               fact="FARTHEST OBJECT EVER")
    draw_panel(cv, 686, 468, 324, 318, scene_health, 160,
               "HEALTH",
               ["AMERICA LOSES", "ITS MEASLES-FREE", "STATUS"],
               ["5,412 CASES IN 2026", "EBOLA IN CONGO TOPS 11,000"],
               fact="STATUS HELD SINCE 2000")

    # Ticker: also on Wednesday.
    card_border(cv, 14, 798, 996, 210)
    cv.rect(24, 810, 16, 16, RED)
    cv.text("ALSO ON WEDNESDAY", 50, 808, 4, INK)
    items = [
        "CYCLONE AKVAN BEARS DOWN ON INDIA'S ANDHRA COAST",
        "RUSSIAN MILITARY PLANE CRASHES IN SIBERIA, 19 DEAD",
        "EU PROPOSES 45BN EURO LOAN FOR UKRAINE IN 2027",
        "CATEGORY 5 CYCLONE XAVIER HITS COOK ISLANDS",
    ]
    ty = 852
    for item in items:
        cv.rect(24, ty + 4, 10, 10, RED)
        cv.text(item, 44, ty, 3, INK)
        ty += 26
    cv.hline(24, 964, 976, (170, 170, 170))
    cv.text_centred("THE DAY IN ONE IMAGE - WEDNESDAY 18 NOVEMBER 2026",
                    WIDTH // 2, 976, 3, GREY)
    return cv


def default_output():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        return os.path.join(out_dir, "entry.png")
    return "/output/entry.png"


def main(argv):
    path = argv[1] if len(argv) > 1 else default_output()
    page = build_page()
    size = write_png(page, path)
    print("Wrote %s (%d bytes)" % (path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
