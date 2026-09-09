using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Mcoc.UnityViewer.EditorTools
{
    [InitializeOnLoad]
    public static class AutoOpenScene
    {
        static AutoOpenScene()
        {
            EditorApplication.delayCall += () =>
            {
                var active = EditorSceneManager.GetActiveScene().path;
                if (string.IsNullOrEmpty(active) || !active.EndsWith("Main.unity"))
                {
                    var scene = EditorSceneManager.OpenScene("Assets/Main.unity");
                    Debug.Log("[AutoOpenScene] Escena abierta: " + scene.path);
                }
            };
        }
    }
}