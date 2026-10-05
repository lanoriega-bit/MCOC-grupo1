using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
public static class FreePlacementBoot
{
    public static void Run()
    {
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        new GameObject("FreePlacementChecks").AddComponent<FreePlacementChecks>();
        EditorApplication.EnterPlaymode();
    }
}


