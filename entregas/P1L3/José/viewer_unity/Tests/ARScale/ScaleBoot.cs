using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
public static class ScaleBoot
{
    public static void Run()
    {
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        new GameObject("ScaleChecks").AddComponent<ScaleChecks>();
        EditorApplication.EnterPlaymode();
    }
}
