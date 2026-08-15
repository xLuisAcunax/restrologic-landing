/**
 * Animation scenes.
 *
 * Each export is an independent, idempotent scene that finds its own targets
 * and does nothing when they are absent. Scenes never assume page structure
 * beyond the data attributes they query, so sections can be reordered or
 * removed without breaking motion.
 */

import {
  gsap,
  ScrollTrigger,
  ease,
  duration,
  motionEnabled,
  splitWords,
} from './motion';

/* -------------------------------------------------------------------------- */
/* Hero — the one sequenced, non-scroll timeline on the page                   */
/* -------------------------------------------------------------------------- */

export function heroScene(): void {
  const hero = document.querySelector<HTMLElement>('[data-hero]');
  if (!hero) return;

  const lines = hero.querySelectorAll<HTMLElement>('[data-hero-line] > span');
  const badge = hero.querySelector('[data-hero-badge]');
  const lede = hero.querySelector('[data-hero-lede]');
  const actions = hero.querySelector('[data-hero-actions]');
  const proofItems = hero.querySelectorAll('[data-hero-proof] > *');
  const mock = hero.querySelector('[data-hero-mock]');
  const floats = hero.querySelectorAll<HTMLElement>('[data-float]');

  const tl = gsap.timeline({
    defaults: { ease: ease.outExpo, duration: duration.base },
  });

  if (badge) {
    tl.from(badge, { opacity: 0, y: 14, duration: duration.fast });
  }

  tl.from(
    lines,
    { yPercent: 118, duration: 0.95, stagger: 0.09 },
    badge ? '-=0.15' : 0,
  );

  if (lede) tl.from(lede, { opacity: 0, y: 22 }, '-=0.6');
  if (actions) tl.from(actions, { opacity: 0, y: 20 }, '-=0.5');

  if (proofItems.length) {
    tl.from(proofItems, { opacity: 0, y: 18, stagger: 0.08 }, '-=0.45');
  }

  if (mock) {
    tl.from(
      mock,
      { opacity: 0, y: 46, scale: 0.96, duration: 1.15 },
      '-=1.05',
    );
  }

  if (floats.length) {
    tl.from(
      floats,
      { opacity: 0, scale: 0.86, y: 16, stagger: 0.12, ease: ease.back },
      '-=0.65',
    );

    // Hand each card off to its own endless drift once it has landed.
    floats.forEach((card, index) => {
      gsap.to(card, {
        y: index % 2 === 0 ? -10 : -14,
        duration: 3 + index * 0.6,
        ease: 'sine.inOut',
        repeat: -1,
        yoyo: true,
        delay: 1.4 + index * 0.2,
      });
    });
  }
}

/* -------------------------------------------------------------------------- */
/* Generic scroll reveal                                                       */
/* -------------------------------------------------------------------------- */

export function revealScene(): void {
  const targets = gsap.utils.toArray<HTMLElement>('[data-reveal]');

  targets.forEach((el) => {
    // Elements inside the hero are owned by the hero timeline.
    if (el.closest('[data-hero]')) {
      gsap.set(el, { clearProps: 'opacity' });
      return;
    }

    const delay = Number(el.dataset.revealDelay ?? 0);

    gsap.fromTo(
      el,
      { opacity: 0, y: 26 },
      {
        opacity: 1,
        y: 0,
        duration: duration.base,
        ease: ease.out,
        delay,
        scrollTrigger: {
          trigger: el,
          start: 'top 88%',
          once: true,
        },
      },
    );
  });
}

/** Staggered reveal for grids — children animate in sequence, not together. */
export function staggerScene(): void {
  const groups = gsap.utils.toArray<HTMLElement>('[data-stagger]');

  groups.forEach((group) => {
    const children = Array.from(group.children) as HTMLElement[];
    if (!children.length) return;

    gsap.fromTo(
      children,
      { opacity: 0, y: 30 },
      {
        opacity: 1,
        y: 0,
        duration: duration.base,
        ease: ease.out,
        stagger: 0.08,
        scrollTrigger: { trigger: group, start: 'top 85%', once: true },
      },
    );
  });
}

/* -------------------------------------------------------------------------- */
/* Headings — per-word mask reveal                                             */
/* -------------------------------------------------------------------------- */

