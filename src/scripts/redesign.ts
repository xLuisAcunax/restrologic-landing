const root = document.querySelector<HTMLElement>('.landing-redesign');

if (root && root.dataset.ready !== 'true') {
  root.dataset.ready = 'true';

  const revealItems = root.querySelectorAll<HTMLElement>('[data-reveal]');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reducedMotion || !('IntersectionObserver' in window)) {
    revealItems.forEach((item) => item.classList.add('is-visible'));
  } else {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.14 },
    );
    revealItems.forEach((item) => observer.observe(item));
  }

  const progress = root.querySelector<HTMLElement>('[data-scroll-progress]');
  const updateProgress = () => {
    if (!progress) return;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = `${max > 0 ? (window.scrollY / max) * 100 : 0}%`;
  };
  updateProgress();
  window.addEventListener('scroll', updateProgress, { passive: true });

  const hero = root.querySelector<HTMLElement>('[data-hero-pointer]');
  hero?.addEventListener('pointermove', (event) => {
    if (reducedMotion) return;
    const rect = hero.getBoundingClientRect();
    hero.style.setProperty('--pointer-x', `${((event.clientX - rect.left) / rect.width) * 100}%`);
    hero.style.setProperty('--pointer-y', `${((event.clientY - rect.top) / rect.height) * 100}%`);
  });

  const menu = root.querySelector<HTMLElement>('[data-nav-menu]');
  const menuToggle = root.querySelector<HTMLButtonElement>('[data-menu-toggle]');
  const closeMenu = () => {
    menu?.classList.remove('is-open');
    menuToggle?.classList.remove('is-open');
    menuToggle?.setAttribute('aria-expanded', 'false');
  };
  menuToggle?.addEventListener('click', () => {
    const open = !menu?.classList.contains('is-open');
    menu?.classList.toggle('is-open', open);
    menuToggle.classList.toggle('is-open', open);
    menuToggle.setAttribute('aria-expanded', String(open));
  });
  menu?.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));

  const tabs = [...root.querySelectorAll<HTMLButtonElement>('[data-module-tab]')];
  const panels = [...root.querySelectorAll<HTMLElement>('[data-module-panel]')];
  const activateModule = (id: string, focus = false) => {
    tabs.forEach((tab) => {
      const active = tab.dataset.moduleTab === id;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      if (active && focus) tab.focus();
    });
    panels.forEach((panel) => {
      panel.hidden = panel.dataset.modulePanel !== id;
    });
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateModule(tab.dataset.moduleTab ?? 'dashboard'));
    tab.addEventListener('keydown', (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === 'Home'
        ? 0
        : event.key === 'End'
          ? tabs.length - 1
          : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
      activateModule(tabs[next]?.dataset.moduleTab ?? 'dashboard', true);
    });
  });

  const form = root.querySelector<HTMLFormElement>('[data-demo-form]');
  const success = root.querySelector<HTMLElement>('[data-form-success]');
  form?.addEventListener('submit', (event) => {
    event.preventDefault();
    success?.removeAttribute('hidden');
    form.reset();
  });
}
