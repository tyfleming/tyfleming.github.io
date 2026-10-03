# Ty Fleming

A small static research website for Ty Fleming, Imaging Science PhD student at Washington University in St. Louis.

## Pages

- `index.html` — introduction
- `research.html` — project overview
- `filo.html` — spatial neuroimaging methods
- `sleep.html` — sleep decoding workflow and probability simplex
- `publications.html` — prior publications and ongoing work
- `about.html` — background and contact

The site uses plain HTML, CSS, and one local JavaScript file. The FILO page includes paired cortical input maps from the ongoing analysis, credited in its caption.

The sleep simplex loads `assets/sleep-probabilities.json`: 9,121 subject-held-out, calibrated four-stage probability vectors from `evaluation_protocol/nested_cycle_tangent_blend/oof_probabilities.npz` on ml-sys-1. The static export has four probabilities per row and no participant, session, window, path, or observed-stage identifiers. Rows represent overlapping causal windows, so they are not independent samples. `assets/sleep-decoding-workflow.png` is the expanded technical diagram from the same remote project.

## Local preview

Run `python3 -m http.server 8000` in this directory and open `http://localhost:8000/`.

## Publishing

This repository should be named `tyfleming.github.io` and published from the root of the `main` branch through GitHub Pages. All links and assets are relative to the site root.
