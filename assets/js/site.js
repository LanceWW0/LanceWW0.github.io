/* Site behaviour: mobile navigation.
   Loaded with `defer`, so the DOM is parsed before this runs.
   The theme controller lives here too — see the theme section below. */
(function () {
  'use strict';

  var root = document.documentElement;

  /* ---------------------------------------------------------------
     Mobile navigation
     --------------------------------------------------------------- */
  var nav = document.getElementById('site-nav');
  var navToggle = document.getElementById('nav-toggle');

  if (nav && navToggle) {
    // Only the mobile panel is hidden off-screen. On desktop the nav is
    // laid out inline and must stay in the tab order, so `inert` is
    // applied and removed as the viewport crosses the breakpoint.
    var mobile = window.matchMedia('(max-width: 767.98px)');

    function setNav(open) {
      root.toggleAttribute('data-nav-open', open);
      root.classList.toggle('is-locked', open);
      navToggle.setAttribute('aria-expanded', String(open));
      navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');

      if (open) {
        nav.removeAttribute('inert');
        var first = nav.querySelector('a');
        if (first) first.focus();
      } else {
        if (mobile.matches) nav.setAttribute('inert', '');
        if (document.activeElement && nav.contains(document.activeElement)) {
          navToggle.focus();
        }
      }
    }

    function syncInert() {
      if (mobile.matches && !root.hasAttribute('data-nav-open')) {
        nav.setAttribute('inert', '');
      } else {
        nav.removeAttribute('inert');
      }
    }

    navToggle.addEventListener('click', function () {
      setNav(!root.hasAttribute('data-nav-open'));
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && root.hasAttribute('data-nav-open')) setNav(false);
    });

    // Close after following a link (same-page anchors would otherwise
    // leave the panel covering the target).
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setNav(false);
    });

    // Crossing the breakpoint with the panel open would leave a stuck
    // overlay on desktop.
    var onChange = function () { setNav(false); syncInert(); };
    if (mobile.addEventListener) mobile.addEventListener('change', onChange);
    else mobile.addListener(onChange);

    syncInert();
  }

  /* ---------------------------------------------------------------
     Store picker modal (app pages published on both stores)
     --------------------------------------------------------------- */
  var modal = document.getElementById('store-modal');

  if (modal) {
    var lastTrigger = null;

    var openModal = function (trigger) {
      lastTrigger = trigger || null;
      modal.hidden = false;
      root.classList.add('is-locked');
      var first = modal.querySelector('.store-choice');
      if (first) first.focus();
    };

    var closeModal = function () {
      modal.hidden = true;
      root.classList.remove('is-locked');
      if (lastTrigger && typeof lastTrigger.focus === 'function') lastTrigger.focus();
    };

    document.querySelectorAll('[data-store-trigger]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        openModal(btn);
      });
    });

    modal.querySelectorAll('[data-store-close]').forEach(function (el) {
      el.addEventListener('click', closeModal);
    });

    modal.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;
      // Keep Tab inside the dialog while it is open.
      var items = modal.querySelectorAll('a[href], button:not([disabled])');
      if (!items.length) return;
      var first = items[0], last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus();
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !modal.hidden) closeModal();
    });
  }

  /* ---------------------------------------------------------------
     Theme toggle

     The inline script in <head> has already resolved data-theme, so this
     only has to handle changes. While no explicit preference is stored we
     keep following the OS; the first click stores a preference and that
     wins from then on.
     --------------------------------------------------------------- */
  var themeToggle = document.getElementById('theme-toggle');
  var themeMeta = document.querySelector('meta[name="theme-color"]');
  var os = window.matchMedia('(prefers-color-scheme: dark)');
  var locked = false;

  try { locked = !!localStorage.getItem('theme-pref'); } catch (e) {}

  function applyTheme(dark) {
    root.setAttribute('data-theme', dark ? 'dark' : 'light');
    root.style.colorScheme = dark ? 'dark' : 'light';
    if (themeMeta) themeMeta.setAttribute('content', dark ? '#0f1115' : '#ffffff');
    if (themeToggle) {
      themeToggle.setAttribute('aria-pressed', String(dark));
      themeToggle.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    }
  }

  // Suppress the 60+ colour transitions in the stylesheet for one frame,
  // otherwise flipping the theme animates the whole page in a slow wave.
  function withoutTransitions(fn) {
    root.classList.add('theme-transitioning');
    fn();
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        root.classList.remove('theme-transitioning');
      });
    });
  }

  applyTheme(root.getAttribute('data-theme') === 'dark');

  var onOS = function (e) { if (!locked) withoutTransitions(function () { applyTheme(e.matches); }); };
  if (os.addEventListener) os.addEventListener('change', onOS);
  else os.addListener(onOS);

  if (themeToggle) {
    themeToggle.hidden = false;
    themeToggle.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') !== 'dark';
      locked = true;
      try { localStorage.setItem('theme-pref', next ? 'dark' : 'light'); } catch (e) {}
      withoutTransitions(function () { applyTheme(next); });
    });
  }
})();
