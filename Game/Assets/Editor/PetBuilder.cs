using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;

// Editor-only: turns the pup frames into 8 animation clips, an Animator that
// switches between them, and a test scene. Menu: PocketPet > Build Pup.
public static class PetBuilder
{
    const string Frames = "Assets/Sprites/Pup";
    const string AnimDir = "Assets/Animations/Pup";
    const string ScenePath = "Assets/Scenes/SampleScene.unity";

    // Order = the "Mood" number each animation answers to.
    // Frames per second: calm moods slower, lively ones faster.
    static readonly (string name, float fps)[] Moods =
    {
        ("idle", 6f), ("happy", 10f), ("sad", 5f), ("crying", 8f),
        ("eating", 8f), ("playing", 9f), ("studying", 5f), ("sleeping", 3f),
    };

    [MenuItem("PocketPet/Build Pup")]
    public static void Build()
    {
        ImportSettings();
        Directory.CreateDirectory(AnimDir);
        Directory.CreateDirectory(Path.GetDirectoryName(ScenePath));

        var controller = AnimatorController.CreateAnimatorControllerAtPath($"{AnimDir}/Pup.controller");
        controller.AddParameter("Mood", AnimatorControllerParameterType.Int);
        var machine = controller.layers[0].stateMachine;

        for (int i = 0; i < Moods.Length; i++)
        {
            var (name, fps) = Moods[i];
            var clip = MakeClip(name, fps);
            var state = machine.AddState(name);
            state.motion = clip;
            if (i == 0) machine.defaultState = state;

            // From anywhere, Mood == i jumps straight to this animation.
            var t = machine.AddAnyStateTransition(state);
            t.AddCondition(AnimatorConditionMode.Equals, i, "Mood");
            t.hasExitTime = false;
            t.duration = 0f;
            t.canTransitionToSelf = false;
        }

        MakeScene(controller);
        AssetDatabase.SaveAssets();
        Debug.Log("PetBuilder: pup built");
    }

    // Pixel art needs Point filtering (no blur) and no compression (no
    // colour smearing). Pivot at the bottom so the feet stay planted.
    static void ImportSettings()
    {
        foreach (var path in Directory.GetFiles(Frames, "*.png"))
        {
            var imp = (TextureImporter)AssetImporter.GetAtPath(path.Replace(Path.DirectorySeparatorChar, '/'));
            imp.textureType = TextureImporterType.Sprite;
            imp.spriteImportMode = SpriteImportMode.Single;
            imp.filterMode = FilterMode.Point;
            imp.textureCompression = TextureImporterCompression.Uncompressed;
            imp.mipmapEnabled = false;
            imp.spritePixelsPerUnit = 100f;
            var s = new TextureImporterSettings();
            imp.ReadTextureSettings(s);
            s.spriteAlignment = (int)SpriteAlignment.BottomCenter;
            imp.SetTextureSettings(s);
            imp.SaveAndReimport();
        }
    }

    static AnimationClip MakeClip(string name, float fps)
    {
        var sprites = Directory.GetFiles(Frames, name + "_*.png")
            .OrderBy(p => p)                                    // _01, _02 ... sort correctly
            .Select(p => AssetDatabase.LoadAssetAtPath<Sprite>(p.Replace(Path.DirectorySeparatorChar, '/')))
            .ToList();
        if (sprites.Count == 0) throw new System.Exception($"no frames for {name}");

        var keys = new List<ObjectReferenceKeyframe>();
        for (int i = 0; i < sprites.Count; i++)
            keys.Add(new ObjectReferenceKeyframe { time = i / fps, value = sprites[i] });
        // Repeat the last frame one step later, or it would flash for 0 seconds.
        keys.Add(new ObjectReferenceKeyframe { time = sprites.Count / fps, value = sprites[^1] });

        var clip = new AnimationClip { frameRate = fps };
        var binding = EditorCurveBinding.PPtrCurve("", typeof(SpriteRenderer), "m_Sprite");
        AnimationUtility.SetObjectReferenceCurve(clip, binding, keys.ToArray());
        var settings = AnimationUtility.GetAnimationClipSettings(clip);
        settings.loopTime = true;
        AnimationUtility.SetAnimationClipSettings(clip, settings);
        AssetDatabase.CreateAsset(clip, $"{AnimDir}/{name}.anim");
        return clip;
    }

    const string Rooms = "Assets/Sprites/Rooms";
    const string UI = "Assets/Sprites/UI";

    // The three buttons: UI picture name -> Mood it plays.
    static readonly (string button, int mood)[] Buttons =
    {
        ("food", 4),    // eating
        ("love", 1),    // happy
        ("play", 5),    // playing
    };

