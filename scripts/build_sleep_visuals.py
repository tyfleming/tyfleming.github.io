"""Build the static, accessible SVG companions to sleep.html.

The representative JSON contains no subject or scan identifiers. Saved model
outputs and reconstructed intermediate tensors are identified on the page.
Figure numbers, titles, and dimensions live in the HTML captions; each SVG
carries only the plot, its panel labels, and a provenance tag (saved,
reconstructed, derived, schematic, or illustrative).
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

# Two palettes shared with style.css. "day" is the minimal light site; "night" is the
# Night Oracle variant. Both keep a diverging blue/rust pair around a neutral midpoint so
# zero never reads as "missing", and a stage ramp validated (OKLab ΔE) for CVD and
# normal-vision separation on its own surface. Select with --theme (default: night).
WIDTH = 760
THEMES = {
    "day": dict(
        INK="#111418", INK2="#3a414b", MUTED="#6b7380", FAINT="#a3a9b2", LINE="#e3e6ea",
        GRID="#eceef1", AXIS="#c9ced5", PANEL="#f3f4f6", PAPER="#ffffff", EDGE="#dde1e6",
        ACCENT="#0f6e6a", ACCENT_LIGHT="#8fc0bb", ACCENT_PALE="#cfe4e1", GRAY="#98a1ab",
        GRAY_LIGHT="#d3d8de", NEG="#3b6aa6", POS="#b9592f", NEG_STRONG="#335f99",
        POS_STRONG="#a44c27", MID="#eef0f3",
        STAGE_COLORS=["#d4922a", "#cf6068", "#9460b8", "#3f4a9c"],
    ),
    "night": dict(
        INK="#ece6d6", INK2="#c1c9d0", MUTED="#8f9aa6", FAINT="#5e6a77", LINE="#24323f",
        GRID="#1b2834", AXIS="#3a4856", PANEL="#1a2733", PAPER="#111c26", EDGE="#2a3845",
        ACCENT="#d8b57c", ACCENT_LIGHT="#8c7550", ACCENT_PALE="#4a4234", GRAY="#7d8894",
        GRAY_LIGHT="#3a4855", NEG="#6f9fe0", POS="#e58a5c", NEG_STRONG="#5a8bd0",
        POS_STRONG="#d57a4c", MID="#26323d",
        STAGE_COLORS=["#c38824", "#b24f63", "#6453a7", "#359bd9"],
    ),
}
THEME = "night"
for _arg in __import__("sys").argv[1:]:
    if _arg.startswith("--theme="):
        THEME = _arg.split("=", 1)[1]
if THEME not in THEMES:
    raise SystemExit(f"Unknown theme {THEME!r}; choose from {', '.join(THEMES)}.")
globals().update(THEMES[THEME])
STAGES = ["Wake", "N1", "N2", "N3"]
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,Helvetica,Arial,sans-serif"
MONO = "'SF Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SERIF = "Charter,'Bitstream Charter','Iowan Old Style',Georgia,serif"
NETWORK_ORDER = SUPPLEMENT["network_basis"]["network_order"]


def interp(a: str, b: str, t: float) -> str:
    t = max(0, min(1, t))
    aa = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    bb = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(aa, bb))


def diverge(value: float, limit: float) -> str:
    ratio = max(-1, min(1, value / limit))
    return interp(MID, POS if ratio >= 0 else NEG, abs(ratio))


def cell_text_color(fill: str) -> str:
    """Choose white or near-black, whichever reads better on a tinted cell."""
    rgb = [int(fill[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    luminance = sum(a * b for a, b in zip(linear, (.2126, .7152, .0722)))
    white_contrast = 1.05 / (luminance + .05)
    dark_contrast = (luminance + .05) / .0575
    return "#ffffff" if white_contrast >= dark_contrast else "#111418"


def toy_fill(value: float, limit: float) -> str:
    """Use stronger data hues so saturated toy-matrix cells support white labels."""
    ratio = max(-1, min(1, value / limit))
    return interp(MID, POS_STRONG if ratio >= 0 else NEG_STRONG, abs(ratio))


def text_width(value: str, size: float, mono: bool = False, weight: int = 400) -> float:
    """Approximate rendered width; good enough to place tags after labels."""
    if mono:
        return len(value) * size * 0.61
    total = 0.0
    for ch in value:
        if ch in "il.,:;|!'()[]ftjrI ·/":
            total += 0.31
        elif ch in "mwMW%":
            total += 0.84
        elif ch.isupper() or ch.isdigit():
            total += 0.64
        else:
            total += 0.54
    return total * size * (1.05 if weight >= 600 else 1)


class SVG:
    def __init__(self, title: str, description: str, height: int):
        self.height = height
        self.gradients = 0
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
            f'viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc" '
            f'font-family="{SANS}">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(description)}</desc>',
            f'<rect width="{WIDTH}" height="{height}" fill="{PAPER}"/>',
        ]

    def raw(self, value: str) -> None:
        self.parts.append(value)

    def line(self, x1, y1, x2, y2, color=LINE, width=1, opacity=1, cap="butt") -> None:
        self.raw(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="{width}" opacity="{opacity}" stroke-linecap="{cap}"/>'
        )

    def rect(self, x, y, w, h, color, stroke=None, width=1, rx=0, opacity=1) -> None:
        border = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        corner = f' rx="{rx}"' if rx else ""
        alpha = f' opacity="{opacity}"' if opacity != 1 else ""
        self.raw(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{max(0, w):.2f}" height="{max(0, h):.2f}" '
            f'fill="{color}"{border}{corner}{alpha}/>'
        )

    def text(self, x, y, value, size=12, color=MUTED, weight=400, anchor="start",
             mono=False, family=None, italic=False) -> None:
        font = family or (MONO if mono else None)
        extra = f' font-family="{font}"' if font else ""
        if italic:
            extra += ' font-style="italic"'
        self.raw(
            f'<text x="{x:.2f}" y="{y:.2f}" fill="{color}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{extra}>{escape(str(value))}</text>'
        )

    def math(self, x, y, value, size=16, anchor="start", color=INK) -> None:
        self.text(x, y, value, size, color, 400, anchor, family=SERIF, italic=True)

    def circle(self, x, y, r, fill, stroke=None, width=1) -> None:
        border = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        self.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}"{border}/>')

    def polyline(self, points, color, width=1.6, opacity=1) -> None:
        pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        self.raw(
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round" opacity="{opacity}"/>'
        )

    def tag(self, x, y, value) -> float:
        """Provenance pill (saved, reconstructed, …); y is the text baseline."""
        w = text_width(value, 10, mono=True) + 14
        self.rect(x, y - 11.5, w, 16, PANEL, rx=8)
        self.text(x + 7, y, value, 10, MUTED, 500, mono=True)
        return w

    def label(self, x, y, value, tag=None, size=12.5) -> None:
        self.text(x, y, value, size, INK, 600)
        if tag:
            self.tag(x + text_width(value, size, weight=600) + 9, y - 0.5, tag)

    def swatch(self, x, y, color, value, shape="square") -> float:
        """Legend entry; y is the text baseline. Returns the entry width."""
        if shape == "dot":
            self.circle(x + 4.5, y - 4, 4.5, color)
        elif shape == "ring":
            self.circle(x + 4.5, y - 4, 3.8, PAPER, color, 1.8)
        elif shape == "line":
            self.line(x, y - 4, x + 14, y - 4, color, 2.2, cap="round")
            x += 5
        else:
            self.rect(x, y - 8.5, 9, 9, color, rx=2)
        self.text(x + 15, y, value, 11.5, INK2)
        return 15 + text_width(value, 11.5) + 18

    def diverging_legend(self, x, y, w, limit, fmt=lambda v: f"{v:g}", label=None) -> None:
        """Horizontal blue → gray → rust scale bar; y is the bar's top edge."""
        self.gradients += 1
        gid = f"scale{self.gradients}"
        self.raw(
            f'<defs><linearGradient id="{gid}" x1="0" x2="1" y1="0" y2="0">'
            f'<stop offset="0" stop-color="{NEG}"/><stop offset=".5" stop-color="{MID}"/>'
            f'<stop offset="1" stop-color="{POS}"/></linearGradient></defs>'
        )
        self.raw(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="6" rx="3" fill="url(#{gid})"/>')
        for frac, value in ((0, -limit), (.5, 0), (1, limit)):
            anchor = ("start", "middle", "end")[int(frac * 2)]
            shown = "0" if value == 0 else ("−" if value < 0 else "+") + fmt(abs(value))
            self.text(x + w * frac, y + 20, shown, 10, MUTED, 400, anchor, mono=True)
        if label:
            self.text(x + w / 2, y - 7, label, 10.5, MUTED, 400, "middle")

    def save(self, figure_id: str) -> None:
        self.raw("</svg>")
        name = f"sleep-figure-{figure_id}.svg"
        (OUT / name).write_text("\n".join(self.parts) + "\n")


def heatmap(svg: SVG, values, x, y, size, limit=1.0, gap=1.5) -> None:
    rows, cols = len(values), len(values[0])
    pitch = size / cols
    assert math.isclose(size / rows, pitch, rel_tol=1e-9), "matrix cells must be square"
    for row, values_row in enumerate(values):
        for col, value in enumerate(values_row):
            svg.rect(x + col * pitch, y + row * pitch, pitch - gap, pitch - gap,
                     diverge(value, limit), rx=1.5)


def arrow(svg: SVG, x1, y1, x2, y2, color=FAINT, width=1.2) -> None:
    svg.line(x1, y1, x2, y2, color, width, cap="round")
    angle = math.atan2(y2 - y1, x2 - x1)
    a, b = angle + 2.55, angle - 2.55
    svg.polyline([(x2 + 6 * math.cos(a), y2 + 6 * math.sin(a)), (x2, y2),
                  (x2 + 6 * math.cos(b), y2 + 6 * math.sin(b))], color, width)


def percentages(values) -> list[float]:
    """Round four probabilities to tenths while keeping their sum at 100.0%."""
    scaled = [value / sum(values) * 1000 for value in values]
    tenths = [math.floor(value) for value in scaled]
    missing = 1000 - sum(tenths)
    order = sorted(range(len(values)), key=lambda i: scaled[i] - tenths[i], reverse=True)
    for i in order[:missing]:
        tenths[i] += 1
    return [value / 10 for value in tenths]


def probability_label(value: float) -> str:
    return "<0.1%" if 0 < value < 0.0005 else f"{value * 100:.1f}%"


def dumbbells(svg: SVG, raw, calibrated, temperature, x0, x1, top, pitch, value_x) -> None:
    """Raw (ring) → calibrated (dot) per stage on one shared 0–100% axis."""
    def px(value: float) -> float:
        return x0 + (x1 - x0) * value
    bottom = top + pitch * 3 + 16
    for tick in (0, .25, .5, .75, 1):
        svg.line(px(tick), top - 16, px(tick), bottom, GRID if 0 < tick < 1 else AXIS, 1)
        if tick in (0, .5, 1):
            svg.text(px(tick), bottom + 15, f"{tick * 100:.0f}%", 10, MUTED, 400, "middle", mono=True)
    svg.text(value_x, top - 22, "raw → calibrated", 10, MUTED, 500, "end", mono=True)
    for i, (name, before, after) in enumerate(zip(STAGES, raw, calibrated)):
        y = top + i * pitch
        color = STAGE_COLORS[i]
        svg.text(x0 - 14, y + 4, name, 12, INK, 600, "end")
        svg.line(px(before), y, px(after), y, color, 2.4, .45, cap="round")
        svg.circle(px(before), y, 4.4, PAPER, color, 1.8)
        svg.circle(px(after), y, 5.6, PAPER)
        svg.circle(px(after), y, 4.6, color)
        svg.text(value_x - 60, y + 4, probability_label(before), 11, MUTED, 400, "end", mono=True)
        svg.text(value_x - 48, y + 4, "→", 11, FAINT, 400, "middle")
        svg.text(value_x, y + 4, probability_label(after), 11, INK, 600, "end", mono=True)
    entry = svg.swatch(x0, top - 40, MUTED, "raw", "ring")
    svg.swatch(x0 + entry, top - 40, MUTED, f"calibrated · T = {temperature:.3f}", "dot")


def visual_01() -> None:
    s = SVG("Overlapping causal fMRI windows", "A schematic 35-volume timeline shows two 30-volume windows at endpoints five volumes apart. Below it, three reconstructed standardized network means (Auditory, None, and Visual) and a motion-validity strip show the current representative window. The endpoint sleep label is not an input.", 322)
    s.label(20, 26, "Window selection", "schematic")
    x0, dx = 150, 14
    def fx(frame: int) -> float:
        return x0 + frame * dx
    s.text(138, 59, "prior t−5", 12, INK2, 500, "end")
    s.text(138, 83, "current t", 12, INK2, 500, "end")
    for i in range(35):
        if i < 30:
            s.rect(fx(i), 49, dx - 2, 12, GRAY_LIGHT, rx=2)
        else:
            s.rect(fx(i) + .5, 49.5, dx - 3, 11, PAPER, LINE, 1, rx=2)
        if i >= 5:
            s.rect(fx(i), 73, dx - 2, 12, ACCENT, rx=2)
        else:
            s.rect(fx(i) + .5, 73.5, dx - 3, 11, PAPER, LINE, 1, rx=2)
    # Stride bracket between the two endpoints; overlap bracket below.
    s.polyline([(fx(30) - 1, 44), (fx(30) - 1, 40), (fx(35) - 2, 40), (fx(35) - 2, 44)], FAINT, 1)
    s.text((fx(30) + fx(35)) / 2 - 1, 34, "stride 5", 10.5, MUTED, 400, "middle")
    s.polyline([(fx(5), 92), (fx(5), 96), (fx(30) - 2, 96), (fx(30) - 2, 92)], FAINT, 1)
    s.text((fx(5) + fx(30)) / 2, 112, "25 overlapping frames", 11, MUTED, 400, "middle")
    s.line(fx(35) - 1, 68, fx(35) - 1, 90, ACCENT, 1.4)
    s.text(fx(35) + 10, 83, "endpoint t", 11.5, INK2, 500)

    features = DATA["step_1_window"]["cortical_features"]
    valid = DATA["step_1_window"]["motion_valid"]
    s.label(20, 152, "Current window signals", "reconstructed")
    centers = [fx(5 + k) + (dx - 2) / 2 for k in range(30)]
    for center, index in ((190, 0), (228, 6), (266, 12)):
        s.line(centers[0], center, centers[-1], center, GRID, 1)
        s.text(206, center - 2, f"mean {index + 1:02d}", 11.5, INK2, 500, "end")
        s.text(206, center + 12, NETWORK_ORDER[index], 10.5, MUTED, 400, "end")
        s.polyline([(centers[frame], center - max(-3, min(3, row[index])) * 5.5)
                    for frame, row in enumerate(features)], INK2, 1.6)
    s.text(206, 306, "FD < 0.2 mm", 11, MUTED, 400, "end")
    for frame, passed in enumerate(valid):
        s.rect(fx(5 + frame), 298, dx - 2, 8, ACCENT_LIGHT if passed else POS, rx=1.5)
    s.text(fx(35) + 10, 306, f"{sum(valid)}/30 valid", 11, MUTED, 400, mono=False)
    s.line(fx(35) - 1, 170, fx(35) - 1, 286, ACCENT, 1.4)
    s.text(fx(35) + 10, 194, "predict", 11.5, INK2, 600)
    s.text(fx(35) + 10, 210, "endpoint label", 10.5, MUTED)
    s.text(fx(35) + 10, 224, "scores only;", 10.5, MUTED)
    s.text(fx(35) + 10, 238, "never an input", 10.5, MUTED)
    s.save("01-01")


def visual_02() -> None:
    s = SVG("Default-network residual modes", "The Default community contains 41 of the Gordon atlas's 333 cortical parcels. Each of its 41 parcel rows has a loading on each of two fold-trained residual principal components, so the basis is 41 by 2. Six numeric rows are shown; all 41 loadings of each component are separately tiled in atlas order into square-cell grids. Three reconstructed standardized held-out traces show its network mean and two residual scores across 30 frames.", 264)
    basis = SUPPLEMENT["network_basis"]
    assert basis["chosen_network"] == "Default" and basis["chosen_network_parcels"] == 41
    loadings = basis["top_two_loadings_in_atlas_parcel_order"]
    assert len(loadings) == 41 and all(len(row) == 2 for row in loadings)
    s.label(20, 26, "First 6 of 41 parcels")
    s.text(132, 56, "PC 1", 10.5, MUTED, 500, "end", mono=True)
    s.text(186, 56, "PC 2", 10.5, MUTED, 500, "end", mono=True)
    s.line(20, 64, 188, 64, AXIS, 1)
    for i, row in enumerate(loadings[:6]):
        y = 84 + i * 26
        s.text(20, y, f"parcel {i+1:02d}", 11.5, MUTED)
        s.text(132, y, f"{row[0]:+.2f}", 12, INK, 500, "end", mono=True)
        s.text(186, y, f"{row[1]:+.2f}", 12, INK, 500, "end", mono=True)
        s.line(20, y + 9, 188, y + 9, LINE, 1)
    s.line(214, 14, 214, 250, LINE)
    s.label(234, 26, "41 loadings per PC")
    limit = max(abs(v) for row in loadings for v in row)
    for k, x0 in ((0, 236), (1, 322)):
        s.text(x0, 56, f"PC {k+1}", 10.5, MUTED, 500, mono=True)
        for parcel, row in enumerate(loadings):
            col, grid_row = parcel % 6, parcel // 6
            s.rect(x0 + col * 12.5, 66 + grid_row * 12.5, 11, 11, diverge(row[k], limit), rx=1.5)
        s.text(x0, 168, "01 → 41", 10, FAINT, 400, mono=True)
    s.diverging_legend(236, 186, 160, limit, lambda v: f"{v:.2f}")
    s.text(236, 232, "tiled in atlas parcel order", 11, MUTED)
    s.text(236, 248, "each tile = one loading", 11, MUTED)
    s.line(420, 14, 420, 250, LINE)
    s.label(440, 26, "Held-out output", "reconstructed")
    features = DATA["step_1_window"]["cortical_features"]
    for center, index, name in ((84, 3, "mean"), (148, 19, "PC 1"), (212, 20, "PC 2")):
        s.text(480, center + 4, name, 11.5, INK2, 500, "end")
        s.line(492, center, 740, center, GRID)
        s.polyline([(492 + 248 * u / 29, center - max(-3, min(3, row[index])) * 9.5)
                    for u, row in enumerate(features)], INK2, 1.6)
    s.text(492, 252, "frame 1", 10.5, MUTED)
    s.text(740, 252, "frame 30", 10.5, MUTED, 400, "end")
    s.save("02-04")


def visual_network_inventory() -> None:
    """Show every atlas community and its contribution to the 39 channels."""
    basis = SUPPLEMENT["network_basis"]
    names = basis["network_order"]
    counts = basis["parcel_counts"]
    assert len(names) == len(counts) == 13 and sum(counts) == 333
    display = {
        "CinguloOperc": "Cingulo-opercular",
        "ParietalMemoryNetwork": "Parietal memory",
        "DorsalAttn": "Dorsal attention",
        "FrontoParietal": "Frontoparietal",
        "None": "None (atlas label)",
        "RetrosplenialTemporal": "Retrosplenial temporal",
        "SMhand": "Somatomotor hand",
        "SMmouth": "Somatomotor mouth",
        "VentralAttn": "Ventral attention",
    }
    s = SVG(
        "Gordon atlas network inventory and 39 signal channels",
        "All 13 Gordon atlas communities and their actual parcel counts, totaling 333. "
        "Each community contributes one parcel-mean signal and two residual PCA scores "
        "per fMRI volume, for 13 mean signals plus 26 residual signals. "
        "The atlas community called None is a real category, not missing data. "
        "The Default community, used in Figure 02.4, is highlighted.",
        354,
    )
    s.text(20, 26, "atlas community", 10.5, MUTED, 500, mono=True)
    s.text(196, 26, "parcels", 10.5, MUTED, 500, mono=True)
    s.text(560, 26, "signals per volume", 10.5, MUTED, 500, mono=True)
    channel_x = (560, 616, 672)
    channel_colors = (ACCENT, ACCENT_LIGHT, ACCENT_PALE)
    for x, label, color in zip(channel_x, ("mean", "PC 1", "PC 2"), channel_colors):
        s.swatch(x, 48, color, label)
    s.line(20, 58, 740, 58, AXIS)
    bar_w = 280
    for i, (name, count) in enumerate(zip(names, counts)):
        y = 70 + i * 19
        chosen = name == "Default"
        s.text(20, y + 9.5, display.get(name, name), 12, INK if chosen else INK2, 600 if chosen else 400)
        width = bar_w * count / max(counts)
        s.rect(196, y + 1, width, 11, ACCENT if chosen else GRAY_LIGHT, rx=2)
        s.text(196 + width + 7, y + 10.5, count, 11, INK if chosen else MUTED, 600 if chosen else 400, mono=True)
        for x, color in zip(channel_x, channel_colors):
            s.rect(x, y + 1.5, 10, 10, color, rx=2)
    s.line(20, 320, 740, 320, AXIS)
    s.text(20, 342, "13 communities", 12, INK, 600)
    s.text(196, 342, "333 parcels", 11.5, INK, 600, mono=True)
    s.text(740, 342, "39 = 13 means + 26 PC scores", 11.5, INK, 600, "end", mono=True)
    s.save("02-05")


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


def toy_matrix(s, values, x0, y0, cell=34, gap=4, fmt=str, tint=False, limit=None):
    """Numeric matrix; neutral cells for raw values, diverging tints for signed ones."""
    top = limit or max(abs(v) for r in values for v in r)
    size = 11.5 if max(len(fmt(v)) for r in values for v in r) <= 3 else 10.5
    for i, row in enumerate(values):
        for j, value in enumerate(row):
            left, y = x0 + j * (cell + gap), y0 + i * (cell + gap)
            fill = toy_fill(value, top) if tint else PANEL
            s.rect(left, y, cell, cell, fill, rx=4)
            s.text(left + cell / 2, y + cell / 2 + 4, fmt(value), size,
                   cell_text_color(fill) if tint else INK, 600, "middle", mono=True)
    return len(values[0]) * (cell + gap) - gap, len(values) * (cell + gap) - gap


def signed(value) -> str:
    return "0" if value == 0 else f"{value:+g}".replace("-", "−")


def visual_parcel_projection() -> None:
    x, means, residuals, _, _, _, _, _ = toy_pca()
    s = SVG("Same-volume parcel mean subtraction",
            "Illustrative four-volume, four-parcel matrix. Each row's four parcel values are averaged. Subtracting that row's own mean from all four values produces residuals that sum to zero. In the first row, 8, 6, 3, 3 have mean 5 and residuals 3, 1, minus 2, minus 2.", 282)
    ox, top = 130, 54
    w, h = toy_matrix(s, x, ox, top)
    s.math(ox, 38, "X")
    s.text(ox + w / 2, top + h + 22, "measured parcel values", 11.5, MUTED, 400, "middle")
    s.text(ox + w + 24, top + h / 2 + 7, "−", 22, MUTED, 300, "middle")
    mx = ox + w + 48
    toy_matrix(s, [[v] for v in means], mx, top, fmt=lambda v: f"{v:g}")
    s.math(mx, 38, "m")
    s.text(mx + 17, top + h + 22, "same-volume mean", 11.5, MUTED, 400, "middle")
    s.text(mx + 58, top + h / 2 + 7, "=", 22, MUTED, 300, "middle")
    ex = mx + 82
    toy_matrix(s, residuals, ex, top, fmt=signed, tint=True)
    s.math(ex, 38, "E")
    s.text(ex + w / 2, top + h + 22, "parcel residuals", 11.5, MUTED, 400, "middle")
    sx = ex + w + 30
    s.text(sx + 12, 38, "Σ", 15, INK, 400, "middle", family=SERIF)
    for i, row in enumerate(residuals):
        s.text(sx + 12, top + i * 38 + 21, signed(sum(row)), 11.5, MUTED, 500, "middle", mono=True)
    s.text(sx + 12, top + h + 22, "row sums", 11.5, MUTED, 400, "middle")
    for left, width in ((ox, w), (mx, 34), (ex, w)):
        s.rect(left - 3.5, top - 3.5, width + 7, 41, "none", ACCENT, 1.4, rx=6)
    s.text(ox, 262, "First volume", 12, INK, 600)
    s.text(ox + 92, 262, "(8, 6, 3, 3) − (5, 5, 5, 5) = (3, 1, −2, −2)", 12, INK2, 400, mono=True)
    s.save("02-01")


def visual_toy_pca_fit() -> None:
    _, _, residuals, reference, centered, covariance, components, _ = toy_pca()
    s = SVG("How training residuals determine PCA components",
            "Illustrative training calculation for four volumes and four parcels. The training residual mean is [1, minus 1, 0, 0]. Subtracting this reference from each residual row gives centered patterns [2, 2, minus 2, minus 2], [minus 2, minus 2, 2, 2], [1, minus 1, 1, minus 1], and [minus 1, 1, minus 1, 1]. Their covariance is C transpose C divided by four. Its two leading eigenvectors form a four-by-two component matrix, with eigenvalues 8 and 2.", 290)
    s.label(20, 26, "Training reference")
    s.text(20, 48, "μ = mean of residual rows = (1, −1, 0, 0)", 12, INK2, 400, mono=True)
    top, cell, gap = 104, 34, 4
    w, h = toy_matrix(s, centered, 20, top, cell, gap, fmt=signed, tint=True)
    s.math(20, 92, "E − μ")
    s.text(72, 92, "4 × 4", 10.5, MUTED, 400, mono=True)
    s.text(20, top + h + 22, "centered training patterns", 11.5, MUTED)
    arrow(s, 20 + w + 14, top + h / 2, 20 + w + 64, top + h / 2)
    s.text(20 + w + 39, top + h / 2 - 10, "CᵀC / 4", 10.5, MUTED, 500, "middle", mono=True)
    kx = 20 + w + 78
    toy_matrix(s, covariance, kx, top, cell, gap, fmt=lambda v: f"{v:g}".replace("-", "−"), tint=True)
    s.math(kx, 92, "K")
    s.text(kx + 18, 92, "4 × 4", 10.5, MUTED, 400, mono=True)
    s.text(kx, top + h + 22, "parcel covariance", 11.5, MUTED)
    arrow(s, kx + w + 14, top + h / 2, kx + w + 64, top + h / 2)
    s.text(kx + w + 39, top + h / 2 - 10, "top 2", 10.5, MUTED, 500, "middle", mono=True)
    ux = kx + w + 78
    uw, _ = toy_matrix(s, components, ux, top, cell, gap,
                       fmt=lambda v: f"{v:+.1f}".replace("-", "−"), tint=True)
    s.math(ux, 76, "U")
    s.text(ux + 16, 76, "4 × 2", 10.5, MUTED, 400, mono=True)
    s.text(ux + cell / 2, 96, "PC 1", 10, MUTED, 500, "middle", mono=True)
    s.text(ux + cell + gap + cell / 2, 96, "PC 2", 10, MUTED, 500, "middle", mono=True)
    s.text(ux, top + h + 22, "learned components", 11.5, MUTED)
    ax = ux + uw + 26
    s.text(ax, top + 18, "PC 1", 12, INK, 600)
    s.text(ax, top + 36, "(+, +, −, −)", 11.5, INK2, 400, mono=True)
    s.text(ax, top + 70, "PC 2", 12, INK, 600)
    s.text(ax, top + 88, "(+, −, +, −)", 11.5, INK2, 400, mono=True)
    s.text(ax, top + 124, "λ₁ = 8 · λ₂ = 2", 11.5, MUTED, 400, mono=True)
    s.save("02-02")


def visual_toy_pca_scores() -> None:
    _, _, _, _, centered, _, components, scores = toy_pca()
    s = SVG("One volume becomes one PCA point",
            "Illustrative PCA projection for volume one only. Its centered parcel residuals are [2, 2, minus 2, minus 2]. The fitted PC1 weights are [0.5, 0.5, minus 0.5, minus 0.5], giving score 4. The fitted PC2 weights are [0.5, minus 0.5, 0.5, minus 0.5], giving score zero. One point at horizontal PC1 coordinate 4 and vertical PC2 coordinate zero represents this one volume; the other three training volumes are intentionally omitted.", 262)
    s.label(20, 26, "Volume 1 · centered residual")
    s.math(20, 66, "e − μ", 15)
    for j, value in enumerate(centered[0]):
        fill = toy_fill(value, 2)
        x = 104 + 40 * j
        s.rect(x, 42, 34, 34, fill, rx=4)
        s.text(x + 17, 63, signed(value), 11.5, cell_text_color(fill), 600, "middle", mono=True)
    s.label(20, 116, "Fitted parcel weights")
    for k, y in ((0, 130), (1, 184)):
        s.text(20, y + 22, f"PC {k+1}", 12, INK2, 600)
        for j in range(4):
            value = components[j][k]
            fill = toy_fill(value, .5)
            x = 104 + 40 * j
            s.rect(x, y, 34, 34, fill, rx=4)
            s.text(x + 17, y + 21, f"{value:+.1f}".replace("-", "−"), 11.5, cell_text_color(fill), 600, "middle", mono=True)
        s.text(286, y + 22, f"dot = {scores[0][k]:g}", 12, INK, 600, mono=True)
    s.line(410, 14, 410, 244, LINE)
    s.label(434, 26, "One volume · one point")
    ox, oy, unit = 540, 146, 36
    s.line(452, oy, 734, oy, AXIS, 1)
    s.line(ox, 228, ox, 58, AXIS, 1)
    arrow(s, 726, oy, 736, oy, AXIS)
    arrow(s, ox, 66, ox, 56, AXIS)
    s.text(736, oy + 20, "PC 1", 11, INK2, 600, "end", mono=True)
    s.text(ox + 9, 62, "PC 2", 11, INK2, 600, mono=True)
    s.text(ox - 7, oy + 16, "0", 10.5, MUTED, 400, "end", mono=True)
    px = ox + unit * scores[0][0]
    s.line(px, oy - 5, px, oy + 5, AXIS, 1)
    s.text(px, oy + 20, "4", 10.5, MUTED, 400, "middle", mono=True)
    s.circle(px, oy, 8.5, PAPER)
    s.circle(px, oy, 6.5, ACCENT)
    s.text(px, oy - 16, "(+4, 0)", 12, INK, 600, "middle", mono=True)
    s.text(px, oy + 38, "volume 1", 11, MUTED, 500, "middle")
    s.text(434, 248, "PC 2 = 0: no vertical displacement", 11, MUTED)
    s.save("02-03")


SUBSET_NAMES = ["Aud mean", "Def mean", "Vis mean", "Aud PC1", "Def PC1", "Def PC2"]


def visual_03() -> None:
    s = SVG("Shrinkage connectivity from a short window", "Six selected features from the full 39-feature operation show sample covariance, reconstructed Ledoit-Wolf shrinkage covariance, and final correlation. Rows are Auditory, Default, and Visual means, Auditory and Default residual PC1, and Default residual PC2. The saved shrinkage fraction for this window is 0.1511; eigenvalue flooring made no change.", 282)
    features = DATA["step_1_window"]["cortical_features"]
    valid = DATA["step_1_window"]["motion_valid"]
    selected = [row for row, ok in zip(features, valid) if ok]
    assert len(selected) == SUPPLEMENT["window_shrinkage_connectivity"]["valid_feature_rows"]
    indices = SUPPLEMENT["window_shrinkage_connectivity"]["subset_feature_indices"]
    assert indices == [0, 3, 12, 13, 19, 20]
    means = [sum(row[j] for row in selected) / len(selected) for j in indices]
    sample = [[sum((row[i] - means[a]) * (row[j] - means[b]) for row in selected) / len(selected)
               for b, j in enumerate(indices)] for a, i in enumerate(indices)]
    w = SUPPLEMENT["window_shrinkage_connectivity"]
    shrink = w["ledoit_wolf_covariance_subset"]
    corr = w["stabilized_correlation_subset"]
    limit = max(abs(v) for matrix in (sample, shrink) for row in matrix for v in row)
    size, top = 144, 50
    for x, matrix, label, sublabel, scale in (
        (100, sample, "Sample covariance", "S · 30 valid frames", limit),
        (348, shrink, "Shrinkage covariance", "(1−λ)S + λμI", limit),
        (596, corr, "Correlation state", "D⁻¹ᐟ² Σ D⁻¹ᐟ²", 1),
    ):
        s.text(x + size / 2, 32, label, 12.5, INK, 600, "middle")
        heatmap(s, matrix, x, top, size, scale)
        s.text(x + size / 2, top + size + 22, sublabel, 11, MUTED, 400, "middle", mono=True)
    for i, name in enumerate(SUBSET_NAMES):
        s.text(92, top + i * 24 + 15.5, name, 10.5, MUTED, 400, "end", mono=True)
    arrow(s, 256, top + size / 2, 336, top + size / 2)
    s.text(296, top + size / 2 - 10, f"λ = {w['ledoit_wolf_shrinkage']:.3f}", 10.5, INK2, 500, "middle", mono=True)
    arrow(s, 504, top + size / 2, 584, top + size / 2)
    s.text(544, top + size / 2 - 10, "normalize", 10.5, INK2, 500, "middle", mono=True)
    s.diverging_legend(172, 248, 248, limit, lambda v: f"{v:.1f}", "covariance scale · both covariance panels")
    s.diverging_legend(596, 248, 144, 1, lambda v: f"{v:g}", "correlation scale")
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


SUPERSCRIPT = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def visual_shrinkage_spectrum() -> None:
    s = SVG("Shrinkage lifts the zero eigenvalues of a short-window covariance", "An eigenvalue spectrum reconstructed from this 30-valid-frame, 39-signal window compares sample covariance with its actual Ledoit-Wolf shrinkage covariance. The ordinary sample matrix has ten near-zero eigenvalues; shrinkage makes every eigenvalue positive.", 268)
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
    s.label(20, 26, "Covariance eigenvalues · log scale", "reconstructed")
    entry = s.swatch(470, 26, GRAY, "sample", "line")
    s.swatch(470 + entry, 26, ACCENT, "Ledoit–Wolf shrinkage", "line")
    x0, x1, y0, y1 = 66, 596, 52, 220
    ceiling = 10 ** math.ceil(math.log10(max(sample[0], shrunk[0])))
    floor = 1e-8
    def yy(value: float) -> float:
        return y1 - (math.log10(max(floor, value)) - math.log10(floor)) / (math.log10(ceiling) - math.log10(floor)) * (y1 - y0)
    def xx(rank: int) -> float:
        return x0 + (rank - 1) * (x1 - x0) / 38
    s.rect(xx(30), y0, x1 - xx(30), y1 - y0, PANEL)
    s.text((xx(30) + x1) / 2, y0 + 16, "10 null directions", 10.5, MUTED, 500, "middle")
    for exponent in range(-8, int(round(math.log10(ceiling))) + 1, 2):
        y = yy(10 ** exponent)
        s.line(x0, y, x1, y, GRID, 1)
        s.text(x0 - 8, y + 4, "10" + str(exponent).translate(SUPERSCRIPT), 10.5, MUTED, 400, "end", mono=True)
    s.line(x0, y1, x1, y1, AXIS, 1)
    for rank in (1, 10, 20, 30, 39):
        s.text(xx(rank), y1 + 17, str(rank), 10.5, MUTED, 400, "middle", mono=True)
    s.text(x1, y1 + 36, "eigenvalue rank", 11, MUTED, 400, "end")
    for values, color in ((sample, GRAY), (shrunk, ACCENT)):
        s.polyline([(xx(i + 1), yy(value)) for i, value in enumerate(values)], color, 2)
    s.circle(xx(39), yy(shrunk[-1]), 4, ACCENT, PAPER, 2)
    s.circle(xx(39), yy(sample[-1]), 4, GRAY, PAPER, 2)
    s.text(x1 + 14, yy(shrunk[-1]) - 2, "shrinkage", 11.5, INK, 600)
    s.text(x1 + 14, yy(shrunk[-1]) + 13, f"λ = {lam:.3f}", 11, MUTED, 400, mono=True)
    s.text(x1 + 14, yy(sample[-1]) - 10, "sample", 11.5, INK, 600)
    s.text(x1 + 14, yy(sample[-1]) + 5, "10 near zero", 11, MUTED)
    s.save("03-01")


def visual_04() -> None:
    s = SVG("Lag-specific tangent references", "At each of the current, 25-volume, and 50-volume lags, a reconstructed correlation is compared with its reconstructed fold-trained reference to produce a tangent matrix. Six-by-six excerpts are shown from the full 39-by-39 matrices. All three tangents become 2340 coordinates, clipped and reduced to 64 whitened PCA scores.", 344)
    records = SUPPLEMENT["lag_geometry"]["lag_records"]
    indices = SUPPLEMENT["lag_geometry"]["subset_feature_indices"]
    matrices = DATA["step_3_causal_lags"]["correlations"]
    s.label(20, 26, "Six-channel excerpts", "reconstructed")
    xs, ys, size = (196, 290, 384), (62, 146, 230), 66
    for col, (x, rec, matrix) in enumerate(zip(xs, records, matrices)):
        s.text(x + size / 2, 52, ("now", "−25 volumes", "−50 volumes")[col], 11.5, INK2, 600, "middle")
        snippets = ([[matrix[i][j] for j in indices] for i in indices],
                    rec["reference_subset"], rec["tangent_subset"])
        for y, subset in zip((ys[0] + 4, ys[1] + 4, ys[2] + 4), snippets):
            heatmap(s, subset, x, y, size, 1, gap=1.2)
    for y, symbol, label, note in ((ys[0], "C", "state", "this window"),
                                   (ys[1], "G", "reference", "training"),
                                   (ys[2], "T", "tangent", "log map")):
        s.math(20, y + 36, symbol, 17)
        s.text(40, y + 34, label, 12, INK, 600)
        s.text(40, y + 50, note, 11, MUTED)
    s.diverging_legend(196, 316, 254, 1, lambda v: f"{v:g}")
    s.line(482, 14, 482, 330, LINE)
    s.label(504, 26, "PCA output", "reconstructed")
    s.text(504, 56, "3 × 780 → 2,340", 11, INK2, 500, mono=True)
    s.text(504, 74, "clip → PCA → 64", 11, INK2, 500, mono=True)
    scores = DATA["step_5_pca"]["whitened_score"]
    for i, value in enumerate(scores):
        col, row = i % 8, i // 8
        s.rect(540 + col * 16, 96 + row * 16, 14.5, 14.5, diverge(value, 2.5), rx=2)
    s.text(540 + 64, 246, "64 whitened scores", 11, MUTED, 400, "middle")
    s.diverging_legend(540, 316, 127, 2.5, lambda v: f"{v:g}")
    s.save("04-01")


def visual_05() -> None:
    s = SVG("Tangent decoder and temperature calibration", "The reconstructed 64 whitened tangent scores enter shrinkage LDA. Saved uncalibrated and calibrated stage probabilities are compared directly on one axis. The fitted tangent temperature is 2.114, softening this representative prediction.", 274)
    p = SUPPLEMENT["probability_calibration"]
    scores = DATA["step_5_pca"]["whitened_score"]
    s.label(20, 26, "64 PCA scores", "reconstructed")
    for i, value in enumerate(scores):
        col, row = i % 8, i // 8
        s.rect(20 + col * 15, 52 + row * 15, 13.5, 13.5, diverge(value, 2.5), rx=2)
    s.diverging_legend(20, 186, 118, 2.5, lambda v: f"{v:g}")
    arrow(s, 152, 112, 186, 112)
    s.rect(194, 76, 100, 72, PANEL, rx=10)
    s.text(244, 98, "shrinkage", 10.5, MUTED, 500, "middle")
    s.text(244, 119, "LDA", 17, INK, 600, "middle")
    s.text(244, 137, "equal priors", 10.5, MUTED, 400, "middle")
    arrow(s, 302, 112, 336, 112)
    s.line(352, 14, 352, 258, LINE)
    s.label(374, 26, "Stage probabilities", "saved")
    dumbbells(s, p["tangent_raw_probability"], p["tangent_calibrated_probability"],
              p["tangent_temperature"], 420, 620, 98, 38, 740)
    s.text(374, 262, f"Temperature T = {p['tangent_temperature']:.3f} softens this window’s LDA output.", 11, MUTED)
    s.save("05-01")


HODGE = (("H harmonic", ACCENT), ("G gradient", GRAY), ("C curl", GRAY_LIGHT))


def visual_06() -> None:
    s = SVG("Lagged edge flow and Hodge energy", "At left, schematic forward and reverse cross-lag parcel interactions define one antisymmetric edge flow. At right, saved harmonic, gradient, and curl energy fractions from the representative window are shown for three lags and their pooled flow, followed by the three saved temporal change features.", 262)
    s.label(20, 26, "One edge · cross-lag pairs", "schematic")
    for y, left, right, label, color in (
        (78, "i at u", "j at u + τ", "forward", INK2),
        (128, "j at u", "i at u + τ", "reverse", FAINT),
    ):
        s.circle(26, y - 4, 4.5, PAPER, color, 1.6)
        s.text(38, y, left, 12, INK, 500)
        arrow(s, 92, y - 4, 196, y - 4, color, 1.4)
        s.circle(208, y - 4, 4.5, PAPER, color, 1.6)
        s.text(220, y, right, 12, INK, 500)
        s.text(144, y - 14, label, 10.5, MUTED, 400, "middle")
    s.line(20, 152, 320, 152, LINE)
    s.text(20, 180, "edge flow = forward − reverse", 13, INK, 600)
    s.text(20, 204, "τ = 1, 2, 3 volumes; valid pairs only", 11.5, MUTED)
    s.text(20, 224, "Then project flow onto H, G, and C spaces.", 11.5, MUTED)
    s.line(344, 14, 344, 248, LINE)

    values = DATA["step_7_cycle_ridge"]["feature_values"]
    s.label(366, 26, "Hodge energy shares", "saved")
    cursor = 414
    for name, color in HODGE:
        cursor += s.swatch(cursor, 54, color, name)
    left, right = 414, 740
    for row, name in enumerate(("lag 1", "lag 2", "lag 3", "pooled")):
        y = 72 + row * 32
        s.text(left - 12, y + 14, name, 12, INK2, 500, "end")
        fractions = values[row * 5 + 2:row * 5 + 5]
        total = sum(fractions)
        cursor = left
        span = right - left - 2 * 2
        for fraction, (_, color) in zip(fractions, HODGE):
            width = span * fraction / total
            s.rect(cursor, y, width, 20, color, rx=3)
            share = f"{fraction * 100:.1f}%"
            if width > text_width(share, 10.5, mono=True) + 16:
                s.text(cursor + width / 2, y + 14, share, 10.5, cell_text_color(color), 500, "middle", mono=True)
            cursor += width + 2
    s.line(366, 214, 740, 214, LINE)
    s.text(366, 240, f"Δ norm {values[20]:.2f}   ·   cosine {values[21]:.2f}   ·   angle {values[22]:.2f} rad", 11.5, INK2, 500, mono=True)
    s.save("06-02")


def visual_atlas_graph() -> None:
    s = SVG("Actual cortical atlas graph used for signed edge flows", "All 333 Gordon cortical parcels and all 1152 actual undirected six-nearest-neighbor graph edges are shown in a two-dimensional projection of public MNI atlas coordinates. Default-network nodes are highlighted. Neighbor selection was performed in original three-dimensional coordinate space; directionality enters only when lagged signal flow is assigned to edges.", 276)
    assert TOPOLOGY["topology"]["nodes"] == 333
    assert TOPOLOGY["topology"]["edges"] == 1152
    assert TOPOLOGY["topology"]["triangles"] == 986
    points = TOPOLOGY["node_xy"]
    networks = TOPOLOGY["node_network"]
    edges = TOPOLOGY["edges"]
    assert len(points) == len(networks) == 333 and len(edges) == 1152
    default_index = TOPOLOGY["network_names"].index("Default")
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    box = (24, 18, 440, 258)
    scale = min((box[2] - box[0]) / (max(xs) - min(xs)), (box[3] - box[1]) / (max(ys) - min(ys)))
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    mx, my = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    def xy(i: int) -> tuple[float, float]:
        px, py = points[i]
        return cx + (px - mx) * scale, cy - (py - my) * scale
    for i, j in edges:
        s.line(*xy(i), *xy(j), EDGE, 0.6)
    for i in range(333):
        if networks[i] != default_index:
            s.circle(*xy(i), 1.5, GRAY)
    for i in range(333):
        if networks[i] == default_index:
            s.circle(*xy(i), 3.2, PAPER)
            s.circle(*xy(i), 2.4, ACCENT)
    s.line(472, 14, 472, 262, LINE)
    s.label(494, 26, "Fixed graph construction", "actual")
    for y, quantity, label in ((76, "333", "cortical parcels"),
                               (118, "6", "nearest neighbors in 3D"),
                               (160, "1,152", "undirected edges"),
                               (202, "986", "filled triangles")):
        s.text(494, y, quantity, 22, INK, 500)
        s.text(574, y - 1, label, 12, MUTED)
    s.circle(498.5, 242, 4, ACCENT)
    s.text(510, 246, "Default network highlighted", 11.5, INK2)
    s.save("06-01")


def visual_cycle_feature_map() -> None:
    s = SVG("The 23 saved cycle features", "A compact numerical map of all 23 saved directed-cycle features for the representative window: five flow summaries at each of three lags, five for their weighted pooled flow, and three temporal change summaries. Share columns carry small bars proportional to each fraction of total flow energy.", 254)
    values = DATA["step_7_cycle_ridge"]["feature_values"]
    columns = (("total norm", None), ("harmonic norm", None),
               ("H share", HODGE[0][1]), ("G share", HODGE[1][1]), ("C share", HODGE[2][1]))
    centers = [196 + j * 124 for j in range(5)]
    for (label, color), x in zip(columns, centers):
        offset = 0
        if color:
            offset = 8
            s.rect(x - text_width(label, 11.5, weight=600) / 2 - 8, 26 - 8.5, 9, 9, color, rx=2)
        s.text(x + offset / 2 + 2, 26, label, 11.5, INK, 600, "middle")
    s.line(20, 40, 740, 40, AXIS)
    for i, label in enumerate(("lag 1", "lag 2", "lag 3", "pooled")):
        y = 70 + i * 38
        s.text(20, y, label, 12.5, INK2, 600)
        for j in range(5):
            value = values[i * 5 + j]
            displayed = f"{value * 100:.1f}%" if j >= 2 else f"{value:.2f}"
            s.text(centers[j], y, displayed, 13, INK, 500, "middle", mono=True)
            if j >= 2:
                s.rect(centers[j] - 36, y + 7, 72, 3, GRID, rx=1.5)
                s.rect(centers[j] - 36, y + 7, max(2, 72 * value), 3, columns[j][1], rx=1.5)
        s.line(20, y + 18, 740, y + 18, LINE)
    s.text(20, 232, "change in pooled", 12, INK2, 600)
    s.text(20, 247, "harmonic state", 12, INK2, 600)
    for x, text in zip(centers, (f"norm {values[20]:.2f}", f"cosine {values[21]:.2f}",
                                 f"angle {values[22]:.2f} rad")):
        s.text(x, 240, text, 12, INK, 500, "middle", mono=True)
    s.save("06-03")


def visual_cycle_calibration() -> None:
    s = SVG("Cycle branch before and after calibration", "The same representative held-out window has saved raw and calibrated Wake, N1, N2, and N3 cycle-branch probabilities on one axis. The fitted cycle temperature is 0.888, which modestly sharpens these probabilities.", 238)
    p = SUPPLEMENT["probability_calibration"]
    s.label(20, 26, "Class-balanced logistic output", "saved")
    dumbbells(s, p["cycle_raw_probability"], p["cycle_calibrated_probability"],
              p["cycle_temperature"], 80, 560, 90, 34, 740)
    s.text(740, 50, f"T = {p['cycle_temperature']:.3f} modestly sharpens these probabilities", 11, MUTED, 400, "end")
    s.save("06-04")


def visual_07() -> None:
    s = SVG("Weighted blend then final calibration", "Saved tangent, cycle, and final four-stage probability vectors, drawn as stacked strips that sum to 100 percent, with a derived pre-temperature weighted mixture for the same window. The cycle weight is 0.30. Exact percentages are listed at right.", 240)
    alpha = DATA["step_8_blend_simplex"]["cycle_weight"]
    tangent = DATA["step_6_tangent_lda"]["probability"]
    cycle = DATA["step_7_cycle_ridge"]["probability"]
    mix = [(1 - alpha) * a + alpha * b for a, b in zip(tangent, cycle)]
    final = DATA["step_8_blend_simplex"]["final_probability"]
    temperature = SUPPLEMENT["probability_calibration"]["final_blend_temperature"]
    cursor = 136
    for name, color in zip(STAGES, STAGE_COLORS):
        cursor += s.swatch(cursor, 26, color, name, "dot") - 4
    value_x = (594, 642, 690, 738)
    for x, name in zip(value_x, STAGES):
        s.text(x, 26, name, 10.5, MUTED, 500, "end", mono=True)
    rows = [
        ("tangent", tangent, "saved", 48),
        ("cycle", cycle, "saved", 86),
        ("mix q", mix, "derived", 146),
        ("final p", final, "saved", 206),
    ]
    left, right = 136, 548
    for name, probabilities, source, y in rows:
        s.text(20, y + 14, name, 12.5, INK, 600)
        s.tag(20 + text_width(name, 12.5, weight=600) + 8, y + 14, source)
        span = right - left - 3 * 2
        cursor = left
        for col, value in enumerate(probabilities):
            width = span * value
            s.rect(cursor, y, width, 20, STAGE_COLORS[col], rx=3 if width > 6 else 0)
            cursor += width + 2
        displayed = percentages(probabilities)
        for x, value in zip(value_x, displayed):
            s.text(x, y + 14, f"{value:.1f}%", 11, INK, 500, "end", mono=True)
    s.text(left, 128, f"q = (1 − α)·tangent + α·cycle,  α = {alpha:.2f}", 11, MUTED, 400, mono=True)
    s.text(left, 188, f"p = temperature-calibrated q,  T = {temperature:.3f}", 11, MUTED, 400, mono=True)
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
    for fn in (visual_01, visual_02, visual_network_inventory, visual_03, visual_04,
               visual_05, visual_06, visual_07):
        fn()
    for fn in (visual_parcel_projection, visual_toy_pca_fit, visual_toy_pca_scores,
               visual_shrinkage_spectrum, visual_atlas_graph,
               visual_cycle_feature_map, visual_cycle_calibration):
        fn()
    print("Built fifteen sleep-method SVGs from the validated representative export and atlas topology.")
