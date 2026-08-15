# RestroLogic — Landing Page

Marketing site for RestroLogic, the all-in-one restaurant management platform.
Built with **Astro 5**, a hand-rolled CSS design-token system, and **GSAP** for
scroll and timeline motion. Spanish is the default locale; English is served
under `/en/`.

The palette is taken from the product UI so the two read as one brand: indigo
ink, amber for the brand and active states, cyan for actions, and mint / rose /
violet / teal as functional accents on a cool blue-grey canvas.

---

## Getting started

```bash
npm install     # gsap is a new dependency — this step is required
npm run dev     # http://localhost:4321
npm run build   # static output in dist/
npm run preview # serve the built output
npm run check   # astro check (types + template diagnostics)
```

---

## Architecture

```
src/
├── assets/screens/      Product screenshots (WebP, run through Astro's image pipeline)
├── components/
│   ├── layout/          Header, Footer, Logo, ThemeScript, ThemeToggle, LanguagePicker
│   ├── sections/        One component per page section, top to bottom
│   └── ui/              Primitives: Button, Icon, SectionHeading
├── i18n/                ui.ts (dictionary) + utils.ts (locale resolution)
├── layouts/Layout.astro Document shell: SEO, schema.org, fonts, analytics
├── lib/content.ts       Structural content model — what renders, not what it says
├── pages/               index.astro (es) and [lang]/index.astro (en)
├── scripts/             Client TypeScript: motion foundation, scenes, UI controllers
└── styles/              The design system (see below)
tools/                   Preview builder, screenshot runner, audits (dev only)
```

### The three-layer separation

The point of the structure is that each kind of change has exactly one home:

| To change… | Edit | Never touch |
|---|---|---|
| Wording, in any language | `src/i18n/ui.ts` | components |
| Which cards/plans/steps exist | `src/lib/content.ts` | markup or copy |
| How something looks | `src/styles/*.css` | components |

Adding a seventh feature card is a two-line edit in `content.ts` plus its
strings in `ui.ts`. No component changes, and both locales stay in lockstep
because `TranslationKey` is derived from the Spanish dictionary and every other
locale is type-checked against it — a missing key is a build error, not a
silent runtime fallback.

### Styles

Plain CSS, layered by escalating specificity, imported in order by
`styles/global.css`:

| File | Responsibility |
|---|---|
| `tokens.css` | Primitive + semantic design tokens; both themes |
| `base.css` | Reset, document defaults, typography, a11y primitives |
| `primitives.css` | Layout building blocks: container, section, grid, decorative layers |
| `components.css` | Reusable UI: button, card, chip, field, header, footer |
| `sections.css` | Section-scoped styles, one root class each |
| `animations.css` | Keyframes and ambient looping motion |

**The token contract:** components consume *semantic* tokens (`--text`,
`--surface`, `--brand`) and never primitives (`--rl-amber-500`). Themes are
pure overrides of the semantic layer, which is why no component branches on
theme anywhere in the codebase.

### The tone system

Seven hue ramps (`--hue-amber-*`, `--hue-cyan-*`, …) drive the multi-colour
look. Each is a quintet: `base` / `ink` (text) / `soft` (fill) / `border` /
`on` (label colour) — plus `strong`, the contrast-safe fill for any toned
surface that carries a label.

The `.tone--*` classes re-point `--brand`, `--brand-ink`, `--brand-soft` and
friends at one ramp for a subtree. Because every component already reads those
semantic tokens, wrapping an element in `.tone--cyan` recolours its icon tile,
chip, border, hover glow and cursor spotlight **with no component CSS at all**:

```astro
<article class={`card card--interactive tone--${feature.tone}`}>
```

The hue for each card, step, stat and module lives in `lib/content.ts`, so
re-colouring a section is a one-word data edit.

**Two rules worth knowing:**

