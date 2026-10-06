using UnityEditor;
using UnityEngine;

namespace Mcoc.UnityViewer.EditorTools
{
    public static class ArchitecturalContextReviewMenu
    {
        [MenuItem("MCOC/Revisar arquitectura visual")]
        public static void Run()
        {
            var viewer = Object.FindFirstObjectByType<ViewerController>();
            if (!Application.isPlaying || viewer == null || viewer.gameObject.scene.path != "Assets/Main.unity")
            {
                Debug.LogWarning("Entre en Play en Assets/Main.unity para revisar el contexto visual desktop.");
                return;
            }
            viewer.RunArchitecturalContextReview();
        }
    }
}
