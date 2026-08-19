#!/usr/bin/env python3
"""
Build a standalone HTML preview of the RestroLogic landing page.

Why this exists: the design system lives in plain CSS files that the Astro
components consume by class name. This script reproduces the components'
markup and feeds it the *same* stylesheets and the *same* i18n strings, so the
result is a faithful, dependency-free rendering of the real page. It is used
to screenshot and review the design without an Astro build, and it doubles as
a shareable preview file.

Usage:  python3 tools/build_preview.py [--lang es|en] [--out preview.html]
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

# --------------------------------------------------------------------------- #
# Extract the real i18n dictionary and icon set from the TypeScript sources.
# --------------------------------------------------------------------------- #

KV = re.compile(
    r"'(?P<key>[a-zA-Z0-9._]+)':\s*(?P<val>'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")",
    re.S,
)


def _unquote(raw: str) -> str:
    body = raw[1:-1]
    return body.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n")


def load_dict(lang: str) -> dict[str, str]:
    """Pull one locale's key/value pairs out of src/i18n/ui.ts."""
    text = (SRC / "i18n" / "ui.ts").read_text(encoding="utf-8")

    if lang == "es":
        start = text.index("const es = {")
        end = text.index("} as const;", start)
    else:
        start = text.index("const en: Dictionary = {")
        end = text.index("\n};", start)

    block = text[start:end]
    return {m.group("key"): _unquote(m.group("val")) for m in KV.finditer(block)}


def load_icons() -> dict[str, str]:
    """Pull the icon path data out of icons.ts."""
    text = (SRC / "components" / "ui" / "icons.ts").read_text(encoding="utf-8")
    start = text.index("export const iconPaths = {")
    end = text.index("} as const;", start)
    block = text[start:end]

    icons: dict[str, str] = {}
    for m in re.finditer(
        r"(?P<name>[a-zA-Z]+):\s*\n?\s*'(?P<val>(?:[^'\\]|\\.)*)'", block
    ):
        icons[m.group("name")] = m.group("val").replace("\\'", "'")
    return icons


T: dict[str, str] = {}
ICONS: dict[str, str] = {}


def t(key: str) -> str:
    if key not in T:
        raise KeyError(f"Missing translation key: {key}")
    return T[key]


def icon(name: str, cls: str = "", style: str = "") -> str:
    if name not in ICONS:
        raise KeyError(f"Missing icon: {name} (have: {sorted(ICONS)})")
    attrs = ""
    if cls:
        attrs += f' class="{cls}"'
    if style:
        attrs += f' style="{style}"'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true" focusable="false"{attrs}>'
        f"{ICONS[name]}</svg>"
    )


# --------------------------------------------------------------------------- #
# Content model — mirrors src/lib/content.ts
# --------------------------------------------------------------------------- #

NAV = [
    ("#features", "nav.features"),
    ("#modules", "nav.modules"),
    ("#how", "nav.how"),
    ("#pricing", "nav.pricing"),
    ("#faq", "nav.faq"),
]

FEATURES = [
    ("utensils", "orders", "clay"),
    ("chefHat", "kitchen", "rust"),
    ("package", "inventory", "olive"),
    ("receipt", "cash", "indigo"),
    ("sliders", "products", "plum"),
    ("chart", "reports", "honey"),
]

PIPELINE_TONES = ["clay", "rust", "olive", "indigo"]
STAT_TONES = ["clay", "rust", "plum", "indigo"]
HOW_TONES = ["clay", "plum", "olive"]

MARQUEE = [
    ("utensils", "marquee.1", "clay"),
    ("chefHat", "marquee.2", "rust"),
    ("package", "marquee.3", "olive"),
    ("flame", "marquee.4", "plum"),
    ("receipt", "marquee.5", "indigo"),
    ("bike", "marquee.6", "honey"),
    ("chart", "marquee.7", "olive"),
    ("shield", "marquee.8", "rust"),
]

# icon, id, screen basename, tone, [(callout key suffix, x, y, anchor)]
MODULES = [
    ("utensils", "pos", "pos-mesas", "clay",
     [("call.1", 38, 58, None), ("call.2", 80, 77, "end")]),
    ("chefHat", "kitchen", "cocina", "honey",
     [("call.1", 61, 69, "end"), ("call.2", 87, 48, "end")]),
    ("banknote", "cash", "caja", "olive",
     [("call.1", 89, 23, "end"), ("call.2", 53, 65, None)]),
    ("package", "inventory", "inventario", "indigo",
     [("call.1", 60, 19, "end"), ("call.2", 42, 68, None)]),
    ("chart", "reports", "reportes-ordenes", "plum",
     [("call.1", 83, 34, "end"), ("call.2", 94, 60, "end")]),
]

GALLERY = [
    ("dashboard", "dashboard", "dashboard", "clay"),
    ("sliders", "products", "productos", "plum"),
    ("chefHat", "kds", "cocina-full", "honey"),
    ("fileText", "orderdetail", "orden-auditoria", "indigo"),
    ("package", "alerts", "inventario-alertas", "rust"),
    ("shield", "roles", "roles", "olive"),
    ("receipt", "taxes", "impuestos", "indigo"),
]

