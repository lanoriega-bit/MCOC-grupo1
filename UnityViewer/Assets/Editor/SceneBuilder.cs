using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Mcoc.UnityViewer;

namespace Mcoc.UnityViewer.EditorTools
{
    public static class SceneBuilder
    {
        const string ScenePath = "Assets/Main.unity";
        const string BuildDir = "Builds/Windows";

        [MenuItem("MCOC/Montar escena y compilar Windows")]
        public static void BuildAll()
        {
            CreateScene();
            BuildWindows();
        }

        [MenuItem("MCOC/Crear escena solo")]
        public static void CreateSceneOnly()
        {
            CreateScene();
        }

        [MenuItem("MCOC/Compilar Windows")]
        public static void BuildWindowsOnly()
        {
            BuildWindows();
        }

        public static void CreateScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // Camara
            var camGo = new GameObject("Main Camera");
            var cam = camGo.AddComponent<Camera>();
            camGo.tag = "MainCamera";
            cam.fieldOfView = 45f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.15f, 0.15f, 0.17f, 1f);
            Vector3 target = new Vector3(24.98f, 7.3f, 9.83f);
            camGo.transform.position = target + new Vector3(0f, 18f, -85f);
            camGo.transform.LookAt(target);

            // Luz direccional
            var lightGo = new GameObject("Main Light");
            var light = lightGo.AddComponent<Light>();
            light.type = LightType.Directional;
            lightGo.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

            // Contenedor del viewer
            var holder = new GameObject("Viewer");
            holder.AddComponent<ViewerController>();

            // Panel de info (texto on-screen)
            var canvasGo = new GameObject("InfoCanvas");
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasGo.AddComponent<UnityEngine.UI.CanvasScaler>();
            canvasGo.AddComponent<UnityEngine.UI.GraphicRaycaster>();

            var infoGo = new GameObject("InfoText");
            infoGo.transform.SetParent(canvasGo.transform, false);
            var text = infoGo.AddComponent<UnityEngine.UI.Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = 14;
            text.color = Color.white;
            var rt = infoGo.GetComponent<RectTransform>();
            rt.anchorMin = new Vector2(0f, 1f);
            rt.anchorMax = new Vector2(1f, 1f);
            rt.pivot = new Vector2(0.5f, 1f);
            rt.anchoredPosition = new Vector2(0f, -4f);
            rt.sizeDelta = new Vector2(0f, 160f);
            rt.offsetMin = new Vector2(8f, 0f);
            rt.offsetMax = new Vector2(-8f, 0f);

            var statusGo = new GameObject("StatusText");
            statusGo.transform.SetParent(canvasGo.transform, false);
            var status = statusGo.AddComponent<UnityEngine.UI.Text>();
            status.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            status.fontSize = 14;
            status.color = Color.yellow;
            var srt = statusGo.GetComponent<RectTransform>();
            srt.anchorMin = new Vector2(0f, 0f);
            srt.anchorMax = new Vector2(0f, 0f);
            srt.pivot = new Vector2(0f, 0f);
            srt.anchoredPosition = new Vector2(8f, 8f);
            srt.sizeDelta = new Vector2(400f, 24f);

            // Conectar referencias serializadas del ViewerController
            var vc = holder.GetComponent<ViewerController>();
            var so = new SerializedObject(vc);
            so.FindProperty("infoText").objectReferenceValue = text;
            so.FindProperty("statusText").objectReferenceValue = status;
            so.ApplyModifiedPropertiesWithoutUndo();

            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log("Escena guardada en " + ScenePath);

            var scenes = EditorBuildSettings.scenes;
            var updated = new System.Collections.Generic.List<EditorBuildSettingsScene>(scenes) { new EditorBuildSettingsScene(ScenePath, true) };
            EditorBuildSettings.scenes = updated.ToArray();
            Debug.Log("Escena anadida a Build Settings.");
        }

        public static void BuildWindows()
        {
            if (!File.Exists(ScenePath)) { Debug.LogError("No existe la escena. Corre primero 'Montar escena'."); return; }
            if (!Directory.Exists(BuildDir)) Directory.CreateDirectory(BuildDir);
            var opts = new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = Path.Combine(BuildDir, "MCOC-Viewer.exe"),
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            };
            var report = BuildPipeline.BuildPlayer(opts);
            if (report.summary.result == UnityEditor.Build.Reporting.BuildResult.Succeeded)
                Debug.Log("BUILD OK: " + report.summary.outputPath);
            else
                Debug.LogError("BUILD FALLIDO: " + report.summary.result);
        }
    }
}
