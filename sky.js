// Day ↔ night page transitions. Entering a night page (<html data-theme="night">), a dusk
// curtain falls from the top; leaving it, a dawn curtain rises. The next page starts under
// the same sky and fades in. Loaded synchronously in <head> so the arrival sky paints first.
(() => {
  const root = document.documentElement;
  const KEY = 'sky-transition';
  const NIGHT_PAGES = ['sleep.html'];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

  try {
    const arriving = sessionStorage.getItem(KEY);
    if (arriving) {
      sessionStorage.removeItem(KEY);
      if (!reduced.matches) root.classList.add(`sky-arrive-${arriving}`);
    }
  } catch (error) { /* storage unavailable: navigate without the arrival sky */ }

  const themeOf = url => NIGHT_PAGES.some(page => url.pathname.endsWith(`/${page}`) || url.pathname === page) ? 'night' : 'day';
  let leaving = false;

  document.addEventListener('click', event => {
    if (leaving || reduced.matches || event.defaultPrevented || event.button !== 0 ||
        event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest('a[href]');
    if (!link || (link.target && link.target !== '_self') || link.hasAttribute('download')) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || url.pathname === location.pathname || !/(\.html|\/)$/.test(url.pathname)) return;
    const from = root.dataset.theme === 'night' ? 'night' : 'day';
    const to = themeOf(url);
    if (from === to) return;

    event.preventDefault();
    leaving = true;
    const veil = document.createElement('div');
    veil.className = `sky-veil sky-veil--${to === 'night' ? 'dusk' : 'dawn'}`;
    veil.setAttribute('aria-hidden', 'true');
    document.body.append(veil);
    let gone = false;
    const go = () => {
      if (gone) return;
      gone = true;
      try { sessionStorage.setItem(KEY, to); } catch (error) { /* arrive without the sky */ }
      location.href = url.href;
    };
    veil.addEventListener('animationend', event => { if (event.target === veil) go(); });
    setTimeout(go, 1200);
  });

  // The themed curtain replaces the default cross-fade for that one navigation.
  window.addEventListener('pageswap', event => {
    if (leaving && event.viewTransition) event.viewTransition.skipTransition();
  });

  // Returning through the back/forward cache: clear any curtain left from leaving.
  window.addEventListener('pageshow', event => {
    if (!event.persisted) return;
    leaving = false;
    document.querySelectorAll('.sky-veil').forEach(veil => veil.remove());
    root.classList.remove('sky-arrive-night', 'sky-arrive-day');
  });
})();
