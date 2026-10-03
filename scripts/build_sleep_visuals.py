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
            '<svg xmlns="http://www.w3.org/2000/svg" width="740" height="230" viewBox="0 0 740 230" '
            'role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(description)}</desc>',
            '<rect width="740" height="230" fill="#ffffff"/>',
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


def probability_bars(svg: SVG, values, x=155, y=58, width=445, gap=36, show_values=True) -> None:
    displayed = percentages(values)
    for i, (stage, p) in enumerate(zip(STAGES, values)):
        yy = y + i * gap
        svg.text(x - 30, yy + 10, stage, 14, INK, 600, "end")
        svg.rect(x, yy, width, 13, "#eff3f2")
        svg.rect(x, yy, max(1, width * p), 13, STAGE_COLORS[i])
        if show_values:
            svg.text(x + width + 18, yy + 11, f"{displayed[i]:.1f}%", 13, INK, 600)


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
    s = SVG("Causal fMRI window", "Three reconstructed network-mean signals over the 30-volume window. All 30 frames are motion-valid and the prediction is made at the right endpoint.")
    s.header("01 / causal window", "30 volumes · 62.4 seconds")
    features = DATA["step_1_window"]["cortical_features"]
    valid = DATA["step_1_window"]["motion_valid"]
    x0, x1 = 95, 660
    for center, index, color in [(77, 0, ACCENT), (125, 6, POS), (173, 12, NEG)]:
        s.line(x0, center, x1, center, LINE)
        s.text(82, center + 4, f"mean {index + 1:02d}", 11, MUTED, 500, "end")
        pts = []
        for t, row in enumerate(features):
            x = x0 + t * (x1 - x0) / 29
            y = center - max(-3, min(3, row[index])) * 8
            pts.append((x, y))
        s.polyline(pts, color, 1.8)
    s.line(x1, 51, x1, 195, ACCENT, 1)
    s.text(x1 + 8, 52, "endpoint t", 11, ACCENT, 600)
    for t, passed in enumerate(valid):
        s.rect(x0 + t * (x1 - x0) / 30, 202, (x1 - x0) / 30 - 1, 5,
               ACCENT if passed else POS)
    s.text(x0, 224, "t−29", 11)
    s.text(x1, 224, "t", 11, MUTED, 400, "end")
    s.text(714, 205, "motion-valid", 10, MUTED, 400, "end")
    s.save(1)


def visual_02() -> None:
    s = SVG("Cortical signal compression", "A heatmap of 30 time points by 39 reconstructed cortical features: 13 network means followed by 26 within-network residual component scores.")
    s.header("02 / cortical signals", "333 parcels → 39 features")
    m = DATA["step_1_window"]["cortical_features"]
    transposed = [list(row[j] for row in m) for j in range(39)]
    heatmap(s, transposed, 170, 54, 490, 134, 3)
    y_div = 54 + 134 * 13 / 39
    s.line(170, y_div, 660, y_div, INK, 1)
    s.text(155, 80, "13 means", 12, INK, 600, "end")
    s.text(155, 145, "26 residual", 12, INK, 600, "end")
    s.text(170, 207, "first frame", 11)
    s.text(660, 207, "endpoint", 11, MUTED, 400, "end")
    s.text(414, 224, "color: feature value, clipped to ±3", 10, MUTED, 400, "middle")
    s.save(2)


def visual_03() -> None:
    s = SVG("Functional connectivity matrix", "The reconstructed 39 by 39 positive-definite correlation matrix. Warm cells are positive, cool cells negative, and the diagonal equals one.")
    s.header("03 / functional connectivity", "39 × 39 · positive definite")
    matrix = DATA["step_2_spd"]["current_correlation"]
    heatmap(s, matrix, 245, 49, 164, 164, 1)
    s.text(210, 62, "features", 11, MUTED, 400, "end")
    s.text(327, 226, "features", 11, MUTED, 400, "middle")
    s.text(464, 89, "Diagonal = 1", 13, INK, 600)
    s.text(464, 119, "Symmetric around diagonal", 12)
    s.text(464, 149, "Cool = negative", 12, NEG)
    s.text(464, 173, "Warm = positive", 12, POS)
    for i in range(61):
        s.rect(464 + i * 4, 185, 4.1, 8, diverge(-1 + i / 30, 1))
    s.text(464, 209, "−1", 10)
    s.text(584, 209, "0", 10, MUTED, 400, "middle")
    s.text(706, 209, "+1", 10, MUTED, 400, "end")
    s.save(3)


