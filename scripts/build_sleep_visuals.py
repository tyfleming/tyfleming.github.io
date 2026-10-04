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


def sample_correlation(rows, valid):
    """Descriptive sample correlation before shrinkage, from reconstructed features."""
    selected = [row for row, keep in zip(rows, valid) if keep]
    n, d = len(selected), len(selected[0])
    means = [sum(row[j] for row in selected) / n for j in range(d)]
    centered = [[row[j] - means[j] for j in range(d)] for row in selected]
    variance = [sum(row[j] ** 2 for row in centered) for j in range(d)]
    return [
        [
            sum(row[i] * row[j] for row in centered) /
            math.sqrt(variance[i] * variance[j]) if variance[i] * variance[j] > 0 else 0
            for j in range(d)
        ]
        for i in range(d)
    ]


def visual_01() -> None:
    s = SVG("Causal fMRI window", "Three reconstructed standardized network-mean traces from a 30-volume window. A motion mask shows all frames valid; the window ends at the prediction endpoint. Stage labels are not model inputs.")
    s.header("01 / causal window", "30 volumes · 62.4 seconds")
    features = DATA["step_1_window"]["cortical_features"]
    valid = DATA["step_1_window"]["motion_valid"]
    x0, x1 = 119, 628
    s.text(x0, 59, "PAST DATA ENTER THE MODEL", 10, ACCENT, 700)
    for center, index, color in [(94, 0, ACCENT), (146, 6, POS), (198, 12, NEG)]:
        s.line(x0, center, x1, center, LINE)
        s.text(105, center + 4, f"mean {index + 1:02d}", 11, MUTED, 600, "end")
        pts = []
        for t, row in enumerate(features):
            x = x0 + t * (x1 - x0) / 29
            y = center - max(-3, min(3, row[index])) * 9
            pts.append((x, y))
        s.polyline(pts, color, 2)
    s.line(x1, 66, x1, 226, ACCENT, 1.4)
    s.text(641, 84, "endpoint t", 11, ACCENT, 700)
    s.text(641, 104, "predict here", 10, MUTED)
    s.text(105, 245, "FD < 0.2", 10, MUTED, 400, "end")
    for t, passed in enumerate(valid):
        s.rect(x0 + t * (x1 - x0) / 30, 230, (x1 - x0) / 30 - 1, 8,
               ACCENT if passed else POS)
    s.text(x0, 255, "t−29", 10)
    s.text(x1, 255, "t", 10, MUTED, 400, "end")
    s.footer("Thirty frames form one causal window; the endpoint stage is a training/evaluation label.")
    s.save(1)


def visual_02() -> None:
    s = SVG("From parcels to network signals", "A schematic of parcel averaging, within-network mean removal, and two fold-fitted PCA residual scores per network, beside the actual reconstructed 39-by-30 standardized feature heatmap.")
    s.header("02 / cortical signals", "333 parcels → 13 means + 26 residual scores")
    s.text(28, 62, "ONE NETWORK · SCHEMATIC", 10, ACCENT, 700)
    for x, color in zip([42, 64, 86, 108, 130, 152], [NEG, ACCENT, POS, NEG, POS, ACCENT]):
        s.circle(x, 87, 7, color)
    s.text(185, 91, "parcel values", 11, MUTED)
    s.line(106, 99, 106, 116, ACCENT, 1.5)
    arrow(s, 106, 116, 106, 128, ACCENT)
    s.text(28, 146, "network mean", 12, INK, 600)
    s.text(157, 146, "subtract mean → residuals", 11, INK)
    s.rect(28, 159, 104, 11, "#edf2f1")
    s.rect(28, 159, 65, 11, ACCENT)
    s.rect(157, 159, 104, 11, "#edf2f1")
    s.rect(157, 159, 37, 11, NEG)
    s.rect(215, 159, 46, 11, POS)
    s.text(28, 194, "fold-fitted residual PCA", 11, MUTED)
    arrow(s, 118, 201, 118, 220, ACCENT)
    s.text(28, 244, "1 mean + 2 scores / volume", 12, INK, 600)
    s.line(314, 53, 314, 249)
    s.text(337, 62, "STANDARDIZED WINDOW · RECONSTRUCTED", 10, ACCENT, 700)
    m = DATA["step_1_window"]["cortical_features"]
    transposed = [[row[j] for row in m] for j in range(39)]
    x, y, w, h = 458, 72, 174, 174
    heatmap(s, transposed, x, y, w, h, 3)
    s.line(x, y + h * 13 / 39, x + w, y + h * 13 / 39, INK, 1.3)
    s.text(446, 101, "13 means", 11, INK, 600, "end")
    s.text(446, 174, "26 PCA", 11, INK, 600, "end")
    s.text(x, 256, "frame 1", 10)
    s.text(x + w, 256, "frame 30", 10, MUTED, 400, "end")
    s.footer("Repeat this operation across 13 networks, then standardize all 39 signals on training data.")
    s.save(2)


