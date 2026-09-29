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
                if (Application.isPlaying || EditorApplication.isPlayingOrWillChangePlaymode) return;
                var active = EditorSceneManager.GetActiveScene().path;
                // Main remains the default only when no saved scene is active.
                // Do not replace explicit development scenes such as P1L6_AR_Prototype.
                if (string.IsNullOrEmpty(active))
                {
                    var scene = EditorSceneManager.OpenScene("Assets/Main.unity");
                    Debug.Log("[AutoOpenScene] Escena abierta: " + scene.path);
                }
            };
        }
    }
}