def visual_04() -> None:
    s = SVG("Causal tangent transformation", "Three reconstructed causal-lag correlation matrices; the current tangent matrix is shown as an example of the per-lag transform, followed by 64 whitened PCA coordinates.")
    s.header("04 / tangent representation", "3 × 780 → 64")
    matrices = DATA["step_3_causal_lags"]["correlations"]
    tangent = DATA["step_4_tangent"]["current_tangent"]
    blocks = [(matrices[0], "now", 0.9), (matrices[1], "−52 s", 0.9),
              (matrices[2], "−104 s", 0.9), (tangent, "tangent", 0.7)]
    for i, (matrix, label, scale) in enumerate(blocks):
        x = 30 + i * 133
        heatmap(s, matrix, x, 65, 104, 104, scale)
        s.text(x + 52, 190, label, 11, INK, 600, "middle")
        if i == 2:
            arrow(s, x + 109, 117, x + 126, 117)
    arrow(s, 536, 117, 553, 117)
    scores = DATA["step_5_pca"]["whitened_score"]
    for i, value in enumerate(scores):
        col, row = i % 16, i // 16
        s.rect(570 + col * 8.5, 82 + row * 14, 7, 11, diverge(value, 2.5))
    s.rect(570, 82, 16 * 8.5, 4 * 14, "none", LINE)
    s.text(638, 190, "64 PCA scores", 11, INK, 600, "middle")
    s.text(30, 222, "Each lag maps to a tangent matrix; the current map is shown. Reference and PCA use training subjects.", 11)
    s.save(4)


def visual_05() -> None:
    s = SVG("Tangent decoder probabilities", "Four stage probability bars from the held-out tangent-LDA branch for the representative window.")
    s.header("05 / tangent decoder", "held-out branch output")
    probability_bars(s, DATA["step_6_tangent_lda"]["probability"], y=59)
    s.text(155, 218, "All four probabilities sum to one.", 11)
    s.save(5)


def visual_06() -> None:
    s = SVG("Directed-flow and cycle features", "Strongest reconstructed directed atlas edges at left and the saved 23-feature cycle summary at right.")
    s.header("06 / directed-cycle branch", "24 strongest edges · 23 features")
    edges = DATA["step_7_cycle_ridge"]["strongest_pooled_flow_edges"]
    endpoints = [edge[key] for edge in edges for key in ("source_xyz", "target_xyz")]
    xs = [p[0] for p in endpoints]
    zs = [p[2] for p in endpoints]
    def pos(p):
        return (35 + (p[0] - min(xs)) / (max(xs) - min(xs)) * 268,
                63 + (max(zs) - p[2]) / (max(zs) - min(zs)) * 126)
    s.rect(24, 52, 299, 150, "none", LINE)
    for edge in edges:
        source, target = pos(edge["source_xyz"]), pos(edge["target_xyz"])
        if edge["pooled_flow"] < 0:
            source, target = target, source
        arrow(s, *source, *target, POS if edge["pooled_flow"] >= 0 else NEG, 1.1)
        s.circle(*source, 1.8, INK)
    s.text(28, 218, "atlas x/z projection · direction from lagged flow", 10)
    values = DATA["step_7_cycle_ridge"]["feature_values"]
    names = ["flow", "harmonic", "harmonic %", "gradient %", "curl %"]
    for col, name in enumerate(names):
        x = 370 + col * 67
        s.text(x, 59, name, 10, INK, 600)
        col_values = [values[row * 5 + col] for row in range(4)]
        max_value = max(col_values)
        for row, val in enumerate(col_values):
            y = 73 + row * 24
            s.rect(x, y, 53, 8, "#eff3f2")
            s.rect(x, y, 53 * val / max_value, 8, ACCENT)
    for row, name in enumerate(["lag 1", "lag 2", "lag 3", "pooled"]):
        s.text(350, 81 + row * 24, name, 10, MUTED, 400, "end")
    s.line(345, 177, 716, 177)
    s.text(368, 195, f"cycle step norm {values[20]:.2f}", 10, INK)
    s.text(505, 195, f"cosine {values[21]:.2f}", 10, INK)
    s.text(619, 195, f"angle {values[22]:.2f} rad", 10, INK)
    s.text(370, 219, "bars scaled separately by feature type", 10)
    s.save(6)


