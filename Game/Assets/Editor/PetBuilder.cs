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

    // Uses the Universal 2D template's own SampleScene (Main Camera and
    // Global Light 2D already in it, same as Shadow) and only adds the pup.
    static void MakeScene(AnimatorController controller)
    {
        var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
        var old = GameObject.Find("Pup");
        if (old != null) Object.DestroyImmediate(old);

        var pet = new GameObject("Pup");
        // The template camera shows 10 units of height; at 3x the pup fills
        // about half the screen instead of a sixth.
        pet.transform.localScale = Vector3.one * 3f;
        pet.transform.position = new Vector3(0f, -2.5f, 0f);
        var sr = pet.AddComponent<SpriteRenderer>();
        sr.sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{Frames}/idle_01.png");
        // URP 2D's own sprite material, so the Global Light 2D lights the pup.
        var lit = AssetDatabase.LoadAssetAtPath<Material>(
            "Packages/com.unity.render-pipelines.universal/Runtime/Materials/Sprite-Lit-Default.mat");
        if (lit != null) sr.sharedMaterial = lit;
        pet.AddComponent<Animator>().runtimeAnimatorController = controller;

        EditorSceneManager.SaveScene(scene, ScenePath);
        EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
    }
}
