"""Cut art/source/ui_sheet.png into one PNG per UI piece, trimmed tight.

Each separate piece goes whole to the slot that holds most of its pixels
(so a loose sparkle joins the button beside it). A piece split across two
rows (the bath buttons, joined by their bubbles) is cut at the row line.

Run:  python tools/slice_ui.py
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = "art/source/ui_sheet.png"
OUT = "art/ui"
PAD = 2

# Row bands (y ranges) and the names of the pieces in each, left to right.
ROWS = [
    ((0, 266), ["button_home", "button_food", "button_love", "button_bath", "button_play"]),
    ((266, 478), ["button_home_pressed", "button_food_pressed", "button_love_pressed",
                  "button_bath_pressed", "button_play_pressed"]),
    ((478, 618), ["icon_paw", "icon_heart", "icon_star", "icon_fish", "icon_yarn",
                  "icon_bubbles", "icon_book", "icon_gear", "icon_gear_small", "icon_gift"]),
    ((618, 745), ["square_home", "square_food", "square_love", "square_bath", "square_play",
                  "square_paw", "square_book", "square_settings", "square_gift", "square_close"]),
    ((745, 884), ["round_home", "round_food", "round_love", "round_bath", "round_play",
                  "round_paw", "round_book", "round_settings", "round_gift", "round_close"]),
    ((884, 1024), ["bar_paw", "bar_heart", "bar_star", "speech_bubble"]),
]

img = np.array(Image.open(SRC).convert("RGBA"))
H, W = img.shape[:2]
solid = img[..., 3] > 40
lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=2))
lab = np.where(img[..., 3] > 0, lab, 0)            # labels only where there is paint

# Slots: in each row, the big pieces set the column borders (midpoints).
slot = np.full((H, W), -1, int)
names = []
for (y0, y1), row_names in ROWS:
    band = lab[y0:y1]
    sizes = np.bincount(band.ravel())
    sizes[0] = 0
    big = [i for i in np.nonzero(sizes > 5000)[0]]
    centres = sorted(np.nonzero(band == i)[1].mean() for i in big)
    assert len(centres) == len(row_names), f"row {y0}: {len(centres)} pieces, expected {len(row_names)}"
    edges = [0] + [int((a + b) / 2) for a, b in zip(centres, centres[1:])] + [W]
    for k, name in enumerate(row_names):
        slot[y0:y1, edges[k]:edges[k + 1]] = len(names)
        names.append(name)

# Owner of each piece = the slot with most of its pixels; split only if
# no slot holds 90% of it.
owner = np.full((H, W), -1, int)
for i in range(1, n + 1):
    ys, xs = np.nonzero(lab == i)
    if len(ys) == 0:
        continue
    counts = np.bincount(slot[ys, xs] + 1)[1:]
    if counts.max() >= 0.9 * len(ys):
        owner[ys, xs] = counts.argmax()
    else:
        owner[ys, xs] = slot[ys, xs]

os.makedirs(OUT, exist_ok=True)
for k, name in enumerate(names):
    ys, xs = np.nonzero(owner == k)
    piece = np.zeros_like(img)
    piece[ys, xs] = img[ys, xs]
    y0, y1 = max(0, ys.min() - PAD), min(H, ys.max() + 1 + PAD)
    x0, x1 = max(0, xs.min() - PAD), min(W, xs.max() + 1 + PAD)
    Image.fromarray(piece[y0:y1, x0:x1]).save(f"{OUT}/{name}.png")
total = int((img[..., 3] > 40).sum())
kept = sum(int((np.array(Image.open(f"{OUT}/{nm}.png"))[..., 3] > 40).sum()) for nm in names)
print(f"{len(names)} pieces; visible pixels sheet {total}, pieces {kept}, missing {total - kept}")
