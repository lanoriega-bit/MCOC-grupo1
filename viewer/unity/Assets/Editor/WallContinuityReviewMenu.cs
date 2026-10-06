using UnityEditor;
using UnityEngine;
namespace Mcoc.UnityViewer.EditorTools
{
    public static class WallContinuityReviewMenu
    {
        [MenuItem("MCOC/Validar núcleos CURRENT y capturar vistas")]
        public static void Run()
        {
            var viewer = Object.FindFirstObjectByType<ViewerController>();
            if (!Application.isPlaying || viewer == null) { Debug.LogWarning("Abra Assets/Main.unity y entre en Play antes de esta prueba."); return; }
            viewer.RunWallContinuityReview();
        }
    }
}
