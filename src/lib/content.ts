/**
 * Structural content model.
 *
 * Sections describe *what* they render as data; the copy itself lives in the
 * i18n dictionary and is resolved at render time. Keeping the two apart means
 * adding a feature card or a plan is a data edit, never a markup edit, and a
 * new locale never has to touch a component.
 */

import type { IconName } from '../components/ui/icons';
import type { TranslationKey } from '../i18n/ui';

/* -------------------------------------------------------------------------- */
/* Navigation                                                                  */
/* -------------------------------------------------------------------------- */

export interface NavItem {
  /** Anchor in default-locale form; run through `translatePath` at render. */
  href: string;
  labelKey: TranslationKey;
}

export const navItems: readonly NavItem[] = [
  { href: '/#features', labelKey: 'nav.features' },
  { href: '/#modules', labelKey: 'nav.modules' },
  { href: '/#how', labelKey: 'nav.how' },
  { href: '/#pricing', labelKey: 'nav.pricing' },
  { href: '/#faq', labelKey: 'nav.faq' },
] as const;

/* -------------------------------------------------------------------------- */
/* Features                                                                    */
/* -------------------------------------------------------------------------- */

/** The accent hues available to sections. Maps to `.tone--*` in tokens.css. */
export type Tone =
  | 'clay'
  | 'honey'
  | 'olive'
  | 'indigo'
  | 'rust'
  | 'plum';

export interface Feature {
  id: string;
  icon: IconName;
  titleKey: TranslationKey;
  textKey: TranslationKey;
  bulletKeys: readonly TranslationKey[];
  /** Accent hue. Six features, six distinct hues — none repeat. */
  tone: Tone;
}

export const features: readonly Feature[] = [
  {
    id: 'orders',
    tone: 'clay',
    icon: 'utensils',
    titleKey: 'features.orders.title',
    textKey: 'features.orders.text',
    bulletKeys: ['features.orders.1', 'features.orders.2', 'features.orders.3'],
  },
  {
    id: 'kitchen',
    tone: 'rust',
    icon: 'chefHat',
    titleKey: 'features.kitchen.title',
    textKey: 'features.kitchen.text',
    bulletKeys: [
      'features.kitchen.1',
      'features.kitchen.2',
      'features.kitchen.3',
    ],
  },
  {
    id: 'inventory',
    tone: 'olive',
    icon: 'package',
    titleKey: 'features.inventory.title',
    textKey: 'features.inventory.text',
    bulletKeys: [
      'features.inventory.1',
      'features.inventory.2',
      'features.inventory.3',
    ],
  },
  {
    id: 'cash',
    tone: 'indigo',
    icon: 'receipt',
    titleKey: 'features.cash.title',
    textKey: 'features.cash.text',
    bulletKeys: ['features.cash.1', 'features.cash.2', 'features.cash.3'],
  },
  {
    id: 'products',
    tone: 'plum',
    icon: 'sliders',
    titleKey: 'features.products.title',
    textKey: 'features.products.text',
    bulletKeys: [
      'features.products.1',
      'features.products.2',
      'features.products.3',
    ],
  },
  {
    id: 'reports',
    tone: 'honey',
    icon: 'chart',
    titleKey: 'features.reports.title',
    textKey: 'features.reports.text',
    bulletKeys: [
      'features.reports.1',
      'features.reports.2',
      'features.reports.3',
    ],
  },
] as const;

/* -------------------------------------------------------------------------- */
/* Order pipeline                                                              */
/* -------------------------------------------------------------------------- */

export interface PipelineStep {
  titleKey: TranslationKey;
  textKey: TranslationKey;
  timeKey: TranslationKey;
  tone: Tone;
}

export const pipelineSteps: readonly PipelineStep[] = [
  {
    tone: 'clay',
    titleKey: 'pipeline.1.title',
    textKey: 'pipeline.1.text',
    timeKey: 'pipeline.1.time',
  },
  {
    tone: 'rust',
    titleKey: 'pipeline.2.title',
    textKey: 'pipeline.2.text',
    timeKey: 'pipeline.2.time',
  },
  {
    tone: 'olive',
    titleKey: 'pipeline.3.title',
    textKey: 'pipeline.3.text',
    timeKey: 'pipeline.3.time',
  },
  {
    tone: 'indigo',
    titleKey: 'pipeline.4.title',
    textKey: 'pipeline.4.text',
    timeKey: 'pipeline.4.time',
  },
] as const;

