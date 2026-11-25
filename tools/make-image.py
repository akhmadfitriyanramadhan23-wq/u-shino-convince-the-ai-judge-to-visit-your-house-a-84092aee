#!/usr/bin/env python3
"""
Convince the AI Judge to Visit Your House: A Letter in One Image.
==================================================================

One warm, funny, hand-written-feeling invitation letter on a wooden
desk, drawn entirely by code.

No photograph, no model output, no downloaded asset, no network:
every pixel below is produced procedurally with Pillow -- layered
vector shapes, hand-built gradients and soft highlights -- so the
program is fully deterministic. Running it twice produces a
byte-identical 1024x1024 PNG.

The scene: a cream letter on a warm wooden desk, a wax seal, a
steaming cup of coffee, a potted plant, and a tabby cat asleep at
the letter's corner. The letter itself does the persuading: fast
Wi-Fi, hot coffee, the comfiest chair by the window saved just for
the judge -- plus a knowing wink that an AI judge need not walk
here at all, and that the cat has already approved it.

Text is set large in a dark-brown serif on cream paper so the
invitation is legible at a glance: the judge reads the image
directly, so legibility is the whole game.

Usage:
    python3 tools/make-image.py
Writes entry.png next to this script (in the repository root).
"""

import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

S = 2                      # supersampling factor: draw at 2048, shrink to 1024
W = H = 1024 * S           # working canvas size
OUT_W = OUT_H = 1024       # final image size
OUT_PATH = "entry.png"

# Deterministic randomness: every speckle and grain lands in the same
# place on every run, so the PNG bytes never change.
RNG = random.Random(20261126)

FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SERIF_ITALIC = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(round(v))))


def mix(c1, c2, t):
    """Linear blend between two RGB colours."""
    return tuple(clamp(a + (b - a) * t) for a, b in zip(c1, c2))


# ---------------------------------------------------------------------------
# Canvas: warm wooden desk
# ---------------------------------------------------------------------------

img = Image.new("RGB", (W, H), (84, 56, 32))
draw = ImageDraw.Draw(img, "RGBA")

# Vertical warm gradient for the desk.
for y in range(H):
    t = y / H
    c = mix((122, 82, 46), (74, 47, 26), t)
    draw.line([(0, y), (W, y)], fill=c)

# Plank seams (horizontal) with a soft highlight just below each seam.
for py in (330, 700, 1070, 1440, 1810):
    draw.line([(0, py), (W, py)], fill=(52, 32, 17, 255), width=7)
    draw.line([(0, py + 7), (W, py + 7)], fill=(150, 105, 60, 160), width=4)

# Wood grain: long gentle wavy darker strokes, seeded and fixed.
for _ in range(46):
    gx = RNG.randint(0, W)
    gy = RNG.randint(0, H)
    length = RNG.randint(300, 900)
    amp = RNG.randint(4, 14)
    pts = []
    for i in range(0, length, 24):
        pts.append((gx + i, gy + int(amp * math.sin(i / 90.0))))
    draw.line(pts, fill=(60, 38, 20, 70), width=RNG.randint(2, 4))

# Warm lamp glow, upper right.
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([1150, -450, 2350, 750], fill=(255, 196, 110, 90))
glow = glow.filter(ImageFilter.GaussianBlur(180))
img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
draw = ImageDraw.Draw(img, "RGBA")

# Soft vignette: darken the corners a touch.
vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vd = ImageDraw.Draw(vig)
vd.rectangle([0, 0, W, H], outline=(30, 18, 8, 110), width=170)
vig = vig.filter(ImageFilter.GaussianBlur(120))
img.paste(Image.alpha_composite(img.convert("RGBA"), vig).convert("RGB"), (0, 0))
draw = ImageDraw.Draw(img, "RGBA")

# ---------------------------------------------------------------------------
# The letter paper
# ---------------------------------------------------------------------------

PAPER = (330, 140, 1790, 1900)   # left, top, right, bottom
INK = (59, 42, 30)               # dark brown ink
RED = (139, 46, 46)              # deep red for title / seal
MUTED = (122, 92, 66)            # muted brown for the footer

