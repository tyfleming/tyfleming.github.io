# Ty Fleming

A small static research website for Ty Fleming, Imaging Science PhD student at Washington University in St. Louis.

## Pages

- `index.html` — introduction
- `research.html` — project overview
- `filo.html` — spatial neuroimaging methods
- `sleep.html` — sleep decoding workflow and probability simplex
- `publications.html` — prior publications and ongoing work
- `about.html` — background and contact

The site uses plain HTML and CSS, local JavaScript for the simplex and math rendering, and a pinned KaTeX release for the sleep equations. The FILO page includes paired cortical input maps from the ongoing analysis, credited in its caption.

The sleep simplex loads `assets/sleep-probabilities.json`: 9,121 subject-held-out, calibrated four-stage probability vectors from `evaluation_protocol/nested_cycle_tangent_blend/oof_probabilities.npz` on ml-sys-1. The static export has four probabilities per row and no participant, session, window, path, or observed-stage identifiers. Rows represent overlapping causal windows, so they are not independent samples. `assets/sleep-decoding-workflow.png` is the expanded technical diagram from the same remote project.

The simplex also loads `assets/sleep-ground-truth.json` with `schema_version: 1`, the same four `stages`, `probabilities_sha256` matching the exact bytes of the probability JSON, and one integer `labels` value (0–3) per row. When validated, the page exposes a prediction/observed-stage color toggle and shows both labels in the readout. The observed labels were checked row-for-row against the saved experiment before export. The public sidecar contains only stage codes and the probability-file checksum; no participant, session, or window identifiers are included. Rows are grouped by participant and ordered by time within participant, so this public per-window pairing may reveal sleep architecture despite omitted identifiers; it was published with Ty Fleming’s explicit approval.

The eight published SVG method panels were generated with `python3 scripts/build_sleep_visuals.py` from a local representative tensor export that is excluded from this public repository. Cycle features and probabilities are saved model outputs; cortical signals, SPD matrices, tangent features, and PCA scores are deterministic reconstructions using that held-out fold's frozen transforms. The first visual uses three reconstructed network means from the 30 × 39 feature window because raw 333-parcel time courses were not exported. The sample correlation in step 03 and the pre-temperature blend in step 07 are derived from that representative window. Parcel-to-residual, LDA-score, and graph-flow sketches explain operations rather than depict saved intermediate data; they are labeled schematic on the page. The graph sketches do not depict atlas locations. To regenerate the panels, place the approved local export at `assets/sleep-decoding-representative.json` and run the script.

## Local preview

Run `python3 -m http.server 8000` in this directory and open `http://localhost:8000/`.

## Publishing

This repository should be named `tyfleming.github.io` and published from the root of the `main` branch through GitHub Pages. All links and assets are relative to the site root.