    // Uses the Universal 2D template's own SampleScene (Main Camera and
    // Global Light 2D already in it, same as Shadow) and adds the room,
    // the pup and three buttons.
    static void MakeScene(AnimatorController controller)
    {
        SpriteImports(Rooms, FilterMode.Point);       // pixel art: keep it sharp
        SpriteImports(UI, FilterMode.Bilinear);       // smooth painted buttons

        var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
        foreach (var name in new[] { "Pup", "Background", "Canvas", "EventSystem" })
        {
            var old = GameObject.Find(name);
            if (old != null) Object.DestroyImmediate(old);
        }

        var lit = AssetDatabase.LoadAssetAtPath<Material>(
            "Packages/com.unity.render-pipelines.universal/Runtime/Materials/Sprite-Lit-Default.mat");

        // Background: the bedroom, scaled to cover a 16:9 view of the
        // template camera (10 units tall), drawn behind everything.
        var cam = Camera.main;
        var bg = new GameObject("Background");
        var bgr = bg.AddComponent<SpriteRenderer>();
        bgr.sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{Rooms}/bedroom.png");
        bgr.sortingOrder = -10;
        if (lit != null) bgr.sharedMaterial = lit;
        float viewH = cam.orthographicSize * 2f, viewW = viewH * 16f / 9f;
        var size = bgr.sprite.bounds.size;
        float scale = Mathf.Max(viewH / size.y, viewW / size.x);
        bg.transform.localScale = Vector3.one * scale;
        bg.transform.position = Vector3.zero;

        // Pup: standing on the rug. At 3x it fills about half the screen.
        var pet = new GameObject("Pup");
        pet.transform.localScale = Vector3.one * 3f;
        pet.transform.position = new Vector3(0f, -3.3f, 0f);
        var sr = pet.AddComponent<SpriteRenderer>();
        sr.sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{Frames}/idle_01.png");
        if (lit != null) sr.sharedMaterial = lit;     // lit by the Global Light 2D
        var animator = pet.AddComponent<Animator>();
        animator.runtimeAnimatorController = controller;

        MakeButtons(animator);

        EditorSceneManager.SaveScene(scene, ScenePath);
        EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
    }

    static void MakeButtons(Animator animator)
    {
        // Canvas = the layer UI is drawn on, on top of the game. The scaler
        // keeps buttons the same size on any screen (designed for 1920x1080).
        var canvasGo = new GameObject("Canvas");
        var canvas = canvasGo.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        var scaler = canvasGo.AddComponent<UnityEngine.UI.CanvasScaler>();
        scaler.uiScaleMode = UnityEngine.UI.CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);
        scaler.matchWidthOrHeight = 0.5f;
        canvasGo.AddComponent<UnityEngine.UI.GraphicRaycaster>();
        var actions = canvasGo.AddComponent<PetButtons>();
        actions.pet = animator;

        // EventSystem = what turns mouse clicks and taps into button presses.
        // This project uses the Input System, so it needs its UI module.
        var events = new GameObject("EventSystem");
        events.AddComponent<UnityEngine.EventSystems.EventSystem>();
        events.AddComponent<UnityEngine.InputSystem.UI.InputSystemUIInputModule>();

        // Three buttons stacked down the right side of the screen.
        for (int i = 0; i < Buttons.Length; i++)
        {
            var (name, mood) = Buttons[i];
            var normal = AssetDatabase.LoadAssetAtPath<Sprite>($"{UI}/button_{name}.png");
            var pressed = AssetDatabase.LoadAssetAtPath<Sprite>($"{UI}/button_{name}_pressed.png");

            var go = new GameObject($"Button {name}", typeof(RectTransform));
            go.transform.SetParent(canvasGo.transform, false);
            var rect = (RectTransform)go.transform;
            rect.anchorMin = rect.anchorMax = new Vector2(1f, 0.5f);   // right edge, middle
            rect.pivot = new Vector2(1f, 0.5f);
            rect.sizeDelta = new Vector2(300f, 250f);
            rect.anchoredPosition = new Vector2(-40f, 270f - i * 270f);

            var image = go.AddComponent<UnityEngine.UI.Image>();
            image.sprite = normal;
            image.preserveAspect = true;

            var button = go.AddComponent<UnityEngine.UI.Button>();
            button.targetGraphic = image;
            button.transition = UnityEngine.UI.Selectable.Transition.SpriteSwap;
            button.spriteState = new UnityEngine.UI.SpriteState { pressedSprite = pressed };
            // Saved in the scene, so the button works with no setup in Play.
            UnityEditor.Events.UnityEventTools.AddIntPersistentListener(button.onClick, actions.Play, mood);
        }
    }

    static void SpriteImports(string folder, FilterMode filter)
    {
        foreach (var path in Directory.GetFiles(folder, "*.png"))
        {
            var imp = (TextureImporter)AssetImporter.GetAtPath(path.Replace(Path.DirectorySeparatorChar, '/'));
            imp.textureType = TextureImporterType.Sprite;
            imp.spriteImportMode = SpriteImportMode.Single;
            imp.filterMode = filter;
            imp.textureCompression = TextureImporterCompression.Uncompressed;
            imp.mipmapEnabled = false;
            imp.SaveAndReimport();
        }
    }
}
