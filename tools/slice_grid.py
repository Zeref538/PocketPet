"""Cut a grid-style sprite sheet into one PNG per frame.

Used for sheets where frames touch their neighbours, so the pieces can't be
found as separate blobs. Each grid line is placed at the emptiest line within
SEARCH pixels of where it should be, so a cut runs through the gap between
two frames instead of through a tail.

Each frame is placed by where its IDEAL cell starts, not by where its own
cut landed, so a jump still rises and lands when the frames play in order.
At the end every frame of the pet is trimmed to one shared box.

Run:  python tools/slice_grid.py pup
      python tools/slice_grid.py bunny
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

SEARCH = 25
ORDER = ["idle", "happy", "sad", "crying", "eating", "playing", "studying", "sleeping"]


def pup():
    """8 rows x 6 frames, one animation per row, transparent background."""
    rgba = np.array(Image.open("art/source/pup_sheet.png").convert("RGBA"))
    H, W = rgba.shape[:2]
    cells = []
    xs = [round(W * k / 6) for k in range(7)]
    ys = [round(H * k / 8) for k in range(9)]
    for r, name in enumerate(ORDER):
        for c in range(6):
            cells.append((name, c + 1, (xs[c], ys[r], xs[c + 1], ys[r + 1])))
    return rgba, cells


def bunny():
    """Two blocks of 4 columns; each column is one animation, frames go DOWN.
    Solid black background, a title banner over each column, numbers 1-4."""
    rgba = np.array(Image.open("art/source/bunny_sheet.png").convert("RGBA"))
    H, W = rgba.shape[:2]
    # Colour key: pure black becomes transparent. 70% of pixels are <= 5,
    # outlines and floor shadows sit well above 12, so they stay.
    rgba[..., 3] = np.where(rgba[..., :3].max(2) <= 12, 0, 255)

    # Drop banners (wide and short) and the grey frame numbers (small, at
    # the far left of each column).
    lab, n = ndimage.label(ndimage.binary_dilation(rgba[..., 3] > 0, iterations=2))
    col_w = W / 4
    for i, s in enumerate(ndimage.find_objects(lab), 1):
        h, w = s[0].stop - s[0].start, s[1].stop - s[1].start
        col_left = (s[1].start // col_w) * col_w
        banner = h < 50 and w > 150
        number = w < 22 and h < 26 and s[1].stop <= col_left + 45
        if banner or number:
            rgba[s][lab[s] == i, 3] = 0

    xs = [round(col_w * k) for k in range(5)]
    blocks = [(50, [146, 240, 338], 445), (495, [586, 683, 778], H)]
    cells = []
    for b, (top, mids, bottom) in enumerate(blocks):
        ys = [top] + mids + [bottom]
        for c in range(4):
            name = ORDER[b * 4 + c]
            for k in range(4):
                cells.append((name, k + 1, (xs[c], ys[k], xs[c + 1], ys[k + 1])))
    return rgba, cells


def valley(profile, guess, lo, hi):
    """Emptiest line within SEARCH of the guess, kept inside [lo, hi]."""
    a, b = max(lo, guess - SEARCH), min(hi, guess + SEARCH)
    if b <= a:
        return guess
    return a + int(np.argmin(profile[a:b]))


def main(pet):
    rgba, cells = {"pup": pup, "bunny": bunny}[pet]()
    solid = rgba[..., 3] > 0
    H, W = solid.shape
    out = f"art/frames/{pet}"
    os.makedirs(out, exist_ok=True)

    pieces = []
    for name, k, (x0, y0, x1, y1) in cells:
        # Snap each edge to the emptiest nearby line inside this cell's strip.
        rows = solid[max(0, y0 - SEARCH):min(H, y1 + SEARCH), x0:x1]
        cols = solid[y0:y1, max(0, x0 - SEARCH):min(W, x1 + SEARCH)]
        ry = rows.sum(1); oy = max(0, y0 - SEARCH)
        cx = cols.sum(0); ox = max(0, x0 - SEARCH)
        top = valley(ry, y0 - oy, 0, len(ry)) + oy if y0 > 0 else 0
        bot = valley(ry, y1 - oy, 0, len(ry)) + oy if y1 < H else H
        left = valley(cx, x0 - ox, 0, len(cx)) + ox if x0 > 0 else 0
        right = valley(cx, x1 - ox, 0, len(cx)) + ox if x1 < W else W
        crop = rgba[top:bot, left:right].copy()
        # A neighbour's tail or ball that crosses the cut leaves a sliver on
        # this side. Pieces are judged on clearly visible pixels only
        # (alpha > 40): the image AI leaves near-invisible alpha-1 trails
        # that would otherwise glue a sliver to the pet's body.
        lab, n = ndimage.label(crop[..., 3] > 40)
        if n > 1:
            sizes = np.bincount(lab.ravel())[1:]
            # "Touching" means within 4px: the cut sits on the emptiest
            # line, so a sliver usually starts a pixel or two inside it.
            edge = set(np.unique(np.concatenate(
                [lab[:4].ravel(), lab[-4:].ravel(),
                 lab[:, :4].ravel(), lab[:, -4:].ravel()]))) - {0}
            drop = [i for i in edge if sizes[i - 1] < sizes.max() * 0.05]
            keep = (lab > 0) & ~np.isin(lab, drop)
            # keep faint edge pixels only next to a piece that stays
            crop[~ndimage.binary_dilation(keep, iterations=2), 3] = 0
        # Shift relative to the IDEAL cell so motion inside a row survives.
        pieces.append((name, k, crop, left - x0, top - y0, (x1 - x0, y1 - y0)))

    pad = SEARCH + 4
    cw = max(p[5][0] for p in pieces) + 2 * pad
    ch = max(p[5][1] for p in pieces) + 2 * pad
    canvases = []
    for name, k, crop, dx, dy, _ in pieces:
        canvas = np.zeros((ch, cw, 4), np.uint8)
        y, x = pad + dy, pad + dx
        canvas[y:y + crop.shape[0], x:x + crop.shape[1]] = crop
        canvases.append((name, k, canvas))

    # One shared box around every frame's content: same size, still aligned.
    union = np.zeros((ch, cw), bool)
    for _, _, c in canvases:
        union |= c[..., 3] > 40
    ys, xs = np.nonzero(union)
    box = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
    for name, k, c in canvases:
        Image.fromarray(c).crop(box).save(f"{out}/{name}_{k:02d}.png")
    print(f"{pet}: {len(canvases)} frames, each {box[2] - box[0]}x{box[3] - box[1]}")


if __name__ == "__main__":
    main(sys.argv[1])
