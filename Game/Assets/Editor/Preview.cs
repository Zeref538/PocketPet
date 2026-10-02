using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

// Editor-only: renders the test scene to Logs/preview.png without opening the Editor window.
public static class Preview
{
    public static void Run()
    {
        EditorSceneManager.OpenScene(EditorBuildSettings.scenes[0].path);
        var cam = Camera.main;
        var rt = new RenderTexture(640, 480, 24);
        cam.targetTexture = rt; cam.Render(); cam.Render();
        RenderTexture.active = rt;
        var tex = new Texture2D(640, 480, TextureFormat.RGB24, false);
        tex.ReadPixels(new Rect(0, 0, 640, 480), 0, 0);
        File.WriteAllBytes("Logs/preview.png", tex.EncodeToPNG());
    }
}