def visual_07() -> None:
    s = SVG("Probability blend", "Four-class tangent, cycle, and final calibrated probabilities for the same held-out window. The cycle blend weight is 0.30.")
    alpha = DATA["step_8_blend_simplex"]["cycle_weight"]
    s.header("07 / probability blend", f"cycle weight α = {alpha:.2f}")
    rows = [
        ("tangent", DATA["step_6_tangent_lda"]["probability"]),
        ("cycle", DATA["step_7_cycle_ridge"]["probability"]),
        ("final", DATA["step_8_blend_simplex"]["final_probability"]),
    ]
    for i, name in enumerate(STAGES):
        s.text(212 + i * 122, 62, name, 12, INK, 600, "middle")
    for row, (name, probabilities) in enumerate(rows):
        y = 77 + row * 45
        s.text(116, y + 16, name, 13, INK, 600, "end")
        displayed = percentages(probabilities)
        for col, p in enumerate(probabilities):
            x = 163 + col * 122
            s.rect(x, y, 98, 12, "#eff3f2")
            s.rect(x, y, max(1, 98 * p), 12, STAGE_COLORS[col])
            s.text(x + 98, y + 30, f"{displayed[col]:.1f}%", 11, INK, 400, "end")
    s.line(148, 160, 650, 160, LINE)
    s.text(163, 213, "The final row includes calibration after the two branches are blended.", 11)
    s.save(7)


def visual_08() -> None:
    s = SVG("Tetrahedral probability projection", "One actual held-out four-stage probability vector placed inside a tetrahedron. Its Wake probability is largest and the same values appear in the right-side readout.")
    s.header("08 / simplex projection", "one held-out vector")
    vertices = DATA["step_8_blend_simplex"]["tetrahedron_vertices"]
    probabilities = DATA["step_8_blend_simplex"]["final_probability"]
    point = DATA["step_8_blend_simplex"]["simplex_xyz"]
    yaw, pitch = -0.45, 0.18
    def projected(q):
        x, y, z = q
        x1 = x * math.cos(yaw) + z * math.sin(yaw)
        z1 = -x * math.sin(yaw) + z * math.cos(yaw)
        y1 = y * math.cos(pitch) - z1 * math.sin(pitch)
        return (232 + x1 * 160, 132 - y1 * 100)
    corners = [projected(v) for v in vertices]
    for a in range(4):
        for b in range(a + 1, 4):
            s.line(*corners[a], *corners[b], LINE, 1.3)
    for i, (corner, name) in enumerate(zip(corners, STAGES)):
        s.circle(*corner, 5, STAGE_COLORS[i])
        dx = 10 if corner[0] < 232 else -10
        anchor = "start" if dx > 0 else "end"
        s.text(corner[0] + dx, corner[1] + 4, name, 11, INK, 600, anchor)
    pxy = projected(point)
    s.circle(*pxy, 8, PAPER, INK, 2)
    s.circle(*pxy, 3.5, ACCENT)
    s.line(445, 49, 445, 201)
    displayed = percentages(probabilities)
    for i, (name, p) in enumerate(zip(STAGES, probabilities)):
        y = 65 + i * 38
        s.rect(466, y - 9, 9, 9, STAGE_COLORS[i])
        s.text(487, y, name, 12, INK, 500)
        s.text(680, y, f"{displayed[i]:.1f}%", 13, INK, 600, "end")
    s.text(466, 216, "position = probability-weighted vertices", 10)
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
