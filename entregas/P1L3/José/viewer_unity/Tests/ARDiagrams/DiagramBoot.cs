using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
public static class DiagramBoot
{
    public static void Run()
    {
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        new GameObject("Checks").AddComponent<ARDiagramChecks>();
        EditorApplication.EnterPlaymode();
    }
}
