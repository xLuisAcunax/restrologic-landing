import {
  ui,
  defaultLang,
  languages,
  localeTags,
  type Lang,
  type TranslationKey,
} from './ui';

/** Narrow an unknown string to a supported locale. */
export function isLang(value: string | undefined): value is Lang {
  return typeof value === 'string' && value in languages;
}

/**
 * Resolve the active locale from the request URL.
 * The default locale is un-prefixed (`/`), others are prefixed (`/en/`).
 */
export function getLangFromUrl(url: URL): Lang {
  const [, segment] = url.pathname.split('/');
  return isLang(segment) ? segment : defaultLang;
}

/** Returns a `t(key)` lookup bound to a locale, falling back to the default. */
export function useTranslations(lang: Lang) {
  return function t(key: TranslationKey): string {
    return ui[lang][key] ?? ui[defaultLang][key];
  };
}

/**
 * Build a locale-aware href. Paths are always authored in their default-locale
 * form (`/#pricing`) and translated at render time (`/en/#pricing`).
 */
export function useTranslatedPath(lang: Lang) {
  return function translatePath(path: string, target: Lang = lang): string {
    const normalised = path.startsWith('/') ? path : `/${path}`;
    return target === defaultLang ? normalised : `/${target}${normalised}`;
  };
}

/** BCP-47 tag for `<html lang>`, `hreflang` and Intl APIs. */
export function getLocaleTag(lang: Lang): string {
  return localeTags[lang];
}

export { defaultLang, languages, type Lang, type TranslationKey };
