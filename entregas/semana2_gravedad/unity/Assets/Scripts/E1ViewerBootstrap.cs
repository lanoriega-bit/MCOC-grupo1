using UnityEngine;

namespace Mcoc.Semana2.UnityE1
{
    public static class E1ViewerBootstrap
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void CreateViewer()
        {
            if (Object.FindObjectOfType<E1ViewerController>() != null) return;
            GameObject go = new GameObject("E1 Gravity Viewer Controller");
            go.AddComponent<E1ViewerController>();
        }
    }
}
