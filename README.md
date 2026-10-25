# Ty Fleming

A small static research website for Ty Fleming, Imaging Science PhD student at Washington University in St. Louis.

The design is a plain academic page: one serif typeface, one 720px column, modest type sizes, and plain text links. Visitors can switch between light and dark themes with the moon/sun button in the header (`theme.js`). The site follows the system setting until a visitor chooses, then remembers the choice in local storage; without JavaScript it simply follows the system setting.

## Pages

- `index.html` — introduction
- `research.html` — project overview
- `filo.html` — spatial neuroimaging methods
- `sleep.html` — high-level overview of the sleep decoding project
- `publications.html` — prior publications and ongoing work
- `about.html` — background and contact

The site uses plain HTML and CSS, plus `theme.js` for the theme toggle. `head-studies.js` draws the portrait studies on the unlinked `head-studies.html` page only.

The Sleep decoding page is a high-level overview of ongoing, unpublished work (why it matters, the approach, current focus, and status). It loads no data files; detailed methods and results will accompany a future paper.

The header shows a small line-drawn brain (top view, one fold per hemisphere) beside the name, as inline SVG in each page in the same ink as the name. The home and research overview show `assets/connectivity-matrix.svg`, a decorative motif in the style of a brain connectivity (correlation) matrix with block structure. It is not real data.

## Local preview

Run `python3 -m http.server 8000 --bind 127.0.0.1` in this directory and open `http://127.0.0.1:8000/`.

## Publishing

This repository should be named `tyfleming.github.io` and published from the root of the `main` branch through GitHub Pages. All links and assets are relative to the site root.
