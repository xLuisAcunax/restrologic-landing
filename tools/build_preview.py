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
    """Pull the icon path data out of Icon.astro."""
    text = (SRC / "components" / "ui" / "Icon.astro").read_text(encoding="utf-8")
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
    ("utensils", "orders", "amber"),
    ("chefHat", "kitchen", "rose"),
    ("package", "inventory", "mint"),
    ("receipt", "cash", "cyan"),
    ("sliders", "products", "violet"),
    ("chart", "reports", "indigo"),
]

PIPELINE_TONES = ["amber", "rose", "mint", "cyan"]
STAT_TONES = ["amber", "rose", "violet", "cyan"]
HOW_TONES = ["amber", "violet", "mint"]

MARQUEE = [
    ("utensils", "marquee.1", "amber"),
    ("chefHat", "marquee.2", "rose"),
    ("package", "marquee.3", "mint"),
    ("flame", "marquee.4", "violet"),
    ("receipt", "marquee.5", "cyan"),
    ("bike", "marquee.6", "indigo"),
    ("chart", "marquee.7", "teal"),
    ("shield", "marquee.8", "rose"),
]

MODULES = [
    ("dashboard", "admin", "dashboard", "indigo"),
    ("utensils", "pos", "pos-mesas", "amber"),
    ("package", "inventory", "inventario", "mint"),
    ("chart", "reports", "reportes-ordenes", "violet"),
]

GALLERY = [
    ("sliders", "products", "productos", "violet"),
    ("chefHat", "orders", "pos-ordenes", "rose"),
    ("receipt", "cash", "caja", "cyan"),
    ("fileText", "cashreport", "reportes-caja", "teal"),
]

