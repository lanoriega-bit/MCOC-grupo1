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
        private SeismicData seismic;
        private AnalysisResultsData analysisResults;
        private AnalysisCasesData analysisCases;
        private P1L3DeliveryData delivery;
        private CapacityData capacity;
        private Texture2D fiberTexture;
        private Texture2D momentCurvatureTexture;
        private Texture2D pmInteractionTexture;
        private bool deliveryPanelVisible = false;
        private int deliveryTab = 0;
        private string activeAnalysisCase = "R";
        private bool uiHidden = false;
        private bool inspectorVisible = true;
        private Texture2D expandedGraph = null;
        private string expandedGraphTitle = "";
        private float deformationScaleEX = 1f;
        private float deformationScaleEY = 1f;
        private readonly Dictionary<string, Vector2> memberTrib = new Dictionary<string, Vector2>();
        private readonly Dictionary<string, AnalysisElementResult> analysisByElementId = new Dictionary<string, AnalysisElementResult>();
        private readonly Dictionary<string, ExcludedAnalysisElement> excludedByElementId = new Dictionary<string, ExcludedAnalysisElement>();
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
        private Vector2 infoScroll = Vector2.zero;
        private Vector2 controlsScroll = Vector2.zero;
        private string inspectorIdentity = "";
        private string inspectorGeometry = "";
        private string inspectorProperties = "";
        private string inspectorTributary = "";
        private string inspectorAnalysis = "";
        private string inspectorCapacity = "";
        private bool inspectorGeometryOpen = false;
        private bool inspectorPropertiesOpen = false;
        private bool inspectorTributaryOpen = false;
        private bool inspectorAnalysisOpen = true;
        private bool inspectorCapacityOpen = false;
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
            { "tributary", "Areas tributarias" },
            { "tributary_point", "Tributarias a soportes" },
            { "seismic_arrow", "Sismo EX/EY" },
            { "seismic_cm", "Centros de masa" },
            { "seismic_mass", "Masa por piso" },
            { "seismic_shear", "Corte basal" },
            { "seismic_pattern", "Patron sismico" },
            { "seismic_deform", "Deformada (sentido)" },
            { "seismic_torsion", "Torsion de piso" }
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
            analysisResults = JsonLoader.LoadAnalysisResults();
            analysisCases = JsonLoader.LoadAnalysisCases();
            delivery = JsonLoader.LoadDelivery();
            capacity = JsonLoader.LoadCapacity();
            fiberTexture = JsonLoader.LoadPng("fiber_section.png");
            momentCurvatureTexture = JsonLoader.LoadPng("moment_curvature.png");
            pmInteractionTexture = JsonLoader.LoadPng("pm_interaction.png");
            ActivateAnalysisCase(analysisCases != null && !string.IsNullOrEmpty(analysisCases.default_case) ? analysisCases.default_case : "R");
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
            seismic = JsonLoader.LoadSeismic();
            if (seismic != null) BuildSeismic();
            RunVisibilitySelfCheck();
            ResetPresentation();
            SetStatus($"{model.solids?.Count ?? 0} solidos, {model.segments?.Count ?? 0} lineas CAD, {model.labels?.Count ?? 0} etiquetas");
        }

        void ActivateAnalysisCase(string requested)
        {
            string normalized = (requested ?? "R").Replace("CASE_", "").ToUpperInvariant();
            AnalysisResultsData chosen = null;
            if (analysisCases != null && analysisCases.cases != null)
            {
                foreach (var item in analysisCases.cases)
                {
                    if (item == null) continue;
                    string candidate = (item.case_name ?? "").Replace("CASE_", "").ToUpperInvariant();
                    if (candidate == normalized) { chosen = item; break; }
                }
            }
            if (chosen == null) chosen = analysisResults;
            if (chosen == null) return;

            activeAnalysisCase = normalized;
            analysisResults = chosen;
            analysisByElementId.Clear();
            excludedByElementId.Clear();
            if (chosen.elements != null)
                foreach (var result in chosen.elements)
                    if (!string.IsNullOrEmpty(result.element_id)) analysisByElementId[result.element_id] = result;
            if (chosen.excluded_elements != null)
                foreach (var item in chosen.excluded_elements)
                    if (!string.IsNullOrEmpty(item.element_id)) excludedByElementId[item.element_id] = item;
            if (lastSelected != null) ShowInfo(lastSelected);
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

        // ---------- Sismo EX/EY (Integrante B) ----------
        void BuildSeismic()
        {
            if (seismic == null || seismic.floors == null) return;
            float maxF = 1f;
            float maxMass = 1f;
            float maxTor = 1f;
            foreach (var f in seismic.floors)
            {
                maxF = Mathf.Max(maxF, (float)f.F_EX_kN);
                maxF = Mathf.Max(maxF, (float)f.F_EY_kN);
                maxMass = Mathf.Max(maxMass, (float)f.mass_ton);
                maxTor = Mathf.Max(maxTor, (float)f.M_torsion_EX_kNm);
                maxTor = Mathf.Max(maxTor, (float)f.M_torsion_EY_kNm);
            }
            foreach (var f in seismic.floors)
            {
                float z = (float)f.z_m;
                Vector3 cm = new Vector3((float)f.cm_x, (float)f.cm_y, z);
                CreateArrow("sismo_EX_" + f.building + "_" + f.floor, cm, Vector3.right, (float)f.F_EX_kN, maxF, new Color(1f, 0.3f, 0.2f), "seismic_arrow", f.floor, f.building, "EX");
                CreateArrow("sismo_EY_" + f.building + "_" + f.floor, cm, Vector3.up, (float)f.F_EY_kN, maxF, new Color(0.3f, 0.5f, 1f), "seismic_arrow", f.floor, f.building, "EY");
                CreateCmMarker("sismo_CM_" + f.building + "_" + f.floor, cm, f);
                CreateMassBar("sismo_M_" + f.building + "_" + f.floor, cm, (float)f.mass_ton, maxMass, f.floor, f.building);
                CreatePatternBar("sismo_patron_EX_" + f.building + "_" + f.floor, cm, Vector3.right, (float)f.F_EX_kN, maxF, new Color(1f, 0.35f, 0.25f), f);
                CreatePatternBar("sismo_patron_EY_" + f.building + "_" + f.floor, cm, Vector3.up, (float)f.F_EY_kN, maxF, new Color(0.35f, 0.55f, 1f), f);
                CreateTorsionArc("sismo_T_EX_" + f.building + "_" + f.floor, cm, (float)f.M_torsion_EX_kNm, maxTor, 0f, f);
                CreateTorsionArc("sismo_T_EY_" + f.building + "_" + f.floor, cm, (float)f.M_torsion_EY_kNm, maxTor, 180f, f);
            }
            foreach (var b in seismic.buildings)
            {
                CreateBuildingLevelVisuals(b);
                CreateDeformFrame(b, true);
                CreateDeformFrame(b, false);
            }
        }

        void CreateBuildingLevelVisuals(SeismicBuilding b)
        {
            if (b == null || b.floors_EX == null || b.floors_EX.Count == 0) return;
            Vector3 cmG = new Vector3((float)b.cm_x_m, (float)b.cm_y_m, 0f);
            float vMax = Mathf.Max(1f, (float)b.V_EX_kN);

            CreateArrow("sismo_V_EX_" + b.building, cmG, Vector3.right, (float)b.V_EX_kN, vMax, new Color(1f, 0.2f, 0.15f), "seismic_shear", "S1", b.building, "V_EX");
            CreateArrow("sismo_V_EY_" + b.building, cmG, Vector3.up, (float)b.V_EY_kN, vMax, new Color(0.2f, 0.4f, 1f), "seismic_shear", "S1", b.building, "V_EY");

            _shearLabels.Add(new Label2D((float)b.cm_x_m, (float)b.cm_y_m, 0f, $"Corte basal EX: {b.V_EX_kN:F1} kN", new Color(1f, 0.4f, 0.3f)));
            _shearLabels.Add(new Label2D((float)b.cm_x_m, (float)b.cm_y_m, 0f, $"Corte basal EY: {b.V_EY_kN:F1} kN", new Color(0.4f, 0.6f, 1f)));
        }

        // Patrón sísmico: barra horizontal proporcional a F EN el centro de masa de cada piso
        void CreatePatternBar(string name, Vector3 cm, Vector3 dir, float forceKN, float maxForce, Color color, SeismicFloor f)
        {
            float len = Mathf.Clamp(forceKN / maxForce * 14f, 0.3f, 14f);
            var go = new GameObject(name);
            var lr = go.AddComponent<LineRenderer>();
            lr.useWorldSpace = false;
            lr.positionCount = 2;
            lr.SetPosition(0, cm + new Vector3(0f, 0f, 0.4f));
            lr.SetPosition(1, cm + dir * len + new Vector3(0f, 0f, 0.4f));
            lr.startWidth = 0.4f; lr.endWidth = 0.4f;
            lr.material = SeismicLineMat(color);
            var ei = go.AddComponent<ElementInfo>();
            ei.go = go;
            ei.id = name;
            ei.humanId = "Patron " + name.Replace("sismo_patron_", "");
            ei.category = "seismic_pattern";
            ei.floor = f.floor;
            ei.building = f.building;
            ei.isSeismic = true;
            ei.seismicForceKN = forceKN;
            ei.baseColor = color;
            ei.nodeI = cm;
            ei.nodeJ = cm;
            Register(go, "seismic_pattern", f.floor);
            allElements.Add(ei);
        }

        // Deformada: usa exclusivamente desplazamientos nodales de la corrida OpenSees EX/EY.
        // El factor solo amplifica la forma para verla; no altera los resultados mostrados.
        void CreateDeformFrame(SeismicBuilding b, bool ex)
        {
            AnalysisResultsData analysisCase = FindAnalysisCaseData(ex ? "EX" : "EY");
            if (analysisCase == null || analysisCase.nodes == null || analysisCase.elements == null) return;
            var nodes = new Dictionary<int, AnalysisNodeResult>();
            float maxU = 0f;
            foreach (var node in analysisCase.nodes)
            {
                if (node == null) continue;
                nodes[node.node_tag] = node;
                float magnitude = Mathf.Sqrt((float)(node.ux_m * node.ux_m + node.uy_m * node.uy_m + node.uz_m * node.uz_m));
                maxU = Mathf.Max(maxU, magnitude);
            }
            float scale = maxU > 1.0e-9f ? Mathf.Clamp(8f / maxU, 1f, 250f) : 1f;
            if (ex) deformationScaleEX = scale; else deformationScaleEY = scale;
            Color color = ex ? new Color(1f, 0.15f, 0.1f) : new Color(0.2f, 0.55f, 1f);
            string elementPrefix = b.building == "EDIFICIO_1" ? "E1-" : "E2-";
            foreach (var element in analysisCase.elements)
            {
                if (element == null || string.IsNullOrEmpty(element.element_id) || !element.element_id.StartsWith(elementPrefix)) continue;
                if (!nodes.TryGetValue(element.node_i, out var ni) || !nodes.TryGetValue(element.node_j, out var nj)) continue;
                Vector3 p0 = V(ni.coord);
                Vector3 p1 = V(nj.coord);
                Vector3 d0 = new Vector3((float)ni.ux_m, (float)ni.uy_m, (float)ni.uz_m) * scale;
                Vector3 d1 = new Vector3((float)nj.ux_m, (float)nj.uy_m, (float)nj.uz_m) * scale;
                CreateDeformLine(p0 + d0, p1 + d1, color, b.building, element.floor ?? "");
            }
        }

        AnalysisResultsData FindAnalysisCaseData(string name)
        {
            if (analysisCases == null || analysisCases.cases == null) return null;
            foreach (var item in analysisCases.cases)
                if (item != null && (item.case_name ?? "").Replace("CASE_", "").ToUpperInvariant() == name.ToUpperInvariant()) return item;
            return null;
        }

        void CreateDeformLine(Vector3 p0, Vector3 p1, Color color, string building, string floor)
        {
            var go = new GameObject("def_" + building + "_" + floor);
            var lr = go.AddComponent<LineRenderer>();
            lr.useWorldSpace = false;
            lr.positionCount = 2;
            lr.SetPosition(0, p0);
            lr.SetPosition(1, p1);
            lr.startWidth = 0.28f; lr.endWidth = 0.28f;
            lr.material = SeismicLineMat(color);
            var ei = go.AddComponent<ElementInfo>();
            ei.go = go;
            ei.id = go.name;
            ei.humanId = "Deformada " + building + " " + floor;
            ei.category = "seismic_deform";
            ei.floor = floor;
            ei.building = building;
            ei.isSeismic = true;
            ei.baseColor = color;
            ei.nodeI = p0;
            ei.nodeJ = p1;
            Register(go, "seismic_deform", floor);
            allElements.Add(ei);
        }

        // Torsión de piso: arco horizontal con flecha que muestra giro del diafragma, radio ∝ Mt
        void CreateTorsionArc(string name, Vector3 cm, float torKNm, float maxTor, float startDeg, SeismicFloor f)
        {
            float r = 1.2f + (torKNm / Mathf.Max(1f, maxTor)) * 4f;
            int n = 24;
            var go = new GameObject(name);
            var lr = go.AddComponent<LineRenderer>();
            lr.useWorldSpace = false;
            lr.positionCount = n + 2;
            float a0 = startDeg * Mathf.Deg2Rad;
            for (int i = 0; i <= n; i++)
            {
                float a = a0 + i * (300f * Mathf.Deg2Rad / n);
                lr.SetPosition(i, cm + new Vector3(Mathf.Cos(a) * r, Mathf.Sin(a) * r, 0.5f));
            }
            float tipA = a0 + 300f * Mathf.Deg2Rad;
            Vector3 tip = cm + new Vector3(Mathf.Cos(tipA) * r, Mathf.Sin(tipA) * r, 0.5f);
            Vector3 tangent = new Vector3(-Mathf.Sin(tipA), Mathf.Cos(tipA), 0f);
            lr.SetPosition(n + 1, tip + tangent * r * 0.5f);
            lr.startWidth = 0.22f; lr.endWidth = 0.22f;
            lr.material = SeismicLineMat(new Color(1f, 0.3f, 0.6f));
            var ei = go.AddComponent<ElementInfo>();
            ei.go = go;
            ei.id = name;
            ei.humanId = "Torsion " + f.building + " " + f.floor;
            ei.category = "seismic_torsion";
            ei.floor = f.floor;
            ei.building = f.building;
            ei.isSeismic = true;
            ei.seismicForceKN = torKNm;
            ei.baseColor = new Color(1f, 0.3f, 0.6f);
            ei.nodeI = cm;
            ei.nodeJ = cm;
            Register(go, "seismic_torsion", f.floor);
            allElements.Add(ei);
        }

        void CreateMassBar(string name, Vector3 cm, float massTon, float maxMass, string floor, string building)
        {
            float h = 0.4f + (massTon / maxMass) * 8f;
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.position = cm + new Vector3(0.5f, -0.5f, h * 0.5f);
            go.transform.localScale = new Vector3(0.35f, 0.35f, h);
            var rnd = go.GetComponent<Renderer>();
            rnd.sharedMaterial = SeismicLineMat(new Color(1f, 0.65f, 0.1f));
            var ei = go.AddComponent<ElementInfo>();
            ei.go = go;
            ei.id = name;
            ei.humanId = "Masa " + name.Replace("sismo_M_", "");
            ei.category = "seismic_mass";
            ei.floor = floor;
            ei.building = building;
            ei.coordCenter = cm;
            ei.baseColor = rnd.sharedMaterial.color;
            ei.isSeismic = true;
            Register(go, "seismic_mass", floor);
            allElements.Add(ei);
        }

        struct Label2D { public float x; public float y; public float z; public string text; public Color color; public Label2D(float x, float y, float z, string t, Color c) { this.x = x; this.y = y; this.z = z; this.text = t; this.color = c; } }
        private readonly List<Label2D> _shearLabels = new List<Label2D>();

        void CreateArrow(string name, Vector3 origin, Vector3 dir, float forceKN, float maxForce, Color color, string cat, string floor, string building, string caseName)
        {
            float length = Mathf.Clamp(forceKN / maxForce * 12f, 0.3f, 12f);
            Vector3 p0 = origin;
            Vector3 p1 = origin + dir * length;
            var go = new GameObject(name);
            var lr = go.AddComponent<LineRenderer>();
            lr.useWorldSpace = false;
            lr.positionCount = 4;
            lr.SetPosition(0, p0);
            lr.SetPosition(1, p1);
            float shaft = length * 0.35f;
            Vector3 perp = new Vector3(-dir.y, dir.x, 0f).normalized * length * 0.12f;
            lr.SetPosition(2, p1 - dir * shaft + perp);
            lr.SetPosition(3, p1 - dir * shaft - perp);
            lr.startWidth = 0.18f; lr.endWidth = 0.18f;
            lr.material = SeismicLineMat(color);
            var ei = go.AddComponent<ElementInfo>();
            ei.go = go;
            ei.id = name;
            ei.humanId = "F_" + caseName + " " + building + " " + floor;
            ei.category = cat;
            ei.floor = floor;
            ei.building = building;
            ei.baseColor = color;
            ei.coordCenter = (p0 + p1) * 0.5f;
            ei.nodeI = p0;
            ei.nodeJ = p1;
            ei.isSeismic = true;
            ei.seismicForceKN = forceKN;
            ei.seismicCase = caseName;
            Register(go, cat, floor);
            allElements.Add(ei);
        }

        void CreateCmMarker(string name, Vector3 cm, SeismicFloor f)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = name;
            go.transform.position = cm + new Vector3(0f, 0f, 0.35f);
            go.transform.localScale = Vector3.one * 0.5f;
            var rnd = go.GetComponent<Renderer>();
            rnd.sharedMaterial = SeismicLineMat(new Color(1f, 0.9f, 0.2f));
            var ei = go.AddComponent<ElementInfo>();
            ei.go = go;
            ei.id = name;
            ei.humanId = "CM " + f.building + " " + f.floor;
            ei.category = "seismic_cm";
            ei.floor = f.floor;
            ei.building = f.building;
            ei.coordCenter = cm;
            ei.nodeI = cm;
            ei.nodeJ = cm;
            ei.isSeismic = true;
            ei.seismicForceKN = f.F_EX_kN;
            ei.baseColor = rnd.sharedMaterial.color;
            Register(go, "seismic_cm", f.floor);
            allElements.Add(ei);
        }

        static Material SeismicLineMat(Color color)
        {
            var sh = Shader.Find("Sprites/Default");
            if (sh == null) sh = Shader.Find("Legacy Shaders/Particles/Alpha Blended");
            if (sh == null) sh = Shader.Find("Unlit/Color");
            if (sh == null) sh = Shader.Find("Standard");
            var mat = new Material(sh);
            if (mat != null) mat.color = color;
            return mat;
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
            Register(go, cat, floor);
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
            if (!typeVisible.ContainsKey(type)) typeVisible[type] = DefaultTypeVisibility(type);
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
            if (Input.GetKeyDown(KeyCode.H)) uiHidden = !uiHidden;
            if (Input.GetKeyDown(KeyCode.R)) ResetPresentation();
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
            if (uiHidden) return false;
            if (expandedGraph != null) return true;
            Vector2 m = Input.mousePosition;
            m.y = Screen.height - m.y;
            // Zona panel derecho (navegacion + buscar, arriba)
            if (m.x > Screen.width - 370 && m.y < 215) return true;
            // Zona panel izquierdo (pisos y tipos)
            if (ControlsRect().Contains(m)) return true;
            // Zona panel de info (arriba izquierda)
            if (lastSelected != null && InspectorRect().Contains(m)) return true;
            if (deliveryPanelVisible && DeliveryRect().Contains(m)) return true;
            if (!deliveryPanelVisible && new Rect(Screen.width * 0.5f - 90f, 10f, 180f, 28f).Contains(m)) return true;
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
                        else if (ei.isSeismic)
                        {
                            // material propio por marcador/flecha sismica: restaurar su color base
                            if (rnd.sharedMaterial != null)
                            {
                                rnd.sharedMaterial.color = ei.baseColor;
                                rnd.sharedMaterial.DisableKeyword("_EMISSION");
                                rnd.sharedMaterial.SetColor("_EmissionColor", Color.black);
                            }
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
            else if (ei.isSeismic && ei.category == "seismic_cm")
            {
                var sf = FindSeismicFloor(ei.building, ei.floor);
                if (sf != null)
                {
                    cargaLine = $"Masa sismica: {sf.mass_ton.ToString("F3")} ton\n" +
                        $"W sismico: {sf.w_seismic_kN.ToString("F3")} kN\n" +
                        $"F_EX: {sf.F_EX_kN.ToString("F3")} kN   F_EY: {sf.F_EY_kN.ToString("F3")} kN\n" +
                        $"Corte EX: {sf.story_shear_EX_kN.ToString("F3")} kN   Corte EY: {sf.story_shear_EY_kN.ToString("F3")} kN\n" +
                        $"Torsion EX: {sf.M_torsion_EX_kNm.ToString("F3")} kNm   Torsion EY: {sf.M_torsion_EY_kNm.ToString("F3")} kNm";
                }
            }
            else if (ei.isSeismic)
            {
                cargaLine = $"Fuerza sismica {ei.seismicCase}: {ei.seismicForceKN.ToString("F3")} kN";
            }
            else if (ei.tribFromTag)
            {
                cargaLine = $"Carga tributaria que soporta: {ei.tribLoadKN.ToString("F3")} kN\n" +
                    $"Area tributaria asociada: {ei.tribAreaM2.ToString("F3")} m2";
            }
            string analysisLine = "\nModelo FE: sin correspondencia";
            if (analysisByElementId.TryGetValue(id, out var ar))
            {
                var f = ar.localForce_end1;
                string forces = f != null && f.Count >= 6
                    ? $"P={f[0] / 1000.0:F3} kN, Vy={f[1] / 1000.0:F3} kN, Vz={f[2] / 1000.0:F3} kN, T={f[3] / 1000.0:F3} kNm, My={f[4] / 1000.0:F3} kNm, Mz={f[5] / 1000.0:F3} kNm"
                    : "fuerzas no disponibles";
                analysisLine = $"\nModelo FE: incluido\nCaso: {ar.case_name}\nanalysis_id: {ar.analysis_id}\nOpenSees tag: {ar.opensees_tag}\nExtremo i: {forces}";
            }
            else if (excludedByElementId.TryGetValue(id, out var excluded))
            {
                analysisLine = $"\nModelo FE: no incluido\nMotivo: {excluded.reason}";
            }
            string capacityLine = "";
            if (capacity != null && !string.IsNullOrEmpty(capacity.mapped_element_id) && capacity.mapped_element_id == id)
            {
                capacityLine = $"\nCapacidad HA (laboratorio): {capacity.b_m:F2} x {capacity.h_m:F2} m, {capacity.num_bars} barras, f'c={capacity.fc_pa / 1e6:F1} MPa, fy={capacity.fy_pa / 1e6:F1} MPa";
            }
            inspectorIdentity = $"{id}\n{cat} | Piso {ei.floor} | {(string.IsNullOrEmpty(ei.building) ? "Sin edificio" : ei.building)}\nEjes: {ejes}";
            inspectorGeometry = $"Coordenadas: {coord}\nNodo i: {P(ei.nodeI)}\nNodo j: {P(ei.nodeJ)}\nLongitud: {ei.lengthM:F3} m";
            inspectorProperties = $"Seccion: {section}\nMaterial: {ei.materialName}\nelementTag: {ei.elementTag ?? "-"}";
            inspectorTributary = string.IsNullOrEmpty(cargaLine) ? "Sin carga tributaria asociada." : cargaLine;
            inspectorAnalysis = analysisLine.TrimStart('\n');
            inspectorCapacity = string.IsNullOrEmpty(capacityLine) ? "Este elemento no tiene un analisis de capacidad asociado." : capacityLine.TrimStart('\n');
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
                (string.IsNullOrEmpty(cargaLine) ? "" : "\n" + cargaLine) +
                analysisLine + capacityLine;
            if (infoText != null) infoText.text = lastInfo;
            lastSelected = ei;
            inspectorVisible = true;
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
            if (uiHidden)
            {
                var hint = new GUIStyle(GUI.skin.label);
                hint.fontSize = 11; hint.normal.textColor = new Color(1f, 1f, 1f, 0.65f);
                GUI.Label(new Rect(10, 8, 190, 20), "H: mostrar interfaz", hint);
                return;
            }
            DrawPanelInfo();
            DrawControls();
            DrawP1L3Panel();
            if (labelsVisible) DrawLabels();
            if (seismic != null) DrawSeismicValueLabels();
            DrawExpandedGraph();
        }

        Rect DeliveryRect()
        {
            float width = Mathf.Clamp(Screen.width - 540f, 520f, 920f);
            float x = Mathf.Max(270f, (Screen.width - width) * 0.5f);
            float height = Mathf.Min(390f, Screen.height - 180f);
            return new Rect(x, Screen.height - height - 10f, width, height);
        }

        void DrawP1L3Panel()
        {
            var title = new GUIStyle(GUI.skin.label);
            title.fontSize = 14; title.fontStyle = FontStyle.Bold; title.normal.textColor = Color.white;
            var text = new GUIStyle(GUI.skin.label);
            text.fontSize = 12; text.normal.textColor = new Color(0.92f, 0.95f, 1f); text.wordWrap = true;
            var pass = new GUIStyle(title); pass.normal.textColor = new Color(0.35f, 1f, 0.55f);
            var warning = new GUIStyle(text); warning.normal.textColor = new Color(1f, 0.78f, 0.25f);
            var button = new GUIStyle(GUI.skin.button); button.fontSize = 12;

            if (!deliveryPanelVisible)
            {
                if (GUI.Button(new Rect(Screen.width * 0.5f - 90f, 10f, 180f, 28f), "Abrir panel P1L3", button)) deliveryPanelVisible = true;
                return;
            }

            Rect r = DeliveryRect();
            GUI.Box(r, "");
            GUI.DrawTexture(r, MakeTex(2, 2, new Color(0.015f, 0.025f, 0.055f, 0.94f)));
            GUI.Label(new Rect(r.x + 12, r.y + 7, 360, 24), "P1L3 | Laboratorio estructural integrado", title);
            if (delivery != null) GUI.Label(new Rect(r.x + r.width - 170, r.y + 7, 110, 22), "Estado: " + delivery.status, delivery.status == "PASS" ? pass : warning);
            if (GUI.Button(new Rect(r.x + r.width - 42, r.y + 5, 30, 24), "X", button)) { deliveryPanelVisible = false; return; }

            float tabY = r.y + 34;
            string[] tabs = { "Resumen", "Casos FE", "Capacidad HA" };
            for (int i = 0; i < tabs.Length; i++)
                if (GUI.Button(new Rect(r.x + 12 + i * 118, tabY, 110, 25), tabs[i], button)) deliveryTab = i;

            Rect body = new Rect(r.x + 12, tabY + 32, r.width - 24, r.height - 76);
            if (delivery == null)
            {
                GUI.Label(body, "No se encontro p1l3_delivery.json. Regenera el bundle de Unity.", warning);
                return;
            }
            if (deliveryTab == 0) DrawDeliverySummary(body, text, pass, warning);
            else if (deliveryTab == 1) DrawAnalysisCases(body, text, pass, warning, button);
            else DrawCapacity(body, text, pass, warning);
        }

        void DrawDeliverySummary(Rect body, GUIStyle text, GUIStyle pass, GUIStyle warning)
        {
            var g = delivery.gravity;
            var s = delivery.seismic;
            var p = delivery.superposition;
            if (g == null || s == null || p == null) { GUI.Label(body, "Resumen P1L3 incompleto.", warning); return; }
            string summary =
                $"PARTE A - CARGA VIVA [{g.status}]\n" +
                $"110 zonas/panos tributarios; Q transferida = {g.Q_transferred_kN:F3} kN; qQ*A = {g.Q_expected_kN:F3} kN; error = {g.Q_conservation_rel_error:E2}.\n\n" +
                $"PARTE B - SISMO PSEUDOESTATICO [{s.status}]\n" +
                $"Coeficiente basal configurable C = {100.0 * s.base_shear_coefficient:F1}% g. EX = {s.total_EX_kN:F3} kN, EY = {s.total_EY_kN:F3} kN. " +
                $"Errores de corte basal: EX {s.EX_rel_error:E2}, EY {s.EY_rel_error:E2}. Sentido deformada: EX {s.EX_deformed_status}, EY {s.EY_deformed_status}. " +
                $"Error maximo al aplicar en CM+excentricidad = {s.max_application_point_error_m:E2} m.\n\n" +
                $"PARTE C - SUPERPOSICION [{p.status}]\n" +
                $"R = {p.lambda_G:F2} G + {p.lambda_Q:F2} Q + {p.lambda_EX:F2} EX + {p.lambda_EY:F2} EY. " +
                $"Comparacion con corrida explicita: desplazamiento {p.displacement_rel_error:E2}, reaccion {p.reaction_rel_error:E2}, fuerza interna {p.internal_force_rel_error:E2}.\n\n" +
                "PARTE D - CAPACIDAD HA\nFiber Section, materiales, armadura, M-phi y P-M disponibles en la pestana Capacidad HA.";
            GUI.Label(body, summary, text);
            float wy = body.y + body.height - 48;
            GUI.Label(new Rect(body.x, wy, body.width, 46),
                "MODELO PROVISIONAL: la geometria/carga tributaria aun es parcial y las deformaciones globales no deben interpretarse como una validacion final del edificio.", warning);
        }

        DeliveryCase FindDeliveryCase(string name)
        {
            if (delivery == null || delivery.cases == null) return null;
            foreach (var item in delivery.cases)
                if (item != null && (item.case_name ?? "").Replace("CASE_", "").ToUpperInvariant() == name.ToUpperInvariant()) return item;
            return null;
        }

        void DrawAnalysisCases(Rect body, GUIStyle text, GUIStyle pass, GUIStyle warning, GUIStyle button)
        {
            GUI.Label(new Rect(body.x, body.y, body.width, 22), "Selecciona el caso para consultar las fuerzas locales de cualquier elemento:", text);
            string[] names = { "G", "Q", "EX", "EY", "R" };
            for (int i = 0; i < names.Length; i++)
            {
                var bs = new GUIStyle(button);
                if (activeAnalysisCase == names[i]) bs.normal.textColor = new Color(0.25f, 1f, 0.5f);
                if (GUI.Button(new Rect(body.x + i * 64, body.y + 28, 58, 26), names[i], bs)) ActivateAnalysisCase(names[i]);
            }
            var c = FindDeliveryCase(activeAnalysisCase);
            if (c == null) { GUI.Label(new Rect(body.x, body.y + 64, body.width, 50), "Caso no disponible.", warning); return; }
            string description =
                $"CASO ACTIVO: {activeAnalysisCase}\n" +
                $"Desplazamiento maximo = {c.max_displacement_m:F6} m en nodo {c.max_node_tag} ({c.max_floor}); " +
                $"u = ({c.ux_m:F6}, {c.uy_m:F6}, {c.uz_m:F6}) m.\n" +
                $"Suma de reacciones = ({c.sum_Rx_kN:F3}, {c.sum_Ry_kN:F3}, {c.sum_Rz_kN:F3}) kN.\n\n" +
                "Haz clic en una viga o columna para ver P, Vy, Vz, T, My y Mz del caso activo. " +
                "El caso R se resolvio explicitamente y tambien se comparo contra la suma lineal de G, Q, EX y EY.";
            GUI.Label(new Rect(body.x, body.y + 66, body.width, 130), description, text);
            if (activeAnalysisCase == "R" && delivery.superposition != null)
                GUI.Label(new Rect(body.x, body.y + 202, body.width, 44),
                    $"Verificacion de superposicion: {delivery.superposition.status} | errores u={delivery.superposition.displacement_rel_error:E2}, R={delivery.superposition.reaction_rel_error:E2}, f={delivery.superposition.internal_force_rel_error:E2}", pass);
            GUI.Label(new Rect(body.x, body.y + body.height - 44, body.width, 42),
                "Advertencia: los valores son resultados del modelo FE integrado actual; la rigidez global sigue en auditoria por geometria, conectividad y ejes locales.", warning);
        }

        void DrawCapacity(Rect body, GUIStyle text, GUIStyle pass, GUIStyle warning)
        {
            if (capacity == null) { GUI.Label(body, "Datos de capacidad HA no disponibles.", warning); return; }
            string header =
                $"Seccion {capacity.section_id}: {capacity.b_m:F2} x {capacity.h_m:F2} m | recubrimiento {capacity.cover_m:F3} m | " +
                $"{capacity.num_bars} barras O{capacity.bar_diameter_m * 1000.0:F0} mm | f'c={capacity.fc_pa / 1e6:F1} MPa | fy={capacity.fy_pa / 1e6:F1} MPa | " +
                $"malla {capacity.num_fibers_y}x{capacity.num_fibers_z}.\nMapeo visible: {capacity.mapped_element_id} -> {capacity.mapped_analysis_id} ({capacity.mapping_distance_m:F3} m).";
            GUI.Label(new Rect(body.x, body.y, body.width, 48), header, text);
            float gap = 8f;
            float imageW = (body.width - gap * 2f) / 3f;
            float imageY = body.y + 54;
            float imageH = Mathf.Min(178f, body.height - 108f);
            Texture2D[] images = { fiberTexture, momentCurvatureTexture, pmInteractionTexture };
            string[] labels = { "Discretizacion y refuerzo", "Momento-curvatura M-phi", "Interaccion P-M" };
            for (int i = 0; i < 3; i++)
            {
                Rect ir = new Rect(body.x + i * (imageW + gap), imageY, imageW, imageH);
                GUI.Box(ir, "");
                if (images[i] != null) GUI.DrawTexture(ir, images[i], ScaleMode.ScaleToFit, true);
                else GUI.Label(ir, "Imagen no disponible", warning);
                GUI.Label(new Rect(ir.x, ir.y + ir.height + 2, ir.width, 20), labels[i], pass);
                if (images[i] != null && GUI.Button(new Rect(ir.x + ir.width - 72, ir.y + 4, 68, 22), "Ampliar"))
                {
                    expandedGraph = images[i];
                    expandedGraphTitle = labels[i];
                }
            }
            GUI.Label(new Rect(body.x, body.y + body.height - 28, body.width, 26), capacity.disclaimer, warning);
        }

        void DrawExpandedGraph()
        {
            if (expandedGraph == null) return;
            GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), MakeTex(2, 2, new Color(0f, 0f, 0f, 0.92f)));
            float width = Mathf.Min(Screen.width - 60f, 1100f);
            float height = Mathf.Min(Screen.height - 90f, 760f);
            Rect frame = new Rect((Screen.width - width) * 0.5f, (Screen.height - height) * 0.5f, width, height);
            GUI.Box(frame, "");
            var title = new GUIStyle(GUI.skin.label);
            title.fontSize = 17; title.fontStyle = FontStyle.Bold; title.normal.textColor = Color.white;
            GUI.Label(new Rect(frame.x + 14, frame.y + 8, frame.width - 110, 26), expandedGraphTitle, title);
            if (GUI.Button(new Rect(frame.x + frame.width - 90, frame.y + 8, 76, 26), "Cerrar"))
            {
                expandedGraph = null;
                expandedGraphTitle = "";
                return;
            }
            GUI.DrawTexture(new Rect(frame.x + 14, frame.y + 42, frame.width - 28, frame.height - 56), expandedGraph, ScaleMode.ScaleToFit, true);
        }

        void DrawPanelInfo()
        {
            if (lastSelected == null) return;
            Rect r = InspectorRect();
            if (!inspectorVisible)
            {
                if (GUI.Button(new Rect(r.x + r.width - 160, r.y, 160, 26), "Abrir inspector")) inspectorVisible = true;
                return;
            }
            GUI.Box(r, "");
            GUI.DrawTexture(r, MakeTex(2, 2, new Color(0.015f, 0.025f, 0.05f, 0.94f)));
            var title = new GUIStyle(GUI.skin.label);
            title.fontSize = 14; title.fontStyle = FontStyle.Bold; title.normal.textColor = Color.white;
            var lbl = new GUIStyle(GUI.skin.label);
            lbl.fontSize = 12; lbl.normal.textColor = new Color(0.93f, 0.95f, 1f); lbl.wordWrap = true;
            GUI.Label(new Rect(r.x + 10, r.y + 7, r.width - 90, 22), "Elemento seleccionado", title);
            if (GUI.Button(new Rect(r.x + r.width - 38, r.y + 5, 28, 24), "X")) { inspectorVisible = false; return; }
            GUI.Label(new Rect(r.x + 10, r.y + 34, r.width - 20, 58), inspectorIdentity, lbl);
            string toCopy = string.IsNullOrEmpty(lastSelected.humanId) ? lastSelected.id : lastSelected.humanId;
            if (GUI.Button(new Rect(r.x + 10, r.y + 94, r.width - 20, 24), "Copiar ID: " + toCopy))
                GUIUtility.systemCopyBuffer = toCopy;

            float contentHeight = 420f;
            infoScroll = GUI.BeginScrollView(new Rect(r.x + 8, r.y + 124, r.width - 16, r.height - 132), infoScroll, new Rect(0, 0, r.width - 40, contentHeight));
            float sy = 2f;
            DrawInspectorSection(ref sy, "Geometria", ref inspectorGeometryOpen, inspectorGeometry, r.width - 42, lbl);
            DrawInspectorSection(ref sy, "Propiedades", ref inspectorPropertiesOpen, inspectorProperties, r.width - 42, lbl);
            DrawInspectorSection(ref sy, "Tributarias / cargas", ref inspectorTributaryOpen, inspectorTributary, r.width - 42, lbl);
            DrawInspectorSection(ref sy, "Modelo FE / resultados " + activeAnalysisCase, ref inspectorAnalysisOpen, inspectorAnalysis, r.width - 42, lbl);
            DrawInspectorSection(ref sy, "Capacidad HA", ref inspectorCapacityOpen, inspectorCapacity, r.width - 42, lbl);
            GUI.EndScrollView();
        }

        Rect InspectorRect()
        {
            float height = Mathf.Clamp(Screen.height - 220f, 300f, 540f);
            return new Rect(Screen.width - 370f, 210f, 360f, height);
        }

        void DrawInspectorSection(ref float y, string heading, ref bool open, string content, float width, GUIStyle label)
        {
            string marker = open ? "▼ " : "▶ ";
            if (GUI.Button(new Rect(0, y, width, 24), marker + heading)) open = !open;
            y += 27f;
            if (!open) return;
            int lines = Mathf.Max(1, (content ?? "").Split('\n').Length);
            float h = Mathf.Max(38f, lines * 18f + 8f);
            GUI.Label(new Rect(8, y, width - 12, h), content, label);
            y += h + 5f;
        }

        void DrawControls()
        {
            float x = Screen.width - 260;
            float y = 10;

            // --- Botones de vista ---
            var btn = new GUIStyle(GUI.skin.button);
            btn.fontSize = 11;
            GUI.Box(new Rect(x, y, 250, 108), "");
            GUI.DrawTexture(new Rect(x, y, 250, 108), MakeTex(2, 2, new Color(0.02f, 0.04f, 0.08f, 0.9f)));
            var ttl = new GUIStyle(GUI.skin.label);
            ttl.fontSize = 12; ttl.fontStyle = FontStyle.Bold; ttl.normal.textColor = Color.white;
            GUI.Label(new Rect(x + 8, y + 4, 240, 18), "Navegacion", ttl);
            var t1 = new GUIStyle(btn); var t2 = new GUIStyle(btn); var t3 = new GUIStyle(btn); var t4 = new GUIStyle(btn); var t5 = new GUIStyle(btn);
            if (GUI.Button(new Rect(x + 8, y + 24, 54, 24), "Lado A", t1)) SideView("A");
            if (GUI.Button(new Rect(x + 66, y + 24, 54, 24), "Lado B", t2)) SideView("B");
            if (GUI.Button(new Rect(x + 124, y + 24, 54, 24), "Lado C", t3)) SideView("C");
            if (GUI.Button(new Rect(x + 182, y + 24, 58, 24), "Lado D", t4)) SideView("D");
            if (GUI.Button(new Rect(x + 8, y + 52, 112, 24), "Vista planta", t5)) TopView();
            if (GUI.Button(new Rect(x + 124, y + 52, 116, 24), labelsVisible ? "IDs: ON" : "IDs: OFF", t1)) labelsVisible = !labelsVisible;
            if (GUI.Button(new Rect(x + 8, y + 80, 112, 22), "Reset vista (R)", t5)) ResetPresentation();
            if (GUI.Button(new Rect(x + 124, y + 80, 116, 22), "Modo limpio (H)", t1)) uiHidden = true;

            // --- Busqueda por ID ---
            GUI.Box(new Rect(x, y + 114, 250, 82), "");
            GUI.DrawTexture(new Rect(x, y + 114, 250, 82), MakeTex(2, 2, new Color(0.02f, 0.04f, 0.08f, 0.9f)));
            GUI.Label(new Rect(x + 8, y + 118, 240, 18), "Buscar por ID (ej. E1-P2-C-034)", ttl);
            searchText = GUI.TextField(new Rect(x + 8, y + 140, 160, 24), searchText, 40);
            if (GUI.Button(new Rect(x + 172, y + 140, 68, 24), "Buscar", t2)) DoSearch();
            if (!string.IsNullOrEmpty(searchResult)) GUI.Label(new Rect(x + 8, y + 168, 240, 18), searchResult, ttl);

            // --- Panel izquierdo: controles visibles + lista desplazable ---
            Rect controls = ControlsRect();
            float lx = controls.x;
            float ly = controls.y;
            GUI.Box(controls, "");
            GUI.DrawTexture(controls, MakeTex(2, 2, new Color(0.02f, 0.04f, 0.08f, 0.92f)));
            var sect = new GUIStyle(GUI.skin.label);
            sect.fontSize = 12; sect.fontStyle = FontStyle.Bold; sect.normal.textColor = Color.white;

            GUI.Label(new Rect(lx + 8, ly + 4, 240, 18), "Visibilidad rapida", sect);
            bool newLabels = GUI.Toggle(new Rect(lx + 8, ly + 25, 116, 20), labelsVisible, "Textos / IDs");
            if (newLabels != labelsVisible) labelsVisible = newLabels;
            QuickTypeToggle(new Rect(lx + 128, ly + 25, 116, 20), "Tributarias", "tributary", "tributary_point");
            QuickTypeToggle(new Rect(lx + 8, ly + 47, 116, 20), "Flechas EX/EY", "seismic_arrow");
            QuickTypeToggle(new Rect(lx + 128, ly + 47, 116, 20), "Deformada", "seismic_deform");
            QuickTypeToggle(new Rect(lx + 8, ly + 69, 116, 20), "Centros masa", "seismic_cm");
            QuickTypeToggle(new Rect(lx + 128, ly + 69, 116, 20), "Masa / peso", "seismic_mass");
            QuickTypeToggle(new Rect(lx + 8, ly + 91, 116, 20), "Corte basal", "seismic_shear");
            QuickTypeToggle(new Rect(lx + 128, ly + 91, 116, 20), "Torsion", "seismic_torsion");

            GUI.Label(new Rect(lx + 8, ly + 118, 240, 18), "Pisos (S = mostrar solo)", sect);
            var floors = SortedFloors();
            float floorX = lx + 8;
            float floorY = ly + 139;
            for (int i = 0; i < floors.Count; i++)
            {
                string f = floors[i];
                bool vis = floorVisible.ContainsKey(f) && floorVisible[f];
                float cellX = floorX + (i % 3) * 78;
                float cellY = floorY + (i / 3) * 22;
                bool novo = GUI.Toggle(new Rect(cellX, cellY, 48, 20), vis, f);
                if (novo != vis) { floorVisible[f] = novo; ReapplyAll(); }
                if (GUI.Button(new Rect(cellX + 49, cellY, 25, 19), "S"))
                {
                    foreach (var key in new List<string>(floorVisible.Keys)) floorVisible[key] = key == f;
                    ReapplyAll();
                }
            }
            float floorRows = Mathf.Ceil(floors.Count / 3f);
            float buttonsY = floorY + floorRows * 22f + 2f;
            if (GUI.Button(new Rect(lx + 8, buttonsY, 112, 22), "Todos los pisos", btn))
            {
                foreach (var k in new List<string>(floorVisible.Keys)) floorVisible[k] = true;
                ReapplyAll();
            }
            if (GUI.Button(new Rect(lx + 128, buttonsY, 112, 22), "Apagar pisos", btn))
            {
                foreach (var k in new List<string>(floorVisible.Keys)) floorVisible[k] = false;
                ReapplyAll();
            }

            float listY = buttonsY + 30f;
            GUI.Label(new Rect(lx + 8, listY, 220, 18), "Todas las capas (desplazar)", sect);
            float viewportY = listY + 20f;
            float viewportH = Mathf.Max(80f, controls.yMax - viewportY - 8f);
            var keys = new List<string>();
            foreach (var key in byType.Keys) if (TypeLabels.ContainsKey(key)) keys.Add(key);
            keys.Sort((a, b) => string.Compare(TypeLabels[a], TypeLabels[b], System.StringComparison.Ordinal));
            float contentH = Mathf.Max(viewportH - 2f, keys.Count * 22f + 4f);
            controlsScroll = GUI.BeginScrollView(new Rect(lx + 6, viewportY, 238, viewportH), controlsScroll, new Rect(0, 0, 214, contentH));
            float ty = 2f;
            foreach (var key in keys)
            {
                bool vis = typeVisible.ContainsKey(key) && typeVisible[key];
                bool novo = GUI.Toggle(new Rect(2, ty, 208, 20), vis, TypeLabels[key]);
                if (novo != vis) { typeVisible[key] = novo; ReapplyAll(); }
                ty += 22;
            }
            GUI.EndScrollView();
        }

        Rect ControlsRect()
        {
            float height = Mathf.Clamp(Screen.height - 235f, 360f, 650f);
            return new Rect(10f, 225f, 250f, height);
        }

        bool DefaultTypeVisibility(string type)
        {
            switch (type)
            {
                case "beam":
                case "column":
                case "column_plan":
                case "wall":
                case "support":
                case "slab":
                case "slab_edge":
                    return true;
                default:
                    return false;
            }
        }

        void ResetPresentation()
        {
            yaw = 30f;
            pitch = 25f;
            orbitDist = 160f;
            orbitTarget = new Vector3(16.41f, 5.99f, -14.73f);
            labelsVisible = false;
            deliveryPanelVisible = false;
            expandedGraph = null;
            expandedGraphTitle = "";
            foreach (var key in new List<string>(floorVisible.Keys)) floorVisible[key] = true;
            foreach (var key in new List<string>(typeVisible.Keys)) typeVisible[key] = DefaultTypeVisibility(key);
            ReapplyAll();
            RestoreHighlight();
            lastInfo = "";
            lastSelected = null;
            searchResult = "Vista y visibilidad restablecidas";
        }

        void RunVisibilitySelfCheck()
        {
            string[] requiredTypes = {
                "beam", "column", "wall", "slab", "support", "tributary",
                "seismic_arrow", "seismic_cm", "seismic_mass", "seismic_shear",
                "seismic_torsion", "seismic_deform"
            };
            var failures = new List<string>();
            foreach (var key in requiredTypes)
            {
                if (!byType.ContainsKey(key) || byType[key].Count == 0) { failures.Add(key + ":sin objetos"); continue; }
                typeVisible[key] = false;
                ReapplyAll();
                foreach (var go in byType[key]) if (go.activeSelf) { failures.Add(key + ":OFF fallo"); break; }
                typeVisible[key] = true;
                ReapplyAll();
                bool anyActive = false;
                foreach (var go in byType[key]) if (go.activeSelf) { anyActive = true; break; }
                if (!anyActive) failures.Add(key + ":ON fallo");
            }
            foreach (var floor in new[] { "S1", "P1", "P2", "P3", "P4" })
            {
                if (!byFloor.ContainsKey(floor) || byFloor[floor].Count == 0) { failures.Add(floor + ":sin objetos"); continue; }
                floorVisible[floor] = false;
                ReapplyAll();
                foreach (var go in byFloor[floor]) if (go.activeSelf) { failures.Add(floor + ":OFF fallo"); break; }
                floorVisible[floor] = true;
            }
            if (failures.Count == 0) Debug.Log("[UI QA] PASS: capas y pisos responden a ON/OFF.");
            else Debug.LogError("[UI QA] FAIL: " + string.Join(", ", failures));
        }

        void QuickTypeToggle(Rect rect, string label, params string[] keys)
        {
            bool visible = true;
            foreach (var key in keys)
                visible = visible && typeVisible.ContainsKey(key) && typeVisible[key];
            bool changed = GUI.Toggle(rect, visible, label);
            if (changed == visible) return;
            foreach (var key in keys)
                if (typeVisible.ContainsKey(key)) typeVisible[key] = changed;
            ReapplyAll();
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

        void DrawSeismicValueLabels()
        {
            if (cam == null || seismic == null || seismic.floors == null) return;
            bool cmVisible = typeVisible.ContainsKey("seismic_cm") ? typeVisible["seismic_cm"] : true;
            bool shearVisible = typeVisible.ContainsKey("seismic_shear") ? typeVisible["seismic_shear"] : true;
            bool arrowVisible = typeVisible.ContainsKey("seismic_arrow") ? typeVisible["seismic_arrow"] : true;
            bool massVisible = typeVisible.ContainsKey("seismic_mass") ? typeVisible["seismic_mass"] : true;
            bool torVisible = typeVisible.ContainsKey("seismic_torsion") ? typeVisible["seismic_torsion"] : true;
            bool anyFloor = cmVisible || massVisible || arrowVisible || torVisible;
            const int boxW = 240;
            GUIStyle ls = new GUIStyle(GUI.skin.label);
            ls.fontSize = 12;
            var sw = Screen.width; var sh = Screen.height;
            var drawn = new HashSet<string>();
            var occupied = new List<Rect>();
            int step = 0;
            if (anyFloor)
            foreach (var f in seismic.floors)
            {
                if (floorVisible.ContainsKey(f.floor) && !floorVisible[f.floor]) continue;
                string key = f.building + "_" + f.floor;
                if (drawn.Contains(key)) continue;
                drawn.Add(key);
                Vector3 cp = transform.TransformPoint(new Vector3((float)f.cm_x + 1.2f, (float)f.cm_y, (float)f.z_m));
                Vector3 sp = cam.WorldToScreenPoint(cp);
                if (sp.z <= 0) continue;
                sp.y = sh - sp.y;
                if (sp.x < 0 || sp.x > sw || sp.y < 0 || sp.y > sh) continue;

                int lines = 0;
                if (massVisible) lines++;
                if (massVisible) lines++; // + linea de peso total
                if (cmVisible) lines++;
                if (arrowVisible) lines += 2;
                if (torVisible) lines++;
                int lineH = 17;
                int pad = 5;
                int boxH = lines * lineH + pad * 2;

                // Lado alterno para que pisos cercanos no se tapen entre si
                bool right = (step % 2 == 0);
                float bx = right ? sp.x + 6 : sp.x - boxW - 6;
                // El intervalo que cubre cada caja (para deteccion de solape vertical)
                float boxTop = sp.y - boxH;
                float boxBot = sp.y;
                if (bx < 0) bx = 0; else if (bx + boxW > sw) bx = sw - boxW;

                Rect placed = PlaceLabelRect(new Rect(bx, boxTop, boxW, boxH), occupied, sw, sh);
                bx = placed.x;
                boxTop = placed.y;
                float labelBase = placed.yMax;
                occupied.Add(placed);

                GUI.DrawTexture(new Rect(bx, boxTop, boxW, boxH), MakeTex(2, 2, new Color(0f, 0f, 0f, 0.75f)));

                int line = -boxH + pad;
                if (massVisible)
                {
                    double totalW = TotalWeight(f.building);
                    ls.fontSize = 13; ls.fontStyle = FontStyle.Bold;
                    ls.normal.textColor = new Color(1f, 0.75f, 0.15f);
                    GUI.Label(new Rect(bx + 6, labelBase + line, boxW - 12, lineH), "MASA PISO " + f.floor + " = " + f.mass_ton.ToString("F1") + " t", ls);
                    line += lineH;
                    ls.fontSize = 12; ls.fontStyle = FontStyle.Normal;
                    ls.normal.textColor = new Color(1f, 0.9f, 0.5f);
                    GUI.Label(new Rect(bx + 6, labelBase + line, boxW - 12, lineH), "PESO TOTAL = " + totalW.ToString("F1") + " kN", ls);
                    line += lineH;
                }
                ls.fontSize = 12; ls.fontStyle = FontStyle.Normal;
                if (cmVisible)
                {
                    ls.normal.textColor = new Color(0.9f, 0.9f, 0.9f);
                    GUI.Label(new Rect(bx + 6, labelBase + line, boxW - 12, lineH), "CM(" + f.cm_x.ToString("F2") + "," + f.cm_y.ToString("F2") + ")  A=" + f.area_m2.ToString("F1") + " m2", ls);
                    line += lineH;
                }
                if (arrowVisible)
                {
                    ls.normal.textColor = new Color(1f, 0.5f, 0.5f);
                    GUI.Label(new Rect(bx + 6, labelBase + line, boxW - 12, lineH), "EX F=" + f.F_EX_kN.ToString("F0") + " kN", ls);
                    line += lineH;
                    ls.normal.textColor = new Color(0.5f, 0.6f, 1f);
                    GUI.Label(new Rect(bx + 6, labelBase + line, boxW - 12, lineH), "EY F=" + f.F_EY_kN.ToString("F0") + " kN", ls);
                    line += lineH;
                }
                if (torVisible)
                {
                    ls.normal.textColor = new Color(1f, 0.55f, 0.85f);
                    GUI.Label(new Rect(bx + 6, labelBase + line, boxW - 12, lineH), "Torsion EX=" + f.M_torsion_EX_kNm.ToString("F0") + "  EY=" + f.M_torsion_EY_kNm.ToString("F0") + " kNm", ls);
                }
                step++;
            }
            if (shearVisible)
            foreach (var lb in _shearLabels)
            {
                Vector3 cp = transform.TransformPoint(new Vector3(lb.x, lb.y, lb.z));
                Vector3 sp = cam.WorldToScreenPoint(cp);
                if (sp.z <= 0) continue;
                sp.y = sh - sp.y;
                if (sp.x < 0 || sp.x > sw || sp.y < 0 || sp.y > sh) continue;
                ls.normal.textColor = lb.color;
                ls.fontSize = 14; ls.fontStyle = FontStyle.Bold;
                GUI.Label(new Rect(sp.x - 80, sp.y + 30, 240, 18), lb.text, ls);
                ls.fontSize = 12; ls.fontStyle = FontStyle.Normal;
            }
        }

        Rect PlaceLabelRect(Rect candidate, List<Rect> occupied, float screenWidth, float screenHeight)
        {
            candidate.x = Mathf.Clamp(candidate.x, 2f, Mathf.Max(2f, screenWidth - candidate.width - 2f));
            candidate.y = Mathf.Clamp(candidate.y, 2f, Mathf.Max(2f, screenHeight - candidate.height - 2f));
            for (int attempt = 0; attempt < 18; attempt++)
            {
                bool collision = false;
                foreach (var other in occupied)
                {
                    Rect padded = new Rect(other.x - 3f, other.y - 3f, other.width + 6f, other.height + 6f);
                    if (!candidate.Overlaps(padded)) continue;
                    collision = true;
                    candidate.y = other.yMax + 5f;
                    if (candidate.yMax > screenHeight - 2f)
                    {
                        candidate.y = 2f + (attempt % 3) * (candidate.height + 5f);
                        candidate.x = candidate.x < screenWidth * 0.5f
                            ? Mathf.Min(screenWidth - candidate.width - 2f, candidate.x + candidate.width + 8f)
                            : Mathf.Max(2f, candidate.x - candidate.width - 8f);
                    }
                    break;
                }
                if (!collision) break;
            }
            return candidate;
        }

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
        double TotalWeight(string building)
        {
            if (seismic == null || seismic.buildings == null) return 0.0;
            foreach (var b in seismic.buildings)
            {
                if (string.Equals(b.building, building, System.StringComparison.Ordinal))
                    return b.total_w_seismic_kN;
            }
            return 0.0;
        }

        SeismicFloor FindSeismicFloor(string building, string floor)
        {
            if (seismic == null || seismic.floors == null) return null;
            foreach (var f in seismic.floors)
            {
                if (string.Equals(f.building, building, System.StringComparison.Ordinal) &&
                    string.Equals(f.floor, floor, System.StringComparison.Ordinal))
                    return f;
            }
            return null;
        }

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
        public bool isSeismic = false;
        public double seismicForceKN;
        public string seismicCase;
    }
}