export function headingScene(): void {
  const headings = gsap.utils.toArray<HTMLElement>('[data-split]');

  headings.forEach((heading) => {
    if (heading.closest('[data-hero]')) return;

    const words = splitWords(heading);
    if (!words.length) return;

    // The element itself is revealed by this scene, not by revealScene.
    gsap.set(heading, { opacity: 1 });

    gsap.fromTo(
      words,
      { yPercent: 112 },
      {
        yPercent: 0,
        duration: 0.85,
        ease: ease.outExpo,
        stagger: 0.045,
        scrollTrigger: { trigger: heading, start: 'top 86%', once: true },
      },
    );
  });
}

/* -------------------------------------------------------------------------- */
/* Count-up statistics                                                         */
/* -------------------------------------------------------------------------- */

export function counterScene(): void {
  const counters = gsap.utils.toArray<HTMLElement>('[data-count]');

  counters.forEach((el) => {
    const raw = el.dataset.count ?? el.textContent ?? '';
    const target = Number.parseFloat(raw.replace(/[^\d.-]/g, ''));
    if (!Number.isFinite(target)) return;

    const prefix = el.dataset.countPrefix ?? '';
    const suffix = el.dataset.countSuffix ?? '';
    const decimals = Number(el.dataset.countDecimals ?? 0);
    const counter = { value: 0 };

    gsap.to(counter, {
      value: target,
      duration: 1.6,
      ease: 'power2.out',
      scrollTrigger: { trigger: el, start: 'top 90%', once: true },
      onUpdate() {
        el.textContent = `${prefix}${counter.value.toFixed(decimals)}${suffix}`;
      },
    });
  });
}

/* -------------------------------------------------------------------------- */
/* Order pipeline — rail draws as the section scrolls past                     */
/* -------------------------------------------------------------------------- */

export function pipelineScene(): void {
  const pipeline = document.querySelector<HTMLElement>('[data-pipeline]');
  if (!pipeline) return;

  const rail = pipeline.querySelector<HTMLElement>('[data-pipeline-rail]');
  const steps = pipeline.querySelectorAll<HTMLElement>('[data-pipeline-step]');

  if (rail) {
    gsap.fromTo(
      rail,
      { '--rail-progress': 0 },
      {
        '--rail-progress': 1,
        ease: 'none',
        scrollTrigger: {
          trigger: pipeline,
          start: 'top 70%',
          end: 'bottom 75%',
          scrub: 0.6,
        },
      },
    );
  }

  if (steps.length) {
    gsap.fromTo(
      steps,
      { opacity: 0, y: 34 },
      {
        opacity: 1,
        y: 0,
        duration: duration.base,
        ease: ease.out,
        stagger: 0.14,
        scrollTrigger: { trigger: pipeline, start: 'top 78%', once: true },
      },
    );
  }
}

/* -------------------------------------------------------------------------- */
/* Module screenshots — parallax drift + cursor tilt                           */
/* -------------------------------------------------------------------------- */

export function moduleScene(): void {
  const shots = gsap.utils.toArray<HTMLElement>('[data-parallax]');

  shots.forEach((shot) => {
    const frame = shot.querySelector<HTMLElement>('.module__frame');
    if (!frame) return;

    gsap.fromTo(
      frame,
      { yPercent: 5 },
      {
        yPercent: -5,
        ease: 'none',
        scrollTrigger: {
          trigger: shot,
          start: 'top bottom',
          end: 'bottom top',
          scrub: 1,
        },
      },
    );

    // Pointer tilt. Skipped on coarse pointers, where it can never fire.
    if (!window.matchMedia('(pointer: fine)').matches) return;

    const quickX = gsap.quickTo(frame, 'rotationY', {
      duration: 0.5,
      ease: 'power3',
    });
    const quickY = gsap.quickTo(frame, 'rotationX', {
      duration: 0.5,
      ease: 'power3',
    });

    shot.addEventListener('pointermove', (event) => {
      const rect = shot.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      quickX(x * 9);
      quickY(-y * 7);
    });

    shot.addEventListener('pointerleave', () => {
      quickX(0);
      quickY(0);
    });
  });
}

/* -------------------------------------------------------------------------- */
/* Magnetic buttons                                                            */
/* -------------------------------------------------------------------------- */