def visual_03() -> None:
    s = SVG("From sample correlation to stable connectivity", "Side-by-side sample correlation calculated from valid rows of the reconstructed window and the reconstructed shrinkage positive-definite correlation matrix.")
    s.header("03 / connectivity", "24–30 valid rows · 39 features")
    features = DATA["step_1_window"]["cortical_features"]
    valid = DATA["step_1_window"]["motion_valid"]
    naive = sample_correlation(features, valid)
    stable = DATA["step_2_spd"]["current_correlation"]
    heatmap(s, naive, 67, 73, 170, 170, 1)
    heatmap(s, stable, 372, 73, 170, 170, 1)
    s.text(152, 61, "sample correlation", 12, INK, 600, "middle")
    s.text(457, 61, "stabilized correlation", 12, INK, 600, "middle")
    arrow(s, 256, 150, 350, 150, ACCENT, 2)
    s.text(303, 129, "shrink +", 11, ACCENT, 600, "middle")
    s.text(303, 181, "normalize", 11, ACCENT, 600, "middle")
    s.text(562, 88, "symmetric", 11, INK, 600)
    s.text(562, 114, "diagonal = 1", 11, INK)
    s.text(562, 140, "positive definite", 11, INK)
    for i in range(36):
        s.rect(562 + i * 4, 185, 4.1, 9, diverge(-1 + i * 2 / 35, 1))
    s.text(562, 210, "−1", 10)
    s.text(634, 210, "0", 10, MUTED, 400, "middle")
    s.text(706, 210, "+1", 10, MUTED, 400, "end")
    s.footer("The left matrix is descriptive; the right is the positive-definite state used by the decoder.")
    s.save(3)


def visual_04() -> None:
    s = SVG("Three causal states to 64 tangent features", "Three reconstructed causal-lag correlation matrices flow through a training-fitted tangent reference, robust clipping, and PCA. The reconstructed current tangent matrix and 64 whitened scores are shown.")
    s.header("04 / tangent representation", "3 × 780 → 2,340 → 64")
    matrices = DATA["step_3_causal_lags"]["correlations"]
    tangent = DATA["step_4_tangent"]["current_tangent"]
    for x, matrix, label in zip((28, 144, 260), matrices, ("now", "−52 s", "−104 s")):
        heatmap(s, matrix, x, 79, 90, 90, 0.9)
        s.text(x + 45, 66, label, 11, INK, 600, "middle")
        s.text(x + 45, 185, "39 × 39", 10, MUTED, 400, "middle")
    arrow(s, 359, 124, 390, 124)
    heatmap(s, tangent, 402, 79, 90, 90, 0.7)
    s.text(447, 66, "tangent example", 11, INK, 600, "middle")
    s.text(447, 185, "current state", 10, MUTED, 400, "middle")
    arrow(s, 505, 124, 538, 124)
    scores = DATA["step_5_pca"]["whitened_score"]
    for i, value in enumerate(scores):
        col, row = i % 8, i // 8
        s.rect(552 + col * 17, 75 + row * 12, 15, 10, diverge(value, 2.5))
    s.rect(552, 75, 8 * 17, 8 * 12, "none", LINE)
    s.text(620, 66, "PCA scores", 11, INK, 600, "middle")
    s.text(620, 185, "64 whitened", 10, MUTED, 400, "middle")
    s.line(28, 207, 716, 207)
    s.text(28, 232, "each lag: log relative to training reference", 10, ACCENT, 600)
    s.text(310, 232, "weighted svec + clipping", 10, ACCENT, 600)
    s.text(544, 232, "training PCA", 10, ACCENT, 600)
    s.footer("All three states enter the feature vector; the tangent heatmap depicts the current state only.")
    s.save(4)


