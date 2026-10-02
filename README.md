# PocketPet

A small virtual-pet game in Unity.

## What's here

Five pets, each with idle, happy, sad, crying, eating, playing, studying and sleeping.

- `art/source/pet_sheet.png`: the wolf sheet, 6 frames per animation
- `art/source/hamster_sheet.png`: the hamster sheet, 4 frames per animation (eating has 5)
- `art/frames/wolf/`: 48 frames, all 202x187
- `art/frames/hamster/`: 33 frames, all 208x187
- `art/source/otter_sheet.png` and `art/frames/otter/`: 64 frames (8 per animation), all 185x142
- `art/source/pup_sheet.png` and `art/frames/pup/`: 48 frames (6 per animation), all 249x153
- `art/source/bunny_sheet.png` and `art/frames/bunny/`: 32 frames (4 per animation), all 137x107
- Frames are named `<animation>_<frame>.png`, for example `idle_01.png`
- `tools/slice_*.py` re-cut each sheet into frames (`python tools/slice_grid.py pup` or `bunny`)

## Just the images

For a faster download with only the frames, use https://github.com/Zeref538/PocketPet-sprites

## Get a copy

### Clone it (stays linked to GitHub, so you can pull updates)

On a Mac, open **Terminal**. On Windows, open **Git Bash**.

```bash
cd ~/Desktop
git clone https://github.com/Zeref538/PocketPet.git
cd PocketPet
```

You now have a `PocketPet` folder on your Desktop.

To get newer changes later:

```bash
cd ~/Desktop/PocketPet
git pull
```

On Windows Command Prompt, `~` doesn't work. Use `cd %USERPROFILE%\Desktop` instead.

### Copy it without Git (download only)

1. Open https://github.com/Zeref538/PocketPet
2. Click the green **Code** button.
3. Click **Download ZIP**.
4. Unzip it where you want it.

A ZIP copy can't `git pull`. Download it again to get updates.

### Save your changes back to GitHub

```bash
git add -A
git commit -m "Say what you changed"
git push
```

If `git push` is refused, someone pushed first. Run `git pull`, then `git push` again.

## Use the frames in Unity

1. Drag `art/frames` into the Unity **Project** window.
2. Select all the PNGs in one pet's folder. In the Inspector set **Texture Type** to **Sprite (2D and UI)**.
3. Set **Filter Mode** to **Point (no filter)** so the pixels stay sharp.
4. Set **Compression** to **None**, then click **Apply**.
5. Select every frame of one animation (for example `idle_01` to `idle_04`) and drag them into the Scene. Unity asks where to save the animation clip.
