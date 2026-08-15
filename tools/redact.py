#!/usr/bin/env python3
"""
Redact personal data from RestroLogic product screenshots.

The screenshots are real captures from a live tenant, so before they go on a
public marketing page they carry a real operator's name and a real, scrapeable
email address. This replaces both with neutral demo identities while leaving
the business figures — which are what make the screens look credible — intact.

Approach: locate every occurrence with OCR rather than hard-coded coordinates,
so the script survives a re-capture at a different window size. For each hit,
sample the surrounding background, paint over the text, and redraw the
replacement at a font size fitted to the original box.

The avatar disc is found by colour (it is the only large amber circle in the
chrome) rather than by OCR, because two capital letters on a coloured disc are
unreliable for Tesseract.

Usage:
    python3 tools/redact.py <src-dir> <out-dir> [--verify]
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections import Counter

import pytesseract
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# What gets replaced
# ---------------------------------------------------------------------------

# Phrase-level rules. Matching whole phrases rather than single words matters:
# "Majo" and "Fonseca" sit in separate OCR boxes, and fitting each to its own
# box independently renders them at two different sizes.
# Phrase-level rules. Matching whole phrases rather than single words matters:
# "Majo" and "Fonseca" sit in separate OCR boxes, and fitting each to its own
# box independently renders them at two different sizes.
#
# Each rule carries a list of candidates, longest/nicest first. A replacement
# is never allowed to outgrow the box it replaces — the surrounding UI has no
# slack, so overflow means colliding with the next column. If the preferred
# text can only fit at a conspicuously smaller size, the next candidate is
# tried instead.
PHRASES: list[tuple[re.Pattern[str], list[str]]] = [
    (
        re.compile(r"majo\s*@\s*pomodoro\.com", re.I),
        ["demo@restrologic.com", "demo@rlogic.com", "demo@rl.com"],
    ),
    (re.compile(r"\bmajo\s+fonseca\b", re.I), ["Ana Restrepo", "Ana R.", "Ana"]),
    (re.compile(r"\bmajo\b", re.I), ["Ana"]),
    (re.compile(r"\bfonseca\b", re.I), ["Restrepo", "R."]),
]

# A replacement rendered below this fraction of the original cap height reads
# as visibly "shrunk to fit", so the next (shorter) candidate is preferred.
MIN_SIZE_RATIO = 0.82

AVATAR_INITIALS = "AR"

# Any of these surviving into the output is a failure.
#
# Note the domain is matched with its TLD: bare "pomodoro" is Italian for
# tomato and appears legitimately in the inventory screen as ingredient names
# ("salsa pomodoro", "masa pomodoro"), which are not identifying data.
FORBIDDEN = re.compile(r"\bmajo\b|\bfonseca\b|pomodoro\.co", re.I)

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf",
    "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",
    "/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def _first_existing(paths: list[str]) -> str:
    for p in paths:
        if pathlib.Path(p).exists():
            return p
    raise SystemExit("No usable font found on this system.")


FONT_PATH = _first_existing(FONT_CANDIDATES)
FONT_BOLD_PATH = _first_existing(FONT_BOLD_CANDIDATES)


# ---------------------------------------------------------------------------
# Colour sampling
# ---------------------------------------------------------------------------


def sample_background(im: Image.Image, box: tuple[int, int, int, int]) -> tuple[int, int, int]:
    """Most common colour on a ring just outside the text box."""
    x0, y0, x1, y1 = box
    w, h = im.size
    pad = 3
    ring: list[tuple[int, int, int]] = []

    for x in range(max(x0 - pad, 0), min(x1 + pad, w)):
        for y in (max(y0 - pad, 0), min(y1 + pad - 1, h - 1)):
            ring.append(im.getpixel((x, y)))
    for y in range(max(y0 - pad, 0), min(y1 + pad, h)):
        for x in (max(x0 - pad, 0), min(x1 + pad - 1, w - 1)):
            ring.append(im.getpixel((x, y)))

    if not ring:
        return (255, 255, 255)
    return Counter(ring).most_common(1)[0][0]


def sample_ink(
    im: Image.Image, box: tuple[int, int, int, int], bg: tuple[int, int, int]
) -> tuple[int, int, int]:
    """The pixel inside the box furthest from the background — i.e. the text."""
    x0, y0, x1, y1 = box
    best, best_d = None, -1
    for x in range(x0, x1):
        for y in range(y0, y1):
            px = im.getpixel((x, y))
            d = sum((px[i] - bg[i]) ** 2 for i in range(3))
            if d > best_d:
                best_d, best = d, px
    return best or (0, 0, 0)


# Reference string spanning ascender to descender. Sizing against a fixed
# reference — rather than against the replacement text — keeps every word on a
# line at the same size regardless of whether it happens to contain a 'p'.
_METRIC_REF = "Hxp"


def fit_font(
    text: str, target_w: int, target_h: int, bold: bool = False
) -> ImageFont.FreeTypeFont:
    """Largest font whose reference height fits target_h and text fits target_w."""
    path = FONT_BOLD_PATH if bold else FONT_PATH
    size = max(target_h + 4, 8)
    while size > 6:
        font = ImageFont.truetype(path, size)
        ref = font.getbbox(_METRIC_REF)
        txt = font.getbbox(text)
        if (ref[3] - ref[1]) <= target_h and (txt[2] - txt[0]) <= target_w:
            return font
        size -= 1
    return ImageFont.truetype(path, 8)


# ---------------------------------------------------------------------------
# Avatar
# ---------------------------------------------------------------------------


def find_avatar(im: Image.Image) -> tuple[int, int, int, int] | None:
    """
    Locate the amber initials disc in the top-right chrome.

    Matched by colour because OCR on two capitals over a coloured disc is
    unreliable. Restricted to the top strip so nothing in the page body can
    be mistaken for it.
    """
    w, _ = im.size
    strip = im.crop((int(w * 0.85), 0, w, 90))
    px = strip.load()
    sw, sh = strip.size

    xs, ys = [], []
    for x in range(sw):
        for y in range(sh):
            r, g, b = px[x, y][:3]
            # Amber disc: strongly warm, bright, and clearly not the dark chrome.
            if r > 210 and 140 < g < 215 and b < 165 and (r - b) > 70:
                xs.append(x)
                ys.append(y)

    if len(xs) < 200:
        return None

    ox = int(w * 0.85)
    return (min(xs) + ox, min(ys), max(xs) + ox, max(ys))


# ---------------------------------------------------------------------------
# Redaction
# ---------------------------------------------------------------------------


def redact(path: pathlib.Path) -> tuple[Image.Image, int]:
    im = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(im)
    data = pytesseract.image_to_data(
        im, lang="spa+eng", output_type=pytesseract.Output.DICT
    )

    changes = 0

    # Group OCR words into lines so a multi-word phrase is treated as one unit.
    lines: dict[tuple[int, int, int, int], list[int]] = {}
    for i, raw in enumerate(data["text"]):
        if not (raw or "").strip():
            continue
        key = (
            data["block_num"][i],
            data["par_num"][i],
            data["line_num"][i],
            data["page_num"][i],
        )
        lines.setdefault(key, []).append(i)

    for indices in lines.values():
        words = [(data["text"][i] or "").strip() for i in indices]
        line_text = " ".join(words)

        rule = next((r for r in PHRASES if r[0].search(line_text)), None)
        if rule is None:
            continue
        pattern, candidates = rule

        # Which words in this line are covered by the match?
        match = pattern.search(line_text)
        assert match is not None
        start, end = match.span()

        covered, cursor = [], 0
        for pos, word in enumerate(words):
            w_start, w_end = cursor, cursor + len(word)
            if w_start < end and w_end > start:
                covered.append(indices[pos])
            cursor = w_end + 1

        if not covered:
            continue

        x0 = min(data["left"][i] for i in covered)
        y0 = min(data["top"][i] for i in covered)
        x1 = max(data["left"][i] + data["width"][i] for i in covered)
        y1 = max(data["top"][i] + data["height"][i] for i in covered)
        if (x1 - x0) < 4 or (y1 - y0) < 4:
            continue

        box = (x0, y0, x1, y1)
        bg = sample_background(im, box)
        ink = sample_ink(im, box, bg)

        box_w, box_h = x1 - x0, y1 - y0

        # Fit strictly inside the original box. A tiny sliver of horizontal
        # slack is fine (glyph bearings), but nothing that would reach the
        # neighbouring column.
        best_text, best_font, best_size = None, None, -1
        for candidate in candidates:
            font = fit_font(candidate, box_w + 4, box_h)
            if font.size > best_size:
                best_text, best_font, best_size = candidate, font, font.size
            if font.size >= box_h * MIN_SIZE_RATIO:
                best_text, best_font = candidate, font
                break

        if best_text is None or best_font is None:
            continue

        draw.rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), fill=bg)

        bbox = best_font.getbbox(best_text)
        draw.text(
            (x0, y0 + (box_h - (bbox[3] - bbox[1])) / 2 - bbox[1]),
            best_text,
            font=best_font,
            fill=ink,
        )
        changes += 1

    # Avatar initials
    disc = find_avatar(im)
    if disc:
        dx0, dy0, dx1, dy1 = disc
        cx, cy = (dx0 + dx1) / 2, (dy0 + dy1) / 2
        radius = min(dx1 - dx0, dy1 - dy0) / 2
        disc_colour = im.getpixel((int(cx), int(dy0 + 3)))

        # Re-fill the disc, then draw the new initials in the original ink.
        inner = im.crop((int(cx - radius * 0.6), int(cy - radius * 0.5),
                         int(cx + radius * 0.6), int(cy + radius * 0.5)))
        ink = min(list(inner.getdata()), key=lambda p: sum(p))

        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                     fill=disc_colour)
        font = fit_font(AVATAR_INITIALS, int(radius * 1.4), int(radius * 1.0), bold=True)
        bbox = draw.textbbox((0, 0), AVATAR_INITIALS, font=font)
        draw.text((cx - (bbox[2] - bbox[0]) / 2 - bbox[0],
                   cy - (bbox[3] - bbox[1]) / 2 - bbox[1]),
                  AVATAR_INITIALS, font=font, fill=ink)
        changes += 1

    return im, changes


def verify(im: Image.Image) -> list[str]:
    """Re-OCR the output and report anything forbidden that survived."""
    text = pytesseract.image_to_string(im, lang="spa+eng")
    return sorted({m.group(0) for m in FORBIDDEN.finditer(text)})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    src = pathlib.Path(args.src)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    failures = 0
    for path in sorted(src.glob("*.png")):
        im, changes = redact(path)
        dest = out / path.name
        im.save(dest)

        note = ""
        if args.verify:
            leftover = verify(im)
            if leftover:
                note = f"  !! STILL PRESENT: {leftover}"
                failures += 1
            else:
                note = "  verified clean"
        print(f"{path.name[-10:-4]}  {changes:2d} redaction(s){note}")

    if failures:
        print(f"\n{failures} file(s) still contain personal data.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