/* -------------------------------------------------------------------------- */
/* Product modules (screenshot rows)                                           */
/* -------------------------------------------------------------------------- */

/**
 * An annotation pinned over a screenshot. `x`/`y` are percentages of the
 * frame, so a callout keeps its position when the image is re-captured at a
 * different window size — and `anchor` decides which corner of the pill sits
 * on that point, which is what keeps it inside the frame near an edge.
 */
export interface Callout {
  labelKey: TranslationKey;
  x: number;
  y: number;
  anchor?: 'start' | 'end';
}

export interface ProductModule {
  id: string;
  tone: Tone;
  icon: IconName;
  titleKey: TranslationKey;
  textKey: TranslationKey;
  altKey: TranslationKey;
  pointKeys: readonly TranslationKey[];
  /** Basename in `src/assets/screens/` — resolved through Astro's image pipeline. */
  image: string;
  callouts?: readonly Callout[];
}

export const productModules: readonly ProductModule[] = [
  {
    id: 'pos',
    tone: 'clay',
    icon: 'utensils',
    titleKey: 'modules.pos.title',
    textKey: 'modules.pos.text',
    altKey: 'modules.pos.alt',
    pointKeys: ['modules.pos.1', 'modules.pos.2', 'modules.pos.3'],
    image: 'pos-mesas',
    callouts: [
      { labelKey: 'modules.pos.call.1', x: 38, y: 58 },
      { labelKey: 'modules.pos.call.2', x: 80, y: 77, anchor: 'end' },
    ],
  },
  {
    id: 'kitchen',
    tone: 'honey',
    icon: 'chefHat',
    titleKey: 'modules.kitchen.title',
    textKey: 'modules.kitchen.text',
    altKey: 'modules.kitchen.alt',
    pointKeys: ['modules.kitchen.1', 'modules.kitchen.2', 'modules.kitchen.3'],
    image: 'cocina',
    callouts: [
      { labelKey: 'modules.kitchen.call.1', x: 61, y: 69, anchor: 'end' },
      { labelKey: 'modules.kitchen.call.2', x: 87, y: 48, anchor: 'end' },
    ],
  },
  {
    id: 'cash',
    tone: 'olive',
    icon: 'banknote',
    titleKey: 'modules.cash.title',
    textKey: 'modules.cash.text',
    altKey: 'modules.cash.alt',
    pointKeys: ['modules.cash.1', 'modules.cash.2', 'modules.cash.3'],
    image: 'caja',
    callouts: [
      { labelKey: 'modules.cash.call.1', x: 89, y: 23, anchor: 'end' },
      { labelKey: 'modules.cash.call.2', x: 53, y: 65 },
    ],
  },
  {
    id: 'inventory',
    tone: 'indigo',
    icon: 'package',
    titleKey: 'modules.inventory.title',
    textKey: 'modules.inventory.text',
    altKey: 'modules.inventory.alt',
    pointKeys: [
      'modules.inventory.1',
      'modules.inventory.2',
      'modules.inventory.3',
    ],
    image: 'inventario',
    callouts: [
      { labelKey: 'modules.inventory.call.1', x: 60, y: 19, anchor: 'end' },
      { labelKey: 'modules.inventory.call.2', x: 42, y: 68 },
    ],
  },
  {
    id: 'reports',
    tone: 'plum',
    icon: 'chart',
    titleKey: 'modules.reports.title',
    textKey: 'modules.reports.text',
    altKey: 'modules.reports.alt',
    pointKeys: ['modules.reports.1', 'modules.reports.2', 'modules.reports.3'],
    image: 'reportes-ordenes',
    callouts: [
      { labelKey: 'modules.reports.call.1', x: 83, y: 34, anchor: 'end' },
      { labelKey: 'modules.reports.call.2', x: 94, y: 60, anchor: 'end' },
    ],
  },
] as const;

/* -------------------------------------------------------------------------- */
/* Screen gallery — the remaining real screens, in a tabbed viewer             */
/* -------------------------------------------------------------------------- */

