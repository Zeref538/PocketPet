# PocketPet

A small virtual-pet game in Unity.

## What's here

- `art/source/pet_sheet.png`: the original sheet, 8 animations x 6 frames
- `art/frames/`: one PNG per frame, all 202x187, named `<animation>_<frame>.png`
- `tools/slice_pet.py`: re-cuts the sheet into frames (`python tools/slice_pet.py`)

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
2. Select all 48 PNGs. In the Inspector set **Texture Type** to **Sprite (2D and UI)**.
3. Set **Filter Mode** to **Point (no filter)** so the pixels stay sharp.
4. Set **Compression** to **None**, then click **Apply**.
5. Select the 6 frames of one animation (for example `idle_01` to `idle_06`) and drag them into the Scene. Unity asks where to save the animation clip.