SOON = [
    ("bike", "delivery", "plum"),
    ("fileText", "invoicing", "indigo"),
    ("globe", "menu", "rust"),
]

PLANS = [
    ("starter", "$29", "$23", ["1", "2", "3", "4"], False),
    ("pro", "$59", "$47", ["1", "2", "3", "4", "5"], True),
    ("enterprise", None, None, ["1", "2", "3", "4"], False),
]

TABLES = [
    ("01", "busy"), ("02", ""), ("03", "ready"), ("04", "busy"),
    ("05", ""), ("06", "busy"), ("07", ""), ("08", "busy"),
    ("09", "ready"), ("10", ""), ("11", "busy"), ("12", "ready"),
]

TICKETS = [("04", "3", "4", "kitchen"), ("08", "2", "9", "ready"), ("02", "5", "17", "paid")]

RAIL = ["dashboard", "utensils", "chefHat", "package", "receipt", "chart"]


# --------------------------------------------------------------------------- #
# Markup builders
# --------------------------------------------------------------------------- #


def header() -> str:
    links = "".join(
        f'<li><a class="nav__link" href="{href}" data-nav-link aria-current="false">{t(key)}</a></li>'
        for href, key in NAV
    )
    return f"""
<header class="header" data-header data-stuck="false">
  <div class="container header__inner">
    <a class="brand" href="#top">{logo('header', 'brand__mark')}<span class="brand__name">Restro<em>Logic</em></span></a>
    <nav class="nav" aria-label="{t('nav.menu')}"><ul class="nav__list">{links}</ul></nav>
    <div class="header__actions">
      <div class="dropdown" data-dropdown data-open="false">
        <button type="button" class="iconbtn" data-dropdown-trigger aria-expanded="false" aria-haspopup="menu" title="{t('nav.language')}">
          <span class="sr-only">{t('nav.language')}</span>{icon('globe')}
        </button>
        <ul class="dropdown__panel" role="menu">
          <li role="none"><a role="menuitem" class="dropdown__item" href="/" aria-current="true">Español</a></li>
          <li role="none"><a role="menuitem" class="dropdown__item" href="/en/">English</a></li>
        </ul>
      </div>
      <button type="button" class="iconbtn theme-toggle" data-theme-toggle aria-pressed="false" title="{t('nav.theme')}">
        <span class="sr-only">{t('nav.theme')}</span>
        <span class="theme-toggle__icons" aria-hidden="true">{icon('sun', 'i-sun')}{icon('moon', 'i-moon')}</span>
      </button>
      <a class="btn btn--primary btn--sm header__cta" href="#contact">{t('nav.contact')}</a>
      <button type="button" class="iconbtn burger" data-drawer-toggle aria-expanded="false" aria-controls="site-drawer">
        <span class="sr-only">{t('nav.menu')}</span>
        <span class="burger__box" aria-hidden="true"><span class="burger__bar"></span><span class="burger__bar"></span><span class="burger__bar"></span></span>
      </button>
    </div>
  </div>
</header>
<div class="drawer" id="site-drawer" data-drawer data-open="false" aria-label="{t('nav.menu')}">
  <nav class="drawer__list">
    {"".join(f'<a class="drawer__link" href="{href}"><span>{i + 1:02d}</span>{t(key)}</a>' for i, (href, key) in enumerate(NAV))}
  </nav>
  <div class="drawer__foot">
    <a class="btn btn--primary" href="#contact">{t('nav.contact')}</a>
  </div>
</div>
<div class="scrollbar" data-scrollbar aria-hidden="true">
  <span class="scrollbar__fill" data-scroll-progress></span>
</div>"""


def logo(uid: str, cls: str) -> str:
    gid = f"rl-logo-{uid}"
    return f"""<svg class="{cls}" width="34" height="34" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
<defs><linearGradient id="{gid}" x1="4" y1="4" x2="28" y2="28" gradientUnits="userSpaceOnUse">
<stop stop-color="var(--rl-clay-300)"/><stop offset="0.55" stop-color="var(--rl-clay-500)"/><stop offset="1" stop-color="var(--rl-rust-500)"/>
</linearGradient></defs>
<rect x="2.5" y="24" width="27" height="3.2" rx="1.6" fill="url(#{gid})"/>
<path d="M5 24a11 11 0 0 1 22 0" stroke="url(#{gid})" stroke-width="2.4" stroke-linecap="round"/>
<circle cx="16" cy="10.4" r="1.9" fill="url(#{gid})"/>
<path d="M10.5 21.5l3.4-3.6 2.7 2.2 4.9-5.1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>
</svg>"""


