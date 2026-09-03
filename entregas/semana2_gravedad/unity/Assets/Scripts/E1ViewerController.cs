using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using UnityEngine;

namespace Mcoc.Semana2.UnityE1
{
    public class E1ViewerController : MonoBehaviour
    {
        private const float FloorHeight = 3.96f;
        private const float BeamWidth = 0.24f;
        private const float BeamDepth = 0.36f;
        private const float SlabVisualThickness = 0.08f;
        private const float GuiWidth = 390f;

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
        private Bounds modelBounds;
        private Vector3 orbitTarget = Vector3.zero;
        private Vector2 lastMouse;
        private Vector2 mouseDown;
        private bool draggingOrbit;
        private bool draggingPan;
        private int nodeIndex;
        private int floorIndex;
        private Vector2 selectionScroll;
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
        }

        private void LateUpdate()
        {
            if (cam == null || labelsRoot == null) return;
            foreach (Transform label in labelsRoot.transform)
            {
                label.rotation = Quaternion.LookRotation(label.position - cam.transform.position, Vector3.up);
            }
        }

        private void OnGUI()
        {
            GUILayout.BeginArea(new Rect(10, 10, GuiWidth, Screen.height - 20), "E1 Unity Viewer", GUI.skin.window);
            GUILayout.Label(statusText);
            GUILayout.Space(4);

            GUILayout.Label("Piso");
            int nextFloor = GUILayout.SelectionGrid(floorIndex, floorOptions, 3);
            if (nextFloor != floorIndex)
            {
                floorIndex = nextFloor;
                ApplyVisibility();
            }

            GUILayout.Space(4);
            bool changed = false;
            changed |= Toggle(ref showNodes, "Nodes");
            changed |= Toggle(ref showBeams, "Beams");
            changed |= Toggle(ref showColumns, "Columns");
            changed |= Toggle(ref showWalls, "Walls");
            changed |= Toggle(ref showSupports, "Supports");
            changed |= Toggle(ref showDiaphragms, "Diaphragms");
            changed |= Toggle(ref showIds, "IDs");
            changed |= Toggle(ref showLocalAxes, "Local Axes");
            changed |= Toggle(ref showTributaryAreas, "Tributary Areas");
            changed |= Toggle(ref showSlabs, "Slabs / L101 marker");
            if (changed) ApplyVisibility();

            GUILayout.Space(4);
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Frame/Reset View")) FrameAll();
            if (GUILayout.Button("Clear selection")) ClearSelection();
            GUILayout.EndHorizontal();

            GUILayout.Space(4);
            GUILayout.Label("Search ID");
            GUILayout.BeginHorizontal();
            searchText = GUILayout.TextField(searchText);
            if (GUILayout.Button("Ir", GUILayout.Width(52))) SearchById(searchText);
            GUILayout.EndHorizontal();

            GUILayout.Space(6);
            GUILayout.Label("Seleccion");
            selectionScroll = GUILayout.BeginScrollView(selectionScroll, GUILayout.ExpandHeight(true));
            GUILayout.TextArea(selectionText, GUILayout.ExpandHeight(true));
            GUILayout.EndScrollView();
            GUILayout.EndArea();
        }

        private bool Toggle(ref bool value, string label)
        {
            bool next = GUILayout.Toggle(value, label);
            bool changed = next != value;
            value = next;
            return changed;
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
                statusText = "ERROR: no se pudo cargar edificio1_unity.json";
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
            ComputeBounds();
            ApplyVisibility();
            FrameAll();
            statusText = SummaryText();
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
                Register(view);

                E1NodeInfo nodeI = GetOrCreateNode(beam.floor_id, beam.node_i);
                E1NodeInfo nodeJ = GetOrCreateNode(beam.floor_id, beam.node_j);
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
                    Register(supportView);
                    E1NodeInfo supportNode = GetOrCreateNode(item.floor_id, supportPoint);
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
                Register(view);
                E1NodeInfo nodeI = GetOrCreateNode(item.floor_id, item.node_i);
                E1NodeInfo nodeJ = GetOrCreateNode(item.floor_id, item.node_j);
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
            Register(view);
            AddLocalAxes(id, item.floor_id, view.start, view.end);
            AddLabel(id, center + Vector3.up * (height * 0.5f + 0.25f), item.floor_id);
            List<double> planPoint = new List<double> { item.center[0], item.center[1] };
            E1NodeInfo baseNode = GetOrCreateNode(item.floor_id, planPoint);
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
            Register(view);
            E1NodeInfo nodeI = GetOrCreateNode(item.floor_id, item.node_i);
            E1NodeInfo nodeJ = GetOrCreateNode(item.floor_id, item.node_j);
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
            Register(view);
            E1NodeInfo nodeI = GetOrCreateNode(item.floor_id, item.node_i);
            E1NodeInfo nodeJ = GetOrCreateNode(item.floor_id, item.node_j);
            AddNodeConnection(nodeI, "support", id);
            AddNodeConnection(nodeJ, "support", id);
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

        private E1NodeInfo GetOrCreateNode(int floorId, List<double> point)
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
            transformToSet.rotation = Quaternion.FromToRotation(Vector3.right, direction.normalized);
            transformToSet.localScale = new Vector3(length, depth, width);
        }