1. Any brand-coloured surface that carries text uses `--grad-brand-strong` /
   `--brand-strong` (or a tone's `--tone-strong`), never `--grad-brand`. The
   decorative gradient is lighter than the 4.5:1 floor allows for label text.
2. In light mode the primary button is **bright amber with near-black text**,
   mirroring the app's active nav item. White-on-amber forced the fill so dark
   it read as brown and still only scraped 4.7:1; the flip is both more vivid
   and measures 8.9:1.

Tailwind is still installed and available for one-off utility escape hatches,
but the design system itself is plain CSS so it stays portable and readable.

### Theming

`ThemeScript.astro` runs inline in `<head>` before first paint. It reads
`localStorage['rl-theme']`, falls back to `prefers-color-scheme`, and writes
`data-theme` on `<html>` — so a dark-mode visitor never sees a white flash.

### Motion

GSAP + ScrollTrigger, organised as independent **scenes** in
`scripts/scenes.ts`. Each scene finds its own targets and no-ops when they are
absent, so sections can be reordered or deleted without breaking motion.

Scroll-driven scenes:

| Scene | What it does |
|---|---|
| `scrollProgressScene` | Spectrum progress bar pinned to the top of the viewport |
| `heroScrollScene` | Mock straightens from its 3D angle and drifts as the hero exits; copy parallaxes and fades |
| `orbScene` | Three hero orbs drift at different rates |
| `pipelineScene` | Connector rail draws itself left-to-right, scrubbed to scroll |
| `moduleScene` | Screenshot parallax plus cursor tilt |
| `marqueeScene` | Strip speed follows scroll velocity and reverses with direction |
| `sectionEdgeScene` | Spectrum edges on the CTA panel and stats row draw in |
| `headingScene` / `revealScene` / `staggerScene` / `counterScene` | Word-mask heading reveals, staggered grids, count-ups |

Motion is strictly an enhancement:

- The same inline head script writes `data-motion="on"`, which is what arms
  the hidden pre-animation state in CSS.
- It also arms a 2.5s failsafe. If the motion bundle never reports readiness —
  chunk failed to load, parse error, offline — the attribute flips back to
  `off` and everything is revealed.
- `prefers-reduced-motion` disables GSAP entirely (`motionEnabled()`) and kills
  every CSS loop.

Net effect: no-JS, reduced-motion, and broken-bundle visitors all get a
complete, readable page.

---

## Development tools

`tools/` holds the harness used to build and verify the design without a full
Astro build. Not part of the site bundle.

```bash
python3 tools/check.py                  # static checks (see below)
python3 tools/build_preview.py --lang es # -> preview/restrologic-preview.html
./tools/shoot.sh mylabel                 # screenshots at 3 viewports
```

`tools/check.py` asserts, with no build step: i18n key parity between locales,
that every referenced translation key and icon exists, that no CSS variable or
class is used without being defined, that every relative import resolves, and
— most importantly — that **no shipped screenshot contains personal data**.

`tools/redact.py` produces the screenshots in `src/assets/screens/`. They are
real captures from a live tenant, so the operator's name, avatar initials and
email address are replaced with a neutral demo identity before publication.
Occurrences are located with OCR rather than hard-coded coordinates, so a
re-capture at a different window size still redacts correctly; each output is
re-OCR'd to confirm nothing survived.

```bash
python3 tools/redact.py <raw-screenshot-dir> <output-dir> --verify
```

Business figures are deliberately left intact — they are what make the screens
read as a real operation rather than a demo.

`tools/audit.js` is injected into the preview and measures document-level
horizontal overflow, WCAG contrast for **56 colour pairings per theme** (the
semantic set plus all seven hue ramps checked five ways each), and a11y
hygiene (alt text, accessible names, heading order, duplicate ids, tap-target
sizes).

`tools/preview_motion.js` reproduces the GSAP scenes in vanilla JS so the
scroll behaviour can be seen in the standalone preview, which has no GSAP
bundle. It is **not** shipped and is not a fallback — the real site uses GSAP.
Append `?static=1` to the preview URL to freeze it for screenshots.

---

## Accessibility

Verified at 390 / 820 / 1440px in both themes:

- **Contrast:** 112/112 pairings pass across both themes (AA 4.5:1 for text,
  3:1 for meaningful graphics). Tightest text margin is 4.68:1; tightest
  graphic margin is 3.05:1.
- **Overflow:** zero horizontal overflow at every tested viewport.
- **Targets:** all standalone interactive targets ≥24px (WCAG 2.2 SC 2.5.8).
  The one exception is the inline author credit in the footer, which falls
  under the inline-link exception.
- Single `h1`, no heading-level jumps, no duplicate ids, skip link, visible
  focus rings, `aria-current` scroll spy, Escape-to-close on drawer and
  dropdown.

---

## Deployment notes

Before going live:

1. **Contact form** — `components/sections/Contact.astro` posts to a Formspree
   placeholder. Replace the `action` with your real endpoint.
2. **Pricing** — plan prices live in `lib/content.ts` as USD numbers and are
   formatted per locale via `Intl.NumberFormat`. Change the `currency` in
   `Pricing.astro` to switch to COP.
3. **Footer legal links** point at `#faq` as placeholders until those pages
   exist.
