"""Build the static, accessible SVG companions to sleep.html.

The representative JSON contains no subject or scan identifiers. Saved model
outputs and reconstructed intermediate tensors are identified on the page.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets/sleep-decoding-representative.json"
if not SOURCE.exists():
    raise SystemExit(
        "Local representative export is missing. See README.md; the raw tensor JSON "
        "is intentionally excluded from the public repository."
    )
DATA = json.loads(SOURCE.read_text())
SUPPLEMENT = json.loads((ROOT / "assets/sleep-decoding-method-supplement.json").read_text())
TOPOLOGY = json.loads((ROOT / "assets/sleep-cycle-atlas-topology.json").read_text())
OUT = ROOT / "assets"

INK = "#172126"
MUTED = "#5a6669"
LINE = "#d5dcda"
ACCENT = "#235969"
PAPER = "#ffffff"
NEG = "#315f82"
POS = "#ad673d"
STAGES = ["Wake", "N1", "N2", "N3"]
STAGE_COLORS = ["#b16b2e", "#9a5773", "#207a83", "#565b97"]


def interp(a: str, b: str, t: float) -> str:
    t = max(0, min(1, t))
    aa = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    bb = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(aa, bb))


def diverge(value: float, limit: float) -> str:
    ratio = max(-1, min(1, value / limit))
    return interp(PAPER, POS if ratio >= 0 else NEG, abs(ratio))


def cell_text_color(fill: str) -> str:
    """Choose a legible label color for a tinted matrix cell."""
    rgb = [int(fill[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    luminance = sum(a * b for a, b in zip(linear, (.2126, .7152, .0722)))
    white_contrast = 1.05 / (luminance + .05)
    return PAPER if white_contrast >= 4.5 else "#000000"


def toy_fill(value: float, limit: float) -> str:
    """Use stronger data hues so saturated toy-matrix cells support white labels."""
    ratio = max(-1, min(1, value / limit))
    return interp(PAPER, "#96512d" if ratio >= 0 else NEG, abs(ratio))


class SVG:
    def __init__(self, title: str, description: str):
        self.parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="740" height="300" viewBox="0 0 740 300" '
            'role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(description)}</desc>',
            '<rect width="740" height="300" fill="#ffffff"/>',
        ]

    def raw(self, value: str) -> None:
        self.parts.append(value)

    def line(self, x1, y1, x2, y2, color=LINE, width=1, opacity=1) -> None:
        self.raw(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>'
        )

    def rect(self, x, y, w, h, color, stroke=None, width=1) -> None:
        border = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        self.raw(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'fill="{color}"{border}/>'
        )

    def text(self, x, y, value, size=12, color=MUTED, weight=400, anchor="start") -> None:
        self.raw(
            f'<text x="{x:.2f}" y="{y:.2f}" fill="{color}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif">'
            f"{escape(str(value))}</text>"
        )

    def circle(self, x, y, r, fill, stroke=None, width=1) -> None:
        border = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        self.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}"{border}/>')

    def polyline(self, points, color, width=1.5) -> None:
        pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        self.raw(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}"/>')

    def header(self, label: str, right: str = "") -> None:
        self.text(24, 27, label.upper(), 11, ACCENT, 700)
        if right:
            self.text(716, 27, right, 11, MUTED, 400, "end")
        self.line(24, 39, 716, 39)

    def footer(self, value: str) -> None:
        self.line(24, 260, 716, 260)
        self.text(24, 283, value, 11, MUTED)

    def save(self, figure_id: str) -> None:
        self.raw("</svg>")
        name = f"sleep-figure-{figure_id}.svg"
        (OUT / name).write_text("\n".join(self.parts) + "\n")


def heatmap(svg: SVG, values, x, y, w, h, limit=1.0) -> None:
    rows, cols = len(values), len(values[0])
    dx, dy = w / cols, h / rows
    assert math.isclose(dx, dy, rel_tol=1e-9), "matrix cells must be square"
    for row, values_row in enumerate(values):
        for col, value in enumerate(values_row):
            svg.rect(x + col * dx, y + row * dy, dx + 0.1, dy + 0.1, diverge(value, limit))
    svg.rect(x, y, w, h, "none", LINE)


def arrow(svg: SVG, x1, y1, x2, y2, color=ACCENT, width=1.5) -> None:
    svg.line(x1, y1, x2, y2, color, width)
    angle = math.atan2(y2 - y1, x2 - x1)
    a, b = angle + 2.5, angle - 2.5
    tip = [(x2, y2), (x2 + 5 * math.cos(a), y2 + 5 * math.sin(a)),
           (x2 + 5 * math.cos(b), y2 + 5 * math.sin(b))]
    svg.raw(
        '<polygon points="' + " ".join(f"{x:.2f},{y:.2f}" for x, y in tip)
        + f'" fill="{color}"/>'
    )


def percentages(values) -> list[float]:
    """Round four probabilities to tenths while keeping their sum at 100.0%."""
    scaled = [value / sum(values) * 1000 for value in values]
    tenths = [math.floor(value) for value in scaled]
    missing = 1000 - sum(tenths)
    order = sorted(range(len(values)), key=lambda i: scaled[i] - tenths[i], reverse=True)
    for i in order[:missing]:
        tenths[i] += 1
    return [value / 10 for value in tenths]


def visual_01() -> None:
    s = SVG("Overlapping causal fMRI windows", "A schematic 35-volume timeline shows two 30-volume windows at endpoints five volumes apart. Below it, three reconstructed standardized network means and a motion-validity strip show the current representative window. The endpoint sleep label is not an input.")
    s.header("Figure 01.1 / causal window", "30 frames · 62.4 s · stride 5")
    s.text(28, 61, "WINDOW SELECTION · SCHEMATIC", 10, ACCENT, 700)
    x0, x1 = 182, 636
    dx = (x1 - x0) / 35
    s.text(163, 91, "prior t−5", 10, INK, 600, "end")
    s.text(163, 112, "current t", 10, INK, 600, "end")
    for i in range(35):
        s.rect(x0 + i * dx, 78, dx - 1.5, 9, "#e5eae8" if i < 30 else PAPER, LINE)
        s.rect(x0 + i * dx, 99, dx - 1.5, 9, ACCENT if i >= 5 else PAPER, LINE)
    s.text(x0 + 5 * dx, 128, "25 overlapping frames", 10, MUTED)
    s.text(656, 109, "endpoint", 10, ACCENT, 600)
    s.line(28, 137, 716, 137)

    features = DATA["step_1_window"]["cortical_features"]
    valid = DATA["step_1_window"]["motion_valid"]
    s.text(28, 153, "CURRENT WINDOW · RECONSTRUCTED SIGNALS", 10, ACCENT, 700)
    xx0, xx1 = 137, 636
    for center, index, color in ((175, 0, ACCENT), (207, 6, POS), (239, 12, NEG)):
        s.line(xx0, center, xx1, center, LINE)
        s.text(125, center + 4, f"mean {index + 1:02d}", 11, MUTED, 600, "end")
        pts = []
        for frame, row in enumerate(features):
            x = xx0 + frame * (xx1 - xx0) / 29
            y = center - max(-3, min(3, row[index])) * 6.5
            pts.append((x, y))
        s.polyline(pts, color, 1.8)
    s.line(xx1, 158, xx1, 247, ACCENT, 1.2)
    s.text(651, 181, "predict", 10, ACCENT, 600)
    s.text(125, 254, "FD valid", 10, MUTED, 400, "end")
    for frame, passed in enumerate(valid):
        s.rect(xx0 + frame * (xx1 - xx0) / 30, 248, (xx1 - xx0) / 30 - 1, 6,
               ACCENT if passed else POS)
    s.footer("The endpoint label scores the prediction; it is never a model input.")
    s.save("01-01")


def visual_02() -> None:
    s = SVG("Default-network residual modes", "The Default community contains 41 of the Gordon atlas's 333 cortical parcels. Each of its 41 parcel rows has a loading on each of two fold-trained residual principal components, so the basis is 41 by 2. Six numeric rows are shown; all 41 loadings of each component are separately tiled in atlas order into square-cell grids. Three reconstructed standardized held-out traces show its network mean and two residual scores across 30 frames.")
    s.header("Figure 02.4 / Default network", "41 of 333 atlas parcels → 2 residual modes")
    basis = SUPPLEMENT["network_basis"]
    assert basis["chosen_network"] == "Default" and basis["chosen_network_parcels"] == 41
    loadings = basis["top_two_loadings_in_atlas_parcel_order"]
    assert len(loadings) == 41 and all(len(row) == 2 for row in loadings)
    s.text(28, 61, "FIRST 6 OF 41 PARCELS", 10, ACCENT, 700)
    s.text(109, 82, "PC 1", 10, INK, 600, "end")
    s.text(166, 82, "PC 2", 10, INK, 600, "end")
    for i, row in enumerate(loadings[:6]):
        y = 103 + i * 22
        s.text(28, y, f"parcel {i+1:02d}", 10, MUTED)
        s.text(109, y, f"{row[0]:+.2f}", 11, INK, 600, "end")
        s.text(166, y, f"{row[1]:+.2f}", 11, INK, 600, "end")
        s.line(28, y + 5, 168, y + 5, LINE, 0.6)
    s.line(183, 53, 183, 247)
    s.text(205, 61, "41 LOADINGS PER PC", 10, ACCENT, 700)
    limit = max(abs(v) for row in loadings for v in row)
    for k, x0 in ((0, 203), (1, 271)):
        s.text(x0 + 25, 89, f"PC {k+1}", 10, INK, 600, "middle")
        for parcel, row in enumerate(loadings):
            col, grid_row = parcel % 6, parcel // 6
            s.rect(x0 + col * 8.5, 101 + grid_row * 8.5, 8, 8,
                   diverge(row[k], limit))
        s.text(x0 + 25, 178, "01 → 41", 9, MUTED, 400, "middle")
    s.text(205, 217, "tiled in atlas parcel order", 10, MUTED)
    s.text(205, 235, "each tile = one loading", 10, MUTED)
    s.line(338, 53, 338, 247)
    s.text(359, 61, "HELD-OUT OUTPUT · RECONSTRUCTED", 10, ACCENT, 700)
    features = DATA["step_1_window"]["cortical_features"]
    for center, index, name, color in ((97, 3, "mean", ACCENT), (158, 19, "PC 1", NEG), (219, 20, "PC 2", POS)):
        s.text(405, center + 4, name, 11, INK, 600, "end")
        s.line(420, center, 689, center, LINE)
        s.polyline([(420 + 269 * u / 29, center - max(-3, min(3, row[index])) * 10)
                    for u, row in enumerate(features)], color, 1.8)
    s.text(420, 248, "frame 1", 10)
    s.text(689, 248, "frame 30", 10, MUTED, 400, "end")
    s.footer("Basis rows are Default parcels; columns are two residual modes. Traces show held-out outputs.")
    s.save("02-04")


def toy_pca():
    """Four illustrative training volumes with an exactly checkable PCA fit."""
    x = [[8, 6, 3, 3], [4, 2, 7, 7], [8, 4, 7, 5], [6, 6, 5, 7]]
    means = [sum(row) / 4 for row in x]
    residuals = [[v - means[i] for v in row] for i, row in enumerate(x)]
    reference = [sum(row[j] for row in residuals) / 4 for j in range(4)]
    centered = [[v - reference[j] for j, v in enumerate(row)] for row in residuals]
    covariance = [[sum(row[i] * row[j] for row in centered) / 4
                   for j in range(4)] for i in range(4)]
    components = [[.5, .5], [.5, -.5], [-.5, .5], [-.5, -.5]]
    scores = [[sum(row[j] * components[j][k] for j in range(4))
               for k in range(2)] for row in centered]
    assert means == [5, 5, 6, 6]
    assert reference == [1, -1, 0, 0]
    assert scores == [[4, 0], [-4, 0], [0, 2], [0, -2]]
    assert all(sum(row) == 0 for row in residuals)
    assert all(sum(components[j][k] * components[j][l] for j in range(4)) == (k == l)
               for k in range(2) for l in range(2))
    assert all(abs(sum(covariance[i][j] * components[j][k] for j in range(4))
                   - (8 if k == 0 else 2) * components[i][k]) < 1e-9
               for i in range(4) for k in range(2))
    return x, means, residuals, reference, centered, covariance, components, scores


def toy_matrix(s, label, values, x0, y0, cell_size=30, fmt=str,
               tint=False, show_shape=True):
    s.text(x0, y0 - 13, label, 11, ACCENT, 700)
    rows, cols = len(values), len(values[0])
    for i, row in enumerate(values):
        for j, value in enumerate(row):
            left, top = x0 + j * cell_size, y0 + i * cell_size
            fill = toy_fill(value, max(abs(v) for r in values for v in r)) if tint else PAPER
            s.rect(left, top, cell_size - 3, cell_size - 3, fill, LINE, .8)
            s.text(left + (cell_size - 3) / 2, top + cell_size / 2 + 4,
                   fmt(value), 11, cell_text_color(fill) if tint else INK, 600, "middle")
    if show_shape:
        s.text(x0 + cols * cell_size / 2 - 2, y0 + rows * cell_size + 17,
               f"{rows} × {cols}", 10, MUTED, 400, "middle")


def visual_parcel_projection() -> None:
    x, means, residuals, _, _, _, _, _ = toy_pca()
    s = SVG("Same-volume parcel mean subtraction",
            "Illustrative four-volume, four-parcel matrix. Each row's four parcel values are averaged. Subtracting that row's own mean from all four values produces residuals that sum to zero. In the first row, 8, 6, 3, 3 have mean 5 and residuals 3, 1, minus 2, minus 2.")
    s.header("Figure 02.1 / where residuals come from", "illustrative · 4 volumes × 4 parcels")
    toy_matrix(s, "X · measured parcel values", x, 28, 91, 34, show_shape=False)
    arrow(s, 182, 159, 229, 159)
    toy_matrix(s, "m · same-volume mean", [[v] for v in means], 253, 91, 34,
               fmt=lambda v: f"{v:g}", show_shape=False)
    arrow(s, 306, 159, 365, 159)
    toy_matrix(s, "E · parcel residuals", residuals, 391, 91, 34,
               fmt=lambda v: f"{v:+g}" if v else "0", tint=True, show_shape=False)
    s.text(28, 246, "First volume", 11, ACCENT, 700)
    s.text(109, 246, "(8, 6, 3, 3) − (5, 5, 5, 5) = (3, 1, −2, −2)", 12, INK)
    s.footer("The network mean is recalculated at each volume; every residual row sums to zero.")
    s.save("02-01")


def visual_toy_pca_fit() -> None:
    _, _, residuals, reference, centered, covariance, components, _ = toy_pca()
    s = SVG("How training residuals determine PCA components",
            "Illustrative training calculation for four volumes and four parcels. The training residual mean is [1, minus 1, 0, 0]. Subtracting this reference from each residual row gives centered patterns [2, 2, minus 2, minus 2], [minus 2, minus 2, 2, 2], [1, minus 1, 1, minus 1], and [minus 1, 1, minus 1, 1]. Their covariance is C transpose C divided by four. Its two leading eigenvectors form a four-by-two component matrix, with eigenvalues 8 and 2.")
    s.header("Figure 02.2 / fit the residual modes", "illustrative training calculation")
    s.text(28, 64, "TRAINING REFERENCE", 10, ACCENT, 700)
    s.text(28, 83, "μ = mean of residual rows = (1, −1, 0, 0)", 12, INK)
    toy_matrix(s, "E − μ · centered training patterns", centered, 28, 112, 29,
               fmt=lambda v: f"{v:+g}" if v else "0", tint=True)
    s.text(192, 166, "CᵀC / 4", 11, MUTED, 600, "middle")
    arrow(s, 176, 173, 215, 173)
    toy_matrix(s, "K · parcel covariance", covariance, 239, 112, 29,
               fmt=lambda v: f"{v:g}", tint=True)
    s.text(424, 166, "top 2", 11, MUTED, 600, "middle")
    arrow(s, 403, 173, 453, 173)
    toy_matrix(s, "U · learned components", components, 480, 112, 29,
               fmt=lambda v: f"{v:+.1f}", tint=True)
    s.text(598, 133, "PC 1", 11, NEG, 700)
    s.text(598, 153, "(+,+,−,−)", 11, INK)
    s.text(598, 181, "PC 2", 11, POS, 700)
    s.text(598, 201, "(+,−,+,−)", 11, INK)
    s.text(598, 230, "λ₁ = 8 · λ₂ = 2", 11, MUTED)
    s.footer("PCA directions are fitted to training residuals after subtracting their parcel-wise reference.")
    s.save("02-02")


def visual_toy_pca_scores() -> None:
    _, _, _, _, centered, _, components, scores = toy_pca()
    s = SVG("One volume becomes one PCA point",
            "Illustrative PCA projection for volume one only. Its centered parcel residuals are [2, 2, minus 2, minus 2]. The fitted PC1 weights are [0.5, 0.5, minus 0.5, minus 0.5], giving score 4. The fitted PC2 weights are [0.5, minus 0.5, 0.5, minus 0.5], giving score zero. One point at horizontal PC1 coordinate 4 and vertical PC2 coordinate zero represents this one volume; the other three training volumes are intentionally omitted.")
    s.header("Figure 02.3 / one volume → one point", "illustrative · fitted weights stay fixed")
    s.text(28, 67, "VOLUME 1 · CENTERED RESIDUAL", 10, ACCENT, 700)
    s.text(28, 99, "e − μ", 11, INK, 600)
    for j, value in enumerate(centered[0]):
        fill = toy_fill(value, 2)
        x = 124 + 38 * j
        s.rect(x, 79, 34, 34, fill, LINE, .8)
        s.text(x + 17, 101, f"{value:+g}", 11, cell_text_color(fill), 700, "middle")
    s.text(28, 133, "FITTED PARCEL WEIGHTS", 10, ACCENT, 700)
    for k, y in ((0, 143), (1, 196)):
        s.text(28, y + 19, f"PC {k+1}", 11, NEG if k == 0 else POS, 700)
        for j in range(4):
            value = components[j][k]
            fill = toy_fill(value, .5)
            x = 124 + 38 * j
            s.rect(x, y, 34, 34, fill, LINE, .8)
            s.text(x + 17, y + 22, f"{value:+.1f}", 11, cell_text_color(fill), 700, "middle")
        s.text(340, y + 19, f"dot = {scores[0][k]:g}", 12, INK, 700)
    s.line(430, 56, 430, 249)
    s.text(456, 67, "ONE VOLUME · ONE POINT", 10, ACCENT, 700)
    ox, oy = 548, 170
    arrow(s, 458, oy, 700, oy, MUTED, 1.2)
    arrow(s, ox, 222, ox, 87, MUTED, 1.2)
    s.text(704, oy - 9, "PC 1", 11, NEG, 700, "end")
    s.text(ox + 10, 91, "PC 2", 11, POS, 700)
    s.text(ox - 8, oy + 18, "0", 10, MUTED, 400, "end")
    s.line(671, oy - 6, 671, oy + 6, ACCENT, 1.2)
    s.circle(671, oy, 7, ACCENT, PAPER, 1)
    s.text(671, 145, "(+4, 0)", 12, INK, 700, "middle")
    s.text(671, 204, "volume 1", 11, MUTED, 600, "middle")
    s.text(456, 232, "PC 2 = 0: no vertical displacement", 10, MUTED)
    s.footer("Each new volume uses these same fitted weights and receives its own two-score point.")
    s.save("02-03")


def visual_03() -> None:
    s = SVG("Shrinkage connectivity from a short window", "Six selected features from the full 39-feature operation show sample covariance, reconstructed Ledoit-Wolf shrinkage covariance, and final correlation. The saved shrinkage fraction for this window is 0.1511; eigenvalue flooring made no change.")
    s.header("Figure 03.2 / connectivity matrices", "24–30 valid rows · 39 features")
    features = DATA["step_1_window"]["cortical_features"]
    valid = DATA["step_1_window"]["motion_valid"]
    selected = [row for row, ok in zip(features, valid) if ok]
    assert len(selected) == SUPPLEMENT["window_shrinkage_connectivity"]["valid_feature_rows"]
    indices = SUPPLEMENT["window_shrinkage_connectivity"]["subset_feature_indices"]
    means = [sum(row[j] for row in selected) / len(selected) for j in indices]
    sample = [[sum((row[i] - means[a]) * (row[j] - means[b]) for row in selected) / len(selected)
               for b, j in enumerate(indices)] for a, i in enumerate(indices)]
    w = SUPPLEMENT["window_shrinkage_connectivity"]
    shrink = w["ledoit_wolf_covariance_subset"]
    corr = w["stabilized_correlation_subset"]
    limit = max(abs(v) for matrix in (sample, shrink) for row in matrix for v in row)
    for x, matrix, label, sublabel, scale in (
        (38, sample, "sample covariance", "S · 30 valid frames", limit),
        (282, shrink, "shrinkage covariance", "(1−λ)S + λμI", limit),
        (526, corr, "correlation state", "D⁻¹/² Σ D⁻¹/²", 1),
    ):
        s.text(x + 86, 67, label, 12, INK, 600, "middle")
        heatmap(s, matrix, x + 18, 82, 136, 136, scale)
        s.text(x + 86, 239, sublabel, 11, MUTED, 400, "middle")
    arrow(s, 208, 151, 270, 151)
    arrow(s, 452, 151, 514, 151)
    s.text(239, 133, f"λ={w['ledoit_wolf_shrinkage']:.3f}", 10, ACCENT, 600, "middle")
    s.text(483, 133, "normalize", 10, ACCENT, 600, "middle")
    s.footer("6 selected channels from full 39 × 39 matrices; eigenvalue flooring did not alter this window.")
    s.save("03-02")


def symmetric_eigenvalues(matrix: list[list[float]]) -> list[float]:
    """Jacobi eigenvalues for a small real symmetric matrix; no third-party runtime."""
    a = [row[:] for row in matrix]
    n = len(a)
    for _ in range(50):
        largest = 0.0
        for p in range(n - 1):
            for q in range(p + 1, n):
                v = a[p][q]
                largest = max(largest, abs(v))
                if abs(v) < 1e-12:
                    continue
                tau = (a[q][q] - a[p][p]) / (2 * v)
                t = (1 if tau >= 0 else -1) / (abs(tau) + math.sqrt(1 + tau * tau))
                c = 1 / math.sqrt(1 + t * t)
                sn = t * c
                app, aqq = a[p][p], a[q][q]
                a[p][p], a[q][q] = app - t * v, aqq + t * v
                a[p][q] = a[q][p] = 0.0
                for k in range(n):
                    if k != p and k != q:
                        akp, akq = a[k][p], a[k][q]
                        a[k][p] = a[p][k] = c * akp - sn * akq
                        a[k][q] = a[q][k] = sn * akp + c * akq
        if largest < 1e-10:
            break
    return sorted((a[i][i] for i in range(n)), reverse=True)


def visual_shrinkage_spectrum() -> None:
    s = SVG("Shrinkage lifts the zero eigenvalues of a short-window covariance", "An eigenvalue spectrum reconstructed from this 30-valid-frame, 39-signal window compares sample covariance with its actual Ledoit-Wolf shrinkage covariance. The ordinary sample matrix has ten near-zero eigenvalues; shrinkage makes every eigenvalue positive.")
    s.header("Figure 03.1 / why shrinkage", "30 valid frames · 39 channels")
    rows = [row for row, valid in zip(DATA["step_1_window"]["cortical_features"],
                                    DATA["step_1_window"]["motion_valid"]) if valid]
    n, d = len(rows), len(rows[0])
    means = [sum(row[j] for row in rows) / n for j in range(d)]
    covariance = [[sum((row[i] - means[i]) * (row[j] - means[j]) for row in rows) / n
                   for j in range(d)] for i in range(d)]
    sample = symmetric_eigenvalues(covariance)
    assert sum(abs(value) < 1e-7 for value in sample) == 10
    lam = SUPPLEMENT["window_shrinkage_connectivity"]["ledoit_wolf_shrinkage"]
    mu = sum(covariance[i][i] for i in range(d)) / d
    shrunk = [(1 - lam) * value + lam * mu for value in sample]
    assert min(shrunk) > 0
    s.text(28, 62, "COVARIANCE EIGENVALUE · LOG SCALE", 10, ACCENT, 700)
    x0, x1, y0, y1 = 113, 685, 81, 218
    ceiling = 10 ** math.ceil(math.log10(max(sample[0], shrunk[0])))
    floor = 1e-8
    def yy(value: float) -> float:
        return y1 - (math.log10(max(floor, value)) - math.log10(floor)) / (math.log10(ceiling) - math.log10(floor)) * (y1 - y0)
    s.rect(x0 + 29 * (x1 - x0) / 38, y0, x1 - (x0 + 29 * (x1 - x0) / 38), y1 - y0, "#f3f5f4")
    for tick in (1e-8, 1e-6, 1e-4, 0.01, 1, 10):
        if tick <= ceiling:
            y = yy(tick)
            s.line(x0, y, x1, y, LINE, 0.8)
            s.text(100, y + 4, f"{tick:g}", 10, MUTED, 400, "end")
    s.line(x0, y0, x0, y1, INK)
    s.line(x0, y1, x1, y1, INK)
    for rank in (1, 10, 20, 30, 39):
        x = x0 + (rank - 1) * (x1 - x0) / 38
        s.text(x, 234, str(rank), 10, MUTED, 400, "middle")
    s.text(685, 249, "eigenvalue rank", 10, MUTED, 400, "end")
    s.text(604, 99, "10 null directions", 10, MUTED, 600, "middle")
    for values, color in ((sample, NEG), (shrunk, POS)):
        s.polyline([(x0 + i * (x1 - x0) / 38, yy(value)) for i, value in enumerate(values)], color, 2.2)
    s.rect(366, 53, 11, 4, NEG)
    s.text(382, 61, "sample: 10 near zero", 10, INK)
    s.rect(533, 53, 11, 4, POS)
    s.text(549, 61, f"shrinkage: λ = {lam:.3f}", 10, INK)
    s.footer("A 30-row sample has at most 29 independent directions; shrinkage lifts the null directions.")
    s.save("03-01")


def visual_04() -> None:
    s = SVG("Lag-specific tangent references", "At each of the current, 25-volume, and 50-volume lags, a reconstructed correlation is compared with its reconstructed fold-trained reference to produce a tangent matrix. Six-by-six excerpts are shown from the full 39-by-39 matrices. All three tangents become 2340 coordinates, clipped and reduced to 64 whitened PCA scores.")
    s.header("Figure 04.1 / tangent representation", "3 × 780 → 2,340 → 64")
    records = SUPPLEMENT["lag_geometry"]["lag_records"]
    indices = SUPPLEMENT["lag_geometry"]["subset_feature_indices"]
    matrices = DATA["step_3_causal_lags"]["correlations"]
    xs = (94, 263, 432)
    for col, (x, rec, matrix) in enumerate(zip(xs, records, matrices)):
        s.text(x + 47, 61, ("now", "−25 volumes", "−50 volumes")[col], 11, INK, 600, "middle")
        snippets = ([[matrix[i][j] for j in indices] for i in indices],
                    rec["reference_subset"], rec["tangent_subset"])
        for y, subset, limit in zip((78, 134, 190), snippets, (1, 1, 1)):
            heatmap(s, subset, x + 11, y, 47, 47, limit)
        s.text(x + 69, 105, "state", 10, MUTED)
        s.text(x + 69, 161, "training", 10, MUTED)
        s.text(x + 69, 217, "log map", 10, MUTED)
    for y, label in ((106, "C state"), (162, "G reference"), (218, "T tangent")):
        s.text(24, y, label, 10, ACCENT, 600)
    s.line(580, 53, 580, 248)
    s.text(648, 61, "PCA OUTPUT", 10, ACCENT, 700, "middle")
    scores = DATA["step_5_pca"]["whitened_score"]
    for i, value in enumerate(scores):
        col, row = i % 8, i // 8
        s.rect(592 + col * 14, 84 + row * 14, 12, 12, diverge(value, 2.5))
    s.rect(592, 84, 8 * 14, 8 * 14, "none", LINE)
    s.text(648, 226, "64 whitened scores", 10, MUTED, 400, "middle")
    s.footer("Each C, G, T image shows the same 6 channels from a full 39 × 39 matrix; T uses all 39.")
    s.save("04-01")


def visual_05() -> None:
    s = SVG("Tangent decoder and temperature calibration", "The reconstructed 64 whitened tangent scores enter shrinkage LDA. Saved uncalibrated and calibrated stage probabilities are compared directly. The fitted tangent temperature is 2.114, softening this representative prediction.")
    s.header("Figure 05.1 / tangent decoder", "64 features → four probabilities")
    p = SUPPLEMENT["probability_calibration"]
    scores = DATA["step_5_pca"]["whitened_score"]
    s.text(93, 62, "64 PCA SCORES", 10, ACCENT, 700, "middle")
    for i, value in enumerate(scores):
        col, row = i % 8, i // 8
        s.rect(37 + col * 14, 89 + row * 14, 12, 12, diverge(value, 2.5))
    s.rect(37, 89, 8 * 14, 8 * 14, "none", LINE)
    s.text(93, 222, "reconstructed", 10, MUTED, 400, "middle")
    arrow(s, 162, 143, 197, 143)
    s.text(244, 121, "SHRINKAGE", 10, ACCENT, 700, "middle")
    s.text(244, 143, "LDA", 17, INK, 600, "middle")
    s.text(244, 165, "equal priors", 10, MUTED, 400, "middle")
    arrow(s, 288, 143, 323, 143)
    s.line(458, 54, 458, 246)
    s.text(351, 62, "RAW · SAVED", 10, ACCENT, 700)
    s.text(478, 62, f"CALIBRATED · T = {p['tangent_temperature']:.3f}", 10, ACCENT, 700)
    for i, name in enumerate(STAGES):
        y = 83 + i * 40
        raw = p["tangent_raw_probability"][i]
        calibrated = p["tangent_calibrated_probability"][i]
        s.text(339, y + 13, name, 11, INK, 600)
        s.rect(375, y + 2, 57, 13, "#eff3f2")
        s.rect(375, y + 2, max(1, 57 * raw), 13, STAGE_COLORS[i])
        raw_label = "<0.1%" if 0 < raw < 0.0005 else f"{raw * 100:.1f}%"
        s.text(438, y + 30, raw_label, 10, MUTED, 400, "end")
        s.text(485, y + 13, name, 11, INK, 600)
        s.rect(521, y + 2, 129, 13, "#eff3f2")
        s.rect(521, y + 2, max(1, 129 * calibrated), 13, STAGE_COLORS[i])
        s.text(697, y + 14, f"{calibrated * 100:.1f}%", 11, INK, 600, "end")
    s.footer("Temperature softens this window's LDA output; both probability columns are saved model outputs.")
    s.save("05-01")


def visual_06() -> None:
    s = SVG("Lagged edge flow and Hodge energy", "At left, schematic forward and reverse cross-lag parcel interactions define one antisymmetric edge flow. At right, saved harmonic, gradient, and curl energy fractions from the representative window are shown for three lags and their pooled flow, followed by the three saved temporal change features.")
    s.header("Figure 06.2 / directed-cycle branch", "333 parcel signals · 23 energy-family features")
    s.text(28, 62, "ONE EDGE · SCHEMATIC CROSS-LAG PAIRS", 10, ACCENT, 700)
    for y, left, right, color, label in (
        (101, "i at u", "j at u + τ", POS, "forward"),
        (151, "j at u", "i at u + τ", NEG, "reverse"),
    ):
        s.circle(47, y - 4, 5, PAPER, color, 2)
        s.text(60, y, left, 11, INK, 600)
        arrow(s, 116, y - 4, 213, y - 4, color, 2)
        s.circle(224, y - 4, 5, PAPER, color, 2)
        s.text(237, y, right, 11, INK, 600)
        s.text(169, y - 15, label, 10, MUTED, 400, "middle")
    s.line(28, 173, 324, 173)
    s.text(28, 198, "edge flow = forward − reverse", 12, INK, 600)
    s.text(28, 221, "τ = 1, 2, 3 volumes; valid pairs only", 10, MUTED)
    s.text(28, 244, "Then project flow onto H, G, and C spaces.", 10, MUTED)
    s.line(341, 52, 341, 250)

    values = DATA["step_7_cycle_ridge"]["feature_values"]
    s.text(362, 62, "HODGE ENERGY SHARES · SAVED", 10, ACCENT, 700)
    components = (("H harmonic", NEG), ("G gradient", ACCENT), ("C curl", POS))
    for i, (name, color) in enumerate(components):
        x = 362 + i * 117
        s.rect(x, 76, 9, 9, color)
        s.text(x + 15, 84, name, 10, INK, 500)
    for row, name in enumerate(("lag 1", "lag 2", "lag 3", "pooled")):
        y = 107 + row * 31
        s.text(406, y + 11, name, 11, INK, 600, "end")
        fractions = values[row * 5 + 2:row * 5 + 5]
        total = sum(fractions)
        cursor = 422
        for fraction, (_, color) in zip(fractions, components):
            width = 258 * fraction / total
            s.rect(cursor, y, width, 15, color)
            cursor += width
        s.text(702, y + 11, "100%", 10, MUTED)
    s.line(362, 231, 716, 231)
    s.text(362, 249, f"Δ norm {values[20]:.2f}   ·   cosine {values[21]:.2f}   ·   angle {values[22]:.2f} rad", 10, INK)
    s.footer("Five flow summaries at each lag + five pooled + three temporal summaries = 23.")
    s.save("06-02")


def visual_atlas_graph() -> None:
    s = SVG("Actual cortical atlas graph used for signed edge flows", "All 333 Gordon cortical parcels and all 1152 actual undirected six-nearest-neighbor graph edges are shown in a two-dimensional projection of public MNI atlas coordinates. Default-network nodes are highlighted. Neighbor selection was performed in original three-dimensional coordinate space; directionality enters only when lagged signal flow is assigned to edges.")
    s.header("Figure 06.1 / atlas graph", "actual topology · equal-axis 2D display")
    assert TOPOLOGY["topology"]["nodes"] == 333
    assert TOPOLOGY["topology"]["edges"] == 1152
    assert TOPOLOGY["topology"]["triangles"] == 986
    points = TOPOLOGY["node_xy"]
    networks = TOPOLOGY["node_network"]
    edges = TOPOLOGY["edges"]
    assert len(points) == len(networks) == 333 and len(edges) == 1152
    default_index = TOPOLOGY["network_names"].index("Default")
    def xy(i: int) -> tuple[float, float]:
        px, py = points[i]
        return 250 + px * 125, 150 - py * 125
    for i, j in edges:
        s.line(*xy(i), *xy(j), LINE, 0.48, 0.78)
    for i in range(333):
        x, y = xy(i)
        s.circle(x, y, 2.0 if networks[i] == default_index else 1.15,
                 POS if networks[i] == default_index else ACCENT)
    s.line(469, 53, 469, 248)
    s.text(491, 64, "FIXED GRAPH CONSTRUCTION", 10, ACCENT, 700)
    for y, quantity, label in ((95, "333", "cortical parcels"),
                               (134, "6", "nearest neighbors in 3D"),
                               (173, "1,152", "undirected edges"),
                               (212, "986", "filled triangles")):
        s.text(491, y, quantity, 20, INK, 600)
        s.text(568, y, label, 11, MUTED)
    s.rect(491, 231, 9, 9, POS)
    s.text(507, 239, "Default network highlighted", 10, INK)
    s.footer("Graph edges are undirected; the later cross-lag calculation assigns signed flow to them.")
    s.save("06-01")


def visual_cycle_feature_map() -> None:
    s = SVG("The 23 saved cycle features", "A compact numerical map of all 23 saved directed-cycle features for the representative window: five flow summaries at each of three lags, five for their weighted pooled flow, and three temporal change summaries.")
    s.header("Figure 06.3 / cycle feature vector", "15 lag + 5 pooled + 3 temporal = 23")
    values = DATA["step_7_cycle_ridge"]["feature_values"]
    columns = (("total norm", ACCENT), ("harmonic norm", NEG),
               ("H share", NEG), ("G share", ACCENT), ("C share", POS))
    for j, (label, color) in enumerate(columns):
        x = 145 + j * 111
        s.rect(x, 57, 10, 3, color)
        s.text(x, 76, label, 10, INK, 600)
    for i, label in enumerate(("lag 1", "lag 2", "lag 3", "pooled")):
        y = 90 + i * 35
        s.text(28, y + 18, label, 11, INK, 600)
        for j in range(5):
            x = 145 + j * 111
            s.rect(x, y, 96, 29, PAPER, LINE)
            value = values[i * 5 + j]
            displayed = f"{value * 100:.1f}%" if j >= 2 else f"{value:.2f}"
            s.text(x + 48, y + 19, displayed, 13, INK, 600, "middle")
    s.line(28, 235, 716, 235)
    s.text(28, 252, f"change in pooled harmonic state: norm {values[20]:.2f}   ·   cosine {values[21]:.2f}   ·   angle {values[22]:.2f} rad", 10, INK)
    s.footer("Numbers are saved outputs for one held-out window; shares are fractions of total flow energy.")
    s.save("06-03")


def visual_cycle_calibration() -> None:
    s = SVG("Cycle branch before and after calibration", "The same representative held-out window has saved raw and calibrated Wake, N1, N2, and N3 cycle-branch probabilities. The fitted cycle temperature is 0.888, which modestly sharpens these probabilities.")
    p = SUPPLEMENT["probability_calibration"]
    raw, calibrated = p["cycle_raw_probability"], p["cycle_calibrated_probability"]
    temperature = p["cycle_temperature"]
    s.header("Figure 06.4 / cycle calibration", "23 features → four probabilities")
    s.text(28, 64, "CLASS-BALANCED LOGISTIC OUTPUT", 10, ACCENT, 700)
    s.text(198, 93, "RAW · SAVED", 10, ACCENT, 700, "middle")
    s.text(535, 93, f"CALIBRATED · T = {temperature:.3f}", 10, ACCENT, 700, "middle")
    for i, (stage, before, after) in enumerate(zip(STAGES, raw, calibrated)):
        y = 109 + i * 34
        s.text(72, y + 12, stage, 11, INK, 600, "end")
        s.rect(88, y, 164, 14, "#eff3f2")
        s.rect(88, y, max(1, 164 * before), 14, STAGE_COLORS[i])
        s.text(267, y + 12, f"{before * 100:.1f}%", 11, INK, 600, "end")
        s.text(401, y + 12, stage, 11, INK, 600, "end")
        s.rect(419, y, 164, 14, "#eff3f2")
        s.rect(419, y, max(1, 164 * after), 14, STAGE_COLORS[i])
        s.text(618, y + 12, f"{after * 100:.1f}%", 11, INK, 600, "end")
    arrow(s, 287, 172, 366, 172, ACCENT, 2)
    s.text(326, 151, "temperature", 10, MUTED, 400, "middle")
    s.footer("This branch uses parcel-level directed flow; calibration precedes the final blend.")
    s.save("06-04")


def visual_07() -> None:
    s = SVG("Weighted blend then final calibration", "Saved tangent, cycle, and final four-stage probability vectors, with a derived pre-temperature weighted mixture for the same window. The cycle weight is 0.30.")
    alpha = DATA["step_8_blend_simplex"]["cycle_weight"]
    tangent = DATA["step_6_tangent_lda"]["probability"]
    cycle = DATA["step_7_cycle_ridge"]["probability"]
    mix = [(1 - alpha) * a + alpha * b for a, b in zip(tangent, cycle)]
    final = DATA["step_8_blend_simplex"]["final_probability"]
    s.header("Figure 07.1 / probability blend", f"cycle weight α = {alpha:.2f}")
    for i, name in enumerate(STAGES):
        s.text(219 + i * 124, 60, name, 11, INK, 600, "middle")
    rows = [
        ("tangent", tangent, "saved"),
        ("cycle", cycle, "saved"),
        ("mix q", mix, "derived"),
        ("final p", final, "saved"),
    ]
    for row, (name, probabilities, source) in enumerate(rows):
        y = 75 + row * 45
        s.text(118, y + 12, name, 12, INK, 600, "end")
        s.text(118, y + 27, source, 9, MUTED, 400, "end")
        displayed = percentages(probabilities)
        for col, value in enumerate(probabilities):
            x = 168 + col * 124
            s.rect(x, y, 97, 12, "#eff3f2")
            s.rect(x, y, max(1, 97 * value), 12, STAGE_COLORS[col])
            s.text(x + 97, y + 29, f"{displayed[col]:.1f}%", 10, INK, 400, "end")
    s.footer(f"The mix is derived at α = 0.30; the saved final row uses T = {SUPPLEMENT['probability_calibration']['final_blend_temperature']:.3f}.")
    s.save("07-01")


def validate() -> None:
    assert DATA["stages"] == STAGES
    features = DATA["step_1_window"]["cortical_features"]
    assert len(features) == 30 and all(len(row) == 39 for row in features)
    assert len(DATA["step_1_window"]["motion_valid"]) == 30
    matrices = DATA["step_3_causal_lags"]["correlations"]
    assert len(matrices) == 3 and all(len(m) == 39 and all(len(row) == 39 for row in m) for m in matrices)
    for probabilities in [
        DATA["step_6_tangent_lda"]["probability"],
        DATA["step_7_cycle_ridge"]["probability"],
        DATA["step_8_blend_simplex"]["final_probability"],
    ]:
        assert len(probabilities) == 4 and abs(sum(probabilities) - 1) < 1e-4
    p = SUPPLEMENT["probability_calibration"]
    for name in ("tangent_raw_probability", "tangent_calibrated_probability",
                 "cycle_raw_probability", "cycle_calibrated_probability",
                 "pre_final_temperature_blend", "final_probability"):
        assert len(p[name]) == 4 and abs(sum(p[name]) - 1) < 1e-4
    for source, target in ((DATA["step_6_tangent_lda"]["probability"], p["tangent_calibrated_probability"]),
                           (DATA["step_7_cycle_ridge"]["probability"], p["cycle_calibrated_probability"]),
                           (DATA["step_8_blend_simplex"]["final_probability"], p["final_probability"])):
        assert max(abs(a - b) for a, b in zip(source, target)) < 1e-5
    assert p["stage_order"] == STAGES
    assert TOPOLOGY["privacy"]["participant_or_scan_data_included"] is False
    assert TOPOLOGY["privacy"]["sleep_labels_or_probabilities_included"] is False
    assert SUPPLEMENT["privacy"] == {
        "participant_scan_time_or_label_fields_included": False,
        "raw_333_parcel_series_included": False,
        "performance_metrics_included": False,
    }


if __name__ == "__main__":
    validate()
    for fn in (visual_01, visual_02, visual_03, visual_04,
               visual_05, visual_06, visual_07):
        fn()
    for fn in (visual_parcel_projection, visual_toy_pca_fit, visual_toy_pca_scores,
               visual_shrinkage_spectrum, visual_atlas_graph,
               visual_cycle_feature_map, visual_cycle_calibration):
        fn()
    print("Built fourteen sleep-method SVGs from the validated representative export and atlas topology.")
