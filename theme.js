// Light/dark theme. Runs in <head> so the saved (or system) theme applies before the first
// paint. The header button toggles it, and the choice is remembered across pages and visits.
(() => {
  const root = document.documentElement;
  const KEY = 'theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const saved = () => { try { return localStorage.getItem(KEY); } catch (error) { return null; } };
  let button = null;

  const apply = theme => {
    root.dataset.theme = theme;
    if (button) button.setAttribute('aria-pressed', String(theme === 'dark'));
  };
  apply(saved() || (system.matches ? 'dark' : 'light'));

  // Until the visitor chooses, follow changes to the system setting.
  system.addEventListener('change', event => { if (!saved()) apply(event.matches ? 'dark' : 'light'); });

  document.addEventListener('DOMContentLoaded', () => {
    button = document.querySelector('.theme-toggle');
    if (!button) return;
    button.hidden = false;
    apply(root.dataset.theme);
    button.addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      apply(next);
      try { localStorage.setItem(KEY, next); } catch (error) { /* not remembered */ }
    });
  });
})();
