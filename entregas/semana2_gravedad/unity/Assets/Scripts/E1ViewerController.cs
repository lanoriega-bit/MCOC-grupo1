using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using UnityEngine;
using UnityEngine.EventSystems;

namespace Mcoc.Semana2.UnityE1
{
    public class E1ViewerController : MonoBehaviour
    {
        private const float FloorHeight = 3.96f;
        private const float BeamWidth = 0.24f;
        private const float BeamDepth = 0.36f;
        private const float SlabVisualThickness = 0.08f;
        private const float GuiWidth = 390f;
        private const float InspectorWidth = 520f;
        private const float GuiPickPadding = 20f;
        private const float VerifiedDisplacementLimitFactor = 1.10f;
        private const float VerifiedDeformationScale = 20f;
        private const string StubStatusStub = "SEGMENTATION_STUB_ARTIFACT";

        private static readonly Dictionary<int, float> FloorElevations = new Dictionary<int, float>
        {
            { -1, 3.96f },
            { 1, 7.92f },
            { 2, 11.88f },
            { 3, 15.84f },
            { 4, 19.80f },
        };

        private readonly List<E1ElementView> views = new List<E1ElementView>();
        private readonly Dictionary<string, E1ElementView> elementById = new Dictionary<string, E1ElementView>(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, E1NodeInfo> nodesByKey = new Dictionary<string, E1NodeInfo>();
        private readonly Dictionary<string, E1NodeInfo> nodesById = new Dictionary<string, E1NodeInfo>(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, List<E1ElementView>> tributariesByBeam = new Dictionary<string, List<E1ElementView>>(StringComparer.OrdinalIgnoreCase);

        private E1GravityData data;
        private Camera cam;
        private GameObject root;
        private GameObject labelsRoot;
        private GameObject axesRoot;
        private string activeBuildingFilter = "Both";
        private readonly Dictionary<GameObject, string> responseVisualBuilding = new Dictionary<GameObject, string>();
        private Bounds modelBounds;
        private Vector3 orbitTarget = Vector3.zero;
        private Vector2 lastMouse;
        private Vector2 mouseDown;
        private bool draggingOrbit;
        private bool draggingPan;
        private int nodeIndex;
        private int floorIndex;
        private Vector2 leftPanelScroll;
        private Vector2 inspectorScroll;
        private string searchText = "";
        private string statusText = "Cargando...";
        private string selectionText = "Selecciona una viga, nodo, losa, tributaria o blocker.";
        private string selectedId = "";
        private string selectedBeamId = "";

        private bool showNodes = true;
        private bool showBeams = true;
        private bool showColumns = true;
        private bool showWalls = true;
        private bool showSupports = true;
        private bool showDiaphragms = true;
        private bool showIds;
        private bool showLocalAxes;
        private bool showTributaryAreas;
        private bool showSlabs = true;
        private bool showBlockers;
        private bool showLoads;

        private bool showResponsePanel = true;
        private bool showDeformed;
        private bool showDeformedBlocked;
        private bool showDiagrams;
        private bool showNDiagram;
        private bool showVyDiagram;
        private bool showVzDiagram;
        private bool showTDiagram;
        private bool showMyDiagram;
        private bool showMzDiagram;
        private bool showBlockerHighlight;

        private bool showUnmatched;
        private bool showScoping;
        private bool showFloatingStubs;
        private bool showVisualOnly = true;
        private bool showInterfaceIssues;

        private readonly string[] floorOptions = { "ALL", "1S", "P1", "P2", "P3", "P4" };

        private Material beamMaterial;
        private Material slabMaterial;
        private Material nodeMaterial;
        private Material tributaryMaterial;
        private Material selectedTributaryMaterial;
        private Material blockerMaterial;
        private Material columnMaterial;
        private Material wallMaterial;
        private Material supportMaterial;
        private Material diaphragmMaterial;
        private Material genericMaterial;
        private Material lineMaterial;
        private Material localXMaterial;
        private Material localYMaterial;
        private Material localZMaterial;
        private Material verifiedMaterial;
        private Material floatingMaterial;
        private Material scopingMaterial;
        private Material deformedMaterial;
        private Material deformedBlockedMaterial;
        private Material diagramMaterial;
        private Material diagramScopingMaterial;
        private Material selectedMaterial;
        private Material loadArrowMaterial;

        private E1StructuralResponse responseData;
        private E1StructuralMappingCoverage mappingData;
        private bool responseLoaded;

        private readonly Dictionary<string, E1ResponseElement> responseElementById = new Dictionary<string, E1ResponseElement>(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, E1ElementForcesResponse> responseForcesById = new Dictionary<string, E1ElementForcesResponse>(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, E1StructuralElementMapping> structuralElementMappingByVisualId = new Dictionary<string, E1StructuralElementMapping>(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, E1StructuralSupportMapping> structuralSupportMappingByVisualId = new Dictionary<string, E1StructuralSupportMapping>(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, E1StructuralNodeMapping> structuralNodeMappingByVisualId = new Dictionary<string, E1StructuralNodeMapping>(StringComparer.OrdinalIgnoreCase);

        private readonly List<GameObject> deformedLines = new List<GameObject>();
        private readonly List<GameObject> deformedBlockedLines = new List<GameObject>();
        private readonly List<GameObject> diagramLines = new List<GameObject>();
        private readonly List<GameObject> selectedLoadLines = new List<GameObject>();
        private readonly Dictionary<int, List<LineRenderer>> diagramRenderersByKind = new Dictionary<int, List<LineRenderer>>();

        private float responseDeformScale = 1f;
        private Vector2 responseScroll;
        private bool responsePanelScroll;
        private E1ElementView selectedView;
        private bool leftPanelCollapsed;
        private bool inspectorCollapsed;
        private int inspectorTab;
        private readonly string[] inspectorTabs = { "Properties", "Loads", "Forces", "Displacements", "Diagrams" };
        private readonly Dictionary<Renderer, Material> originalMaterialByRenderer = new Dictionary<Renderer, Material>();
        private bool prevShowDeformed;
        private bool prevShowDeformedBlocked;
        private bool prevShowDiagrams;
        private bool prevShowBlockerHighlight;

        private void Start()
        {
            EnsureCameraAndLight();
            CreateMaterials();
            LoadAndBuild();
        }

        private void Update()
        {
            HandleCamera();
            if (Input.GetKeyDown(KeyCode.F)) FrameAll();
            HandleResponseToggles();
        }

        private void HandleResponseToggles()
        {
            if (!responseLoaded) return;
            bool deformChanged = false;
            bool blockHighlightOn = false;

            if (showDeformed != prevShowDeformed) { prevShowDeformed = showDeformed; deformChanged = true; }
            if (showDeformedBlocked != prevShowDeformedBlocked) { prevShowDeformedBlocked = showDeformedBlocked; deformChanged = true; }
            if (showDiagrams != prevShowDiagrams) { prevShowDiagrams = showDiagrams; deformChanged = true; }
            if (showBlockerHighlight != prevShowBlockerHighlight)
            {
                bool wasOn = prevShowBlockerHighlight;
                prevShowBlockerHighlight = showBlockerHighlight;
                blockHighlightOn = showBlockerHighlight && !wasOn;
            }

            if (deformChanged) BuildResponseVisualizations();
            if (blockHighlightOn) ApplyBlockerHighlight();
            if (deformChanged || blockHighlightOn || !showBlockerHighlight) ApplyResponseVisualVisibility();
        }

        private void LateUpdate()
        {
            if (cam == null || labelsRoot == null) return;
            foreach (Transform label in labelsRoot.transform)
            {
                Vector3 forward = label.position - cam.transform.position;
                if (forward.sqrMagnitude < 0.0001f) continue;
                label.rotation = Quaternion.LookRotation(forward, Vector3.up);
            }
        }

        private void OnGUI()
        {
            DrawLeftControlPanel();
            DrawSelectedInspector();
            if (showInterfaceIssues) DrawInterfaceIssuesOverlay();
        }

        private void DrawInterfaceIssuesOverlay()
        {
            Color original = GUI.backgroundColor;
            GUI.backgroundColor = new Color(0.60f, 0.45f, 0.00f);
            GUILayout.BeginArea(new Rect(Screen.width - 330f, 10f, 320f, 60f));
            GUILayout.BeginVertical(GUI.skin.window);
            GUILayout.Label("INTERFACE ISSUES");
            GUILayout.Label("E1 and E2 share site coordinates but are NOT connected");
            GUILayout.Label("in this FE contract (interface: " +
                (responseData != null && responseData.global_qa != null ? Dash(responseData.global_qa.interface_status) : "unknown") + ").");
            GUILayout.EndVertical();
            GUILayout.EndArea();
            GUI.backgroundColor = original;
        }

        private void DrawLeftControlPanel()
        {
            if (leftPanelCollapsed)
            {
                GUILayout.BeginArea(new Rect(10, 10, 150, 46), "Controls", GUI.skin.window);
                if (GUILayout.Button("Expand")) leftPanelCollapsed = false;
                GUILayout.EndArea();
                return;
            }

            float height = Mathf.Max(220f, Screen.height - 20f);
            string panelTitle = IsMultiBuilding ? "E12 Global / Controls" : "E1 Global / Controls";
            GUILayout.BeginArea(new Rect(10, 10, GuiWidth, height), panelTitle, GUI.skin.window);
            leftPanelScroll = GUILayout.BeginScrollView(leftPanelScroll, GUILayout.Width(GuiWidth - 10f), GUILayout.Height(height - 32f));
            GUILayout.Label(statusText);
            GUILayout.Space(4);

            if (responseLoaded) DrawGlobalQaPanel();

            GUILayout.Space(4);
            SectionHeader("MODEL");
            GUILayout.Label("Piso");
            int nextFloor = GUILayout.SelectionGrid(floorIndex, floorOptions, 3);
            if (nextFloor != floorIndex)
            {
                floorIndex = nextFloor;
                ApplyVisibility();
            }

            bool changed = false;
            changed |= Toggle(ref showNodes, "Nodes");
            changed |= Toggle(ref showBeams, "Beams");
            changed |= Toggle(ref showColumns, "Columns");
            changed |= Toggle(ref showWalls, "Walls");
            changed |= Toggle(ref showSupports, "Supports");
            changed |= Toggle(ref showDiaphragms, "Diaphragms");
            changed |= Toggle(ref showSlabs, "Slabs");
            changed |= Toggle(ref showBlockers, "L101 / Blockers");
            changed |= Toggle(ref showIds, "IDs");
            if (changed) ApplyVisibility();

            if (IsMultiBuilding)
            {
                GUILayout.Space(4);
                SectionHeader("BUILDINGS");
                int buildingIndex = string.Equals(activeBuildingFilter, "E1") ? 0 : string.Equals(activeBuildingFilter, "E2") ? 1 : 2;
                int nextBuilding = GUILayout.SelectionGrid(buildingIndex, new[] { "Building 1 (E1)", "Building 2 (E2)", "Both" }, 3);
                if (nextBuilding != buildingIndex)
                {
                    activeBuildingFilter = nextBuilding == 0 ? "E1" : nextBuilding == 1 ? "E2" : "Both";
                    ApplyVisibility();
                }
            }

            GUILayout.Space(4);
            SectionHeader("LOADS");
            changed = false;
            changed |= Toggle(ref showTributaryAreas, "Tributary Areas");
            changed |= Toggle(ref showLoads, "Loads (selected only)");
            if (changed)
            {
                ApplyVisibility();
                RebuildSelectedLoadVisuals();
            }

            GUILayout.Space(4);
            SectionHeader("STRUCTURAL RESPONSE");
            if (responseLoaded)
            {
                changed = false;
                changed |= Toggle(ref showDeformed, "Deformed Shape (verified)");
                changed |= Toggle(ref showDeformedBlocked, "Deformed Shape (blocked/scoping)");
                changed |= Toggle(ref showNDiagram, "N diagram (selected)");
                changed |= Toggle(ref showVyDiagram, "Vy diagram (selected)");
                changed |= Toggle(ref showVzDiagram, "Vz diagram (selected)");
                changed |= Toggle(ref showTDiagram, "T diagram (selected)");
                changed |= Toggle(ref showMyDiagram, "My diagram (selected)");
                changed |= Toggle(ref showMzDiagram, "Mz diagram (selected)");
                changed |= Toggle(ref showBlockerHighlight, "Blocker Highlight");
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "Deformation scale: {0:F0}x", responseDeformScale));
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "Max verified displacement: {0:F6} m", VerifiedMaxDisplacement()));
                if (showDeformedBlocked)
                {
                    GUILayout.Label("WARNING: blocked/scoping deformation is not physically verified.");
                    GUILayout.Space(2);
                    GUILayout.Label("Unverified overlays (need master on):");
                    changed |= Toggle(ref showUnmatched, "Show unmatched");
                    changed |= Toggle(ref showScoping, "Show scoping");
                    changed |= Toggle(ref showFloatingStubs, "Show floating/stubs");
                    changed |= Toggle(ref showVisualOnly, "Show visual-only");
                    if (IsMultiBuilding) changed |= Toggle(ref showInterfaceIssues, "Show interface issues");
                }
                showDiagrams = AnyDiagramToggleOn();
                if (changed) HandleResponseToggles();
            }
            else
            {
                GUILayout.Label("Structural response JSON not loaded.");
            }

            GUILayout.Space(4);
            SectionHeader("VIEW");
            changed = false;
            changed |= Toggle(ref showLocalAxes, "Local Axes");
            if (changed) ApplyVisibility();

            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Frame/Reset View")) FrameAll();
            if (GUILayout.Button("Clear selection")) ClearSelection();
            GUILayout.EndHorizontal();
            if (GUILayout.Button("Collapse panel")) leftPanelCollapsed = true;

            GUILayout.Space(4);
            GUILayout.Label("Search ID");
            GUILayout.BeginHorizontal();
            searchText = GUILayout.TextField(searchText);
            if (GUILayout.Button("Ir", GUILayout.Width(52))) SearchById(searchText);
            GUILayout.EndHorizontal();
            GUILayout.Label("Selected: " + (selectedView != null ? selectedView.category + " " + selectedView.id : "none"));
            GUILayout.EndScrollView();
            GUILayout.EndArea();
        }

        private void DrawSelectedInspector()
        {
            if (selectedView == null || string.IsNullOrEmpty(selectedId)) return;

            float width = Mathf.Min(InspectorWidth, Mathf.Max(320f, Screen.width - GuiWidth - 60f));
            float height = Mathf.Min(720f, Mathf.Max(260f, Screen.height - 20f));
            float x = Mathf.Max(GuiWidth + 30f, Screen.width - width - 10f);
            Rect rect = new Rect(x, 10f, width, inspectorCollapsed ? 68f : height);
            GUILayout.BeginArea(rect, "Selected Element Inspector", GUI.skin.window);

            GUILayout.BeginHorizontal();
            GUILayout.Label("SELECTED: " + selectedView.category.ToUpperInvariant() + " | " + selectedView.id + " | " + FloorLabel(selectedView.floorId));
            if (GUILayout.Button(inspectorCollapsed ? "Expand" : "Collapse", GUILayout.Width(82f))) inspectorCollapsed = !inspectorCollapsed;
            if (GUILayout.Button("Close", GUILayout.Width(54f))) { ClearSelection(); GUILayout.EndHorizontal(); GUILayout.EndArea(); return; }
            GUILayout.EndHorizontal();

            if (inspectorCollapsed)
            {
                GUILayout.EndArea();
                return;
            }

            string selectedStatus = AnalysisStatusForView(selectedView);
            GUILayout.Label(FriendlyAnalysisStatus(selectedStatus));
            GUILayout.Label("Internal status: " + selectedStatus);
            GUILayout.Label("Reason: " + MappingReasonForView(selectedView));
            inspectorTab = GUILayout.SelectionGrid(inspectorTab, inspectorTabs, inspectorTabs.Length);
            inspectorScroll = GUILayout.BeginScrollView(inspectorScroll, GUILayout.ExpandHeight(true));

            if (inspectorTab == 4)
            {
                GUILayout.TextArea(InspectorText(selectedView, inspectorTab), GUILayout.MinHeight(120f));
                DrawInspectorMiniDiagrams(selectedView);
            }
            else
            {
                GUILayout.TextArea(InspectorText(selectedView, inspectorTab), GUILayout.ExpandHeight(true));
            }

            GUILayout.EndScrollView();
            GUILayout.EndArea();
        }

        private void SectionHeader(string text)
        {
            GUILayout.Label("--- " + text + " ---");
        }

        private bool Toggle(ref bool value, string label)
        {
            bool next = GUILayout.Toggle(value, label);
            bool changed = next != value;
            value = next;
            return changed;
        }

        private bool AnyDiagramToggleOn()
        {
            return showNDiagram || showVyDiagram || showVzDiagram || showTDiagram || showMyDiagram || showMzDiagram;
        }

        private void DrawGlobalQaPanel()
        {
            if (responseData == null || responseData.global_qa == null) return;
            E1GlobalQa qa = responseData.global_qa;
            bool pass = string.Equals(qa.status, "PASS", StringComparison.OrdinalIgnoreCase);
            bool combined = qa.TOTAL_applied_gravity_kN.HasValue || qa.E1_applied_gravity_kN.HasValue || qa.E2_applied_gravity_kN.HasValue;
            Color original = GUI.color;
            GUI.color = new Color(0.16f, 0.20f, 0.16f, 0.92f);
            GUILayout.BeginVertical(GUI.skin.window);
            GUI.color = original;
            GUILayout.Label(combined ? "Global Equilibrium (QA) - E1 + E2" : "Global Equilibrium (QA)");

            if (combined)
            {
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "E1 applied gravity: {0:F2} kN", qa.E1_applied_gravity_kN.GetValueOrDefault()));
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "E2 applied gravity: {0:F2} kN", qa.E2_applied_gravity_kN.GetValueOrDefault()));
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "TOTAL applied gravity: {0:F2} kN", qa.TOTAL_applied_gravity_kN.GetValueOrDefault()));
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "E1 support reactions: {0:F2} kN", qa.E1_support_reactions_kN.GetValueOrDefault()));
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "E2 support reactions: {0:F2} kN", qa.E2_support_reactions_kN.GetValueOrDefault()));
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "TOTAL support reactions: {0:F2} kN", qa.TOTAL_support_reactions_kN.GetValueOrDefault()));
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "Residual Fz: {0:E3} kN", qa.global_residual_kN.GetValueOrDefault()));
                double combinedError = qa.relative_error_pct_combined.HasValue ? qa.relative_error_pct_combined.Value : qa.relative_error_pct.GetValueOrDefault();
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "Relative error: {0:F6}%", combinedError));
            }
            else
            {
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "Applied gravity: {0:F2} kN", qa.applied_gravity_kN.GetValueOrDefault()));
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "Sum support reaction Z: {0:F2} kN", qa.sum_support_reaction_z_kN.GetValueOrDefault()));
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "Residual Fz: {0:E3} kN", qa.residual_fz_kN.GetValueOrDefault()));
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "Relative error: {0:F6}%", qa.relative_error_pct.GetValueOrDefault()));
            }

            string text = pass ? "Global equilibrium: PASS" : "Global equilibrium: FAIL";
            Color badgeColor = pass ? new Color(0.16f, 0.58f, 0.26f) : new Color(0.75f, 0.22f, 0.22f);
            GUI.backgroundColor = badgeColor;
            GUI.color = Color.white;
            if (GUILayout.Button(text)) { }
            GUI.backgroundColor = Color.white;
            GUI.color = original;

            if (combined)
            {
                if (qa.E1_verified_max_displacement_m.HasValue)
                    GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "E1 verified max disp: {0:F4} m", qa.E1_verified_max_displacement_m.Value));
                if (qa.E2_verified_max_displacement_m.HasValue)
                    GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "E2 verified max disp: {0:F4} m", qa.E2_verified_max_displacement_m.Value));
                double combinedMax = qa.combined_verified_max_displacement_m.HasValue ? qa.combined_verified_max_displacement_m.Value : VerifiedMaxDisplacement();
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "Combined verified max disp: {0:F4} m", combinedMax));
                if (!string.IsNullOrWhiteSpace(qa.interface_status))
                    GUILayout.Label("Interface: " + qa.interface_status);
                if (IsMultiBuilding)
                {
                    GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "Blockers: E1 = {0}, E2 = {1}, Total = {2}", CountBlockers("E1").ToString(CultureInfo.InvariantCulture), CountBlockers("E2").ToString(CultureInfo.InvariantCulture), CountBlockers(null).ToString(CultureInfo.InvariantCulture)));
                }
                else
                {
                    GUILayout.Label("Blockers: " + CountBlockers(null).ToString(CultureInfo.InvariantCulture));
                }
            }
            else if (responseData.max_displacement != null)
            {
                GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "Verified region max disp: {0:F4} m (node {1}, floor {2})", responseData.max_displacement.verified_connected_region_max_m.GetValueOrDefault(), responseData.max_displacement.verified_region_node, responseData.max_displacement.verified_region_floor));
            }
            int blockers = data != null && data.geometric_blockers != null ? data.geometric_blockers.Count : 0;
            if (!combined)
            {
                GUILayout.Label("Blockers: " + blockers.ToString(CultureInfo.InvariantCulture));
            }
            if (blockers > 0 && GUILayout.Button("Show blocker location"))
            {
                if (combined && IsMultiBuilding)
                {
                    E1Blocker firstShown = data.geometric_blockers.Find(b => string.Equals(b.building_id, activeBuildingFilter, StringComparison.OrdinalIgnoreCase)) ?? data.geometric_blockers[0];
                    showBlockers = true;
                    SearchById(firstShown != null ? firstShown.slab_id : data.geometric_blockers[0].slab_id);
                }
                else
                {
                    showBlockers = true;
                    E1Blocker blocker = data.geometric_blockers[0];
                    SearchById(blocker.slab_id);
                }
                ApplyVisibility();
            }
            GUILayout.Space(2);
            GUILayout.EndVertical();
        }

        private int CountBlockers(string building)
        {
            if (data == null || data.geometric_blockers == null) return 0;
            if (string.IsNullOrWhiteSpace(building)) return data.geometric_blockers.Count;
            return data.geometric_blockers.Count(b => string.Equals(b.building_id, building, StringComparison.OrdinalIgnoreCase));
        }

        private void EnsureCameraAndLight()
        {
            cam = Camera.main;
            if (cam == null)
            {
                GameObject cameraObject = new GameObject("Main Camera");
                cameraObject.tag = "MainCamera";
                cam = cameraObject.AddComponent<Camera>();
                cameraObject.AddComponent<AudioListener>();
            }
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.035f, 0.067f, 0.118f);
            cam.nearClipPlane = 0.05f;
            cam.farClipPlane = 700f;

            if (FindObjectOfType<Light>() == null)
            {
                GameObject lightObject = new GameObject("Directional Light");
                Light light = lightObject.AddComponent<Light>();
                light.type = LightType.Directional;
                light.intensity = 1.25f;
                lightObject.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
            }
        }

        private void CreateMaterials()
        {
            beamMaterial = Opaque(new Color(1.0f, 0.67f, 0.28f));
            slabMaterial = Transparent(new Color(0.34f, 0.66f, 1.0f, 0.28f));
            nodeMaterial = Opaque(new Color(1.0f, 0.82f, 0.28f));
            tributaryMaterial = Transparent(new Color(0.48f, 0.85f, 0.56f, 0.18f));
            selectedTributaryMaterial = Transparent(new Color(0.48f, 1.0f, 0.56f, 0.46f));
            blockerMaterial = Opaque(new Color(1.0f, 0.32f, 0.32f));
            columnMaterial = Opaque(new Color(0.95f, 0.58f, 0.34f));
            wallMaterial = Transparent(new Color(0.62f, 0.83f, 0.68f, 0.62f));
            supportMaterial = Opaque(new Color(0.88f, 0.84f, 0.66f));
            diaphragmMaterial = Transparent(new Color(0.74f, 0.72f, 1.0f, 0.18f));
            genericMaterial = Opaque(new Color(0.66f, 0.66f, 0.70f));
            lineMaterial = Line(new Color(0.78f, 0.90f, 1.0f));
            localXMaterial = Line(Color.red);
            localYMaterial = Line(Color.green);
            localZMaterial = Line(Color.blue);
            verifiedMaterial = Opaque(new Color(0.18f, 0.75f, 0.35f));
            floatingMaterial = Opaque(new Color(0.90f, 0.42f, 0.10f));
            scopingMaterial = Opaque(new Color(0.95f, 0.72f, 0.15f));
            deformedMaterial = Line(new Color(0.30f, 0.95f, 0.60f));
            deformedBlockedMaterial = Line(new Color(1.0f, 0.62f, 0.20f));
            diagramMaterial = Line(new Color(0.45f, 0.72f, 1.0f));
            diagramScopingMaterial = Line(new Color(0.95f, 0.70f, 0.20f));
            selectedMaterial = Opaque(new Color(1.0f, 0.95f, 0.20f));
            loadArrowMaterial = Line(new Color(1.0f, 0.18f, 0.18f));
        }

        private Material Opaque(Color color)
        {
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = color;
            return mat;
        }

        private Material Transparent(Color color)
        {
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = color;
            mat.SetFloat("_Mode", 3f);
            mat.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
            mat.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
            mat.SetInt("_ZWrite", 0);
            mat.DisableKeyword("_ALPHATEST_ON");
            mat.EnableKeyword("_ALPHABLEND_ON");
            mat.DisableKeyword("_ALPHAPREMULTIPLY_ON");
            mat.renderQueue = 3000;
            return mat;
        }

        private Material Line(Color color)
        {
            Material mat = new Material(Shader.Find("Sprites/Default"));
            mat.color = color;
            return mat;
        }

        private void LoadAndBuild()
        {
            data = E1GravityJsonLoader.Load();
            if (data == null)
            {
                statusText = "ERROR: no se pudo cargar " + E1GravityJsonLoader.ActiveGravityFileName();
                return;
            }

            root = new GameObject("E1_Gravity_Model");
            labelsRoot = new GameObject("E1_ID_Labels");
            axesRoot = new GameObject("E1_Local_Axes");
            labelsRoot.transform.SetParent(root.transform, false);
            axesRoot.transform.SetParent(root.transform, false);

            BuildSlabs();
            BuildBeamsAndNodes();
            BuildGenericElements();
            BuildBlockers();
            LoadResponseData();
            ComputeBounds();
            ApplyVisibility();
            FrameAll();
            statusText = SummaryText();
        }

        private void LoadResponseData()
        {
            responseData = E1GravityJsonLoader.LoadResponse();
            if (responseData == null)
            {
                responseLoaded = false;
                return;
            }
            responseLoaded = true;

            if (responseData.elements != null)
            {
                foreach (KeyValuePair<string, E1ResponseElement> pair in responseData.elements)
                {
                    if (pair.Value != null) responseElementById[pair.Key] = pair.Value;
                }
            }
            if (responseData.element_forces_kN != null)
            {
                foreach (KeyValuePair<string, E1ElementForcesResponse> pair in responseData.element_forces_kN)
                {
                    if (pair.Value != null) responseForcesById[pair.Key] = pair.Value;
                }
            }

            ComputeResponseDeformationScale();
            LoadStructuralMappingData();
            BuildResponseVisualizations();
            ApplyBlockerHighlight();
        }

        private void LoadStructuralMappingData()
        {
            mappingData = E1GravityJsonLoader.LoadMapping();
            structuralElementMappingByVisualId.Clear();
            structuralSupportMappingByVisualId.Clear();
            structuralNodeMappingByVisualId.Clear();

            MergeMapping(mappingData);
            if (IsMultiBuilding)
            {
                E1StructuralMappingCoverage e2Mapping = E1GravityJsonLoader.LoadMapping(E1GravityJsonLoader.E2MappingPath());
                if (e2Mapping != null) MergeMapping(e2Mapping);
            }
        }

        private void MergeMapping(E1StructuralMappingCoverage mapping)
        {
            if (mapping == null || mapping.mappings == null) return;
            if (mapping.mappings.elements != null)
            {
                foreach (KeyValuePair<string, E1StructuralElementMapping> pair in mapping.mappings.elements)
                {
                    if (pair.Value != null) structuralElementMappingByVisualId[pair.Key] = pair.Value;
                }
            }
            if (mapping.mappings.supports != null)
            {
                foreach (KeyValuePair<string, E1StructuralSupportMapping> pair in mapping.mappings.supports)
                {
                    if (pair.Value != null) structuralSupportMappingByVisualId[pair.Key] = pair.Value;
                }
            }
            if (mapping.mappings.nodes != null)
            {
                foreach (KeyValuePair<string, E1StructuralNodeMapping> pair in mapping.mappings.nodes)
                {
                    if (pair.Value != null) structuralNodeMappingByVisualId[pair.Key] = pair.Value;
                }
            }
        }

        private void ComputeResponseDeformationScale()
        {
            responseDeformScale = VerifiedDeformationScale;
        }

        private double VerifiedMaxDisplacement()
        {
            return responseData != null && responseData.max_displacement != null
                ? responseData.max_displacement.verified_connected_region_max_m.GetValueOrDefault()
                : 0.0;
        }

        private void BuildResponseVisualizations()
        {
            ClearResponseVisuals();
            if (responseData == null || responseData.elements == null) return;

            foreach (KeyValuePair<string, E1ResponseElement> pair in responseData.elements)
            {
                E1ResponseElement element = pair.Value;
                if (element == null) continue;
                bool verified = E1AnalysisStatus.IsVerified(element.analysis_status);

                Vector3 i = ResponseToUnity(element.node_i);
                Vector3 j = ResponseToUnity(element.node_j);

                if (showDeformed && CanDrawVerifiedDeformation(element))
                {
                    CreateDeformedLine(pair.Key, i, j, element.node_i, element.node_j, deformedMaterial, deformedLines);
                }
                else if (!verified && showDeformedBlocked && ShowUnverifiedStatus(element.analysis_status))
                {
                    CreateDeformedLine(pair.Key, i, j, element.node_i, element.node_j, deformedBlockedMaterial, deformedBlockedLines);
                }
            }

            if (showDiagrams)
            {
                float maxMag = MaxDiagramMagnitude();
                E1ResponseElement selectedResponse = selectedView != null ? MatchResponseElement(selectedView) : null;
                foreach (KeyValuePair<string, E1ResponseElement> pair in responseData.elements)
                {
                    E1ResponseElement element = pair.Value;
                    if (element == null) continue;
                    if (selectedResponse == null || !SameResponseElement(element, selectedResponse)) continue;
                    bool verified = E1AnalysisStatus.IsVerified(element.analysis_status);
                    bool scoping = !verified && string.Equals(element.analysis_status, E1AnalysisStatus.Scoping, StringComparison.OrdinalIgnoreCase);
                    if (!verified && !scoping) continue;
                    Vector3 i = ResponseToUnity(element.node_i);
                    Vector3 j = ResponseToUnity(element.node_j);
                    CreateDiagramLine(pair.Key, i, j, element, verified ? 0 : 1, maxMag);
                }
            }
        }

        private float MaxDiagramMagnitude()
        {
            float max = 0f;
            if (responseData == null || responseData.element_forces_kN == null) return max;
            foreach (KeyValuePair<string, E1ElementForcesResponse> pair in responseData.element_forces_kN)
            {
                if (pair.Value == null || pair.Value.forces_kN == null) continue;
                foreach (KeyValuePair<string, double> f in pair.Value.forces_kN)
                {
                    float v = (float)Math.Abs(f.Value);
                    if (v > max) max = v;
                }
            }
            return max;
        }

        private bool SameResponseElement(E1ResponseElement a, E1ResponseElement b)
        {
            if (a == null || b == null) return false;
            return ResponseCoordsNear(a.node_i, b.node_i) && ResponseCoordsNear(a.node_j, b.node_j) ||
                   ResponseCoordsNear(a.node_i, b.node_j) && ResponseCoordsNear(a.node_j, b.node_i);
        }

        private float DiagramRepresentativeMagnitude(E1ResponseElement element)
        {
            if (responseData == null || responseData.element_forces_kN == null) return 0f;
            if (!responseData.element_forces_kN.TryGetValue(elementOfId(element), out E1ElementForcesResponse forces)) return 0f;
            if (forces == null || forces.forces_kN == null) return 0f;
            float mag = 0f;
            foreach (KeyValuePair<string, double> f in forces.forces_kN)
            {
                if (f.Key.StartsWith("M", StringComparison.OrdinalIgnoreCase))
                {
                    float v = (float)Math.Abs(f.Value);
                    if (v > mag) mag = v;
                }
            }
            return mag;
        }

        private string elementOfId(E1ResponseElement element)
        {
            if (responseData == null || responseData.elements == null) return null;
            foreach (KeyValuePair<string, E1ResponseElement> pair in responseData.elements)
            {
                if (ReferenceEquals(pair.Value, element)) return pair.Key;
            }
            return null;
        }

        private void CreateDiagramLine(string id, Vector3 baseI, Vector3 baseJ, E1ResponseElement element, int kindIndex, float maxMag)
        {
            GameObject go = new GameObject("DIAGRAM_" + id);
            go.transform.SetParent(root.transform, false);
            responseVisualBuilding[go] = BuildingFromResponseKey(id);
            LineRenderer lr = go.AddComponent<LineRenderer>();
            lr.useWorldSpace = true;
            Vector3 dir = baseJ - baseI;
            Vector3 side = Vector3.Cross(Vector3.up, dir.normalized);
            if (side.sqrMagnitude < 0.0001f) side = Vector3.up;
            side = side.normalized;

            float mag = DiagramRepresentativeMagnitude(element);
            float offset = maxMag > 0.0001f ? Mathf.Clamp(mag / maxMag, 0f, 1f) * 0.6f : 0f;
            Vector3 p0 = baseI + side * offset;
            Vector3 p1 = baseJ + side * offset;

            lr.positionCount = 2;
            lr.SetPosition(0, p0);
            lr.SetPosition(1, p1);
            lr.startWidth = Mathf.Max(0.03f, 0.03f + offset);
            lr.endWidth = Mathf.Max(0.03f, 0.03f + offset);
            lr.sharedMaterial = kindIndex == 0 ? diagramMaterial : diagramScopingMaterial;

            if (!diagramRenderersByKind.TryGetValue(kindIndex, out List<LineRenderer> list))
            {
                list = new List<LineRenderer>();
                diagramRenderersByKind[kindIndex] = list;
            }
            list.Add(lr);
            diagramLines.Add(go);
        }

        private void ClearResponseVisuals()
        {
            foreach (GameObject go in deformedLines) if (go != null) Destroy(go);
            foreach (GameObject go in deformedBlockedLines) if (go != null) Destroy(go);
            foreach (GameObject go in diagramLines) if (go != null) Destroy(go);
            responseVisualBuilding.Clear();
            deformedLines.Clear();
            deformedBlockedLines.Clear();
            diagramLines.Clear();
            diagramRenderersByKind.Clear();
        }

        private void RebuildSelectedLoadVisuals()
        {
            ClearSelectedLoadVisuals();
            if (!showLoads || selectedView == null || selectedView.category != "beam" || selectedView.beam == null) return;
            Vector3 start = selectedView.start;
            Vector3 end = selectedView.end;
            float arrowLength = Mathf.Clamp((float)Math.Abs(selectedView.beam.w_lineal_kN_m) * 0.035f, 0.35f, 1.6f);
            int count = 5;
            for (int k = 0; k < count; k++)
            {
                float t = (k + 0.5f) / count;
                Vector3 top = Vector3.Lerp(start, end, t) + Vector3.up * (arrowLength + 0.45f);
                Vector3 bottom = top - Vector3.up * arrowLength;
                GameObject go = new GameObject("LOAD_ARROW_" + selectedView.beam.beam_id + "_" + k.ToString(CultureInfo.InvariantCulture));
                go.transform.SetParent(root.transform, false);
                LineRenderer lr = go.AddComponent<LineRenderer>();
                lr.useWorldSpace = true;
                lr.positionCount = 2;
                lr.SetPosition(0, top);
                lr.SetPosition(1, bottom);
                lr.startWidth = 0.06f;
                lr.endWidth = 0.12f;
                lr.sharedMaterial = loadArrowMaterial;
                selectedLoadLines.Add(go);
            }
        }

        private void ClearSelectedLoadVisuals()
        {
            foreach (GameObject go in selectedLoadLines) if (go != null) Destroy(go);
            selectedLoadLines.Clear();
        }

        private void CreateDeformedLine(string id, Vector3 baseI, Vector3 baseJ, List<double> nodeIRaw, List<double> nodeJRaw, Material material, List<GameObject> target)
        {
            Vector3 dispI = ResponseDisplayDisplacementAt(nodeIRaw);
            Vector3 dispJ = ResponseDisplayDisplacementAt(nodeJRaw);
            Vector3 worldI = baseI + dispI * responseDeformScale;
            Vector3 worldJ = baseJ + dispJ * responseDeformScale;

            GameObject go = new GameObject("DEFORMED_" + id);
            go.transform.SetParent(root.transform, false);
            responseVisualBuilding[go] = BuildingFromResponseKey(id);
            LineRenderer lr = go.AddComponent<LineRenderer>();
            lr.useWorldSpace = true;
            lr.positionCount = 2;
            lr.SetPosition(0, worldI);
            lr.SetPosition(1, worldJ);
            lr.startWidth = 0.10f;
            lr.endWidth = 0.10f;
            lr.sharedMaterial = material;
            target.Add(go);
        }

        private Vector3 ResponseToUnity(List<double> node)
        {
            return ModelToUnity(node, 0, 0f);
        }

        private Vector3 ResponseDisplayDisplacementAt(List<double> node)
        {
            if (responseData == null || responseData.displacements_m == null || node == null || node.Count < 3)
                return Vector3.zero;
            string tag = FindResponseNodeTag(node);
            if (tag == null) return FindSupportRestraintAt(node) != null ? Vector3.zero : Vector3.zero;
            if (responseData.displacements_m.TryGetValue(tag, out E1DisplacementResponse disp))
            {
                if (disp == null) return Vector3.zero;
                // Verified gravity deformation is displayed with the validated vertical
                // component only. Full ux/uy/uz remain reported in the inspector.
                return new Vector3(0f, (float)disp.uz_m.GetValueOrDefault(), 0f);
            }
            return Vector3.zero;
        }

        private bool CanDrawVerifiedDeformation(E1ResponseElement element)
        {
            if (element == null) return false;
            if (!E1AnalysisStatus.IsVerified(element.analysis_status)) return false;
            if (string.Equals(element.stub_status, StubStatusStub, StringComparison.OrdinalIgnoreCase)) return false;
            return IsVerifiedDisplayDisplacement(element.node_i) && IsVerifiedDisplayDisplacement(element.node_j);
        }

        private bool IsVerifiedDisplayDisplacement(List<double> node)
        {
            if (node == null || node.Count < 3) return false;
            if (FindSupportRestraintAt(node) != null) return true;
            string tag = FindResponseNodeTag(node);
            if (tag == null) return false;
            if (responseData == null || responseData.node_analysis_status == null) return false;
            if (!responseData.node_analysis_status.TryGetValue(tag, out string status) || !E1AnalysisStatus.IsVerified(status)) return false;
            E1DisplacementResponse disp = FindDisplacement(node);
            if (disp == null) return false;
            double limit = VerifiedVerticalDisplacementLimit();
            return Math.Abs(disp.uz_m.GetValueOrDefault()) <= limit;
        }

        private E1SupportRestraintResponse FindSupportRestraintAt(List<double> node)
        {
            if (responseData == null || responseData.support_restraints == null || node == null || node.Count < 3) return null;
            foreach (KeyValuePair<string, E1SupportRestraintResponse> pair in responseData.support_restraints)
            {
                E1SupportRestraintResponse restraint = pair.Value;
                if (restraint == null || !ResponseCoordsNear(restraint.coords, node)) continue;
                return restraint;
            }
            return null;
        }

        private double VerifiedVerticalDisplacementLimit()
        {
            double max = responseData != null && responseData.max_displacement != null
                ? responseData.max_displacement.verified_connected_region_max_m.GetValueOrDefault()
                : 0.0;
            return Math.Max(0.0005, max * VerifiedDisplacementLimitFactor);
        }

        private string FindResponseNodeTag(List<double> node)
        {
            if (responseData == null || responseData.displacements_m == null || node == null || node.Count < 3) return null;
            foreach (KeyValuePair<string, E1DisplacementResponse> pair in responseData.displacements_m)
            {
                if (ResponseCoordsNear(pair.Value != null ? pair.Value.coords : null, node)) return pair.Key;
            }
            return null;
        }

        private bool ResponseCoordsNear(List<double> a, List<double> b)
        {
            if (a == null || b == null || a.Count < 3 || b.Count < 3) return false;
            const double tol = 0.01;
            return Math.Abs(a[0] - b[0]) < tol && Math.Abs(a[1] - b[1]) < tol && Math.Abs(a[2] - b[2]) < tol;
        }

        private string SummaryText()
        {
            int slabs = data.losas == null ? 0 : data.losas.Count;
            int beams = data.vigas == null ? 0 : data.vigas.Count;
            int blockers = data.geometric_blockers == null ? 0 : data.geometric_blockers.Count;
            int columns = data.columns == null ? 0 : data.columns.Count;
            int walls = data.walls == null ? 0 : data.walls.Count;
            int supports = data.supports == null ? 0 : data.supports.Count;
            int diaphragms = data.diaphragms == null ? 0 : data.diaphragms.Count;
            return string.Format(CultureInfo.InvariantCulture, "{0}: {1} losas, {2} vigas, {3} nodos, {4} columnas, {5} muros, {6} apoyos, {7} diafragmas, {8} blocker", data.building_id, slabs, beams, nodesById.Count, columns, walls, supports, diaphragms, blockers);
        }

        private void BuildSlabs()
        {
            if (data.losas == null) return;
            foreach (E1Slab slab in data.losas)
            {
                if (slab.vertices == null || slab.vertices.Count < 3) continue;
                Mesh mesh = BuildPolygonMesh(slab.vertices, FloorY(slab.floor_id) - SlabVisualThickness * 0.5f);
                if (mesh == null) continue;
                GameObject go = new GameObject("SLAB_" + slab.slab_id);
                go.transform.SetParent(root.transform, false);
                MeshFilter mf = go.AddComponent<MeshFilter>();
                MeshRenderer mr = go.AddComponent<MeshRenderer>();
                MeshCollider mc = go.AddComponent<MeshCollider>();
                mf.sharedMesh = mesh;
                mc.sharedMesh = mesh;
                mr.sharedMaterial = slabMaterial;

                E1ElementView view = go.AddComponent<E1ElementView>();
                view.id = slab.slab_id;
                view.category = "slab";
                view.floorId = slab.floor_id;
                view.slab = slab;
                view.building = slab.building_id;
                Register(view);
                AddPolygonLine("EDGE_" + slab.slab_id, slab.vertices, FloorY(slab.floor_id) + 0.03f, lineMaterial, 0.03f, "slab", slab.floor_id, slab.slab_id);
                AddLabel(slab.slab_id, MeshCenter(mesh), slab.floor_id);
            }
        }

        private void BuildBeamsAndNodes()
        {
            if (data.vigas == null) return;
            foreach (E1Beam beam in data.vigas)
            {
                if (!IsPoint2(beam.node_i) || !IsPoint2(beam.node_j)) continue;
                Vector3 start = ToWorld(beam.node_i, beam.floor_id, 0.16f);
                Vector3 end = ToWorld(beam.node_j, beam.floor_id, 0.16f);
                GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                go.name = "BEAM_" + beam.beam_id;
                go.transform.SetParent(root.transform, false);
                SetTransformBetween(go.transform, start, end, BeamWidth, BeamDepth);
                go.GetComponent<Renderer>().sharedMaterial = beamMaterial;

                E1ElementView view = go.AddComponent<E1ElementView>();
                view.id = beam.beam_id;
                view.category = "beam";
                view.floorId = beam.floor_id;
                view.beam = beam;
                view.start = start;
                view.end = end;
                view.building = beam.building_id;
                Register(view);

                E1NodeInfo nodeI = GetOrCreateNode(beam.floor_id, beam.node_i, beam.building_id);
                E1NodeInfo nodeJ = GetOrCreateNode(beam.floor_id, beam.node_j, beam.building_id);
                nodeI.beams.Add(beam.beam_id);
                nodeJ.beams.Add(beam.beam_id);

                BuildBeamTributaries(beam);
                AddLocalAxes(beam.beam_id, beam.floor_id, start, end);
                AddLabel(beam.beam_id, (start + end) * 0.5f + Vector3.up * 0.18f, beam.floor_id);
            }
        }

        private void BuildBeamTributaries(E1Beam beam)
        {
            if (beam.poligonos_tributarios == null) return;
            foreach (E1TributaryPolygon tributary in beam.poligonos_tributarios)
            {
                if (tributary.polygon == null || tributary.polygon.Count < 3) continue;
                Mesh mesh = BuildPolygonMesh(tributary.polygon, FloorY(beam.floor_id) + 0.08f);
                if (mesh == null) continue;
                GameObject go = new GameObject("TRIB_" + beam.beam_id + "__" + tributary.slab_id);
                go.transform.SetParent(root.transform, false);
                MeshFilter mf = go.AddComponent<MeshFilter>();
                MeshRenderer mr = go.AddComponent<MeshRenderer>();
                MeshCollider mc = go.AddComponent<MeshCollider>();
                mf.sharedMesh = mesh;
                mc.sharedMesh = mesh;
                mr.sharedMaterial = tributaryMaterial;

                E1ElementView view = go.AddComponent<E1ElementView>();
                view.id = beam.beam_id + "__" + tributary.slab_id;
                view.category = "tributary";
                view.parentId = beam.beam_id;
                view.floorId = beam.floor_id;
                view.beam = beam;
                view.tributary = tributary;
                view.building = beam.building_id;
                Register(view, false);
                if (!tributariesByBeam.ContainsKey(beam.beam_id)) tributariesByBeam.Add(beam.beam_id, new List<E1ElementView>());
                tributariesByBeam[beam.beam_id].Add(view);
                AddPolygonLine("TRIB_EDGE_" + view.id, tributary.polygon, FloorY(beam.floor_id) + 0.09f, localYMaterial, 0.02f, "tributary", beam.floor_id, view.id);
            }
        }

        private void BuildGenericElements()
        {
            BuildGenericLinearList(data.columns, "column");
            BuildGenericLinearList(data.walls, "wall");
            BuildGenericLinearList(data.supports, "support");
            BuildGenericDiaphragms(data.diaphragms);
        }

        private void BuildGenericLinearList(List<E1GenericElement> list, string category)
        {
            if (list == null) return;
            foreach (E1GenericElement item in list)
            {
                if (category == "column" && item.center != null)
                {
                    BuildColumnBox(item, GenericId(item, category));
                    continue;
                }
                if (category == "wall" && IsPoint2(item.node_i) && IsPoint2(item.node_j))
                {
                    BuildWallPanel(item, GenericId(item, category));
                    continue;
                }
                if (category == "support" && IsPoint2(item.node_i) && IsPoint2(item.node_j))
                {
                    BuildSupportLinear(item, GenericId(item, category));
                    continue;
                }
                if (category == "support" && !IsPoint2(item.node_i) && !IsPoint2(item.node_j))
                {
                    List<double> supportPoint = item.point ?? item.center;
                    if (!IsPoint2(supportPoint)) continue;
                    string supportId = GenericId(item, category);
                    GameObject supportGo = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                    supportGo.name = "SUPPORT_" + supportId;
                    supportGo.transform.SetParent(root.transform, false);
                    supportGo.transform.position = ToUnityPoint(supportPoint, item.floor_id) + Vector3.up * 0.2f;
                    supportGo.transform.localScale = Vector3.one * 0.55f;
                    supportGo.GetComponent<Renderer>().sharedMaterial = supportMaterial;
                    E1ElementView supportView = supportGo.AddComponent<E1ElementView>();
                    supportView.id = supportId;
                    supportView.category = category;
                    supportView.floorId = item.floor_id;
                    supportView.generic = item;
                    supportView.building = item.building_id;
                    Register(supportView);
                    E1NodeInfo supportNode = GetOrCreateNode(item.floor_id, supportPoint, item.building_id);
                    AddNodeConnection(supportNode, category, supportId);
                    continue;
                }
                if (!IsPoint2(item.node_i) || !IsPoint2(item.node_j)) continue;
                string id = GenericId(item, category);
                Vector3 start = ToUnityPoint(item.node_i, item.floor_id);
                Vector3 end = ToUnityPoint(item.node_j, item.floor_id);
                GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                go.name = category.ToUpperInvariant() + "_" + id;
                go.transform.SetParent(root.transform, false);
                SetTransformBetween(go.transform, start, end, BeamWidth, BeamDepth);
                go.GetComponent<Renderer>().sharedMaterial = genericMaterial;

                E1ElementView view = go.AddComponent<E1ElementView>();
                view.id = id;
                view.category = category;
                view.floorId = item.floor_id;
                view.generic = item;
                view.start = start;
                view.end = end;
                view.building = item.building_id;
                Register(view);
                E1NodeInfo nodeI = GetOrCreateNode(item.floor_id, item.node_i, item.building_id);
                E1NodeInfo nodeJ = GetOrCreateNode(item.floor_id, item.node_j, item.building_id);
                AddNodeConnection(nodeI, category, id);
                AddNodeConnection(nodeJ, category, id);
                if (category == "column") AddLocalAxes(id, item.floor_id, start, end);
            }
        }

        private void BuildColumnBox(E1GenericElement item, string id)
        {
            Vector3 center = ToUnityPoint(item.center, item.floor_id);
            float width = (float)(item.width_m ?? item.section?.width_m ?? item.section?.b ?? 0.45);
            float depth = (float)(item.depth_m ?? item.width_m ?? item.section?.width_m ?? item.section?.b ?? 0.45);
            float height = (float)(item.height_m ?? item.length_m ?? FloorHeight);
            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = "COLUMN_" + id;
            go.transform.SetParent(root.transform, false);
            go.transform.position = center;
            go.transform.localScale = new Vector3(Mathf.Max(width, 0.08f), Mathf.Max(height, 0.08f), Mathf.Max(depth, 0.08f));
            go.GetComponent<Renderer>().sharedMaterial = columnMaterial;

            E1ElementView view = go.AddComponent<E1ElementView>();
            view.id = id;
            view.category = "column";
            view.floorId = item.floor_id;
            view.generic = item;
            view.start = center - Vector3.up * height * 0.5f;
            view.end = center + Vector3.up * height * 0.5f;
            view.building = item.building_id;
            Register(view);
            AddLocalAxes(id, item.floor_id, view.start, view.end);
            AddLabel(id, center + Vector3.up * (height * 0.5f + 0.25f), item.floor_id);
            List<double> planPoint = new List<double> { item.center[0], item.center[1] };
            E1NodeInfo baseNode = GetOrCreateNode(item.floor_id, planPoint, item.building_id);
            AddNodeConnection(baseNode, "column", id);
        }

        private void BuildWallPanel(E1GenericElement item, string id)
        {
            Vector3 start = ToUnityPoint(item.node_i, item.floor_id);
            Vector3 end = ToUnityPoint(item.node_j, item.floor_id);
            float height = (float)(item.height_m ?? FloorHeight);
            float thickness = (float)(item.width_m ?? item.depth_m ?? 0.18);
            Vector3 horizontal = end - start;
            horizontal.y = 0f;
            Vector3 normal = Vector3.Cross(Vector3.up, horizontal.normalized);
            if (normal.sqrMagnitude < 0.0001f) normal = Vector3.forward;
            Vector3 offset = normal.normalized * thickness * 0.5f;
            Vector3[] vertices =
            {
                start - offset - Vector3.up * height * 0.5f,
                end - offset - Vector3.up * height * 0.5f,
                end - offset + Vector3.up * height * 0.5f,
                start - offset + Vector3.up * height * 0.5f,
                start + offset - Vector3.up * height * 0.5f,
                end + offset - Vector3.up * height * 0.5f,
                end + offset + Vector3.up * height * 0.5f,
                start + offset + Vector3.up * height * 0.5f,
            };
            int[] triangles =
            {
                0, 1, 2, 0, 2, 3,
                5, 4, 7, 5, 7, 6,
                4, 0, 3, 4, 3, 7,
                1, 5, 6, 1, 6, 2,
                3, 2, 6, 3, 6, 7,
                4, 5, 1, 4, 1, 0,
            };
            Mesh mesh = new Mesh { name = "wall_panel" };
            mesh.vertices = vertices;
            mesh.triangles = triangles;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();

            GameObject go = new GameObject("WALL_" + id);
            go.transform.SetParent(root.transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterial = wallMaterial;
            go.AddComponent<MeshCollider>().sharedMesh = mesh;
            E1ElementView view = go.AddComponent<E1ElementView>();
            view.id = id;
            view.category = "wall";
            view.floorId = item.floor_id;
            view.generic = item;
            view.start = start;
            view.end = end;
            view.building = item.building_id;
            Register(view);
            E1NodeInfo nodeI = GetOrCreateNode(item.floor_id, item.node_i, item.building_id);
            E1NodeInfo nodeJ = GetOrCreateNode(item.floor_id, item.node_j, item.building_id);
            AddNodeConnection(nodeI, "wall", id);
            AddNodeConnection(nodeJ, "wall", id);
            AddLabel(id, (start + end) * 0.5f + Vector3.up * (height * 0.5f + 0.2f), item.floor_id);
        }

        private void BuildSupportLinear(E1GenericElement item, string id)
        {
            Vector3 start = ToUnityPoint(item.node_i, item.floor_id);
            Vector3 end = ToUnityPoint(item.node_j, item.floor_id);
            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = "SUPPORT_" + id;
            go.transform.SetParent(root.transform, false);
            float width = (float)(item.width_m ?? 0.45);
            float height = (float)(item.height_m ?? 0.3);
            SetTransformBetween(go.transform, start, end, width, height);
            go.GetComponent<Renderer>().sharedMaterial = supportMaterial;
            E1ElementView view = go.AddComponent<E1ElementView>();
            view.id = id;
            view.category = "support";
            view.floorId = item.floor_id;
            view.generic = item;
            view.start = start;
            view.end = end;
            view.building = item.building_id;
            Register(view);
            E1NodeInfo nodeIL = GetOrCreateNode(item.floor_id, item.node_i, item.building_id);
            E1NodeInfo nodeJL = GetOrCreateNode(item.floor_id, item.node_j, item.building_id);
            AddNodeConnection(nodeIL, "support", id);
            AddNodeConnection(nodeJL, "support", id);
            AddLabel(id, (start + end) * 0.5f + Vector3.up * 0.35f, item.floor_id);
        }

        private void AddNodeConnection(E1NodeInfo node, string category, string id)
        {
            if (category == "beam" && !node.beams.Contains(id)) node.beams.Add(id);
            else if (category == "column" && !node.columns.Contains(id)) node.columns.Add(id);
            else if (category == "support" && !node.supports.Contains(id)) node.supports.Add(id);
            else if (category == "wall" && !node.walls.Contains(id)) node.walls.Add(id);
        }

        private void BuildGenericDiaphragms(List<E1GenericElement> list)
        {
            if (list == null) return;
            foreach (E1GenericElement item in list)
            {
                List<List<double>> points = item.points ?? item.vertices;
                if (points == null || points.Count < 2) continue;
                string id = GenericId(item, "diaphragm");
                GameObject plane = BuildDiaphragmPlane(id, item, points);
                E1ElementView view = plane.GetComponent<E1ElementView>();
                if (view != null) view.generic = item;
            }
        }

        private GameObject BuildDiaphragmPlane(string id, E1GenericElement item, List<List<double>> points)
        {
            Mesh mesh = BuildGenericPolygonMesh(points);
            GameObject go = new GameObject("DIAPHRAGM_" + id);
            go.transform.SetParent(root.transform, false);
            if (mesh != null)
            {
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                go.AddComponent<MeshRenderer>().sharedMaterial = diaphragmMaterial;
                go.AddComponent<MeshCollider>().sharedMesh = mesh;
            }
            AddGenericPolyline("DIAPHRAGM_EDGE_" + id, points, lineMaterial, 0.06f, go.transform);
            E1ElementView view = go.AddComponent<E1ElementView>();
            view.id = id;
            view.category = "diaphragm";
            view.floorId = item.floor_id;
            view.generic = item;
            view.building = item.building_id;
            Register(view);
            AddLabel(id, GenericCenter(points), item.floor_id);
            return go;
        }

        private void BuildBlockers()
        {
            if (data.geometric_blockers == null) return;
            foreach (E1Blocker blocker in data.geometric_blockers)
            {
                Vector3 position = BlockerPosition(blocker);
                GameObject go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                go.name = "BLOCKER_" + blocker.slab_id;
                go.transform.SetParent(root.transform, false);
                go.transform.position = position;
                go.transform.localScale = Vector3.one * 0.8f;
                go.GetComponent<Renderer>().sharedMaterial = blockerMaterial;
                E1ElementView view = go.AddComponent<E1ElementView>();
                view.id = blocker.slab_id;
                view.category = "blocker";
                view.floorId = blocker.floor_id;
                view.blocker = blocker;
                view.building = blocker.building_id;
                Register(view);
                AddLabel(blocker.slab_id, position + Vector3.up * 0.7f, blocker.floor_id);
            }
        }

        private Vector3 BlockerPosition(E1Blocker blocker)
        {
            if (data.vigas != null)
            {
                List<Vector3> points = new List<Vector3>();
                foreach (E1Beam beam in data.vigas)
                {
                    if (beam.floor_id != blocker.floor_id) continue;
                    if (IsPoint2(beam.node_i)) points.Add(ToWorld(beam.node_i, beam.floor_id, 0.85f));
                    if (IsPoint2(beam.node_j)) points.Add(ToWorld(beam.node_j, beam.floor_id, 0.85f));
                }
                if (points.Count > 0)
                {
                    Vector3 min = points[0];
                    foreach (Vector3 p in points) min = Vector3.Min(min, p);
                    return min + new Vector3(1.2f, 0f, 1.2f);
                }
            }
            return new Vector3(0f, FloorY(blocker.floor_id) + 0.85f, 0f);
        }

        private string GenericId(E1GenericElement item, string category)
        {
            if (!string.IsNullOrWhiteSpace(item.id)) return item.id;
            if (category == "column" && !string.IsNullOrWhiteSpace(item.column_id)) return item.column_id;
            if (category == "wall" && !string.IsNullOrWhiteSpace(item.wall_id)) return item.wall_id;
            if (category == "support" && !string.IsNullOrWhiteSpace(item.support_id)) return item.support_id;
            if (category == "diaphragm" && !string.IsNullOrWhiteSpace(item.diaphragm_id)) return item.diaphragm_id;
            return category + "_floor_" + item.floor_id;
        }

        private E1NodeInfo GetOrCreateNode(int floorId, List<double> point, string building = null)
        {
            string key = NodeKey(floorId, point);
            if (nodesByKey.TryGetValue(key, out E1NodeInfo existing)) return existing;

            nodeIndex++;
            E1NodeInfo node = new E1NodeInfo();
            node.id = "N_" + FloorLabel(floorId).Replace("P", "F") + "_" + nodeIndex.ToString("0000", CultureInfo.InvariantCulture);
            node.floorId = floorId;
            node.point2 = new Vector2((float)point[0], (float)point[1]);
            node.world = ToWorld(point, floorId, 0.28f);
            nodesByKey.Add(key, node);
            nodesById.Add(node.id, node);

            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = "NODE_" + node.id;
            go.transform.SetParent(root.transform, false);
            go.transform.position = node.world;
            go.transform.localScale = Vector3.one * 0.32f;
            go.GetComponent<Renderer>().sharedMaterial = nodeMaterial;

            E1ElementView view = go.AddComponent<E1ElementView>();
            view.id = node.id;
            view.category = "node";
            view.floorId = floorId;
            view.node = node;
            view.building = building;
            Register(view);
            AddLabel(node.id, node.world + Vector3.up * 0.28f, floorId);
            return node;
        }

        private string NodeKey(int floorId, List<double> point)
        {
            return string.Format(CultureInfo.InvariantCulture, "{0}|{1:F3}|{2:F3}", floorId, point[0], point[1]);
        }

        private void Register(E1ElementView view, bool searchable = true)
        {
            views.Add(view);
            if (searchable && !string.IsNullOrWhiteSpace(view.id) && !elementById.ContainsKey(view.id)) elementById.Add(view.id, view);
            AttachSelectable(view);
            RememberOriginalMaterials(view.gameObject);
        }

        private void AttachSelectable(E1ElementView view)
        {
            if (view == null) return;
            StructuralSelectable selectable = view.GetComponent<StructuralSelectable>();
            if (selectable == null) selectable = view.gameObject.AddComponent<StructuralSelectable>();
            selectable.elementType = view.category;
            selectable.elementId = view.id;
            selectable.floorId = view.floorId;
            selectable.sourceId = view.parentId;
            selectable.view = view;
        }

        private void RememberOriginalMaterials(GameObject go)
        {
            if (go == null) return;
            foreach (Renderer renderer in go.GetComponentsInChildren<Renderer>())
            {
                if (renderer != null && !originalMaterialByRenderer.ContainsKey(renderer))
                {
                    originalMaterialByRenderer.Add(renderer, renderer.sharedMaterial);
                }
            }
        }

        private GameObject AddPolygonLine(string name, List<List<double>> polygon, float y, Material material, float width, string category, int floorId, string id)
        {
            GameObject go = new GameObject(name);
            go.transform.SetParent(root.transform, false);
            LineRenderer lr = go.AddComponent<LineRenderer>();
            lr.useWorldSpace = true;
            lr.loop = true;
            lr.positionCount = polygon.Count;
            lr.startWidth = width;
            lr.endWidth = width;
            lr.sharedMaterial = material;
            for (int i = 0; i < polygon.Count; i++) lr.SetPosition(i, ToWorld(polygon[i], floorId, y - FloorY(floorId)));

            E1ElementView view = go.AddComponent<E1ElementView>();
            view.id = id;
            view.category = category;
            view.floorId = floorId;
            if (category == "tributary") view.parentId = id.Split(new[] { "__" }, StringSplitOptions.None)[0];
            Register(view, false);
            return go;
        }

        private void AddGenericPolyline(string name, List<List<double>> points, Material material, float width, Transform parent)
        {
            GameObject go = new GameObject(name);
            go.transform.SetParent(parent, false);
            LineRenderer lr = go.AddComponent<LineRenderer>();
            lr.useWorldSpace = true;
            lr.loop = true;
            lr.positionCount = points.Count;
            lr.startWidth = width;
            lr.endWidth = width;
            lr.sharedMaterial = material;
            int floorId = parent.GetComponent<E1ElementView>() != null ? parent.GetComponent<E1ElementView>().floorId : 0;
            for (int i = 0; i < points.Count; i++) lr.SetPosition(i, ToUnityPoint(points[i], floorId));
        }

        private void AddLocalAxes(string ownerId, int floorId, Vector3 start, Vector3 end)
        {
            Vector3 localX = (end - start).normalized;
            if (localX.sqrMagnitude < 0.0001f) localX = Vector3.right;
            Vector3 referenceUp = Vector3.up;
            Vector3 localZ = Vector3.Cross(localX, referenceUp).normalized;
            if (localZ.sqrMagnitude < 0.0001f) localZ = Vector3.forward;
            Vector3 localY = Vector3.Cross(localZ, localX).normalized;

            Vector3 origin = (start + end) * 0.5f + Vector3.up * 0.38f;
            float scale = Mathf.Clamp(Vector3.Distance(start, end) * 0.12f, 0.8f, 1.8f);
            GameObject go = new GameObject("LOCAL_AXES_" + ownerId);
            go.transform.SetParent(axesRoot.transform, false);
            AddAxisLine(go.transform, "x", origin, localX, scale, localXMaterial);
            AddAxisLine(go.transform, "y", origin, localY, scale * 0.75f, localYMaterial);
            AddAxisLine(go.transform, "z", origin, localZ, scale * 0.75f, localZMaterial);

            E1ElementView view = go.AddComponent<E1ElementView>();
            view.id = "LOCAL_AXES_" + ownerId;
            view.category = "local_axis";
            view.parentId = ownerId;
            view.floorId = floorId;
            Register(view, false);
        }

        private void AddAxisLine(Transform parent, string name, Vector3 origin, Vector3 direction, float length, Material material)
        {
            GameObject go = new GameObject(name);
            go.transform.SetParent(parent, false);
            LineRenderer lr = go.AddComponent<LineRenderer>();
            lr.useWorldSpace = true;
            lr.positionCount = 2;
            lr.SetPosition(0, origin);
            lr.SetPosition(1, origin + direction.normalized * length);
            lr.startWidth = 0.06f;
            lr.endWidth = 0.02f;
            lr.sharedMaterial = material;
        }

        private void AddLabel(string id, Vector3 position, int floorId)
        {
            GameObject go = new GameObject("ID_" + id);
            go.transform.SetParent(labelsRoot.transform, false);
            go.transform.position = position;
            TextMesh text = go.AddComponent<TextMesh>();
            text.text = id;
            text.characterSize = 0.26f;
            text.anchor = TextAnchor.MiddleCenter;
            text.alignment = TextAlignment.Center;
            text.color = Color.white;

            E1ElementView view = go.AddComponent<E1ElementView>();
            view.id = "ID_" + id;
            view.category = "id";
            view.parentId = id;
            view.floorId = floorId;
            Register(view, false);
        }

        private Mesh BuildPolygonMesh(List<List<double>> polygon, float y)
        {
            List<Vector2> points2 = CleanPolygon(polygon);
            if (points2.Count < 3) return null;
            List<int> triangles = Triangulate(points2);
            if (triangles.Count < 3) triangles = FanTriangulate(points2.Count);

            Vector3[] vertices = new Vector3[points2.Count];
            for (int i = 0; i < points2.Count; i++) vertices[i] = new Vector3(points2[i].x, y, points2[i].y);
            Mesh mesh = new Mesh();
            mesh.name = "polygon_mesh";
            mesh.vertices = vertices;
            mesh.triangles = triangles.ToArray();
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        private Mesh BuildGenericPolygonMesh(List<List<double>> polygon)
        {
            List<Vector3> points3 = polygon.Where(IsPoint2).Select(point => ToUnityPoint(point, 0)).ToList();
            if (points3.Count > 2 && Vector3.Distance(points3[0], points3[points3.Count - 1]) < 0.001f) points3.RemoveAt(points3.Count - 1);
            if (points3.Count < 3) return null;
            List<Vector2> points2 = points3.Select(p => new Vector2(p.x, p.z)).ToList();
            List<int> triangles = Triangulate(points2);
            if (triangles.Count < 3) triangles = FanTriangulate(points2.Count);
            Mesh mesh = new Mesh { name = "generic_polygon_mesh" };
            mesh.vertices = points3.ToArray();
            mesh.triangles = triangles.ToArray();
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        private List<Vector2> CleanPolygon(List<List<double>> polygon)
        {
            List<Vector2> points = new List<Vector2>();
            foreach (List<double> point in polygon)
            {
                if (!IsPoint2(point)) continue;
                Vector2 p = new Vector2((float)point[0], (float)point[1]);
                if (points.Count == 0 || Vector2.Distance(points[points.Count - 1], p) > 0.001f) points.Add(p);
            }
            if (points.Count > 2 && Vector2.Distance(points[0], points[points.Count - 1]) < 0.001f) points.RemoveAt(points.Count - 1);
            return points;
        }

        private List<int> Triangulate(List<Vector2> points)
        {
            List<int> indices = new List<int>();
            List<int> remaining = new List<int>();
            for (int i = 0; i < points.Count; i++) remaining.Add(i);
            bool ccw = SignedArea(points) > 0f;
            int guard = 0;
            while (remaining.Count > 3 && guard < points.Count * points.Count)
            {
                guard++;
                bool clipped = false;
                for (int i = 0; i < remaining.Count; i++)
                {
                    int prev = remaining[(i - 1 + remaining.Count) % remaining.Count];
                    int curr = remaining[i];
                    int next = remaining[(i + 1) % remaining.Count];
                    if (!IsConvex(points[prev], points[curr], points[next], ccw)) continue;
                    if (ContainsAnyPoint(points, remaining, prev, curr, next)) continue;
                    if (ccw) { indices.Add(prev); indices.Add(curr); indices.Add(next); }
                    else { indices.Add(prev); indices.Add(next); indices.Add(curr); }
                    remaining.RemoveAt(i);
                    clipped = true;
                    break;
                }
                if (!clipped) break;
            }
            if (remaining.Count == 3)
            {
                if (ccw) { indices.Add(remaining[0]); indices.Add(remaining[1]); indices.Add(remaining[2]); }
                else { indices.Add(remaining[0]); indices.Add(remaining[2]); indices.Add(remaining[1]); }
            }
            return indices;
        }

        private List<int> FanTriangulate(int count)
        {
            List<int> triangles = new List<int>();
            for (int i = 1; i < count - 1; i++)
            {
                triangles.Add(0);
                triangles.Add(i);
                triangles.Add(i + 1);
            }
            return triangles;
        }

        private float SignedArea(List<Vector2> points)
        {
            float area = 0f;
            for (int i = 0; i < points.Count; i++)
            {
                Vector2 a = points[i];
                Vector2 b = points[(i + 1) % points.Count];
                area += a.x * b.y - b.x * a.y;
            }
            return area * 0.5f;
        }

        private bool IsConvex(Vector2 a, Vector2 b, Vector2 c, bool ccw)
        {
            float cross = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
            return ccw ? cross > 0.00001f : cross < -0.00001f;
        }

        private bool ContainsAnyPoint(List<Vector2> points, List<int> remaining, int ia, int ib, int ic)
        {
            Vector2 a = points[ia];
            Vector2 b = points[ib];
            Vector2 c = points[ic];
            foreach (int index in remaining)
            {
                if (index == ia || index == ib || index == ic) continue;
                if (PointInTriangle(points[index], a, b, c)) return true;
            }
            return false;
        }

        private bool PointInTriangle(Vector2 p, Vector2 a, Vector2 b, Vector2 c)
        {
            float d1 = Sign(p, a, b);
            float d2 = Sign(p, b, c);
            float d3 = Sign(p, c, a);
            bool hasNeg = d1 < 0f || d2 < 0f || d3 < 0f;
            bool hasPos = d1 > 0f || d2 > 0f || d3 > 0f;
            return !(hasNeg && hasPos);
        }

        private float Sign(Vector2 p1, Vector2 p2, Vector2 p3)
        {
            return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);
        }

        private void SetTransformBetween(Transform transformToSet, Vector3 start, Vector3 end, float width, float depth)
        {
            Vector3 direction = end - start;
            float length = Mathf.Max(direction.magnitude, 0.05f);
            transformToSet.position = (start + end) * 0.5f;
            if (direction.sqrMagnitude < 0.0001f)
            {
                transformToSet.rotation = Quaternion.identity;
            }
            else
            {
                transformToSet.rotation = Quaternion.FromToRotation(Vector3.right, direction.normalized);
            }
            transformToSet.localScale = new Vector3(length, depth, width);
        }

        private Vector3 ToWorld(List<double> point, int floorId, float yOffset = 0f)
        {
            return ModelToUnity(point, floorId, yOffset);
        }

        private Vector3 ToUnityPoint(List<double> point, int floorId)
        {
            return ModelToUnity(point, floorId, 0f);
        }

        private Vector3 ModelToUnity(List<double> point, int floorId, float verticalOffset = 0f)
        {
            if (point == null || point.Count < 2) return Vector3.zero;

            // Coordinate contract: model/OpenSees [X, Y, Z] maps to Unity [X, Z, Y].
            // When only plan coordinates are available, floorId supplies physical Z.
            if (point.Count >= 3)
            {
                return new Vector3((float)point[0], (float)point[2] + verticalOffset, (float)point[1]);
            }

            return new Vector3((float)point[0], FloorY(floorId) + verticalOffset, (float)point[1]);
        }

        private bool IsPoint2(List<double> point)
        {
            return point != null && point.Count >= 2 && !double.IsNaN(point[0]) && !double.IsNaN(point[1]);
        }

        private float FloorY(int floorId)
        {
            if (FloorElevations.TryGetValue(floorId, out float y)) return y;
            return floorId * FloorHeight;
        }

        private string FloorLabel(int floorId)
        {
            if (floorId == -1) return "1S";
            return "P" + floorId.ToString(CultureInfo.InvariantCulture);
        }

        private bool FloorMatches(int floorId)
        {
            string selected = floorOptions[floorIndex];
            if (selected == "ALL") return true;
            if (floorId == 0 && selected == "1S") return true;
            return selected == FloorLabel(floorId);
        }

        private bool CategoryVisible(E1ElementView view)
        {
            switch (view.category)
            {
                case "node": return showNodes;
                case "beam": return showBeams;
                case "column": return showColumns;
                case "wall": return showWalls && (showVisualOnly || HasVerifiedResponseForView(view));
                case "support": return showSupports && (showVisualOnly || HasVerifiedSupportMapping(view));
                case "diaphragm": return showDiaphragms;
                case "id": return showIds;
                case "local_axis": return showLocalAxes || (!string.IsNullOrEmpty(selectedId) && view.parentId == selectedId);
                case "tributary": return showTributaryAreas || (!string.IsNullOrEmpty(selectedBeamId) && view.parentId == selectedBeamId);
                case "slab": return showSlabs;
                case "blocker": return showBlockers;
                default: return true;
            }
        }

        private bool HasVerifiedSupportMapping(E1ElementView view)
        {
            E1StructuralSupportMapping mapping = SupportMappingForView(view);
            return mapping != null && E1AnalysisStatus.IsVerified(mapping.fe_status);
        }

        private bool HasVerifiedResponseForView(E1ElementView view)
        {
            E1ResponseElement matched = MatchResponseElement(view);
            return matched != null && E1AnalysisStatus.IsVerified(matched.analysis_status);
        }

        private bool ShowUnverifiedStatus(string status)
        {
            if (string.Equals(status, "UNMATCHED_STRUCTURAL_RESPONSE", StringComparison.OrdinalIgnoreCase)) return showUnmatched;
            if (string.Equals(status, "RECONCILED_SCOPING_RESPONSE", StringComparison.OrdinalIgnoreCase)) return showScoping;
            if (string.Equals(status, "FLOATING_LOAD_PATH_BLOCKER", StringComparison.OrdinalIgnoreCase) || string.Equals(status, "SEGMENTATION_STUB", StringComparison.OrdinalIgnoreCase)) return showFloatingStubs;
            if (string.Equals(status, "VISUAL_ONLY", StringComparison.OrdinalIgnoreCase) || string.Equals(status, "GEOMETRIC_BLOCKER", StringComparison.OrdinalIgnoreCase)) return showVisualOnly;
            return false;
        }

        private void ApplyVisibility()
        {
            foreach (E1ElementView view in views)
            {
                bool visible = FloorMatches(view.floorId) && CategoryVisible(view) && BuildingMatches(view);
                view.gameObject.SetActive(visible);
                if (view.category == "tributary")
                {
                    MeshRenderer mr = view.GetComponent<MeshRenderer>();
                    if (mr != null) mr.sharedMaterial = view.parentId == selectedBeamId ? selectedTributaryMaterial : tributaryMaterial;
                }
            }
            ApplyResponseVisualVisibility();
        }

        private bool IsMultiBuilding
        {
            get { return data != null && data.buildings != null && data.buildings.Count > 1; }
        }

        private bool BuildingMatches(E1ElementView view)
        {
            if (!IsMultiBuilding) return true;
            if (string.IsNullOrEmpty(activeBuildingFilter) || activeBuildingFilter == "Both") return true;
            string building = ResolveBuilding(view);
            return !string.IsNullOrEmpty(building) && string.Equals(building, activeBuildingFilter, StringComparison.Ordinal);
        }

        private string ResolveBuilding(E1ElementView view)
        {
            string building = null;
            if (view != null && !string.IsNullOrEmpty(view.building)) building = view.building;
            if (string.IsNullOrEmpty(building) && view != null && !string.IsNullOrEmpty(view.parentId))
            {
                if (elementById.TryGetValue(view.parentId, out E1ElementView parent) && parent != null && !string.IsNullOrEmpty(parent.building))
                    building = parent.building;
            }
            if (string.IsNullOrEmpty(building) && view != null && !string.IsNullOrEmpty(view.id))
            {
                if (elementById.TryGetValue(view.id, out E1ElementView self) && self != null && !string.IsNullOrEmpty(self.building))
                    building = self.building;
            }
            if (string.Equals(building, "EDIFICIO_1", StringComparison.OrdinalIgnoreCase)) building = "E1";
            if (string.IsNullOrEmpty(building)) building = "E1";
            return building;
        }

        private bool ResponseBuildingMatches(GameObject go)
        {
            if (!IsMultiBuilding || string.IsNullOrEmpty(activeBuildingFilter) || activeBuildingFilter == "Both") return true;
            string building;
            if (responseVisualBuilding.TryGetValue(go, out building))
                return string.Equals(building, activeBuildingFilter, StringComparison.Ordinal);
            return true;
        }

        private string BuildingFromResponseKey(string key)
        {
            if (string.IsNullOrEmpty(key)) return null;
            if (key.StartsWith("E2::", StringComparison.Ordinal)) return "E2";
            if (key.StartsWith("E1::", StringComparison.Ordinal)) return "E1";
            return null;
        }

        private void ApplyResponseVisualVisibility()
        {
            foreach (GameObject go in deformedLines) if (go != null) go.SetActive(showDeformed && ResponseBuildingMatches(go));
            foreach (GameObject go in deformedBlockedLines) if (go != null) go.SetActive(showDeformedBlocked && ResponseBuildingMatches(go));
            foreach (GameObject go in diagramLines) if (go != null) go.SetActive(showDiagrams && ResponseBuildingMatches(go));
            bool loadsVisible = showLoads && selectedView != null && FloorMatches(selectedView.floorId) && BuildingMatches(selectedView);
            foreach (GameObject go in selectedLoadLines) if (go != null) go.SetActive(loadsVisible);
        }

        private void ApplyBlockerHighlight()
        {
            ResetModelMaterials();
            if (responseData == null || !showBlockerHighlight)
            {
                ApplySelectionHighlight(selectedView);
                return;
            }

            foreach (E1ElementView view in views)
            {
                if (view.category != "column" && view.category != "beam") continue;
                E1ResponseElement matched = MatchResponseElement(view);
                if (matched == null) continue;
                Material mat = null;
                if (E1AnalysisStatus.IsBlocking(matched.analysis_status)) mat = floatingMaterial;
                else if (string.Equals(matched.analysis_status, E1AnalysisStatus.Scoping, StringComparison.OrdinalIgnoreCase)) mat = scopingMaterial;
                else if (E1AnalysisStatus.IsVerified(matched.analysis_status)) mat = verifiedMaterial;
                if (mat == null) continue;
                Renderer renderer = view.GetComponentInChildren<Renderer>();
                if (renderer != null) renderer.sharedMaterial = mat;
            }
            ApplySelectionHighlight(selectedView);
        }

        private void ResetModelMaterials()
        {
            foreach (KeyValuePair<Renderer, Material> pair in originalMaterialByRenderer)
            {
                if (pair.Key != null) pair.Key.sharedMaterial = pair.Value;
            }
        }

        private void ClearSelectionHighlight()
        {
            if (selectedView == null) return;
            foreach (Renderer renderer in selectedView.GetComponentsInChildren<Renderer>())
            {
                if (renderer != null && originalMaterialByRenderer.TryGetValue(renderer, out Material original))
                {
                    renderer.sharedMaterial = original;
                }
            }
            selectedView = null;
            if (showBlockerHighlight) ApplyBlockerHighlight();
        }

        private void ApplySelectionHighlight(E1ElementView view)
        {
            if (view == null || selectedMaterial == null) return;
            foreach (Renderer renderer in view.GetComponentsInChildren<Renderer>())
            {
                if (renderer == null) continue;
                if (!originalMaterialByRenderer.ContainsKey(renderer)) originalMaterialByRenderer.Add(renderer, renderer.sharedMaterial);
                renderer.sharedMaterial = selectedMaterial;
            }
        }

        private E1ResponseElement MatchResponseElement(E1ElementView view)
        {
            if (view == null) return null;
            E1StructuralElementMapping mapping = MappingForView(view);
            if (mapping != null && !string.IsNullOrWhiteSpace(mapping.fe_element_id))
            {
                if (responseElementById.TryGetValue(mapping.fe_element_id, out E1ResponseElement mapped)) return mapped;
            }

            if (responseElementById.TryGetValue(view.id, out E1ResponseElement byId)) return byId;

            if (responseData == null || responseData.elements == null) return null;
            List<double> rawI = null;
            List<double> rawJ = null;
            if (view.beam != null)
            {
                rawI = view.beam.node_i;
                rawJ = view.beam.node_j;
            }
            else if (view.generic != null)
            {
                rawI = view.generic.node_i;
                rawJ = view.generic.node_j;
            }

            if (rawI == null || rawJ == null) return null;
            foreach (KeyValuePair<string, E1ResponseElement> pair in responseData.elements)
            {
                if (pair.Value == null) continue;
                if (pair.Value.kind != view.category) continue;
                bool same = ResponseCoordsNear(pair.Value.node_i, rawI) && ResponseCoordsNear(pair.Value.node_j, rawJ);
                bool reversed = ResponseCoordsNear(pair.Value.node_i, rawJ) && ResponseCoordsNear(pair.Value.node_j, rawI);
                if (same || reversed) return pair.Value;
            }
            return null;
        }

        private E1StructuralElementMapping MappingForView(E1ElementView view)
        {
            if (view == null || string.IsNullOrEmpty(view.id)) return null;
            if (structuralElementMappingByVisualId.TryGetValue(view.id, out E1StructuralElementMapping mapping)) return mapping;
            if (view.beam != null && structuralElementMappingByVisualId.TryGetValue(view.beam.beam_id, out mapping)) return mapping;
            if (view.generic != null)
            {
                string genericId = GenericId(view.generic, view.category);
                if (structuralElementMappingByVisualId.TryGetValue(genericId, out mapping)) return mapping;
            }
            return null;
        }

        private void ClearSelection()
        {
            ClearSelectionHighlight();
            selectedId = "";
            selectedBeamId = "";
            selectionText = "Selecciona una viga, nodo, losa, tributaria o blocker.";
            ClearSelectedLoadVisuals();
            BuildResponseVisualizations();
            ApplyVisibility();
        }

        private void SearchById(string query)
        {
            if (string.IsNullOrWhiteSpace(query)) return;
            E1ElementView view;
            if (!elementById.TryGetValue(query.Trim(), out view))
            {
                view = elementById.Values.FirstOrDefault(v => v.id.IndexOf(query.Trim(), StringComparison.OrdinalIgnoreCase) >= 0);
            }
            if (view == null)
            {
                statusText = "No se encontro ID: " + query;
                return;
            }
            Select(view);
            ZoomTo(view.transform.position);
        }

        private void Select(E1ElementView view)
        {
            if (view == null) return;
            ClearSelectionHighlight();
            selectedView = view;
            ApplySelectionHighlight(view);
            selectedId = view.id;
            selectedBeamId = view.category == "beam" && view.beam != null ? view.beam.beam_id : "";
            selectionText = SelectionText(view);
            inspectorCollapsed = false;
            inspectorScroll = Vector2.zero;
            BuildResponseVisualizations();
            RebuildSelectedLoadVisuals();
            ApplyVisibility();
        }

        private string SelectionText(E1ElementView view)
        {
            StringBuilder sb = new StringBuilder();
            if (view.category == "beam" && view.beam != null) sb.Append(BeamText(view.beam));
            else if (view.category == "node" && view.node != null) sb.Append(NodeText(view.node));
            else if (view.category == "tributary" && view.tributary != null) sb.Append(TributaryText(view.beam, view.tributary));
            else if (view.category == "slab" && view.slab != null) sb.Append(SlabText(view.slab));
            else if (view.category == "blocker" && view.blocker != null) sb.Append(BlockerText(view.blocker));
            else if (view.generic != null) sb.Append(GenericText(view.category, view.generic));
            else sb.Append(view.id);

            AppendResponseInfo(sb, view);
            return sb.ToString();
        }

        private string InspectorText(E1ElementView view, int tab)
        {
            if (view == null) return "No selection.";
            switch (tab)
            {
                case 0: return InspectorPropertiesText(view);
                case 1: return InspectorLoadsText(view);
                case 2: return InspectorForcesText(view);
                case 3: return InspectorDisplacementsText(view);
                case 4: return InspectorDiagramsText(view);
                default: return selectionText;
            }
        }

        private string AnalysisStatusForView(E1ElementView view)
        {
            if (view == null) return "-";
            if (view.category == "wall" || view.category == "slab" || view.category == "tributary" || view.category == "blocker") return "VISUAL_ONLY";
            if (view.category == "support")
            {
                E1StructuralSupportMapping supportMapping = SupportMappingForView(view);
                if (supportMapping != null && !string.IsNullOrEmpty(supportMapping.fe_status)) return supportMapping.fe_status;
                return "VISUAL_ONLY";
            }
            E1StructuralElementMapping mapping = MappingForView(view);
            if (mapping != null && !string.IsNullOrEmpty(mapping.fe_status)) return mapping.fe_status;
            E1ResponseElement matched = MatchResponseElement(view);
            if (matched != null && !string.IsNullOrEmpty(matched.analysis_status)) return matched.analysis_status;
            if (view.category == "node") return NodeAnalysisStatus(view.node);
            return "UNMATCHED_STRUCTURAL_RESPONSE";
        }

        private string FriendlyAnalysisStatus(string status)
        {
            if (string.Equals(status, E1AnalysisStatus.Verified, StringComparison.OrdinalIgnoreCase)) return "Structural response: verified connected FE member";
            if (string.Equals(status, E1AnalysisStatus.Scoping, StringComparison.OrdinalIgnoreCase)) return "Structural response: reconciled scoping FE member";
            if (string.Equals(status, E1AnalysisStatus.FloatingBlocker, StringComparison.OrdinalIgnoreCase)) return "Structural response: blocked by floating load path";
            if (string.Equals(status, "VISUAL_ONLY", StringComparison.OrdinalIgnoreCase)) return "Structural response: visual geometry only";
            return "Structural response: not matched to verified FE member";
        }

        private string MappingReasonForView(E1ElementView view)
        {
            E1StructuralElementMapping elementMapping = MappingForView(view);
            if (elementMapping != null && !string.IsNullOrEmpty(elementMapping.reason)) return elementMapping.reason;
            E1StructuralSupportMapping supportMapping = SupportMappingForView(view);
            if (supportMapping != null && !string.IsNullOrEmpty(supportMapping.reason)) return supportMapping.reason;
            if (view != null && view.category == "node" && structuralNodeMappingByVisualId.TryGetValue(view.id, out E1StructuralNodeMapping nodeMapping) && !string.IsNullOrEmpty(nodeMapping.reason)) return nodeMapping.reason;
            if (view != null && view.category == "wall") return "Walls are visual-only in the final FE model; no N/V/M invented.";
            return "No conservative visual-to-FE mapping is available for this object.";
        }

        private string NodeAnalysisStatus(E1NodeInfo node)
        {
            if (node == null || responseData == null || responseData.node_analysis_status == null) return "VISUAL_ONLY";
            if (structuralNodeMappingByVisualId.TryGetValue(node.id, out E1StructuralNodeMapping mapping) && !string.IsNullOrEmpty(mapping.fe_status)) return mapping.fe_status;
            List<double> raw = new List<double> { node.point2.x, node.point2.y, FloorY(node.floorId) };
            string tag = FindResponseNodeTag(raw);
            return tag != null && responseData.node_analysis_status.TryGetValue(tag, out string status) ? status : "UNMATCHED_STRUCTURAL_RESPONSE";
        }

        private string InspectorPropertiesText(E1ElementView view)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("=== SELECTED ===");
            sb.AppendLine("TYPE: " + view.category.ToUpperInvariant());
            sb.AppendLine("ID: " + view.id);
            sb.AppendLine("FLOOR: " + FloorLabel(view.floorId));
            sb.AppendLine(FriendlyAnalysisStatus(AnalysisStatusForView(view)));
            sb.AppendLine("INTERNAL STATUS: " + AnalysisStatusForView(view));
            sb.AppendLine("REASON: " + MappingReasonForView(view));
            AppendMappingDetails(sb, view);
            sb.AppendLine();

            if (view.category == "beam" && view.beam != null) AppendBeamProperties(sb, view);
            else if (view.category == "node" && view.node != null) sb.Append(NodeText(view.node));
            else if (view.category == "support" && view.generic != null) AppendSupportProperties(sb, view);
            else if (view.category == "wall" && view.generic != null) AppendWallProperties(sb, view.generic);
            else if (view.category == "column" && view.generic != null) AppendColumnProperties(sb, view);
            else if (view.category == "blocker" && view.blocker != null) sb.Append(BlockerText(view.blocker));
            else if (view.category == "slab" && view.slab != null) sb.Append(SlabText(view.slab));
            else if (view.generic != null) sb.Append(GenericText(view.category, view.generic));
            else sb.Append(selectionText);
            return sb.ToString();
        }

        private void AppendMappingDetails(StringBuilder sb, E1ElementView view)
        {
            E1StructuralElementMapping mapping = MappingForView(view);
            if (mapping == null) return;
            sb.AppendLine("FE ID: " + (string.IsNullOrEmpty(mapping.fe_element_id) ? "-" : mapping.fe_element_id));
            sb.AppendLine("Mapping confidence: " + (mapping.mapping_confidence ?? "-"));
            sb.AppendLine("Transform region: " + (mapping.transform_region ?? "-"));
            if (!string.IsNullOrEmpty(mapping.raw_fe_status)) sb.AppendLine("Raw FE status: " + mapping.raw_fe_status);
            if (mapping.xy_distance_m.HasValue) sb.AppendLine("XY residual: " + F(mapping.xy_distance_m.Value) + " m");
            if (mapping.transformed_xy_distance_m.HasValue) sb.AppendLine("Transformed XY residual: " + F(mapping.transformed_xy_distance_m.Value) + " m");
            if (mapping.transformed_distance_m.HasValue) sb.AppendLine("Transformed residual: " + F(mapping.transformed_distance_m.Value) + " m");
            if (mapping.endpoint_avg_distance_m.HasValue) sb.AppendLine("Endpoint avg residual: " + F(mapping.endpoint_avg_distance_m.Value) + " m");
            if (mapping.midpoint_distance_m.HasValue) sb.AppendLine("Midpoint residual: " + F(mapping.midpoint_distance_m.Value) + " m");
            if (mapping.angle_deg.HasValue) sb.AppendLine("Angle delta: " + F(mapping.angle_deg.Value) + " deg");
            if (mapping.height_delta_m.HasValue) sb.AppendLine("Height delta: " + F(mapping.height_delta_m.Value) + " m");
            if (mapping.nearest_transformed_distance_m.HasValue) sb.AppendLine("Nearest transformed distance: " + F(mapping.nearest_transformed_distance_m.Value) + " m");
        }

        private void AppendBeamProperties(StringBuilder sb, E1ElementView view)
        {
            E1Beam beam = view.beam;
            E1ResponseElement fe = FeMetadataForView(view);
            sb.AppendLine("=== IDENTIFICATION ===");
            sb.AppendLine("beam ID: " + beam.beam_id);
            sb.AppendLine("floor: " + FloorLabel(beam.floor_id));
            sb.AppendLine("node i: " + PointText(beam.node_i));
            sb.AppendLine("node j: " + PointText(beam.node_j));
            sb.AppendLine("coordinates i/j: " + PointText(beam.node_i) + " -> " + PointText(beam.node_j));
            sb.AppendLine("length: " + F(beam.longitud_m) + " m");
            sb.AppendLine();
            if (HasFeStructuralMetadata(fe))
            {
                AppendFeStructuralProperties(sb, view, fe);
                return;
            }
            sb.AppendLine("=== SECTION / MATERIAL ===");
            sb.AppendLine("section ID: -");
            sb.AppendLine("b: " + Maybe(beam.section?.width_m ?? beam.section?.b, " m"));
            sb.AppendLine("h: " + Maybe(beam.section?.height_m ?? beam.section?.h, " m"));
            sb.AppendLine("A: -");
            sb.AppendLine("Iy: -");
            sb.AppendLine("Iz: -");
            sb.AppendLine("J: -");
            sb.AppendLine("E: -");
            sb.AppendLine("G: -");
            sb.AppendLine("material: -");
            sb.AppendLine("OpenSees element type: elasticBeamColumn where available in response model");
            sb.AppendLine("geomTransf: Linear where available in response model");
            sb.AppendLine();
            sb.AppendLine("=== CONNECTIVITY ===");
            sb.AppendLine("connected elements at i/j: " + ConnectedMembersText(beam));
            sb.AppendLine("diaphragm: floor diaphragm inferred by level");
            sb.AppendLine("releases/end conditions: not provided in gravity JSON");
        }

        private void AppendColumnProperties(StringBuilder sb, E1ElementView view)
        {
            E1GenericElement item = view.generic;
            E1ResponseElement fe = FeMetadataForView(view);
            sb.AppendLine("=== COLUMN ===");
            sb.AppendLine("column ID: " + GenericId(item, "column"));
            sb.AppendLine("floor/story: " + FloorLabel(item.floor_id));
            sb.AppendLine("node i: " + PointText(item.node_i));
            sb.AppendLine("node j: " + PointText(item.node_j));
            sb.AppendLine("height: " + Maybe(item.height_m ?? item.length_m, " m"));
            if (HasFeStructuralMetadata(fe))
            {
                sb.AppendLine();
                AppendFeStructuralProperties(sb, view, fe);
                sb.AppendLine("load-path status: " + AnalysisStatusForView(view));
                return;
            }
            sb.AppendLine("section: " + SectionText(item.section));
            sb.AppendLine("dimensions: width=" + Maybe(item.width_m ?? item.section?.width_m ?? item.section?.b, " m") + ", depth=" + Maybe(item.depth_m ?? item.section?.height_m ?? item.section?.h, " m"));
            sb.AppendLine("A/Iy/Iz/J: - / - / - / -");
            sb.AppendLine("E/G/material: - / - / hormigon armado assumed by analysis contract");
            sb.AppendLine("local axes: shown when selected or toggle ON");
            sb.AppendLine("connectivity: " + GenericConnectivityText(item, "column"));
            sb.AppendLine("load-path status: " + AnalysisStatusForView(view));
            sb.AppendLine("end conditions: not explicit in visual JSON");
        }

        private E1ResponseElement FeMetadataForView(E1ElementView view)
        {
            if (view == null) return null;

            E1StructuralElementMapping mapping = MappingForView(view);
            if (mapping != null && !string.IsNullOrWhiteSpace(mapping.fe_element_id))
            {
                if (responseForcesById.TryGetValue(mapping.fe_element_id, out E1ElementForcesResponse mappedForces)) return mappedForces;
                if (responseElementById.TryGetValue(mapping.fe_element_id, out E1ResponseElement mappedElement)) return mappedElement;
            }

            if (!string.IsNullOrWhiteSpace(view.id))
            {
                if (responseForcesById.TryGetValue(view.id, out E1ElementForcesResponse byViewIdForces)) return byViewIdForces;
                if (responseElementById.TryGetValue(view.id, out E1ResponseElement byViewIdElement)) return byViewIdElement;
            }

            E1ResponseElement matched = MatchResponseElement(view);
            if (matched == null) return null;
            string responseId = elementOfId(matched);
            if (!string.IsNullOrWhiteSpace(responseId) && responseForcesById.TryGetValue(responseId, out E1ElementForcesResponse matchedForces)) return matchedForces;
            string forcesId = FindResponseForcesId(matched);
            if (!string.IsNullOrWhiteSpace(forcesId) && responseForcesById.TryGetValue(forcesId, out E1ElementForcesResponse foundForces)) return foundForces;
            return matched;
        }

        private bool HasFeStructuralMetadata(E1ResponseElement fe)
        {
            return fe != null &&
                   (!string.IsNullOrWhiteSpace(fe.element_type) ||
                    fe.section != null ||
                    fe.material != null ||
                    fe.geomTransf != null ||
                    fe.connectivity != null);
        }

        private void AppendFeStructuralProperties(StringBuilder sb, E1ElementView view, E1ResponseElement fe)
        {
            sb.AppendLine("=== FE STRUCTURAL PROPERTIES ===");
            sb.AppendLine("FE ID: " + FeIdForView(view, fe));
            sb.AppendLine("Type: " + Dash(fe.element_type));
            sb.AppendLine("L FE: " + MaybeLength(ResponseLength(fe), " m"));
            sb.AppendLine();

            sb.AppendLine("SECTION");
            E1ResponseSection section = fe.section;
            sb.AppendLine("section ID: " + Dash(section != null ? section.section_id : null));
            sb.AppendLine("b = " + MaybeFormat(section != null ? section.b_m : null, " m", "F3"));
            sb.AppendLine("h = " + MaybeFormat(section != null ? section.h_m : null, " m", "F3"));
            sb.AppendLine("A = " + MaybeFormat(section != null ? section.A_m2 : null, " m2", "0.000000#"));
            sb.AppendLine("Iy = " + MaybeFormat(section != null ? section.Iy_m4 : null, " m4", "0.000000#"));
            sb.AppendLine("Iz = " + MaybeFormat(section != null ? section.Iz_m4 : null, " m4", "0.000000#"));
            sb.AppendLine("J = " + MaybeFormat(section != null ? section.J_m4 : null, " m4", "0.000000#"));
            sb.AppendLine();

            sb.AppendLine("MATERIAL");
            E1ResponseMaterial material = fe.material;
            sb.AppendLine(Dash(material != null ? material.name : null));
            sb.AppendLine("E = " + MaybeGPa(material != null ? material.E_Pa : null));
            sb.AppendLine("G = " + MaybeGPa(material != null ? material.G_Pa : null));
            sb.AppendLine("nu = " + MaybeFormat(material != null ? material.poisson : null, "", "F3"));
            sb.AppendLine();

            E1ResponseConnectivity connectivity = fe.connectivity;
            sb.AppendLine("CONNECTIVITY");
            sb.AppendLine("node i = " + MaybeInt(connectivity != null ? connectivity.node_i : null));
            sb.AppendLine("node j = " + MaybeInt(connectivity != null ? connectivity.node_j : null));
            sb.AppendLine("node i coords = " + PointText(connectivity != null ? connectivity.node_i_coords : null));
            sb.AppendLine("node j coords = " + PointText(connectivity != null ? connectivity.node_j_coords : null));
            sb.AppendLine("connected at i:");
            AppendStringList(sb, connectivity != null ? connectivity.connected_element_ids_at_i : null);
            sb.AppendLine("connected at j:");
            AppendStringList(sb, connectivity != null ? connectivity.connected_element_ids_at_j : null);
            sb.AppendLine("diaphragm floor = " + Dash(connectivity != null ? connectivity.diaphragm_floor : null));
            sb.AppendLine("master node = " + MaybeInt(connectivity != null ? connectivity.diaphragm_master_node : null));
            sb.AppendLine();

            E1ResponseGeomTransf geom = fe.geomTransf;
            sb.AppendLine("geomTransf: " + GeomTransfText(geom));
            sb.AppendLine("end releases: " + Dash(connectivity != null ? connectivity.end_releases : null));
            sb.AppendLine("connection model: " + Dash(connectivity != null ? connectivity.connection_model : null));
        }

        private string FeIdForView(E1ElementView view, E1ResponseElement fe)
        {
            E1StructuralElementMapping mapping = MappingForView(view);
            if (mapping != null && !string.IsNullOrWhiteSpace(mapping.fe_element_id)) return mapping.fe_element_id;
            string responseId = elementOfId(fe);
            return string.IsNullOrWhiteSpace(responseId) ? "-" : responseId;
        }

        private double? ResponseLength(E1ResponseElement fe)
        {
            if (fe == null || fe.node_i == null || fe.node_j == null || fe.node_i.Count < 3 || fe.node_j.Count < 3) return null;
            double dx = fe.node_j[0] - fe.node_i[0];
            double dy = fe.node_j[1] - fe.node_i[1];
            double dz = fe.node_j[2] - fe.node_i[2];
            return Math.Sqrt(dx * dx + dy * dy + dz * dz);
        }

        private string GeomTransfText(E1ResponseGeomTransf geom)
        {
            if (geom == null) return "-";
            string text = Dash(geom.type);
            if (geom.id.HasValue) text += " (ID " + geom.id.Value.ToString(CultureInfo.InvariantCulture) + ")";
            if (!string.IsNullOrWhiteSpace(geom.description)) text += ": " + geom.description;
            return text;
        }

        private void AppendStringList(StringBuilder sb, List<string> values)
        {
            if (values == null || values.Count == 0)
            {
                sb.AppendLine("-");
                return;
            }
            foreach (string value in values) sb.AppendLine(Dash(value));
        }

        private void AppendWallProperties(StringBuilder sb, E1GenericElement item)
        {
            sb.AppendLine("=== WALL ===");
            sb.AppendLine("wall ID: " + GenericId(item, "wall"));
            sb.AppendLine("floor: " + FloorLabel(item.floor_id));
            sb.AppendLine("node i: " + PointText(item.node_i));
            sb.AppendLine("node j: " + PointText(item.node_j));
            sb.AppendLine("vertices/geometry: line prism " + PointText(item.node_i) + " -> " + PointText(item.node_j));
            sb.AppendLine("thickness: " + Maybe(item.width_m ?? item.depth_m, " m"));
            sb.AppendLine("material: -");
            sb.AppendLine("connected nodes: visual endpoints");
            sb.AppendLine();
            sb.AppendLine("STRUCTURAL RESPONSE:");
            sb.AppendLine("NOT AVAILABLE — VISUAL GEOMETRY ONLY");
        }

        private void AppendSupportProperties(StringBuilder sb, E1ElementView view)
        {
            E1GenericElement item = view.generic;
            E1StructuralSupportMapping mapping = SupportMappingForView(view);
            string feNode = SupportNodeId(mapping);
            string building = ResolveBuilding(view);
            E1SupportRestraintResponse restraint = SupportRestraint(feNode, building);
            E1ReactionResponse reaction = SupportReaction(feNode, building);
            sb.AppendLine("=== SUPPORT ===");
            sb.AppendLine("visual ID: " + GenericId(item, "support"));
            sb.AppendLine("FE node: " + Dash(feNode));
            sb.AppendLine("visual coordinates: " + SupportVisualCoordinatesText(item));
            sb.AppendLine("FE coordinates: " + PointText(restraint != null ? restraint.coords : reaction != null ? reaction.coords : null));
            sb.AppendLine("mapping status: " + Dash(mapping != null ? mapping.fe_status : null));
            sb.AppendLine("mapping confidence: " + Dash(mapping != null ? mapping.transform_region : null));
            if (mapping != null && mapping.transformed_distance_m.HasValue) sb.AppendLine("mapping residual: " + F(mapping.transformed_distance_m.Value) + " m");
            sb.AppendLine();
            sb.AppendLine("=== RESTRAINTS ===");
            AppendSupportRestraints(sb, item, restraint);
            sb.AppendLine("Support description: " + DerivedSupportType(item, restraint));
            sb.AppendLine();
            AppendSupportResponseInfo(sb, view);
        }

        private string InspectorLoadsText(E1ElementView view)
        {
            if (view.category != "beam" || view.beam == null)
            {
                StringBuilder other = new StringBuilder();
                other.AppendLine("=== LOADS / LOAD PATH ===");
                other.AppendLine("DIRECT APPLIED MEMBER LOADS: None / not directly applied in the gravity JSON.");
                if (view.category == "column")
                {
                    other.AppendLine("LOAD PATH: gravity is transferred from slabs to beams and then through the frame columns.");
                    other.AppendLine("Connected members: " + (view.generic != null ? GenericConnectivityText(view.generic, "column") : "-"));
                    other.AppendLine("Story/floor: " + FloorLabel(view.floorId));
                    other.AppendLine("Response reason: " + MappingReasonForView(view));
                }
                else if (view.category == "support")
                {
                    other.AppendLine("LOAD PATH: support reactions are available only for supports mapped to restrained FE nodes.");
                    other.AppendLine("Response reason: " + MappingReasonForView(view));
                }
                else if (view.category == "wall")
                {
                    other.AppendLine("LOAD PATH: wall is visual-only in the final FE model; no direct wall load/response is reported.");
                }
                else if (view.category == "node")
                {
                    other.AppendLine("LOAD PATH: node receives member connectivity; no direct nodal gravity load is shown unless present in FE response metadata.");
                }
                return other.ToString();
            }
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("=== APPLIED LOADS ===");
            sb.Append(BeamSlabLoadText(view.beam));
            sb.AppendLine("tributary area: " + F(view.beam.area_tributaria_m2) + " m2");
            sb.AppendLine("qG: " + Maybe(view.beam.qG_kN_m2, " kN/m2"));
            sb.AppendLine("SC separately: " + (BeamScText(view.beam) ?? "-"));
            sb.AppendLine("P transferred: " + F(view.beam.P_kN) + " kN");
            sb.AppendLine("w distributed: " + F(view.beam.w_lineal_kN_m) + " kN/m");
            sb.AppendLine("P = qG * Atrib = " + Maybe(view.beam.qG_kN_m2, "") + " * " + F(view.beam.area_tributaria_m2));
            sb.AppendLine("w = P / L = " + F(view.beam.P_kN) + " / " + F(view.beam.longitud_m));
            sb.AppendLine("point loads: -");
            sb.AppendLine("additional line loads: -");
            sb.AppendLine();
            sb.AppendLine("Visual loads: toggle 'Loads (selected only)' draws arrows only for selected beam.");
            return sb.ToString();
        }

        private string InspectorForcesText(E1ElementView view)
        {
            StringBuilder sb = new StringBuilder();
            E1ResponseElement matched = MatchResponseElement(view);
            string status = AnalysisStatusForView(view);
            sb.AppendLine("=== STRUCTURAL RESPONSE ===");
            sb.AppendLine("analysis_status: " + status);
            if (matched == null)
            {
                sb.AppendLine(FriendlyAnalysisStatus(status));
                sb.AppendLine("Response unavailable because: " + MappingReasonForView(view));
                return sb.ToString();
            }
            if (!E1AnalysisStatus.IsVerified(status))
            {
                sb.AppendLine("WARNING: Structural response not verified: no traceable foundation load path.");
                sb.AppendLine("Reason: " + MappingReasonForView(view));
                if (E1AnalysisStatus.IsBlocking(status)) return sb.ToString();
            }
            AppendForcesSection(sb, view, matched);
            return sb.ToString();
        }

        private string InspectorDisplacementsText(E1ElementView view)
        {
            StringBuilder sb = new StringBuilder();
            if (view.category == "node" && view.node != null)
            {
                sb.Append(NodeText(view.node));
                AppendNodeResponseInfo(sb, view);
                return sb.ToString();
            }
            E1ResponseElement matched = MatchResponseElement(view);
            sb.AppendLine("=== DISPLACEMENTS ===");
            sb.AppendLine("analysis_status: " + AnalysisStatusForView(view));
            if (matched == null)
            {
                sb.AppendLine("Response unavailable because: " + MappingReasonForView(view));
                return sb.ToString();
            }
            if (E1AnalysisStatus.IsBlocking(AnalysisStatusForView(view)))
            {
                sb.AppendLine("No verified displacement response available for this member.");
                sb.AppendLine("Reason: " + MappingReasonForView(view));
                return sb.ToString();
            }
            AppendElementDisplacements(sb, matched);
            return sb.ToString();
        }

        private string InspectorDiagramsText(E1ElementView view)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("=== DIAGRAMS ===");
            sb.AppendLine("Longitudinal axis normalized 0 -> L.");
            sb.AppendLine("Only end forces are available; diagrams are linear interpolation between i and j, not curvature/envelope.");
            sb.AppendLine("Response status: " + AnalysisStatusForView(view));
            if (MatchResponseElement(view) == null || E1AnalysisStatus.IsBlocking(AnalysisStatusForView(view))) sb.AppendLine("No verified FE response available for this member. Reason: " + MappingReasonForView(view));
            return sb.ToString();
        }

        private void DrawInspectorMiniDiagrams(E1ElementView view)
        {
            E1ElementForcesResponse forces = ForcesForView(view);
            if (forces == null || forces.forces_kN == null)
            {
                GUILayout.Label("No force data available for mini-diagrams.");
                return;
            }

            DrawMiniDiagram("N", "kN", GetForce(forces, "N1"), GetForce(forces, "N2"));
            DrawMiniDiagram("Vy", "kN", GetForce(forces, "Vy1"), GetForce(forces, "Vy2"));
            DrawMiniDiagram("Vz", "kN", GetForce(forces, "Vz1"), GetForce(forces, "Vz2"));
            DrawMiniDiagram("T", "kN·m", GetForce(forces, "T1"), GetForce(forces, "T2"));
            DrawMiniDiagram("My", "kN·m", GetForce(forces, "My1"), GetForce(forces, "My2"));
            DrawMiniDiagram("Mz", "kN·m", GetForce(forces, "Mz1"), GetForce(forces, "Mz2"));
        }

        private void DrawMiniDiagram(string label, string unit, double vi, double vj)
        {
            double min = Math.Min(vi, vj);
            double max = Math.Max(vi, vj);
            double scale = Math.Max(Math.Abs(min), Math.Abs(max));
            GUILayout.Label(string.Format(CultureInfo.InvariantCulture, "{0} ({1})  min={2:F3}, max={3:F3}", label, unit, min, max));
            Rect r = GUILayoutUtility.GetRect(360f, 44f, GUILayout.ExpandWidth(true));
            GUI.Box(r, "");
            float mid = r.y + r.height * 0.5f;
            GUI.Box(new Rect(r.x + 8f, mid - 1f, r.width - 16f, 2f), "");

            if (scale < 1e-9) scale = 1.0;
            float x0 = r.x + 16f;
            float x1 = r.x + r.width - 16f;
            float y0 = mid - (float)(vi / scale) * (r.height * 0.34f);
            float y1 = mid - (float)(vj / scale) * (r.height * 0.34f);
            GUI.Box(new Rect(x0 - 3f, y0 - 3f, 6f, 6f), "");
            GUI.Box(new Rect(x1 - 3f, y1 - 3f, 6f, 6f), "");
            GUI.Label(new Rect(x0 - 4f, r.y + r.height - 16f, 60f, 16f), "0");
            GUI.Label(new Rect(x1 - 16f, r.y + r.height - 16f, 60f, 16f), "L");
            GUI.Label(new Rect(x0 + 8f, y0 - 10f, 150f, 18f), vi.ToString("F2", CultureInfo.InvariantCulture));
            GUI.Label(new Rect(x1 - 92f, y1 - 10f, 90f, 18f), vj.ToString("F2", CultureInfo.InvariantCulture));
        }

        private E1ElementForcesResponse ForcesForView(E1ElementView view)
        {
            string status = AnalysisStatusForView(view);
            if (E1AnalysisStatus.IsBlocking(status)) return null;
            E1ResponseElement matched = MatchResponseElement(view);
            if (matched == null || responseData == null || responseData.element_forces_kN == null) return null;
            string responseId = FindResponseForcesId(matched);
            return responseId != null && responseData.element_forces_kN.TryGetValue(responseId, out E1ElementForcesResponse forces) ? forces : null;
        }

        private void AppendResponseInfo(StringBuilder sb, E1ElementView view)
        {
            if (!responseLoaded || responseData == null) return;

            if (view.category == "beam")
            {
                AppendBeamResponseInfo(sb, view);
            }
            else if (view.category == "column")
            {
                AppendElementResponseInfo(sb, view, "COLUMN");
            }
            else if (view.category == "support")
            {
                AppendSupportResponseInfo(sb, view);
            }
            else if (view.category == "node" && view.node != null)
            {
                AppendNodeResponseInfo(sb, view);
            }
            else
            {
                E1ResponseElement matched = MatchResponseElement(view);
                if (matched != null) AppendStatusLine(sb, matched.analysis_status);
                else
                {
                    sb.AppendLine();
                    sb.AppendLine("--- ANALYSIS STATUS ---");
                    sb.AppendLine("Analysis Status: -");
                }
            }
        }

        private void AppendStatusLine(StringBuilder sb, string status)
        {
            sb.AppendLine();
            sb.AppendLine("--- ANALYSIS STATUS ---");
            sb.AppendLine(FriendlyAnalysisStatus(status));
            sb.AppendLine("Internal status: " + (string.IsNullOrEmpty(status) ? "-" : status));
            if (string.Equals(status, E1AnalysisStatus.Scoping, StringComparison.OrdinalIgnoreCase))
            {
                sb.AppendLine("WARNING: Reconciled scoping response; use with caution, not as final verified demand.");
            }
            else if (E1AnalysisStatus.IsBlocking(status))
            {
                string warning = responseData != null && !string.IsNullOrEmpty(responseData.blocker_warning_text) ? responseData.blocker_warning_text : "Structural response not verified: no traceable foundation load path.";
                sb.AppendLine("WARNING: " + warning);
            }
        }

        private void AppendElementResponseInfo(StringBuilder sb, E1ElementView view, string kindLabel)
        {
            E1ResponseElement matched = MatchResponseElement(view);
            if (matched == null)
            {
                sb.AppendLine();
                sb.AppendLine("--- ANALYSIS STATUS ---");
                sb.AppendLine(FriendlyAnalysisStatus(AnalysisStatusForView(view)));
                sb.AppendLine("Reason: " + MappingReasonForView(view));
                return;
            }

            string status = matched.analysis_status;
            AppendStatusLine(sb, status);

            if (E1AnalysisStatus.IsVerified(status) || string.Equals(status, E1AnalysisStatus.Scoping, StringComparison.OrdinalIgnoreCase))
            {
                AppendForcesSection(sb, view, matched);
                AppendElementDisplacements(sb, matched);
            }
            else if (E1AnalysisStatus.IsBlocking(status))
            {
                sb.AppendLine("Response unavailable because: " + MappingReasonForView(view));
            }
        }

        private void AppendForcesSection(StringBuilder sb, E1ElementView view, E1ResponseElement matched)
        {
            if (responseData == null || responseData.element_forces_kN == null) return;
            string responseId = FindResponseForcesId(matched);
            if (responseId == null) return;
            if (!responseData.element_forces_kN.TryGetValue(responseId, out E1ElementForcesResponse forces)) return;
            if (forces == null || forces.forces_kN == null) return;

            sb.AppendLine();
            sb.AppendLine("--- INTERNAL FORCES ---");
            sb.AppendLine("N: " + F(GetForce(forces, "N1")) + " / " + F(GetForce(forces, "N2")) + " kN");
            sb.AppendLine("Vy: " + F(GetForce(forces, "Vy1")) + " / " + F(GetForce(forces, "Vy2")) + " kN");
            sb.AppendLine("Vz: " + F(GetForce(forces, "Vz1")) + " / " + F(GetForce(forces, "Vz2")) + " kN");
            sb.AppendLine("T: " + F(GetForce(forces, "T1")) + " / " + F(GetForce(forces, "T2")) + " kN·m");
            sb.AppendLine("My: " + F(GetForce(forces, "My1")) + " / " + F(GetForce(forces, "My2")) + " kN·m");
            sb.AppendLine("Mz: " + F(GetForce(forces, "Mz1")) + " / " + F(GetForce(forces, "Mz2")) + " kN·m");
        }

        private double GetForce(E1ElementForcesResponse forces, string key)
        {
            if (forces == null || forces.forces_kN == null) return 0.0;
            return forces.forces_kN.TryGetValue(key, out double v) ? v : 0.0;
        }

        private void AppendElementDisplacements(StringBuilder sb, E1ResponseElement matched)
        {
            if (responseData == null || responseData.displacements_m == null) return;
            sb.AppendLine();
            sb.AppendLine("--- DISPLACEMENTS ---");
            E1DisplacementResponse i = FindDisplacement(matched.node_i);
            E1DisplacementResponse j = FindDisplacement(matched.node_j);
            sb.AppendLine("Node i: " + DisplacementText(i));
            sb.AppendLine("Node j: " + DisplacementText(j));
        }

        private string DisplacementText(E1DisplacementResponse d)
        {
            if (d == null) return "-";
            return string.Format(CultureInfo.InvariantCulture, "u=({0:F5},{1:F5},{2:F5}) m", d.ux_m.GetValueOrDefault(), d.uy_m.GetValueOrDefault(), d.uz_m.GetValueOrDefault());
        }

        private E1DisplacementResponse FindDisplacement(List<double> node)
        {
            if (responseData == null || responseData.displacements_m == null || node == null) return null;
            string tag = FindResponseNodeTag(node);
            if (tag != null && responseData.displacements_m.TryGetValue(tag, out E1DisplacementResponse d)) return d;
            return null;
        }

        private void AppendNodeResponseInfo(StringBuilder sb, E1ElementView view)
        {
            if (responseData == null) return;
            E1NodeInfo node = view.node;
            string tag = null;
            if (structuralNodeMappingByVisualId.TryGetValue(node.id, out E1StructuralNodeMapping nodeMapping) && !string.IsNullOrEmpty(nodeMapping.fe_node_id))
            {
                tag = nodeMapping.fe_node_id;
            }
            else
            {
                List<double> raw = new List<double> { node.point2.x, node.point2.y, FloorY(node.floorId) };
                tag = FindResponseNodeTag(raw);
            }
            if (tag == null)
            {
                sb.AppendLine();
                sb.AppendLine("--- ANALYSIS STATUS ---");
                sb.AppendLine(FriendlyAnalysisStatus("UNMATCHED_STRUCTURAL_RESPONSE"));
                sb.AppendLine("Reason: " + MappingReasonForView(view));
                return;
            }

            string status = responseData.node_analysis_status != null && responseData.node_analysis_status.TryGetValue(tag, out string s) ? s : null;
            AppendStatusLine(sb, status);

            if (E1AnalysisStatus.IsVerified(status) && responseData.displacements_m != null && responseData.displacements_m.TryGetValue(tag, out E1DisplacementResponse disp))
            {
                sb.AppendLine();
                sb.AppendLine("--- DISPLACEMENTS ---");
                sb.AppendLine(DisplacementText(disp));
            }

            if (responseData.reactions_kN != null && responseData.reactions_kN.TryGetValue(tag, out E1ReactionResponse reaction))
            {
                sb.AppendLine();
                sb.AppendLine("--- REACTIONS ---");
                sb.AppendLine(string.Format(CultureInfo.InvariantCulture, "R: ({0:F3}, {1:F3}, {2:F3}) kN", reaction.Rx_kN.GetValueOrDefault(), reaction.Ry_kN.GetValueOrDefault(), reaction.Rz_kN.GetValueOrDefault()));
            }
        }

        private void AppendSupportResponseInfo(StringBuilder sb, E1ElementView view)
        {
            E1StructuralSupportMapping mapping = SupportMappingForView(view);
            string feNode = SupportNodeId(mapping);
            string building = ResolveBuilding(view);
            E1ReactionResponse reaction = SupportReaction(feNode, building);
            bool verified = mapping != null && E1AnalysisStatus.IsVerified(mapping.fe_status) && reaction != null;

            sb.AppendLine("--- REACTIONS ---");
            if (!string.IsNullOrWhiteSpace(feNode)) sb.AppendLine("FE node: " + feNode);
            if (mapping != null && !string.IsNullOrEmpty(mapping.reason)) sb.AppendLine("Mapping reason: " + mapping.reason);
            if (!verified)
            {
                sb.AppendLine("Reactions not traceable/verified for this support.");
                return;
            }

            sb.AppendLine(string.Format(CultureInfo.InvariantCulture, "Fx: {0:F3} kN", reaction.Rx_kN.GetValueOrDefault()));
            sb.AppendLine(string.Format(CultureInfo.InvariantCulture, "Fy: {0:F3} kN", reaction.Ry_kN.GetValueOrDefault()));
            sb.AppendLine(string.Format(CultureInfo.InvariantCulture, "Fz: {0:F3} kN", reaction.Rz_kN.GetValueOrDefault()));
            sb.AppendLine(string.Format(CultureInfo.InvariantCulture, "Mx: {0:F3} kN·m", reaction.Mx.GetValueOrDefault()));
            sb.AppendLine(string.Format(CultureInfo.InvariantCulture, "My: {0:F3} kN·m", reaction.My.GetValueOrDefault()));
            sb.AppendLine(string.Format(CultureInfo.InvariantCulture, "Mz: {0:F3} kN·m", reaction.Mz.GetValueOrDefault()));
        }

        private E1StructuralSupportMapping SupportMappingForView(E1ElementView view)
        {
            if (view == null) return null;
            if (!string.IsNullOrWhiteSpace(view.id) && structuralSupportMappingByVisualId.TryGetValue(view.id, out E1StructuralSupportMapping mapping)) return mapping;
            if (view.generic != null)
            {
                string genericId = GenericId(view.generic, "support");
                if (!string.IsNullOrWhiteSpace(genericId) && structuralSupportMappingByVisualId.TryGetValue(genericId, out mapping)) return mapping;
            }
            return null;
        }

        private string SupportNodeId(E1StructuralSupportMapping mapping)
        {
            return mapping != null && !string.IsNullOrWhiteSpace(mapping.fe_node_id) ? mapping.fe_node_id : null;
        }

        private E1SupportRestraintResponse SupportRestraint(string feNode, string building = null)
        {
            if (responseData == null || responseData.support_restraints == null || string.IsNullOrWhiteSpace(feNode)) return null;
            if (responseData.support_restraints.TryGetValue(feNode, out E1SupportRestraintResponse restraint)) return restraint;
            string composite = CompositeResponseKey(building, feNode);
            return composite != null && responseData.support_restraints.TryGetValue(composite, out restraint) ? restraint : null;
        }

        private E1ReactionResponse SupportReaction(string feNode, string building = null)
        {
            if (responseData == null || responseData.reactions_kN == null || string.IsNullOrWhiteSpace(feNode)) return null;
            if (responseData.reactions_kN.TryGetValue(feNode, out E1ReactionResponse reaction)) return reaction;
            string composite = CompositeResponseKey(building, feNode);
            return composite != null && responseData.reactions_kN.TryGetValue(composite, out reaction) ? reaction : null;
        }

        private string CompositeResponseKey(string building, string feNode)
        {
            if (string.IsNullOrWhiteSpace(building) || string.IsNullOrWhiteSpace(feNode)) return null;
            string composite = building + "::" + feNode;
            return composite;
        }

        private string SupportVisualCoordinatesText(E1GenericElement item)
        {
            if (item == null) return "-";
            if (IsPoint2(item.point)) return PointText(item.point);
            if (IsPoint2(item.node_i) && IsPoint2(item.node_j)) return PointText(item.node_i) + " -> " + PointText(item.node_j);
            return PointText(item.node_i);
        }

        private void AppendSupportRestraints(StringBuilder sb, E1GenericElement item, E1SupportRestraintResponse restraint)
        {
            if (restraint != null && restraint.fixity != null && restraint.fixity.Count >= 6)
            {
                sb.AppendLine("Tx = " + RestraintState(restraint.fixity, 0));
                sb.AppendLine("Ty = " + RestraintState(restraint.fixity, 1));
                sb.AppendLine("Tz = " + RestraintState(restraint.fixity, 2));
                sb.AppendLine("RotX = " + RestraintState(restraint.fixity, 3));
                sb.AppendLine("RotY = " + RestraintState(restraint.fixity, 4));
                sb.AppendLine("RotZ = " + RestraintState(restraint.fixity, 5));
                if (!string.IsNullOrWhiteSpace(restraint.source)) sb.AppendLine("source: " + restraint.source);
                return;
            }

            sb.AppendLine(DofText(item));
        }

        private string RestraintState(List<int> fixity, int index)
        {
            return fixity != null && fixity.Count > index && fixity[index] != 0 ? "FIXED" : "FREE";
        }

        private string RestrainedDofsText(E1GenericElement item)
        {
            if (item == null || item.restrained_dofs == null || item.restrained_dofs.Count == 0) return "-";
            return string.Join(", ", item.restrained_dofs);
        }

        private string DerivedSupportType(E1GenericElement item, E1SupportRestraintResponse restraint = null)
        {
            if (restraint != null && restraint.fixity != null && restraint.fixity.Count >= 6)
            {
                bool allFixed = restraint.fixity.Take(6).All(v => v != 0);
                if (allFixed) return "Fixed";
                bool anyFixed = restraint.fixity.Take(6).Any(v => v != 0);
                return anyFixed ? "Partial restraint" : "Free";
            }
            if (item == null || item.restrained_dofs == null || item.restrained_dofs.Count == 0) return "-";
            List<int> dofs = item.restrained_dofs;
            bool rot = dofs.Contains(3) || dofs.Contains(4) || dofs.Contains(5);
            bool trans = dofs.Contains(0) || dofs.Contains(1) || dofs.Contains(2);
            if (rot && trans) return "Fixed";
            if (trans && !rot) return "Pinned";
            if (!trans && rot) return "Roller (moment only?)";
            return "-";
        }

        private string DofText(E1GenericElement item)
        {
            List<int> dofs = item != null ? item.restrained_dofs : null;
            bool unknown = dofs == null || dofs.Count == 0;
            Func<int, string> state = index => unknown ? "UNKNOWN" : (dofs.Contains(index) ? "FIXED" : "FREE");
            return "Tx = " + state(0) + "\n" +
                   "Ty = " + state(1) + "\n" +
                   "Tz = " + state(2) + "\n" +
                   "RotX = " + state(3) + "\n" +
                   "RotY = " + state(4) + "\n" +
                   "RotZ = " + state(5);
        }

        private string GenericConnectivityText(E1GenericElement item, string category)
        {
            if (item == null) return "-";
            string id = GenericId(item, category);
            List<string> connected = new List<string>();
            foreach (E1NodeInfo node in nodesById.Values)
            {
                bool hit = category == "column" && node.columns.Contains(id) ||
                           category == "wall" && node.walls.Contains(id) ||
                           category == "support" && node.supports.Contains(id);
                if (!hit) continue;
                connected.AddRange(node.beams.Select(x => "beam:" + x));
                connected.AddRange(node.columns.Where(x => x != id).Select(x => "column:" + x));
                connected.AddRange(node.walls.Where(x => x != id).Select(x => "wall:" + x));
                connected.AddRange(node.supports.Where(x => x != id).Select(x => "support:" + x));
            }
            return connected.Count == 0 ? "-" : string.Join(", ", connected.Distinct());
        }

        private string FindResponseForcesId(E1ResponseElement matched)
        {
            if (responseData == null || responseData.element_forces_kN == null) return null;
            foreach (KeyValuePair<string, E1ElementForcesResponse> pair in responseData.element_forces_kN)
            {
                if (pair.Value == null) continue;
                bool same = ResponseCoordsNear(pair.Value.node_i, matched.node_i) && ResponseCoordsNear(pair.Value.node_j, matched.node_j);
                bool reversed = ResponseCoordsNear(pair.Value.node_i, matched.node_j) && ResponseCoordsNear(pair.Value.node_j, matched.node_i);
                if (same || reversed)
                    return pair.Key;
            }
            return null;
        }

        private void AppendBeamResponseInfo(StringBuilder sb, E1ElementView view)
        {
            AppendElementResponseInfo(sb, view, "BEAM");
        }

        private string BeamText(E1Beam beam)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("=== IDENTIFICATION ===");
            sb.AppendLine("beam_id: " + beam.beam_id);
            sb.AppendLine("floor: " + FloorLabel(beam.floor_id));
            sb.AppendLine("node_i: " + PointText(beam.node_i));
            sb.AppendLine("node_j: " + PointText(beam.node_j));
            sb.AppendLine("length: " + F(beam.longitud_m) + " m");

            sb.AppendLine();
            sb.AppendLine("=== SECTION / MATERIAL ===");
            sb.AppendLine("section: " + SectionText(beam.section));
            sb.AppendLine("b/h: " + SectionText(beam.section));
            sb.AppendLine("A: -");
            sb.AppendLine("Iy: -");
            sb.AppendLine("Iz: -");
            sb.AppendLine("J: -");
            sb.AppendLine("material: -");
            sb.AppendLine("E/G: -");
            sb.AppendLine("OpenSees type: -");

            sb.AppendLine();
            sb.AppendLine("=== CONNECTIVITY ===");
            sb.AppendLine("slab_ids/member_slab_ids: " + Join(beam.slab_ids ?? beam.member_slab_ids));
            sb.AppendLine("connected members: " + ConnectedMembersText(beam));
            sb.AppendLine("end conditions/releases: not provided in gravity JSON");
            sb.AppendLine("diaphragm relation: floor diaphragm inferred by level");

            sb.AppendLine();
            sb.AppendLine("=== APPLIED LOADS ===");
            sb.Append(BeamSlabLoadText(beam));
            sb.AppendLine("Atrib (tributary_area): " + F(beam.area_tributaria_m2) + " m2");
            sb.AppendLine("qG: " + Maybe(beam.qG_kN_m2, " kN/m2"));
            sb.AppendLine("P (transferred load): " + F(beam.P_kN) + " kN");
            sb.AppendLine("w (line load): " + F(beam.w_lineal_kN_m) + " kN/m");
            string sc = BeamScText(beam);
            if (sc != null) sb.AppendLine("SC: " + sc);
            sb.AppendLine("point loads: -");
            sb.AppendLine("additional line loads: -");
            sb.AppendLine();
            sb.AppendLine("--- GEOMETRY / GRAVITY ---");
            sb.AppendLine("gravity_verified: " + beam.gravity_verified);
            int tribCount = beam.poligonos_tributarios == null ? 0 : beam.poligonos_tributarios.Count;
            sb.AppendLine("tributary polygons shown: " + tribCount + " (selected beam highlighted)");
            return sb.ToString();
        }

        private string BeamSlabLoadText(E1Beam beam)
        {
            if (beam == null || data == null || data.losas == null) return "";
            List<string> ids = beam.slab_ids ?? beam.member_slab_ids;
            if (ids == null || ids.Count == 0) return "slab IDs: -\nPP.LOSA: -\nPM_ADIC: -\n";

            StringBuilder sb = new StringBuilder();
            sb.AppendLine("slab IDs: " + Join(ids));
            foreach (string id in ids)
            {
                E1Slab slab = data.losas.FirstOrDefault(s => s.slab_id == id);
                if (slab == null) continue;
                sb.AppendLine("PP.LOSA " + id + ": " + Maybe(slab.pp_kN_m2, " kN/m2"));
                sb.AppendLine("PM_ADIC " + id + ": " + Maybe(slab.pm_adic_kN_m2, " kN/m2"));
            }
            return sb.ToString();
        }

        private string ConnectedMembersText(E1Beam beam)
        {
            if (beam == null) return "-";
            List<string> connected = new List<string>();
            foreach (E1NodeInfo node in nodesById.Values)
            {
                if (node.beams.Contains(beam.beam_id))
                {
                    connected.AddRange(node.columns.Select(id => "column:" + id));
                    connected.AddRange(node.walls.Select(id => "wall:" + id));
                    connected.AddRange(node.supports.Select(id => "support:" + id));
                }
            }
            return connected.Count == 0 ? "-" : string.Join(", ", connected.Distinct());
        }

        private string BeamScText(E1Beam beam)
        {
            if (data == null || data.losas == null) return null;
            List<string> ids = beam.slab_ids ?? beam.member_slab_ids;
            if (ids == null) return null;
            double? sc = null;
            foreach (string id in ids)
            {
                foreach (E1Slab slab in data.losas)
                {
                    if (slab.slab_id == id && slab.sc_kN_m2.HasValue)
                    {
                        sc = slab.sc_kN_m2;
                        break;
                    }
                }
                if (sc.HasValue) break;
            }
            return sc.HasValue ? F(sc.Value) + " kN/m2" : null;
        }

        private string NodeText(E1NodeInfo node)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("node_id: " + node.id);
            sb.AppendLine("floor: " + FloorLabel(node.floorId));
            sb.AppendLine("point: " + node.point2.x.ToString("F3", CultureInfo.InvariantCulture) + ", " + node.point2.y.ToString("F3", CultureInfo.InvariantCulture));
            sb.AppendLine("elementos conectados:");
            sb.AppendLine("beams: " + Join(node.beams));
            sb.AppendLine("columns: " + Join(node.columns));
            sb.AppendLine("supports: " + Join(node.supports));
            sb.AppendLine("walls: " + Join(node.walls));
            return sb.ToString();
        }

        private string TributaryText(E1Beam beam, E1TributaryPolygon tributary)
        {
            return "tributary polygon\n" +
                "beam_id: " + beam.beam_id + "\n" +
                "slab_id: " + tributary.slab_id + "\n" +
                "floor: " + FloorLabel(beam.floor_id) + "\n" +
                "area: " + F(tributary.area_m2) + " m2\n" +
                "beam P: " + F(beam.P_kN) + " kN\n" +
                "beam w: " + F(beam.w_lineal_kN_m) + " kN/m";
        }

        private string SlabText(E1Slab slab)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("slab_id: " + slab.slab_id);
            sb.AppendLine("floor: " + FloorLabel(slab.floor_id));
            sb.AppendLine("gravity_verified: " + slab.gravity_verified);
            sb.AppendLine("status: " + (slab.status ?? slab.load_status ?? "-"));
            sb.AppendLine("area_efectiva: " + Maybe(slab.area_efectiva_m2, " m2"));
            sb.AppendLine("thickness: " + Maybe(slab.thickness_m, " m"));
            sb.AppendLine("q_G: " + Maybe(slab.qG_kN_m2, " kN/m2"));
            sb.AppendLine("total_carga: " + Maybe(slab.total_carga_kN, " kN"));
            sb.AppendLine("receiver_beam_ids: " + Join(slab.receiver_beam_ids));
            return sb.ToString();
        }

        private string BlockerText(E1Blocker blocker)
        {
            return "DOCUMENTED GEOMETRIC BLOCKER\n" +
                "slab_id: " + blocker.slab_id + "\n" +
                "floor: " + FloorLabel(blocker.floor_id) + "\n" +
                "status: " + blocker.status + "\n" +
                "area_m2: " + F(blocker.area_m2) + "\n" +
                "reasons: " + Join(blocker.reasons) + "\n" +
                "final_reason: " + (blocker.final_reason ?? "-") + "\n" +
                "L101 excluded from verified gravity because its diagonal CAD boundary cannot be closed without artificial geometry.\n" +
                "Global equilibrium remains PASS over the verified gravity universe.";
        }

        private string GenericText(string category, E1GenericElement item)
        {
            return category + "\n" +
                "id: " + GenericId(item, category) + "\n" +
                "floor: " + FloorLabel(item.floor_id) + "\n" +
                "node_i: " + PointText(item.node_i) + "\n" +
                "node_j: " + PointText(item.node_j) + "\n" +
                "section: " + SectionText(item.section) + "\n" +
                "length: " + Maybe(item.length_m, " m") + "\n" +
                "source: " + (item.visual_source ?? item.source_dxf ?? "-") + "\n" +
                "implementation: " + (item.implementation ?? "-") + "\n" +
                "notes: " + (item.notes ?? "-");
        }

        private string SectionText(E1Section section)
        {
            if (section == null) return "-";
            double? width = section.width_m ?? section.b;
            double? height = section.height_m ?? section.h;
            if (width.HasValue && height.HasValue) return F(width.Value) + " x " + F(height.Value) + " m";
            return "-";
        }

        private string Maybe(double? value, string unit)
        {
            return value.HasValue ? F(value.Value) + unit : "-";
        }

        private string MaybeFormat(double? value, string unit, string format)
        {
            return value.HasValue ? value.Value.ToString(format, CultureInfo.InvariantCulture) + unit : "-";
        }

        private string MaybeLength(double? value, string unit)
        {
            return MaybeFormat(value, unit, "0.000###");
        }

        private string MaybeGPa(double? valuePa)
        {
            return valuePa.HasValue ? (valuePa.Value / 1000000000.0).ToString("F3", CultureInfo.InvariantCulture) + " GPa" : "-";
        }

        private string MaybeInt(int? value)
        {
            return value.HasValue ? value.Value.ToString(CultureInfo.InvariantCulture) : "-";
        }

        private string Dash(string value)
        {
            return string.IsNullOrWhiteSpace(value) ? "-" : value;
        }

        private string F(double value)
        {
            return value.ToString("F3", CultureInfo.InvariantCulture);
        }

        private string PointText(List<double> point)
        {
            if (!IsPoint2(point)) return "-";
            if (point.Count >= 3)
            {
                return string.Format(CultureInfo.InvariantCulture, "({0:F3}, {1:F3}, {2:F3})", point[0], point[1], point[2]);
            }
            return string.Format(CultureInfo.InvariantCulture, "({0:F3}, {1:F3})", point[0], point[1]);
        }

        private string Join(List<string> values)
        {
            return values == null || values.Count == 0 ? "-" : string.Join(", ", values);
        }

        private void HandleCamera()
        {
            if (cam == null) return;
            bool overGui = IsPointerOverGui();
            Vector2 mouse = Input.mousePosition;

            if (Input.GetMouseButtonDown(0) && !overGui)
            {
                if (TrySelect(mouse))
                {
                    draggingOrbit = false;
                    return;
                }
                draggingOrbit = true;
                lastMouse = mouse;
                mouseDown = mouse;
            }
            if (Input.GetMouseButtonDown(1) || Input.GetMouseButtonDown(2))
            {
                draggingPan = true;
                lastMouse = mouse;
            }

            if (draggingOrbit && Input.GetMouseButton(0))
            {
                Vector2 delta = mouse - lastMouse;
                cam.transform.RotateAround(orbitTarget, Vector3.up, delta.x * 0.18f);
                cam.transform.RotateAround(orbitTarget, cam.transform.right, -delta.y * 0.18f);
                lastMouse = mouse;
            }

            if (draggingPan && (Input.GetMouseButton(1) || Input.GetMouseButton(2)))
            {
                Vector2 delta = mouse - lastMouse;
                float distance = Vector3.Distance(cam.transform.position, orbitTarget);
                Vector3 pan = (-cam.transform.right * delta.x - cam.transform.up * delta.y) * distance * 0.0015f;
                orbitTarget += pan;
                cam.transform.position += pan;
                lastMouse = mouse;
            }

            if (Input.GetMouseButtonUp(0))
            {
                draggingOrbit = false;
            }
            if (Input.GetMouseButtonUp(1) || Input.GetMouseButtonUp(2)) draggingPan = false;

            float scroll = Input.mouseScrollDelta.y;
            if (Mathf.Abs(scroll) > 0.001f && !overGui)
            {
                Vector3 fromTarget = cam.transform.position - orbitTarget;
                float nextDistance = Mathf.Clamp(fromTarget.magnitude * (1f - scroll * 0.12f), 2f, 260f);
                cam.transform.position = orbitTarget + fromTarget.normalized * nextDistance;
            }
        }

        private bool IsPointerOverGui()
        {
            Vector2 p = Input.mousePosition;
            float yFromTop = Screen.height - p.y;
            if (!leftPanelCollapsed && p.x <= GuiWidth + GuiPickPadding && yFromTop <= Screen.height) return true;
            if (leftPanelCollapsed && p.x <= 170f && yFromTop <= 66f) return true;
            if (selectedView != null)
            {
                float width = Mathf.Min(InspectorWidth, Mathf.Max(320f, Screen.width - GuiWidth - 60f));
                float height = inspectorCollapsed ? 68f : Mathf.Min(720f, Mathf.Max(260f, Screen.height - 20f));
                float x = Mathf.Max(GuiWidth + 30f, Screen.width - width - 10f);
                Rect inspectorRect = new Rect(x, 10f, width, height);
                if (inspectorRect.Contains(new Vector2(p.x, yFromTop))) return true;
            }
            return EventSystem.current != null && EventSystem.current.IsPointerOverGameObject();
        }

        private bool TrySelect(Vector2 screenPosition)
        {
            Camera pickCamera = Camera.main != null ? Camera.main : cam;
            Ray ray = pickCamera.ScreenPointToRay(screenPosition);
            RaycastHit[] hits = Physics.RaycastAll(ray, 700f);
            if (hits == null || hits.Length == 0) return false;

            Array.Sort(hits, (a, b) =>
            {
                int pa = SelectionPriority(ViewFromHit(a.collider));
                int pb = SelectionPriority(ViewFromHit(b.collider));
                if (pa != pb) return pa.CompareTo(pb);
                return a.distance.CompareTo(b.distance);
            });

            foreach (RaycastHit hit in hits)
            {
                E1ElementView view = ViewFromHit(hit.collider);
                if (view == null) continue;
                if (!view.gameObject.activeInHierarchy) continue;
                Select(view);
                return true;
            }
            return false;
        }

        private E1ElementView ViewFromHit(Collider collider)
        {
            if (collider == null) return null;
            StructuralSelectable selectable = collider.GetComponentInParent<StructuralSelectable>();
            if (selectable != null && selectable.view != null) return selectable.view;
            return collider.GetComponentInParent<E1ElementView>();
        }

        private int SelectionPriority(E1ElementView view)
        {
            if (view == null) return 100;
            switch (view.category)
            {
                case "beam": return 0;
                case "column": return 1;
                case "wall": return 2;
                case "support": return 3;
                case "node": return 4;
                case "tributary": return 5;
                case "diaphragm": return 6;
                case "slab": return 7;
                case "blocker": return 8;
                default: return 50;
            }
        }

        private void ZoomTo(Vector3 position)
        {
            orbitTarget = position;
            Vector3 direction = (cam.transform.position - position).normalized;
            if (direction.sqrMagnitude < 0.001f) direction = new Vector3(1f, 0.6f, -1f).normalized;
            cam.transform.position = position + direction * 16f;
            cam.transform.LookAt(orbitTarget, Vector3.up);
        }

        private void FrameAll()
        {
            if (cam == null) return;
            orbitTarget = modelBounds.center;
            float radius = Mathf.Max(modelBounds.extents.x, modelBounds.extents.y, modelBounds.extents.z, 8f);
            cam.transform.position = orbitTarget + new Vector3(radius * 1.05f, radius * 0.72f, -radius * 1.25f);
            cam.transform.LookAt(orbitTarget, Vector3.up);
            cam.farClipPlane = Mathf.Max(700f, radius * 8f);
        }

        private void ComputeBounds()
        {
            bool initialized = false;
            Bounds bounds = new Bounds(Vector3.zero, Vector3.one);
            foreach (E1ElementView view in views)
            {
                if (view.category == "id" || view.category == "local_axis" || view.category == "blocker" || view.category == "tributary") continue;
                Renderer renderer = view.GetComponent<Renderer>();
                if (renderer == null) renderer = view.GetComponentInChildren<Renderer>();
                if (renderer == null) continue;
                if (!initialized)
                {
                    bounds = renderer.bounds;
                    initialized = true;
                }
                else bounds.Encapsulate(renderer.bounds);
            }
            modelBounds = initialized ? bounds : new Bounds(Vector3.zero, Vector3.one * 10f);
        }

        private Vector3 GenericCenter(List<List<double>> points)
        {
            if (points == null || points.Count == 0) return Vector3.zero;
            Vector3 sum = Vector3.zero;
            foreach (List<double> p in points) sum += ToUnityPoint(p, 0);
            return sum / points.Count;
        }

        private Vector3 MeshCenter(Mesh mesh)
        {
            return mesh.bounds.center;
        }
    }

    public class E1ElementView : MonoBehaviour
    {
        public string id;
        public string category;
        public string parentId;
        public string building;
        public int floorId;
        public Vector3 start;
        public Vector3 end;
        public E1Beam beam;
        public E1Slab slab;
        public E1TributaryPolygon tributary;
        public E1Blocker blocker;
        public E1GenericElement generic;
        public E1NodeInfo node;
    }

    public class StructuralSelectable : MonoBehaviour
    {
        public string elementType;
        public string elementId;
        public string sourceId;
        public string analysisId;
        public int floorId;
        public E1ElementView view;
    }

    public class E1NodeInfo
    {
        public string id;
        public int floorId;
        public Vector2 point2;
        public Vector3 world;
        public readonly List<string> beams = new List<string>();
        public readonly List<string> columns = new List<string>();
        public readonly List<string> supports = new List<string>();
        public readonly List<string> walls = new List<string>();
    }
}