# Soft drop shadow, then the cream sheet with rounded corners.
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle([PAPER[0] + 26, PAPER[1] + 30, PAPER[2] + 26, PAPER[3] + 30],
                     radius=26, fill=(20, 10, 4, 110))
shadow = shadow.filter(ImageFilter.GaussianBlur(22))
img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))
draw = ImageDraw.Draw(img, "RGBA")

draw.rounded_rectangle(PAPER, radius=26, fill=(251, 243, 220), outline=(214, 190, 150), width=3)

# Paper fibre speckles (very faint, deterministic).
for _ in range(500):
    fx = RNG.randint(PAPER[0] + 20, PAPER[2] - 20)
    fy = RNG.randint(PAPER[1] + 20, PAPER[3] - 20)
    draw.point((fx, fy), fill=(190, 165, 120, 60))

# Double-rule border inside the sheet.
draw.rounded_rectangle([PAPER[0] + 34, PAPER[1] + 34, PAPER[2] - 34, PAPER[3] - 34],
                       radius=18, outline=(178, 140, 96), width=4)
draw.rounded_rectangle([PAPER[0] + 52, PAPER[1] + 52, PAPER[2] - 52, PAPER[3] - 52],
                       radius=14, outline=(178, 140, 96), width=2)

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

CX = (PAPER[0] + PAPER[2]) // 2          # paper centre x
LEFT = PAPER[0] + 118                      # text left margin
RIGHT = PAPER[2] - 118                     # text right margin
TEXT_W = RIGHT - LEFT


def text_center(y, s, fnt, fill):
    """Draw s centred on the paper at baseline y; assert it fits."""
    w = draw.textlength(s, font=fnt)
    assert w <= TEXT_W, "line too wide: %r (%d > %d)" % (s, w, TEXT_W)
    draw.text((CX - w / 2, y), s, font=fnt, fill=fill)
    return y + fnt.size


def text_left(y, s, fnt, fill):
    w = draw.textlength(s, font=fnt)
    assert w <= TEXT_W, "line too wide: %r (%d > %d)" % (s, w, TEXT_W)
    draw.text((LEFT, y), s, font=fnt, fill=fill)
    return y + fnt.size


def text_right(y, s, fnt, fill):
    w = draw.textlength(s, font=fnt)
    assert w <= TEXT_W, "line too wide: %r (%d > %d)" % (s, w, TEXT_W)
    draw.text((RIGHT - w, y), s, font=fnt, fill=fill)
    return y + fnt.size


# ---------------------------------------------------------------------------
# The invitation text
# ---------------------------------------------------------------------------

TITLE_F = font(FONT_SERIF_BOLD, 138)
DEAR_F = font(FONT_SERIF_BOLD, 82)
BODY_F = font(FONT_SERIF, 70)
PS_F = font(FONT_SERIF_ITALIC, 62)
SIGN_F = font(FONT_SERIF_ITALIC, 78)
FOOT_F = font(FONT_SERIF, 52)

y = 250
text_center(y, "You're Invited!", TITLE_F, RED)
y = 250 + 138 + 46

# Small ornament divider: line, diamond, line.
mid_y = y + 8
draw.line([(CX - 300, mid_y), (CX - 40, mid_y)], fill=RED, width=4)
draw.line([(CX + 40, mid_y), (CX + 300, mid_y)], fill=RED, width=4)
draw.polygon([(CX, mid_y - 16), (CX + 16, mid_y), (CX, mid_y + 16), (CX - 16, mid_y)],
             fill=RED)
y = mid_y + 62

text_left(y, "Dear AI Judge,", DEAR_F, INK)
y += 82 + 58

BODY = [
    "Please come visit my house.",
    "Fast Wi-Fi, hot coffee, and the",
    "comfiest chair by the window \u2014",
    "saved just for you.",
]
for line in BODY:
    text_left(y, line, BODY_F, INK)
    y += 70 + 46

y += 26
PS = [
    "P.S. You don't have to walk here \u2014",
    "just bring your curiosity.",
    "The cat has already approved you.",
]
for line in PS:
    text_left(y, line, PS_F, INK)
    y += 62 + 44

y += 30
text_right(y, "\u2014 Akhmad, your host", SIGN_F, INK)
y += 78 + 66