        private Vector3 ToWorld(List<double> point, int floorId, float yOffset = 0f)
        {
            return new Vector3((float)point[0], FloorY(floorId) + yOffset, (float)point[1]);
        }

        private Vector3 ToUnityPoint(List<double> point, int floorId)
        {
            if (point != null && point.Count >= 3) return new Vector3((float)point[0], (float)point[2], (float)point[1]);
            return ToWorld(point, floorId, 0f);
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
                case "wall": return showWalls;
                case "support": return showSupports;
                case "diaphragm": return showDiaphragms;
                case "id": return showIds;
                case "local_axis": return showLocalAxes || (!string.IsNullOrEmpty(selectedId) && view.parentId == selectedId);
                case "tributary": return showTributaryAreas || (!string.IsNullOrEmpty(selectedBeamId) && view.parentId == selectedBeamId);
                case "slab": return showSlabs;
                case "blocker": return showSlabs;
                default: return true;
            }
        }

        private void ApplyVisibility()
        {
            foreach (E1ElementView view in views)
            {
                bool visible = FloorMatches(view.floorId) && CategoryVisible(view);
                view.gameObject.SetActive(visible);
                if (view.category == "tributary")
                {
                    MeshRenderer mr = view.GetComponent<MeshRenderer>();
                    if (mr != null) mr.sharedMaterial = view.parentId == selectedBeamId ? selectedTributaryMaterial : tributaryMaterial;
                }
            }
        }

        private void ClearSelection()
        {
            selectedId = "";
            selectedBeamId = "";
            selectionText = "Selecciona una viga, nodo, losa, tributaria o blocker.";
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
            selectedId = view.id;
            selectedBeamId = view.category == "beam" && view.beam != null ? view.beam.beam_id : "";
            selectionText = SelectionText(view);
            ApplyVisibility();
        }

        private string SelectionText(E1ElementView view)
        {
            if (view.category == "beam" && view.beam != null) return BeamText(view.beam);
            if (view.category == "node" && view.node != null) return NodeText(view.node);
            if (view.category == "tributary" && view.tributary != null) return TributaryText(view.beam, view.tributary);
            if (view.category == "slab" && view.slab != null) return SlabText(view.slab);
            if (view.category == "blocker" && view.blocker != null) return BlockerText(view.blocker);
            if (view.generic != null) return GenericText(view.category, view.generic);
            return view.id;
        }

        private string BeamText(E1Beam beam)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("beam_id: " + beam.beam_id);
            sb.AppendLine("floor: " + FloorLabel(beam.floor_id));
            sb.AppendLine("node_i: " + PointText(beam.node_i));
            sb.AppendLine("node_j: " + PointText(beam.node_j));
            sb.AppendLine("length: " + F(beam.longitud_m) + " m");
            sb.AppendLine("section: " + SectionText(beam.section));
            sb.AppendLine("slab_ids/member_slab_ids: " + Join(beam.slab_ids ?? beam.member_slab_ids));
            sb.AppendLine("tributary_area: " + F(beam.area_tributaria_m2) + " m2");
            sb.AppendLine("q_G: " + Maybe(beam.qG_kN_m2, " kN/m2"));
            sb.AppendLine("transferred_load P: " + F(beam.P_kN) + " kN");
            sb.AppendLine("line_load w: " + F(beam.w_lineal_kN_m) + " kN/m");
            sb.AppendLine("gravity_verified: " + beam.gravity_verified);
            int tribCount = beam.poligonos_tributarios == null ? 0 : beam.poligonos_tributarios.Count;
            sb.AppendLine("tributary polygons shown: " + tribCount + " (selected beam highlighted)");
            return sb.ToString();
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
            return "GEOMETRIC BLOCKER\n" +
                "slab_id: " + blocker.slab_id + "\n" +
                "floor: " + FloorLabel(blocker.floor_id) + "\n" +
                "status: " + blocker.status + "\n" +
                "area_m2: " + F(blocker.area_m2) + "\n" +
                "reasons: " + Join(blocker.reasons) + "\n" +
                "final_reason: " + (blocker.final_reason ?? "-") + "\n" +
                "No se inventa poligono para L101.";
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

        private string F(double value)
        {
            return value.ToString("F3", CultureInfo.InvariantCulture);
        }

        private string PointText(List<double> point)
        {
            if (!IsPoint2(point)) return "-";
            return string.Format(CultureInfo.InvariantCulture, "({0:F3}, {1:F3})", point[0], point[1]);
        }

        private string Join(List<string> values)
        {
            return values == null || values.Count == 0 ? "-" : string.Join(", ", values);
        }

        private void HandleCamera()
        {
            if (cam == null) return;
            bool overGui = Input.mousePosition.x <= GuiWidth + 20f;
            Vector2 mouse = Input.mousePosition;

            if (Input.GetMouseButtonDown(0) && !overGui)
            {
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
                if (draggingOrbit && Vector2.Distance(mouseDown, mouse) < 5f && !overGui) TrySelect(mouse);
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

        private void TrySelect(Vector2 screenPosition)
        {
            Ray ray = cam.ScreenPointToRay(screenPosition);
            if (!Physics.Raycast(ray, out RaycastHit hit, 700f)) return;
            E1ElementView view = hit.collider.GetComponentInParent<E1ElementView>();
            if (view != null) Select(view);
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
                if (view.category == "id" || view.category == "local_axis") continue;
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