def visual_05() -> None:
    s = SVG("Tangent scores to calibrated stage probabilities", "The reconstructed 64-component whitened PCA vector enters a schematic shrinkage-LDA score stage and temperature calibration. Four bars show saved held-out tangent-branch probabilities.")
    s.header("05 / tangent decoder", "64 features → four probabilities")
    scores = DATA["step_5_pca"]["whitened_score"]
    s.text(94, 65, "64 WHITENED SCORES", 10, ACCENT, 700, "middle")
    for i, value in enumerate(scores):
        col, row = i % 8, i // 8
        s.rect(37 + col * 14, 82 + row * 13, 12, 11, diverge(value, 2.5))
    s.rect(37, 82, 8 * 14, 8 * 13, "none", LINE)
    arrow(s, 173, 136, 213, 136)
    s.text(278, 88, "SHRINKAGE LDA", 10, ACCENT, 700, "middle")
    for i, name in enumerate(STAGES):
        s.rect(218, 101 + i * 30, 119, 22, PAPER, LINE)
        s.text(278, 116 + i * 30, "score " + name, 11, INK, 600, "middle")
    arrow(s, 351, 136, 392, 136)
    s.text(366, 113, "softmax", 10, MUTED, 400, "middle")
    s.text(366, 169, "temperature", 10, MUTED, 400, "middle")
    values = DATA["step_6_tangent_lda"]["probability"]
    displayed = percentages(values)
    s.text(535, 65, "SAVED BRANCH OUTPUT", 10, ACCENT, 700, "middle")
    for i, (name, value) in enumerate(zip(STAGES, values)):
        y = 83 + i * 38
        s.text(424, y + 11, name, 11, INK, 600)
        s.rect(472, y, 173, 14, "#eff3f2")
        s.rect(472, y, max(1, 173 * value), 14, STAGE_COLORS[i])
        s.text(690, y + 12, f"{displayed[i]:.1f}%", 11, INK, 600, "end")
    s.footer("The four probabilities sum to one; their maximum gives the tangent branch's stage.")
    s.save(5)


def graph_pattern(s: SVG, kind: str, x: int) -> None:
    """Small labeled topology examples; no atlas coordinates are implied."""
    if kind == "gradient":
        for xx in (x, x + 28, x + 56):
            s.circle(xx, 170, 3.5, PAPER, INK, 1)
        arrow(s, x + 5, 170, x + 22, 170, ACCENT, 1.7)
        arrow(s, x + 34, 170, x + 51, 170, ACCENT, 1.7)
    elif kind == "curl":
        s.raw(f'<polygon points="{x+28},146 {x},190 {x+56},190" fill="#eff3f2" stroke="{LINE}"/>')
        arrow(s, x + 31, 152, x + 50, 183, POS, 1.7)
        arrow(s, x + 48, 190, x + 8, 190, POS, 1.7)
        arrow(s, x + 6, 183, x + 25, 152, POS, 1.7)
        for xx, yy in ((x + 28, 146), (x, 190), (x + 56, 190)):
            s.circle(xx, yy, 3.5, PAPER, INK, 1)
    else:
        s.raw(f'<polygon points="{x},148 {x+55},148 {x+55},195 {x},195" fill="none" stroke="{LINE}"/>')
        for a, b, c, d in ((x+6,148,x+48,148),(x+55,154,x+55,189),
                           (x+48,195,x+6,195),(x,189,x,154)):
            arrow(s, a, b, c, d, NEG, 1.7)
        for xx, yy in ((x,148),(x+55,148),(x+55,195),(x,195)):
            s.circle(xx, yy, 3.5, PAPER, INK, 1)


