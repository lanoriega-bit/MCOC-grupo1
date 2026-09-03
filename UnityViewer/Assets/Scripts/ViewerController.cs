using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Mcoc.UnityViewer
{
    /// <summary>
    /// Controlador principal del visor 3D (rol "Unity Viewer"). Construye la escena
    /// desde el JSON, permite mostrar/ocultar por tipo y piso (con boton "solo"),
    /// vistas laterales A/B/C/D y planta, IDs on/off, y al hacer clic sobre un
    /// elemento muestra sus datos (ID, nodos, seccion, material, longitud,
    /// area y carga tributaria cuando esten presentes en el contrato).
    /// </summary>
    public class ViewerController : MonoBehaviour
    {
        [Header("Carga")]
        [SerializeField] private string jsonFileName = "model_viewer.json";

        [Header("Camara")]
        [SerializeField] private float orbitSpeed = 4f;
        [SerializeField] private float zoomSpeed = 1.0f;
        [SerializeField] private float minZoom = 1f;
        [SerializeField] private float maxZoom = 600f;
        [SerializeField] private float panSpeed = 0.1f;

        private Vector3 orbitTarget;
        private float orbitDist = 160f;
        private float yaw = 30f;      // giro horizontal (grados, continua)
        private float pitch = 25f;    // elevacion (grados, -89..89)

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
        private readonly List<ElementInfo> allElements = new List<ElementInfo>();

        private Camera cam;
        private Transform selected = null;
        private string lastInfo = "";
        private bool labelsVisible = false;
        private static Texture2D whiteTex;

        private static readonly Dictionary<string, string> TypeLabels = new Dictionary<string, string>
        {
            { "beam", "Vigas" },
            { "column", "Pilares/columnas" },
            { "column_plan", "Pilares CAD" },
            { "wall", "Muros" },
            { "support", "Apoyos" },
            { "diaphragm", "Diafragmas" },
            { "slab", "Piso/techo" },
            { "axis", "Ejes CAD" },
            { "slab_edge", "Borde losa" },
            { "node", "Nodos" },
            { "cad_reference", "Lineas CAD ref." }
        };

        private static readonly Dictionary<string, int> FloorOrder = new Dictionary<string, int>
        {
            { "base", 0 }, { "1S", 1 }, { "1", 2 }, { "2", 3 }, { "3", 4 }, { "4", 5 }
        };

        void Start()
        {
            cam = Camera.main;
            if (cam == null) cam = Camera.main;
            orbitTarget = new Vector3(37.29f, 18.66f, 10.96f);
            if (cam != null) { cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(0.07f, 0.11f, 0.19f, 1f); }
            model = JsonLoader.LoadModel(jsonFileName);
            if (model == null) { SetStatus("Error: no se pudo cargar el modelo."); return; }
            BuildScene();
            SetStatus($"{model.solids?.Count ?? 0} solidos, {model.segments?.Count ?? 0} lineas CAD, {model.labels?.Count ?? 0} etiquetas");
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
            var data = go.AddComponent<ElementInfo>();
            data.go = go;
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
            Register(go, solid.category, solid.floor);
            allElements.Add(data);
            return go;
        }

        void CreateSegment(SegmentData seg)
        {
            if (seg.points == null || seg.points.Count < 2) return;
            var go = new GameObject("seg_" + seg.elementTag);
            var lr = go.AddComponent<LineRenderer>();
            lr.positionCount = seg.points.Count;
            for (int i = 0; i < seg.points.Count; i++) lr.SetPosition(i, V(seg.points[i]));
            lr.startWidth = 0.03f; lr.endWidth = 0.03f;
            lr.material = LineMaterial(ColorFor(seg.category == "axis" ? "axis" : "cad_reference"));
            Register(go, seg.category == "axis" ? "axis" : "cad_reference", seg.floor);
        }

        void CreateDiaphragm(DiaphragmData dia)
        {
            if (dia.points == null || dia.points.Count < 2) return;
            var go = new GameObject("dia_" + dia.floor);
            var lr = go.AddComponent<LineRenderer>();
            lr.positionCount = dia.points.Count;
            lr.loop = true;
            for (int i = 0; i < dia.points.Count; i++) lr.SetPosition(i, V(dia.points[i]));
            lr.startWidth = 0.06f; lr.endWidth = 0.06f;
            lr.material = LineMaterial(ColorFor("diaphragm"));
            Register(go, "diaphragm", dia.floor);
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
                    var ei = go.AddComponent<ElementInfo>();
                    ei.id = "NOD_" + key.Replace("|", "_").Replace(",", "_");
                    ei.category = "node";
                    ei.floor = solid.floor;
                    ei.materialName = "generado";
                    ei.go = go;
                    Register(go, "node", solid.floor);
                    allElements.Add(ei);
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
            if (!typeVisible.ContainsKey(type)) typeVisible[type] = type != "cad_reference";
            if (!floorVisible.ContainsKey(floor)) floorVisible[floor] = true;
            ApplyVisibility(go, type, floor);
        }

        void ApplyVisibility(GameObject go, string type, string floor)
        {
            bool vis = typeVisible.ContainsKey(type) ? typeVisible[type] : true;
            if (floorVisible.ContainsKey(floor)) vis = vis && floorVisible[floor];
            go.SetActive(vis);
        }

        void ReapplyAll()
        {
            foreach (var kv in byType)
                foreach (var go in kv.Value)
                    ApplyVisibility(go, kv.Key, go.GetComponent<ElementInfo>()?.floor ?? "");
        }

        // ---------- Seleccion por clic ----------
        void Update()
        {
            if (Input.GetMouseButtonDown(0) && !IsMouseOverUI()) TrySelect(Input.mousePosition);
            PolarCam();
        }

        bool IsMouseOverUI()
        {
            Vector2 m = Input.mousePosition;
            m.y = Screen.height - m.y;
            // Zona panel derecho (navegacion, arriba)
            if (m.x > Screen.width - 260 && m.y < 92) return true;
            // Zona panel izquierdo (pisos y tipos)
            if (m.x < 260 && m.y > 225 && m.y < 705) return true;
            // Zona panel de info (arriba izquierda)
            if (m.x < 370 && m.y < 210) return true;
            return false;
        }

        void TrySelect(Vector2 screenPos)
        {
            if (cam == null) return;
            Ray ray = cam.ScreenPointToRay(screenPos);
            RaycastHit[] hits = Physics.RaycastAll(ray, 1000f);
            if (hits.Length == 0) return;
            System.Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
            foreach (var hit in hits)
            {
                var ei = hit.collider.GetComponentInParent<ElementInfo>();
                if (ei != null)
                {
                    selected = hit.collider.transform;
                    ShowInfo(ei);
                    return;
                }
            }
        }

        void ShowInfo(ElementInfo ei)
        {
            string cat = TypeLabels.ContainsKey(ei.category) ? TypeLabels[ei.category] : ei.category;
            string section = "-";
            if (ei.widthM > 0 && ei.heightM > 0) section = ei.widthM.ToString("F3") + " x " + ei.heightM.ToString("F3") + " m";
            string tributaria = "pendiente (contrato gravedad)";
            if (ei.tribAreaM2 > 0) tributaria = ei.tribAreaM2.ToString("F3") + " m2 / " + ei.tribLoadKN.ToString("F3") + " kN";
            lastInfo = $"Tag: {ei.id}\n" +
                $"Tipo: {cat}\n" +
                $"Piso: {ei.floor}\n" +
                $"Seccion: {section}\n" +
                $"Material: {ei.materialName}\n" +
                $"Nodo i: {P(ei.nodeI)}\n" +
                $"Nodo j: {P(ei.nodeJ)}\n" +
                $"Longitud: {ei.lengthM.ToString("F3")} m\n" +
                $"Tributaria: {tributaria}";
            if (infoText != null) infoText.text = lastInfo;
        }

        // ---------- Vistas ----------
        void TopView()
        {
            yaw = 30f;
            pitch = 89f;
            orbitDist = 150f;
        }

        void SideView(string side)
        {
            // D = sur: caja desde +Z; A este: desde +X; B norte: desde -Z; C oeste: desde -X
            var angles = new Dictionary<string, float> { { "D", 0f }, { "A", 90f }, { "B", 180f }, { "C", 270f } };
            yaw = angles.ContainsKey(side) ? angles[side] : 0f;
            pitch = 6f;
            orbitDist = 185f;
        }

        // ---------- UI (IMGUI garantiza visibilidad en build) ----------
        void OnGUI()
        {
            if (whiteTex == null) whiteTex = MakeTex(2, 2, Color.white);
            DrawPanelInfo();
            DrawControls();
            if (labelsVisible) DrawLabels();
        }

        void DrawPanelInfo()
        {
            if (string.IsNullOrEmpty(lastInfo)) return;
            var style = new GUIStyle(GUI.skin.box);
            style.fontSize = 13;
            style.alignment = TextAnchor.UpperLeft;
            style.normal.textColor = Color.white;
            style.normal.background = whiteTex;
            var tex = MakeTex(2, 2, new Color(0f, 0f, 0f, 0.78f));
            GUI.Box(new Rect(10, 10, 360, 200), "");
            GUI.DrawTexture(new Rect(10, 10, 360, 200), tex);
            var lbl = new GUIStyle(GUI.skin.label);
            lbl.fontSize = 13;
            lbl.normal.textColor = Color.white;
            GUI.Label(new Rect(20, 16, 340, 190), lastInfo, lbl);
        }

        void DrawControls()
        {
            float x = Screen.width - 260;
            float y = 10;

            // --- Botones de vista ---
            var btn = new GUIStyle(GUI.skin.button);
            btn.fontSize = 12;
            GUI.Box(new Rect(x, y, 250, 82), "");
            GUI.DrawTexture(new Rect(x, y, 250, 82), MakeTex(2, 2, new Color(0.02f, 0.04f, 0.08f, 0.85f)));
            var ttl = new GUIStyle(GUI.skin.label);
            ttl.fontSize = 12; ttl.fontStyle = FontStyle.Bold; ttl.normal.textColor = Color.white;
            GUI.Label(new Rect(x + 8, y + 4, 240, 18), "Navegacion", ttl);
            var t1 = new GUIStyle(btn); var t2 = new GUIStyle(btn); var t3 = new GUIStyle(btn); var t4 = new GUIStyle(btn); var t5 = new GUIStyle(btn);
            if (GUI.Button(new Rect(x + 8, y + 24, 44, 24), "Lado A", t1)) SideView("A");
            if (GUI.Button(new Rect(x + 56, y + 24, 44, 24), "Lado B", t2)) SideView("B");
            if (GUI.Button(new Rect(x + 104, y + 24, 44, 24), "Lado C", t3)) SideView("C");
            if (GUI.Button(new Rect(x + 152, y + 24, 44, 24), "Lado D", t4)) SideView("D");
            if (GUI.Button(new Rect(x + 8, y + 52, 120, 24), "Vista planta", t5)) TopView();
            if (GUI.Button(new Rect(x + 132, y + 52, 108, 24), labelsVisible ? "IDs: on" : "IDs: off", t1)) labelsVisible = !labelsVisible;

            // --- Panel izquierdo: Pisos y Tipos ---
            float lx = 10;
            float ly = 225;
            GUI.Box(new Rect(lx, ly, 250, 480), "");
            GUI.DrawTexture(new Rect(lx, ly, 250, 480), MakeTex(2, 2, new Color(0.02f, 0.04f, 0.08f, 0.85f)));
            var sect = new GUIStyle(GUI.skin.label);
            sect.fontSize = 12; sect.fontStyle = FontStyle.Bold; sect.normal.textColor = Color.white;

            GUI.Label(new Rect(lx + 8, ly + 4, 240, 18), "Pisos", sect);
            var floors = SortedFloors();
            float iy = ly + 24;
            foreach (var f in floors)
            {
                bool vis = floorVisible.ContainsKey(f) && floorVisible[f];
                bool novo = GUI.Toggle(new Rect(lx + 8, iy, 150, 20), vis, "Piso " + f);
                if (novo != vis) { floorVisible[f] = novo; ReapplyAll(); }
                if (GUI.Button(new Rect(lx + 160, iy, 70, 20), "solo"))
                {
                    foreach (var k in floorVisible.Keys) floorVisible[k] = (k == f);
                    ReapplyAll();
                }
                iy += 22;
            }

            iy += 10;
            GUI.Label(new Rect(lx + 8, iy, 240, 18), "Tipos", sect);
            iy += 22;
            float ty = iy;
            foreach (var kv in byType)
            {
                if (!TypeLabels.ContainsKey(kv.Key)) continue;
                bool vis = typeVisible.ContainsKey(kv.Key) && typeVisible[kv.Key];
                bool novo = GUI.Toggle(new Rect(lx + 8, ty, 220, 20), vis, TypeLabels[kv.Key]);
                if (novo != vis) { typeVisible[kv.Key] = novo; ReapplyAll(); }
                ty += 22;
            }
        }

        List<string> SortedFloors()
        {
            var list = new List<string>(byFloor.Keys);
            list.Sort((a, b) => (FloorOrder.ContainsKey(a) ? FloorOrder[a] : 99).CompareTo(FloorOrder.ContainsKey(b) ? FloorOrder[b] : 99));
            return list;
        }

        void DrawLabels()
        {
            if (cam == null) return;
            GUIStyle ls = new GUIStyle(GUI.skin.label);
            ls.fontSize = 10;
            ls.normal.textColor = new Color(1f, 0.82f, 0.3f);
            var sw = Screen.width; var sh = Screen.height;
            foreach (var ei in allElements)
            {
                if (ei.go == null || !ei.go.activeInHierarchy) continue;
                Vector3 cp = ei.nodeI + (ei.nodeJ - ei.nodeI) * 0.5f;
                Vector3 sp = cam.WorldToScreenPoint(cp);
                if (sp.z <= 0) continue;
                sp.y = sh - sp.y;
                if (sp.x < 0 || sp.x > sw || sp.y < 0 || sp.y > sh) continue;
                GUI.Label(new Rect(sp.x - 30, sp.y - 8, 80, 16), ShortTag(ei.id), ls);
            }
        }

        static string ShortTag(string tag) => tag.Replace("SOL_", "").Replace("CAD_", "").Replace("seg_", "");

        // ---------- Camara orbital (esferica: estable, gira en todos los sentidos) ----------
        private Vector2 lastMouse = new Vector2(-1f, -1f);
        private float velYaw = 0f;
        private float velPitch = 0f;

        void PolarCam()
        {
            if (cam == null) return;

            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) > 0.001f)
            {
                orbitDist = Mathf.Clamp(orbitDist - scroll * zoomSpeed * 25f, 3f, maxZoom);
            }

            bool orb = false;
            if (Input.GetMouseButton(0) && !IsMouseOverUI()) orb = true;
            if (Input.GetMouseButton(1)) orb = true;

            Vector2 cur = new Vector2(Input.mousePosition.x, Input.mousePosition.y);
            Vector2 delta = (lastMouse.x >= 0f) ? cur - lastMouse : Vector2.zero;
            lastMouse = cur;

            const float sens = 0.15f;

            if (orb)
            {
                // Rotacion directa: X gira horizontal, Y sube/baja. Inercia capturada.
                velYaw = delta.x * sens;
                velPitch = delta.y * sens;
                yaw += velYaw;
                pitch += velPitch;
                pitch = Mathf.Clamp(pitch, -89f, 89f);
            }
            else
            {
                lastMouse = cur;
                // Inercia suave: sigue deslizandose y frena gradualmente
                if (Mathf.Abs(velYaw) > 0.02f || Mathf.Abs(velPitch) > 0.02f)
                {
                    yaw += velYaw;
                    pitch += velPitch;
                    pitch = Mathf.Clamp(pitch, -89f, 89f);
                    float decay = Mathf.Pow(0.3f, Time.deltaTime * 10f);
                    velYaw *= decay;
                    velPitch *= decay;
                }
                else
                {
                    velYaw = 0f;
                    velPitch = 0f;
                }
            }

            // Pan con boton central + arrastrar
            if (Input.GetMouseButton(2))
            {
                Vector3 rightc = cam.transform.right;
                Vector3 upc = cam.transform.up;
                orbitTarget -= rightc * Input.GetAxis("Mouse X") * panSpeed * orbitDist * 0.02f;
                orbitTarget -= upc * Input.GetAxis("Mouse Y") * panSpeed * orbitDist * 0.02f;
            }

            // Posicion esferica determinista (sin gimbal lock, gira 360 horizontal y vertical)
            float ry = yaw * Mathf.Deg2Rad;
            float rp = pitch * Mathf.Deg2Rad;
            Vector3 offset = new Vector3(
                Mathf.Sin(ry) * Mathf.Cos(rp),
                Mathf.Sin(rp),
                Mathf.Cos(ry) * Mathf.Cos(rp)
            ) * orbitDist;
            cam.transform.position = orbitTarget + offset;
            cam.transform.LookAt(orbitTarget);
        }

        // ---------- helpers ----------
        static Vector3 V(List<double> p)
        {
            if (p == null || p.Count < 3) return Vector3.zero;
            return new Vector3((float)p[0], (float)p[1], (float)p[2]);
        }

        static string P(Vector3 v) => "(" + v.x.ToString("F3") + ", " + v.y.ToString("F3") + ", " + v.z.ToString("F3") + ")";

        static Material LineMaterial(Color color)
        {
            var sh = Shader.Find("Sprites/Default");
            if (sh == null) sh = Shader.Find("Legacy Shaders/Particles/Alpha Blended");
            if (sh == null) sh = Shader.Find("Standard");
            var mat = new Material(sh);
            mat.color = color;
            return mat;
        }

        static Texture2D MakeTex(int w, int h, Color col)
        {
            var t = new Texture2D(w, h);
            for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) t.SetPixel(x, y, col);
            t.Apply();
            return t;
        }

        void SetStatus(string msg) { if (statusText != null) statusText.text = msg; }
        void ToggleType(string type, bool v) { typeVisible[type] = v; ReapplyAll(); }
        void ToggleFloor(string floor, bool v) { floorVisible[floor] = v; ReapplyAll(); }

        static Color ColorFor(string category)
        {
            switch (category)
            {
                case "beam": return new Color(1f, 0.55f, 0.1f);
                case "column": return new Color(1f, 0.45f, 0f);
                case "column_plan": return new Color(1f, 0.5f, 0.05f);
                case "wall": return new Color(1f, 0.66f, 0.22f);
                case "support": return new Color(0.85f, 0.4f, 0.05f);
                case "diaphragm": return new Color(0.9f, 0.9f, 1f);
                case "slab": return new Color(1f, 0.62f, 0.15f);
                case "slab_edge": return new Color(1f, 0.72f, 0.3f);
                case "axis": return new Color(0.8f, 0.8f, 0.8f);
                case "node": return new Color(1f, 0.82f, 0.3f);
                case "cad_reference": return new Color(0.6f, 0.7f, 0.8f);
                default: return new Color(0.7f, 0.7f, 0.7f);
            }
        }
    }

    // Datos del elemento seleccionable, incluye campos de tributaria (contrato de Luis)
    public class ElementInfo : MonoBehaviour
    {
        public GameObject go;
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