def app_shell() -> str:
    """Python mirror of components/sections/AppShell.astro."""
    groups = [
        ("shell.group.service", [
            ("utensils", "shell.nav.pos", False, None),
            ("chefHat", "shell.nav.kitchen", False, "4"),
            ("banknote", "shell.nav.cash", True, None),
        ]),
        ("shell.group.manage", [
            ("sliders", "shell.nav.products", False, None),
            ("package", "shell.nav.inventory", False, None),
            ("fileText", "shell.nav.reports", False, None),
            ("chart", "shell.nav.dashboard", False, None),
        ]),
        ("shell.group.system", [
            ("settings", "shell.nav.settings", False, None),
        ]),
    ]

    nav = ""
    for label, items in groups:
        rows = ""
        for name, key, active, badge in items:
            rows += (
                '<span class="shell__navitem" data-shell-nav{}>{}'
                '<span class="shell__navtext">{}</span>{}</span>'
            ).format(
                ' data-active="true"' if active else "",
                icon(name),
                t(key),
                f'<span class="shell__navbadge">{badge}</span>' if badge else "",
            )
        nav += (
            f'<div class="shell__navgroup">'
            f'<span class="shell__navlabel">{t(label)}</span>{rows}</div>'
        )

    cards = [
        ("clay", "chart", "shell.kpi.sales", "$ ", 358000, "shell.kpi.sales.foot", False),
        ("olive", "trendingUp", "shell.kpi.moves", "+ $ ", 0, "shell.kpi.moves.foot", False),
        ("indigo", "receipt", "shell.kpi.control", "$ ", 35800, "shell.kpi.control.foot", False),
        ("honey", "banknote", "shell.kpi.expected", "$ ", 208900, "shell.kpi.expected.foot", True),
    ]

    kpis = ""
    for tone, ic, label, prefix, count, foot, featured in cards:
        pretty = f"{count:,}".replace(",", ".")
        feat_attr = ' data-featured="true"' if featured else ""
        kpis += (
            f'<div class="shell__kpi tone--{tone}" data-shell-kpi'
            f'{feat_attr}>'
            f'<div class="shell__kpi-head">'
            f'<span class="shell__kpi-label">{t(label)}</span>'
            f'<span class="shell__kpi-icon">{icon(ic)}</span></div>'
            f'<div class="shell__kpi-val"><span class="shell__kpi-prefix">{prefix}</span>'
            f'<span data-count="{count}" data-count-group="true">{pretty}</span></div>'
            f'<div class="shell__kpi-foot">{t(foot)}</div></div>'
        )

    moves = [
        ("2:10PM", "shell.move.1", "+ $ 94.600"),
        ("2:10PM", "shell.move.2", "+ $ 45.100"),
        ("2:10PM", "shell.move.3", "+ $ 51.700"),
        ("2:09PM", "shell.move.4", "+ $ 44.000"),
    ]
    rows = ""
    for index, (time_, key, amount) in enumerate(moves):
        fresh_attr = ' data-fresh="true"' if index == 0 else ""
        rows += (
            f'<div class="shell__row" data-shell-row'
            f'{fresh_attr}>'
            f'<span class="shell__row-time">{time_}</span>'
            f'<span class="shell__row-tag">{t("shell.moves.type")}</span>'
            f'<span class="shell__row-desc">{t(key)}</span>'
            f'<span class="shell__row-amount">{amount}</span></div>'
        )

    states = [
        ("pending", "indigo", "shell.ticket.pending"),
        ("cooking", "clay", "shell.ticket.cooking"),
        ("ready", "olive", "shell.ticket.ready"),
    ]
    chips = ""
    for index, (sid, tone, key) in enumerate(states):
        on_attr = ' data-on="true"' if index == 0 else ""
        chips += (
            f'<span class="floatcard__state tone--{tone}" data-ticket-state="{sid}"'
            f'{on_attr}>{t(key)}</span>'
        )

    return f"""
<div class="shell" data-shell aria-hidden="true">
  <div class="shell__chrome">
    <div class="shell__lights"><i></i><i></i><i></i></div>
    <div class="shell__url">{t('shell.url')}</div>
  </div>
  <div class="shell__body">
    <aside class="shell__side">
      <div class="shell__brand">
        <span class="shell__brand-mark"></span>
        <span class="shell__brand-word">Restro<span class="shell__brand-word-alt">Logic</span></span>
      </div>
      <div class="shell__nav">{nav}</div>
      <span class="shell__navitem shell__navitem--muted">{icon('logOut')}<span class="shell__navtext">{t('shell.logout')}</span></span>
    </aside>
    <div class="shell__main">
      <header class="shell__top">
        <span class="shell__pill shell__pill--branch"><span class="dot"></span>{t('shell.branch')}{icon('chevronDown', cls='shell__caret')}</span>
        <span class="shell__pill shell__pill--open">{icon('clock')}{t('shell.shift')}</span>
        <span class="shell__spacer"></span>
        <span class="shell__clock"><b data-shell-clock>14:10</b><em>{t('shell.date')}</em></span>
        <span class="shell__user">
          <span class="shell__user-text"><b>{t('shell.user.name')}</b><em>{t('shell.user.role')}</em></span>
          <span class="shell__avatar">AR</span>
        </span>
      </header>
      <div class="shell__content">
        <div class="shell__kpis">{kpis}</div>
        <div class="shell__panel">
          <div class="shell__panel-head">
            <span class="shell__panel-title">{t('shell.moves.title')}</span>
            <span class="shell__panel-meta">{t('shell.moves.meta')}</span>
          </div>
          <div class="shell__rows">{rows}</div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="floatcard floatcard--kds" data-float data-shell-ticket aria-hidden="true">
  <span class="floatcard__row"><span class="floatcard__table">{t('shell.ticket.table')}</span>{chips}</span>
  <span class="floatcard__body">
    <span class="floatcard__title">{t('shell.ticket.title')}</span>
    <span class="floatcard__meta"><span class="floatcard__bar"><i data-ticket-bar></i></span><span data-ticket-meta>{t('shell.ticket.meta')}</span></span>
  </span>
</div>

<div class="floatcard floatcard--stock is-floating is-floating--slow tone--rust" data-float aria-hidden="true">
  <span class="icon-tile" style="inline-size:2rem;block-size:2rem">{icon('package')}</span>
  <span class="floatcard__body"><span class="floatcard__title">{t('shell.card.stock.title')}</span><span class="floatcard__meta">{t('shell.card.stock.meta')}</span></span>
</div>

<div class="floatcard floatcard--cash is-floating is-floating--fast tone--olive" data-float aria-hidden="true">
  <span class="icon-tile" style="inline-size:2rem;block-size:2rem">{icon('check')}</span>
  <span class="floatcard__body"><span class="floatcard__title">{t('shell.card.cash.title')}</span><span class="floatcard__meta">{t('shell.card.cash.meta')}</span></span>
</div>
"""


