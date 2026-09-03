using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Mcoc.UnityViewer
{
    /// <summary>
    /// Controlador principal del visor 3D (rol "Unity Viewer"). Construye la escena
    /// desde el JSON, permite mostrar/ocultar por tipo y piso, y al hacer clic sobre
    /// un elemento muestra sus datos (ID, nodos, seccion, material, longitud,
    /// area y carga tributaria cuando esten presentes en el contrato).
    /// </summary>
    public class ViewerController : MonoBehaviour
    {
        [Header("Carga")]
        [SerializeField] private string jsonFileName = "model_viewer.json";

        [Header("Camara")]
        [SerializeField] private float orbitSpeed = 0.5f;
        [SerializeField] private float zoomSpeed = 1.0f;
        [SerializeField] private float minZoom = 1f;
        [SerializeField] private float maxZoom = 200f;

        [Header("UI")]
        [SerializeField] private Transform tipoToggleContainer;
        [SerializeField] private Transform pisoToggleContainer;
        [SerializeField] private Text infoText;
        [SerializeField] private Text statusText;

        private ModelData model;
        private readonly Dictionary<string, List<GameObject>> byType = new Dictionary<string, List<GameObject>>();
        private readonly Dictionary<string, List<GameObject>> byFloor = new Dictionary<string, List<GameObject>>();
        private readonly Dictionary<string, bool> typeVisible = new Dictionary<string, bool>();
        private readonly Dictionary<string, bool> floorVisible = new Dictionary<string, bool>();

        private Camera cam;
        private Transform selected = null;

        private static readonly Dictionary<string, string> TypeLabels = new Dictionary<string, string>
        {
            { "beam", "Vigas" },
            { "column", "Pilares/columnas" },
            { "column_plan", "Pilares CAD" },
            { "wall", "Muros" },
            { "support", "Apoyos" },
            { "diaphragm", "Diafragmas" },
            { "slab", "Pisos/losas" },
            { "axis", "Ejes CAD" },
            { "slab_edge", "Borde losa" },
            { "node", "Nodos" },
            { "cad_reference", "Lineas CAD ref." }
        };

        void Start()
        {
            cam = Camera.main;
            if (cam == null) cam = Camera.main;
            model = JsonLoader.LoadModel(jsonFileName);
            if (model == null) { SetStatus("Error: no se pudo cargar el modelo."); return; }
            BuildScene();
            BuildToggles();
            SetStatus($"{model.solids?.Count ?? 0} solidos, {model.segments?.Count ?? 0} lineas CAD");
        }

        // ---------- Construccion de escena ----------
        void BuildScene()
        {
            if (model.solids != null)
                foreach (var solid in model.solids) CreateSolid(solid);
            if (model.segments != null)
                foreach (var seg in model.segments) CreateSegment(seg);
            if (model.diaphragms != null)
                foreach (var dia in model.diaphragms) CreateDiaphragm(dia);
            CreateNodes();
        }

        GameObject CreateSolid(SolidData solid)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = solid.solidTag;
            Register(go, solid.category, solid.floor);
            var data = go.AddComponent<ElementInfo>();
            data.kind = solid.kind;
            data.id = solid.solidTag;
            data.category = solid.category;
            data.floor = solid.floor;
            data.sourceLayer = solid.source_layer;
            data.sourceDxf = solid.source_dxf;
            data.lengthM = solid.length_m;
            data.widthM = solid.width_m;
            data.heightM = solid.height_m;
            data.materialName = solid.material ?? "hormigon";

            Vector3 start = V(solid.start);
            Vector3 end = V(solid.end);
            if (solid.kind == "linear_prism")
            {
                Vector3 center = (start + end) * 0.5f;
                float lenXY = Mathf.Max(Vector3.Distance(start, end), 0.05f);
                go.transform.position = center;
                go.transform.localScale = new Vector3(lenXY, (float)(solid.width_m <= 0 ? 0.32 : solid.width_m), (float)(solid.height_m <= 0 ? 0.6 : solid.height_m));
                float ang = Mathf.Atan2(end.y - start.y, end.x - start.x) * Mathf.Rad2Deg;
                go.transform.rotation = Quaternion.Euler(0, 0, ang);
                data.nodeI = start;
                data.nodeJ = end;
            }
            else if (solid.center != null)
            {
                go.transform.position = V(solid.center);
                go.transform.localScale = new Vector3((float)(solid.width_m <= 0 ? 0.4 : solid.width_m), (float)(solid.depth_m <= 0 ? solid.width_m : solid.depth_m), (float)(solid.height_m <= 0 ? 0.6 : solid.height_m));
                data.nodeI = V(solid.center);
                data.nodeJ = V(solid.center);
            }
            var rnd = go.GetComponent<Renderer>();
            if (rnd != null) rnd.material.color = ColorFor(solid.category);
            return go;
        }

        void CreateSegment(SegmentData seg)
        {
            if (seg.points == null || seg.points.Count < 2) return;
            var go = new GameObject("seg_" + seg.elementTag);
            Register(go, seg.category == "axis" ? "axis" : "cad_reference", seg.floor);
            var lr = go.AddComponent<LineRenderer>();
            lr.positionCount = seg.points.Count;
            for (int i = 0; i < seg.points.Count; i++) lr.SetPosition(i, V(seg.points[i]));
            lr.startWidth = 0.03f; lr.endWidth = 0.03f;
            lr.material = new Material(Shader.Find("Sprites/Default"));
            lr.startColor = lr.endColor = ColorFor(seg.category == "axis" ? "axis" : "cad_reference");
        }

        void CreateDiaphragm(DiaphragmData dia)
        {
            if (dia.points == null || dia.points.Count < 2) return;
            var go = new GameObject("dia_" + dia.floor);
            Register(go, "diaphragm", dia.floor);
            var lr = go.AddComponent<LineRenderer>();
            lr.positionCount = dia.points.Count;
            lr.loop = true;
            for (int i = 0; i < dia.points.Count; i++) lr.SetPosition(i, V(dia.points[i]));
            lr.startWidth = 0.06f; lr.endWidth = 0.06f;
            lr.material = new Material(Shader.Find("Sprites/Default"));
            lr.startColor = lr.endColor = ColorFor("diaphragm");
        }

        void CreateNodes()
        {
            if (model.solids == null) return;
            var seen = new HashSet<string>();
            foreach (var solid in model.solids)
            {
                if (solid.category != "beam" && solid.category != "wall" && solid.category != "column" && solid.category != "column_plan" && solid.category != "support") continue;
                var candidates = new List<Vector3>();
                if (solid.kind == "linear_prism") { candidates.Add(V(solid.start)); candidates.Add(V(solid.end)); }
                else if (solid.center != null) candidates.Add(V(solid.center));
                foreach (var p in candidates)
                {
                    string key = solid.floor + "|" + p.x.ToString("F3") + "," + p.y.ToString("F3") + "," + p.z.ToString("F3");
                    if (seen.Contains(key)) continue;
                    seen.Add(key);
                    var go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                    go.name = "nod_" + key;
                    go.transform.position = p;
                    go.transform.localScale = Vector3.one * 0.28f;
                    go.GetComponent<Renderer>().material.color = ColorFor("node");
                    Register(go, "node", solid.floor);
                }
            }
        }

        void Register(GameObject go, string type, string floor)
        {
            go.transform.SetParent(transform, false);
            if (!byType.ContainsKey(type)) byType.Add(type, new List<GameObject>());
            byType[type].Add(go);
            if (!byFloor.ContainsKey(floor)) byFloor.Add(floor, new List<GameObject>());
            byFloor[floor].Add(go);
            if (!typeVisible.ContainsKey(type)) typeVisible[type] = true;
            if (!floorVisible.ContainsKey(floor)) floorVisible[floor] = true;
            ApplyVisibility(go, type, floor);
        }

        void ApplyVisibility(GameObject go, string type, string floor)
        {
            bool vis = typeVisible.ContainsKey(type) ? typeVisible[type] : true;
            if (floorVisible.ContainsKey(floor)) vis = vis && floorVisible[floor];
            go.SetActive(vis);
        }

        // ---------- UI toggles ----------
        void BuildToggles()
        {
            if (tipoToggleContainer != null)
            {
                foreach (var kv in byType)
                {
                    if (!TypeLabels.ContainsKey(kv.Key)) continue;
                    var label = TypeLabels[kv.Key];
                    var go = CreateToggle(label, kv.Key, true, tipoToggleContainer);
                    if (go != null) go.name = "tt_" + kv.Key;
                }
            }
            if (pisoToggleContainer != null)
            {
                foreach (var kv in byFloor)
                {
                    var go = CreateToggle($"Piso {kv.Key}", kv.Key, false, pisoToggleContainer);
                    if (go != null) go.name = "ft_" + kv.Key;
                }
            }
        }

        GameObject CreateToggle(string labelText, string key, bool isType, Transform parent)
        {
            var go = new GameObject("toggle", typeof(Toggle), typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var lbl = new GameObject("label", typeof(Text), typeof(RectTransform));
            lbl.transform.SetParent(go.transform, false);
            var t = go.GetComponent<Toggle>();
            if (isType) t.onValueChanged.AddListener(v => ToggleType(key, v));
            else t.onValueChanged.AddListener(v => ToggleFloor(key, v));
            t.isOn = true;
            return go;
        }

        void ToggleType(string type, bool visible) { typeVisible[type] = visible; ReapplyAll(); }
        void ToggleFloor(string floor, bool visible) { floorVisible[floor] = visible; ReapplyAll(); }

        void ReapplyAll()
        {
            foreach (var kv in byType)
                foreach (var go in kv.Value)
                    ApplyVisibility(go, kv.Key, go.GetComponent<ElementInfo>()?.floor ?? "");
        }

        // ---------- Seleccion por clic ----------
        void Update()
        {
            if (Input.GetMouseButtonDown(0)) TrySelect(Input.mousePosition);
            PolarCam();
        }

        void TrySelect(Vector2 screenPos)
        {
            Ray ray = cam.ScreenPointToRay(screenPos);
            if (Physics.Raycast(ray, out RaycastHit hit, 500f))
            {
                var ei = hit.collider.GetComponentInParent<ElementInfo>();
                selected = hit.collider.transform;
                if (ei != null) ShowInfo(ei);
            }
        }

        void ShowInfo(ElementInfo ei)
        {
            if (infoText == null) return;
            string cat = TypeLabels.ContainsKey(ei.category) ? TypeLabels[ei.category] : ei.category;
            string section = "-";
            if (ei.widthM > 0 && ei.heightM > 0) section = ei.widthM.ToString("F3") + " x " + ei.heightM.ToString("F3") + " m";
            string tributaria = "pendiente (contrato gravedad)";
            if (ei.tribAreaM2 > 0) tributaria = ei.tribAreaM2.ToString("F3") + " m2 / " + ei.tribLoadKN.ToString("F3") + " kN";
            infoText.text = $"Tag: {ei.id}\n" +
                $"Tipo: {cat}\n" +
                $"Piso: {ei.floor}\n" +
                $"Seccion: {section}\n" +
                $"Material: {ei.materialName}\n" +
                $"Nodo i: {P(ei.nodeI)}\n" +
                $"Nodo j: {P(ei.nodeJ)}\n" +
                $"Longitud: {ei.lengthM.ToString("F3")} m\n" +
                $"Tributaria: {tributaria}";
        }

        void PolarCam()
        {
            if (cam == null) return;
            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) > 0.001f)
            {
                cam.fieldOfView = Mathf.Clamp(cam.fieldOfView - scroll * zoomSpeed * 8f, minZoom, maxZoom);
            }
        }

        // ---------- helpers ----------
        static Vector3 V(List<double> p)
        {
            if (p == null || p.Count < 3) return Vector3.zero;
            return new Vector3((float)p[0], (float)p[1], (float)p[2]);
        }

        static string P(Vector3 v) => "(" + v.x.ToString("F3") + ", " + v.y.ToString("F3") + ", " + v.z.ToString("F3") + ")";

        static Color ColorFor(string category)
        {
            switch (category)
            {
                case "beam": return new Color(0.45f, 0.75f, 1f);
                case "column": return new Color(0.95f, 0.65f, 0.4f);
                case "column_plan": return new Color(0.95f, 0.65f, 0.4f);
                case "wall": return new Color(0.65f, 0.85f, 0.6f);
                case "support": return new Color(1f, 1f, 0.9f);
                case "diaphragm": return new Color(0.9f, 0.9f, 1f);
                case "slab": return new Color(0.55f, 0.55f, 0.75f);
                case "slab_edge": return new Color(0.7f, 0.7f, 1f);
                case "axis": return new Color(0.8f, 0.8f, 0.8f);
                case "node": return new Color(1f, 0.82f, 0.3f);
                case "cad_reference": return new Color(0.6f, 0.7f, 0.8f);
                default: return new Color(0.7f, 0.7f, 0.7f);
            }
        }

        void SetStatus(string msg) { if (statusText != null) statusText.text = msg; }
    }

    // Datos del elemento seleccionable, incluye campos de tributaria (contrato de Luis)
    public class ElementInfo : MonoBehaviour
    {
        public string id;
        public string category;
        public string kind;
        public string floor;
        public string sourceLayer;
        public string sourceDxf;
        public string materialName;
        public double widthM;
        public double heightM;
        public double lengthM;
        public Vector3 nodeI;
        public Vector3 nodeJ;
        public double tribAreaM2;
        public double tribLoadKN;
    }
}
