// Day ↔ night page transitions. Pages opt into night with <html data-theme="night">.
// Entering a night page, the night page descends over the day page with a soft edge
// (dusk); leaving it, the day page rises from the bottom (dawn). Where the browser
// supports cross-document view transitions, the real pages animate in one continuous
// motion; otherwise a matching curtain covers the navigation. Loaded in <head>.
(() => {
  const root = document.documentElement;
  const KEY = 'sky-transition';
  const NIGHT_PAGES = ['sleep.html'];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const native = 'onpagereveal' in window && 'CSSViewTransitionRule' in window;

  const themeOf = url => NIGHT_PAGES.some(page => url.pathname.endsWith(`/${page}`) || url.pathname === page) ? 'night' : 'day';
  const current = () => root.dataset.theme === 'night' ? 'night' : 'day';
  // Returns 'night' or 'day' when following href changes theme, otherwise null.
  const crossing = href => {
    if (!href) return null;
    const url = new URL(href, location.href);
    if (url.origin !== location.origin || url.pathname === location.pathname || !/(\.html|\/)$/.test(url.pathname)) return null;
    const to = themeOf(url);
    return to === current() ? null : to;
  };
  const remember = to => { try { sessionStorage.setItem(KEY, to); } catch (error) { /* no storage: plain navigation */ } };
  const recall = () => {
    try { const to = sessionStorage.getItem(KEY); sessionStorage.removeItem(KEY); return to; } catch (error) { return null; }
  };

  if (native) {
    // The browser holds the old page until the new one is ready; CSS animates the pair.
    let clicked = null;
    document.addEventListener('click', event => { clicked = event.target.closest?.('a[href]')?.href || null; }, true);
    window.addEventListener('pageswap', event => {
      const to = crossing(event.activation?.entry?.url || clicked);
      if (to && event.viewTransition && !reduced.matches) remember(to);
    });
    window.addEventListener('pagereveal', event => {
      const to = recall();
      if (to && event.viewTransition?.types) event.viewTransition.types.add(`to-${to}`);
    });
    return;
  }

  // Fallback: draw the same soft-edged curtain over the page, navigate, then lift it.
  const arriving = recall();
  if (arriving && !reduced.matches) root.classList.add(`sky-arrive-${arriving}`);
  let leaving = false;
  document.addEventListener('click', event => {
    if (leaving || reduced.matches || event.defaultPrevented || event.button !== 0 ||
        event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest('a[href]');
    if (!link || (link.target && link.target !== '_self') || link.hasAttribute('download')) return;
    const to = crossing(link.href);
    if (!to) return;
    event.preventDefault();
    leaving = true;
    const veil = document.createElement('div');
    veil.className = `sky-veil sky-veil--${to === 'night' ? 'dusk' : 'dawn'}`;
    veil.setAttribute('aria-hidden', 'true');
    document.body.append(veil);
    let gone = false;
    const go = () => { if (gone) return; gone = true; remember(to); location.href = link.href; };
    veil.addEventListener('animationend', go, { once: true });
    setTimeout(go, 1100);
  });
  window.addEventListener('pageshow', event => {
    if (!event.persisted) return;
    leaving = false;
    document.querySelectorAll('.sky-veil').forEach(veil => veil.remove());
    root.classList.remove('sky-arrive-night', 'sky-arrive-day');
  });
})();
