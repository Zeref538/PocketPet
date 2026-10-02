# PocketPet

A small virtual-pet game in Unity.

## What's here

Five pets, each with idle, happy, sad, crying, eating, playing, studying and sleeping.

- `art/source/pet_sheet.png`: the wolf sheet, 6 frames per animation
- `art/source/hamster_sheet.png`: the hamster sheet, 4 frames per animation (eating has 5)
- `art/frames/wolf/`: 48 frames, all 202x187
- `art/frames/hamster/`: 33 frames, all 208x187
- `art/source/otter_sheet.png` and `art/frames/otter/`: 64 frames (8 per animation), all 185x142
- `art/source/pup_sheet.png` and `art/frames/pup/`: 48 frames (6 per animation), all 294x149, feet pinned to the same spot
- `art/source/bunny_sheet.png` and `art/frames/bunny/`: 32 frames (4 per animation), all 137x107
- Frames are named `<animation>_<frame>.png`, for example `idle_01.png`
- `art/source/ui_sheet.png` and `art/ui/`: 44 UI pieces (buttons, pressed buttons, icons, square and round buttons, bars, speech bubble), also in `Game/Assets/Sprites/UI/`
- `tools/slice_*.py` re-cut each sheet into frames (`python tools/slice_grid.py pup` or `bunny`)

## Import the pup project into Unity

The Unity project is the `Game` folder. It is a **Universal 2D** project (URP with the 2D Renderer), set up the same way as Shadow, using **Unity 6000.5.10f1**.

### 1. Get the files

Clone the repo (see [Get a copy](#get-a-copy) below) or download the ZIP and unzip it.

### 2. Add the project

1. Open **Unity Hub** and click **Projects** on the left.
2. Click **Add**, then **Add project from disk**.
3. Pick the `Game` folder inside `PocketPet`. Not `PocketPet` itself: Hub only accepts a folder that has `Assets`, `Packages` and `ProjectSettings` directly inside it.
4. Make sure the version shown is **6000.5.10f1**, then click the project to open it.
5. The first open takes a few minutes while Unity builds its `Library` cache.

### 3. See the animations

1. In the **Project** window, open `Assets/Scenes/SampleScene.unity`. It has the Main Camera, the Global Light 2D and the **Pup**.
2. Press **Play**. The pup plays its idle animation in place.
3. To watch the others: click **Pup**, open **Window > Animation > Animator**, and change the **Mood** number (0 to 7) while playing.

What is where:

- `Assets/Sprites/Pup/`: the 48 frames, set to Point filter (sharp pixels) with the pivot at the feet
- `Assets/Animations/Pup/`: the 8 clips and `Pup.controller`
- Every frame has the pup's feet on the same spot, so it animates without sliding around

### Use it in your own code

The Animator has one number, `Mood`. Set it to switch animation:

```csharp
GetComponent<Animator>().SetInteger("Mood", 4);   // 4 = eating
```

0 idle, 1 happy, 2 sad, 3 crying, 4 eating, 5 playing, 6 studying, 7 sleeping.

To rebuild the clips after changing frames: menu **PocketPet > Build Pup**.

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
