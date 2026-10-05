using Mcoc.UnityViewer.P1L6AR;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Mcoc.UnityViewer.EditorTools
{
    public static class P1L6ARSceneBuilder
    {
        public const string ScenePath = "Assets/P1L6_AR_Prototype.unity";

        [MenuItem("MCOC/P1L6/Construir prototipo AR")]
        public static void BuildScene()
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject root = new GameObject("ARVisualizationRoot");
            root.AddComponent<IdentityModelToARTransform>();

            GameObject repository = new GameObject("ARCurrentDataset");
            repository.transform.SetParent(root.transform);
            repository.AddComponent<ARDatasetRepository>();

            GameObject fakeAnchor = new GameObject("FakeAnchor");
            fakeAnchor.transform.SetParent(root.transform);
            fakeAnchor.AddComponent<FakeAnchorProvider>();

            GameObject renderer = new GameObject("ARStructuralElementRenderer");
            renderer.transform.SetParent(root.transform);
            renderer.AddComponent<StructuralARElementRenderer>();

            GameObject controller = new GameObject("ARStructuralElementController");
            controller.transform.SetParent(root.transform);
            controller.AddComponent<ARStructuralElementController>();

            GameObject resultPanel = new GameObject("ARResultPanel");
            resultPanel.transform.SetParent(root.transform);
            resultPanel.AddComponent<ARResultPanel>();

            GameObject simulator = new GameObject("DesktopARSimulation");
            simulator.transform.SetParent(root.transform);
            simulator.AddComponent<ARDesktopSimulator>();
            simulator.AddComponent<ARPrototypeSelfCheck>();

            GameObject cameraObject = new GameObject("Camera", typeof(Camera), typeof(AudioListener));
            cameraObject.tag = "MainCamera";
            cameraObject.transform.position = new Vector3(0, 1.4f, -5.5f);
            cameraObject.transform.rotation = Quaternion.Euler(8, 0, 0);
            cameraObject.GetComponent<Camera>().backgroundColor = new Color(0.035f, 0.055f, 0.085f);

            GameObject lightObject = new GameObject("Lighting", typeof(Light));
            lightObject.transform.rotation = Quaternion.Euler(48, -32, 0);
            Light light = lightObject.GetComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.25f;

            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "ReferenceGround";
            ground.transform.position = new Vector3(0, -0.02f, 0);
            ground.transform.localScale = Vector3.one * 0.8f;
            ground.GetComponent<Renderer>().sharedMaterial = new Material(Shader.Find("Standard"))
            {
                color = new Color(0.12f, 0.14f, 0.17f)
            };

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            Debug.Log("[P1L6 AR] Escena creada: " + ScenePath);
        }

        public static void BuildAndPlayForQa()
        {
            if (Application.isPlaying || EditorApplication.isPlayingOrWillChangePlaymode) return;
            if (!File.Exists(ScenePath)) BuildScene();
            else EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            EditorApplication.isPlaying = true;
        }
    }
}