export function magneticScene(): void {
  if (!window.matchMedia('(pointer: fine)').matches) return;

  const magnets = gsap.utils.toArray<HTMLElement>('[data-magnetic]');

  magnets.forEach((magnet) => {
    const moveX = gsap.quickTo(magnet, 'x', { duration: 0.4, ease: 'power3' });
    const moveY = gsap.quickTo(magnet, 'y', { duration: 0.4, ease: 'power3' });

    magnet.addEventListener('pointermove', (event) => {
      const rect = magnet.getBoundingClientRect();
      const x = event.clientX - rect.left - rect.width / 2;
      const y = event.clientY - rect.top - rect.height / 2;
      moveX(x * 0.28);
      moveY(y * 0.4);
    });

    magnet.addEventListener('pointerleave', () => {
      moveX(0);
      moveY(0);
    });
  });
}

/* -------------------------------------------------------------------------- */
/* Card spotlight — writes cursor position into CSS custom properties          */
/* -------------------------------------------------------------------------- */

export function spotlightScene(): void {
  if (!window.matchMedia('(pointer: fine)').matches) return;

  document
    .querySelectorAll<HTMLElement>('.card--spotlight')
    .forEach((card) => {
      card.addEventListener('pointermove', (event) => {
        const rect = card.getBoundingClientRect();
        card.style.setProperty('--mx', `${event.clientX - rect.left}px`);
        card.style.setProperty('--my', `${event.clientY - rect.top}px`);
      });
    });
}

/* -------------------------------------------------------------------------- */
/* Live ticket rotation inside the hero mock                                   */
/* -------------------------------------------------------------------------- */

export function mockScene(): void {
  const tables = gsap.utils.toArray<HTMLElement>('[data-mock-table]');
  if (!tables.length) return;

  // Occasionally flip a free table to "busy" and back, so the floor map feels
  // like a live service rather than a static screenshot.
  const cycle = gsap.timeline({ repeat: -1, repeatDelay: 2.2, delay: 2 });

  tables.slice(0, 4).forEach((table, index) => {
    cycle
      .call(
        () => {
          table.dataset.state = index % 2 === 0 ? 'busy' : 'ready';
        },
        undefined,
        index * 1.1,
      )
      .call(
        () => {
          table.dataset.state = '';
        },
        undefined,
        index * 1.1 + 2.4,
      );
  });

  // Draw the sparkline by animating its own dash offset — no paid plugin
  // needed, and it degrades to a fully drawn line if the scene never runs.
  const spark = document.querySelector<SVGPathElement>('[data-mock-spark]');
  if (spark && typeof spark.getTotalLength === 'function') {
    const length = spark.getTotalLength();

    gsap.fromTo(
      spark,
      { strokeDasharray: length, strokeDashoffset: length },
      {
        strokeDashoffset: 0,
        duration: 1.6,
        ease: ease.out,
        delay: 0.8,
        onComplete() {
          // Clear the dash so the line stays crisp at any zoom level.
          spark.style.strokeDasharray = '';
          spark.style.strokeDashoffset = '';
        },
      },
    );
  }
}

/* -------------------------------------------------------------------------- */
/* Scroll progress — spectrum bar pinned to the top of the viewport            */
/* -------------------------------------------------------------------------- */

export function scrollProgressScene(): void {
  const bar = document.querySelector<HTMLElement>('[data-scrollbar]');
  const fill = document.querySelector<HTMLElement>('[data-scroll-progress]');
  if (!bar || !fill) return;

  gsap.fromTo(
    fill,
    { '--scroll-progress': 0 },
    {
      '--scroll-progress': 1,
      ease: 'none',
      scrollTrigger: {
        trigger: document.documentElement,
        start: 'top top',
        end: 'bottom bottom',
        scrub: 0.25,
        onUpdate(self) {
          // Keep the bar hidden at the very top so it never competes with
          // the hero on first paint.
          bar.dataset.visible = String(self.progress > 0.005);
        },
      },
    },
  );
}

/* -------------------------------------------------------------------------- */
/* Hero mock — scrubbed as the hero scrolls away                              */
/* -------------------------------------------------------------------------- */

