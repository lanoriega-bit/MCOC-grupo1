using System;
using System.IO;
using System.Linq;
using Mcoc.UnityViewer.P1L6AR;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Mcoc.UnityViewer.EditorTools
{
    public static class P1L6ARFinalSceneBuilder
    {
        public const string SourceScenePath = "Assets/Scenes/Luis_AR_Test.unity";
        public const string FinalScenePath = "Assets/Scenes/P1L6_AR_Final.unity";
        public const string MainScenePath = "Assets/Main.unity";
        public const string PrototypeScenePath = "Assets/P1L6_AR_Prototype.unity";

        // Provisional demo calibration only: the image centre represents the
        // base centre of E2-P1-C-002 in Unity coordinates. It is deliberately
        // not a claim about the marker's final physical building location.
        static readonly Vector3 DemoModelOriginUnity = new Vector3(7.502f, 3.96f, -0.001f);

        [MenuItem("MCOC/P1L6/Construir escena AR final")]
        public static void BuildFinalScene()
        {
            if (!File.Exists(SourceScenePath))
                throw new FileNotFoundException("Escena AR de Luis ausente", SourceScenePath);

            Scene scene = EditorSceneManager.OpenScene(SourceScenePath, OpenSceneMode.Single);
            LuisARImageAnchor luisTracker = UnityEngine.Object.FindAnyObjectByType<LuisARImageAnchor>();
            if (luisTracker == null)
                throw new InvalidOperationException("Luis_AR_Test no contiene LuisARImageAnchor.");

            SerializedObject trackerObject = new SerializedObject(luisTracker);
            trackerObject.FindProperty("cubePrefab").objectReferenceValue = null;
            trackerObject.ApplyModifiedPropertiesWithoutUndo();

            DestroyAll<FakeAnchorProvider>();
            DestroyAll<IdentityModelToARTransform>();
            DestroyAll<ARDesktopSimulator>();
            DestroyNamed("P1L6MobileIntegration");

            GameObject root = new GameObject("P1L6MobileIntegration");

            LuisAnchorProviderAdapter provider = root.AddComponent<LuisAnchorProviderAdapter>();
            SetObjectReference(provider, "source", luisTracker);

            TrackedModelToARTransformBehaviour transform = root.AddComponent<TrackedModelToARTransformBehaviour>();
            SetObjectReference(transform, "anchorProvider", provider);
            SetVector3(transform, "modelOriginUnityMetres", DemoModelOriginUnity);

            ARDatasetRepository repository = ChildWith<ARDatasetRepository>(root.transform, "ARCurrentDataset");
            StructuralARElementRenderer renderer = ChildWith<StructuralARElementRenderer>(root.transform, "ARStructuralElementRenderer");
            ARStructuralElementController controller = ChildWith<ARStructuralElementController>(root.transform, "ARStructuralElementController");
            SetObjectReference(controller, "repository", repository);
            SetObjectReference(controller, "elementRenderer", renderer);
            SetObjectReference(controller, "anchorProviderBehaviour", provider);
            SetObjectReference(controller, "transformBehaviour", transform);
            SetString(controller, "initialElementTag", "E2-P1-C-002");
            SetFloat(controller, "visualizationScale", 0.25f);

            ARResultPanel panel = ChildWith<ARResultPanel>(root.transform, "ARResultPanel");
            SetObjectReference(panel, "controller", controller);

            EditorSceneManager.SaveScene(scene, FinalScenePath);
            ConfigureBuildScenes();
            AssetDatabase.SaveAssets();
            Debug.Log("[P1L6 MOBILE] Escena final creada: " + FinalScenePath);
        }

        public static void BuildAndValidateForBatch()
        {
            BuildFinalScene();
            ValidateFinalScene();
        }

        [MenuItem("MCOC/P1L6/Validar escena AR final")]
        public static void ValidateFinalScene()
        {
            Scene scene = EditorSceneManager.OpenScene(FinalScenePath, OpenSceneMode.Single);
            RequireCount<UnityEngine.XR.ARFoundation.ARSession>(1);
            RequireCount<Unity.XR.CoreUtils.XROrigin>(1);
            RequireCount<UnityEngine.XR.ARFoundation.ARTrackedImageManager>(1);
            RequireCount<UnityEngine.XR.ARFoundation.ARAnchorManager>(1);
            RequireCount<LuisARImageAnchor>(1);
            RequireCount<LuisAnchorProviderAdapter>(1);
            RequireCount<ARDatasetRepository>(1);
            RequireCount<ARStructuralElementController>(1);
            RequireCount<StructuralARElementRenderer>(1);
            RequireCount<TrackedModelToARTransformBehaviour>(1);
            RequireCount<ARResultPanel>(1);
            RequireCount<FakeAnchorProvider>(0);
            RequireCount<IdentityModelToARTransform>(0);
            RequireCount<ARDesktopSimulator>(0);

            Camera[] cameras = UnityEngine.Object.FindObjectsByType<Camera>(FindObjectsSortMode.None);
            if (cameras.Length != 1)
                throw new InvalidOperationException("La escena final debe tener exactamente una cámara; encontradas: " + cameras.Length);

            if (!File.Exists("Assets/StreamingAssets/p1l6_current_ar_elements.json"))
                throw new FileNotFoundException("Dataset CURRENT ausente.");
            if (!File.Exists(MainScenePath) || !File.Exists(PrototypeScenePath))
                throw new FileNotFoundException("Main o prototipo AR ausente.");

            ValidateSpatialTransform();
            ValidateCurrentCandidates();

            LuisARImageAnchor tracker = UnityEngine.Object.FindAnyObjectByType<LuisARImageAnchor>();
            SerializedObject trackerObject = new SerializedObject(tracker);
            if (trackerObject.FindProperty("cubePrefab").objectReferenceValue != null)
                throw new InvalidOperationException("La escena final no debe instanciar el cubo de prueba.");

            UnityEngine.XR.ARFoundation.ARTrackedImageManager imageManager =
                UnityEngine.Object.FindAnyObjectByType<UnityEngine.XR.ARFoundation.ARTrackedImageManager>();
            if (imageManager.referenceLibrary == null || imageManager.referenceLibrary.count != 1)
                throw new InvalidOperationException("La escena final debe usar una biblioteca con ImagenPrueba.");

            EditorBuildSettingsScene[] enabled = EditorBuildSettings.scenes.Where(x => x.enabled).ToArray();
            if (enabled.Length != 1 || enabled[0].path != FinalScenePath)
                throw new InvalidOperationException("El build móvil debe tener una sola escena activa: " + FinalScenePath);

            ValidateDesktopScene(MainScenePath, "Main");
            ValidateDesktopScene(PrototypeScenePath, "P1L6_AR_Prototype");
            EditorSceneManager.OpenScene(FinalScenePath, OpenSceneMode.Single);

            Debug.Log("[P1L6 MOBILE QA] PASS scene=" + FinalScenePath +
                " cameras=1 arSessions=1 initialElement=E2-P1-C-002 dataset=CURRENT");
        }

        static void ValidateSpatialTransform()
        {
            TrackedModelToARTransformBehaviour transform =
                UnityEngine.Object.FindAnyObjectByType<TrackedModelToARTransformBehaviour>();
            Vector3 columnCentre = new Vector3(7.502f, 5.94f, -0.001f);
            Vector3 local = transform.ToAnchorLocalPoint(columnCentre, columnCentre, 0.25f);
            if (Vector3.Distance(local, new Vector3(0f, 0.495f, 0f)) > 1e-4f)
                throw new InvalidOperationException("Posición AR de columna incorrecta: " + local);

            Vector3 columnDirection = transform.ToAnchorLocalRotation(Vector3.up) * Vector3.up;
            Vector3 beamDirection = transform.ToAnchorLocalRotation(Vector3.right) * Vector3.up;
            if (Vector3.Angle(columnDirection, Vector3.up) > 0.01f)
                throw new InvalidOperationException("La columna no queda vertical.");
            if (Vector3.Angle(beamDirection, Vector3.right) > 0.01f)
                throw new InvalidOperationException("La viga no queda horizontal en +X.");
        }

        static void ValidateCurrentCandidates()
        {
            string json = File.ReadAllText("Assets/StreamingAssets/p1l6_current_ar_elements.json");
            ARDatasetRoot dataset = JsonUtility.FromJson<ARDatasetRoot>(json);
            StructuralElementARData column = dataset.elements.Single(x => x.elementTag == "E2-P1-C-002");
            StructuralElementARData beam = dataset.elements.Single(x => x.elementTag == "E2-P1-V-032");
            if (column.element_id != column.elementTag || column.solidTag != "SOL2_1_column_0001" ||
                column.opensees_tags.Length != 1 || column.opensees_tags[0] != 10039 ||
                column.current_result_R?.segments?.Length < 1 || column.capacity == null)
                throw new InvalidOperationException("Contrato CURRENT incorrecto para E2-P1-C-002.");
            if (beam.element_id != beam.elementTag || beam.solidTag != "SOL2_1_beam_0121" ||
                beam.opensees_tags.Length != 1 || beam.opensees_tags[0] != 10231 ||
                beam.current_result_R?.segments?.Length < 1 || beam.capacity == null)
                throw new InvalidOperationException("Contrato CURRENT incorrecto para E2-P1-V-032.");
        }

        static void ValidateDesktopScene(string path, string label)
        {
            Scene scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Single);
            if (!scene.IsValid() || scene.rootCount == 0)
                throw new InvalidOperationException(label + " no abre correctamente.");
            if (label == "P1L6_AR_Prototype")
            {
                RequireCount<FakeAnchorProvider>(1);
                RequireCount<IdentityModelToARTransform>(1);
                RequireCount<ARDatasetRepository>(1);
                RequireCount<StructuralARElementRenderer>(1);
            }
            Debug.Log("[P1L6 MOBILE QA] PASS desktop scene=" + path);
        }

        static T ChildWith<T>(Transform parent, string name) where T : Component
        {
            GameObject child = new GameObject(name);
            child.transform.SetParent(parent, false);
            return child.AddComponent<T>();
        }

        static void ConfigureBuildScenes()
        {
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(FinalScenePath, true),
                new EditorBuildSettingsScene(MainScenePath, false),
                new EditorBuildSettingsScene(PrototypeScenePath, false),
                new EditorBuildSettingsScene(SourceScenePath, false)
            };
        }

        static void DestroyAll<T>() where T : Component
        {
            foreach (T component in UnityEngine.Object.FindObjectsByType<T>(FindObjectsSortMode.None))
                UnityEngine.Object.DestroyImmediate(component.gameObject);
        }

        static void DestroyNamed(string name)
        {
            GameObject existing = GameObject.Find(name);
            if (existing != null) UnityEngine.Object.DestroyImmediate(existing);
        }

        static void RequireCount<T>(int expected) where T : UnityEngine.Object
        {
            int actual = UnityEngine.Object.FindObjectsByType<T>(FindObjectsSortMode.None).Length;
            if (actual != expected)
                throw new InvalidOperationException(typeof(T).Name + " count " + actual + " != " + expected);
        }

        static void SetObjectReference(UnityEngine.Object target, string property, UnityEngine.Object value)
        {
            SerializedObject serialized = new SerializedObject(target);
            serialized.FindProperty(property).objectReferenceValue = value;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        static void SetVector3(UnityEngine.Object target, string property, Vector3 value)
        {
            SerializedObject serialized = new SerializedObject(target);
            serialized.FindProperty(property).vector3Value = value;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        static void SetString(UnityEngine.Object target, string property, string value)
        {
            SerializedObject serialized = new SerializedObject(target);
            serialized.FindProperty(property).stringValue = value;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        static void SetFloat(UnityEngine.Object target, string property, float value)
        {
            SerializedObject serialized = new SerializedObject(target);
            serialized.FindProperty(property).floatValue = value;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }
    }
}
