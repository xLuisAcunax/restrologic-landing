#!/usr/bin/env python3
"""
Screenshot the standalone preview at review viewports, in both themes.

Replaces the old shoot.sh: it drives Chromium directly so the theme can be
forced, the motion failsafe can be tripped deliberately, and full-page and
above-the-fold captures come out of the same run.

Usage:
    python3 tools/shoot.py [label] [--full] [--viewport 1440] [--theme light]
    python3 tools/shoot.py --audit          # run tools/audit.js and print JSON
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PREVIEW = ROOT / "preview" / "restrologic-preview.html"
OUT = ROOT / "preview" / "shots"

VIEWPORTS = {390: 844, 820: 1180, 1440: 900}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("label", nargs="?", default="shot")
    ap.add_argument("--full", action="store_true", help="full-page capture")
    ap.add_argument("--viewport", type=int, action="append")
    ap.add_argument("--theme", action="append", choices=["light", "dark"])
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--scroll", type=float, default=0.0,
                    help="scroll to this fraction of the page before capturing")
    args = ap.parse_args()

    if not PREVIEW.exists():
        print("No preview built. Run tools/build_preview.py first.", file=sys.stderr)
        return 1

    widths = args.viewport or [1440]
    themes = args.theme or ["light"]
    OUT.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--force-color-profile=srgb"])
        for width in widths:
            height = VIEWPORTS.get(width, 900)
            for theme in themes:
                page = browser.new_page(
                    viewport={"width": width, "height": height},
                    device_scale_factor=2 if width <= 820 else 1,
                )
                # ?static=1 freezes the preview's motion engine and reveals
                # every pre-animation state, which is what a screenshot needs.
                page.goto(PREVIEW.as_uri() + "?static=1")
                page.evaluate(
                    "t => document.documentElement.setAttribute('data-theme', t)", theme
                )
                # The preview's motion engine hides pre-animation state. Settle
                # it so a capture is not a page of invisible sections.
                page.wait_for_timeout(1200)
                page.evaluate("() => window.scrollTo(0, 0)")
                if args.scroll:
                    page.evaluate(
                        "f => window.scrollTo(0, document.body.scrollHeight * f)",
                        args.scroll,
                    )
                    page.wait_for_timeout(900)

                if args.full:
                    # A full-page capture never scrolls, so lazy images stay
                    # unfetched and land in the shot as empty boxes. Flipping
                    # the attribute after the fact does not start a fetch in
                    # Chromium — walking the page does. The walk is bounded:
                    # scrollHeight grows as images arrive, and an unbounded
                    # loop chasing it does not terminate.
                    page.evaluate(
                        """async () => {
                          const step = window.innerHeight * 0.8;
                          const total = document.body.scrollHeight;
                          const steps = Math.min(80, Math.ceil(total / step));
                          for (let i = 0; i <= steps; i += 1) {
                            window.scrollTo(0, i * step);
                            await new Promise(r => setTimeout(r, 70));
                          }
                          window.scrollTo(0, 0);
                          const pending = [...document.images].filter(i => !i.complete);
                          await Promise.race([
                            Promise.all(pending.map(i => new Promise(res => {
                              i.addEventListener('load', res, { once: true });
                              i.addEventListener('error', res, { once: true });
                            }))),
                            new Promise(r => setTimeout(r, 4000)),
                          ]);
                        }"""
                    )
                    page.wait_for_timeout(700)

                if args.audit:
                    # audit.js writes its report into the document rather than
                    # returning it, so read it back out of the page.
                    page.evaluate(
                        (ROOT / "tools" / "audit.js").read_text(encoding="utf-8")
                    )
                    raw = page.text_content("#audit") or "{}"
                    print(f"--- {width}px {theme}")
                    print(raw)
                    page.close()
                    continue

                name = f"{args.label}-{width}-{theme}.png"
                page.screenshot(path=str(OUT / name), full_page=args.full)
                print(f"  {name}")
                page.close()
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
