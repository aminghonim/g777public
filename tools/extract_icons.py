#!/usr/bin/env python3
"""Extract hexagon icons and their inner symbolic shapes from a screenshot.

Usage:
  python tools/extract_icons.py --input path/to/image.png --output out/icons

The script will try to detect neon-cyan hexagon borders, crop each detected
hexagon (with padding), and produce a PNG per icon where the background is
transparent and the inner symbol pixels are preserved exactly.

This is a best-effort, pixel-preserving extractor using only Pillow + numpy.
"""
from __future__ import annotations

import argparse
import os
from typing import List, Tuple

import numpy as np
from PIL import Image


def load_image(path: str) -> np.ndarray:
    img = Image.open(path).convert("RGBA")
    return np.array(img)


def neon_multicolor_mask(arr: np.ndarray) -> np.ndarray:
    """Return boolean mask for any vibrant neon-colored pixels.
    
    Detects Cyan, Purple, Orange, etc. by looking for high saturation and brightness.
    """
    r = arr[..., 0].astype(int)
    g = arr[..., 1].astype(int)
    b = arr[..., 2].astype(int)

    # Brightness check
    bright = (r + g + b) > 120
    
    # Saturation/Vibrancy check: look for high difference between channels
    # Neon colors have at least one or two very high channels and one low channel
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    vibrant = (max_c - min_c) > 60  # Only colorful pixels
    
    # Exclude near-white (backgrounds)
    not_white = (r < 240) | (g < 240) | (b < 240)

    mask = bright & vibrant & not_white
    return mask


def find_components(mask: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """Find bounding boxes of connected components in boolean mask.

    Returns list of (minx, miny, maxx, maxy) in image coords.
    """
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    boxes = []

    for y in range(h):
        for x in range(w):
            if mask[y, x] and not visited[y, x]:
                # flood fill
                stack = [(x, y)]
                visited[y, x] = True
                minx = maxx = x
                miny = maxy = y
                while stack:
                    sx, sy = stack.pop()
                    for nx in (sx - 1, sx, sx + 1):
                        for ny in (sy - 1, sy, sy + 1):
                            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                                continue
                            if not visited[ny, nx] and mask[ny, nx]:
                                visited[ny, nx] = True
                                stack.append((nx, ny))
                                minx = min(minx, nx)
                                maxx = max(maxx, nx)
                                miny = min(miny, ny)
                                maxy = max(maxy, ny)
                boxes.append((minx, miny, maxx + 1, maxy + 1))
    return boxes


def expand_box(box: Tuple[int, int, int, int], img_w: int, img_h: int, pad: int = 12):
    x0, y0, x1, y1 = box
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(img_w, x1 + pad)
    y1 = min(img_h, y1 + pad)
    return (x0, y0, x1, y1)


def preserve_symbol(crop_arr: np.ndarray, border_mask_crop: np.ndarray) -> Image.Image:
    """Create an RGBA PIL image where non-border pixels inside crop are preserved,
    and background is made transparent using border_mask to separate icon area.
    """
    # Build an alpha mask where either the pixel is non-background (not white/black)
    # or inside the hexagon area defined by dilation of the border mask.
    rgba = crop_arr.copy()
    h, w = border_mask_crop.shape

    # Create interior mask by filling holes: simple approach - invert border and flood fill
    interior = ~border_mask_crop

    # Use alpha from source luminance: preserve any pixel not near background
    r = rgba[..., 0].astype(int)
    g = rgba[..., 1].astype(int)
    b = rgba[..., 2].astype(int)
    lum = (r + g + b) / 3
    foreground = lum < 240  # not near white

    final_mask = interior & foreground

    out = Image.fromarray(rgba, mode="RGBA")
    alpha = np.array(out.split()[-1])
    alpha[~final_mask] = 0
    out.putalpha(Image.fromarray(alpha))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="path to screenshot image")
    p.add_argument("--output", default="out/icons", help="output directory")
    p.add_argument("--pad", type=int, default=12, help="padding around detected box")
    args = p.parse_args()

    arr = load_image(args.input)
    mask = neon_multicolor_mask(arr)
    boxes = find_components(mask)

    if not boxes:
        print(
            "No neon hexagon borders detected. Try increasing image contrast or use a crop."
        )
        return

    # User Request: Filter icons to target the main 8-12 hex icons and ignore noise
    # We look for boxes with width and height between a reasonable range (e.g. 50-250px)
    # and a somewhat square aspect ratio.
    filtered_boxes = []
    for b in boxes:
        x0, y0, x1, y1 = b
        bw = x1 - x0
        bh = y1 - y0
        area = bw * bh
        aspect = bw / bh if bh > 0 else 0
        
        # Heuristic for main G777 Hex icons (Lowered to 30 for smaller screenshots)
        if 30 < bw < 300 and 30 < bh < 300 and 0.7 < aspect < 1.4:
            filtered_boxes.append(b)

    if not filtered_boxes:
        print("Borders detected, but none matched the Size Filter criteria (60px-300px, square-ish).")
        print(f"Total raw boxes found: {len(boxes)}")
        if boxes:
            print("First 5 raw box sizes (w, h):", [(b[2]-b[0], b[3]-b[1]) for b in boxes[:5]])
        return

    print(f"Filtering complete: Extracted {len(filtered_boxes)} high-quality candidates from {len(boxes)} raw components.")

    h, w = mask.shape
    for i, b in enumerate(filtered_boxes, start=1):
        eb = expand_box(b, w, h, pad=args.pad)
        x0, y0, x1, y1 = eb
        crop = arr[y0:y1, x0:x1]
        border_crop = mask[y0:y1, x0:x1]
        out_img = preserve_symbol(crop, border_crop)
        out_path = os.path.join(args.output, f"refined_icon_{i:02d}.png")
        out_img.save(out_path)
        print(f"Saved: {out_path} ({x1-x0}x{y1-y0} px)")


if __name__ == "__main__":
    main()
