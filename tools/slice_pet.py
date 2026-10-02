"""Cut art/source/pet_sheet.png (8 rows x 6 frames) into one PNG per frame.

Rows are split at the empty gaps between them. Columns can't be split that
way, because sparkles and tails cross the borders, so each border is placed
at the emptiest column within 30px of where it should be (every width/6).

Every frame is padded to the same size, keeping where the pet sat inside its
cell, so a jump still rises and lands when the frames are played in order.

Run:  python tools/slice_pet.py
"""
import os
import numpy as np
from PIL import Image

SRC = "art/source/pet_sheet.png"
OUT = "art/frames/wolf"
ROWS = ["idle", "happy", "sad", "crying", "eating", "playing", "studying", "sleeping"]
COLS = 6

img = Image.open(SRC).convert("RGBA")
a = np.array(img)
solid = a[..., 3] > 40
H, W = solid.shape

# Row bands: runs of rows that contain something.
filled = solid.sum(1) > 0
bands, start = [], None
for y, f in enumerate(filled):
    if f and start is None:
        start = y
    if not f and start is not None:
        bands.append((start, y)); start = None
if start is not None:
    bands.append((start, H))
bands = [b for b in bands if b[1] - b[0] > 40]
assert len(bands) == len(ROWS), f"found {len(bands)} rows, expected {len(ROWS)}"

cells = []
for (y0, y1), name in zip(bands, ROWS):
    prof = solid[y0:y1].sum(0)
    cuts = [0]
    for k in range(1, COLS):
        guess = round(W * k / COLS)
        lo, hi = guess - 30, guess + 30
        cuts.append(lo + int(np.argmin(prof[lo:hi])))
    cuts.append(W)
    for i in range(COLS):
        cells.append((name, i + 1, cuts[i], y0, cuts[i + 1], y1))

cw = max(c[4] - c[2] for c in cells) + 8
ch = max(c[5] - c[3] for c in cells) + 8
os.makedirs(OUT, exist_ok=True)
for name, i, x0, y0, x1, y1 in cells:
    frame = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    piece = img.crop((x0, y0, x1, y1))
    # centre sideways, sit on the bottom: same anchor for every frame
    frame.alpha_composite(piece, ((cw - piece.width) // 2, ch - piece.height - 4))
    frame.save(f"{OUT}/{name}_{i:02d}.png")
print(f"{len(cells)} frames, each {cw}x{ch}")