SOON = [
    ("bike", "delivery", "violet"),
    ("fileText", "invoicing", "cyan"),
    ("globe", "menu", "rose"),
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
<stop stop-color="var(--rl-amber-300)"/><stop offset="0.55" stop-color="var(--rl-amber-500)"/><stop offset="1" stop-color="var(--rl-rose-500)"/>
</linearGradient></defs>
<rect x="2.5" y="24" width="27" height="3.2" rx="1.6" fill="url(#{gid})"/>
<path d="M5 24a11 11 0 0 1 22 0" stroke="url(#{gid})" stroke-width="2.4" stroke-linecap="round"/>
<circle cx="16" cy="10.4" r="1.9" fill="url(#{gid})"/>
<path d="M10.5 21.5l3.4-3.6 2.7 2.2 4.9-5.1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>
</svg>"""


def app_mock() -> str:
    active_attr = ' data-active="true"'
    rail = "".join(
        '<span class="mock__railitem"{}>{}</span>'.format(
            active_attr if i == 0 else "", icon(n)
        )
        for i, n in enumerate(RAIL)
    )
    floor = "".join(
        '<span class="mock__table" data-mock-table{}>{}</span>'.format(
            ' data-state="{}"'.format(state) if state else "", tid
        )
        for tid, state in TABLES
    )
    tickets = "".join(
        f'<div class="mock__ticket"><span class="mock__ticket-name">Mesa {tb}</span>'
        f'<span class="mock__ticket-meta">{it} · {mn} min</span>'
        f'<span class="mock__ticket-state" data-s="{st}">{t("mock.state." + st)}</span></div>'
        for tb, it, mn, st in TICKETS
    )
    spark = "M0 45 L20 38 L40 42 L60 28 L80 32 L100 20 L120 26 L140 14 L160 18 L180 8 L200 12"
    return f"""
<div class="mock" aria-hidden="true">
  <div class="mock__bar">
    <div class="mock__lights"><i></i><i></i><i></i></div>
    <div class="mock__url">{t('mock.url')}</div>
  </div>
  <div class="mock__body">
    <nav class="mock__rail">{rail}</nav>
    <div class="mock__main">
      <div class="mock__head">
        <div><div class="mock__h">{t('mock.title')}</div><div class="mock__sub">{t('mock.subtitle')}</div></div>
        <span class="chip chip--accent"><span class="dot dot--pulse"></span>Live</span>
      </div>
      <div class="mock__kpis">
        <div class="mock__kpi"><div class="mock__kpi-label">{t('mock.kpi.1')}</div><div class="mock__kpi-val">$4.82M</div><div class="mock__kpi-trend">+12.4%</div></div>
        <div class="mock__kpi"><div class="mock__kpi-label">{t('mock.kpi.2')}</div><div class="mock__kpi-val">148</div><div class="mock__kpi-trend">+8.1%</div></div>
        <div class="mock__kpi"><div class="mock__kpi-label">{t('mock.kpi.3')}</div><div class="mock__kpi-val">$32.5K</div><div class="mock__kpi-trend">+3.9%</div></div>
      </div>
      <div class="mock__chart">
        <svg viewBox="0 0 200 60" preserveAspectRatio="none">
          <defs><linearGradient id="rl-spark-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="var(--brand)" stop-opacity="0.32"/>
            <stop offset="100%" stop-color="var(--brand)" stop-opacity="0"/>
          </linearGradient></defs>
          <path class="mock__spark-fill" d="{spark} L200 60 L0 60 Z"/>
          <path class="mock__spark-line" data-mock-spark d="{spark}"/>
        </svg>
      </div>
      <div><div class="mock__kpi-label" style="margin-bottom:.35rem">{t('mock.floor')}</div><div class="mock__floor">{floor}</div></div>
      <div><div class="mock__kpi-label" style="margin-bottom:.35rem">{t('mock.tickets')}</div><div class="mock__tickets">{tickets}</div></div>
    </div>
  </div>
</div>
<div class="floatcard floatcard--kds is-floating" data-float aria-hidden="true">
  <span class="icon-tile icon-tile--accent" style="inline-size:2rem;block-size:2rem">{icon('chefHat')}</span>
  <span class="floatcard__body"><span class="floatcard__title">{t('mock.card.kds.title')}</span><span class="floatcard__meta">{t('mock.card.kds.meta')}</span></span>
</div>
<div class="floatcard floatcard--stock is-floating is-floating--slow" data-float aria-hidden="true">
  <span class="icon-tile" style="inline-size:2rem;block-size:2rem">{icon('package')}</span>
  <span class="floatcard__body"><span class="floatcard__title">{t('mock.card.stock.title')}</span><span class="floatcard__meta">{t('mock.card.stock.meta')}</span></span>
</div>
<div class="floatcard floatcard--cash is-floating is-floating--fast" data-float aria-hidden="true">
  <span class="icon-tile icon-tile--accent" style="inline-size:2rem;block-size:2rem">{icon('receipt')}</span>
  <span class="floatcard__body"><span class="floatcard__title">{t('mock.card.cash.title')}</span><span class="floatcard__meta">{t('mock.card.cash.meta')}</span></span>
</div>"""


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
    <div class="orb orb--amber hero__orb-1" data-parallax-orb="0.18"></div>
    <div class="orb orb--cyan hero__orb-2" data-parallax-orb="-0.26"></div>
    <div class="orb orb--violet hero__orb-3" data-parallax-orb="0.34"></div>
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
    <div class="hero__visual" data-hero-mock>{app_mock()}</div>
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
    for i, (ic, mid, img, tone) in enumerate(MODULES):
        points = "".join(
            f'<li class="module__point">{icon("check")}{t(f"modules.{mid}.{n}")}</li>'
            for n in (1, 2, 3)
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
              <img src="assets/screens/{img}.webp" alt="{t(f'modules.{mid}.alt')}" loading="lazy" decoding="async">
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
    <p>© 2026 RestroLogic. {t('footer.rights')} {t('footer.built')} <a href="#" style="color:var(--brand-ink)">Luis Acuña</a>.</p>
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@300..800&family=Fraunces:ital,opsz,wght@1,9..144,400..600&display=swap">
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
    }
    missing = [name for name, marker in required.items() if marker not in html]
    if missing:
        print("BUILD CHECK FAILED — missing:", ", ".join(missing), file=sys.stderr)
        return 1

    # Every hue must actually appear, or a tone mapping has silently collapsed.
    hues = ["amber", "cyan", "mint", "indigo", "rose", "violet", "teal"]
    absent = [h for h in hues if f"tone--{h}" not in html]
    if absent:
        print("BUILD CHECK FAILED — unused hues:", ", ".join(absent), file=sys.stderr)
        return 1

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    print(f"wrote {out.relative_to(ROOT)}  ({len(html) / 1024:.0f} KB, "
          f"{len(T)} strings, {len(ICONS)} icons, {len(hues)} hues) — checks OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
