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
        private TributaryData tributaries;
        private readonly Dictionary<string, Vector2> memberTrib = new Dictionary<string, Vector2>();
        private readonly Dictionary<string, List<GameObject>> byType = new Dictionary<string, List<GameObject>>();
        private readonly Dictionary<string, List<GameObject>> byFloor = new Dictionary<string, List<GameObject>>();
        private readonly Dictionary<string, bool> typeVisible = new Dictionary<string, bool>();
        private readonly Dictionary<string, bool> floorVisible = new Dictionary<string, bool>();
        private readonly List<ElementInfo> allElements = new List<ElementInfo>();
        private static readonly Dictionary<string, Material> MaterialsByCat = new Dictionary<string, Material>();

        private Camera cam;
        private Transform selected = null;
        private string lastInfo = "";
        private bool labelsVisible = false;
        private ElementInfo lastSelected = null;
        private string searchText = "";
        private string searchResult = "";
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
            { "cad_reference", "Lineas CAD ref." },
            { "tributary", "Areas tributarias" }
        };

        private static readonly Dictionary<string, int> FloorOrder = new Dictionary<string, int>
        {
            { "base", 0 }, { "1S", 1 }, { "S1", 1 }, { "1", 2 }, { "P1", 2 }, { "2", 3 }, { "P2", 3 }, { "3", 4 }, { "P3", 4 }, { "4", 5 }, { "P4", 5 }
        };

        void Start()
        {
            cam = Camera.main;
            if (cam == null) cam = Camera.main;
            // El modelo usa Z como altura (piso/m = x,y ; nivel = z).
            // Girar el contenedor de la escena -90° en X: su +Z (altura) pasa a ser +Y
            // de Unity (vertical real), y la planta queda en el plano XZ horizontal.
            transform.rotation = Quaternion.Euler(-90f, 0f, 0f);
            // centro del modelo en coordenadas giratorias (era (16.4,14.7,6.0) en coords. de modelo)
            orbitTarget = new Vector3(16.41f, 5.99f, -14.73f);
            if (cam != null)
            {
                cam.clearFlags = CameraClearFlags.Skybox;
                RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
                RenderSettings.ambientSkyColor = new Color(0.6f, 0.7f, 0.85f);
            }
            LoadMaterials();
            model = JsonLoader.LoadModel(jsonFileName);
            if (model == null) { SetStatus("Error: no se pudo cargar el modelo."); return; }
            tributaries = JsonLoader.LoadTributaries();
            if (tributaries != null)
            {
                // indice por elementTag para asignar carga tributaria a vigas/columnas/apoyos
                memberTrib.Clear();
                if (tributaries.areas != null)
                    foreach (var a in tributaries.areas)
                        if (!string.IsNullOrEmpty(a.elementTag))
                            memberTrib[a.elementTag] = new Vector2((float)a.area_m2, (float)a.load_kN);
                if (tributaries.point_areas != null)
                    foreach (var a in tributaries.point_areas)
                        if (!string.IsNullOrEmpty(a.elementTag) && !memberTrib.ContainsKey(a.elementTag))
                            memberTrib[a.elementTag] = new Vector2((float)a.area_m2, (float)a.load_kN);
            }
            BuildScene();
            if (tributaries != null) BuildTributaries();
            SetStatus($"{model.solids?.Count ?? 0} solidos, {model.segments?.Count ?? 0} lineas CAD, {model.labels?.Count ?? 0} etiquetas");
        }

        void LoadMaterials()
        {
            MaterialsByCat["beam"] = LoadMat("MatAcero", new Color(1f, 0.7f, 0.25f));
            MaterialsByCat["column"] = LoadMat("MatConcreto", new Color(1f, 0.6f, 0.2f));
            MaterialsByCat["column_plan"] = LoadMat("MatConcreto", new Color(1f, 0.65f, 0.22f));
            MaterialsByCat["wall"] = LoadMat("MatConcreto", new Color(1f, 0.75f, 0.3f));
            MaterialsByCat["support"] = LoadMat("MatAluminio", new Color(0.9f, 0.5f, 0.1f));
            MaterialsByCat["slab"] = LoadMat("MatVidrio", new Color(0.45f, 0.72f, 0.85f));
            MaterialsByCat["slab_edge"] = LoadMat("MatVidrio", new Color(0.6f, 0.8f, 0.9f));
            MaterialsByCat["diaphragm"] = LoadMat("MatVidrio", new Color(0.9f, 0.9f, 1f));
            MaterialsByCat["axis"] = LoadMat("MatAluminio", new Color(0.85f, 0.85f, 0.85f));
            MaterialsByCat["node"] = LoadMat("MatAcero", new Color(1f, 0.85f, 0.35f));
            MaterialsByCat["cad_reference"] = LoadMat("MatAcero", new Color(0.6f, 0.7f, 0.8f));
        }

        static Material LoadMat(string resName, Color tint)
        {
            var m = Resources.Load<Material>("Materials/" + resName);
            if (m == null) return null;
            var inst = UnityEngine.Object.Instantiate(m);
            inst.name = resName;
            inst.color = tint;
            return inst;
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
            go.name = string.IsNullOrEmpty(solid.id) ? solid.solidTag : solid.id;
            var data = go.AddComponent<ElementInfo>();
            data.go = go;
            data.kind = solid.kind;
            data.id = string.IsNullOrEmpty(solid.id) ? solid.solidTag : solid.id;
            data.humanId = string.IsNullOrEmpty(solid.human_id) ? (string.IsNullOrEmpty(solid.id) ? solid.solidTag : solid.id) : solid.human_id;
            data.elementTag = solid.elementTag;
            data.category = solid.category;
            data.floor = solid.floor;
            data.building = solid.building;
            data.sourceLayer = solid.source_layer;
            data.sourceDxf = solid.source_dxf;
            data.axisX = solid.axis_x;
            data.axisY = solid.axis_y;
            data.lengthM = solid.length_m;
            data.widthM = solid.width_m;
            data.heightM = solid.height_m;
            data.materialName = solid.material ?? "hormigon";
            data.coordZBottom = solid.model_z_m;
            data.coordZTop = solid.model_z_m;

            // carga tributaria soportada (si calculada)
            if (solid.elementTag != null && memberTrib.TryGetValue(solid.elementTag, out var trib))
            {
                data.tribAreaM2 = trib.x;
                data.tribLoadKN = trib.y;
                data.tribFromTag = true;
            }

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
                data.coordCenter = center;
            }
            else if (solid.center != null)
            {
                go.transform.position = V(solid.center);
                go.transform.localScale = new Vector3((float)(solid.width_m <= 0 ? 0.4 : solid.width_m), (float)(solid.depth_m <= 0 ? solid.width_m : solid.depth_m), (float)(solid.height_m <= 0 ? 0.6 : solid.height_m));
                data.nodeI = V(solid.center);
                data.nodeJ = V(solid.center);
                data.coordCenter = V(solid.center);
            }
            var rnd = go.GetComponent<Renderer>();
            if (rnd != null) { rnd.sharedMaterial = MatFor(solid.category); data.baseColor = tintOf(solid.category); }
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
            lr.material = LineMaterial(tintOf(seg.category == "axis" ? "axis" : "cad_reference"));
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
            lr.material = LineMaterial(tintOf("diaphragm"));
            Register(go, "diaphragm", dia.floor);
        }

        // ---------- Areas tributarias ----------
        void BuildTributaries()
        {
            if (tributaries == null) return;
            float maxLoad = 1f;
            if (tributaries.areas != null)
                foreach (var a in tributaries.areas) maxLoad = Mathf.Max(maxLoad, (float)a.load_kN);
            if (tributaries.point_areas != null)
                foreach (var a in tributaries.point_areas) maxLoad = Mathf.Max(maxLoad, (float)a.load_kN);

            // altura z de cada slab (por building+floor) para apoyar las areas sobre la losa
            var slabZ = new Dictionary<string, float>();
            if (model.solids != null)
            {
                foreach (var s in model.solids)
                {
                    if (s.category != "slab" || s.center == null || s.center.Count < 3) continue;
                    string key = (s.building ?? "") + "|" + (s.floor ?? "");
                    slabZ[key] = (float)s.center[2];
                }
            }

            int idx = 0;
            if (tributaries.areas != null)
            {
                foreach (var a in tributaries.areas)
                {
                    if (a.polygon == null || a.polygon.Count < 3) continue;
                    float z = slabZ.TryGetValue((a.building ?? "") + "|" + (a.floor ?? ""), out var zz) ? zz : 0f;
                    z += 0.06f;
                    var ei = CreateTribPoly("trib_" + (a.beam_id ?? idx.ToString()), a.polygon, z, maxLoad, (float)a.load_kN, "tributary", a.building, a.floor, a.beam_id, a.elementTag);
                    ei.tribAreaM2 = a.area_m2;
                    ei.tribLoadKN = a.load_kN;
                    if (a.start != null && a.start.Count >= 2) ei.nodeI = new Vector3((float)a.start[0], (float)a.start[1], z);
                    if (a.end != null && a.end.Count >= 2) ei.nodeJ = new Vector3((float)a.end[0], (float)a.end[1], z);
                    if (a.mid != null && a.mid.Count >= 2) ei.coordCenter = new Vector3((float)a.mid[0], (float)a.mid[1], z);
                    idx++;
                }
            }
            if (tributaries.point_areas != null)
            {
                foreach (var a in tributaries.point_areas)
                {
                    if (a.polygon == null || a.polygon.Count < 3) continue;
                    float z = slabZ.TryGetValue((a.building ?? "") + "|" + (a.floor ?? ""), out var zz) ? zz : 0f;
                    z += 0.06f;
                    var ei = CreateTribPoly("tribpt_" + (a.elementTag ?? idx.ToString()), a.polygon, z, maxLoad, (float)a.load_kN, "tributary_point", a.building, a.floor, a.member_id, a.elementTag);
                    ei.tribAreaM2 = a.area_m2;
                    ei.tribLoadKN = a.load_kN;
                    idx++;
                }
            }
        }

        ElementInfo CreateTribPoly(string name, List<Point2D> polygon, float z, float maxLoad, float loadKN, string cat, string building, string floor, string id, string elementTag)
        {
            var go = new GameObject(name);
            var mf = go.AddComponent<MeshFilter>();
            var mr = go.AddComponent<MeshRenderer>();
            mf.mesh = PolygonMesh(polygon, z);
            var mc = go.AddComponent<MeshCollider>();
            mc.sharedMesh = mf.mesh;
            float t = maxLoad < 1e-6f ? 0f : Mathf.Clamp01(loadKN / maxLoad);
            mr.sharedMaterial = TributaryMat(t);
            var ei = go.AddComponent<ElementInfo>();
            ei.go = go;
            ei.id = id;
            ei.humanId = id;
            ei.elementTag = elementTag;
            ei.category = cat;
            ei.floor = floor;
            ei.building = building;
            ei.baseColor = mr.sharedMaterial.color;
            ei.baseMat = mr.sharedMaterial;
            Register(go, "tributary", floor);
            allElements.Add(ei);
            return ei;
        }

        static Mesh PolygonMesh(List<Point2D> polygon, float z)
        {
            if (polygon == null || polygon.Count < 3) return new Mesh();
            int n = polygon.Count;
            var verts = new Vector3[n];
            for (int i = 0; i < n; i++)
            {
                verts[i] = new Vector3((float)polygon[i].x, (float)polygon[i].y, z);
            }
            // centroide como punto central para un triangulo fan
            Vector3 cen = Vector3.zero;
            foreach (var v in verts) cen += v;
            cen /= n;
            var mesh = new Mesh();
            var meshVerts = new Vector3[n + 1];
            meshVerts[0] = cen;
            for (int i = 0; i < n; i++) meshVerts[i + 1] = verts[i];
            // doble cara: triangulos en ambos sentidos para evitar culling por winding
            var tris = new int[n * 6];
            for (int i = 0; i < n; i++)
            {
                int b = i + 1, c = (i + 1) % n + 1;
                tris[i * 6] = 0; tris[i * 6 + 1] = b; tris[i * 6 + 2] = c;
                tris[i * 6 + 3] = 0; tris[i * 6 + 4] = c; tris[i * 6 + 5] = b;
            }
            mesh.vertices = meshVerts;
            mesh.triangles = tris;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        static Material TributaryMat(float t)
        {
            // azul (baja carga) -> verde -> amarillo -> rojo (alta carga)
            Color col = Color.Lerp(Color.Lerp(new Color(0.2f, 0.5f, 1f), new Color(0.2f, 0.9f, 0.3f), t < 0.5f ? t * 2f : 1f),
                Color.Lerp(new Color(0.9f, 0.9f, 0.2f), new Color(1f, 0.2f, 0.1f), t < 0.5f ? 0f : (t - 0.5f) * 2f), 0.5f);
            // sin iluminacion: evita negros por normales canceladas en malla doble cara
            var sh = Shader.Find("Sprites/Default");
            if (sh == null) sh = Shader.Find("Legacy Shaders/Particles/Alpha Blended");
            if (sh == null) sh = Shader.Find("Unlit/Color");
            if (sh == null) sh = Shader.Find("Standard");
            var mat = new Material(sh);
            if (mat != null)
            {
                mat.color = new Color(col.r, col.g, col.b, 0.55f);
                mat.SetFloat("_Mode", 3f);
                mat.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
                mat.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
                mat.EnableKeyword("_ALPHAPREMULTIPLY_ON");
                mat.renderQueue = 3000;
            }
            return mat;
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
                    go.GetComponent<Renderer>().material.color = tintOf("node");
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
            // Seleccion SOLO con click limpio (sin arrastre). Arrastrar = rotar camara.
            if (Input.GetMouseButtonDown(0) && !IsMouseOverUI())
            {
                mouseDownPos = MousePos2();
                clickPending = true;
            }
            if (clickPending && (MousePos2() - mouseDownPos).sqrMagnitude > 49f) clickPending = false;
            if (Input.GetMouseButtonUp(0))
            {
                if (clickPending && !IsMouseOverUI()) TrySelect(Input.mousePosition);
                clickPending = false;
            }
            if (Input.GetKeyDown(KeyCode.Return) && !string.IsNullOrEmpty(searchText)) DoSearch();
            if (Input.GetKeyDown(KeyCode.Escape)) RestoreHighlight();
            PolarCam();
        }

        bool IsMouseOverUI()
        {
            Vector2 m = Input.mousePosition;
            m.y = Screen.height - m.y;
            // Zona panel derecho (navegacion + buscar, arriba)
            if (m.x > Screen.width - 260 && m.y < 170) return true;
            // Zona panel izquierdo (pisos y tipos)
            if (m.x < 260 && m.y > 225 && m.y < 705) return true;
            // Zona panel de info (arriba izquierda)
            if (m.x < 380 && m.y < 210) return true;
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
                    Select(ei);
                    return;
                }
            }
        }

        void Select(ElementInfo ei)
        {
            RestoreHighlight();
            selected = ei.go.transform;
            ei.isHighlighted = true;
            var rnd = ei.go.GetComponent<Renderer>();
            if (rnd != null && rnd.sharedMaterial != null)
            {
                // materializar solo para esta pieza: NO altera el material compartido
                // de la categoria, por lo que el color base (naranja) se conserva.
                var baseMat = rnd.sharedMaterial;
                var mat = rnd.material;
                mat.color = Color.Lerp(baseMat.color, Color.cyan, 0.65f);
                mat.EnableKeyword("_EMISSION");
                mat.SetColor("_EmissionColor", new Color(0.15f, 0.3f, 0.35f));
            }
            ShowInfo(ei);
        }

        void RestoreHighlight()
        {
            if (selected != null)
            {
                var ei = selected.GetComponent<ElementInfo>();
                if (ei != null)
                {
                    var rnd = ei.go != null ? ei.go.GetComponent<Renderer>() : null;
                    if (rnd != null)
                    {
                        if (ei.category == "tributary" || ei.category == "tributary_point")
                        {
                            // material propio por area tributaria: restaurar su color base
                            rnd.sharedMaterial = ei.baseMat;
                            if (rnd.sharedMaterial != null) rnd.sharedMaterial.color = ei.baseColor;
                        }
                        else
                        {
                            // material compartido de categoria (base intacta = naranja)
                            var baseMat = MatFor(ei.category);
                            if (baseMat != null)
                            {
                                rnd.sharedMaterial = baseMat;
                            }
                            else if (rnd.sharedMaterial != null)
                            {
                                rnd.sharedMaterial.color = ei.baseColor;
                                rnd.sharedMaterial.DisableKeyword("_EMISSION");
                                rnd.sharedMaterial.SetColor("_EmissionColor", Color.black);
                            }
                        }
                    }
                    ei.isHighlighted = false;
                }
            }
            selected = null;
        }

        void ShowInfo(ElementInfo ei)
        {
            string cat = TypeLabels.ContainsKey(ei.category) ? TypeLabels[ei.category] : ei.category;
            string section = "-";
            if (ei.widthM > 0 && ei.heightM > 0) section = ei.widthM.ToString("F3") + " x " + ei.heightM.ToString("F3") + " m";
            string trib = ei.tribAreaM2 > 0 ? ei.tribAreaM2.ToString("F3") + " m2 / " + ei.tribLoadKN.ToString("F3") + " kN" : "-";
            string id = string.IsNullOrEmpty(ei.humanId) ? ei.id : ei.humanId;
            string ejes = string.IsNullOrEmpty(ei.axisX) ? (string.IsNullOrEmpty(ei.axisY) ? "-" : ei.axisY) : (string.IsNullOrEmpty(ei.axisY) ? ei.axisX : ei.axisX + " / " + ei.axisY);
            string coord = "centro " + P(ei.coordCenter);
            if (ei.coordCenter == Vector3.zero && ei.nodeI != Vector3.zero) coord = "i " + P(ei.nodeI) + "  j " + P(ei.nodeJ);
            string cargaLine = "";
            if (ei.category == "tributary" || ei.category == "tributary_point")
            {
                cargaLine = $"Area tributaria: {ei.tribAreaM2.ToString("F3")} m2\n" +
                    $"Carga gravitacional: {ei.tribLoadKN.ToString("F3")} kN (qG={(tributaries != null ? tributaries.qG_kN_m2.ToString("F3") : "?")} kN/m2)";
            }
            else if (ei.tribFromTag)
            {
                cargaLine = $"Carga tributaria que soporta: {ei.tribLoadKN.ToString("F3")} kN\n" +
                    $"Area tributaria asociada: {ei.tribAreaM2.ToString("F3")} m2";
            }
            lastInfo = $"ID: {id}\n" +
                $"elementTag: {ei.elementTag ?? "-"}\n" +
                $"Tipo: {cat}\n" +
                $"Piso: {ei.floor}\n" +
                $"Edificio: {(string.IsNullOrEmpty(ei.building) ? "-" : ei.building)}\n" +
                $"Ejes: {ejes}\n" +
                $"Coordenadas: {coord}\n" +
                $"Seccion: {section}\n" +
                $"Material: {ei.materialName}\n" +
                $"Longitud: {ei.lengthM.ToString("F3")} m\n" +
                $"Tributaria: {trib}" +
                (string.IsNullOrEmpty(cargaLine) ? "" : "\n" + cargaLine);
            if (infoText != null) infoText.text = lastInfo;
            lastSelected = ei;
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
            var btnc = new GUIStyle(GUI.skin.button);
            btnc.fontSize = 12;
            string toCopy = "";
            if (lastSelected != null) toCopy = string.IsNullOrEmpty(lastSelected.humanId) ? lastSelected.id : lastSelected.humanId;
            if (!string.IsNullOrEmpty(toCopy) && GUI.Button(new Rect(10 + 360 + 8, 10, 180, 26), "Copiar ID: " + toCopy, btnc))
            {
                GUIUtility.systemCopyBuffer = toCopy;
                lastInfo = lastInfo + "\n[ID copiado: " + toCopy + "]";
                infoText.text = lastInfo;
            }
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

            // --- Busqueda por ID ---
            GUI.Box(new Rect(x, y + 88, 250, 76), "");
            GUI.DrawTexture(new Rect(x, y + 88, 250, 76), MakeTex(2, 2, new Color(0.02f, 0.04f, 0.08f, 0.85f)));
            GUI.Label(new Rect(x + 8, y + 92, 240, 18), "Buscar por ID (ej. E1-P2-C-034)", ttl);
            searchText = GUI.TextField(new Rect(x + 8, y + 114, 160, 24), searchText, 40);
            if (GUI.Button(new Rect(x + 172, y + 114, 68, 24), "Buscar", t2)) DoSearch();
            if (!string.IsNullOrEmpty(searchResult)) GUI.Label(new Rect(x + 8, y + 142, 240, 18), searchResult, ttl);

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
                Vector3 cp = transform.TransformPoint(ei.nodeI + (ei.nodeJ - ei.nodeI) * 0.5f);
                Vector3 sp = cam.WorldToScreenPoint(cp);
                if (sp.z <= 0) continue;
                sp.y = sh - sp.y;
                if (sp.x < 0 || sp.x > sw || sp.y < 0 || sp.y > sh) continue;
                GUI.Label(new Rect(sp.x - 30, sp.y - 8, 80, 16), ShortTag(ei.id), ls);
            }
        }

        static string ShortTag(string tag) => tag.Replace("SOL_", "").Replace("CAD_", "").Replace("seg_", "");

        // ---------- Busqueda por ID ----------
        void DoSearch()
        {
            if (string.IsNullOrEmpty(searchText)) return;
            string q = searchText.Trim().ToLowerInvariant();
            ElementInfo hit = null;
            foreach (var ei in allElements)
            {
                if (ei == null || ei.go == null) continue;
                string hay = (ei.humanId ?? "") + " " + (ei.id ?? "") + " " + (ei.elementTag ?? "");
                if (hay.ToLowerInvariant().Contains(q)) { hit = ei; break; }
            }
            if (hit != null)
            {
                if (hit.category == "node") { searchResult = hit.id; return; }
                hit.go.SetActive(true);
                var rk = hit.category; if (typeVisible.ContainsKey(rk)) { typeVisible[rk] = true; ReapplyAll(); }
                var rf = hit.floor; if (floorVisible.ContainsKey(rf)) { floorVisible[rf] = true; ReapplyAll(); }
                Select(hit);
                searchResult = "Encontrado: " + (string.IsNullOrEmpty(hit.humanId) ? hit.id : hit.humanId);
                // centrar camara en el elemento (coord. locales del modelo -> mundo)
                Vector3 c = (hit.nodeI + hit.nodeJ) * 0.5f;
                if (c == Vector3.zero) c = hit.coordCenter;
                orbitTarget = transform.TransformPoint(c);
                orbitDist = Mathf.Clamp(60f, 5f, maxZoom);
            }
            else
            {
                searchResult = "Sin resultado: " + searchText;
            }
        }

        // ---------- Camara orbital (esferica: estable, gira en todos los sentidos) ----------
        private Vector2 lastMouse = new Vector2(-1f, -1f);
        private float velYaw = 0f;
        private float velPitch = 0f;
        private Vector2 mouseDownPos;
        private bool clickPending = false;

        Vector2 MousePos2()
        {
            Vector3 m = Input.mousePosition;
            return new Vector2(m.x, m.y);
        }

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
                // Rotacion directa con sentido "grabar y girar" (el modelo sigue al cursor).
                velYaw = -delta.x * sens;
                velPitch = -delta.y * sens;
                yaw += velYaw;
                pitch += velPitch;
                pitch = Mathf.Clamp(pitch, -89f, 89f);
            }
            else
            {
                lastMouse = cur;
                // Inercia suave con frenado rapido: deja de girar en ~0.25s
                if (Mathf.Abs(velYaw) > 0.02f || Mathf.Abs(velPitch) > 0.02f)
                {
                    yaw += velYaw;
                    pitch += velPitch;
                    pitch = Mathf.Clamp(pitch, -89f, 89f);
                    float decay = Mathf.Pow(0.02f, Time.deltaTime * 12f);
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
            if (MaterialsByCat.TryGetValue("axis", out var axisMat) && axisMat != null) return axisMat;
            var sh = Shader.Find("Sprites/Default");
            if (sh == null) sh = Shader.Find("Legacy Shaders/Particles/Alpha Blended");
            if (sh == null) sh = Shader.Find("Standard");
            var mat = new Material(sh);
            mat.color = color;
            return mat;
        }

        static Material MatFor(string category)
        {
            if (MaterialsByCat.TryGetValue(category ?? "", out var m) && m != null) return m;
            if (MaterialsByCat.TryGetValue("beam", out var def) && def != null) return def;
            return null;
        }

        static Color tintOf(string category)
        {
            if (MaterialsByCat.TryGetValue(category ?? "", out var m) && m != null) return m.color;
            return new Color(0.8f, 0.8f, 0.8f);
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
    }

    // Datos del elemento seleccionable, incluye campos de tributaria (contrato de Luis)
    public class ElementInfo : MonoBehaviour
    {
        public GameObject go;
        public string id;
        public string humanId;
        public string elementTag;
        public string category;
        public string kind;
        public string floor;
        public string building;
        public string sourceLayer;
        public string sourceDxf;
        public string axisX;
        public string axisY;
        public string materialName;
        public double widthM;
        public double heightM;
        public double lengthM;
        public Vector3 nodeI;
        public Vector3 nodeJ;
        public Vector3 coordCenter;
        public double coordZBottom;
        public double coordZTop;
        public double tribAreaM2;
        public double tribLoadKN;
        public bool tribFromTag;
        public Color baseColor;
        public Material baseMat;
        public bool isHighlighted = false;
    }
}
