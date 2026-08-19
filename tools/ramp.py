#!/usr/bin/env python3
"""
Generate the RestroLogic hue ramps and check them against WCAG.

The palette is anchored on colours sampled directly from the product UI
(tools/sample_app.py output): the terracotta of the active nav item, the olive
of an "ACTIVO" chip, the denim of a "PENDIENTE" chip, the rust of a critical
stock badge, the cream canvas and the espresso chrome.

Rather than hand-picking ten steps per hue and hoping they are even, each ramp
is interpolated in OKLab — which keeps perceived lightness linear, so step 600
of one hue is as dark as step 600 of another and the tone system stays
balanced when a card swaps colours.

Every step that the design system actually pairs is then measured, so a ramp
that cannot carry its own label fails here rather than in an audit later.

Usage:  python3 tools/ramp.py [--css]
"""

from __future__ import annotations

import argparse
import math

# --------------------------------------------------------------------------- #
# Colour maths
# --------------------------------------------------------------------------- #


def hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(max(0.0, min(1.0, c)) * 255):02x}" for c in rgb)


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def rgb_to_oklab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = (_srgb_to_linear(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_rgb(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = (v**3 for v in (l_, m_, s_))
    return (
        _linear_to_srgb(+4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
        _linear_to_srgb(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
        _linear_to_srgb(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s),
    )


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = (_srgb_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = relative_luminance(hex_to_rgb(a)), relative_luminance(hex_to_rgb(b))
    lo, hi = sorted((la, lb))
    return (hi + 0.05) / (lo + 0.05)


# --------------------------------------------------------------------------- #
# Ramp construction
# --------------------------------------------------------------------------- #

# Target OKLab lightness per step. Chosen so 500-600 land where a saturated
# brand colour naturally sits, and 50-100 are pale enough to carry dark text.
STEPS = {
    50: 0.975,
    100: 0.945,
    200: 0.890,
    300: 0.810,
    400: 0.720,
    500: 0.640,
    600: 0.550,
    700: 0.455,
    800: 0.360,
    900: 0.265,
    950: 0.190,
}

# Each hue is anchored on a real colour lifted from the product UI. The anchor
# fixes the hue angle and the chroma envelope; the ramp then walks lightness.
#
#   clay    the active sidebar item and every primary button
#   honey   the logo gradient's warm end; the "cocinando" energy
#   olive   ACTIVO / DISPONIBLE / PAGADA chips
#   indigo  PENDIENTE / RESERVADAS chips and the "Preparar" action
#   rust    AGOTADO, stock crítico, "cerrar caja", destructive actions
#   plum    landing-only. A wine note that belongs in a warm restaurant
#           palette and gives the tone system a sixth hue without pretending
#           to be a colour the product ships.
#   sand    the neutral ramp: cream canvas through to espresso chrome
ANCHORS = {
    "clay": "#c67139",
    "honey": "#d9a017",
    "olive": "#76835a",
    "indigo": "#4a5da8",
    "rust": "#b32d1c",
    "plum": "#8d4a63",
    "sand": "#8c7c66",
}

# Chroma multiplier per step: colour peaks in the middle and fades at both
# ends, which is how a ramp stays believable rather than turning neon at 300
# and muddy at 900.
CHROMA = {
    50: 0.16,
    100: 0.30,
    200: 0.52,
    300: 0.74,
    400: 0.92,
    500: 1.00,
    600: 1.00,
    700: 0.92,
    800: 0.80,
    900: 0.66,
    950: 0.55,
}

# The neutral ramp is warm but must not read as a colour. Its chroma is capped
# hard, otherwise a full-bleed cream section looks tinted orange.
NEUTRAL_CHROMA_CAP = 0.78


def build_ramp(name: str, anchor: str) -> dict[int, str]:
    _, a, b = rgb_to_oklab(hex_to_rgb(anchor))
    base_chroma = math.hypot(a, b)
    hue = math.atan2(b, a)

    ramp: dict[int, str] = {}
    for step, lightness in STEPS.items():
        mult = CHROMA[step]
        if name == "sand":
            mult *= NEUTRAL_CHROMA_CAP
        c = base_chroma * mult
        rgb = oklab_to_rgb((lightness, math.cos(hue) * c, math.sin(hue) * c))
        ramp[step] = rgb_to_hex(rgb)
    return ramp


# --------------------------------------------------------------------------- #
# Verification
# --------------------------------------------------------------------------- #

AA_TEXT = 4.5
AA_GRAPHIC = 3.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--css", action="store_true", help="emit CSS custom properties")
    args = ap.parse_args()

    ramps = {name: build_ramp(name, anchor) for name, anchor in ANCHORS.items()}

    if args.css:
        for name, ramp in ramps.items():
            print(f"  /* {name} — anchored on {ANCHORS[name]} */")
            for step, value in ramp.items():
                print(f"  --rl-{name}-{step}: {value};")
            print()
        return 0

    # Canvas colours the ramps have to work against.
    light_bg = "#f9f4ed"
    light_surface = "#ffffff"
    dark_bg = "#17140f"
    dark_surface = "#211d17"

    failures: list[str] = []

    def check(label: str, fg: str, bg: str, floor: float, note: bool = False) -> None:
        """`note=True` records a measurement without gating on it — used for
        reference pairings we deliberately do not ship."""
        ratio = contrast(fg, bg)
        if note:
            mark = "-- "
        else:
            mark = "ok " if ratio >= floor else "FAIL"
            if ratio < floor:
                failures.append(f"{label}: {ratio:.2f} < {floor}")
        print(f"  {mark} {label:<34s} {fg} on {bg}  {ratio:5.2f}")

    print("LIGHT — ink on canvas / surface")
    for name, ramp in ramps.items():
        if name == "sand":
            continue
        check(f"{name}-700 on canvas", ramp[700], light_bg, AA_TEXT)
        check(f"{name}-700 on surface", ramp[700], light_surface, AA_TEXT)

    print("\nLIGHT — label on tinted chip (soft fill)")
    for name, ramp in ramps.items():
        if name == "sand":
            continue
        check(f"{name}-800 on {name}-50", ramp[800], ramp[50], AA_TEXT)

    print("\nLIGHT — filled surface carrying a white label")
    for name, ramp in ramps.items():
        if name == "sand":
            continue
        check(f"white on {name}-700", "#ffffff", ramp[700], AA_TEXT)

    print("\nLIGHT — graphic (borders, icon strokes)")
    for name, ramp in ramps.items():
        if name == "sand":
            continue
        check(f"{name}-500 on canvas", ramp[500], light_bg, AA_GRAPHIC)

    print("\nDARK — ink on canvas / surface")
    for name, ramp in ramps.items():
        if name == "sand":
            continue
        check(f"{name}-300 on dark bg", ramp[300], dark_bg, AA_TEXT)
        check(f"{name}-300 on dark surface", ramp[300], dark_surface, AA_TEXT)

    print("\nDARK — near-black label on a bright fill")
    for name, ramp in ramps.items():
        if name == "sand":
            continue
        check(f"{name}-950 on {name}-300", ramp[950], ramp[300], AA_TEXT)

    print("\nBrand button candidates — the app fills a pill with terracotta")
    clay = ramps["clay"]
    espresso = "#201e1d"
    # Reference only. This is the combination the product itself ships and it
    # is the reason the landing page does not simply copy the hex: white on
    # #c67139 misses AA. The landing deepens the fill to clay-600 instead,
    # which keeps the terracotta reading and clears the floor.
    check("app terracotta + white (ref)", "#ffffff", "#c67139", AA_TEXT, note=True)
    check("app terracotta + espresso ink", espresso, "#c67139", AA_TEXT)
    check("clay-500 + espresso ink", espresso, clay[500], AA_TEXT)
    check("clay-600 + white", "#ffffff", clay[600], AA_TEXT)

    print("\nHue separation — ramps must stay tellable apart at icon weight")
    # Contrast is the wrong metric here: every step sits at the same OKLab
    # lightness by construction, so any two would measure ~1.0. What matters
    # is angular distance around the hue circle.
    names = [n for n in ramps if n != "sand"]
    angles = {}
    for n in names:
        _, a, b = rgb_to_oklab(hex_to_rgb(ramps[n][500]))
        angles[n] = math.degrees(math.atan2(b, a)) % 360
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = abs(angles[a] - angles[b]) % 360
            d = min(d, 360 - d)
            flag = "ok " if d >= 18 else "!! "
            if d < 18:
                failures.append(f"{a}/{b} hue separation {d:.0f}deg < 18")
            print(f"  {flag}{a}-500 vs {b}-500  {d:5.1f}deg apart")

    print("\nNeutrals")
    sand = ramps["sand"]
    check("sand-950 (ink) on canvas", sand[950], light_bg, AA_TEXT)
    check("sand-700 (muted) on canvas", sand[700], light_bg, AA_TEXT)
    check("sand-700 (muted) on surface", sand[700], light_surface, AA_TEXT)
    check("sand-100 (text) on dark bg", sand[100], dark_bg, AA_TEXT)
    check("sand-300 (muted) on dark bg", sand[300], dark_bg, AA_TEXT)
    check("sand-300 (muted) on dark surf", sand[300], dark_surface, AA_TEXT)

    print()
    if failures:
        print(f"{len(failures)} pairing(s) below floor:")
        for f in failures:
            print("  -", f)
        return 1
    print("all pairings pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