export function heroScrollScene(): void {
  const hero = document.querySelector<HTMLElement>('[data-hero]');
  if (!hero) return;

  const mock = hero.querySelector<HTMLElement>('[data-hero-mock]');
  const copy = hero.querySelector<HTMLElement>('.hero__copy');

  // The mock straightens up and settles back as you scroll past the fold.
  if (mock && window.matchMedia('(min-width: 68rem)').matches) {
    gsap.fromTo(
      mock,
      { rotationY: -9, rotationX: 4, y: 0 },
      {
        rotationY: 0,
        rotationX: 0,
        y: -40,
        ease: 'none',
        scrollTrigger: {
          trigger: hero,
          start: 'top top',
          end: 'bottom top',
          scrub: 0.8,
        },
      },
    );
  }

  // Copy drifts up slightly faster than the page, and fades as it leaves.
  if (copy) {
    gsap.to(copy, {
      y: -60,
      opacity: 0.25,
      ease: 'none',
      scrollTrigger: {
        trigger: hero,
        start: 'center center',
        end: 'bottom top',
        scrub: 0.6,
      },
    });
  }
}

/* -------------------------------------------------------------------------- */
/* Decorative orbs — each drifts at its own rate                              */
/* -------------------------------------------------------------------------- */

export function orbScene(): void {
  const orbs = gsap.utils.toArray<HTMLElement>('[data-parallax-orb]');

  orbs.forEach((orb) => {
    const rate = Number(orb.dataset.parallaxOrb ?? 0.2);
    const section = orb.closest('section') ?? orb.parentElement;
    if (!section) return;

    gsap.to(orb, {
      yPercent: rate * 100,
      ease: 'none',
      scrollTrigger: {
        trigger: section,
        start: 'top bottom',
        end: 'bottom top',
        scrub: 1.2,
      },
    });
  });
}

/* -------------------------------------------------------------------------- */
/* Marquee — scroll direction and velocity steer the strip                    */
/* -------------------------------------------------------------------------- */

export function marqueeScene(): void {
  const track = document.querySelector<HTMLElement>('.marquee__track');
  if (!track) return;

  // Hand the loop over from CSS so GSAP can modulate its rate.
  track.style.animation = 'none';

  const half = track.scrollWidth / 2;
  if (!half) return;

  const loop = gsap.to(track, {
    x: -half,
    duration: 38,
    ease: 'none',
    repeat: -1,
    modifiers: {
      // Wrapping in a modifier keeps the loop seamless at any rate.
      x: (value) => `${gsap.utils.wrap(-half, 0, parseFloat(value))}px`,
    },
  });

  // Scrolling down speeds the strip up, scrolling up reverses it, and the
  // rate always decays back to a walking pace. A single quickTo target keeps
  // the two forces from fighting each other.
  const target = { scale: 1 };
  const applyScale = gsap.quickTo(target, 'scale', {
    duration: 0.5,
    ease: 'power2.out',
    onUpdate: () => loop.timeScale(target.scale),
  });

  ScrollTrigger.create({
    onUpdate(self) {
      const boost = 1 + Math.min(Math.abs(self.getVelocity()) / 900, 3.5);
      applyScale(boost * self.direction);
    },
  });

  // Settle back to the idle rate once scrolling stops.
  ScrollTrigger.addEventListener('scrollEnd', () => applyScale(1));
}

/* -------------------------------------------------------------------------- */
/* Section headings — the eyebrow rule draws itself in                        */
/* -------------------------------------------------------------------------- */

export function sectionEdgeScene(): void {
  const panels = gsap.utils.toArray<HTMLElement>('.cta__panel, .stats');

  panels.forEach((panel) => {
    gsap.fromTo(
      panel,
      { '--edge-progress': 0 },
      {
        '--edge-progress': 1,
        ease: ease.outExpo,
        duration: 1.3,
        scrollTrigger: { trigger: panel, start: 'top 82%', once: true },
      },
    );
  });
}

/* -------------------------------------------------------------------------- */
/* Registry                                                                    */
/* -------------------------------------------------------------------------- */

const scenes = [
  heroScene,
  heroScrollScene,
  scrollProgressScene,
  orbScene,
  headingScene,
  revealScene,
  staggerScene,
  counterScene,
  pipelineScene,
  moduleScene,
  marqueeScene,
  sectionEdgeScene,
  magneticScene,
  spotlightScene,
  mockScene,
];

/** Runs every scene. Individual failures are contained, never fatal. */
export function initScenes(): void {
  if (!motionEnabled()) return;

  scenes.forEach((scene) => {
    try {
      scene();
    } catch (error) {
      console.error(`[motion] scene "${scene.name}" failed`, error);
    }
  });

  ScrollTrigger.refresh();
}
