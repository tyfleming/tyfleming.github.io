// Highlights the "On this page" entry for the section being read.
(() => {
  const toc = document.querySelector('.doc-toc');
  if (!toc) return;
  const links = Array.from(toc.querySelectorAll('a[href^="#"]'));
  const entries = links
    .map(link => ({link, target: document.getElementById(link.hash.slice(1))}))
    .filter(entry => entry.target);
  let active = null, queued = false;

  function update() {
    queued = false;
    const offset = window.innerHeight * 0.28;
    let current = entries[0];
    for (const entry of entries) {
      if (entry.target.getBoundingClientRect().top - offset <= 0) current = entry;
    }
    if (current === active) return;
    active = current;
    links.forEach(link => link.classList.remove('is-active'));
    current.link.classList.add('is-active');
    const parent = current.link.closest('ol ol')?.parentElement.querySelector(':scope > a');
    if (parent) parent.classList.add('is-active');
  }
  window.addEventListener('scroll', () => {
    if (!queued) { queued = true; requestAnimationFrame(update); }
  }, {passive: true});
  window.addEventListener('resize', update);
  update();
})();