def hero() -> str:
    proof = "".join(
        f'<div class="hero__proof-item"><span class="hero__proof-num">{t(f"hero.proof.{i}.num")}</span>'
        f'<span class="hero__proof-label">{t(f"hero.proof.{i}.label")}</span></div>'
        for i in (1, 2, 3)
    )
    return f"""
<section class="hero" data-hero id="top">
  <div class="hero__bg" aria-hidden="true">
    <div class="wash"></div>
    <div class="orb orb--clay hero__orb-1" data-parallax-orb="0.18"></div>
    <div class="orb orb--indigo hero__orb-2" data-parallax-orb="-0.26"></div>
    <div class="orb orb--plum hero__orb-3" data-parallax-orb="0.34"></div>
    <div class="dotgrid" data-parallax-orb="0.08"></div>
  </div>
  <div class="container hero__inner">
    <div class="hero__copy">
      <p class="chip chip--brand" data-hero-badge>{icon('sparkles', style='width:.9rem;height:.9rem')}{t('hero.badge')}</p>
      <h1 class="hero__title">
        <span class="hero__line" data-hero-line><span>{t('hero.title.1')}</span></span>
        <span class="hero__line" data-hero-line><span class="text-accent text-gradient">{t('hero.title.2')}</span></span>
      </h1>
      <p class="hero__lede" data-hero-lede>{t('hero.lede')}</p>
      <div class="cluster hero__actions" data-hero-actions>
        <a class="btn btn--primary btn--lg" href="#contact" data-magnetic>{t('hero.cta.primary')}{icon('arrowRight', 'btn__arrow')}</a>
        <a class="btn btn--outline btn--lg" href="#modules">{t('hero.cta.secondary')}</a>
      </div>
      <div class="hero__proof" data-hero-proof>{proof}</div>
    </div>
    <div class="hero__visual" data-hero-mock>{app_shell()}</div>
  </div>
</section>"""


def marquee() -> str:
    items = "".join(
        f'<span class="marquee__item tone--{tone}">{icon(ic)}{t(key)}</span>'
        for ic, key, tone in MARQUEE * 2
    )
    return f'<section class="marquee" aria-label="{t("marquee.label")}"><div class="marquee__track">{items}</div></section>'


def heading(eyebrow: str, title: str, lede: str, align_start: bool = False) -> str:
    cls = "section__head section__head--start" if align_start else "section__head"
    return f"""<div class="{cls}">
      <p class="eyebrow" data-reveal>{eyebrow}</p>
      <h2 class="section__title" data-reveal data-split>{title}</h2>
      <p class="section__lede" data-reveal>{lede}</p>
    </div>"""


def pipeline() -> str:
    steps = "".join(
        f'<article class="pipeline__step tone--{PIPELINE_TONES[i - 1]}" data-pipeline-step>'
        f'<span class="pipeline__num" aria-hidden="true">{i:02d}</span>'
        f'<h3 class="pipeline__title">{t(f"pipeline.{i}.title")}</h3>'
        f'<p class="pipeline__text">{t(f"pipeline.{i}.text")}</p>'
        f'<p class="pipeline__time">{t(f"pipeline.{i}.time")}</p></article>'
        for i in range(1, 5)
    )
    return f"""
<section class="section section--tinted" id="flow"><div class="container">
  {heading(t('pipeline.eyebrow'), t('pipeline.title'), t('pipeline.lede'))}
  <div class="pipeline" data-pipeline><div class="pipeline__track">
    <div class="pipeline__rail" data-pipeline-rail aria-hidden="true"></div>{steps}
  </div></div>
</div></section>"""


