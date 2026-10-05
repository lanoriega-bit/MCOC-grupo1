using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
public static class SurfaceBoot
{
    public static void Run()
    {
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        new GameObject("SurfaceChecks").AddComponent<SurfaceChecks>();
        EditorApplication.EnterPlaymode();
    }
}
