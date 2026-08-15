/**
 * Interactive behaviour that is not animation: theme, navigation, drawer,
 * language dropdown, pricing switch, scroll spy.
 *
 * Every controller is defensive — it returns early when its markup is absent,
 * so the same bundle is safe on any page.
 */

const THEME_STORAGE_KEY = 'rl-theme';
type Theme = 'light' | 'dark';

/* -------------------------------------------------------------------------- */
/* Theme                                                                       */
/* -------------------------------------------------------------------------- */

function currentTheme(): Theme {
  return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
}

function applyTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme;
  document
    .querySelectorAll<HTMLElement>('[data-theme-toggle]')
    .forEach((button) => {
      button.setAttribute('aria-pressed', String(theme === 'dark'));
    });

  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    /* Private mode or blocked storage — the theme still applies for this page. */
  }
}

export function initTheme(): void {
  applyTheme(currentTheme());

  document
    .querySelectorAll<HTMLElement>('[data-theme-toggle]')
    .forEach((button) => {
      button.addEventListener('click', () => {
        applyTheme(currentTheme() === 'dark' ? 'light' : 'dark');
      });
    });

  // Follow the OS only while the visitor has not made an explicit choice.
  window
    .matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', (event) => {
      let stored: string | null = null;
      try {
        stored = localStorage.getItem(THEME_STORAGE_KEY);
      } catch {
        /* ignore */
      }
      if (!stored) applyTheme(event.matches ? 'dark' : 'light');
    });
}

/* -------------------------------------------------------------------------- */
/* Sticky header                                                               */
/* -------------------------------------------------------------------------- */

export function initHeader(): void {
  const header = document.querySelector<HTMLElement>('[data-header]');
  if (!header) return;

  const sentinel = document.createElement('div');
  sentinel.setAttribute('aria-hidden', 'true');
  sentinel.style.cssText = 'position:absolute;top:0;height:1px;width:1px;';
  document.body.prepend(sentinel);

  const observer = new IntersectionObserver(
    ([entry]) => {
      header.dataset.stuck = String(!entry.isIntersecting);
    },
    { rootMargin: '-8px 0px 0px 0px' },
  );

  observer.observe(sentinel);
}

/* -------------------------------------------------------------------------- */
/* Mobile drawer                                                               */
/* -------------------------------------------------------------------------- */

export function initDrawer(): void {
  const toggle = document.querySelector<HTMLButtonElement>('[data-drawer-toggle]');
  const drawer = document.querySelector<HTMLElement>('[data-drawer]');
  if (!toggle || !drawer) return;

  const setOpen = (open: boolean): void => {
    drawer.dataset.open = String(open);
    document.documentElement.dataset.drawerOpen = String(open);
    toggle.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';

    if (open) {
      drawer.querySelector<HTMLAnchorElement>('a')?.focus();
    }
  };

  toggle.addEventListener('click', () => {
    setOpen(drawer.dataset.open !== 'true');
  });

  // Any navigation closes the drawer.
  drawer.addEventListener('click', (event) => {
    if ((event.target as HTMLElement).closest('a')) setOpen(false);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && drawer.dataset.open === 'true') {
      setOpen(false);
      toggle.focus();
    }
  });

  // Never leave the drawer open when the layout switches to desktop.
  window.matchMedia('(min-width: 60rem)').addEventListener('change', (event) => {
    if (event.matches) setOpen(false);
  });
}

/* -------------------------------------------------------------------------- */
/* Language dropdown                                                           */
/* -------------------------------------------------------------------------- */

export function initDropdowns(): void {
  const dropdowns = document.querySelectorAll<HTMLElement>('[data-dropdown]');
  if (!dropdowns.length) return;

  const closeAll = (except?: HTMLElement): void => {
    dropdowns.forEach((dropdown) => {
      if (dropdown === except) return;
      dropdown.dataset.open = 'false';
      dropdown
        .querySelector('[data-dropdown-trigger]')
        ?.setAttribute('aria-expanded', 'false');
    });
  };

  dropdowns.forEach((dropdown) => {
    const trigger = dropdown.querySelector<HTMLButtonElement>(
      '[data-dropdown-trigger]',
    );
    if (!trigger) return;

    trigger.addEventListener('click', (event) => {
      event.stopPropagation();
      const open = dropdown.dataset.open !== 'true';
      closeAll(dropdown);
      dropdown.dataset.open = String(open);
      trigger.setAttribute('aria-expanded', String(open));
    });
  });

  document.addEventListener('click', () => closeAll());
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeAll();
  });
}

/* -------------------------------------------------------------------------- */
/* Pricing period switch                                                       */
/* -------------------------------------------------------------------------- */

