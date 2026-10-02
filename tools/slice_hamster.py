"""Cut art/source/hamster_sheet.png into one PNG per frame.

This sheet has two animations per row, a text label above each, and not
every animation has the same number of frames (eating has 5). So frames are
found by shape, not by a grid:

- every separate blob of pixels is found
- labels (short, wide strips) are dropped
- each big blob is one frame of the pet
- each small blob (tear, sparkle, Zzz, bulb) joins the nearest frame in its
  own animation

Within one animation, every frame keeps its height above the shared floor
line, so a jump still rises and lands when played in order.

Run:  python tools/slice_hamster.py
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = "art/source/hamster_sheet.png"
OUT = "art/frames/hamster"
# (row, half) -> animation name; half 0 = left side of the sheet
NAMES = {(0, 0): "idle", (0, 1): "happy", (1, 0): "sad", (1, 1): "crying",
         (2, 0): "eating", (2, 1): "playing", (3, 0): "studying", (3, 1): "sleeping"}
EXPECT = {"eating": 5}          # every other animation has 4

img = Image.open(SRC).convert("RGBA")
rgba = np.array(img)
H, W = rgba.shape[:2]
solid = rgba[..., 3] > 0
lab, n = ndimage.label(ndimage.binary_dilation(rgba[..., 3] > 60, iterations=4))
blobs = []
for i, s in enumerate(ndimage.find_objects(lab), 1):
    area = int((lab[s] == i).sum())
    h, w = s[0].stop - s[0].start, s[1].stop - s[1].start
    if area < 150 or (h < 40 and w > 60):          # dust, or a text label
        continue
    cy, cx = (s[0].start + s[0].stop) / 2, (s[1].start + s[1].stop) / 2
    blobs.append(dict(id=i, s=s, area=area, cx=cx, cy=cy,
                      key=(int(cy // (H / 4)), int(cx >= W / 2))))

frames = {}
for b in sorted((b for b in blobs if b["area"] > 12000), key=lambda b: b["cx"]):
    frames.setdefault(b["key"], []).append(dict(ids=[b["id"]], cx=b["cx"], cy=b["cy"]))
for b in (b for b in blobs if b["area"] <= 12000):
    group = frames[b["key"]]
    min(group, key=lambda f: (f["cx"] - b["cx"]) ** 2 + (f["cy"] - b["cy"]) ** 2)["ids"].append(b["id"])

for key, name in NAMES.items():
    want = EXPECT.get(name, 4)
    assert len(frames[key]) == want, f"{name}: found {len(frames[key])} frames, expected {want}"

# Cut every frame by its own pixels; note each one's box.
cuts = []
for key, group in frames.items():
    for f in group:
        mask = np.isin(lab, f["ids"]) & solid
        ys, xs = np.nonzero(mask)
        piece = rgba.copy()
        piece[..., 3] = np.where(mask, piece[..., 3], 0)
        box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        cuts.append((key, Image.fromarray(piece).crop(box), box))

# One canvas size for all; each animation shares a floor line.
floor = {k: max(c[2][3] for c in cuts if c[0] == k) for k in frames}
lift = max(floor[k] - box[1] for k, _, box in cuts)     # tallest frame above its floor
cw = max(p.width for _, p, _ in cuts) + 8
ch = lift + 8
os.makedirs(OUT, exist_ok=True)
count = {}
for key, piece, box in cuts:
    name = NAMES[key]
    count[name] = count.get(name, 0) + 1
    frame = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    bottom_gap = floor[key] - box[3]            # how far above the floor it sits
    frame.alpha_composite(piece, ((cw - piece.width) // 2, ch - 4 - bottom_gap - piece.height))
    frame.save(f"{OUT}/{name}_{count[name]:02d}.png")
print(f"{len(cuts)} frames, each {cw}x{ch}:", count)
