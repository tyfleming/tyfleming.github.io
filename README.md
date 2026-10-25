# Ty Fleming

A small static research website for Ty Fleming, Imaging Science PhD student at Washington University in St. Louis.

The design is a plain academic page: one serif typeface, one 720px column, modest type sizes, and plain text links. The Sleep decoding page uses the same layout in dark colors (`<html data-theme="night">`). To make another page dark, give it `<html data-theme="night">`.

## Pages

- `index.html` — introduction
- `research.html` — project overview
- `filo.html` — spatial neuroimaging methods
- `sleep.html` — high-level overview of the sleep decoding project
- `publications.html` — prior publications and ongoing work
- `about.html` — background and contact

The site uses plain HTML and CSS. `head-studies.js` draws the portrait studies on the unlinked `head-studies.html` page only.

The Sleep decoding page is a high-level overview of ongoing, unpublished work (why it matters, the approach, current focus, and status). It loads no data files; detailed methods and results will accompany a future paper.

The home and research overview show `assets/connectivity-matrix.svg`, a decorative motif in the style of a brain connectivity (correlation) matrix with block structure. It is not real data.

## Local preview

Run `python3 -m http.server 8000 --bind 127.0.0.1` in this directory and open `http://127.0.0.1:8000/`.

## Publishing

This repository should be named `tyfleming.github.io` and published from the root of the `main` branch through GitHub Pages. All links and assets are relative to the site root.
