using UnityEditor;
using UnityEngine;
namespace Mcoc.UnityViewer.EditorTools
{
    public static class VisualUxReviewMenu
    {
        [MenuItem("MCOC/Validar UX visual CURRENT")]
        public static void Run()
        {
            var viewer=Object.FindFirstObjectByType<ViewerController>();
            if(!Application.isPlaying||viewer==null){Debug.LogWarning("Abra Main.unity y entre en Play primero.");return;}
            viewer.RunVisualUxReview();
        }
    }
}