export interface GalleryScreen {
  id: string;
  tone: Tone;
  icon: IconName;
  titleKey: TranslationKey;
  textKey: TranslationKey;
  altKey: TranslationKey;
  image: string;
}

export const galleryScreens: readonly GalleryScreen[] = [
  {
    id: 'dashboard',
    tone: 'clay',
    icon: 'dashboard',
    titleKey: 'gallery.dashboard.title',
    textKey: 'gallery.dashboard.text',
    altKey: 'gallery.dashboard.alt',
    image: 'dashboard',
  },
  {
    id: 'products',
    tone: 'plum',
    icon: 'sliders',
    titleKey: 'gallery.products.title',
    textKey: 'gallery.products.text',
    altKey: 'gallery.products.alt',
    image: 'productos',
  },
  {
    id: 'kds',
    tone: 'honey',
    icon: 'chefHat',
    titleKey: 'gallery.kds.title',
    textKey: 'gallery.kds.text',
    altKey: 'gallery.kds.alt',
    image: 'cocina-full',
  },
  {
    id: 'orderdetail',
    tone: 'indigo',
    icon: 'fileText',
    titleKey: 'gallery.orderdetail.title',
    textKey: 'gallery.orderdetail.text',
    altKey: 'gallery.orderdetail.alt',
    image: 'orden-auditoria',
  },
  {
    id: 'alerts',
    tone: 'rust',
    icon: 'package',
    titleKey: 'gallery.alerts.title',
    textKey: 'gallery.alerts.text',
    altKey: 'gallery.alerts.alt',
    image: 'inventario-alertas',
  },
  {
    id: 'roles',
    tone: 'olive',
    icon: 'shield',
    titleKey: 'gallery.roles.title',
    textKey: 'gallery.roles.text',
    altKey: 'gallery.roles.alt',
    image: 'roles',
  },
  {
    id: 'taxes',
    tone: 'indigo',
    icon: 'receipt',
    titleKey: 'gallery.taxes.title',
    textKey: 'gallery.taxes.text',
    altKey: 'gallery.taxes.alt',
    image: 'impuestos',
  },
] as const;

/* -------------------------------------------------------------------------- */
/* Roadmap — modules that do not exist yet                                     */
/* -------------------------------------------------------------------------- */

export interface SoonItem {
  id: string;
  tone: Tone;
  icon: IconName;
  titleKey: TranslationKey;
  textKey: TranslationKey;
}

/**
 * Deliberately separated from `features`: nothing on this list can be
 * demonstrated yet, so it must never appear alongside shipped capability.
 */
export const soonItems: readonly SoonItem[] = [
  {
    id: 'delivery',
    tone: 'plum',
    icon: 'bike',
    titleKey: 'soon.delivery.title',
    textKey: 'soon.delivery.text',
  },
  {
    id: 'invoicing',
    tone: 'indigo',
    icon: 'fileText',
    titleKey: 'soon.invoicing.title',
    textKey: 'soon.invoicing.text',
  },
  {
    id: 'menu',
    tone: 'rust',
    icon: 'globe',
    titleKey: 'soon.menu.title',
    textKey: 'soon.menu.text',
  },
] as const;

/* -------------------------------------------------------------------------- */
/* How it works                                                                */
/* -------------------------------------------------------------------------- */

export interface HowStep {
  titleKey: TranslationKey;
  textKey: TranslationKey;
  tone: Tone;
}

export const howSteps: readonly HowStep[] = [
  { titleKey: 'how.1.title', textKey: 'how.1.text', tone: 'clay' },
  { titleKey: 'how.2.title', textKey: 'how.2.text', tone: 'plum' },
  { titleKey: 'how.3.title', textKey: 'how.3.text', tone: 'olive' },
] as const;

/* -------------------------------------------------------------------------- */
/* Stats                                                                       */
/* -------------------------------------------------------------------------- */

export interface Stat {
  numKey: TranslationKey;
  labelKey: TranslationKey;
  tone: Tone;
}

export const stats: readonly Stat[] = [
  { numKey: 'stats.1.num', labelKey: 'stats.1.label', tone: 'clay' },
  { numKey: 'stats.2.num', labelKey: 'stats.2.label', tone: 'rust' },
  { numKey: 'stats.3.num', labelKey: 'stats.3.label', tone: 'plum' },
  { numKey: 'stats.4.num', labelKey: 'stats.4.label', tone: 'indigo' },
] as const;

