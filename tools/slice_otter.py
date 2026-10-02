"""Cut art/source/otter_sheet.png (8 rows x 8 frames) into one PNG per frame.

Rows are split at the empty gaps between them. Inside a row, sparkles and
tears cross the borders between frames, so a grid would slice them. Instead:
each big blob of pixels is one frame of the otter, and each small blob
(tear, sparkle, Zzz, bulb) joins the nearest otter in the same row.

Within a row, every frame keeps its height above the shared floor line, so
a jump still rises and lands when played in order.

Run:  python tools/slice_otter.py
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = "art/source/otter_sheet.png"
OUT = "art/frames/otter"
ROWS = ["idle", "happy", "sad", "crying", "eating", "playing", "studying", "sleeping"]
PER_ROW = 8
BIG = 6000          # pixels; an otter is 9,000-15,000, a tear or sparkle far less

img = Image.open(SRC).convert("RGBA")
rgba = np.array(img)
solid = rgba[..., 3] > 0
H, W = solid.shape

filled = (rgba[..., 3] > 60).sum(1) > 0
bands, start = [], None
for y, f in enumerate(filled):
    if f and start is None:
        start = y
    if not f and start is not None:
        bands.append((start, y)); start = None
bands = [b for b in bands if b[1] - b[0] > 20]
assert len(bands) == len(ROWS), f"found {len(bands)} rows, expected {len(ROWS)}"

lab, n = ndimage.label(ndimage.binary_dilation(rgba[..., 3] > 60, iterations=3))
blobs = []
for i, s in enumerate(ndimage.find_objects(lab), 1):
    area = int((lab[s] == i).sum())
    if area < 80:
        continue
    cy, cx = (s[0].start + s[0].stop) / 2, (s[1].start + s[1].stop) / 2
    row = min(range(len(bands)), key=lambda r: abs((bands[r][0] + bands[r][1]) / 2 - cy))
    blobs.append(dict(id=i, area=area, cx=cx, cy=cy, row=row))

frames = {r: [] for r in range(len(ROWS))}
for b in sorted((b for b in blobs if b["area"] > BIG), key=lambda b: b["cx"]):
    frames[b["row"]].append(dict(ids=[b["id"]], cx=b["cx"], cy=b["cy"]))
for r, name in enumerate(ROWS):
    assert len(frames[r]) == PER_ROW, f"{name}: found {len(frames[r])} frames, expected {PER_ROW}"
for b in (b for b in blobs if b["area"] <= BIG):
    min(frames[b["row"]], key=lambda f: (f["cx"] - b["cx"]) ** 2 + (f["cy"] - b["cy"]) ** 2)["ids"].append(b["id"])

cuts = []
for r, group in frames.items():
    for k, f in enumerate(group, 1):
        mask = np.isin(lab, f["ids"]) & solid
        ys, xs = np.nonzero(mask)
        piece = rgba.copy()
        piece[..., 3] = np.where(mask, piece[..., 3], 0)
        box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        cuts.append((r, k, Image.fromarray(piece).crop(box), box))

floor = {r: max(c[3][3] for c in cuts if c[0] == r) for r in frames}
cw = max(p.width for _, _, p, _ in cuts) + 8
ch = max(floor[r] - box[1] for r, _, _, box in cuts) + 8
os.makedirs(OUT, exist_ok=True)
for r, k, piece, box in cuts:
    frame = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    above_floor = floor[r] - box[3]
    frame.alpha_composite(piece, ((cw - piece.width) // 2, ch - 4 - above_floor - piece.height))
    frame.save(f"{OUT}/{ROWS[r]}_{k:02d}.png")
print(f"{len(cuts)} frames, each {cw}x{ch}")
