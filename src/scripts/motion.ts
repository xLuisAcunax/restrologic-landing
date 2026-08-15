/**
 * Motion foundation.
 *
 * Owns GSAP registration and the single source of truth for whether motion is
 * allowed. Every scene asks `motionEnabled()` before it animates, so honouring
 * `prefers-reduced-motion` is not left to the discipline of each scene.
 */

import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const reduceMotionQuery =
  typeof window !== 'undefined'
    ? window.matchMedia('(prefers-reduced-motion: reduce)')
    : null;

export function prefersReducedMotion(): boolean {
  return reduceMotionQuery?.matches ?? false;
}

export function motionEnabled(): boolean {
  return !prefersReducedMotion();
}

/** Shared easing vocabulary — mirrors the CSS custom properties. */
export const ease = {
  out: 'power3.out',
  outExpo: 'expo.out',
  inOut: 'power2.inOut',
  back: 'back.out(1.7)',
} as const;

export const duration = {
  fast: 0.35,
  base: 0.7,
  slow: 1.1,
} as const;

/**
 * Marks the document as motion-capable. CSS uses this to set the pre-animation
 * hidden state, which guarantees content stays visible when JS never runs.
 */
export function enableMotionStyling(): void {
  document.documentElement.dataset.motion = 'on';
}

/**
 * Split an element's text into per-word spans wrapped in an overflow mask.
 *
 * Bails out when the element contains child elements, so nested markup (links,
 * emphasis) is never destroyed. Returns the inner spans, ready to animate.
 */
export function splitWords(el: HTMLElement): HTMLElement[] {
  if (el.childElementCount > 0 || el.dataset.split === 'done') {
    return Array.from(el.querySelectorAll<HTMLElement>('.word__inner'));
  }

  const text = (el.textContent ?? '').trim();
  if (!text) return [];

  const words = text.split(/\s+/);
  const fragment = document.createDocumentFragment();
  const inners: HTMLElement[] = [];

  words.forEach((word, index) => {
    const outer = document.createElement('span');
    outer.className = 'word';

    const inner = document.createElement('span');
    inner.className = 'word__inner';
    inner.textContent = word;

    outer.appendChild(inner);
    fragment.appendChild(outer);
    inners.push(inner);

    if (index < words.length - 1) {
      fragment.appendChild(document.createTextNode(' '));
    }
  });

  el.textContent = '';
  el.appendChild(fragment);
  el.dataset.split = 'done';

  return inners;
}

/** Recalculate every ScrollTrigger once webfonts have settled. */
export function refreshOnFontsReady(): void {
  if (!('fonts' in document)) return;
  document.fonts.ready.then(() => ScrollTrigger.refresh()).catch(() => {
    /* Font loading is best-effort; a failure must never break the page. */
  });
}

export { gsap, ScrollTrigger };
