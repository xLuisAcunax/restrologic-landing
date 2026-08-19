/**
 * Preview-only motion engine.
 *
 * The production site uses GSAP + ScrollTrigger (src/scripts/scenes.ts). GSAP
 * could not be downloaded in the sandbox this preview was built in, so this
 * file reproduces the same scenes with ~200 lines of vanilla JS against the
 * same data attributes. It exists so the scroll behaviour can be *seen* before
 * running the real site; it is not shipped and is not a fallback.
 *
 * Scene parity with scenes.ts:
 *   heroScene · heroScrollScene · scrollProgressScene · orbScene ·
 *   headingScene · revealScene · staggerScene · counterScene ·
 *   pipelineScene · moduleScene · marqueeScene · sectionEdgeScene ·
 *   magneticScene · spotlightScene
 */
(function () {
  'use strict';

  var root = document.documentElement;

  // Opt out for reduced-motion users, and for the screenshot harness — a
  // headless render advances virtual time without advancing CSS transitions,
  // so a moving page cannot be captured in its resting state.
  var staticMode =
    window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
    /[?&]static/.test(location.search) ||
    root.hasAttribute('data-static');

  if (staticMode) {
    root.dataset.motion = 'off';
    return;
  }

  root.dataset.motion = 'on';

  // Failsafe, mirroring the production one in ThemeScript.astro: if anything
  // below throws, reveal every animated element rather than leaving the page
  // blank. Cleared once the engine has finished wiring itself up.
  var failsafe = window.setTimeout(function () {
    document
      .querySelectorAll('[data-reveal],[data-stagger] > *,[data-pipeline-step],[data-float],[data-split]')
      .forEach(function (el) {
        el.style.opacity = '1';
        el.style.transform = 'none';
      });
    root.dataset.motion = 'off';
  }, 3000);

  var lerp = function (a, b, t) {
    return a + (b - a) * t;
  };
  var clamp = function (v, min, max) {
    return Math.min(Math.max(v, min), max);
  };
  var easeOutExpo = function (t) {
    return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
  };

  /* ---------------------------------------------------------------- split -- */
  // Wrap each word in a mask so headings can rise line by line.
  function splitWords(el) {
    if (el.childElementCount > 0 || el.dataset.split === 'done') return [];
    var text = (el.textContent || '').trim();
    if (!text) return [];

    var frag = document.createDocumentFragment();
    var inners = [];
    text.split(/\s+/).forEach(function (word, i, arr) {
      var outer = document.createElement('span');
      outer.className = 'word';
      var inner = document.createElement('span');
      inner.className = 'word__inner';
      inner.textContent = word;
      outer.appendChild(inner);
      frag.appendChild(outer);
      inners.push(inner);
      if (i < arr.length - 1) frag.appendChild(document.createTextNode(' '));
    });

    el.textContent = '';
    el.appendChild(frag);
    el.dataset.split = 'done';
    return inners;
  }

  document.querySelectorAll('[data-split]').forEach(function (h) {
    if (h.closest('[data-hero]')) return;
    var words = splitWords(h);
    h.style.opacity = '1';
    words.forEach(function (w, i) {
      w.style.transform = 'translateY(112%)';
      w.style.transition =
        'transform .85s cubic-bezier(.16,1,.3,1) ' + i * 0.045 + 's';
    });
  });

  /* --------------------------------------------------------------- reveal -- */
  var revealables = [];
  document.querySelectorAll('[data-reveal]').forEach(function (el) {
    if (el.closest('[data-hero]')) return;
    el.style.opacity = '0';
    el.style.transform = 'translateY(26px)';
    el.style.transition =
      'opacity .7s cubic-bezier(.22,1,.36,1), transform .7s cubic-bezier(.22,1,.36,1)';
    revealables.push(el);
  });

  document.querySelectorAll('[data-stagger]').forEach(function (group) {
    Array.prototype.forEach.call(group.children, function (child, i) {
      child.style.opacity = '0';
      child.style.transform = 'translateY(30px)';
      child.style.transition =
        'opacity .7s cubic-bezier(.22,1,.36,1) ' + i * 0.08 + 's, ' +
        'transform .7s cubic-bezier(.22,1,.36,1) ' + i * 0.08 + 's';
      revealables.push(child);
    });
  });

  document.querySelectorAll('[data-pipeline-step]').forEach(function (el, i) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(34px)';
    el.style.transition =
      'opacity .7s cubic-bezier(.22,1,.36,1) ' + i * 0.14 + 's, ' +
      'transform .7s cubic-bezier(.22,1,.36,1) ' + i * 0.14 + 's';
    revealables.push(el);
  });

  var io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
        el.querySelectorAll &&
          el.querySelectorAll('.word__inner').forEach(function (w) {
            w.style.transform = 'translateY(0)';
          });
        io.unobserve(el);
      });
    },
    { rootMargin: '0px 0px -12% 0px' },
  );

  revealables.forEach(function (el) {
    io.observe(el);
  });

  document.querySelectorAll('[data-split]').forEach(function (h) {
    if (h.closest('[data-hero]')) return;
    new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.querySelectorAll('.word__inner').forEach(function (w) {
            w.style.transform = 'translateY(0)';
          });
          obs.disconnect();
        });
      },
      { rootMargin: '0px 0px -14% 0px' },
    ).observe(h);
  });

  /* -------------------------------------------------------------- counters -- */
  document.querySelectorAll('[data-count]').forEach(function (el) {
    var target = parseFloat((el.dataset.count || '').replace(/[^\d.-]/g, ''));
    if (!isFinite(target)) return;
    var grouped = el.dataset.countGroup === 'true';
    var render = function (v) {
      return grouped
        ? v.toLocaleString('es-CO', { maximumFractionDigits: 0 })
        : String(v);
    };
    new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var start = performance.now();
          (function tick(now) {
            var t = clamp((now - start) / 1600, 0, 1);
            el.textContent = render(Math.round(target * easeOutExpo(t)));
            if (t < 1) requestAnimationFrame(tick);
          })(start);
          obs.disconnect();
        });
      },
      { rootMargin: '0px 0px -10% 0px' },
    ).observe(el);
  });

  /* ----------------------------------------------------------------- hero -- */
  var heroTargets = [
    ['[data-hero-badge]', 0],
    ['[data-hero-lede]', 0.55],
    ['[data-hero-actions]', 0.68],
  ];
  heroTargets.forEach(function (pair) {
    var el = document.querySelector(pair[0]);
    if (!el) return;
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    requestAnimationFrame(function () {
      el.style.transition =
        'opacity .7s cubic-bezier(.16,1,.3,1) ' + pair[1] + 's, ' +
        'transform .7s cubic-bezier(.16,1,.3,1) ' + pair[1] + 's';
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    });
  });

  document.querySelectorAll('[data-hero-line] > span').forEach(function (l, i) {
    l.style.transform = 'translateY(118%)';
    requestAnimationFrame(function () {
      l.style.transition =
        'transform .95s cubic-bezier(.16,1,.3,1) ' + (0.12 + i * 0.09) + 's';
      l.style.transform = 'translateY(0)';
    });
  });

  document.querySelectorAll('[data-hero-proof] > *').forEach(function (el, i) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(18px)';
    requestAnimationFrame(function () {
      el.style.transition =
        'opacity .7s cubic-bezier(.16,1,.3,1) ' + (0.8 + i * 0.08) + 's, ' +
        'transform .7s cubic-bezier(.16,1,.3,1) ' + (0.8 + i * 0.08) + 's';
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    });
  });

  var mock = document.querySelector('[data-hero-mock]');
  if (mock) {
    mock.style.opacity = '0';
    mock.style.transform = 'translateY(46px) scale(.96)';
    requestAnimationFrame(function () {
      mock.style.transition =
        'opacity 1.15s cubic-bezier(.16,1,.3,1) .35s, transform 1.15s cubic-bezier(.16,1,.3,1) .35s';
      mock.style.opacity = '1';
      mock.style.transform = 'translateY(0) scale(1)';
    });
  }

  document.querySelectorAll('[data-float]').forEach(function (el, i) {
    el.style.opacity = '0';
    requestAnimationFrame(function () {
      el.style.transition = 'opacity .7s ease ' + (0.9 + i * 0.12) + 's';
      el.style.opacity = '1';
    });
  });

  /* --------------------------------------------------------- scroll engine -- */
  var mockEl = document.querySelector('.mock');
  var heroSection = document.querySelector('[data-hero]');
  var heroCopy = document.querySelector('.hero__copy');
  var orbs = Array.prototype.slice.call(
    document.querySelectorAll('[data-parallax-orb]'),
  );
  var shots = Array.prototype.slice.call(
    document.querySelectorAll('[data-parallax] .module__frame'),
  );
  var rail = document.querySelector('[data-pipeline-rail]');
  var pipeline = document.querySelector('[data-pipeline]');
  var bar = document.querySelector('[data-scrollbar]');
  var fill = document.querySelector('[data-scroll-progress]');
  var wide = window.matchMedia('(min-width: 68rem)').matches;

  var smooth = { progress: 0 };

  function frame() {
    var vh = window.innerHeight;
    var doc = document.documentElement;
    var max = doc.scrollHeight - vh;
    var progress = max > 0 ? clamp(window.scrollY / max, 0, 1) : 0;

    smooth.progress = lerp(smooth.progress, progress, 0.14);

    /* scrollProgressScene */
    if (fill && bar) {
      fill.style.setProperty('--scroll-progress', smooth.progress.toFixed(4));
      bar.dataset.visible = String(progress > 0.005);
    }

    /* heroScrollScene */
    if (heroSection) {
      var heroRect = heroSection.getBoundingClientRect();
      var out = clamp(-heroRect.top / Math.max(heroRect.height, 1), 0, 1);

      if (mockEl && wide) {
        mockEl.style.transform =
          'perspective(1600px) rotateY(' + (-9 + 9 * out) + 'deg) rotateX(' +
          (4 - 4 * out) + 'deg) translateY(' + -40 * out + 'px)';
      }
      if (heroCopy) {
        var fade = clamp((out - 0.35) / 0.65, 0, 1);
        heroCopy.style.transform = 'translateY(' + -60 * fade + 'px)';
        heroCopy.style.opacity = String(1 - 0.75 * fade);
      }
    }

    /* orbScene */
    orbs.forEach(function (orb) {
      var rate = parseFloat(orb.dataset.parallaxOrb || '0.2');
      var host = orb.closest('section') || orb.parentElement;
      if (!host) return;
      var r = host.getBoundingClientRect();
      var p = clamp((vh - r.top) / (vh + r.height), 0, 1);
      orb.style.transform = 'translateY(' + rate * 100 * (p - 0.5) * 2 + '%)';
    });

    /* moduleScene — parallax half */
    shots.forEach(function (frameEl) {
      var r = frameEl.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) return;
      var p = clamp((vh - r.top) / (vh + r.height), 0, 1);
      frameEl.style.transform = 'translateY(' + (5 - 10 * p) + '%)';
    });

    /* pipelineScene — rail draw */
    if (rail && pipeline) {
      var pr = pipeline.getBoundingClientRect();
      var railP = clamp((vh * 0.7 - pr.top) / Math.max(pr.height * 0.75, 1), 0, 1);
      rail.style.setProperty('--rail-progress', railP.toFixed(4));
    }

    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  /* ------------------------------------------------------------- marquee -- */
  var track = document.querySelector('.marquee__track');
  if (track) {
    track.style.animation = 'none';
    var half = track.scrollWidth / 2;
    var offset = 0;
    var scale = 1;
    var targetScale = 1;
    var lastY = window.scrollY;
    var lastT = performance.now();

    window.addEventListener(
      'scroll',
      function () {
        var now = performance.now();
        var dt = Math.max(now - lastT, 1);
        var velocity = ((window.scrollY - lastY) / dt) * 1000;
        lastY = window.scrollY;
        lastT = now;
        targetScale =
          (1 + Math.min(Math.abs(velocity) / 900, 3.5)) *
          (velocity >= 0 ? 1 : -1);
      },
      { passive: true },
    );

    (function marquee() {
      targetScale = lerp(targetScale, targetScale >= 0 ? 1 : -1, 0.03);
      scale = lerp(scale, targetScale, 0.08);
      offset -= (half / 38 / 60) * scale;
      if (offset <= -half) offset += half;
      if (offset > 0) offset -= half;
      track.style.transform = 'translateX(' + offset + 'px)';
      requestAnimationFrame(marquee);
    })();
  }

  /* ---------------------------------------------------- magnetic + spotlight */
  if (window.matchMedia('(pointer: fine)').matches) {
    document.querySelectorAll('[data-magnetic]').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        el.style.transform =
          'translate(' + (e.clientX - r.left - r.width / 2) * 0.28 + 'px,' +
          (e.clientY - r.top - r.height / 2) * 0.4 + 'px)';
      });
      el.addEventListener('pointerleave', function () {
        el.style.transition = 'transform .4s cubic-bezier(.22,1,.36,1)';
        el.style.transform = 'translate(0,0)';
        setTimeout(function () {
          el.style.transition = '';
        }, 400);
      });
    });

    document.querySelectorAll('.card--spotlight').forEach(function (card) {
      card.addEventListener('pointermove', function (e) {
        var r = card.getBoundingClientRect();
        card.style.setProperty('--mx', e.clientX - r.left + 'px');
        card.style.setProperty('--my', e.clientY - r.top + 'px');
      });
    });
  }

  /* --------------------------------------------------------- section edges -- */
  document.querySelectorAll('.cta__panel, .stats').forEach(function (panel) {
    panel.style.setProperty('--edge-progress', '0');
    new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var start = performance.now();
          (function tick(now) {
            var t = clamp((now - start) / 1300, 0, 1);
            panel.style.setProperty('--edge-progress', easeOutExpo(t).toFixed(4));
            if (t < 1) requestAnimationFrame(tick);
          })(start);
          obs.disconnect();
        });
      },
      { rootMargin: '0px 0px -18% 0px' },
    ).observe(panel);
  });

  /* ------------------------------------------------------------- app shell --
     Vanilla mirror of scenes.ts `shellScene`. Not a fallback — the real site
     runs GSAP — but the preview has no bundle, and a still replica would hide
     exactly the behaviour this hero exists to demonstrate. */
  (function shell() {
    var root = document.querySelector('[data-shell]');
    if (!root || document.documentElement.dataset.motion === 'off') return;

    var format = function (v) {
      return v.toLocaleString('es-CO', { maximumFractionDigits: 0 });
    };

    /* Shift clock — one minute per four seconds. */
    var clock = root.querySelector('[data-shell-clock]');
    if (clock) {
      var minutes = 14 * 60 + 10;
      window.setInterval(function () {
        minutes = (minutes + 1) % (24 * 60);
        clock.textContent =
          String(Math.floor(minutes / 60)).padStart(2, '0') +
          ':' +
          String(minutes % 60).padStart(2, '0');
      }, 4000);
    }

    /* A comanda advancing Pendiente -> Cocinando -> Listo. */
    var chips = document.querySelectorAll('[data-ticket-state]');
    var bar = document.querySelector('[data-ticket-bar]');
    if (chips.length) {
      var step = 0;
      window.setInterval(function () {
        step = (step + 1) % (chips.length + 1);
        var active = step % chips.length;
        Array.prototype.forEach.call(chips, function (chip, i) {
          if (i === active && step < chips.length) chip.dataset.on = 'true';
          else if (i === 0 && step === chips.length) chip.dataset.on = 'true';
          else delete chip.dataset.on;
        });
        if (bar) {
          bar.style.width =
            step >= chips.length
              ? '8%'
              : (((active + 1) / chips.length) * 100).toFixed(0) + '%';
        }
      }, 2600);
    }

    /* Payments landing: a row recycles to the top and sales grows by it. */
    var list = root.querySelector('.shell__rows');
    var figure = root.querySelector('[data-shell-kpi] [data-count]');
    if (list && list.children.length > 1) {
      var payments = [11400, 38500, 24900, 45100, 19800];
      var index = 0;
      var sales = Number((figure && figure.dataset.count) || 0);

      window.setInterval(function () {
        var payment = payments[index % payments.length];
        index += 1;

        var last = list.lastElementChild;
        var first = list.firstElementChild;
        if (!last || !first) return;

        var amount = last.querySelector('.shell__row-amount');
        if (amount) amount.textContent = '+ $ ' + format(payment);
        list.insertBefore(last, first);

        last.style.transition = 'none';
        last.style.opacity = '0';
        last.style.transform = 'translateY(-14px)';
        last.style.backgroundColor = 'rgba(200,115,59,0.10)';
        requestAnimationFrame(function () {
          last.style.transition =
            'opacity .5s ease, transform .5s cubic-bezier(.16,1,.3,1), background-color .9s ease';
          last.style.opacity = '1';
          last.style.transform = 'translateY(0)';
          last.style.backgroundColor = 'rgba(200,115,59,0)';
        });

        if (figure) {
          var from = sales;
          sales += payment;
          var start = performance.now();
          (function tick(now) {
            var t = clamp((now - start) / 1100, 0, 1);
            figure.textContent = format(
              Math.round(from + (sales - from) * easeOutExpo(t)),
            );
            if (t < 1) requestAnimationFrame(tick);
          })(start);
        }
      }, 7900);
    }
  })();

  // Everything wired successfully — stand the failsafe down.
  window.clearTimeout(failsafe);
})();