def features() -> str:
    cards = ""
    for ic, fid, tone in FEATURES:
        bullets = "".join(
            f'<li class="feature__li">{icon("check")}{t(f"features.{fid}.{n}")}</li>'
            for n in (1, 2, 3)
        )
        cards += f"""<article class="card card--interactive card--spotlight feature tone--{tone}">
          <div class="feature__head"><span class="icon-tile">{icon(ic)}</span>
          <h3 class="card__title">{t(f'features.{fid}.title')}</h3></div>
          <p class="card__text">{t(f'features.{fid}.text')}</p>
          <ul class="feature__list">{bullets}</ul></article>"""
    return f"""
<section class="section" id="features"><div class="container">
  {heading(t('features.eyebrow'), t('features.title'), t('features.lede'))}
  <div class="grid-auto features__grid" data-stagger>{cards}</div>
</div></section>"""


def modules() -> str:
    rows = ""
    for i, (ic, mid, img, tone, calls) in enumerate(MODULES):
        points = "".join(
            f'<li class="module__point">{icon("check")}{t(f"modules.{mid}.{n}")}</li>'
            for n in (1, 2, 3)
        )
        callouts = ""
        for suffix, x, y, anchor in calls:
            anchor_attr = f' data-anchor="{anchor}"' if anchor else ""
            callouts += (
                f'<span class="callout" data-callout{anchor_attr} '
                f'style="--x:{x}%;--y:{y}%" aria-hidden="true">'
                f'<span class="callout__dot"></span>'
                f'<span class="callout__label">{t(f"modules.{mid}.{suffix}")}</span></span>'
            )
        rev = " module--reverse" if i % 2 else ""
        rows += f"""<article class="module tone--{tone}{rev}">
          <div class="module__copy" data-reveal>
            <span class="chip chip--brand">{icon(ic, style='width:.9rem;height:.9rem')}{t('modules.tag')}</span>
            <h3 class="module__title">{t(f'modules.{mid}.title')}</h3>
            <p class="module__text">{t(f'modules.{mid}.text')}</p>
            <ul class="module__points">{points}</ul>
          </div>
          <div class="module__shot" data-parallax data-reveal>
            <div class="module__frame">
              <div class="module__chrome" aria-hidden="true"><span class="module__lights"><i></i><i></i><i></i></span></div>
              <div class="module__canvas">
                <img src="assets/screens/{img}.webp" alt="{t(f'modules.{mid}.alt')}" loading="lazy" decoding="async">
                {callouts}
              </div>
            </div>
          </div>
        </article>"""
    return f"""
<section class="section" id="modules"><div class="container">
  {heading(t('modules.eyebrow'), t('modules.title'), t('modules.lede'))}{rows}
</div></section>"""


def gallery() -> str:
    tabs, panels = "", ""
    for i, (ic, gid, img, tone) in enumerate(GALLERY):
        sel = "true" if i == 0 else "false"
        tabs += (
            f'<button type="button" role="tab" id="gtab-{gid}" class="gallery__tab tone--{tone}" '
            f'data-gallery-tab="{gid}" aria-selected="{sel}" aria-controls="gpanel-{gid}" '
            f'tabindex="{0 if i == 0 else -1}">{icon(ic)}<span>{t(f"gallery.{gid}.title")}</span></button>'
        )
        panels += (
            f'<div role="tabpanel" id="gpanel-{gid}" class="gallery__panel tone--{tone}" '
            f'data-gallery-panel="{gid}" aria-labelledby="gtab-{gid}" data-active="{sel}"'
            f'{"" if i == 0 else " hidden"}>'
            f'<figure class="gallery__figure">'
            f'<img src="assets/screens/{img}.webp" alt="{t(f"gallery.{gid}.alt")}" loading="lazy" decoding="async">'
            f'</figure>'
            f'<figcaption class="gallery__caption">'
            f'<h3 class="gallery__title">{t(f"gallery.{gid}.title")}</h3>'
            f'<p class="gallery__text">{t(f"gallery.{gid}.text")}</p>'
            f'</figcaption></div>'
        )
    return f"""
<section class="section section--tight gallery" id="gallery"><div class="container">
  {heading(t('gallery.eyebrow'), t('gallery.title'), t('gallery.lede'))}
  <div class="gallery__shell" data-gallery data-reveal>
    <div class="gallery__tabs" role="tablist" aria-label="{t('gallery.title')}">{tabs}</div>
    <div class="gallery__stage">{panels}</div>
  </div>
</div></section>"""


def coming_soon() -> str:
    items = "".join(
        f'<li class="soon__item tone--{tone}"><span class="icon-tile">{icon(ic)}</span>'
        f'<div><h3 class="soon__item-title">{t(f"soon.{sid}.title")}</h3>'
        f'<p class="soon__item-text">{t(f"soon.{sid}.text")}</p></div></li>'
        for ic, sid, tone in SOON
    )
    return f"""
<section class="section section--tight"><div class="container">
  <div class="soon" data-reveal>
    <div class="soon__head">
      <span class="chip chip--accent"><span class="dot dot--pulse"></span>{t('soon.badge')}</span>
      <h2 class="soon__title">{t('soon.title')}</h2>
      <p class="soon__lede">{t('soon.lede')}</p>
    </div>
    <ul class="soon__list" data-stagger>{items}</ul>
  </div>
</div></section>"""


