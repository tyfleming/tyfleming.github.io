# Ty Fleming

A small static research website for Ty Fleming, Imaging Science PhD student at Washington University in St. Louis.

This branch (`variant/sleep-night`) uses the light minimal theme across the site and switches the Sleep decoding page to the Night Oracle theme with `<html data-theme="night">`: ivory serif headings, moon-gold accents, tarot-style framing, and star-marked section dividers. Links into the sleep research are drawn as small night cards on the light pages. Crossing between day and night pages plays a sky transition (`sky.js`): entering the sleep page, the night page descends over the day page behind a soft edge while the day page dims (dusk); leaving it, the day page rises from the bottom (dawn). Browsers with cross-document view transitions animate the real pages in one motion (including back/forward where the Navigation API is available); others get a matching soft-edged curtain. Nothing plays for visitors who prefer reduced motion. Other navigations cross-fade (`@view-transition`). Add a page to `NIGHT_PAGES` in `sky.js` and give it `<html data-theme="night">` to make it a night page. The night stage palette is re-stepped for the dark surface and passes the same color-vision checks (Wake `#c38824`, N1 `#b24f63`, N2 `#6453a7`, N3 `#359bd9`). The all-light theme lives on `variant/minimal-modern` and the all-night theme on `variant/night-oracle`.

## Pages

- `index.html` — introduction
- `research.html` — project overview
- `filo.html` — spatial neuroimaging methods
- `sleep.html` — high-level overview of the sleep decoding project
- `publications.html` — prior publications and ongoing work
- `about.html` — background and contact

The site uses plain HTML and CSS, with local JavaScript for the sleep page’s “On this page” index (`toc.js`). `head-studies.js` draws the portrait studies on the unlinked `head-studies.html` page only.

The Sleep decoding page is a high-level overview of ongoing, unpublished work (why it matters, the approach, current focus, and status). It loads no data files; detailed methods and results will accompany a future paper.

The home and research overview show `assets/connectivity-matrix.svg`, a decorative motif in the style of a brain connectivity (correlation) matrix with block structure. It is not real data.

## Local preview

Run `python3 -m http.server 8000 --bind 127.0.0.1` in this directory and open `http://127.0.0.1:8000/`.

## Publishing

This repository should be named `tyfleming.github.io` and published from the root of the `main` branch through GitHub Pages. All links and assets are relative to the site root.