export function initPricingSwitch(): void {
  const segmented = document.querySelector<HTMLElement>('[data-billing]');
  if (!segmented) return;

  const options = Array.from(
    segmented.querySelectorAll<HTMLButtonElement>('[data-billing-option]'),
  );
  const thumb = segmented.querySelector<HTMLElement>('[data-billing-thumb]');
  if (!options.length) return;

  const moveThumb = (active: HTMLElement): void => {
    if (!thumb) return;
    thumb.style.width = `${active.offsetWidth}px`;
    thumb.style.transform = `translateX(${active.offsetLeft - options[0].offsetLeft}px)`;
  };

  const select = (period: 'monthly' | 'yearly'): void => {
    options.forEach((option) => {
      const isActive = option.dataset.billingOption === period;
      option.setAttribute('aria-selected', String(isActive));
      if (isActive) moveThumb(option);
    });

    document
      .querySelectorAll<HTMLElement>('[data-price]')
      .forEach((price) => {
        const next = price.dataset[period];
        if (next) price.textContent = next;
      });

    document
      .querySelectorAll<HTMLElement>('[data-period-label]')
      .forEach((label) => {
        const next = label.dataset[period];
        if (next) label.textContent = next;
      });
  };

  options.forEach((option) => {
    option.addEventListener('click', () => {
      select(
        (option.dataset.billingOption as 'monthly' | 'yearly') ?? 'monthly',
      );
    });
  });

  // Position the thumb under the initially selected option.
  const initial =
    options.find((o) => o.getAttribute('aria-selected') === 'true') ??
    options[0];
  requestAnimationFrame(() => moveThumb(initial));
  window.addEventListener('resize', () => moveThumb(initial), {
    passive: true,
  });
}

/* -------------------------------------------------------------------------- */
/* Scroll spy — highlights the nav link for the section in view                */
/* -------------------------------------------------------------------------- */

export function initScrollSpy(): void {
  const links = Array.from(
    document.querySelectorAll<HTMLAnchorElement>('[data-nav-link]'),
  );
  if (!links.length) return;

  const sections = links
    .map((link) => {
      const id = link.getAttribute('href')?.split('#')[1];
      return id ? document.getElementById(id) : null;
    })
    .filter((section): section is HTMLElement => section !== null);

  if (!sections.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        links.forEach((link) => {
          const matches = link.getAttribute('href')?.endsWith(`#${entry.target.id}`);
          link.setAttribute('aria-current', String(Boolean(matches)));
        });
      });
    },
    { rootMargin: '-45% 0px -50% 0px' },
  );

  sections.forEach((section) => observer.observe(section));
}

/* -------------------------------------------------------------------------- */
/* Accordion — one open at a time                                              */
/* -------------------------------------------------------------------------- */

export function initAccordion(): void {
  const items = Array.from(
    document.querySelectorAll<HTMLDetailsElement>('[data-accordion] details'),
  );
  if (!items.length) return;

  items.forEach((item) => {
    item.addEventListener('toggle', () => {
      if (!item.open) return;
      items.forEach((other) => {
        if (other !== item) other.open = false;
      });
    });
  });
}

/* -------------------------------------------------------------------------- */
/* Screen gallery tabs                                                         */
/* -------------------------------------------------------------------------- */

export function initGallery(): void {
  const gallery = document.querySelector<HTMLElement>('[data-gallery]');
  if (!gallery) return;

  const tabs = Array.from(
    gallery.querySelectorAll<HTMLButtonElement>('[data-gallery-tab]'),
  );
  const panels = Array.from(
    gallery.querySelectorAll<HTMLElement>('[data-gallery-panel]'),
  );
  if (!tabs.length || !panels.length) return;

  const select = (id: string, focus = false): void => {
    tabs.forEach((tab) => {
      const active = tab.dataset.galleryTab === id;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      if (active && focus) tab.focus();
    });

    panels.forEach((panel) => {
      const active = panel.dataset.galleryPanel === id;
      panel.hidden = !active;
      panel.dataset.active = String(active);
    });
  };

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const id = tab.dataset.galleryTab;
      if (id) select(id);
    });
  });

  // Roving focus: arrow keys move between tabs, Home/End jump to the ends.
  gallery.addEventListener('keydown', (event) => {
    const current = tabs.findIndex(
      (tab) => tab.getAttribute('aria-selected') === 'true',
    );
    if (current < 0) return;

    let next = current;
    switch (event.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        next = (current + 1) % tabs.length;
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        next = (current - 1 + tabs.length) % tabs.length;
        break;
      case 'Home':
        next = 0;
        break;
      case 'End':
        next = tabs.length - 1;
        break;
      default:
        return;
    }

    event.preventDefault();
    const id = tabs[next]?.dataset.galleryTab;
    if (id) select(id, true);
  });
}

/** Boots every controller. */
export function initUI(): void {
  const controllers = [
    initTheme,
    initHeader,
    initDrawer,
    initDropdowns,
    initPricingSwitch,
    initScrollSpy,
    initAccordion,
    initGallery,
  ];

  controllers.forEach((controller) => {
    try {
      controller();
    } catch (error) {
      console.error(`[ui] "${controller.name}" failed`, error);
    }
  });
}
