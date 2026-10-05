using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
public static class OverlayBoot
{
    public static void Run()
    {
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        new GameObject("OverlayChecks").AddComponent<OverlayChecks>();
        EditorApplication.EnterPlaymode();
    }
}

