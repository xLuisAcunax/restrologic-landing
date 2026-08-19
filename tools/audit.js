/**
 * In-page audit, injected into the preview and read back via --dump-dom.
 *
 * Checks that matter for this design and that a human eye misses:
 *   1. Document-level horizontal overflow (per viewport).
 *   2. WCAG contrast ratios for every semantic text/background pairing that
 *      the design actually uses, in both themes.
 *   3. Accessibility hygiene: image alts, button names, heading order,
 *      duplicate ids, tap-target sizes.
 */
(function () {
  function srgbToLin(c) {
    c /= 255;
    return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  }

  function luminance(rgb) {
    return (
      0.2126 * srgbToLin(rgb[0]) +
      0.7152 * srgbToLin(rgb[1]) +
      0.0722 * srgbToLin(rgb[2])
    );
  }

  /** Resolve any CSS colour (including var()/color-mix) to [r,g,b] via canvas. */
  var probe = document.createElement('div');
  document.body.appendChild(probe);

  function resolve(expr) {
    probe.style.color = '';
    probe.style.color = expr;
    var v = getComputedStyle(probe).color;
    var m = v.match(/[\d.]+/g);
    if (!m) return null;
    return [Number(m[0]), Number(m[1]), Number(m[2]), m[3] === undefined ? 1 : Number(m[3])];
  }

  /** Flatten a possibly-translucent foreground over a known background. */
  function over(fg, bg) {
    var a = fg[3] === undefined ? 1 : fg[3];
    return [
      fg[0] * a + bg[0] * (1 - a),
      fg[1] * a + bg[1] * (1 - a),
      fg[2] * a + bg[2] * (1 - a),
    ];
  }

  function contrast(fgExpr, bgExpr, baseExpr) {
    var base = resolve(baseExpr || 'var(--bg)');
    var bgRaw = resolve(bgExpr);
    var fg = resolve(fgExpr);
    if (!fg || !bgRaw || !base) return null;
    // Soft chips use translucent backgrounds; measuring their raw rgb reports
    // the colour they would be at full opacity, which is not what renders.
    var bg = over(bgRaw, base);
    var f = luminance(over(fg, bg));
    var b = luminance(bg);
    var hi = Math.max(f, b);
    var lo = Math.min(f, b);
    return (hi + 0.05) / (lo + 0.05);
  }

  // Pairings the design genuinely renders. label, foreground, background, min.
  var PAIRS = [
    ['body text on page', 'var(--text)', 'var(--bg)', 4.5],
    ['muted text on page', 'var(--text-muted)', 'var(--bg)', 4.5],
    ['subtle text on page', 'var(--text-subtle)', 'var(--bg)', 4.5],
    ['body text on surface', 'var(--text)', 'var(--surface)', 4.5],
    ['muted text on surface', 'var(--text-muted)', 'var(--surface)', 4.5],
    ['subtle text on surface', 'var(--text-subtle)', 'var(--surface)', 4.5],
    ['muted on tinted section', 'var(--text-muted)', 'var(--bg-tint)', 4.5],
    ['eyebrow (brand ink) on page', 'var(--brand-ink)', 'var(--bg)', 4.5],
    ['brand ink on tinted', 'var(--brand-ink)', 'var(--bg-tint)', 4.5],
    ['chip text on brand-soft', 'var(--brand-ink)', 'var(--brand-soft)', 4.5, 'var(--bg)'],
    ['chip text on accent-soft', 'var(--accent-ink)', 'var(--accent-soft)', 4.5, 'var(--bg)'],
    ['primary button label', 'var(--text-on-brand)', 'var(--brand-strong)', 4.5],
    ['plan badge label', 'var(--text-on-brand)', 'var(--brand-strong)', 4.5],
    ['pipeline number', 'var(--text-on-brand)', 'var(--brand-strong)', 4.5],
    ['headline gradient lightest stop', 'var(--grad-text-floor)', 'var(--bg)', 3.0],
    ['success text on surface', 'var(--status-success)', 'var(--surface)', 4.5],
    ['accent icon on surface', 'var(--accent)', 'var(--surface)', 3.0],
    ['brand icon on surface', 'var(--brand)', 'var(--surface)', 3.0],
    ['border on page (non-text)', 'var(--border-strong)', 'var(--bg)', 1.4],
    ['action (cyan) text on page', 'var(--action-ink)', 'var(--bg)', 4.5],
    ['action (cyan) on surface', 'var(--action)', 'var(--surface)', 3.0],
  ];

  // Every hue in the accent system, checked the same three ways it is used:
  // as label text on the page, as label text inside its own soft chip, and as
  // the fill under a label on a toned badge.
  var HUES = ['clay', 'honey', 'olive', 'indigo', 'rust', 'plum'];

  HUES.forEach(function (h) {
    PAIRS.push([
      h + ': ink on page',
      'var(--hue-' + h + '-ink)',
      'var(--bg)',
      4.5,
    ]);
    PAIRS.push([
      h + ': ink on surface',
      'var(--hue-' + h + '-ink)',
      'var(--surface)',
      4.5,
    ]);
    PAIRS.push([
      h + ': ink on own soft chip',
      'var(--hue-' + h + '-ink)',
      'var(--hue-' + h + '-soft)',
      4.5,
      'var(--surface)',
    ]);
    PAIRS.push([
      h + ': label on strong fill',
      'var(--hue-' + h + '-on)',
      'var(--hue-' + h + '-strong)',
      4.5,
    ]);
    PAIRS.push([
      h + ': base as graphic',
      'var(--hue-' + h + ')',
      'var(--surface)',
      3.0,
    ]);
  });

  function runContrast(theme) {
    document.documentElement.dataset.theme = theme;
    return PAIRS.map(function (p) {
      var ratio = contrast(p[1], p[2], p[4]);
      return {
        theme: theme,
        label: p[0],
        ratio: ratio === null ? null : Math.round(ratio * 100) / 100,
        min: p[3],
        pass: ratio !== null && ratio >= p[3],
      };
    });
  }

  var results = { overflow: {}, contrast: [], a11y: [] };

  // ---- 1. Overflow -------------------------------------------------------
  var de = document.documentElement;
  results.overflow = {
    clientWidth: de.clientWidth,
    scrollWidth: de.scrollWidth,
    overflowPx: de.scrollWidth - de.clientWidth,
  };

  // ---- 2. Contrast (both themes) ----------------------------------------
  var originalTheme = de.dataset.theme;
  results.contrast = runContrast('light').concat(runContrast('dark'));
  de.dataset.theme = originalTheme;

  // ---- 3. Accessibility hygiene -----------------------------------------
  document.querySelectorAll('img').forEach(function (img) {
    if (!img.hasAttribute('alt')) {
      results.a11y.push('img without alt: ' + (img.getAttribute('src') || '?'));
    } else if (img.getAttribute('alt').trim() === '') {
      results.a11y.push('img with empty alt: ' + (img.getAttribute('src') || '?'));
    }
  });

  document.querySelectorAll('button, a').forEach(function (el) {
    var name = (
      el.getAttribute('aria-label') ||
      el.textContent ||
      ''
    ).trim();
    if (!name) {
      results.a11y.push(
        'unnamed ' + el.tagName.toLowerCase() + ': .' + (el.className || '(no class)'),
      );
    }
  });

  var ids = {};
  document.querySelectorAll('[id]').forEach(function (el) {
    ids[el.id] = (ids[el.id] || 0) + 1;
  });
  Object.keys(ids).forEach(function (id) {
    if (ids[id] > 1) results.a11y.push('duplicate id: #' + id + ' x' + ids[id]);
  });

  var last = 0;
  document.querySelectorAll('h1,h2,h3,h4,h5,h6').forEach(function (h) {
    var lvl = Number(h.tagName[1]);
    if (last && lvl > last + 1) {
      results.a11y.push(
        'heading jump h' + last + ' -> h' + lvl + ': "' + h.textContent.trim().slice(0, 40) + '"',
      );
    }
    last = lvl;
  });

  var h1s = document.querySelectorAll('h1').length;
  if (h1s !== 1) results.a11y.push('expected exactly one h1, found ' + h1s);

  // Interactive targets smaller than 24px in either axis.
  document.querySelectorAll('button, a, input, textarea, summary').forEach(function (el) {
    var r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return;
    if (r.height < 24 || r.width < 24) {
      results.a11y.push(
        'small target ' + Math.round(r.width) + 'x' + Math.round(r.height) +
          ': ' + el.tagName.toLowerCase() + '.' + String(el.className).slice(0, 40),
      );
    }
  });

  probe.remove();

  document.body.innerHTML =
    '<pre id="audit">' +
    JSON.stringify(results, null, 1).replace(/</g, '&lt;') +
    '</pre>';
})();
