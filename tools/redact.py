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
#
# Order matters: the list is applied in sequence, so specific mailbox rules
# must precede the catch-all that rewrites any remaining @pomodoro.com
# address. The staff roster in the Configuración screen carries four distinct
# accounts, and each needs a stable replacement — rewriting them all to the
# same address would make the roster look broken.
PHRASES: list[tuple[re.Pattern[str], list[str]]] = [
    (
        re.compile(r"majo\s*@\s*pomodoro\.com", re.I),
        ["demo@restrologic.com", "demo@rlogic.com", "demo@rl.com"],
    ),
    (
        re.compile(r"emilia\s*@\s*pomodoro\.com", re.I),
        ["caja@restrologic.com", "caja@rlogic.com", "caja@rl.com"],
    ),
    (
        re.compile(r"arturo\s*@\s*pomodoro\.com", re.I),
        ["salon@restrologic.com", "salon@rlogic.com", "salon@rl.com"],
    ),
    (
        re.compile(r"coffee\s*@\s*pomodoro\.com", re.I),
        ["barra@restrologic.com", "barra@rlogic.com", "barra@rl.com"],
    ),
    (re.compile(r"\bmajo\s+fonseca\b", re.I), ["Ana Restrepo", "Ana R.", "Ana"]),
    (re.compile(r"\bcoffee\s+pachangas\b", re.I), ["Diego Martín", "Diego M.", "Diego"]),
    (re.compile(r"\bmajo\b", re.I), ["Ana"]),
    (re.compile(r"\bfonseca\b", re.I), ["Restrepo", "R."]),
    (re.compile(r"\bemilia\b", re.I), ["Camila", "Cami"]),
    (re.compile(r"\barturo\b", re.I), ["Julián", "Julio"]),
    (re.compile(r"\bpachangas\b", re.I), ["Martín", "M."]),
    # Catch-all. Any mailbox on the tenant domain that the specific rules above
    # did not claim — a re-capture with a new account, an OCR split that broke
    # the local part — still must not ship.
    (
        re.compile(r"[a-z0-9._+-]+\s*@\s*pomodoro\.com", re.I),
        ["staff@restrologic.com", "staff@rlogic.com", "staff@rl.com"],
    ),
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


def initials_for(name: str) -> str:
    """First letter of each word, capped at two — the app's own avatar rule."""
    parts = [p for p in re.split(r"\s+", name.strip()) if p and p[0].isalpha()]
    return "".join(p[0].upper() for p in parts[:2]) or "?"


def find_disc_beside(
    im: Image.Image, box: tuple[int, int, int, int], reach: int = 150
) -> tuple[int, int, int, int] | None:
    """
    Locate the initials disc that belongs to a name at `box`.

    Anchoring the search to the name rather than to a fixed corner is what
    makes this work across layouts: the roster puts the disc to the left of
    the name, the header chrome puts it to the right. Both sides are tried.
    Matched by colour rather than OCR because two capitals over a coloured
    disc are unreliable for Tesseract.
    """
    for side in ("left", "right"):
        found = _disc_on_side(im, box, reach, side)
        if found:
            return found
    return None


def _disc_on_side(
    im: Image.Image, box: tuple[int, int, int, int], reach: int, side: str
) -> tuple[int, int, int, int] | None:
    x0, y0, x1, y1 = box
    pad = max(10, (y1 - y0))
    if side == "left":
        sx0, sx1 = max(0, x0 - reach), max(0, x0 - 2)
    else:
        sx0, sx1 = min(im.size[0], x1 + 2), min(im.size[0], x1 + reach)
    sy0 = max(0, y0 - pad)
    sy1 = min(im.size[1], y1 + pad)
    if sx1 - sx0 < 12 or sy1 - sy0 < 12:
        return None

    strip = im.crop((sx0, sy0, sx1, sy1))
    px = strip.load()
    sw, sh = strip.size

    # The disc fill is the dominant colour in the strip that is not the card
    # background. Corners of the strip are background by construction.
    corners = [px[0, 0][:3], px[sw - 1, 0][:3], px[0, sh - 1][:3], px[sw - 1, sh - 1][:3]]
    bg = Counter(corners).most_common(1)[0][0]

    counts: Counter[tuple[int, int, int]] = Counter()
    for x in range(sw):
        for y in range(sh):
            c = px[x, y][:3]
            if sum(abs(a - b) for a, b in zip(c, bg)) > 24:
                counts[c] += 1

    if not counts:
        return None
    fill, n = counts.most_common(1)[0]
    if n < 200:
        return None

    xs, ys = [], []
    for x in range(sw):
        for y in range(sh):
            c = px[x, y][:3]
            if sum(abs(a - b) for a, b in zip(c, fill)) <= 18:
                xs.append(x)
                ys.append(y)

    if len(xs) < 200:
        return None

    bw, bh = max(xs) - min(xs), max(ys) - min(ys)
    if bw < 16 or bh < 16:
        return None
    # A disc is square-ish. Anything much wider than tall is a pill or a chip.
    if not (0.7 <= (bw / bh if bh else 0) <= 1.4):
        return None

    return (min(xs) + sx0, min(ys) + sy0, max(xs) + sx0, max(ys) + sy0)


def redraw_disc(
    im: Image.Image, draw: ImageDraw.ImageDraw, disc: tuple[int, int, int, int], text: str
) -> None:
    """Repaint an initials disc with `text`, keeping its fill and ink."""
    dx0, dy0, dx1, dy1 = disc
    cx, cy = (dx0 + dx1) / 2, (dy0 + dy1) / 2
    radius = min(dx1 - dx0, dy1 - dy0) / 2
    disc_colour = im.getpixel((int(cx), int(dy0 + 2)))

    inner = im.crop((int(cx - radius * 0.6), int(cy - radius * 0.5),
                     int(cx + radius * 0.6), int(cy + radius * 0.5)))
    pixels = list(inner.getdata())
    if not pixels:
        return
    ink = min(pixels, key=lambda p: sum(p))
    # If the disc has no darker ink on it, the initials are light on dark.
    if sum(abs(a - b) for a, b in zip(ink, disc_colour)) < 40:
        ink = max(pixels, key=lambda p: sum(p))

    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=disc_colour)
    font = fit_font(text, int(radius * 1.4), int(radius * 1.0), bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (bbox[2] - bbox[0]) / 2 - bbox[0],
               cy - (bbox[3] - bbox[1]) / 2 - bbox[1]),
              text, font=font, fill=ink)


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

        # A single OCR line can hold several independent hits — a roster row
        # carries a staff name *and* that person's mailbox, and the header
        # carries a name beside the account it belongs to. Keep re-matching
        # against the words that have not been claimed yet, so the second and
        # third occurrence on a line are redacted too rather than silently
        # shipping because the first one matched.
        claimed: set[int] = set()

        while True:
            active = [p for p in range(len(words)) if p not in claimed]
            if not active:
                break
            line_text = " ".join(words[p] for p in active)

            rule = next((r for r in PHRASES if r[0].search(line_text)), None)
            if rule is None:
                break
            pattern, candidates = rule

            match = pattern.search(line_text)
            assert match is not None
            start, end = match.span()

            # Which of the still-unclaimed words does the match span?
            covered_pos, cursor = [], 0
            for pos in active:
                w_start, w_end = cursor, cursor + len(words[pos])
                if w_start < end and w_end > start:
                    covered_pos.append(pos)
                cursor = w_end + 1

            if not covered_pos:
                break

            claimed.update(covered_pos)
            covered = [indices[p] for p in covered_pos]

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

            # A replaced *name* usually has an initials disc beside it, and
            # leaving "MF" next to "Ana Restrepo" both looks broken and leaks
            # the original initials. Addresses have no disc, so skip them.
            if "@" not in best_text:
                disc = find_disc_beside(im, box)
                if disc:
                    redraw_disc(im, draw, disc, initials_for(best_text))
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

    # WebP is included deliberately. A capture that arrives already converted
    # is still a raw capture: it has not been through this script, and skipping
    # it by extension is how an unredacted screen reaches the public site.
    sources = sorted(
        p for p in src.iterdir() if p.suffix.lower() in {".png", ".webp", ".jpg", ".jpeg"}
    )

    failures = 0
    for path in sources:
        im, changes = redact(path)
        dest = (out / path.name).with_suffix(".png")
        im.save(dest)

        note = ""
        if args.verify:
            leftover = verify(im)
            if leftover:
                note = f"  !! STILL PRESENT: {leftover}"
                failures += 1
            else:
                note = "  verified clean"
        print(f"{path.stem:28s} {changes:2d} redaction(s){note}")

    if failures:
        print(f"\n{failures} file(s) still contain personal data.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
