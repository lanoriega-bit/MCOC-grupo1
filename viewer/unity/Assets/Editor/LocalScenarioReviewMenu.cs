using UnityEditor;
using UnityEngine;

namespace Mcoc.UnityViewer.EditorTools
{
    public static class LocalScenarioReviewMenu
    {
        [MenuItem("MCOC/Validar carga local en Main Play")]
        public static void Run()
        {
            var viewer=Object.FindFirstObjectByType<ViewerController>();
            if(!Application.isPlaying||viewer==null||viewer.gameObject.scene.path!="Assets/Main.unity")
            {Debug.LogWarning("Entra en Play en Assets/Main.unity. No abre escenas ni módulos AR.");return;}
            viewer.RunLocalScenarioReview();
        }
    }
}