def how() -> str:
    steps = "".join(
        f'<li class="step tone--{HOW_TONES[i - 1]}"><span class="step__marker" aria-hidden="true">{i}</span>'
        f'<div><h3 class="step__title">{t(f"how.{i}.title")}</h3>'
        f'<p class="step__text">{t(f"how.{i}.text")}</p></div></li>'
        for i in (1, 2, 3)
    )
    stats = "".join(
        f'<div class="stat tone--{STAT_TONES[i - 1]}"><div class="stat__num" data-count="{t(f"stats.{i}.num")}">{t(f"stats.{i}.num")}</div>'
        f'<div class="stat__label">{t(f"stats.{i}.label")}</div></div>'
        for i in (1, 2, 3, 4)
    )
    return f"""
<section class="section section--tinted" id="how"><div class="container">
  {heading(t('how.eyebrow'), t('how.title'), t('how.lede'))}
  <ol class="steps" data-stagger>{steps}</ol>
  <div class="stats" style="margin-top:clamp(3rem,2rem+4vw,4.5rem)" data-reveal>{stats}</div>
</div></section>"""


def pricing() -> str:
    cards = ""
    for pid, monthly, yearly, feats, featured in PLANS:
        price = monthly if monthly else t("pricing.enterprise.price")
        period = (
            f'<span class="plan__period" data-period-label data-monthly="{t("pricing.period.month")}" '
            f'data-yearly="{t("pricing.period.year")}">{t("pricing.period.month")}</span>'
            if monthly
            else ""
        )
        flag = f'<span class="plan__flag">{t("pricing.popular")}</span>' if featured else ""
        items = "".join(
            f'<li class="plan__feature">{icon("check")}{t(f"pricing.{pid}.{n}")}</li>' for n in feats
        )
        word_cls = "" if monthly else " plan__amount--word"
        cards += f"""<article class="plan {'plan--featured' if featured else ''}">{flag}
          <header><h3 class="plan__name">{t(f'pricing.{pid}.name')}</h3>
          <p class="plan__desc">{t(f'pricing.{pid}.desc')}</p></header>
          <div class="plan__price"><span class="plan__amount " data-price data-monthly="{price}" data-yearly="{yearly or price}">{price}</span>{period}</div>
          <ul class="plan__features">{items}</ul>
          <div class="plan__cta"><a class="btn btn--{'primary' if featured else 'outline'} btn--block" href="#contact">{t(f'pricing.{pid}.cta')}</a></div>
        </article>"""
    return f"""
<section class="section" id="pricing"><div class="container">
  {heading(t('pricing.eyebrow'), t('pricing.title'), t('pricing.lede'))}
  <div class="pricing__switch" data-reveal>
    <div class="segmented" role="tablist" data-billing>
      <span class="segmented__thumb" data-billing-thumb aria-hidden="true"></span>
      <button type="button" role="tab" class="segmented__option" data-billing-option="monthly" aria-selected="true">{t('pricing.monthly')}</button>
      <button type="button" role="tab" class="segmented__option" data-billing-option="yearly" aria-selected="false">{t('pricing.yearly')}</button>
    </div>
    <span class="chip chip--accent">{t('pricing.save')}</span>
  </div>
  <div class="pricing__grid" data-stagger>{cards}</div>
  <p class="pricing__note" data-reveal>{t('pricing.note')}</p>
</div></section>"""


def faq() -> str:
    items = "".join(
        f'<details class="qa"{" open" if i == 1 else ""}><summary class="qa__summary">{t(f"faq.{i}.q")}'
        f'<span class="qa__icon" aria-hidden="true">{icon("plus", style="width:.85rem;height:.85rem")}</span></summary>'
        f'<div class="qa__body"><p>{t(f"faq.{i}.a")}</p></div></details>'
        for i in range(1, 7)
    )
    return f"""
<section class="section section--tinted" id="faq"><div class="container"><div class="faq">
  <div class="faq__aside">
    {heading(t('faq.eyebrow'), t('faq.title'), t('faq.lede'), align_start=True)}
    <a class="btn btn--soft" href="#contact">{t('faq.contact')}{icon('arrowRight', 'btn__arrow')}</a>
  </div>
  <div class="accordion" data-accordion data-stagger>{items}</div>
</div></div></section>"""