/* -------------------------------------------------------------------------- */
/* Pricing                                                                     */
/* -------------------------------------------------------------------------- */

export interface Plan {
  id: string;
  nameKey: TranslationKey;
  descKey: TranslationKey;
  ctaKey: TranslationKey;
  featureKeys: readonly TranslationKey[];
  featured?: boolean;
  /** Numeric price in USD, or `null` for "contact us" tiers. */
  monthly: number | null;
  yearly: number | null;
  /** Used instead of a number when `monthly` is null. */
  customPriceKey?: TranslationKey;
  href: string;
}

export const plans: readonly Plan[] = [
  {
    id: 'starter',
    nameKey: 'pricing.starter.name',
    descKey: 'pricing.starter.desc',
    ctaKey: 'pricing.starter.cta',
    featureKeys: [
      'pricing.starter.1',
      'pricing.starter.2',
      'pricing.starter.3',
      'pricing.starter.4',
    ],
    monthly: 29,
    yearly: 23,
    href: '/#contact',
  },
  {
    id: 'pro',
    nameKey: 'pricing.pro.name',
    descKey: 'pricing.pro.desc',
    ctaKey: 'pricing.pro.cta',
    featureKeys: [
      'pricing.pro.1',
      'pricing.pro.2',
      'pricing.pro.3',
      'pricing.pro.4',
      'pricing.pro.5',
    ],
    featured: true,
    monthly: 59,
    yearly: 47,
    href: '/#contact',
  },
  {
    id: 'enterprise',
    nameKey: 'pricing.enterprise.name',
    descKey: 'pricing.enterprise.desc',
    ctaKey: 'pricing.enterprise.cta',
    featureKeys: [
      'pricing.enterprise.1',
      'pricing.enterprise.2',
      'pricing.enterprise.3',
      'pricing.enterprise.4',
    ],
    monthly: null,
    yearly: null,
    customPriceKey: 'pricing.enterprise.price',
    href: '/#contact',
  },
] as const;

/* -------------------------------------------------------------------------- */
/* FAQ                                                                         */
/* -------------------------------------------------------------------------- */

export interface FaqItem {
  qKey: TranslationKey;
  aKey: TranslationKey;
}

export const faqItems: readonly FaqItem[] = [
  { qKey: 'faq.1.q', aKey: 'faq.1.a' },
  { qKey: 'faq.2.q', aKey: 'faq.2.a' },
  { qKey: 'faq.3.q', aKey: 'faq.3.a' },
  { qKey: 'faq.4.q', aKey: 'faq.4.a' },
  { qKey: 'faq.5.q', aKey: 'faq.5.a' },
  { qKey: 'faq.6.q', aKey: 'faq.6.a' },
] as const;

/* -------------------------------------------------------------------------- */
/* Marquee                                                                     */
/* -------------------------------------------------------------------------- */

export const marqueeItems: readonly {
  icon: IconName;
  labelKey: TranslationKey;
  tone: Tone;
}[] = [
  { icon: 'utensils', labelKey: 'marquee.1', tone: 'clay' },
  { icon: 'chefHat', labelKey: 'marquee.2', tone: 'rust' },
  { icon: 'package', labelKey: 'marquee.3', tone: 'olive' },
  { icon: 'flame', labelKey: 'marquee.4', tone: 'plum' },
  { icon: 'receipt', labelKey: 'marquee.5', tone: 'indigo' },
  { icon: 'bike', labelKey: 'marquee.6', tone: 'honey' },
  { icon: 'chart', labelKey: 'marquee.7', tone: 'olive' },
  { icon: 'shield', labelKey: 'marquee.8', tone: 'rust' },
] as const;

/* -------------------------------------------------------------------------- */
/* Site constants                                                              */
/* -------------------------------------------------------------------------- */

export const site = {
  name: 'RestroLogic',
  domain: 'https://restrologic.com',
  author: {
    name: 'Luis Acuña',
    github: 'https://github.com/xLuisAcunax',
    linkedin: 'https://www.linkedin.com/in/ldacuna83/',
  },
  analyticsId: 'G-YSWQK9R0KK',
} as const;