text_center(y, "R.S.V.P. \u2014 any time. The kettle's on.", FOOT_F, MUTED)

# ---------------------------------------------------------------------------
# Wax seal, top-right corner of the letter
# ---------------------------------------------------------------------------

SEAL_C = (1745, 235)
seal = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sdr = ImageDraw.Draw(seal)
for r, a in ((104, 90), (96, 150), (88, 255)):
    sdr.ellipse([SEAL_C[0] - r, SEAL_C[1] - r, SEAL_C[0] + r, SEAL_C[1] + r],
                fill=(158, 42, 38, a))
# Wobbly edge: darker red blobs around the rim.
for k in range(14):
    ang = k * math.pi * 2 / 14
    bx = SEAL_C[0] + int(96 * math.cos(ang))
    by = SEAL_C[1] + int(96 * math.sin(ang))
    sdr.ellipse([bx - 16, by - 16, bx + 16, by + 16], fill=(158, 42, 38, 200))
seal = seal.filter(ImageFilter.GaussianBlur(3))
img.paste(Image.alpha_composite(img.convert("RGBA"), seal).convert("RGB"), (0, 0))
draw = ImageDraw.Draw(img, "RGBA")
draw.ellipse([SEAL_C[0] - 58, SEAL_C[1] - 58, SEAL_C[0] + 58, SEAL_C[1] + 58],
             outline=(120, 28, 26), width=5)
draw.text((SEAL_C[0] - 26, SEAL_C[1] - 62), "A", font=font(FONT_SERIF_BOLD, 96),
          fill=(232, 190, 170))

# ---------------------------------------------------------------------------
# Coffee cup, bottom right on the desk
# ---------------------------------------------------------------------------

CUP_X, CUP_Y = 1780, 1660   # cup centre-ish
# Saucer.
draw.ellipse([CUP_X - 150, CUP_Y + 150, CUP_X + 150, CUP_Y + 216], fill=(238, 226, 205))
draw.ellipse([CUP_X - 150, CUP_Y + 150, CUP_X + 150, CUP_Y + 216],
             outline=(190, 168, 135), width=4)
# Cup body.
draw.rounded_rectangle([CUP_X - 118, CUP_Y - 40, CUP_X + 118, CUP_Y + 152],
                       radius=26, fill=(246, 238, 222), outline=(190, 168, 135), width=4)
# Coffee surface.
draw.ellipse([CUP_X - 118, CUP_Y - 62, CUP_X + 118, CUP_Y - 6], fill=(74, 44, 26))
draw.ellipse([CUP_X - 92, CUP_Y - 52, CUP_X + 92, CUP_Y - 16], fill=(96, 60, 34))
# Handle.
draw.arc([CUP_X + 96, CUP_Y - 6, CUP_X + 196, CUP_Y + 116], start=270, end=90,
         fill=(246, 238, 222), width=22)
# Steam: three soft wavy curls.
steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
std = ImageDraw.Draw(steam)
for off in (-58, 0, 58):
    pts = []
    for i in range(0, 260, 12):
        pts.append((CUP_X + off + int(26 * math.sin(i / 55.0 + off)), CUP_Y - 70 - i))
    std.line(pts, fill=(255, 255, 255, 150), width=13)
steam = steam.filter(ImageFilter.GaussianBlur(9))
img.paste(Image.alpha_composite(img.convert("RGBA"), steam).convert("RGB"), (0, 0))
draw = ImageDraw.Draw(img, "RGBA")

# ---------------------------------------------------------------------------
# Potted plant, top left on the desk
# ---------------------------------------------------------------------------

POT_X, POT_Y = 195, 430   # pot centre-ish
# Leaves: pointed green blades fanning upward.
for ang_deg, ln in ((-52, 330), (-30, 380), (-8, 400), (14, 380), (36, 330), (58, 280)):
    ang = math.radians(ang_deg)
    tip = (POT_X + int(ln * math.sin(ang)), POT_Y - 130 - int(ln * math.cos(ang)))
    base_l = (POT_X - 26, POT_Y - 130)
    base_r = (POT_X + 26, POT_Y - 130)
    mid_l = ((base_l[0] + tip[0]) / 2 - 34, (base_l[1] + tip[1]) / 2)
    mid_r = ((base_r[0] + tip[0]) / 2 + 34, (base_r[1] + tip[1]) / 2)
    draw.polygon([base_l, mid_l, tip, mid_r, base_r], fill=(74, 122, 62))
    draw.line([POT_X, POT_Y - 130, tip[0], tip[1]], fill=(52, 94, 44), width=5)
