using System.IO;
using System.Collections.Generic;
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
        static readonly string ResultPath = Path.Combine(Directory.GetCurrentDirectory(), "Temp", "p1l4-ui-smoke.result.txt");
        static double playStarted;
        static bool running;
        static bool demoExecuted;
        static readonly List<string> captured = new List<string>();

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
            demoExecuted = false;
            captured.Clear();
            if (File.Exists(ResultPath)) File.Delete(ResultPath);
            Application.logMessageReceived += CaptureLog;
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
                Application.logMessageReceived -= CaptureLog;
                running = false;
                Debug.Log("[UI QA] PLAY_SMOKE_COMPLETE: arranque y ciclo Play/Edit finalizados.");
                captured.Add("[UI QA] PLAY_SMOKE_COMPLETE: arranque y ciclo Play/Edit finalizados.");
                File.WriteAllLines(ResultPath, captured.ToArray());
            }
        }

        static void CaptureLog(string condition, string stackTrace, LogType type)
        {
            if (condition.Contains("[UI QA]") || condition.Contains("[P1L4 QA]") || condition.Contains("[P1L4 DEMO QA]") || condition.Contains("[P1L5 QA]") || condition.Contains("[P1L5 DEMO QA]") || type == LogType.Error || type == LogType.Exception)
                captured.Add(condition);
        }

        static void WaitForRuntimeChecks()
        {
            if (!EditorApplication.isPlaying) return;
            double elapsed = EditorApplication.timeSinceStartup - playStarted;
            if (!demoExecuted && elapsed >= 6.0)
            {
                demoExecuted = true;
                var viewer = Object.FindFirstObjectByType<ViewerController>();
                if (viewer == null) Debug.LogError("[P1L4 DEMO QA] FAIL: ViewerController no encontrado en Play.");
                else viewer.RunActiveDemoSequenceCheck();
            }
            if (elapsed < 14.0) return;
            EditorApplication.update -= WaitForRuntimeChecks;
            EditorApplication.isPlaying = false;
        }
    }
}
