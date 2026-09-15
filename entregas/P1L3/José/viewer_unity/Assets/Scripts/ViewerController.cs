using System.Collections.Generic;
using System.Text;
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
        private ArchitecturalVisualModelData architecture;
        private TributaryData tributaries;
        private SeismicData seismic;
        private AnalysisResultsData analysisResults;
        private AnalysisCasesData analysisCases;
        private FeDiagnosticData feDiagnostic;
        private P1L3DeliveryData delivery;
        private CapacityData capacity;
        private P1L4StructuralMetadataData p1l4Metadata;
        private DemandCapacityData demandCapacity;
        private P1L4LoadCatalogData p1l4LoadCatalog;
        private PhysicalContextData physicalContext;
        private Texture2D fiberTexture;
        private Texture2D momentCurvatureTexture;
        private Texture2D pmInteractionTexture;
        private bool deliveryPanelVisible = false;
        private int deliveryTab = 0;
        private string activeAnalysisCase = "R";
        private bool uiHidden = false;
        private bool inspectorVisible = true;
        private bool visibilityPanelVisible = true;
        private bool legendExpanded = false;
        private Texture2D expandedGraph = null;
        private string expandedGraphTitle = "";
        private float deformationScaleEX = 1f;
        private float deformationScaleEY = 1f;
        private float activeDeformationScale = 50f;
        private bool activeDeformationVisible = false;
        private readonly List<GameObject> activeDeformationObjects = new List<GameObject>();
        private int diagramMode = 0; // 0 off, 1 My, 2 Mz, 3 N, 4 Vy, 5 Vz
        private string diagramCaption = "Diagramas: seleccione un elemento";
        private readonly List<GameObject> selectedDiagramObjects = new List<GameObject>();
        private bool diagram2DVisible = false;
        private int selectedDiagramMemberIndex = 0;
        private bool demandCapacityPlotVisible = false;
        private bool localAxesVisible = false;
        private readonly List<GameObject> selectedLocalAxisObjects = new List<GameObject>();
        private readonly Dictionary<string, Vector2> memberTrib = new Dictionary<string, Vector2>();
        private readonly Dictionary<string, List<AnalysisElementResult>> analysisByElementId = new Dictionary<string, List<AnalysisElementResult>>();
        private readonly Dictionary<string, ExcludedAnalysisElement> excludedByElementId = new Dictionary<string, ExcludedAnalysisElement>();
        private readonly Dictionary<string, JoseElementForce> joseByAnalysisId = new Dictionary<string, JoseElementForce>();
        private readonly Dictionary<int, JoseNodeDisplacement> joseDisplacementByNode = new Dictionary<int, JoseNodeDisplacement>();
        private JoseSupportsData joseSupports;
        private string joseForcesStatus = "N/A";
        private readonly Dictionary<string, FeDiagnosticElement> diagnosticByElementId = new Dictionary<string, FeDiagnosticElement>();
        private readonly Dictionary<string, List<P1L4ElementMetadata>> p1l4MetadataByElementId = new Dictionary<string, List<P1L4ElementMetadata>>();
        private readonly Dictionary<string, PhysicalContextClassification> physicalContextByElementId = new Dictionary<string, PhysicalContextClassification>();
        private readonly Dictionary<string, DemandCapacityElement> demandCapacityByElementId = new Dictionary<string, DemandCapacityElement>();
        private readonly Dictionary<int, P1L4SupportData> p1l4SupportsByNode = new Dictionary<int, P1L4SupportData>();
        private readonly Dictionary<string, List<GameObject>> byType = new Dictionary<string, List<GameObject>>();
        private readonly Dictionary<string, List<GameObject>> byFloor = new Dictionary<string, List<GameObject>>();
        private readonly Dictionary<string, bool> typeVisible = new Dictionary<string, bool>();
        private readonly Dictionary<string, bool> floorVisible = new Dictionary<string, bool>();
        private readonly Dictionary<GameObject, string> registeredType = new Dictionary<GameObject, string>();
        private readonly Dictionary<GameObject, string> registeredFloor = new Dictionary<GameObject, string>();
        private readonly List<ElementInfo> allElements = new List<ElementInfo>();
        private static readonly Dictionary<string, Material> MaterialsByCat = new Dictionary<string, Material>();

        private Camera cam;
        private Transform selected = null;
        private string lastInfo = "";
        private bool labelsVisible = false;
        private int diagnosticViewMode = 0; // 0 geometria, 1 FE, 2 ambos
        private bool diagnosticColorsVisible = false;
        private bool diagnosticProblemsOnly = false;
        private bool diagnosticWalls = true;
        private bool diagnosticBeams = true;
        private bool diagnosticColumns = true;
        private bool diagnosticEd2Only = false;
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
        private string inspectorTraceability = "";
        private bool inspectorGeometryOpen = false;
        private bool inspectorPropertiesOpen = false;
        private bool inspectorTributaryOpen = false;
        private bool inspectorAnalysisOpen = true;
        private bool inspectorCapacityOpen = false;
        private bool inspectorTraceabilityOpen = false;
        private static Texture2D whiteTex;

        private static readonly Dictionary<string, string> TypeLabels = new Dictionary<string, string>
        {
            { "beam", "Vigas" },
            { "column", "Pilares/columnas" },
            { "column_plan", "Pilares CAD" },
            { "wall", "Muros" },
            { "support", "Apoyos" },
            { "p1l4_support", "Apoyos nodales FE P1L4" },
            { "p1l4_load_surface", "Cargas 700 superficiales (NO APLICADAS)" },
            { "p1l4_load_line", "Cargas 700 lineales (NO APLICADAS)" },
            { "diaphragm", "Analisis - Diafragma" },
            { "slab", "Referencia - Losa provisional" },
            { "axis", "Ejes CAD" },
            { "slab_edge", "Bordes DXF RLE-LOSA" },
            { "architectural_slab", "Arquitectura - Losa P4" },
            { "architectural_slab_edge", "Arquitectura - Borde reconstruido" },
            { "node", "Nodos" },
            { "cad_reference", "Lineas CAD ref." },
            { "tributary", "Areas tributarias" },
            { "tributary_point", "Tributarias a soportes" },
            { "seismic_arrow", "Sismo EX/EY" },
            { "seismic_cm", "Centros de masa" },
            { "seismic_mass", "Masa por piso" },
            { "seismic_shear", "Corte basal" },
            { "seismic_pattern", "Patron sismico" },
            { "seismic_deform_ex", "Deformada OpenSees EX" },
            { "seismic_deform_ey", "Deformada OpenSees EY" },
            { "analysis_deformed", "Deformada caso activo P1L4" },
            { "analysis_diagram", "Diagrama del elemento seleccionado" },
            { "selected_local_axes", "Ejes locales del elemento" },
            { "seismic_torsion", "Torsion de piso" },
            { "fe_candidate", "Malla FE candidata POST-P1L3" },
            { "physical_context", "CONTEXTO FÍSICO (VISUAL ONLY)" }
        };

        private static readonly Dictionary<string, int> FloorOrder = new Dictionary<string, int>
        {
            { "base", 0 }, { "1S", 1 }, { "S1", 1 }, { "1", 2 }, { "P1", 2 }, { "2", 3 }, { "P2", 3 }, { "3", 4 }, { "P3", 4 }, { "4", 5 }, { "P4", 5 }
        };

        void Start()
        {
            cam = Camera.main;
            if (cam == null) cam = Camera.main;
            // La escena historica conserva Text de Canvas; el inspector IMGUI actual
            // reemplaza esos duplicados y evita que queden flotando sobre el modelo.
            if (infoText != null) infoText.gameObject.SetActive(false);
            if (statusText != null) statusText.gameObject.SetActive(false);
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
            var visualLines = JsonLoader.LoadVisualLines();
            if (visualLines != null)
            {
                model.segments = visualLines.segments;
                model.diaphragms = visualLines.diaphragms;
            }
            architecture = JsonLoader.LoadArchitecture();
            analysisResults = JsonLoader.LoadAnalysisResults();
            analysisCases = JsonLoader.LoadAnalysisCases();
            feDiagnostic = JsonLoader.LoadFeDiagnostic();
            diagnosticByElementId.Clear();
            if (feDiagnostic != null && feDiagnostic.elements != null)
                foreach (var item in feDiagnostic.elements)
                    if (item != null && !string.IsNullOrEmpty(item.element_id))
                        diagnosticByElementId[item.element_id] = item;
            delivery = JsonLoader.LoadDelivery();
            capacity = JsonLoader.LoadCapacity();
            p1l4Metadata = JsonLoader.LoadP1L4StructuralMetadata();
            demandCapacity = JsonLoader.LoadDemandCapacity();
            p1l4LoadCatalog = JsonLoader.LoadP1L4LoadCatalog();
            physicalContext = JsonLoader.LoadPhysicalContext();
            physicalContextByElementId.Clear();
            if (physicalContext != null && physicalContext.classifications != null)
                foreach (var item in physicalContext.classifications)
                    if (item != null && !string.IsNullOrEmpty(item.element_id))
                        physicalContextByElementId[item.element_id] = item;
            BuildP1L4Indexes();
            fiberTexture = JsonLoader.LoadPng("fiber_section.png");
            momentCurvatureTexture = JsonLoader.LoadPng("moment_curvature.png");
            pmInteractionTexture = JsonLoader.LoadPng("pm_interaction.png");
            joseSupports = JsonLoader.LoadJoseSupports();
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
            BuildP1L4Supports();
            if (feDiagnostic != null) BuildFeCandidate();
            if (architecture != null) BuildArchitecture();
            if (tributaries != null) BuildTributaries();
            BuildP1L4Loads();
            BuildPhysicalContext();
            seismic = JsonLoader.LoadSeismic();
            if (seismic != null) BuildSeismic();
            RunVisibilitySelfCheck();
            RunDiagnosticSelfCheck();
            RunP1L4SelfCheck();
            RunP1L4DemoSequenceCheck();
            ResetPresentation();
            SetStatus($"POST-P1L3: {model.solids?.Count ?? 0} solidos | FE candidato: {feDiagnostic?.members?.Count ?? 0} miembros (no ejecutado)");
        }

        void BuildP1L4Indexes()
        {
            p1l4MetadataByElementId.Clear();
            demandCapacityByElementId.Clear();
            p1l4SupportsByNode.Clear();
            if (p1l4Metadata != null && p1l4Metadata.elements != null)
            {
                foreach (var item in p1l4Metadata.elements)
                {
                    if (item == null || string.IsNullOrEmpty(item.element_id)) continue;
                    if (!p1l4MetadataByElementId.TryGetValue(item.element_id, out var rows))
                    {
                        rows = new List<P1L4ElementMetadata>();
                        p1l4MetadataByElementId[item.element_id] = rows;
                    }
                    rows.Add(item);
                }
            }
            if (demandCapacity != null && demandCapacity.elements != null)
                foreach (var item in demandCapacity.elements)
                    if (item != null && !string.IsNullOrEmpty(item.element_id))
                        demandCapacityByElementId[item.element_id] = item;
            if (p1l4Metadata != null && p1l4Metadata.supports != null)
                foreach (var item in p1l4Metadata.supports)
                    if (item != null) p1l4SupportsByNode[item.node_tag] = item;
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
                    if (!string.IsNullOrEmpty(result.element_id))
                    {
                        if (!analysisByElementId.TryGetValue(result.element_id, out var rows))
                        {
                            rows = new List<AnalysisElementResult>();
                            analysisByElementId[result.element_id] = rows;
                        }
                        rows.Add(result);
                    }
            if (chosen.excluded_elements != null)
                foreach (var item in chosen.excluded_elements)
                    if (!string.IsNullOrEmpty(item.element_id)) excludedByElementId[item.element_id] = item;

            // La salida plana entregada por José es la fuente integrada de Semana 4.
            // Se indexa por analysis_id para preservar relaciones geometría 1:N.
            joseByAnalysisId.Clear();
            var joseForces = JsonLoader.LoadJoseForces(normalized);
            joseForcesStatus = joseForces != null && !string.IsNullOrEmpty(joseForces.status)
                ? joseForces.status : "N/A";
            if (joseForces != null && joseForces.elements != null)
                foreach (var item in joseForces.elements)
                    if (item != null && !string.IsNullOrEmpty(item.analysis_id))
                        joseByAnalysisId[item.analysis_id] = item;
            joseDisplacementByNode.Clear();
            var joseDisplacements = JsonLoader.LoadJoseDisplacements(normalized);
            if (joseDisplacements != null && joseDisplacements.nodes != null)
                foreach (var item in joseDisplacements.nodes)
                    if (item != null) joseDisplacementByNode[item.node_tag] = item;
            if (model != null && model.solids != null) RebuildActiveDeformedShape();
            if (lastSelected != null) ShowInfo(lastSelected);
        }

        void RebuildActiveDeformedShape()
        {
            foreach (var go in activeDeformationObjects)
            {
                if (go == null) continue;
                if (registeredFloor.TryGetValue(go, out var priorFloor) && byFloor.TryGetValue(priorFloor, out var floorObjects))
                    floorObjects.Remove(go);
                registeredType.Remove(go);
                registeredFloor.Remove(go);
                if (Application.isPlaying) Destroy(go); else DestroyImmediate(go);
            }
            activeDeformationObjects.Clear();
            if (byType.ContainsKey("analysis_deformed")) byType["analysis_deformed"].Clear();
            if (analysisResults == null || analysisResults.nodes == null || analysisResults.elements == null) return;

            var nodes = new Dictionary<int, AnalysisNodeResult>();
            foreach (var node in analysisResults.nodes)
                if (node != null) nodes[node.node_tag] = node;
            Color color = ActiveCaseColor(activeAnalysisCase);
            foreach (var element in analysisResults.elements)
            {
                if (element == null || !nodes.TryGetValue(element.node_i, out var ni) || !nodes.TryGetValue(element.node_j, out var nj)) continue;
                Vector3 di = joseDisplacementByNode.TryGetValue(element.node_i, out var jdi)
                    ? new Vector3((float)jdi.ux_m, (float)jdi.uy_m, (float)jdi.uz_m)
                    : new Vector3((float)ni.ux_m, (float)ni.uy_m, (float)ni.uz_m);
                Vector3 dj = joseDisplacementByNode.TryGetValue(element.node_j, out var jdj)
                    ? new Vector3((float)jdj.ux_m, (float)jdj.uy_m, (float)jdj.uz_m)
                    : new Vector3((float)nj.ux_m, (float)nj.uy_m, (float)nj.uz_m);
                Vector3 p0 = V(ni.coord) + di * activeDeformationScale;
                Vector3 p1 = V(nj.coord) + dj * activeDeformationScale;
                var go = new GameObject($"P1L4_DEF_{activeAnalysisCase}_{element.analysis_id}");
                var line = go.AddComponent<LineRenderer>();
                line.useWorldSpace = false;
                line.positionCount = 2;
                line.SetPosition(0, p0);
                line.SetPosition(1, p1);
                line.startWidth = 0.18f;
                line.endWidth = 0.18f;
                line.material = SeismicLineMat(color);
                Register(go, "analysis_deformed", element.floor ?? "");
                activeDeformationObjects.Add(go);
            }
            typeVisible["analysis_deformed"] = activeDeformationVisible;
            ReapplyAll();
        }

        static Color ActiveCaseColor(string caseName)
        {
            switch (caseName)
            {
                case "G": return new Color(0.75f, 0.78f, 0.85f);
                case "Q": return new Color(0.25f, 0.95f, 0.45f);
                case "EX": return new Color(1f, 0.2f, 0.12f);
                case "EY": return new Color(0.2f, 0.55f, 1f);
                default: return new Color(1f, 0.25f, 0.85f);
            }
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
            MaterialsByCat["architectural_slab"] = LoadMat("MatConcreto", new Color(0.28f, 0.72f, 0.68f));
            MaterialsByCat["architectural_slab_edge"] = LoadMat("MatAcero", new Color(0.95f, 0.82f, 0.25f));
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

        void BuildP1L4Supports()
        {
            if (p1l4Metadata == null || p1l4Metadata.supports == null) return;
            foreach (var support in p1l4Metadata.supports)
            {
                if (support == null || support.coord_m == null || support.coord_m.Count < 3) continue;
                Vector3 coord = V(support.coord_m);
                var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                go.name = "P1L4_SUPPORT_" + support.node_tag;
                go.transform.position = coord;
                go.transform.localScale = new Vector3(0.42f, 0.42f, 0.28f);
                var renderer = go.GetComponent<Renderer>();
                renderer.sharedMaterial = LineMaterial(new Color(0.95f, 0.25f, 0.85f));

                var info = go.AddComponent<ElementInfo>();
                info.go = go;
                info.id = support.support_id;
                info.humanId = support.support_id;
                info.category = "p1l4_support";
                info.floor = string.IsNullOrEmpty(support.floor) ? "base" : support.floor;
                info.building = SupportBuilding(support.node_tag);
                info.materialName = "restriccion nodal OpenSees";
                info.nodeI = coord;
                info.coordCenter = coord;
                info.baseColor = renderer.sharedMaterial.color;
                info.isP1L4Support = true;
                info.supportNodeTag = support.node_tag;
                info.fixUX = support.UX;
                info.fixUY = support.UY;
                info.fixUZ = support.UZ;
                info.fixRX = support.RX;
                info.fixRY = support.RY;
                info.fixRZ = support.RZ;
                Register(go, "p1l4_support", info.floor);
                allElements.Add(info);
            }
        }

        string SupportBuilding(int nodeTag)
        {
            if (p1l4Metadata != null && p1l4Metadata.elements != null)
                foreach (var item in p1l4Metadata.elements)
                    if (item != null && (item.node_i == nodeTag || item.node_j == nodeTag))
                        return string.IsNullOrEmpty(item.building) ? "Modelo global" : item.building;
            return "Modelo global";
        }

        void BuildP1L4Loads()
        {
            if (p1l4LoadCatalog == null || p1l4LoadCatalog.entries == null) return;
            var slabZ = new Dictionary<string, float>();
            if (model != null && model.solids != null)
                foreach (var solid in model.solids)
                {
                    if (solid == null || solid.category != "slab" || solid.center == null || solid.center.Count < 3) continue;
                    string key = (solid.building ?? "") + "|" + (solid.floor ?? "");
                    float top = (float)solid.center[2] + (float)solid.height_m * 0.5f;
                    if (!slabZ.ContainsKey(key) || slabZ[key] < top) slabZ[key] = top;
                }

            foreach (var load in p1l4LoadCatalog.entries)
            {
                if (load == null || load.coordinates_xy_flat == null) continue;
                string key = (load.building ?? "") + "|" + (load.floor ?? "");
                float z = (slabZ.TryGetValue(key, out var top) ? top : 0f) + 0.12f;
                ElementInfo info = null;
                if (load.geometry_type == "Polygon" && load.coordinates_xy_flat.Count >= 6)
                {
                    var polygon = new List<Point2D>();
                    for (int i = 0; i + 1 < load.coordinates_xy_flat.Count; i += 2)
                        polygon.Add(new Point2D { x = load.coordinates_xy_flat[i], y = load.coordinates_xy_flat[i + 1] });
                    info = CreateTribPoly("load_" + load.load_id, polygon, z, 1f, 0f, "p1l4_load_surface", load.building, load.floor, load.load_id, "");
                    var renderer = info.go.GetComponent<Renderer>();
                    renderer.sharedMaterial = SeismicLineMat(load.load_type.StartsWith("SC_")
                        ? new Color(0.1f, 0.8f, 1f, 0.38f)
                        : new Color(1f, 0.55f, 0.12f, 0.38f));
                    info.baseMat = renderer.sharedMaterial;
                    info.baseColor = renderer.sharedMaterial.color;
                }
                else if (load.geometry_type == "LineString" && load.coordinates_xy_flat.Count >= 4)
                {
                    Vector3 start = new Vector3((float)load.coordinates_xy_flat[0], (float)load.coordinates_xy_flat[1], z);
                    Vector3 end = new Vector3((float)load.coordinates_xy_flat[2], (float)load.coordinates_xy_flat[3], z);
                    Vector3 direction = end - start;
                    if (direction.magnitude < 0.01f) continue;
                    var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    go.name = "load_" + load.load_id;
                    go.transform.position = (start + end) * 0.5f;
                    go.transform.localScale = new Vector3(direction.magnitude, 0.12f, 0.12f);
                    go.transform.rotation = Quaternion.FromToRotation(Vector3.right, direction.normalized);
                    var renderer = go.GetComponent<Renderer>();
                    renderer.sharedMaterial = LineMaterial(load.application_status.StartsWith("READY")
                        ? new Color(0.15f, 0.9f, 0.95f)
                        : new Color(1f, 0.25f, 0.2f));
                    info = go.AddComponent<ElementInfo>();
                    info.go = go;
                    info.id = load.load_id;
                    info.humanId = load.load_id;
                    info.category = "p1l4_load_line";
                    info.floor = load.floor;
                    info.building = load.building;
                    info.nodeI = start;
                    info.nodeJ = end;
                    info.coordCenter = (start + end) * 0.5f;
                    info.lengthM = direction.magnitude;
                    info.baseColor = renderer.sharedMaterial.color;
                    Register(go, "p1l4_load_line", load.floor);
                    allElements.Add(info);
                }
                if (info == null) continue;
                info.isP1L4Load = true;
                info.loadType = load.load_type;
                info.loadValue = load.SI_value;
                info.loadUnit = load.SI_unit;
                info.loadApplicationStatus = load.application_status;
                info.loadReceiverStatus = load.receiver_status;
                info.loadReceiverIds = load.receiver_ids == null ? "" : string.Join(", ", load.receiver_ids.ToArray());
                info.sourceDxf = load.source_sheet;
                info.confidence = load.confidence;
                info.materialName = "carga auditada; no aplicada al modelo P1L4";
            }
        }

        void BuildFeCandidate()
        {
            if (feDiagnostic.members == null) return;
            foreach (var member in feDiagnostic.members)
            {
                Vector3 start = V(member.start);
                Vector3 end = V(member.end);
                Vector3 direction = end - start;
                float length = direction.magnitude;
                if (length < 0.01f) continue;
                var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                go.name = "FE_" + member.analysis_id;
                go.transform.position = (start + end) * 0.5f;
                go.transform.localScale = new Vector3(length, 0.055f, 0.055f);
                go.transform.rotation = Quaternion.FromToRotation(Vector3.right, direction.normalized);
                var renderer = go.GetComponent<Renderer>();
                var color = DiagnosticColor(member.validation);
                renderer.sharedMaterial = LineMaterial(color);

                var info = go.AddComponent<ElementInfo>();
                info.go = go;
                info.id = member.element_id;
                info.humanId = member.element_id;
                info.elementTag = member.geometryElementTag;
                info.category = member.type;
                info.floor = member.floor;
                info.building = member.building;
                info.materialName = "miembro FE candidato (no ejecutado)";
                info.nodeI = start;
                info.nodeJ = end;
                info.coordCenter = (start + end) * 0.5f;
                info.lengthM = length;
                info.baseColor = color;
                info.isFeCandidateVisual = true;
                info.analysisId = member.analysis_id;
                info.openseesTag = member.opensees_element_tag;
                info.diagnosticStatus = member.validation;
                if (diagnosticByElementId.TryGetValue(member.element_id, out var diagnostic))
                    ApplyDiagnosticInfo(info, diagnostic);
                ApplyPhysicalContextInfo(info);
                Register(go, "fe_candidate", member.floor);
                allElements.Add(info);
            }
        }

        void BuildArchitecture()
        {
            if (architecture.objects == null) return;
            foreach (var item in architecture.objects)
            {
                if (item == null || item.surface_vertices_xy_flat == null || item.surface_triangles == null || item.outline_xy_flat == null) continue;
                if (item.surface_vertices_xy_flat.Count < 6 || item.surface_triangles.Count < 3 || item.outline_xy_flat.Count < 6) continue;
                CreateArchitecturalSlab(item);
            }
        }

        void CreateArchitecturalSlab(ArchitecturalObjectData item)
        {
            int n = item.surface_vertices_xy_flat.Count / 2;
            float top = (float)item.top_z_m;
            float bottom = top - (float)item.thickness_m;
            var vertices = new Vector3[n * 2];
            for (int i = 0; i < n; i++)
            {
                float x = (float)item.surface_vertices_xy_flat[i * 2];
                float y = (float)item.surface_vertices_xy_flat[i * 2 + 1];
                vertices[i] = new Vector3(x, y, top);
                vertices[i + n] = new Vector3(x, y, bottom);
            }
            var triangles = new List<int>();
            for (int i = 0; i + 2 < item.surface_triangles.Count; i += 3)
            {
                int a = item.surface_triangles[i];
                int b = item.surface_triangles[i + 1];
                int c = item.surface_triangles[i + 2];
                triangles.Add(a); triangles.Add(b); triangles.Add(c);
                triangles.Add(c + n); triangles.Add(b + n); triangles.Add(a + n);
            }
            int outlineCount = Mathf.Min(item.outline_xy_flat.Count / 2, n);
            for (int i = 0; i < outlineCount; i++)
            {
                int j = (i + 1) % outlineCount;
                triangles.Add(i); triangles.Add(j + n); triangles.Add(j);
                triangles.Add(i); triangles.Add(i + n); triangles.Add(j + n);
            }

            var mesh = new Mesh { name = item.id + "_mesh" };
            mesh.vertices = vertices;
            mesh.triangles = triangles.ToArray();
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();

            var go = new GameObject(item.id);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = MatFor("architectural_slab");
            go.AddComponent<MeshCollider>().sharedMesh = mesh;
            var info = go.AddComponent<ElementInfo>();
            info.go = go;
            info.id = item.id;
            info.humanId = item.id;
            info.category = "architectural_slab";
            info.kind = "extruded_polygon";
            info.floor = item.floor;
            info.building = item.building;
            info.sourceLayer = item.source_layer;
            info.sourceDxf = item.source_sheet;
            info.materialName = "hormigon arquitectonico (visual)";
            info.heightM = item.thickness_m;
            info.visualAreaM2 = item.area_m2;
            info.confidence = item.confidence;
            info.participatesInFE = item.participates_in_FE;
            info.hasFEParticipationFlag = true;
            info.coordZBottom = bottom;
            info.coordZTop = top;
            info.coordCenter = mesh.bounds.center;
            info.nodeI = vertices[0];
            info.nodeJ = vertices[Mathf.Min(1, n - 1)];
            info.baseColor = tintOf("architectural_slab");
            Register(go, "architectural_slab", item.floor);
            allElements.Add(info);

            var edge = new GameObject(item.id + "-EDGE");
            var line = edge.AddComponent<LineRenderer>();
            line.positionCount = outlineCount;
            line.loop = true;
            for (int i = 0; i < outlineCount; i++)
                line.SetPosition(i, new Vector3((float)item.outline_xy_flat[i * 2], (float)item.outline_xy_flat[i * 2 + 1], top + 0.01f));
            line.startWidth = 0.08f;
            line.endWidth = 0.08f;
            line.material = LineMaterial(tintOf("architectural_slab_edge"));
            var edgeInfo = edge.AddComponent<ElementInfo>();
            edgeInfo.go = edge;
            edgeInfo.id = item.id + "-EDGE";
            edgeInfo.humanId = edgeInfo.id;
            edgeInfo.category = "architectural_slab_edge";
            edgeInfo.floor = item.floor;
            edgeInfo.building = item.building;
            edgeInfo.sourceLayer = item.source_layer;
            edgeInfo.sourceDxf = item.source_sheet;
            edgeInfo.materialName = "contorno arquitectonico (visual)";
            edgeInfo.confidence = item.confidence;
            edgeInfo.participatesInFE = false;
            edgeInfo.hasFEParticipationFlag = true;
            edgeInfo.coordCenter = mesh.bounds.center;
            edgeInfo.nodeI = new Vector3((float)item.outline_xy_flat[0], (float)item.outline_xy_flat[1], top);
            edgeInfo.nodeJ = edgeInfo.nodeI;
            Register(edge, "architectural_slab_edge", item.floor);
            allElements.Add(edgeInfo);
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
            if (diagnosticByElementId.TryGetValue(data.id, out var diagnostic))
                ApplyDiagnosticInfo(data, diagnostic);
            ApplyPhysicalContextInfo(data);

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

        void ApplyDiagnosticInfo(ElementInfo info, FeDiagnosticElement diagnostic)
        {
            info.diagnosticStatus = diagnostic.validation;
            info.structuralClassification = diagnostic.structural_classification;
            info.diagnosticMotive = diagnostic.motive;
            info.diagnosticComponent = diagnostic.component_id;
            info.expectedConnection = diagnostic.expected_connection;
            info.diagnosticEvidence = diagnostic.evidence;
            info.diagnosticSource = string.IsNullOrEmpty(diagnostic.source_dxf)
                ? diagnostic.source_layer
                : diagnostic.source_dxf + " / " + diagnostic.source_layer;
            info.crosswalk = diagnostic.crosswalk;
        }

        void ApplyPhysicalContextInfo(ElementInfo info)
        {
            if (info == null || string.IsNullOrEmpty(info.id)) return;
            if (!physicalContextByElementId.TryGetValue(info.id, out var item)) return;
            info.physicalCluster = item.cluster;
            info.physicalClassification = item.physical_classification;
            info.physicalSupport = item.physical_support;
            info.mainFeParticipation = item.main_fe_participation;
            info.revisedDiagnostic = item.revised_diagnostic;
            info.duplicateClassification = item.duplicate_classification;
            info.physicalEvidence = item.evidence;
        }

        void BuildPhysicalContext()
        {
            if (physicalContext == null) return;
            if (physicalContext.clusters != null)
            {
                foreach (var cluster in physicalContext.clusters)
                {
                    if (cluster == null || cluster.center == null || cluster.size == null) continue;
                    Vector3 center = V(cluster.center);
                    Vector3 size = V(cluster.size);
                    Color color = ContextColor(cluster.color);
                    CreateContextBox(cluster, center, size, color);
                    _physicalContextLabels.Add(new Label2D(center.x, center.y, center.z + size.z * 0.5f + 0.4f, cluster.label, color));
                }
            }
            if (physicalContext.level_markers != null)
            {
                foreach (var marker in physicalContext.level_markers)
                {
                    if (marker == null || marker.start == null || marker.end == null) continue;
                    Color color = ContextColor(marker.color);
                    CreateContextLine(V(marker.start), V(marker.end), 0.10f, color, marker.id, marker.floor);
                    Vector3 middle = (V(marker.start) + V(marker.end)) * 0.5f;
                    _physicalContextLabels.Add(new Label2D(middle.x, middle.y, middle.z + 0.25f, marker.label, color));
                }
            }
        }

        void CreateContextBox(PhysicalContextCluster cluster, Vector3 center, Vector3 size, Color color)
        {
            Vector3 h = size * 0.5f;
            var corners = new Vector3[8];
            int index = 0;
            for (int z = -1; z <= 1; z += 2)
                for (int y = -1; y <= 1; y += 2)
                    for (int x = -1; x <= 1; x += 2)
                        corners[index++] = center + new Vector3(x * h.x, y * h.y, z * h.z);
            int[,] edges = { {0,1},{2,3},{4,5},{6,7},{0,2},{1,3},{4,6},{5,7},{0,4},{1,5},{2,6},{3,7} };
            for (int i = 0; i < 12; i++)
                CreateContextLine(corners[edges[i,0]], corners[edges[i,1]], 0.08f, color, cluster.id + "_edge_" + i, cluster.floor);

            var marker = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            marker.name = cluster.id;
            marker.transform.position = center;
            marker.transform.localScale = Vector3.one * 0.7f;
            marker.GetComponent<Renderer>().sharedMaterial = LineMaterial(color);
            var info = marker.AddComponent<ElementInfo>();
            info.go = marker;
            info.id = cluster.id;
            info.humanId = cluster.label;
            info.category = "physical_context";
            info.floor = cluster.floor;
            info.building = "EDIFICIO_1";
            info.materialName = cluster.note;
            info.coordCenter = center;
            info.nodeI = center;
            info.nodeJ = center;
            info.hasFEParticipationFlag = true;
            info.participatesInFE = false;
            info.physicalCluster = cluster.id;
            info.physicalClassification = "VISUAL_CONTEXT_REGION";
            info.physicalSupport = "NO_FE_SUPPORT_ASSIGNED";
            info.mainFeParticipation = "VISUAL_ONLY";
            info.revisedDiagnostic = physicalContext.status;
            info.physicalEvidence = cluster.note;
            Register(marker, "physical_context", cluster.floor);
            allElements.Add(info);
        }

        void CreateContextLine(Vector3 start, Vector3 end, float thickness, Color color, string name, string floor)
        {
            Vector3 direction = end - start;
            if (direction.magnitude < 0.001f) return;
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.position = (start + end) * 0.5f;
            go.transform.localScale = new Vector3(direction.magnitude, thickness, thickness);
            go.transform.rotation = Quaternion.FromToRotation(Vector3.right, direction.normalized);
            go.GetComponent<Renderer>().sharedMaterial = LineMaterial(color);
            var collider = go.GetComponent<Collider>();
            if (collider != null) Destroy(collider);
            Register(go, "physical_context", floor);
        }

        static Color ContextColor(string html)
        {
            if (!string.IsNullOrEmpty(html) && ColorUtility.TryParseHtmlString(html, out var color)) return color;
            return new Color(1f, 0.6f, 0.1f);
        }

        static Color DiagnosticColor(string status)
        {
            switch (status)
            {
                case "CONNECTED_EXPECTED": return new Color(0.2f, 0.9f, 0.35f);
                case "FREE_END_EXPECTED": return new Color(0.2f, 0.55f, 1f);
                case "DISCONNECTED_ERROR": return new Color(1f, 0.2f, 0.16f);
                case "UNRESOLVED": return new Color(1f, 0.78f, 0.12f);
                default: return new Color(0.58f, 0.62f, 0.7f, 0.7f);
            }
        }

        void CreateSegment(SegmentData seg)
        {
            int pointCount = seg.points_flat != null ? seg.points_flat.Count / 3 : seg.points != null ? seg.points.Count : 0;
            if (pointCount < 2) return;
            string displayType = seg.category == "axis" ? "axis" : seg.category == "slab_edge" ? "slab_edge" : "cad_reference";
            string publicId = !string.IsNullOrEmpty(seg.id) ? seg.id : !string.IsNullOrEmpty(seg.elementTag) ? seg.elementTag : "SEG";
            var go = new GameObject("seg_" + publicId);
            var lr = go.AddComponent<LineRenderer>();
            lr.positionCount = pointCount;
            for (int i = 0; i < pointCount; i++) lr.SetPosition(i, SegmentPoint(seg, i));
            lr.startWidth = 0.03f; lr.endWidth = 0.03f;
            lr.material = LineMaterial(tintOf(displayType));
            var data = go.AddComponent<ElementInfo>();
            data.go = go;
            data.id = publicId;
            data.humanId = string.IsNullOrEmpty(seg.human_id) ? publicId : seg.human_id;
            data.elementTag = seg.elementTag;
            data.category = displayType;
            data.floor = seg.floor;
            data.building = seg.building;
            data.sourceLayer = seg.source_layer;
            data.sourceDxf = seg.source_dxf;
            data.lengthM = seg.length_m;
            data.confidence = seg.confidence;
            data.nodeI = SegmentPoint(seg, 0);
            data.nodeJ = SegmentPoint(seg, pointCount - 1);
            data.coordCenter = (data.nodeI + data.nodeJ) * 0.5f;
            data.materialName = "referencia DXF";
            Register(go, displayType, seg.floor);
            allElements.Add(data);
        }

        void CreateDiaphragm(DiaphragmData dia)
        {
            int pointCount = dia.points_flat != null ? dia.points_flat.Count / 3 : dia.points != null ? dia.points.Count : 0;
            if (pointCount < 2) return;
            var go = new GameObject("dia_" + dia.floor);
            var lr = go.AddComponent<LineRenderer>();
            lr.positionCount = pointCount;
            lr.loop = true;
            for (int i = 0; i < pointCount; i++) lr.SetPosition(i, DiaphragmPoint(dia, i));
            lr.startWidth = 0.06f; lr.endWidth = 0.06f;
            lr.material = LineMaterial(tintOf("diaphragm"));
            var data = go.AddComponent<ElementInfo>();
            data.go = go;
            data.id = !string.IsNullOrEmpty(dia.id) ? dia.id : "DIA-" + dia.floor;
            data.humanId = string.IsNullOrEmpty(dia.human_id) ? data.id : dia.human_id;
            data.category = "diaphragm";
            data.floor = dia.floor;
            data.building = dia.building;
            data.materialName = "referencia analitica";
            data.hasFEParticipationFlag = true;
            data.participatesInFE = true;
            data.nodeI = DiaphragmPoint(dia, 0);
            data.nodeJ = DiaphragmPoint(dia, pointCount - 1);
            data.coordCenter = (data.nodeI + data.nodeJ) * 0.5f;
            Register(go, "diaphragm", dia.floor);
            allElements.Add(data);
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
                CreateDeformLine(p0 + d0, p1 + d1, color, b.building, element.floor ?? "", ex ? "seismic_deform_ex" : "seismic_deform_ey");
            }
        }

        AnalysisResultsData FindAnalysisCaseData(string name)
        {
            if (analysisCases == null || analysisCases.cases == null) return null;
            foreach (var item in analysisCases.cases)
                if (item != null && (item.case_name ?? "").Replace("CASE_", "").ToUpperInvariant() == name.ToUpperInvariant()) return item;
            return null;
        }

        AnalysisNodeResult FindAnalysisNode(int tag)
        {
            if (analysisResults == null || analysisResults.nodes == null) return null;
            foreach (var node in analysisResults.nodes)
                if (node != null && node.node_tag == tag) return node;
            return null;
        }

        void CreateDeformLine(Vector3 p0, Vector3 p1, Color color, string building, string floor, string category)
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
            ei.category = category;
            ei.floor = floor;
            ei.building = building;
            ei.isSeismic = true;
            ei.baseColor = color;
            ei.nodeI = p0;
            ei.nodeJ = p1;
            Register(go, category, floor);
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
            floor = floor ?? "";
            go.transform.SetParent(transform, false);
            registeredType[go] = type;
            registeredFloor[go] = floor;
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
            var info = go.GetComponent<ElementInfo>();
            bool isFe = info != null && info.isFeCandidateVisual;
            bool isStructuralGeometry = !isFe && info != null &&
                (info.category == "beam" || info.category == "wall" || info.category == "column");
            if (isFe) vis = vis && diagnosticViewMode != 0;
            else if (diagnosticViewMode == 1) vis = false;
            if ((isFe || isStructuralGeometry) && info != null)
            {
                if (info.category == "wall" && !diagnosticWalls) vis = false;
                if (info.category == "beam" && !diagnosticBeams) vis = false;
                if (info.category == "column" && !diagnosticColumns) vis = false;
                if (diagnosticEd2Only && info.building != "EDIFICIO_2") vis = false;
                if (diagnosticProblemsOnly)
                    vis = vis && (info.diagnosticStatus == "DISCONNECTED_ERROR" || info.diagnosticStatus == "UNRESOLVED");
                UpdateDiagnosticMaterial(info);
            }
            else if (diagnosticProblemsOnly)
            {
                vis = false;
            }
            go.SetActive(vis);
        }

        void UpdateDiagnosticMaterial(ElementInfo info)
        {
            if (info == null || info.go == null || info.isFeCandidateVisual) return;
            var renderer = info.go.GetComponent<Renderer>();
            if (renderer == null) return;
            if (diagnosticColorsVisible && !string.IsNullOrEmpty(info.diagnosticStatus))
            {
                var material = renderer.material;
                material.color = DiagnosticColor(info.diagnosticStatus);
            }
            else
            {
                var material = MatFor(info.category);
                if (material != null) renderer.sharedMaterial = material;
            }
        }

        void ReapplyAll()
        {
            foreach (var kv in byType)
                foreach (var go in kv.Value)
                    ApplyVisibility(go,
                        registeredType.TryGetValue(go, out var type) ? type : kv.Key,
                        registeredFloor.TryGetValue(go, out var floor) ? floor : "");
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
            if (new Rect(10f, 10f, 250f, 207f).Contains(m)) return true;
            if (visibilityPanelVisible && ControlsRect().Contains(m)) return true;
            if (!visibilityPanelVisible && new Rect(10f, 225f, 150f, 28f).Contains(m)) return true;
            // Zona panel de info (arriba izquierda)
            if (lastSelected != null && inspectorVisible && InspectorRect().Contains(m)) return true;
            if (lastSelected != null && !inspectorVisible && new Rect(InspectorRect().x + InspectorRect().width - 160f, InspectorRect().y, 160f, 26f).Contains(m)) return true;
            bool legendShown =
                (typeVisible.ContainsKey("seismic_arrow") && typeVisible["seismic_arrow"]) ||
                (typeVisible.ContainsKey("seismic_torsion") && typeVisible["seismic_torsion"]) ||
                (typeVisible.ContainsKey("seismic_deform_ex") && typeVisible["seismic_deform_ex"]) ||
                (typeVisible.ContainsKey("seismic_deform_ey") && typeVisible["seismic_deform_ey"]) ||
                (typeVisible.ContainsKey("tributary") && typeVisible["tributary"]);
            if (legendShown && m.x > Screen.width - 250f && m.y > Screen.height - (legendExpanded ? 126f : 40f)) return true;
            if (deliveryPanelVisible && DeliveryRect().Contains(m)) return true;
            if (new Rect(Screen.width * 0.5f - 195f, 10f, 390f, 94f).Contains(m)) return true;
            if (!deliveryPanelVisible && new Rect(Screen.width * 0.5f - 90f, 110f, 180f, 26f).Contains(m)) return true;
            if (new Rect(Screen.width * 0.5f - 245f, 142f, 490f, 58f).Contains(m)) return true;
            if (demandCapacityPlotVisible)
            {
                float plotWidth = Mathf.Min(660f, Screen.width - 80f);
                float plotHeight = Mathf.Min(500f, Screen.height - 80f);
                if (new Rect((Screen.width - plotWidth) * 0.5f, (Screen.height - plotHeight) * 0.5f, plotWidth, plotHeight).Contains(m)) return true;
            }
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
            ClearSelectedDiagram();
            ClearSelectedLocalAxes();
        }

        void ShowInfo(ElementInfo ei)
        {
            if (ei.isP1L4Load)
            {
                ShowP1L4LoadInfo(ei);
                return;
            }
            if (ei.isP1L4Support)
            {
                ShowP1L4SupportInfo(ei);
                return;
            }
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
            string analysisLine = BuildP1L4AnalysisText(ei, id, section, coord);
            string resultsLine = BuildP1L4ResultsText(ei, id);
            string diagnosticLine = "";
            if (!string.IsNullOrEmpty(ei.diagnosticStatus))
            {
                var mappings = new List<string>();
                if (ei.crosswalk != null)
                    foreach (var mapping in ei.crosswalk)
                        mappings.Add($"{mapping.analysis_id} | OpenSees {mapping.opensees_element_tag} | nodos {mapping.opensees_node_i}-{mapping.opensees_node_j}");
                string crosswalkLine = mappings.Count == 0
                    ? "Sin segmento FE candidato"
                    : string.Join("\n", mappings.ToArray());
                diagnosticLine =
                    $"\n\nDIAGNOSTICO FE POST-P1L3 (candidato no ejecutado)\n" +
                    $"Estado: {ei.diagnosticStatus}\nClase: {ei.structuralClassification}\n" +
                    $"Motivo: {ei.diagnosticMotive}\nComponente: {ei.diagnosticComponent}\n" +
                    $"Conexion esperada: {ei.expectedConnection}\nEvidencia: {ei.diagnosticEvidence}\n" +
                    $"Fuente: {(string.IsNullOrEmpty(ei.diagnosticSource) ? "-" : ei.diagnosticSource)}\n" +
                    $"Geometria: {id}\nCrosswalk 1:N:\n{crosswalkLine}";
            }
            string capacityLine = BuildDemandCapacityText(id);
            string traceabilityLine = BuildTraceabilityText(ei, id, diagnosticLine);
            inspectorIdentity = $"{id}\n{cat} | Piso {ei.floor} | {(string.IsNullOrEmpty(ei.building) ? "Sin edificio" : ei.building)}\nEjes: {ejes}";
            string visualArea = ei.visualAreaM2 > 0 ? $"\nArea visual: {ei.visualAreaM2:F3} m2" : "";
            string source = !string.IsNullOrEmpty(ei.sourceDxf) || !string.IsNullOrEmpty(ei.sourceLayer)
                ? $"\nFuente: {ei.sourceDxf ?? "-"} / {ei.sourceLayer ?? "-"}" : "";
            string confidence = string.IsNullOrEmpty(ei.confidence) ? "" : $"\nConfianza: {ei.confidence}";
            inspectorGeometry = BuildP1L4IdentityText(ei, id, cat, source, confidence);
            inspectorProperties = analysisLine + $"\nLongitud geometrica: {ei.lengthM:F3} m{visualArea}";
            inspectorTributary = string.IsNullOrEmpty(cargaLine) ? "Sin carga tributaria asociada." : cargaLine;
            inspectorAnalysis = resultsLine;
            inspectorCapacity = capacityLine;
            inspectorTraceability = traceabilityLine;
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
                "\n" + resultsLine + "\n" + capacityLine + "\n" + traceabilityLine;
            if (infoText != null) infoText.text = lastInfo;
            lastSelected = ei;
            inspectorVisible = true;
            RebuildSelectedDiagram();
            RebuildSelectedLocalAxes();
        }

        void ShowP1L4LoadInfo(ElementInfo ei)
        {
            string receiver = string.IsNullOrEmpty(ei.loadReceiverIds) ? "N/A" : ei.loadReceiverIds;
            inspectorIdentity = $"{ei.humanId}\n{ei.loadType} | Piso {ei.floor} | {ei.building}";
            inspectorGeometry = $"Geometria: {(ei.category == "p1l4_load_surface" ? "superficie" : "linea")}\nCentro: {P(ei.coordCenter)}";
            inspectorProperties = $"Magnitud: {ei.loadValue:F3} {ei.loadUnit}\nEstado: {ei.loadApplicationStatus}\nConfianza: {ei.confidence}";
            inspectorTributary = $"Receptores: {receiver}\nEstado receptor: {(string.IsNullOrEmpty(ei.loadReceiverStatus) ? "N/A" : ei.loadReceiverStatus)}";
            inspectorAnalysis = "NO APLICADA: esta carga proviene del catalogo 700 auditado y no modifica los resultados historicos mostrados.";
            inspectorCapacity = "N/A";
            inspectorTraceability = $"Lamina fuente: {ei.sourceDxf}\nCatalogo: {p1l4LoadCatalog.source}\nEstado de datos: {p1l4LoadCatalog.data_state}";
            lastInfo = inspectorIdentity + "\n\n" + inspectorProperties + "\n\n" + inspectorTributary + "\n\n" + inspectorAnalysis;
            if (infoText != null) infoText.text = lastInfo;
            lastSelected = ei;
            inspectorVisible = true;
            ClearSelectedDiagram();
            ClearSelectedLocalAxes();
        }

        void ShowP1L4SupportInfo(ElementInfo ei)
        {
            string restrictions = $"UX={(ei.fixUX ? "FIJO" : "LIBRE")}  UY={(ei.fixUY ? "FIJO" : "LIBRE")}  UZ={(ei.fixUZ ? "FIJO" : "LIBRE")}\n" +
                $"RX={(ei.fixRX ? "FIJO" : "LIBRE")}  RY={(ei.fixRY ? "FIJO" : "LIBRE")}  RZ={(ei.fixRZ ? "FIJO" : "LIBRE")}";
            inspectorIdentity = $"{ei.humanId}\nApoyo nodal FE P1L4 | Nodo OpenSees {ei.supportNodeTag}\nPiso {ei.floor} | {ei.building}";
            inspectorGeometry = $"Coordenada global [m]: {P(ei.coordCenter)}\nEl simbolo se ubica en la coordenada exacta del nodo; no se asocia por proximidad a un solido historico.";
            inspectorProperties = restrictions + "\nConvencion: X/Y horizontales, Z vertical en el contrato estructural.";
            inspectorTributary = "N/A: el apoyo no define por si mismo una carga tributaria.";
            inspectorAnalysis = "Condicion de borde del modelo OpenSees historico P1L3.\nReacciones disponibles por caso en el resumen global; no se inventa una reaccion nodal individual.";
            inspectorCapacity = "N/A: una restriccion nodal no tiene curva de capacidad P-M.";
            inspectorTraceability = $"Fuente: {p1l4Metadata.source}\nEstado: {p1l4Metadata.data_state}\nContrato: Assets/StreamingAssets/p1l4_structural_metadata.json";
            lastInfo = inspectorIdentity + "\n\n" + inspectorGeometry + "\n\nRESTRICCIONES\n" + inspectorProperties + "\n\n" + inspectorTraceability;
            if (infoText != null) infoText.text = lastInfo;
            lastSelected = ei;
            inspectorVisible = true;
            ClearSelectedDiagram();
            ClearSelectedLocalAxes();
        }

        void ClearSelectedLocalAxes()
        {
            foreach (var go in selectedLocalAxisObjects)
            {
                if (go == null) continue;
                if (registeredFloor.TryGetValue(go, out var priorFloor) && byFloor.TryGetValue(priorFloor, out var floorObjects))
                    floorObjects.Remove(go);
                registeredType.Remove(go);
                registeredFloor.Remove(go);
                if (Application.isPlaying) Destroy(go); else DestroyImmediate(go);
            }
            selectedLocalAxisObjects.Clear();
            if (byType.ContainsKey("selected_local_axes")) byType["selected_local_axes"].Clear();
        }

        void RebuildSelectedLocalAxes()
        {
            ClearSelectedLocalAxes();
            if (!localAxesVisible || lastSelected == null) return;
            string id = string.IsNullOrEmpty(lastSelected.humanId) ? lastSelected.id : lastSelected.humanId;
            var rows = MetadataForSelection(lastSelected, id);
            if (rows.Count == 0 || rows[0].local_axes == null) return;
            var item = rows[0];
            Vector3 start = (V(item.node_i_coord_m) + V(item.node_j_coord_m)) * 0.5f;
            CreateSelectedAxis(start, V(item.local_axes.x), Color.red, "x", item.floor);
            CreateSelectedAxis(start, V(item.local_axes.y), Color.green, "y", item.floor);
            CreateSelectedAxis(start, V(item.local_axes.z), Color.blue, "z", item.floor);
            typeVisible["selected_local_axes"] = true;
            ReapplyAll();
        }

        void CreateSelectedAxis(Vector3 start, Vector3 direction, Color color, string axisName, string floor)
        {
            var go = new GameObject("P1L4_LOCAL_AXIS_" + axisName);
            var line = go.AddComponent<LineRenderer>();
            line.useWorldSpace = false;
            line.positionCount = 2;
            line.SetPosition(0, start);
            line.SetPosition(1, start + direction.normalized * 2f);
            line.startWidth = 0.16f;
            line.endWidth = 0.05f;
            line.material = SeismicLineMat(color);
            Register(go, "selected_local_axes", floor ?? "");
            selectedLocalAxisObjects.Add(go);
        }

        void SetDiagramMode(int mode)
        {
            diagramMode = mode;
            diagram2DVisible = mode != 0;
            selectedDiagramMemberIndex = 0;
            RebuildSelectedDiagram();
        }

        void ClearSelectedDiagram()
        {
            foreach (var go in selectedDiagramObjects)
            {
                if (go == null) continue;
                if (registeredFloor.TryGetValue(go, out var priorFloor) && byFloor.TryGetValue(priorFloor, out var floorObjects))
                    floorObjects.Remove(go);
                registeredType.Remove(go);
                registeredFloor.Remove(go);
                if (Application.isPlaying) Destroy(go); else DestroyImmediate(go);
            }
            selectedDiagramObjects.Clear();
            if (byType.ContainsKey("analysis_diagram")) byType["analysis_diagram"].Clear();
        }

        void RebuildSelectedDiagram()
        {
            ClearSelectedDiagram();
            if (diagramMode == 0 || lastSelected == null)
            {
                diagramCaption = diagramMode == 0 ? "Diagramas: OFF" : "Diagramas: seleccione un elemento";
                return;
            }
            string id = string.IsNullOrEmpty(lastSelected.humanId) ? lastSelected.id : lastSelected.humanId;
            var results = ResultsForSelection(lastSelected, id);
            var metadata = MetadataForSelection(lastSelected, id);
            int component = diagramMode == 1 ? 4 : diagramMode == 2 ? 5 : diagramMode == 3 ? 0 : diagramMode == 4 ? 1 : 2;
            string componentName = diagramMode == 1 ? "My" : diagramMode == 2 ? "Mz" : diagramMode == 3 ? "N" : diagramMode == 4 ? "Vy" : "Vz";
            string units = diagramMode <= 2 ? "kN.m" : "kN";
            if (results.Count == 0 || metadata.Count == 0)
            {
                diagramCaption = $"{componentName}: N/A para {id} en {activeAnalysisCase}";
                return;
            }
            selectedDiagramMemberIndex = Mathf.Clamp(selectedDiagramMemberIndex, 0, results.Count - 1);
            var result = results[selectedDiagramMemberIndex];
            var end1 = DiagramForceVector(result, true);
            var end2 = DiagramForceVector(result, false);
            double maxAbs = 0.0;
            if (end1 != null && end1.Count > component) maxAbs = System.Math.Max(maxAbs, System.Math.Abs(end1[component] / 1000.0));
            if (end2 != null && end2.Count > component) maxAbs = System.Math.Max(maxAbs, System.Math.Abs(end2[component] / 1000.0));
            // Un cero presente en OpenSees es un resultado válido, no N/A.
            // En ese caso el diagrama coincide con el eje del miembro.
            float displayScale = maxAbs > 1.0e-12 ? 3.0f / (float)maxAbs : 0f;
            P1L4ElementMetadata meta = null;
            foreach (var candidate in metadata)
                if (candidate.analysis_id == result.analysis_id) { meta = candidate; break; }
            if (meta != null && end1 != null && end2 != null && end1.Count > component && end2.Count > component)
            {
                Vector3 p0 = V(meta.node_i_coord_m);
                Vector3 p1 = V(meta.node_j_coord_m);
                List<double> offsetAxis = diagramMode == 1 || diagramMode == 5 ? meta.local_axes.z : meta.local_axes.y;
                Vector3 axis = V(offsetAxis).normalized;
                float value0 = (float)(end1[component] / 1000.0);
                float value1 = (float)(end2[component] / 1000.0);
                var go = new GameObject($"P1L4_DIAG_{componentName}_{result.analysis_id}");
                var line = go.AddComponent<LineRenderer>();
                line.useWorldSpace = false;
                line.positionCount = 4;
                line.SetPosition(0, p0);
                line.SetPosition(1, p0 + axis * value0 * displayScale);
                line.SetPosition(2, p1 + axis * value1 * displayScale);
                line.SetPosition(3, p1);
                line.startWidth = 0.12f;
                line.endWidth = 0.12f;
                line.material = SeismicLineMat(value0 + value1 >= 0f ? new Color(1f, 0.75f, 0.1f) : new Color(0.25f, 0.95f, 1f));
                Register(go, "analysis_diagram", result.floor ?? "");
                selectedDiagramObjects.Add(go);
            }
            typeVisible["analysis_diagram"] = true;
            ReapplyAll();
            diagramCaption = $"{componentName} | {activeAnalysisCase} | {result.analysis_id} ({selectedDiagramMemberIndex + 1}/{results.Count}) | max |valor|={maxAbs:F2} {units} | END_FORCES_INTERPOLATION | sin cargas interiores";
        }

        List<double> ForceVector(AnalysisElementResult result, bool firstEnd)
        {
            if (result != null && !string.IsNullOrEmpty(result.analysis_id) && joseByAnalysisId.TryGetValue(result.analysis_id, out var jose))
            {
                return firstEnd
                    ? new List<double> { jose.N_end1, jose.Vy_end1, jose.Vz_end1, jose.T_end1, jose.My_end1, jose.Mz_end1 }
                    : new List<double> { jose.N_end2, jose.Vy_end2, jose.Vz_end2, jose.T_end2, jose.My_end2, jose.Mz_end2 };
            }
            return firstEnd ? result?.localForce_end1 : result?.localForce_end2;
        }

        List<double> DiagramForceVector(AnalysisElementResult result, bool firstEnd)
        {
            var raw = ForceVector(result, firstEnd);
            if (raw == null) return null;
            // OpenSees entrega acciones del elemento sobre cada nodo con caras opuestas.
            // Para un diagrama interno con una unica convencion de cara se conserva i
            // y se invierte j. Los valores crudos siguen visibles en el inspector.
            if (firstEnd) return raw;
            var commonFace = new List<double>(raw.Count);
            foreach (double value in raw) commonFace.Add(-value);
            return commonFace;
        }

        List<P1L4ElementMetadata> MetadataForSelection(ElementInfo ei, string id)
        {
            if (!p1l4MetadataByElementId.TryGetValue(id, out var all)) return new List<P1L4ElementMetadata>();
            if (ei == null || string.IsNullOrEmpty(ei.analysisId)) return all;
            var selectedRows = new List<P1L4ElementMetadata>();
            foreach (var item in all)
                if (item.analysis_id == ei.analysisId) selectedRows.Add(item);
            return selectedRows.Count > 0 ? selectedRows : all;
        }

        List<AnalysisElementResult> ResultsForSelection(ElementInfo ei, string id)
        {
            if (!analysisByElementId.TryGetValue(id, out var all)) return new List<AnalysisElementResult>();
            if (ei == null || string.IsNullOrEmpty(ei.analysisId)) return all;
            var selectedRows = new List<AnalysisElementResult>();
            foreach (var item in all)
                if (item.analysis_id == ei.analysisId) selectedRows.Add(item);
            return selectedRows.Count > 0 ? selectedRows : all;
        }

        string BuildP1L4IdentityText(ElementInfo ei, string id, string category, string source, string confidence)
        {
            var rows = MetadataForSelection(ei, id);
            var sb = new StringBuilder();
            sb.AppendLine($"element_id: {id}");
            sb.AppendLine($"Edificio: {(string.IsNullOrEmpty(ei.building) ? "N/A" : ei.building)}");
            sb.AppendLine($"Piso: {(string.IsNullOrEmpty(ei.floor) ? "N/A" : ei.floor)}");
            sb.AppendLine($"Tipo: {category}");
            if (rows.Count == 0)
            {
                sb.AppendLine("OpenSees elementTag: N/A");
                sb.AppendLine("analysis_id: N/A");
                sb.Append($"geometry tag: {(string.IsNullOrEmpty(ei.elementTag) ? "N/A" : ei.elementTag)}");
            }
            else
            {
                sb.AppendLine($"Miembros FE asociados: {rows.Count}");
                foreach (var item in rows)
                    sb.AppendLine($"- {item.analysis_id} | OpenSees {item.opensees_tag} | geom {item.geometry_elementTag}");
            }
            if (!string.IsNullOrEmpty(source)) sb.Append(source);
            if (!string.IsNullOrEmpty(confidence)) sb.Append(confidence);
            return sb.ToString().TrimEnd();
        }

        string BuildP1L4AnalysisText(ElementInfo ei, string id, string fallbackSection, string fallbackCoord)
        {
            var rows = MetadataForSelection(ei, id);
            if (ei.hasFEParticipationFlag && !ei.participatesInFE)
                return "No participa en el modelo FE (capa exclusivamente visual).";
            if (rows.Count == 0)
                return $"Sin metadatos FE.\nCoordenadas: {fallbackCoord}\nSeccion visual: {fallbackSection}\nMaterial visual: {ei.materialName}";
            var sb = new StringBuilder();
            sb.AppendLine($"Fuente: {p1l4Metadata.data_state}");
            foreach (var item in rows)
            {
                sb.AppendLine($"{item.analysis_id} / OpenSees {item.opensees_tag}");
                sb.AppendLine($"Nodos: {item.node_i} {FormatVector(item.node_i_coord_m)} m -> {item.node_j} {FormatVector(item.node_j_coord_m)} m");
                if (item.section != null)
                    sb.AppendLine($"Seccion {item.section_id}: y={item.section.dim_local_y_m:F3} m, z={item.section.dim_local_z_m:F3} m, A={item.section.A_m2:F4} m2");
                else sb.AppendLine("Seccion: N/A");
                if (p1l4Metadata.material != null)
                    sb.AppendLine($"Material {item.material_id}: {p1l4Metadata.material.model}, E={p1l4Metadata.material.E_pa / 1e9:F2} GPa");
                else sb.AppendLine("Material: N/A");
                if (item.local_axes != null)
                    sb.AppendLine($"Ejes locales: x={FormatVector(item.local_axes.x)}, y={FormatVector(item.local_axes.y)}, z={FormatVector(item.local_axes.z)}");
                else sb.AppendLine("Ejes locales: N/A");
                sb.AppendLine($"Restricciones nodo i: {SupportText(item.node_i)}");
                sb.AppendLine($"Restricciones nodo j: {SupportText(item.node_j)}");
            }
            return sb.ToString().TrimEnd();
        }

        string BuildP1L4ResultsText(ElementInfo ei, string id)
        {
            if (ei.hasFEParticipationFlag && !ei.participatesInFE)
                return $"CASO ACTIVO: {activeAnalysisCase}\nN/V/T/M: N/A (no participa en FE).";
            var rows = ResultsForSelection(ei, id);
            if (rows.Count == 0)
            {
                if (excludedByElementId.TryGetValue(id, out var excluded))
                    return $"CASO ACTIVO: {activeAnalysisCase}\nNo incluido en el resultado historico.\nMotivo: {excluded.reason}";
                return $"CASO ACTIVO: {activeAnalysisCase}\nN/V/T/M: N/A (sin correspondencia de resultados).";
            }
            var sb = new StringBuilder();
            sb.AppendLine($"CASO ACTIVO: {activeAnalysisCase}");
            sb.AppendLine($"Estado: {(p1l4Metadata == null ? "P1L3_ENTREGADO_HISTORICO" : p1l4Metadata.data_state)}");
            if (rows.Count > 1) sb.AppendLine($"Crosswalk 1:{rows.Count}; se listan miembros por separado, sin combinar esfuerzos.");
            foreach (var row in rows)
            {
                sb.AppendLine($"{row.analysis_id} | OpenSees {row.opensees_tag}");
                sb.AppendLine("Extremo i: " + FormatForces(ForceVector(row, true)));
                sb.AppendLine("Extremo j: " + FormatForces(ForceVector(row, false)));
                var ni = FindAnalysisNode(row.node_i);
                var nj = FindAnalysisNode(row.node_j);
                if (ni == null || nj == null) sb.AppendLine("Desplazamientos: N/A");
                else
                {
                    sb.AppendLine($"ui=({ni.ux_m:F6}, {ni.uy_m:F6}, {ni.uz_m:F6}) m");
                    sb.AppendLine($"uj=({nj.ux_m:F6}, {nj.uy_m:F6}, {nj.uz_m:F6}) m");
                }
            }
            int expectedCount = analysisResults != null && analysisResults.elements != null ? analysisResults.elements.Count : 0;
            sb.AppendLine($"Fuente integrada José: {joseForcesStatus} ({joseByAnalysisId.Count}/{expectedCount} miembros del caso cargados)");
            return sb.ToString().TrimEnd();
        }

        string BuildDemandCapacityText(string id)
        {
            if (!demandCapacityByElementId.TryGetValue(id, out var item))
                return "Este elemento no tiene contrato de demanda-capacidad P1L4.";
            string contractCase = (item.demand_capacity.@case ?? "").Replace("CASE_", "").ToUpperInvariant();
            var sb = new StringBuilder();
            sb.AppendLine($"Elemento: {item.element_id} | OpenSees {item.opensees_tag}");
            sb.AppendLine($"Curva: P-{item.demand_capacity.pm_axis} | Seccion: {item.section_id}");
            sb.AppendLine($"Caso de demanda: {item.demand_capacity.@case}");
            if (contractCase != activeAnalysisCase)
            {
                sb.AppendLine($"CASO ACTIVO {activeAnalysisCase}: punto de demanda N/A.");
                sb.AppendLine("Cambie a R para mostrar el punto verificado por Luis.");
            }
            else
            {
                sb.AppendLine($"P = {item.demand_capacity.P_kN:F2} kN");
                sb.AppendLine($"{item.demand_capacity.pm_axis} = {item.demand_capacity.M_kNm:F2} kN.m");
                sb.AppendLine($"Capacidad interpolada |M| = {item.demand_capacity.interpolated_capacity_M_abs_kNm:F2} kN.m");
                sb.AppendLine("Estado: " + (item.demand_capacity.inside_envelope ? "DENTRO" : "FUERA"));
            }
            int valid = 0;
            int total = item.capacity != null && item.capacity.points != null ? item.capacity.points.Count : 0;
            if (item.capacity != null && item.capacity.points != null)
                foreach (var point in item.capacity.points) if (point.valid) valid++;
            sb.AppendLine($"Puntos P-M validos: {valid}/{total}");
            if (item.type == "wall") sb.AppendLine("Armadura: ASUMIDO_LAB");
            if (item.capacity != null && !string.IsNullOrEmpty(item.capacity.note)) sb.Append(item.capacity.note);
            return sb.ToString().TrimEnd();
        }

        string BuildTraceabilityText(ElementInfo ei, string id, string diagnosticLine)
        {
            var rows = MetadataForSelection(ei, id);
            var sb = new StringBuilder();
            sb.AppendLine($"Objeto Unity: {ei.go.name}");
            sb.AppendLine($"geometry element_id: {id}");
            if (rows.Count == 0) sb.AppendLine("OpenSees elementTag / analysis_id: N/A");
            else foreach (var item in rows) sb.AppendLine($"OpenSees {item.opensees_tag} -> {item.analysis_id} -> {item.geometry_elementTag}");
            sb.AppendLine($"Resultados: {(p1l4Metadata == null ? "Assets/StreamingAssets/analysis_cases.json" : p1l4Metadata.source)}");
            if (demandCapacityByElementId.TryGetValue(id, out var dc) && dc.traceability != null)
            {
                sb.AppendLine($"Demanda: {dc.traceability.demand_source}");
                sb.AppendLine($"Seccion capacidad: {dc.traceability.capacity_section_config}");
                sb.AppendLine($"Capacidad: {dc.traceability.capacity_source}");
            }
            else sb.AppendLine("Capacidad: N/A");
            if (!string.IsNullOrEmpty(diagnosticLine)) sb.Append(diagnosticLine);
            if (!string.IsNullOrEmpty(ei.physicalClassification))
            {
                sb.AppendLine();
                sb.AppendLine("CONTEXTO FÍSICO POST-P1L3 (no ejecutado)");
                sb.AppendLine($"Cluster: {ei.physicalCluster}");
                sb.AppendLine($"Geometría: {ei.physicalClassification}");
                sb.AppendLine($"Soporte físico: {ei.physicalSupport}");
                sb.AppendLine($"FE principal: {ei.mainFeParticipation}");
                sb.AppendLine($"Diagnóstico revisado: {ei.revisedDiagnostic}");
                sb.AppendLine($"Duplicado: {ei.duplicateClassification}");
                sb.AppendLine($"Evidencia: {ei.physicalEvidence}");
            }
            return sb.ToString().TrimEnd();
        }

        string SupportText(int nodeTag)
        {
            if (!p1l4SupportsByNode.TryGetValue(nodeTag, out var support)) return "libre / sin apoyo registrado";
            return $"UX={FixedText(support.UX)} UY={FixedText(support.UY)} UZ={FixedText(support.UZ)} RX={FixedText(support.RX)} RY={FixedText(support.RY)} RZ={FixedText(support.RZ)}";
        }

        static string FixedText(bool value) => value ? "FIJO" : "LIBRE";

        static string FormatVector(List<double> values)
        {
            if (values == null || values.Count < 3) return "N/A";
            return $"({values[0]:F3}, {values[1]:F3}, {values[2]:F3})";
        }

        static string FormatForces(List<double> values)
        {
            if (values == null || values.Count < 6) return "N=N/A, Vy=N/A, Vz=N/A, T=N/A, My=N/A, Mz=N/A";
            return $"N={values[0] / 1000.0:F3} kN, Vy={values[1] / 1000.0:F3} kN, Vz={values[2] / 1000.0:F3} kN, " +
                $"T={values[3] / 1000.0:F3} kN.m, My={values[4] / 1000.0:F3} kN.m, Mz={values[5] / 1000.0:F3} kN.m";
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
            DrawP1L4Header();
            DrawDiagramControls();
            DrawDiagnosticControls();
            DrawControls();
            DrawP1L3Panel();
            if (labelsVisible) DrawLabels();
            if (seismic != null) DrawSeismicValueLabels();
            DrawPhysicalContextLabels();
            DrawLegend();
            DrawElementDiagram2D();
            DrawExpandedGraph();
            DrawDemandCapacityPlot();
        }

        void DrawDiagramControls()
        {
            float width = 570f;
            float x = (Screen.width - width) * 0.5f;
            Rect r = new Rect(x, 142f, width, 58f);
            GUI.Box(r, "");
            GUI.DrawTexture(r, MakeTex(2, 2, new Color(0.015f, 0.035f, 0.07f, 0.93f)));
            string[] labels = { "OFF", "My", "Mz", "N", "Vy", "Vz" };
            for (int i = 0; i < labels.Length; i++)
            {
                var button = new GUIStyle(GUI.skin.button);
                if (diagramMode == i) button.normal.textColor = new Color(0.25f, 1f, 0.5f);
                if (GUI.Button(new Rect(r.x + 7 + i * 55f, r.y + 5, 50f, 22f), labels[i], button)) SetDiagramMode(i);
            }
            bool axes = GUI.Toggle(new Rect(r.x + 344, r.y + 6, 105, 20), localAxesVisible, "Ejes x/y/z");
            if (axes != localAxesVisible)
            {
                localAxesVisible = axes;
                RebuildSelectedLocalAxes();
            }
            bool plot2D = GUI.Toggle(new Rect(r.x + 452, r.y + 6, 105, 20), diagram2DVisible, "Gráfico 2D");
            if (plot2D != diagram2DVisible) diagram2DVisible = plot2D;
            var text = new GUIStyle(GUI.skin.label);
            text.fontSize = 10; text.normal.textColor = new Color(0.9f, 0.94f, 1f); text.wordWrap = false;
            GUI.Label(new Rect(r.x + 7, r.y + 31, r.width - 14, 20), diagramCaption, text);
        }

        void DrawElementDiagram2D()
        {
            if (!diagram2DVisible || diagramMode == 0 || lastSelected == null) return;
            string id = string.IsNullOrEmpty(lastSelected.humanId) ? lastSelected.id : lastSelected.humanId;
            var rows = ResultsForSelection(lastSelected, id);
            if (rows.Count == 0) return;
            selectedDiagramMemberIndex = Mathf.Clamp(selectedDiagramMemberIndex, 0, rows.Count - 1);
            var row = rows[selectedDiagramMemberIndex];
            int component = diagramMode == 1 ? 4 : diagramMode == 2 ? 5 : diagramMode == 3 ? 0 : diagramMode == 4 ? 1 : 2;
            string componentName = diagramMode == 1 ? "My" : diagramMode == 2 ? "Mz" : diagramMode == 3 ? "N" : diagramMode == 4 ? "Vy" : "Vz";
            string units = diagramMode <= 2 ? "kN.m" : "kN";
            var end1 = DiagramForceVector(row, true);
            var end2 = DiagramForceVector(row, false);
            if (end1 == null || end2 == null || end1.Count <= component || end2.Count <= component) return;
            double v0 = end1[component] / 1000.0;
            double v1 = end2[component] / 1000.0;
            double maxAbs = System.Math.Max(1.0e-9, System.Math.Max(System.Math.Abs(v0), System.Math.Abs(v1)));

            float width = Mathf.Min(700f, Screen.width - 420f);
            float height = Mathf.Min(390f, Screen.height - 250f);
            Rect panel = new Rect((Screen.width - width) * 0.5f, 210f, width, height);
            GUI.Box(panel, "");
            GUI.DrawTexture(panel, MakeTex(2, 2, new Color(0.01f, 0.02f, 0.045f, 0.98f)));
            var title = new GUIStyle(GUI.skin.label);
            title.fontSize = 15; title.fontStyle = FontStyle.Bold; title.normal.textColor = Color.white;
            GUI.Label(new Rect(panel.x + 14, panel.y + 9, panel.width - 60, 24), $"{componentName} 2D | caso {activeAnalysisCase} | {id}", title);
            if (GUI.Button(new Rect(panel.xMax - 44, panel.y + 7, 32, 25), "X")) { diagram2DVisible = false; return; }

            if (rows.Count > 1)
            {
                if (GUI.Button(new Rect(panel.x + 14, panel.y + 38, 34, 22), "<"))
                {
                    selectedDiagramMemberIndex = (selectedDiagramMemberIndex - 1 + rows.Count) % rows.Count;
                    RebuildSelectedDiagram();
                    return;
                }
                GUI.Label(new Rect(panel.x + 54, panel.y + 39, 260, 20), $"Miembro FE {selectedDiagramMemberIndex + 1}/{rows.Count}: {row.analysis_id}");
                if (GUI.Button(new Rect(panel.x + 315, panel.y + 38, 34, 22), ">"))
                {
                    selectedDiagramMemberIndex = (selectedDiagramMemberIndex + 1) % rows.Count;
                    RebuildSelectedDiagram();
                    return;
                }
            }
            else GUI.Label(new Rect(panel.x + 14, panel.y + 39, 330, 20), $"Miembro FE: {row.analysis_id} | OpenSees {row.opensees_tag}");

            Rect plot = new Rect(panel.x + 72, panel.y + 78, panel.width - 102, panel.height - 150);
            float zeroY = plot.center.y;
            DrawGuiLine(new Vector2(plot.x, zeroY), new Vector2(plot.xMax, zeroY), new Color(0.78f, 0.82f, 0.9f), 2f);
            DrawGuiLine(new Vector2(plot.x, plot.y), new Vector2(plot.x, plot.yMax), Color.white, 2f);
            float scale = (plot.height * 0.42f) / (float)maxAbs;
            Vector2 p0 = new Vector2(plot.x, zeroY - (float)v0 * scale);
            Vector2 p1 = new Vector2(plot.xMax, zeroY - (float)v1 * scale);
            Color curve = new Color(0.2f, 0.95f, 0.65f);
            DrawGuiLine(new Vector2(plot.x, zeroY), p0, new Color(curve.r, curve.g, curve.b, 0.55f), 1f);
            DrawGuiLine(p0, p1, curve, 4f);
            DrawGuiLine(p1, new Vector2(plot.xMax, zeroY), new Color(curve.r, curve.g, curve.b, 0.55f), 1f);
            GUI.color = curve;
            GUI.DrawTexture(new Rect(p0.x - 5, p0.y - 5, 10, 10), whiteTex);
            GUI.DrawTexture(new Rect(p1.x - 5, p1.y - 5, 10, 10), whiteTex);
            GUI.color = Color.white;

            var label = new GUIStyle(GUI.skin.label);
            label.fontSize = 11; label.normal.textColor = new Color(0.93f, 0.96f, 1f); label.wordWrap = true;
            GUI.Label(new Rect(plot.x - 18, plot.yMax + 5, 100, 20), "x=0", label);
            GUI.Label(new Rect(plot.xMax - 72, plot.yMax + 5, 90, 20), "x=L", label);
            GUI.Label(new Rect(plot.x + 5, p0.y - 24, 180, 20), $"i: {v0:F3} {units}", label);
            GUI.Label(new Rect(plot.xMax - 190, p1.y - 24, 185, 20), $"j: {v1:F3} {units}", label);
            double minValue = System.Math.Min(v0, v1);
            double maxValue = System.Math.Max(v0, v1);
            string minAt = v0 <= v1 ? "i (x=0)" : "j (x=L)";
            string maxAt = v0 >= v1 ? "i (x=0)" : "j (x=L)";
            GUI.Label(new Rect(panel.x + 360, panel.y + 39, panel.width - 374, 34), $"mín={minValue:F3} {units} @ {minAt}\nmáx={maxValue:F3} {units} @ {maxAt}", label);
            GUI.Label(new Rect(panel.x + 14, panel.yMax - 70, panel.width - 28, 60),
                $"DATOS: fuerzas de extremos OpenSees ({joseForcesStatus}); acciones locales i/j.\nREPRESENTACIÓN: END_FORCES_INTERPOLATION; extremo j convertido a cara interna común. CARGA INTERIOR: ninguna; G/Q/EX/EY/R se aplicaron como cargas nodales. Recta coherente por equilibrio del miembro FE, sin inventar estaciones.", label);
        }

        void DrawP1L4Header()
        {
            float width = 390f;
            float x = (Screen.width - width) * 0.5f;
            Rect r = new Rect(x, 10f, width, 94f);
            GUI.Box(r, "");
            GUI.DrawTexture(r, MakeTex(2, 2, new Color(0.015f, 0.035f, 0.07f, 0.95f)));
            var title = new GUIStyle(GUI.skin.label);
            title.fontSize = 13; title.fontStyle = FontStyle.Bold; title.normal.textColor = Color.white;
            GUI.Label(new Rect(r.x + 8, r.y + 4, 150, 20), "P1L4 | RESULTADOS", title);
            GUI.Label(new Rect(r.x + 160, r.y + 4, 220, 20), "CASO ACTIVO: " + activeAnalysisCase, title);
            string[] names = { "G", "Q", "EX", "EY", "R" };
            for (int i = 0; i < names.Length; i++)
            {
                var button = new GUIStyle(GUI.skin.button);
                if (activeAnalysisCase == names[i]) button.normal.textColor = new Color(0.25f, 1f, 0.5f);
                if (GUI.Button(new Rect(r.x + 8 + i * 75f, r.y + 29, 68f, 26f), names[i], button))
                    ActivateAnalysisCase(names[i]);
            }
            bool show = GUI.Toggle(new Rect(r.x + 8, r.y + 61, 112, 22), activeDeformationVisible, "Deformada");
            if (show != activeDeformationVisible)
            {
                activeDeformationVisible = show;
                typeVisible["analysis_deformed"] = show;
                ReapplyAll();
            }
            GUI.Label(new Rect(r.x + 122, r.y + 62, 44, 20), "Factor");
            float newScale = GUI.HorizontalSlider(new Rect(r.x + 165, r.y + 68, 130, 18), activeDeformationScale, 1f, 250f);
            if (Mathf.Abs(newScale - activeDeformationScale) > 0.25f)
            {
                activeDeformationScale = newScale;
                RebuildActiveDeformedShape();
            }
            GUI.Label(new Rect(r.x + 300, r.y + 62, 48, 20), $"x{activeDeformationScale:F0}");
            if (GUI.Button(new Rect(r.x + 350, r.y + 60, 32, 24), "OFF"))
            {
                activeDeformationVisible = false;
                typeVisible["analysis_deformed"] = false;
                ReapplyAll();
            }
        }

        void DrawDiagnosticControls()
        {
            Rect r = new Rect(10f, 10f, 250f, 207f);
            GUI.Box(r, "");
            GUI.DrawTexture(r, MakeTex(2, 2, new Color(0.02f, 0.04f, 0.08f, 0.94f)));
            var title = new GUIStyle(GUI.skin.label);
            title.fontSize = 12; title.fontStyle = FontStyle.Bold; title.normal.textColor = Color.white;
            var small = new GUIStyle(GUI.skin.label);
            small.fontSize = 10; small.normal.textColor = new Color(0.86f, 0.9f, 1f);
            GUI.Label(new Rect(r.x + 8, r.y + 4, 234, 18), "Datos integrados", title);
            GUI.Label(new Rect(r.x + 8, r.y + 22, 234, 32),
                "Geometria: POST-P1L3 ACTUAL\nResultados: P1L3 ENTREGADO (historico)", small);

            GUI.Label(new Rect(r.x + 8, r.y + 55, 234, 18), "Vista estructural", title);
            string[] modes = { "Geometria", "FE", "Ambos" };
            for (int i = 0; i < modes.Length; i++)
            {
                string label = diagnosticViewMode == i ? "● " + modes[i] : modes[i];
                if (GUI.Button(new Rect(r.x + 8 + i * 78, r.y + 74, 74, 22), label))
                {
                    diagnosticViewMode = i;
                    diagnosticColorsVisible = i != 0;
                    typeVisible["fe_candidate"] = i != 0;
                    ReapplyAll();
                }
            }
            bool colors = GUI.Toggle(new Rect(r.x + 8, r.y + 99, 116, 19), diagnosticColorsVisible, "Diagnostico por color");
            if (colors != diagnosticColorsVisible) { diagnosticColorsVisible = colors; ReapplyAll(); }
            bool problems = GUI.Toggle(new Rect(r.x + 128, r.y + 99, 114, 19), diagnosticProblemsOnly, "Solo problemas FE");
            if (problems != diagnosticProblemsOnly) { diagnosticProblemsOnly = problems; ReapplyAll(); }

            bool walls = GUI.Toggle(new Rect(r.x + 8, r.y + 120, 70, 19), diagnosticWalls, "Muros");
            bool beams = GUI.Toggle(new Rect(r.x + 82, r.y + 120, 70, 19), diagnosticBeams, "Vigas");
            bool columns = GUI.Toggle(new Rect(r.x + 156, r.y + 120, 82, 19), diagnosticColumns, "Columnas");
            bool ed2 = GUI.Toggle(new Rect(r.x + 8, r.y + 140, 100, 19), diagnosticEd2Only, "Solo EDIFICIO_2");
            if (walls != diagnosticWalls || beams != diagnosticBeams || columns != diagnosticColumns || ed2 != diagnosticEd2Only)
            {
                diagnosticWalls = walls; diagnosticBeams = beams; diagnosticColumns = columns; diagnosticEd2Only = ed2;
                ReapplyAll();
            }

            var green = new GUIStyle(small); green.normal.textColor = DiagnosticColor("CONNECTED_EXPECTED");
            var blue = new GUIStyle(small); blue.normal.textColor = DiagnosticColor("FREE_END_EXPECTED");
            var red = new GUIStyle(small); red.normal.textColor = DiagnosticColor("DISCONNECTED_ERROR");
            var yellow = new GUIStyle(small); yellow.normal.textColor = DiagnosticColor("UNRESOLVED");
            GUI.Label(new Rect(r.x + 8, r.y + 161, 113, 18), "● Conectado esperado", green);
            GUI.Label(new Rect(r.x + 126, r.y + 161, 116, 18), "● Extremo libre", blue);
            GUI.Label(new Rect(r.x + 8, r.y + 179, 113, 18), "● Error desconectado", red);
            GUI.Label(new Rect(r.x + 126, r.y + 179, 116, 18), "● No resuelto", yellow);
            if (feDiagnostic != null && feDiagnostic.summary != null)
                GUI.Label(new Rect(r.x + 8, r.y + 195, 234, 14),
                    $"Candidato no ejecutado | {feDiagnostic.summary.focus_elements} revisados", small);
        }

        Rect DeliveryRect()
        {
            float width = Mathf.Clamp(Screen.width - 40f, 360f, 920f);
            float x = (Screen.width - width) * 0.5f;
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
                if (GUI.Button(new Rect(Screen.width * 0.5f - 90f, 110f, 180f, 26f), "Referencia P1L3", button)) deliveryPanelVisible = true;
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
            float gap = 8f;
            float cardW = (body.width - gap) * 0.5f;
            float cardH = Mathf.Min(112f, (body.height - 58f) * 0.5f);
            DrawSummaryCard(new Rect(body.x, body.y, cardW, cardH), "A | Carga viva", g.status,
                $"{g.panel_count} panos\nQ = {g.Q_transferred_kN:F2} kN\nConservacion: {g.Q_conservation_rel_error:E2}", text, pass);
            DrawSummaryCard(new Rect(body.x + cardW + gap, body.y, cardW, cardH), "B | Sismo EX/EY", s.status,
                $"C = {100.0 * s.base_shear_coefficient:F1}% g\nV_EX = {s.base_shear_EX_kN:F2} kN\nV_EY = {s.base_shear_EY_kN:F2} kN", text, pass);
            DrawSummaryCard(new Rect(body.x, body.y + cardH + gap, cardW, cardH), "C | Superposicion", p.status,
                $"R={p.lambda_G:F1}G+{p.lambda_Q:F1}Q+{p.lambda_EX:F1}EX+{p.lambda_EY:F1}EY\nError u: {p.displacement_rel_error:E2}\nError f: {p.internal_force_rel_error:E2}", text, pass);
            DrawSummaryCard(new Rect(body.x + cardW + gap, body.y + cardH + gap, cardW, cardH), "D | Capacidad HA", "DISPONIBLE",
                "Fiber Section 0.70 x 0.70 m\nM-phi e interaccion P-M\nGraficos ampliables", text, pass);
            float wy = body.y + body.height - 48;
            GUI.Label(new Rect(body.x, wy, body.width, 46),
                "MODELO PROVISIONAL: la geometria/carga tributaria aun es parcial y las deformaciones globales no deben interpretarse como una validacion final del edificio.", warning);
        }

        void DrawSummaryCard(Rect rect, string heading, string status, string detail, GUIStyle text, GUIStyle pass)
        {
            GUI.Box(rect, "");
            GUI.DrawTexture(rect, MakeTex(2, 2, new Color(0.035f, 0.065f, 0.12f, 0.96f)));
            var headingStyle = new GUIStyle(pass); headingStyle.fontSize = 13;
            GUI.Label(new Rect(rect.x + 9, rect.y + 6, rect.width - 100, 20), heading, headingStyle);
            GUI.Label(new Rect(rect.x + rect.width - 98, rect.y + 6, 90, 20), status, pass);
            GUI.Label(new Rect(rect.x + 9, rect.y + 29, rect.width - 18, rect.height - 34), detail, text);
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
            GUI.Label(new Rect(body.x, body.y, body.width, 20),
                $"Columna analizada: {capacity.mapped_element_id} -> {capacity.mapped_analysis_id} | mapeo {capacity.mapping_status}", pass);
            string[] fields = {
                $"SECCION\n{capacity.b_m:F2} x {capacity.h_m:F2} m",
                $"MATERIALES\nf'c {capacity.fc_pa / 1e6:F0} MPa | fy {capacity.fy_pa / 1e6:F0} MPa",
                $"REFUERZO\n{capacity.num_bars} O{capacity.bar_diameter_m * 1000.0:F0} mm | r={capacity.cover_m * 1000.0:F0} mm",
                $"FIBRAS\n{capacity.num_fibers_y} x {capacity.num_fibers_z}"
            };
            float fieldW = (body.width - 12f) / 4f;
            for (int i = 0; i < fields.Length; i++)
            {
                Rect fr = new Rect(body.x + i * (fieldW + 4f), body.y + 23f, fieldW, 43f);
                GUI.Box(fr, "");
                GUI.Label(new Rect(fr.x + 5, fr.y + 2, fr.width - 10, fr.height - 4), fields[i], text);
            }
            float gap = 8f;
            float imageW = (body.width - gap * 2f) / 3f;
            float imageY = body.y + 72;
            float imageH = Mathf.Min(166f, body.height - 126f);
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

        void DrawLegend()
        {
            bool arrows = typeVisible.ContainsKey("seismic_arrow") && typeVisible["seismic_arrow"];
            bool torsion = typeVisible.ContainsKey("seismic_torsion") && typeVisible["seismic_torsion"];
            bool deformEX = typeVisible.ContainsKey("seismic_deform_ex") && typeVisible["seismic_deform_ex"];
            bool deformEY = typeVisible.ContainsKey("seismic_deform_ey") && typeVisible["seismic_deform_ey"];
            bool deform = deformEX || deformEY;
            bool tributary = typeVisible.ContainsKey("tributary") && typeVisible["tributary"];
            if (!arrows && !torsion && !deform && !tributary) return;
            float h = legendExpanded ? 116f : 28f;
            Rect r = new Rect(Screen.width - 250f, Screen.height - h - 10f, 240f, h);
            GUI.Box(r, "");
            GUI.DrawTexture(r, MakeTex(2, 2, new Color(0.015f, 0.025f, 0.05f, 0.9f)));
            if (GUI.Button(new Rect(r.x + 6, r.y + 4, r.width - 12, 22), legendExpanded ? "Leyenda ▼" : "Leyenda ▲")) legendExpanded = !legendExpanded;
            if (!legendExpanded) return;
            var label = new GUIStyle(GUI.skin.label); label.fontSize = 11;
            float y = r.y + 31f;
            if (arrows || deform)
            {
                label.normal.textColor = new Color(1f, 0.35f, 0.25f); GUI.Label(new Rect(r.x + 10, y, 100, 18), "Rojo = EX", label);
                label.normal.textColor = new Color(0.35f, 0.6f, 1f); GUI.Label(new Rect(r.x + 118, y, 100, 18), "Azul = EY", label); y += 19f;
            }
            if (torsion) { label.normal.textColor = new Color(1f, 0.35f, 0.7f); GUI.Label(new Rect(r.x + 10, y, 210, 18), "Magenta = torsion", label); y += 19f; }
            if (tributary) { label.normal.textColor = new Color(1f, 0.85f, 0.25f); GUI.Label(new Rect(r.x + 10, y, 210, 18), "Tributarias: escala de carga", label); y += 19f; }
            if (deform)
            {
                label.normal.textColor = Color.white;
                GUI.Label(new Rect(r.x + 10, y, 220, 18), $"Deformada OpenSees: EX x{deformationScaleEX:F1}, EY x{deformationScaleEY:F1}", label);
            }
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
            bool hasDemandCapacity = demandCapacityByElementId.ContainsKey(toCopy);
            float copyWidth = hasDemandCapacity ? (r.width - 30) * 0.5f : r.width - 20;
            if (GUI.Button(new Rect(r.x + 10, r.y + 94, copyWidth, 24), "Copiar ID: " + toCopy))
                GUIUtility.systemCopyBuffer = toCopy;
            if (hasDemandCapacity && GUI.Button(new Rect(r.x + 15 + copyWidth, r.y + 94, copyWidth, 24), "Grafico P-M"))
                demandCapacityPlotVisible = true;

            float contentHeight = 1400f;
            infoScroll = GUI.BeginScrollView(new Rect(r.x + 8, r.y + 124, r.width - 16, r.height - 132), infoScroll, new Rect(0, 0, r.width - 40, contentHeight));
            float sy = 2f;
            DrawInspectorSection(ref sy, "IDENTIDAD", ref inspectorGeometryOpen, inspectorGeometry, r.width - 42, lbl);
            DrawInspectorSection(ref sy, "ANALISIS", ref inspectorPropertiesOpen, inspectorProperties, r.width - 42, lbl);
            DrawInspectorSection(ref sy, "RESULTADOS | " + activeAnalysisCase, ref inspectorAnalysisOpen, inspectorAnalysis, r.width - 42, lbl);
            DrawInspectorSection(ref sy, "CARGAS / TRIBUTARIAS", ref inspectorTributaryOpen, inspectorTributary, r.width - 42, lbl);
            DrawInspectorSection(ref sy, "DEMANDA-CAPACIDAD", ref inspectorCapacityOpen, inspectorCapacity, r.width - 42, lbl);
            DrawInspectorSection(ref sy, "TRAZABILIDAD", ref inspectorTraceabilityOpen, inspectorTraceability, r.width - 42, lbl);
            GUI.EndScrollView();
        }

        void DrawDemandCapacityPlot()
        {
            if (!demandCapacityPlotVisible || lastSelected == null) return;
            string id = string.IsNullOrEmpty(lastSelected.humanId) ? lastSelected.id : lastSelected.humanId;
            if (!demandCapacityByElementId.TryGetValue(id, out var item) || item.capacity == null || item.capacity.points == null)
            {
                demandCapacityPlotVisible = false;
                return;
            }
            float width = Mathf.Min(660f, Screen.width - 80f);
            float height = Mathf.Min(500f, Screen.height - 80f);
            Rect panel = new Rect((Screen.width - width) * 0.5f, (Screen.height - height) * 0.5f, width, height);
            GUI.Box(panel, "");
            GUI.DrawTexture(panel, MakeTex(2, 2, new Color(0.01f, 0.02f, 0.045f, 0.98f)));
            var title = new GUIStyle(GUI.skin.label);
            title.fontSize = 15; title.fontStyle = FontStyle.Bold; title.normal.textColor = Color.white;
            GUI.Label(new Rect(panel.x + 14, panel.y + 9, panel.width - 70, 24), $"P-M | {item.element_id} | eje {item.capacity.pm_axis}", title);
            if (GUI.Button(new Rect(panel.xMax - 44, panel.y + 7, 32, 25), "X")) { demandCapacityPlotVisible = false; return; }

            Rect plot = new Rect(panel.x + 70, panel.y + 48, panel.width - 100, panel.height - 122);
            DrawGuiLine(new Vector2(plot.x, plot.yMax), new Vector2(plot.xMax, plot.yMax), Color.white, 2f);
            DrawGuiLine(new Vector2(plot.x, plot.yMax), new Vector2(plot.x, plot.y), Color.white, 2f);
            var valid = new List<DemandCapacityPoint>();
            double maxM = System.Math.Abs(item.demand_capacity.M_kNm);
            double maxP = item.demand_capacity.compression_magnitude_kN;
            foreach (var point in item.capacity.points)
            {
                maxM = System.Math.Max(maxM, System.Math.Abs(point.M_kNm));
                maxP = System.Math.Max(maxP, point.compression_magnitude_kN);
                if (point.valid) valid.Add(point);
            }
            maxM = System.Math.Max(maxM, 1.0);
            maxP = System.Math.Max(maxP, 1.0);
            valid.Sort((a, b) => a.compression_magnitude_kN.CompareTo(b.compression_magnitude_kN));
            Vector2 previous = Vector2.zero;
            bool hasPrevious = false;
            foreach (var point in valid)
            {
                Vector2 pos = PlotPoint(plot, System.Math.Abs(point.M_kNm), point.compression_magnitude_kN, maxM, maxP);
                if (hasPrevious) DrawGuiLine(previous, pos, new Color(0.2f, 0.95f, 0.55f), 3f);
                GUI.color = new Color(0.2f, 0.95f, 0.55f);
                GUI.DrawTexture(new Rect(pos.x - 4, pos.y - 4, 8, 8), whiteTex);
                GUI.color = Color.white;
                previous = pos;
                hasPrevious = true;
            }
            foreach (var point in item.capacity.points)
            {
                if (point.valid) continue;
                Vector2 pos = PlotPoint(plot, System.Math.Abs(point.M_kNm), point.compression_magnitude_kN, maxM, maxP);
                DrawGuiLine(pos + new Vector2(-4, -4), pos + new Vector2(4, 4), Color.gray, 1f);
                DrawGuiLine(pos + new Vector2(-4, 4), pos + new Vector2(4, -4), Color.gray, 1f);
            }
            string contractCase = (item.demand_capacity.@case ?? "").Replace("CASE_", "").ToUpperInvariant();
            if (contractCase == activeAnalysisCase)
            {
                Vector2 demand = PlotPoint(plot, item.demand_capacity.M_abs_kNm, item.demand_capacity.compression_magnitude_kN, maxM, maxP);
                GUI.color = Color.red;
                GUI.DrawTexture(new Rect(demand.x - 6, demand.y - 6, 12, 12), whiteTex);
                GUI.color = Color.white;
            }
            var label = new GUIStyle(GUI.skin.label);
            label.fontSize = 11; label.normal.textColor = new Color(0.92f, 0.95f, 1f); label.wordWrap = true;
            GUI.Label(new Rect(plot.x, plot.yMax + 5, plot.width, 20), $"|M| [kN.m]   max={maxM:F1}", label);
            GUI.Label(new Rect(panel.x + 8, plot.y, 60, 50), $"|P|\n[kN]\n{maxP:F1}", label);
            string demandText = contractCase == activeAnalysisCase
                ? $"Demanda {item.demand_capacity.@case}: P={item.demand_capacity.P_kN:F2} kN, {item.demand_capacity.pm_axis}={item.demand_capacity.M_kNm:F2} kN.m — {(item.demand_capacity.inside_envelope ? "DENTRO" : "FUERA")}"
                : $"CASO ACTIVO {activeAnalysisCase}: punto de demanda N/A; la demanda disponible corresponde a {item.demand_capacity.@case}.";
            GUI.Label(new Rect(panel.x + 14, panel.yMax - 58, panel.width - 28, 44), demandText + (item.type == "wall" ? "\nArmadura: ASUMIDO_LAB" : ""), label);
        }

        static Vector2 PlotPoint(Rect plot, double moment, double compression, double maxMoment, double maxCompression)
        {
            float x = plot.x + (float)(moment / maxMoment) * plot.width;
            float y = plot.yMax - (float)(compression / maxCompression) * plot.height;
            return new Vector2(x, y);
        }

        static void DrawGuiLine(Vector2 start, Vector2 end, Color color, float width)
        {
            Matrix4x4 previousMatrix = GUI.matrix;
            Color previousColor = GUI.color;
            float angle = Mathf.Atan2(end.y - start.y, end.x - start.x) * Mathf.Rad2Deg;
            float length = Vector2.Distance(start, end);
            GUIUtility.RotateAroundPivot(angle, start);
            GUI.color = color;
            GUI.DrawTexture(new Rect(start.x, start.y - width * 0.5f, length, width), whiteTex);
            GUI.matrix = previousMatrix;
            GUI.color = previousColor;
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
            if (!visibilityPanelVisible)
            {
                if (GUI.Button(new Rect(10, 225, 150, 28), "Abrir visibilidad")) visibilityPanelVisible = true;
                return;
            }
            Rect controls = ControlsRect();
            float lx = controls.x;
            float ly = controls.y;
            GUI.Box(controls, "");
            GUI.DrawTexture(controls, MakeTex(2, 2, new Color(0.02f, 0.04f, 0.08f, 0.92f)));
            var sect = new GUIStyle(GUI.skin.label);
            sect.fontSize = 12; sect.fontStyle = FontStyle.Bold; sect.normal.textColor = Color.white;

            GUI.Label(new Rect(lx + 8, ly + 4, 240, 18), "Visibilidad rapida", sect);
            if (GUI.Button(new Rect(lx + 218, ly + 3, 24, 20), "X")) { visibilityPanelVisible = false; return; }
            bool newLabels = GUI.Toggle(new Rect(lx + 8, ly + 25, 116, 20), labelsVisible, "Textos / IDs");
            if (newLabels != labelsVisible) labelsVisible = newLabels;
            QuickTypeToggle(new Rect(lx + 128, ly + 25, 116, 20), "Tributarias", "tributary", "tributary_point");
            QuickTypeToggle(new Rect(lx + 8, ly + 47, 116, 20), "Apoyos FE", "p1l4_support");
            QuickTypeToggle(new Rect(lx + 128, ly + 47, 116, 20), "Flechas EX/EY", "seismic_arrow");
            QuickTypeToggle(new Rect(lx + 8, ly + 69, 116, 20), "Deformada EX", "seismic_deform_ex");
            QuickTypeToggle(new Rect(lx + 128, ly + 69, 116, 20), "Centros masa", "seismic_cm");
            QuickTypeToggle(new Rect(lx + 8, ly + 91, 116, 20), "Deformada EY", "seismic_deform_ey");
            QuickTypeToggle(new Rect(lx + 128, ly + 91, 116, 20), "Masa / peso", "seismic_mass");
            QuickTypeToggle(new Rect(lx + 8, ly + 113, 116, 20), "Corte basal", "seismic_shear");
            QuickTypeToggle(new Rect(lx + 128, ly + 113, 116, 20), "Torsion", "seismic_torsion");
            QuickTypeToggle(new Rect(lx + 8, ly + 135, 116, 20), "Patron sismico", "seismic_pattern");
            QuickTypeToggle(new Rect(lx + 128, ly + 135, 116, 20), "Cargas 700", "p1l4_load_surface", "p1l4_load_line");

            GUI.Label(new Rect(lx + 8, ly + 161, 240, 18), "Arquitectura (solo visual)", sect);
            QuickTypeToggle(new Rect(lx + 8, ly + 181, 116, 20), "Losa arq. P4", "architectural_slab");
            QuickTypeToggle(new Rect(lx + 128, ly + 181, 116, 20), "Borde arq. P4", "architectural_slab_edge");

            GUI.Label(new Rect(lx + 8, ly + 206, 240, 18), "Pisos (S = mostrar solo)", sect);
            var floors = SortedFloors();
            float floorX = lx + 8;
            float floorY = ly + 227;
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
                case "p1l4_support":
                case "architectural_slab":
                case "architectural_slab_edge":
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
            diagnosticViewMode = 0;
            diagnosticColorsVisible = false;
            diagnosticProblemsOnly = false;
            diagnosticWalls = true;
            diagnosticBeams = true;
            diagnosticColumns = true;
            diagnosticEd2Only = false;
            activeDeformationVisible = false;
            if (typeVisible.ContainsKey("analysis_deformed")) typeVisible["analysis_deformed"] = false;
            diagramMode = 0;
            diagram2DVisible = false;
            selectedDiagramMemberIndex = 0;
            diagramCaption = "Diagramas: seleccione un elemento";
            ClearSelectedDiagram();
            localAxesVisible = false;
            ClearSelectedLocalAxes();
            deliveryPanelVisible = false;
            expandedGraph = null;
            expandedGraphTitle = "";
            uiHidden = false;
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
                "beam", "column", "wall", "slab", "support", "slab_edge", "diaphragm",
                "p1l4_support",
                "architectural_slab", "architectural_slab_edge", "tributary",
                "seismic_arrow", "seismic_cm", "seismic_mass", "seismic_shear",
                "seismic_torsion", "seismic_deform_ex", "seismic_deform_ey"
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

        void RunDiagnosticSelfCheck()
        {
            var failures = new List<string>();
            if (feDiagnostic == null || feDiagnostic.summary == null) failures.Add("contrato FE ausente");
            else
            {
                if (feDiagnostic.summary.focus_elements != 72) failures.Add("foco distinto de 72");
                if (feDiagnostic.members == null || feDiagnostic.members.Count != feDiagnostic.summary.fe_element_count)
                    failures.Add("miembros FE no coinciden con resumen");
                if (feDiagnostic.summary.geometry_elements_split_into_multiple_fe <= 0)
                    failures.Add("crosswalk 1:N ausente");
            }
            if (!byType.ContainsKey("fe_candidate") || byType["fe_candidate"].Count == 0)
                failures.Add("malla FE no construida");

            bool oldFeType = typeVisible.ContainsKey("fe_candidate") && typeVisible["fe_candidate"];
            diagnosticViewMode = 1;
            typeVisible["fe_candidate"] = true;
            ReapplyAll();
            if (!byType.ContainsKey("fe_candidate") || !byType["fe_candidate"].Exists(go => go.activeSelf))
                failures.Add("modo FE no visible");
            diagnosticProblemsOnly = true;
            ReapplyAll();
            foreach (var info in allElements)
            {
                if (info == null || info.go == null || !info.go.activeSelf) continue;
                if (info.diagnosticStatus != "DISCONNECTED_ERROR" && info.diagnosticStatus != "UNRESOLVED")
                {
                    failures.Add("filtro solo problemas deja elementos ajenos");
                    break;
                }
            }
            diagnosticViewMode = 0;
            diagnosticProblemsOnly = false;
            typeVisible["fe_candidate"] = oldFeType;
            ReapplyAll();
            if (failures.Count == 0)
                Debug.Log("[UI QA] PASS: diagnostico FE, filtros y crosswalk 1:N disponibles.");
            else
                Debug.LogError("[UI QA] FAIL diagnostico FE: " + string.Join(", ", failures));
        }

        void RunP1L4SelfCheck()
        {
            var failures = new List<string>();
            if (p1l4Metadata == null) failures.Add("metadata ausente");
            else
            {
                if (p1l4Metadata.elements == null || p1l4Metadata.elements.Count == 0) failures.Add("elementos metadata ausentes");
                if (p1l4Metadata.supports == null || p1l4Metadata.supports.Count == 0) failures.Add("apoyos ausentes");
                if (!byType.ContainsKey("p1l4_support") || byType["p1l4_support"].Count != p1l4Metadata.supports.Count)
                    failures.Add("simbolos de apoyo no coinciden con metadata");
                if (p1l4Metadata.cases == null || p1l4Metadata.cases.Count != 5) failures.Add("casos distintos de G/Q/EX/EY/R");
                if (p1l4Metadata.qa == null || !p1l4Metadata.qa.all_nodes_exist || !p1l4Metadata.qa.all_local_axes_unit_and_orthogonal)
                    failures.Add("QA de nodos/ejes locales no valido");
            }
            if (demandCapacity == null || demandCapacity.validation == null || demandCapacity.validation.status != "PASS")
                failures.Add("demanda-capacidad ausente o invalida");
            else if (demandCapacity.elements == null || demandCapacity.elements.Count < 2)
                failures.Add("faltan columna/muro de demanda-capacidad");
            if (!demandCapacityByElementId.ContainsKey("E2-P1-C-002") || !demandCapacityByElementId.ContainsKey("E2-P1-M-019"))
                failures.Add("IDs de estudio no mapeados");
            if (p1l4LoadCatalog == null || p1l4LoadCatalog.entry_count != 108 || p1l4LoadCatalog.is_structurally_applied)
                failures.Add("catalogo de cargas auditadas ausente o mal rotulado");
            int expectedJoseElements = analysisResults != null && analysisResults.elements != null ? analysisResults.elements.Count : 0;
            if (joseByAnalysisId.Count != expectedJoseElements || joseForcesStatus != "P1L3_ENTREGADO_HISTORICO")
                failures.Add($"export Jose caso {activeAnalysisCase} incompleto o mal rotulado ({joseByAnalysisId.Count}/{expectedJoseElements}, {joseForcesStatus})");
            if (joseDisplacementByNode.Count != 813)
                failures.Add($"desplazamientos Jose incompletos ({joseDisplacementByNode.Count}/813)");
            if (joseSupports == null || joseSupports.supports == null || joseSupports.supports.Count != 106)
                failures.Add("apoyos Jose incompletos");
            if (physicalContext == null || physicalContext.classifications == null || physicalContext.classifications.Count != 40)
                failures.Add("contexto fisico ausente o incompleto");
            else
            {
                if (physicalContext.participates_in_FE || physicalContext.opensees_changed || physicalContext.historical_results_changed)
                    failures.Add("contexto fisico altera FE o resultados");
                if (physicalContext.clusters == null || physicalContext.clusters.Count != 3)
                    failures.Add("clusters de contexto fisico incompletos");
                if (!byType.ContainsKey("physical_context") || byType["physical_context"].Count == 0)
                    failures.Add("capa visual de contexto fisico no construida");
                if (typeVisible.ContainsKey("physical_context") && typeVisible["physical_context"])
                    failures.Add("contexto fisico debe iniciar apagado");
            }
            if (failures.Count == 0)
                Debug.Log($"[P1L4 QA] PASS: metadata={p1l4Metadata.elements.Count}, Jose={joseByAnalysisId.Count}, apoyos={p1l4Metadata.supports.Count}, casos={p1l4Metadata.cases.Count}, demanda-capacidad={demandCapacity.elements.Count}, contexto-fisico={physicalContext.classifications.Count}, diagramas-2D=My/Mz/N/Vy/Vz.");
            else
                Debug.LogError("[P1L4 QA] FAIL: " + string.Join(", ", failures));
        }

        /// <summary>
        /// Recorre programáticamente la misma cadena usada en la defensa en vivo.
        /// No altera resultados ni guarda la escena; deja el caso R y una viga con My visible.
        /// </summary>
        public void RunP1L4DemoSequenceCheck()
        {
            var failures = new List<string>();
            ElementInfo beam = null;
            foreach (var candidate in allElements)
            {
                if (candidate == null || candidate.category != "beam") continue;
                string candidateId = string.IsNullOrEmpty(candidate.humanId) ? candidate.id : candidate.humanId;
                if (candidateId == "E2-P1-V-056" && analysisByElementId.ContainsKey(candidateId) && p1l4MetadataByElementId.ContainsKey(candidateId))
                {
                    beam = candidate;
                    break;
                }
            }
            if (beam == null) failures.Add("viga E2-P1-V-056 no encontrada");
            else
            {
                ShowInfo(beam);
                localAxesVisible = true;
                RebuildSelectedLocalAxes();
                if (selectedLocalAxisObjects.Count != 3) failures.Add("ejes locales de viga no disponibles");
                foreach (var caseName in new[] { "G", "Q", "EX", "EY", "R" })
                {
                    ActivateAnalysisCase(caseName);
                    string beamId = string.IsNullOrEmpty(beam.humanId) ? beam.id : beam.humanId;
                    var rows = ResultsForSelection(beam, beamId);
                    if (rows.Count == 0 || joseByAnalysisId.Count != 1312) failures.Add($"caso {caseName} sin resultados integrados");
                }
                foreach (var mode in new[] { 1, 2, 3, 4, 5 })
                {
                    SetDiagramMode(mode);
                    if (selectedDiagramObjects.Count == 0 || !diagram2DVisible)
                        failures.Add($"diagrama modo {mode} no disponible");
                }
                SetDiagramMode(1);
                if (!diagramCaption.Contains("END_FORCES_INTERPOLATION") || !diagramCaption.Contains("sin cargas interiores"))
                    failures.Add("clasificacion fisica del diagrama no visible");
                string auditedBeamId = string.IsNullOrEmpty(beam.humanId) ? beam.id : beam.humanId;
                var auditedRows = ResultsForSelection(beam, auditedBeamId);
                if (auditedRows.Count != 1) failures.Add("E2-P1-V-056 no tiene un unico miembro FE historico");
                else
                {
                    var rawJ = ForceVector(auditedRows[0], false);
                    var diagramJ = DiagramForceVector(auditedRows[0], false);
                    if (rawJ == null || diagramJ == null || rawJ.Count != diagramJ.Count)
                        failures.Add("vectores i/j de E2-P1-V-056 no disponibles");
                    else
                        for (int index = 0; index < rawJ.Count; index++)
                            if (System.Math.Abs(rawJ[index] + diagramJ[index]) > 1e-9)
                                failures.Add("conversion de j a cara interna comun invalida");
                }
            }

            ElementInfo oneToMany = null;
            foreach (var candidate in allElements)
            {
                if (candidate == null) continue;
                string candidateId = string.IsNullOrEmpty(candidate.humanId) ? candidate.id : candidate.humanId;
                if (diagnosticByElementId.TryGetValue(candidateId, out var diagnostic) &&
                    diagnostic.crosswalk != null && diagnostic.crosswalk.Count > 1)
                {
                    oneToMany = candidate;
                    break;
                }
            }
            if (oneToMany == null) failures.Add("elemento crosswalk 1:N candidato no seleccionable");
            else
            {
                ShowInfo(oneToMany);
                if (oneToMany.crosswalk == null || oneToMany.crosswalk.Count < 2)
                    failures.Add("trazabilidad crosswalk 1:N candidata sin miembros multiples");
            }

            ActivateAnalysisCase("R");
            foreach (var target in new[] { "E2-P1-C-002", "E2-P1-M-019" })
            {
                ElementInfo selectedInfo = null;
                foreach (var candidate in allElements)
                {
                    string candidateId = candidate == null ? "" : (string.IsNullOrEmpty(candidate.humanId) ? candidate.id : candidate.humanId);
                    if (candidateId == target) { selectedInfo = candidate; break; }
                }
                if (selectedInfo == null) failures.Add(target + " no seleccionable");
                else
                {
                    ShowInfo(selectedInfo);
                    string capacityText = BuildDemandCapacityText(target);
                    if (!capacityText.Contains("Estado:")) failures.Add(target + " sin inside/outside");
                    if (target.EndsWith("M-019") && !capacityText.Contains("ASUMIDO_LAB")) failures.Add("muro sin nota ASUMIDO_LAB");
                }
            }
            if (!byType.ContainsKey("p1l4_support") || byType["p1l4_support"].Count != 106) failures.Add("apoyos globales no disponibles");
            if (!byType.ContainsKey("tributary") || byType["tributary"].Count == 0) failures.Add("tributarias globales no disponibles");
            int loadCount = (byType.ContainsKey("p1l4_load_surface") ? byType["p1l4_load_surface"].Count : 0) +
                (byType.ContainsKey("p1l4_load_line") ? byType["p1l4_load_line"].Count : 0);
            if (loadCount != 82) failures.Add($"cargas globales visibles {loadCount}/82");

            if (beam != null)
            {
                ShowInfo(beam);
                SetDiagramMode(1);
                diagram2DVisible = true;
                activeDeformationVisible = true;
                if (typeVisible.ContainsKey("analysis_deformed")) typeVisible["analysis_deformed"] = true;
                ReapplyAll();
            }
            if (failures.Count == 0)
                Debug.Log("[P1L4 DEMO QA] PASS: E2-P1-V-056 identidad/ejes/R/fuerzas/cara-interna/deformada/My-2D/N-V-2D; crosswalk 1:N candidato trazable; COLUMNA P-M/demanda; MURO P-M/ASUMIDO_LAB; GLOBAL cargas/apoyos/tributarias.");
            else Debug.LogError("[P1L4 DEMO QA] FAIL: " + string.Join(", ", failures));
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
            var occupiedCells = new HashSet<string>();
            int drawnCount = 0;
            float cellW = orbitDist > 110f ? 105f : 72f;
            float cellH = orbitDist > 110f ? 28f : 20f;
            foreach (var ei in allElements)
            {
                if (ei.go == null || !ei.go.activeInHierarchy) continue;
                if (ei.isSeismic || ei.category == "node" || ei.category == "axis" || ei.category == "cad_reference" || (ei.category ?? "").StartsWith("tributary")) continue;
                Vector3 cp = transform.TransformPoint(ei.nodeI + (ei.nodeJ - ei.nodeI) * 0.5f);
                Vector3 sp = cam.WorldToScreenPoint(cp);
                if (sp.z <= 0) continue;
                sp.y = sh - sp.y;
                if (sp.x < 0 || sp.x > sw || sp.y < 0 || sp.y > sh) continue;
                bool selectedElement = lastSelected == ei;
                string cell = Mathf.FloorToInt(sp.x / cellW) + ":" + Mathf.FloorToInt(sp.y / cellH);
                if (!selectedElement && (occupiedCells.Contains(cell) || drawnCount >= 220)) continue;
                occupiedCells.Add(cell);
                GUI.Label(new Rect(sp.x - 30, sp.y - 8, 80, 16), ShortTag(ei.id), ls);
                drawnCount++;
            }
        }

        private readonly List<Label2D> _physicalContextLabels = new List<Label2D>();

        void DrawPhysicalContextLabels()
        {
            if (cam == null || !typeVisible.ContainsKey("physical_context") || !typeVisible["physical_context"]) return;
            GUIStyle style = new GUIStyle(GUI.skin.box);
            style.fontSize = 11;
            style.fontStyle = FontStyle.Bold;
            style.alignment = TextAnchor.MiddleCenter;
            foreach (var label in _physicalContextLabels)
            {
                Vector3 world = transform.TransformPoint(new Vector3(label.x, label.y, label.z));
                Vector3 screen = cam.WorldToScreenPoint(world);
                if (screen.z <= 0) continue;
                screen.y = Screen.height - screen.y;
                style.normal.textColor = label.color;
                GUI.Label(new Rect(screen.x - 115, screen.y - 12, 230, 24), label.text, style);
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
            if (visibilityPanelVisible) occupied.Add(ControlsRect());
            occupied.Add(new Rect(Screen.width - 260f, 10f, 250f, 196f));
            if (lastSelected != null && inspectorVisible) occupied.Add(InspectorRect());
            if (deliveryPanelVisible) occupied.Add(DeliveryRect());
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

        static Vector3 SegmentPoint(SegmentData segment, int index)
        {
            if (segment.points_flat != null && segment.points_flat.Count >= index * 3 + 3)
                return new Vector3((float)segment.points_flat[index * 3], (float)segment.points_flat[index * 3 + 1], (float)segment.points_flat[index * 3 + 2]);
            return segment.points != null && segment.points.Count > index ? V(segment.points[index]) : Vector3.zero;
        }

        static Vector3 DiaphragmPoint(DiaphragmData diaphragm, int index)
        {
            if (diaphragm.points_flat != null && diaphragm.points_flat.Count >= index * 3 + 3)
                return new Vector3((float)diaphragm.points_flat[index * 3], (float)diaphragm.points_flat[index * 3 + 1], (float)diaphragm.points_flat[index * 3 + 2]);
            return diaphragm.points != null && diaphragm.points.Count > index ? V(diaphragm.points[index]) : Vector3.zero;
        }

        static string P(Vector3 v) => "(" + v.x.ToString("F3") + ", " + v.y.ToString("F3") + ", " + v.z.ToString("F3") + ")";

        static Material LineMaterial(Color color)
        {
            if (MaterialsByCat.TryGetValue("axis", out var axisMat) && axisMat != null)
            {
                var instance = UnityEngine.Object.Instantiate(axisMat);
                instance.color = color;
                return instance;
            }
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
        public double visualAreaM2;
        public string confidence;
        public bool participatesInFE;
        public bool hasFEParticipationFlag;
        public Color baseColor;
        public Material baseMat;
        public bool isHighlighted = false;
        public bool isSeismic = false;
        public double seismicForceKN;
        public string seismicCase;
        public bool isFeCandidateVisual;
        public bool isP1L4Support;
        public int supportNodeTag;
        public bool fixUX;
        public bool fixUY;
        public bool fixUZ;
        public bool fixRX;
        public bool fixRY;
        public bool fixRZ;
        public bool isP1L4Load;
        public string loadType;
        public double loadValue;
        public string loadUnit;
        public string loadApplicationStatus;
        public string loadReceiverStatus;
        public string loadReceiverIds;
        public string analysisId;
        public int openseesTag;
        public string diagnosticStatus;
        public string structuralClassification;
        public string diagnosticMotive;
        public string diagnosticComponent;
        public string expectedConnection;
        public string diagnosticEvidence;
        public string diagnosticSource;
        public List<FeCrosswalkEntry> crosswalk;
        public string physicalCluster;
        public string physicalClassification;
        public string physicalSupport;
        public string mainFeParticipation;
        public string revisedDiagnostic;
        public string duplicateClassification;
        public string physicalEvidence;
    }
}