def contact() -> str:
    perks = "".join(
        f'<li class="cta__perk">{icon("check")}{t(f"cta.perk.{i}")}</li>' for i in (1, 2, 3)
    )
    def field(fid: str, key: str, typ: str = "text") -> str:
        return f"""<div class="field"><label class="field__label" for="{fid}">{t(f'form.{key}')}</label>
          <input class="input" type="{typ}" id="{fid}" name="{fid}" placeholder="{t(f'form.{key}.placeholder')}"></div>"""

    return f"""
<section class="section cta" id="contact"><div class="container">
  <div class="cta__panel" data-reveal>
    <div class="cta__glow" aria-hidden="true"></div>
    <div class="cta__glow cta__glow--alt" aria-hidden="true"></div>
    <div class="cta__copy">
      <p class="eyebrow">{t('cta.eyebrow')}</p>
      <h2 class="cta__title" data-split>{t('cta.title')}</h2>
      <p class="cta__text">{t('cta.text')}</p>
      <ul class="cta__perks">{perks}</ul>
    </div>
    <form class="cta__form">
      <div class="cta__row">{field('name', 'name')}{field('restaurant', 'restaurant')}</div>
      <div class="cta__row">{field('email', 'email', 'email')}{field('phone', 'phone', 'tel')}</div>
      <div class="field"><label class="field__label" for="message">{t('form.message')}</label>
        <textarea class="textarea" id="message" placeholder="{t('form.message.placeholder')}"></textarea></div>
      <button type="submit" class="btn btn--primary btn--lg btn--block" data-magnetic>{t('form.submit')}{icon('arrowRight', 'btn__arrow')}</button>
      <p class="field__hint" style="text-align:center">{t('form.privacy')}</p>
    </form>
  </div>
</div></section>"""


def footer() -> str:
    product = "".join(f'<a class="footer__link" href="{h}">{t(k)}</a>' for h, k in NAV)
    return f"""
<footer class="footer"><div class="container">
  <div class="footer__grid">
    <div>
      <a class="brand" href="#top">{logo('footer', 'brand__mark')}<span class="brand__name">Restro<em>Logic</em></span></a>
      <p class="footer__tagline">{t('footer.tagline')}</p>
    </div>
    <nav><h2 class="footer__coltitle">{t('footer.col.product')}</h2><div class="footer__links">{product}</div></nav>
    <nav><h2 class="footer__coltitle">{t('footer.col.company')}</h2><div class="footer__links">
      <a class="footer__link" href="#contact">{t('nav.contact')}</a>
      <a class="footer__link" href="#">{t('footer.about')}</a></div></nav>
    <nav><h2 class="footer__coltitle">{t('footer.col.legal')}</h2><div class="footer__links">
      <a class="footer__link" href="#">{t('footer.privacy')}</a>
      <a class="footer__link" href="#">{t('footer.terms')}</a></div></nav>
  </div>
  <div class="footer__bottom">
    <p>RestroLogic 2026. {t('footer.built')} <a href="#" style="color:var(--brand-ink)">Luis Acuña</a>.</p>
    <ul class="social">
      <li><a class="social__link" href="#"><span class="sr-only">GitHub</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .5a12 12 0 0 0-3.8 23.4c.6.1.8-.2.8-.6v-2.1c-3.4.7-4.1-1.6-4.1-1.6-.5-1.3-1.1-1.7-1.1-1.7-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.6 2.4 1.1 3 .9.1-.7.3-1.1.6-1.4-2.7-.3-5.4-1.3-5.4-6 0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.6.1-3.3 0 0 1-.3 3.3 1.3a11.6 11.6 0 0 1 6.1 0c2.2-1.6 3.3-1.3 3.3-1.3.6 1.7.2 3 .1 3.3.8.8 1.2 1.8 1.2 3.1 0 4.6-2.7 5.6-5.4 5.9.4.4.7 1 .7 2.1v3.1c0 .4.2.8.8.6A12 12 0 0 0 12 .5z"/></svg></a></li>
      <li><a class="social__link" href="#"><span class="sr-only">LinkedIn</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.98 3.5A2.5 2.5 0 1 0 5 8.5a2.5 2.5 0 0 0-.02-5zM3 9h4v12H3zM9 9h3.8v1.7h.1c.5-.9 1.8-1.8 3.7-1.8 4 0 4.7 2.6 4.7 6V21h-4v-5.3c0-1.3 0-3-1.8-3s-2.1 1.4-2.1 2.9V21H9z"/></svg></a></li>
    </ul>
  </div>
</div></footer>"""


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #

STYLE_FILES = [
    "tokens.css",
    "base.css",
    "primitives.css",
    "components.css",
    "sections.css",
    "animations.css",
]


