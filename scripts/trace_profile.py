"""Extract a left-facing facial contour from a warm subject on a pale background.

Usage:
  python trace_profile.py reference.png [--overlay /tmp/profile-check.png]

Prints simplified source and 320x420 card coordinates as JSON. The reference
image and optional diagnostic overlay are never added to the website.
Requires NumPy and Pillow. The color threshold and crop bounds are tuned to
this supplied reference; they should be reviewed before tracing another photo.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Interpreted anatomical landmarks in the supplied 500 x 603 photograph.
# The hairline is the skin/hair boundary, not the crown. The jaw follows the
# lower face from the chin toward the mandibular angle; the ear is excluded.
HAIRLINE = [(166, 108), (181, 100), (198, 96), (214, 102),
            (231, 117), (240, 137), (253, 157), (268, 178)]
JAW = [(119, 369), (138, 374), (168, 377), (195, 370),
       (221, 353), (243, 333), (263, 307)]


def card_points(points):
    return [[round(35 + (x - 70) * 0.70, 2), round(50 + (y - 20) * 0.68, 2)] for x, y in points]


def distance(point, start, end):
    vx, vy = end[0] - start[0], end[1] - start[1]
    if vx == vy == 0:
        return float(np.hypot(point[0] - start[0], point[1] - start[1]))
    t = max(0, min(1, ((point[0] - start[0]) * vx + (point[1] - start[1]) * vy) / (vx * vx + vy * vy)))
    return float(np.hypot(point[0] - start[0] - t * vx, point[1] - start[1] - t * vy))


def simplify(points, tolerance):
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    index = max(range(1, len(points) - 1), key=lambda i: distance(points[i], start, end))
    if distance(points[index], start, end) <= tolerance:
        return [start, end]
    return simplify(points[: index + 1], tolerance)[:-1] + simplify(points[index:], tolerance)


def trace(image):
    rgb = np.asarray(image.convert("RGB").filter(ImageFilter.GaussianBlur(1.3)), dtype=np.float32)
    red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    foreground = ((red - green > 11) & (red - blue > 7)) | (rgb.mean(axis=2) < 75)
    edges = []
    for y in range(30, 371):
        # A dark architectural stripe occupies x≈145 above the forehead.
        minimum_x = int(np.interp(y, [30, 100, 130], [205, 165, 140])) if y < 130 else 70
        for x in range(minimum_x, min(360, image.width - 5)):
            if foreground[y - 2 : y + 3, x : x + 5].sum() >= 18:
                edges.append((x, y))
                break
    xs = np.array([x for x, _ in edges], dtype=np.float32)
    # Median rejects isolated dark pixels; a short binomial pass softens stair steps.
    xs = np.array([np.median(xs[max(0, i - 2) : i + 3]) for i in range(len(xs))])
    xs = np.convolve(np.pad(xs, (2, 2), mode="edge"), [1 / 16, 4 / 16, 6 / 16, 4 / 16, 1 / 16], mode="valid")
    smoothed = [(float(x), y) for x, (_, y) in zip(xs, edges)]
    return simplify(smoothed, 1.35), smoothed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("--overlay", type=Path)
    args = parser.parse_args()
    image = Image.open(args.reference)
    points, full = trace(image)
    if args.overlay:
        overlay = image.convert("RGB")
        draw = ImageDraw.Draw(overlay)
        draw.line(full, fill="#e02130", width=2)
        for x, y in points:
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill="#00ddff")
        draw.line(HAIRLINE, fill="#f5c400", width=2)
        draw.line(JAW, fill="#28e0a7", width=2)
        for x, y in HAIRLINE + JAW:
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill="#ffffff")
        overlay.save(args.overlay)
    # Fixed map gives the source photo a stable coordinate system in the card.
    print(json.dumps({"source_size": list(image.size), "source_points": points,
                      "card_points": card_points(points),
                      "hairline_card_points": card_points(HAIRLINE),
                      "jaw_card_points": card_points(JAW)}, indent=2))


if __name__ == "__main__":
    main()
