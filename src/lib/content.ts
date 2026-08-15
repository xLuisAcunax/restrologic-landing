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
  | 'amber'
  | 'cyan'
  | 'mint'
  | 'indigo'
  | 'rose'
  | 'violet'
  | 'teal';

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
    tone: 'amber',
    icon: 'utensils',
    titleKey: 'features.orders.title',
    textKey: 'features.orders.text',
    bulletKeys: ['features.orders.1', 'features.orders.2', 'features.orders.3'],
  },
  {
    id: 'kitchen',
    tone: 'rose',
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
    tone: 'mint',
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
    tone: 'cyan',
    icon: 'receipt',
    titleKey: 'features.cash.title',
    textKey: 'features.cash.text',
    bulletKeys: ['features.cash.1', 'features.cash.2', 'features.cash.3'],
  },
  {
    id: 'products',
    tone: 'violet',
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
    tone: 'indigo',
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
    tone: 'amber',
    titleKey: 'pipeline.1.title',
    textKey: 'pipeline.1.text',
    timeKey: 'pipeline.1.time',
  },
  {
    tone: 'rose',
    titleKey: 'pipeline.2.title',
    textKey: 'pipeline.2.text',
    timeKey: 'pipeline.2.time',
  },
  {
    tone: 'mint',
    titleKey: 'pipeline.3.title',
    textKey: 'pipeline.3.text',
    timeKey: 'pipeline.3.time',
  },
  {
    tone: 'cyan',
    titleKey: 'pipeline.4.title',
    textKey: 'pipeline.4.text',
    timeKey: 'pipeline.4.time',
  },
] as const;

/* -------------------------------------------------------------------------- */
/* Product modules (screenshot rows)                                           */
/* -------------------------------------------------------------------------- */

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
}

export const productModules: readonly ProductModule[] = [
  {
    id: 'admin',
    tone: 'indigo',
    icon: 'dashboard',
    titleKey: 'modules.admin.title',
    textKey: 'modules.admin.text',
    altKey: 'modules.admin.alt',
    pointKeys: ['modules.admin.1', 'modules.admin.2', 'modules.admin.3'],
    image: 'dashboard',
  },
  {
    id: 'pos',
    tone: 'amber',
    icon: 'utensils',
    titleKey: 'modules.pos.title',
    textKey: 'modules.pos.text',
    altKey: 'modules.pos.alt',
    pointKeys: ['modules.pos.1', 'modules.pos.2', 'modules.pos.3'],
    image: 'pos-mesas',
  },
  {
    id: 'inventory',
    tone: 'mint',
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
  },
  {
    id: 'reports',
    tone: 'violet',
    icon: 'chart',
    titleKey: 'modules.reports.title',
    textKey: 'modules.reports.text',
    altKey: 'modules.reports.alt',
    pointKeys: ['modules.reports.1', 'modules.reports.2', 'modules.reports.3'],
    image: 'reportes-ordenes',
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
    id: 'products',
    tone: 'violet',
    icon: 'sliders',
    titleKey: 'gallery.products.title',
    textKey: 'gallery.products.text',
    altKey: 'gallery.products.alt',
    image: 'productos',
  },
  {
    id: 'orders',
    tone: 'rose',
    icon: 'chefHat',
    titleKey: 'gallery.orders.title',
    textKey: 'gallery.orders.text',
    altKey: 'gallery.orders.alt',
    image: 'pos-ordenes',
  },
  {
    id: 'cash',
    tone: 'cyan',
    icon: 'receipt',
    titleKey: 'gallery.cash.title',
    textKey: 'gallery.cash.text',
    altKey: 'gallery.cash.alt',
    image: 'caja',
  },
  {
    id: 'cashreport',
    tone: 'teal',
    icon: 'fileText',
    titleKey: 'gallery.cashreport.title',
    textKey: 'gallery.cashreport.text',
    altKey: 'gallery.cashreport.alt',
    image: 'reportes-caja',
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
    tone: 'violet',
    icon: 'bike',
    titleKey: 'soon.delivery.title',
    textKey: 'soon.delivery.text',
  },
  {
    id: 'invoicing',
    tone: 'cyan',
    icon: 'fileText',
    titleKey: 'soon.invoicing.title',
    textKey: 'soon.invoicing.text',
  },
  {
    id: 'menu',
    tone: 'rose',
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
  { titleKey: 'how.1.title', textKey: 'how.1.text', tone: 'amber' },
  { titleKey: 'how.2.title', textKey: 'how.2.text', tone: 'violet' },
  { titleKey: 'how.3.title', textKey: 'how.3.text', tone: 'mint' },
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
  { numKey: 'stats.1.num', labelKey: 'stats.1.label', tone: 'amber' },
  { numKey: 'stats.2.num', labelKey: 'stats.2.label', tone: 'rose' },
  { numKey: 'stats.3.num', labelKey: 'stats.3.label', tone: 'violet' },
  { numKey: 'stats.4.num', labelKey: 'stats.4.label', tone: 'cyan' },
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
  { icon: 'utensils', labelKey: 'marquee.1', tone: 'amber' },
  { icon: 'chefHat', labelKey: 'marquee.2', tone: 'rose' },
  { icon: 'package', labelKey: 'marquee.3', tone: 'mint' },
  { icon: 'flame', labelKey: 'marquee.4', tone: 'violet' },
  { icon: 'receipt', labelKey: 'marquee.5', tone: 'cyan' },
  { icon: 'bike', labelKey: 'marquee.6', tone: 'indigo' },
  { icon: 'chart', labelKey: 'marquee.7', tone: 'teal' },
  { icon: 'shield', labelKey: 'marquee.8', tone: 'rose' },
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