def build(lang: str, inline_css: bool) -> str:
    motion_js = (ROOT / "tools" / "preview_motion.js").read_text(encoding="utf-8")
    css = ""
    if inline_css:
        css = "<style>\n" + "\n".join(
            (SRC / "styles" / f).read_text(encoding="utf-8") for f in STYLE_FILES
        ) + "\n</style>"
    else:
        css = "".join(
            f'<link rel="stylesheet" href="../src/styles/{f}">' for f in STYLE_FILES
        )

    body = "".join(
        [header(), '<main id="main">', hero(), marquee(), pipeline(), features(),
         modules(), gallery(), coming_soon(), how(), pricing(), faq(),
         contact(), "</main>", footer()]
    )

    return f"""<!doctype html>
<html lang="{lang}" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t('meta.title')}</title>
<meta name="description" content="{t('meta.description')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caprasimo&family=Figtree:wght@400;500;600;700;800&display=swap">
{css}
</head>
<body>
<a class="skip-link" href="#main">{t('nav.skip')}</a>
{body}
<script>
{motion_js}
</script>
<script>
/* Preview-only interactivity. The real site uses src/scripts/*.ts + GSAP. */
(function () {{
  var root = document.documentElement;
  document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {{
    b.addEventListener('click', function () {{
      root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    }});
  }});
  document.querySelectorAll('[data-dropdown]').forEach(function (d) {{
    var trigger = d.querySelector('[data-dropdown-trigger]');
    trigger && trigger.addEventListener('click', function (e) {{
      e.stopPropagation();
      d.dataset.open = d.dataset.open === 'true' ? 'false' : 'true';
    }});
  }});
  var burger = document.querySelector('[data-drawer-toggle]');
  var drawer = document.querySelector('[data-drawer]');
  burger && burger.addEventListener('click', function () {{
    var open = drawer.dataset.open !== 'true';
    drawer.dataset.open = String(open);
    root.dataset.drawerOpen = String(open);
  }});
  var header = document.querySelector('[data-header]');
  window.addEventListener('scroll', function () {{
    header.dataset.stuck = String(window.scrollY > 8);
  }}, {{ passive: true }});
  var seg = document.querySelector('[data-billing]');
  if (seg) {{
    var opts = Array.prototype.slice.call(seg.querySelectorAll('[data-billing-option]'));
    var thumb = seg.querySelector('[data-billing-thumb]');
    function move(el) {{
      thumb.style.width = el.offsetWidth + 'px';
      thumb.style.transform = 'translateX(' + (el.offsetLeft - opts[0].offsetLeft) + 'px)';
    }}
    opts.forEach(function (o) {{
      o.addEventListener('click', function () {{
        var p = o.dataset.billingOption;
        opts.forEach(function (x) {{ x.setAttribute('aria-selected', String(x === o)); }});
        move(o);
        document.querySelectorAll('[data-price],[data-period-label]').forEach(function (n) {{
          if (n.dataset[p]) n.textContent = n.dataset[p];
        }});
      }});
    }});
    requestAnimationFrame(function () {{ move(opts[0]); }});
  }}
}})();
</script>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="es", choices=["es", "en"])
    parser.add_argument("--out", default="preview/restrologic-preview.html")
    parser.add_argument(
        "--link-css",
        action="store_true",
        help="Link the stylesheets instead of inlining them (dev only).",
    )
    parser.add_argument(
        "--inline-images",
        action="store_true",
        help="Embed the screenshots as data URIs, producing a single file that "
             "can be opened or sent anywhere with nothing beside it.",
    )
    args = parser.parse_args()

    global T, ICONS
    T = load_dict(args.lang)
    ICONS = load_icons()

    html = build(args.lang, inline_css=not args.link_css)


    # Self-check. This generator is a pile of string surgery, and a silently
    # mismatched anchor produces a page that looks *almost* right — which is
    # exactly the kind of bug that survives a visual review. Assert the
    # structural markers instead of trusting the replacements.
    required = {
        "tone classes on features": 'feature tone--',
        "tone classes on stats": 'stat tone--',
        "tone classes on steps": 'step tone--',
        "tone classes on pipeline": 'pipeline__step tone--',
        "tone classes on modules": 'module tone--',
        "tone classes on marquee": 'marquee__item tone--',
        "scroll progress bar": 'data-scroll-progress',
        "parallax orbs": 'data-parallax-orb',
        "motion engine": 'Preview-only motion engine',
        "dual CTA glow": 'cta__glow--alt',
        "screen gallery": 'data-gallery-tab',
        "coming soon strip": 'soon__list',
        "real dashboard screen": 'screens/dashboard.webp',
        "screenshot callouts": 'class="callout"',
        "framed captures": 'module__chrome',
    }
    missing = [name for name, marker in required.items() if marker not in html]
    if missing:
        print("BUILD CHECK FAILED — missing:", ", ".join(missing), file=sys.stderr)
        return 1

    # Every hue must actually appear, or a tone mapping has silently collapsed.
    hues = ["clay", "indigo", "olive", "honey", "rust", "plum", "olive"]
    absent = [h for h in hues if f"tone--{h}" not in html]
    if absent:
        print("BUILD CHECK FAILED — unused hues:", ", ".join(absent), file=sys.stderr)
        return 1

    # Inlining happens after the self-check: the check looks for literal
    # asset paths, and a data URI would read as a missing screenshot.

    if args.inline_images:
        import base64

        for shot in sorted((SRC / "assets" / "screens").glob("*.webp")):
            ref = f"assets/screens/{shot.name}"
            if ref not in html:
                continue
            data = base64.b64encode(shot.read_bytes()).decode("ascii")
            html = html.replace(ref, f"data:image/webp;base64,{data}")

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    print(f"wrote {out.relative_to(ROOT)}  ({len(html) / 1024:.0f} KB, "
          f"{len(T)} strings, {len(ICONS)} icons, {len(hues)} hues) — checks OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