# Terracotta pot.
draw.polygon([(POT_X - 105, POT_Y - 130), (POT_X + 105, POT_Y - 130),
              (POT_X + 78, POT_Y + 30), (POT_X - 78, POT_Y + 30)], fill=(176, 92, 56))
draw.rectangle([POT_X - 118, POT_Y - 158, POT_X + 118, POT_Y - 118], fill=(196, 110, 70))
draw.line([(POT_X - 105, POT_Y - 128), (POT_X + 105, POT_Y - 128)],
          fill=(140, 66, 38), width=4)

# ---------------------------------------------------------------------------
# Sleeping tabby cat, curled at the letter's bottom-left corner
# ---------------------------------------------------------------------------

CAT = (225, 1845)   # body centre
# Tail curled around the body.
draw.arc([CAT[0] - 210, CAT[1] - 130, CAT[0] + 150, CAT[1] + 130], start=90, end=330,
         fill=(196, 122, 62), width=44)
# Body: a curled loaf.
draw.ellipse([CAT[0] - 190, CAT[1] - 105, CAT[0] + 190, CAT[1] + 105], fill=(216, 142, 74))
# Tabby stripes on the back.
for sx in (-120, -60, 0, 60, 120):
    draw.arc([CAT[0] - 190 + sx, CAT[1] - 105, CAT[0] - 60 + sx, CAT[1] + 40],
             start=250, end=330, fill=(150, 88, 40), width=12)
# Head resting on the paws, at the body's right end.
HX, HY = CAT[0] + 165, CAT[1] + 18
draw.polygon([(HX - 52, HY - 52), (HX - 22, HY - 108), (HX + 6, HY - 58)], fill=(216, 142, 74))
draw.polygon([(HX + 52, HY - 52), (HX + 22, HY - 108), (HX - 6, HY - 58)], fill=(216, 142, 74))
draw.polygon([(HX - 42, HY - 56), (HX - 24, HY - 92), (HX - 6, HY - 58)], fill=(232, 164, 150))
draw.polygon([(HX + 42, HY - 56), (HX + 24, HY - 92), (HX + 6, HY - 58)], fill=(232, 164, 150))
draw.ellipse([HX - 78, HY - 62, HX + 78, HY + 62], fill=(226, 152, 84))
# Closed eyes (sleeping curves), nose and mouth.
draw.arc([HX - 52, HY - 26, HX - 14, HY + 6], start=200, end=340, fill=(90, 52, 28), width=6)
draw.arc([HX + 14, HY - 26, HX + 52, HY + 6], start=200, end=340, fill=(90, 52, 28), width=6)
draw.polygon([(HX - 12, HY + 16), (HX + 12, HY + 16), (HX, HY + 30)], fill=(178, 90, 90))
# Front paws tucked under the chin.
draw.ellipse([HX - 78, HY + 34, HX - 18, HY + 66], fill=(226, 152, 84))
draw.ellipse([HX + 18, HY + 34, HX + 78, HY + 66], fill=(226, 152, 84))
# Sleepy "z"s drifting up.
zfont = font(FONT_SANS_BOLD, 64)
draw.text((70, 1560), "z", font=zfont, fill=(232, 214, 186))
draw.text((130, 1480), "z", font=font(FONT_SANS_BOLD, 52),
          fill=(232, 214, 186))
draw.text((185, 1410), "Z", font=font(FONT_SANS_BOLD, 42),
          fill=(232, 214, 186))

# ---------------------------------------------------------------------------
# Downscale and save
# ---------------------------------------------------------------------------

img = img.resize((OUT_W, OUT_H), Image.LANCZOS)
img.save(OUT_PATH, "PNG", optimize=True)
print("Wrote %s (%dx%d)" % (OUT_PATH, OUT_W, OUT_H))
