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
        static readonly string CapturePath = Path.Combine(Directory.GetCurrentDirectory(), "Temp", "p1l4-ui-smoke.capture.txt");
        const string ActiveKey = "Mcoc.UiSmokeRunner.Active";
        static double playStarted;
        static bool running;
        static bool demoExecuted;
        static readonly List<string> captured = new List<string>();

        static UiSmokeRunner()
        {
            if (File.Exists(RequestPath))
            {
                File.Delete(RequestPath);
                EditorApplication.delayCall += StartSmoke;
            }
            else if (SessionState.GetBool(ActiveKey, false))
            {
                EditorApplication.delayCall += ResumeSmoke;
            }
        }

        [MenuItem("MCOC/Probar interfaz en Play")]
        public static void StartSmoke()
        {
            if (running || EditorApplication.isPlayingOrWillChangePlaymode) return;
            running = true;
            demoExecuted = false;
            captured.Clear();
            if (File.Exists(ResultPath)) File.Delete(ResultPath);
            if (File.Exists(CapturePath)) File.Delete(CapturePath);
            SessionState.SetBool(ActiveKey, true);
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
                AppendCapture("[UI QA] PLAY_SMOKE_COMPLETE: arranque y ciclo Play/Edit finalizados.");
                File.Copy(CapturePath, ResultPath, true);
                SessionState.SetBool(ActiveKey, false);
                if (System.Array.IndexOf(System.Environment.GetCommandLineArgs(), "--quit-after-smoke") >= 0)
                    EditorApplication.delayCall += () => EditorApplication.Exit(0);
            }
        }

        static void ResumeSmoke()
        {
            running = true;
            Application.logMessageReceived -= CaptureLog;
            Application.logMessageReceived += CaptureLog;
            EditorApplication.playModeStateChanged -= OnPlayModeChanged;
            EditorApplication.playModeStateChanged += OnPlayModeChanged;
            if (!EditorApplication.isPlaying) return;
            playStarted = EditorApplication.timeSinceStartup;
            demoExecuted = false;
            EditorApplication.update -= WaitForRuntimeChecks;
            EditorApplication.update += WaitForRuntimeChecks;
        }

        static void CaptureLog(string condition, string stackTrace, LogType type)
        {
            if (condition.Contains("[UI QA]") || condition.Contains("[P1L4 QA]") || condition.Contains("[P1L4 DEMO QA]") || condition.Contains("[P1L5 QA]") || condition.Contains("[P1L5 DEMO QA]") || type == LogType.Error || type == LogType.Exception)
                AppendCapture(condition);
        }

        static void AppendCapture(string line)
        {
            captured.Add(line);
            File.AppendAllText(CapturePath, line + System.Environment.NewLine);
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
