"""Build the eight static, accessible SVG companions to sleep.html.

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

    def save(self, number: int) -> None:
        self.raw("</svg>")
        (OUT / f"sleep-step-{number:02d}.svg").write_text("\n".join(self.parts) + "\n")


def heatmap(svg: SVG, values, x, y, w, h, limit=1.0) -> None:
    rows, cols = len(values), len(values[0])
    dx, dy = w / cols, h / rows
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
    s.header("01 / causal window", "30 frames · 62.4 s · stride 5")
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
    s.save(1)


def visual_02() -> None:
    s = SVG("Fold-fitted residual modes", "For the Default network, 41 parcels are mean-centered at each volume, projected onto two reconstructed fold-trained PCA loading vectors, and shown as three reconstructed standardized traces: network mean and two residual scores.")
    s.header("02 / cortical signals", "333 parcels → 13 means + 26 residual scores")
    basis = SUPPLEMENT["network_basis"]
    assert basis["chosen_network"] == "Default" and basis["chosen_network_parcels"] == 41
    s.text(28, 61, "DEFAULT NETWORK · 41 PARCELS", 10, ACCENT, 700)
    s.text(28, 86, "per-volume", 11, INK, 600)
    s.text(28, 107, "parcel mean", 11, INK)
    s.text(28, 135, "subtract mean", 11, INK)
    s.text(28, 163, "project residuals", 11, INK)
    for y in (114, 142):
        arrow(s, 91, y, 91, y + 10)
    s.text(28, 204, "Output per volume", 11, MUTED)
    s.text(28, 224, "1 mean + 2 PC scores", 12, INK, 600)
    s.line(183, 53, 183, 247)
    s.text(205, 61, "FOLD PCA BASIS", 10, ACCENT, 700)
    loadings = basis["top_two_loadings_in_atlas_parcel_order"]
    assert len(loadings) == 41 and all(len(row) == 2 for row in loadings)
    heatmap(s, loadings, 234, 75, 74, 159, max(abs(v) for row in loadings for v in row))
    s.text(271, 247, "PC 1   PC 2", 10, MUTED, 400, "middle")
    s.text(224, 86, "01", 10, MUTED, 400, "end")
    s.text(224, 233, "41", 10, MUTED, 400, "end")
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
    s.footer("The loading colors encode sign and magnitude; the three traces are standardized held-out outputs.")
    s.save(2)


def visual_03() -> None:
    s = SVG("Shrinkage connectivity from a short window", "Six selected features from the full 39-feature operation show sample covariance, reconstructed Ledoit-Wolf shrinkage covariance, and final correlation. The saved shrinkage fraction for this window is 0.1511; eigenvalue flooring made no change.")
    s.header("03 / connectivity", "24–30 valid rows · 39 features")
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
    s.save(3)


def visual_04() -> None:
    s = SVG("Lag-specific tangent references", "At each of the current, 25-volume, and 50-volume lags, a reconstructed correlation is compared with its reconstructed fold-trained reference to produce a tangent matrix. Six-by-six excerpts are shown from the full 39-by-39 matrices. All three tangents become 2340 coordinates, clipped and reduced to 64 whitened PCA scores.")
    s.header("04 / tangent representation", "3 × 780 → 2,340 → 64")
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
        s.rect(592 + col * 14, 84 + row * 15, 12, 13, diverge(value, 2.5))
    s.rect(592, 84, 8 * 14, 8 * 15, "none", LINE)
    s.text(648, 226, "64 whitened scores", 10, MUTED, 400, "middle")
    s.footer("Each C, G, T image shows the same 6 channels from a full 39 × 39 matrix; T uses all 39.")
    s.save(4)


def visual_05() -> None:
    s = SVG("Tangent decoder and temperature calibration", "The reconstructed 64 whitened tangent scores enter shrinkage LDA. Saved uncalibrated and calibrated stage probabilities are compared directly. The fitted tangent temperature is 2.114, softening this representative prediction.")
    s.header("05 / tangent decoder", "64 features → four probabilities")
    p = SUPPLEMENT["probability_calibration"]
    scores = DATA["step_5_pca"]["whitened_score"]
    s.text(93, 62, "64 PCA SCORES", 10, ACCENT, 700, "middle")
    for i, value in enumerate(scores):
        col, row = i % 8, i // 8
        s.rect(37 + col * 14, 89 + row * 13, 12, 11, diverge(value, 2.5))
    s.rect(37, 89, 8 * 14, 8 * 13, "none", LINE)
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
    s.save(5)


def visual_06() -> None:
    s = SVG("Lagged edge flow and Hodge energy", "At left, schematic forward and reverse cross-lag parcel interactions define one antisymmetric edge flow. At right, saved harmonic, gradient, and curl energy fractions from the representative window are shown for three lags and their pooled flow, followed by the three saved temporal change features.")
    s.header("06 / directed-cycle branch", "333 parcel signals · 23 energy-family features")
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
    s.save(6)


def visual_07() -> None:
    s = SVG("Weighted blend then final calibration", "Saved tangent, cycle, and final four-stage probability vectors, with a derived pre-temperature weighted mixture for the same window. The cycle weight is 0.30.")
    alpha = DATA["step_8_blend_simplex"]["cycle_weight"]
    tangent = DATA["step_6_tangent_lda"]["probability"]
    cycle = DATA["step_7_cycle_ridge"]["probability"]
    mix = [(1 - alpha) * a + alpha * b for a, b in zip(tangent, cycle)]
    final = DATA["step_8_blend_simplex"]["final_probability"]
    s.header("07 / probability blend", f"cycle weight α = {alpha:.2f}")
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
    s.save(7)


def visual_08() -> None:
    s = SVG("Four probabilities locate one simplex point", "Four saved final stage probabilities combine with the tetrahedron vertices to locate one held-out point. The probability bars and position represent the same vector.")
    s.header("08 / simplex projection", "four probabilities → one 3D point")
    probabilities = DATA["step_8_blend_simplex"]["final_probability"]
    displayed = percentages(probabilities)
    s.text(28, 61, "SAVED FINAL PROBABILITIES", 10, ACCENT, 700)
    for i, (name, value) in enumerate(zip(STAGES, probabilities)):
        y = 77 + i * 39
        s.rect(29, y - 10, 10, 10, STAGE_COLORS[i])
        s.text(48, y, name, 11, INK, 600)
        s.rect(103, y - 8, 140, 13, "#eff3f2")
        s.rect(103, y - 8, max(1, 140 * value), 13, STAGE_COLORS[i])
        s.text(299, y + 2, f"{displayed[i]:.1f}%", 11, INK, 600, "end")
    arrow(s, 319, 142, 363, 142, ACCENT, 2)
    s.text(341, 119, "weighted", 10, MUTED, 400, "middle")
    s.text(341, 173, "sum", 10, MUTED, 400, "middle")
    vertices = DATA["step_8_blend_simplex"]["tetrahedron_vertices"]
    point = DATA["step_8_blend_simplex"]["simplex_xyz"]
    yaw, pitch = -0.45, 0.18
    def projected(q):
        x, y, z = q
        x1 = x * math.cos(yaw) + z * math.sin(yaw)
        z1 = -x * math.sin(yaw) + z * math.cos(yaw)
        y1 = y * math.cos(pitch) - z1 * math.sin(pitch)
        return (520 + x1 * 100, 143 - y1 * 90)
    corners = [projected(v) for v in vertices]
    for a in range(4):
        for b in range(a + 1, 4):
            s.line(*corners[a], *corners[b], LINE, 1.5)
    for i, (corner, name) in enumerate(zip(corners, STAGES)):
        s.circle(*corner, 5, STAGE_COLORS[i])
        dx = 12 if corner[0] < 520 else -12
        anchor = "start" if dx > 0 else "end"
        s.text(corner[0] + dx, corner[1] + 4, name, 11, INK, 600, anchor)
    pxy = projected(point)
    s.circle(*pxy, 8, PAPER, INK, 2)
    s.circle(*pxy, 3.5, ACCENT)
    s.text(520, 242, "one held-out window", 11, MUTED, 400, "middle")
    s.footer("Position represents all four probabilities; rotating the view changes no probability.")
    s.save(8)


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
    assert SUPPLEMENT["privacy"] == {
        "participant_scan_time_or_label_fields_included": False,
        "raw_333_parcel_series_included": False,
        "performance_metrics_included": False,
    }


if __name__ == "__main__":
    validate()
    for fn in (visual_01, visual_02, visual_03, visual_04,
               visual_05, visual_06, visual_07, visual_08):
        fn()
    print("Built eight sleep-method SVGs from the validated representative export.")
