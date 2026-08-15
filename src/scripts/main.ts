/**
 * Client entry point.
 *
 * The pre-animation hidden state is set by the inline head script (so there is
 * no flash of visible-then-hidden content). That script also arms a failsafe
 * timer: if this module never confirms it is ready — a chunk failed to load,
 * a parse error, an offline visitor — the hidden state is torn down and the
 * page renders statically. Motion is an enhancement, never a prerequisite.
 */

import { initUI } from './ui';

function markMotionReady(): void {
  document.documentElement.dataset.motionReady = 'true';
}

async function boot(): Promise<void> {
  initUI();

  try {
    const { motionEnabled, refreshOnFontsReady } = await import('./motion');

    if (!motionEnabled()) {
      document.documentElement.dataset.motion = 'off';
      markMotionReady();
      return;
    }

    const { initScenes } = await import('./scenes');

    // One frame of headroom so the browser can paint before GSAP measures.
    requestAnimationFrame(() => {
      initScenes();
      markMotionReady();
      refreshOnFontsReady();
    });
  } catch (error) {
    // Motion failed to load — reveal everything and carry on.
    console.error('[motion] failed to initialise', error);
    document.documentElement.dataset.motion = 'off';
    markMotionReady();
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => void boot(), {
    once: true,
  });
} else {
  void boot();
}
