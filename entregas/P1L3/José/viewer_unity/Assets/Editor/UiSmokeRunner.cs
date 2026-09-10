using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Mcoc.UnityViewer.EditorTools
{
    /// <summary>
    /// Prueba reproducible del arranque real en Play. Se activa creando
    /// Temp/p1l3-ui-smoke.request y nunca modifica la escena ni los resultados.
    /// </summary>
    [InitializeOnLoad]
    public static class UiSmokeRunner
    {
        static readonly string RequestPath = Path.Combine(Directory.GetCurrentDirectory(), "Temp", "p1l3-ui-smoke.request");
        static double playStarted;
        static bool running;

        static UiSmokeRunner()
        {
            if (!File.Exists(RequestPath)) return;
            File.Delete(RequestPath);
            EditorApplication.delayCall += StartSmoke;
        }

        [MenuItem("MCOC/Probar interfaz en Play")]
        public static void StartSmoke()
        {
            if (running || EditorApplication.isPlayingOrWillChangePlaymode) return;
            running = true;
            EditorSceneManager.OpenScene("Assets/Main.unity", OpenSceneMode.Single);
            EditorApplication.playModeStateChanged += OnPlayModeChanged;
            Debug.Log("[UI QA] Iniciando prueba automatica en Play.");
            EditorApplication.isPlaying = true;
        }

        static void OnPlayModeChanged(PlayModeStateChange state)
        {
            if (state == PlayModeStateChange.EnteredPlayMode)
            {
                playStarted = EditorApplication.timeSinceStartup;
                EditorApplication.update += WaitForRuntimeChecks;
            }
            else if (state == PlayModeStateChange.EnteredEditMode && running)
            {
                EditorApplication.playModeStateChanged -= OnPlayModeChanged;
                running = false;
                Debug.Log("[UI QA] PLAY_SMOKE_COMPLETE: arranque y ciclo Play/Edit finalizados.");
            }
        }

        static void WaitForRuntimeChecks()
        {
            if (!EditorApplication.isPlaying || EditorApplication.timeSinceStartup - playStarted < 12.0) return;
            EditorApplication.update -= WaitForRuntimeChecks;
            EditorApplication.isPlaying = false;
        }
    }
}