def visual_06() -> None:
    s = SVG("Lagged parcel flows and cycle features", "At left, schematic lagged parcel pairing and graph Hodge flow patterns. At right, saved 23-feature energy profile for one held-out window. The graph sketches do not show atlas locations.")
    s.header("06 / directed-cycle branch", "original 333 parcels · 23 features")
    s.text(28, 61, "LAGGED PARCEL PAIR · SCHEMATIC", 10, ACCENT, 700)
    s.text(36, 89, "parcel i", 11, INK, 600)
    s.text(36, 113, "parcel j", 11, INK, 600)
    for y, color in ((85, NEG), (109, POS)):
        s.line(119, y, 270, y, LINE)
        pts = [(119 + i * 19, y - (7 if i % 3 == 0 else -5 if i % 3 == 1 else 1))
               for i in range(9)]
        s.polyline(pts, color, 1.6)
    arrow(s, 145, 83, 177, 105, ACCENT)
    s.text(211, 131, "i→j − j→i · τ = 1, 2, 3", 10, MUTED, 400, "middle")
    s.line(28, 139, 324, 139)
    for kind, x, name in (("gradient", 39, "gradient"), ("curl", 142, "curl"), ("harmonic", 245, "harmonic")):
        graph_pattern(s, kind, x)
        s.text(x + 28, 221, name, 11, INK, 600, "middle")
    s.text(28, 247, "source → sink    ·    filled face    ·    unfilled loop", 10, MUTED)
    s.line(341, 52, 341, 248)
    values = DATA["step_7_cycle_ridge"]["feature_values"]
    s.text(362, 61, "SAVED ENERGY FEATURE PROFILE", 10, ACCENT, 700)
    names = ["flow", "harmonic", "H share", "G share", "C share"]
    for col, name in enumerate(names):
        x = 395 + col * 62
        s.text(x, 83, name, 10, INK, 600)
        col_values = [values[row * 5 + col] for row in range(4)]
        max_value = max(col_values)
        for row, val in enumerate(col_values):
            y = 102 + row * 27
            s.rect(x, y, 49, 8, "#eff3f2")
            s.rect(x, y, 49 * val / max_value, 8, ACCENT)
    for row, name in enumerate(("lag 1", "lag 2", "lag 3", "pooled")):
        s.text(386, 109 + row * 27, name, 10, MUTED, 400, "end")
    s.line(362, 205, 715, 205)
    s.text(362, 224, f"ΔH norm {values[20]:.2f}", 10, INK)
    s.text(479, 224, f"cosine {values[21]:.2f}", 10, INK)
    s.text(586, 224, f"angle {values[22]:.2f} rad", 10, INK)
    s.text(362, 247, "Bars scaled within each feature column.", 10)
    s.footer("Five summaries at each lag + five pooled + three changes = 23 model inputs.")
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
    s.text(701, 178, "↓ T", 11, ACCENT, 700, "end")
    s.footer("The weighted mixture is derived; the final row is the saved, temperature-calibrated output.")
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


if __name__ == "__main__":
    validate()
    for fn in (visual_01, visual_02, visual_03, visual_04,
               visual_05, visual_06, visual_07, visual_08):
        fn()
    print("Built eight sleep-method SVGs from the validated representative export.")
