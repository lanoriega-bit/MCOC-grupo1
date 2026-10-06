using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Rendering;

namespace Mcoc.UnityViewer
{
    public partial class ViewerController
    {
        // Photo-inspired PRESENTATION ONLY. Model coordinates: XY plan, Z height.
        // No ElementInfo, registration, structural tag, dataset writes or FE participation.
        bool architecturalContextVisible = true, facadeSkinVisible = true, glazingVisible = true;
        bool exteriorStairsVisible = true, landscapeVisible = true, scaleFiguresVisible = true, roofVisible = true;
        bool hideArchitectureForResults = true;
        GameObject architecturalContextRoot;
        readonly List<VisualContextGroup> visualContextGroups = new List<VisualContextGroup>();
        readonly List<Material> architecturalContextMaterials = new List<Material>();
        Material facadeOrange, contextConcrete, contextFrame, contextGlass, contextEarth, contextLeaves, contextPeople, contextRoof;
        Bounds visualSiteBounds;
        readonly List<Bounds> mainVisualRoofs = new List<Bounds>();
        Vector3[] visualStairRoute;
        GameObject visualArrivalPlatform, transverseAccessWalk;
        int architecturePrimitiveCount;
        const float SkinOffset = .32f, VisualBayWidth = 2.5f, StairWidth = 1.8f;

        class VisualContextGroup
        {
            public GameObject root;
            public string building, floor, kind;
        }

        void BuildArchitecturalContext()
        {
            if (model?.solids == null || visualTerrainRoot == null) return;
            int structuralCount = allElements.Count;
            architecturalContextRoot = new GameObject("VISUAL_ONLY_ARCHITECTURE_AND_CONTEXT");
            architecturalContextRoot.layer = 2; // Ignore Raycast; keep structural selection transparent.
            architecturalContextRoot.transform.SetParent(transform, false);
            facadeOrange = ContextMaterial("Orange facade", new Color(.93f, .36f, .075f), .14f);
            contextConcrete = ContextMaterial("Light concrete", new Color(.72f, .72f, .67f), .10f);
            contextRoof = ContextMaterial("Neutral grey roof", new Color(.60f, .62f, .64f), .10f);
            contextFrame = ContextMaterial("Charcoal frames and rails", new Color(.12f, .16f, .18f), .25f);
            contextEarth = ContextMaterial("Earth", new Color(.44f, .37f, .27f), .05f);
            contextLeaves = ContextMaterial("Muted foliage", new Color(.28f, .40f, .24f), .05f);
            contextPeople = ContextMaterial("Scale figures", new Color(.29f, .37f, .43f), .12f);
            contextGlass = ContextMaterial("Blue grey glass", new Color(.25f, .43f, .53f, .32f), .65f);
            contextGlass.SetFloat("_Mode", 3);
            contextGlass.SetInt("_SrcBlend", (int)BlendMode.SrcAlpha);
            contextGlass.SetInt("_DstBlend", (int)BlendMode.OneMinusSrcAlpha);
            contextGlass.SetInt("_ZWrite", 0);
            contextGlass.EnableKeyword("_ALPHABLEND_ON");
            contextGlass.renderQueue = 3000;
            contextGlass.SetInt("_Cull", (int)CullMode.Off);

            foreach (string building in new[] { "EDIFICIO_1", "EDIFICIO_2" })
            {
                Bounds frame;
                if (!TryContextFrame(building, "P3", out frame)) continue;
                foreach (string floor in new[] { "P1", "P2", "P3", "P4" })
                {
                    Bounds storey;
                    if (!TryContextFrame(building, floor, out storey)) continue;
                    // Use main P3 footprint; only P4 follows its known projecting column ends.
                    float xmin = floor == "P4" ? storey.min.x : frame.min.x;
                    float xmax = floor == "P4" ? storey.max.x : frame.max.x;
                    BuildOrangeSkin(building, floor, xmin, xmax, frame.min.y - SkinOffset, storey.min.z, storey.max.z);
                    BuildCurtainFacade(building, floor, xmin, xmax, frame.max.y + SkinOffset, storey.min.z, storey.max.z);
                    BuildEndSkin(building, floor, xmin - SkinOffset, frame.min.y, frame.max.y, storey.min.z, storey.max.z);
                    // Preserve the elevated +X entry: two side piers, not a solid wall.
                    if (building == "EDIFICIO_1")
                        BuildEndSkin(building, floor, xmax + SkinOffset, frame.min.y, frame.max.y, storey.min.z, storey.max.z);
                    BuildProjectingGlazing(building, floor, frame, storey);
                }
            }
            BuildContinuousVisualRoof();
            BuildVisualAccessAndStairs();
            BuildLandscapeContext();
            UpdateArchitecturalContextVisibility();
            bool passive = ContextIsPassive();
            Debug.Log($"[ARCHITECTURAL CONTEXT QA] {(passive && structuralCount == allElements.Count ? "PASS" : "FAIL")}: {architecturePrimitiveCount} passive visual primitives; structural registry unchanged; photo interpretation, not surveyed geometry.");
        }

        Material ContextMaterial(string name, Color color, float smoothness)
        {
            var material = new Material(Shader.Find("Standard")) { name = "VISUAL_ONLY_" + name, color = color };
            material.SetFloat("_Glossiness", smoothness);
            architecturalContextMaterials.Add(material);
            return material;
        }

        bool TryContextFrame(string building, string floor, out Bounds bounds)
        {
            bounds = new Bounds();
            bool found = false;
            foreach (var solid in model.solids)
            {
                if (solid.category != "column" || solid.building != building || solid.floor != floor ||
                    solid.center == null || solid.center.Count != 3 || solid.height_m <= 0) continue;
                Vector3 p = V(solid.center);
                Vector3 bottom = p - Vector3.forward * (float)solid.height_m / 2;
                Vector3 top = p + Vector3.forward * (float)solid.height_m / 2;
                if (!found) { bounds = new Bounds(bottom, Vector3.zero); found = true; }
                bounds.Encapsulate(bottom); bounds.Encapsulate(top);
            }
            return found;
        }

        Transform ContextGroup(string name, string kind, string building = "EDIFICIO_1", string floor = null)
        {
            var go = new GameObject("VISUAL_ONLY_" + name); go.layer = 2;
            go.transform.SetParent(architecturalContextRoot.transform, false);
            visualContextGroups.Add(new VisualContextGroup { root = go, building = building, floor = floor, kind = kind });
            return go.transform;
        }

        GameObject ContextPrimitive(PrimitiveType shape, string name, Transform parent, Vector3 position, Vector3 scale, Material material)
        {
            var go = GameObject.CreatePrimitive(shape);
            go.name = "VISUAL_ONLY_" + name; go.layer = 2;
            go.transform.SetParent(parent, false);
            go.transform.localPosition = position; go.transform.localScale = scale;
            var collider = go.GetComponent<Collider>();
            if (collider != null) { collider.enabled = false; Destroy(collider); }
            var renderer = go.GetComponent<Renderer>(); renderer.sharedMaterial = material;
            renderer.shadowCastingMode = material == contextGlass ? ShadowCastingMode.Off : ShadowCastingMode.On;
            architecturePrimitiveCount++;
            return go;
        }

        GameObject ContextBox(Transform parent, string name, Vector3 center, Vector3 size, Material material)
            => ContextPrimitive(PrimitiveType.Cube, name, parent, center, size, material);

        void ContextRail(Transform parent, string name, Vector3 a, Vector3 b, float width, Material material)
        {
            Vector3 delta = b - a;
            if (delta.sqrMagnitude < .000001f) return;
            var go = ContextBox(parent, name, (a + b) / 2, new Vector3(delta.magnitude, width, width), material);
            go.transform.localRotation = Quaternion.FromToRotation(Vector3.right, delta);
        }

        void BuildOrangeSkin(string building, string floor, float xmin, float xmax, float y, float bottom, float top)
        {
            Transform skin = ContextGroup(building + "_" + floor + "_ORANGE_SKIN", "facade", building, floor);
            float height = top - bottom;
            int bays = Mathf.Max(1, Mathf.CeilToInt((xmax - xmin) / VisualBayWidth));
            float spacing = (xmax - xmin) / bays;
            // Narrow orange piers + recessed clear bays leave the structure readable.
            for (int i = 0; i <= bays; i++)
            {
                float x = xmin + i * spacing;
                ContextBox(skin, "Orange_pier", new Vector3(x, y, (bottom + top) / 2), new Vector3(.90f, .34f, height - .20f), facadeOrange);
                if (i == bays) continue;
                Transform windows = ContextGroup(building + "_" + floor + "_RECESSED_WINDOW_" + i, "glass", building, floor);
                float mid = x + spacing / 2;
                ContextBox(windows, "Recessed_window", new Vector3(mid, y + .20f, (bottom + top) / 2), new Vector3(spacing - .95f, .04f, height - .42f), contextGlass);
                ContextRail(windows, "Window_transom", new Vector3(x + .48f, y + .17f, bottom + height * .55f), new Vector3(x + spacing - .48f, y + .17f, bottom + height * .55f), .045f, contextFrame);
                ContextBox(skin, "Window_sunshade", new Vector3(mid, y - .20f, top - .22f), new Vector3(spacing - .90f, .68f, .07f), contextConcrete);
            }
            ContextBox(skin, "Floor_edge_band", new Vector3((xmin + xmax) / 2, y, top - .10f), new Vector3(xmax - xmin + .55f, .52f, .16f), contextConcrete);
        }

        void BuildCurtainFacade(string building, string floor, float xmin, float xmax, float y, float bottom, float top)
        {
            Transform glass = ContextGroup(building + "_" + floor + "_CURTAIN_GLASS", "glass", building, floor);
            ContextBox(glass, "Curtain_glass", new Vector3((xmin + xmax) / 2, y, (bottom + top) / 2), new Vector3(xmax - xmin, .04f, top - bottom - .16f), contextGlass);
            int bays = Mathf.Max(1, Mathf.CeilToInt((xmax - xmin) / VisualBayWidth));
            for (int i = 0; i <= bays; i++)
            {
                float x = Mathf.Lerp(xmin, xmax, (float)i / bays);
                ContextRail(glass, "Curtain_mullion", new Vector3(x, y + .04f, bottom), new Vector3(x, y + .04f, top), .045f, contextFrame);
            }
            foreach (float z in new[] { bottom + .08f, (bottom + top) / 2, top - .08f })
                ContextRail(glass, "Curtain_transom", new Vector3(xmin, y + .04f, z), new Vector3(xmax, y + .04f, z), .045f, contextFrame);
        }

        void BuildEndSkin(string building, string floor, float x, float ymin, float ymax, float bottom, float top)
        {
            Transform end = ContextGroup(building + "_" + floor + "_END_SKIN", "facade", building, floor);
            int bays = Mathf.Max(2, Mathf.CeilToInt((ymax - ymin) / 3.5f));
            for (int i = 0; i <= bays; i++)
                ContextBox(end, "End_orange_pier", new Vector3(x, Mathf.Lerp(ymin, ymax, (float)i / bays), (bottom + top) / 2), new Vector3(.28f, .70f, top - bottom - .20f), facadeOrange);
            ContextBox(end, "End_floor_band", new Vector3(x, (ymin + ymax) / 2, top - .10f), new Vector3(.55f, ymax - ymin + .6f, .16f), contextConcrete);
        }

        void BuildProjectingGlazing(string building, string floor, Bounds frame, Bounds storey)
        {
            // These two boxes follow actual outboard column XY, not measurements from photos.
            var outboard = model.solids.FindAll(s => s.building == building && s.floor == floor && s.category == "column" &&
                s.center != null && s.center.Count == 3 && s.center[1] > frame.max.y + 1);
            if (outboard.Count < 2) return;
            float xmin = float.PositiveInfinity, xmax = float.NegativeInfinity, outerY = frame.max.y;
            foreach (var s in outboard) { xmin = Mathf.Min(xmin, (float)s.center[0]); xmax = Mathf.Max(xmax, (float)s.center[0]); outerY = Mathf.Max(outerY, (float)s.center[1]); }
            if (xmax - xmin < 1) return;
            BuildCurtainFacade(building, floor, xmin, xmax, outerY + .18f, storey.min.z, storey.max.z);
            Transform box = ContextGroup(building + "_" + floor + "_PROJECTING_GLASS_BOX", "glass", building, floor);
            foreach (float x in new[] { xmin, xmax })
            {
                ContextBox(box, "Glass_return", new Vector3(x, (frame.max.y + outerY) / 2, storey.center.z), new Vector3(.04f, outerY - frame.max.y, storey.size.z - .18f), contextGlass);
                ContextRail(box, "Glass_box_corner", new Vector3(x, outerY + .20f, storey.min.z), new Vector3(x, outerY + .20f, storey.max.z), .06f, contextFrame);
            }
            ContextBox(box, "Visual_box_soffit", new Vector3((xmin + xmax) / 2, (frame.max.y + outerY) / 2, storey.min.z - .05f), new Vector3(xmax - xmin, outerY - frame.max.y, .12f), contextConcrete);
            // P2 box cap removed: do not obstruct the corrected stair route.
            // P4 is covered by the continuous neutral-grey roof instead.
        }

        void BuildContinuousVisualRoof()
        {
            Bounds e1, e2, main1, main2;
            if (!TryContextFrame("EDIFICIO_1", "P4", out e1) || !TryContextFrame("EDIFICIO_2", "P4", out e2) ||
                !TryContextFrame("EDIFICIO_1", "P3", out main1) || !TryContextFrame("EDIFICIO_2", "P3", out main2)) return;
            float jointX = (e2.max.x + e1.min.x) / 2;
            float ymin = Mathf.Min(main1.min.y, main2.min.y) - .52f;
            float ymax = Mathf.Max(main1.max.y, main2.max.y) + .52f;
            float roofBottom = Mathf.Max(e1.max.z, e2.max.z) + .015f;
            float outerMinX = e2.min.x, outerMaxX = e1.max.x;
            // Include real roof-level cantilever ends, not only column centres.
            // Read-only footprint: this changes the visual roof, never the beams.
            foreach (var solid in model.solids)
            {
                if (solid.floor != "P4" || solid.category != "beam" || solid.start == null || solid.end == null) continue;
                if (solid.building == "EDIFICIO_2") outerMinX = Mathf.Min(outerMinX, V(solid.start).x, V(solid.end).x);
                if (solid.building == "EDIFICIO_1") outerMaxX = Mathf.Max(outerMaxX, V(solid.start).x, V(solid.end).x);
            }
            // Two contiguous visual panels, without coplanar overlap, follow building filters.
            foreach (string building in new[] { "EDIFICIO_2", "EDIFICIO_1" })
            {
                float xmin = building == "EDIFICIO_2" ? outerMinX - .52f : jointX;
                float xmax = building == "EDIFICIO_2" ? jointX : outerMaxX + .52f;
                Bounds panel = TerrainBox(xmin, xmax, ymin, ymax, roofBottom, roofBottom + .18f);
                mainVisualRoofs.Add(panel);
                Transform roof = ContextGroup(building + "_CONTINUOUS_GREY_ROOF", "roof", building, "P4");
                ContextBox(roof, "Main_roof", panel.center, panel.size, contextRoof);
                var outboard = model.solids.FindAll(s => s.building == building && s.floor == "P4" && s.category == "column" &&
                    s.center != null && s.center.Count == 3 && s.center[1] > ymax);
                if (outboard.Count < 2) continue;
                float boxMin = float.PositiveInfinity, boxMax = float.NegativeInfinity, outerY = ymax;
                foreach (var s in outboard) { boxMin = Mathf.Min(boxMin, (float)s.center[0]); boxMax = Mathf.Max(boxMax, (float)s.center[0]); outerY = Mathf.Max(outerY, (float)s.center[1]); }
                Bounds extension = TerrainBox(boxMin - .25f, boxMax + .25f, ymax, outerY + .35f, roofBottom, roofBottom + .18f);
                ContextBox(roof, "Upper_glass_box_roof_continuation", extension.center, extension.size, contextRoof);
            }
        }

        void BuildVisualAccessAndStairs()
        {
            Bounds frame;
            if (!TryContextFrame("EDIFICIO_1", "P3", out frame)) return;
            BuildReferencedExteriorStair();
            var p2Beam = TerrainReference("E1-P1-V-106");
            if (p2Beam?.start == null) return;
            float accessX = V(p2Beam.start).x + .7f;
            Transform paved = ContextGroup("PEDESTRIAN_ACCESS_AND_PLAZA", "landscape");
            // Existing terrace heights and limits remain the reference for all paving.
            visualSiteBounds = new Bounds(terrainBaseObject.transform.GetChild(0).localPosition,
                terrainBaseObject.transform.GetChild(0).localScale);
            float walkwayEnd = Mathf.Min(visualSiteBounds.max.x - 2, accessX + 11);
            ContextBox(paved, "P2_arrival_plaza", new Vector3((accessX + walkwayEnd) / 2, frame.center.y, accessTerrainElevation + .07f),
                new Vector3(walkwayEnd - accessX, frame.size.y + 1, .08f), contextConcrete);
            AddLevelRails(paved, accessX, walkwayEnd, frame.min.y - .5f, frame.max.y + .5f, accessTerrainElevation);
            // The old promenade/free paving could hang above the grass; leave that area clear.
            // Behind the scale figures: full-width Y route, perpendicular to the building's X axis.
            transverseAccessWalk = ContextBox(paved, "Full_width_transverse_access_walk",
                new Vector3(walkwayEnd, visualSiteBounds.center.y, accessTerrainElevation + .07f),
                new Vector3(PathWidth, visualSiteBounds.size.y, .08f), contextConcrete);
        }

        void BuildReferencedExteriorStair()
        {
            var lower = TerrainReference("E1-P2-C-021");
            var upper = TerrainReference("E1-P3-C-012");
            var horizontalA = TerrainReference("E1-P2-V-064");
            var horizontalB = TerrainReference("E1-P2-V-059");
            var arrival = TerrainReference("E1-P3-V-027");
            var platformEdge = TerrainReference("E1-P3-V-020");
            if (lower?.center == null || upper?.center == null || horizontalA?.start == null || horizontalA.end == null ||
                horizontalB?.start == null || horizontalB.end == null || arrival?.start == null || arrival.end == null ||
                platformEdge?.start == null || platformEdge.end == null)
            { Debug.LogWarning("[VISUAL STAIR] Missing reference; no invented route or structural change."); return; }
            Vector3 la = V(arrival.start), lb = V(arrival.end), ea = V(platformEdge.start), eb = V(platformEdge.end);
            float routeY = (la.y + lb.y) / 2;
            Vector3 low = V(lower.center), high = V(upper.center);
            low.z -= (float)lower.height_m / 2; high.z -= (float)upper.height_m / 2;
            low.y = high.y = routeY; // Adjacent to column faces, not through column axes.
            float endX = Mathf.Min(V(horizontalA.start).x, V(horizontalA.end).x, V(horizontalB.start).x, V(horizontalB.end).x);
            Vector3 horizontalEnd = new Vector3(endX, routeY, high.z);
            Vector3 arrivalPoint = new Vector3(la.x, routeY, la.z + (float)arrival.height_m / 2);
            visualStairRoute = new[] { low, high, horizontalEnd, arrivalPoint };
            Transform first = ContextGroup("STAIR_1_C021_TO_C012", "stairs", "EDIFICIO_1", "P2");
            BuildVisualStairFlight(first, low, high);
            Transform middle = ContextGroup("STAIR_2_HORIZONTAL_V064_V059", "stairs", "EDIFICIO_1", "P2");
            ContextBox(middle, "Horizontal_stair_walkway", (high + horizontalEnd) / 2 - Vector3.forward * .08f,
                new Vector3(high.x - horizontalEnd.x, StairWidth, .16f), contextConcrete);
            AddLevelRails(middle, horizontalEnd.x, high.x, routeY - StairWidth / 2, routeY + StairWidth / 2, high.z);
            Transform last = ContextGroup("STAIR_3_TO_V027_AND_V020", "stairs", "EDIFICIO_1", "P3");
            BuildVisualStairFlight(last, horizontalEnd, arrivalPoint);
            float xmin = Mathf.Min(la.x, ea.x), xmax = Mathf.Max(la.x, ea.x);
            float ymin = Mathf.Min(la.y, lb.y, ea.y, eb.y), ymax = Mathf.Max(la.y, lb.y, ea.y, eb.y);
            visualArrivalPlatform = ContextBox(last, "Arrival_platform_between_V027_V020",
                new Vector3((xmin + xmax) / 2, (ymin + ymax) / 2, arrivalPoint.z - .08f),
                new Vector3(xmax - xmin, ymax - ymin, .16f), contextConcrete);
            AddLevelRails(last, xmin, xmax, ymin, ymax, arrivalPoint.z);
        }

        void BuildVisualStairFlight(Transform parent, Vector3 a, Vector3 b)
        {
            int steps = Mathf.Max(1, Mathf.CeilToInt((b.z - a.z) / .18f));
            float run = Mathf.Abs(b.x - a.x) / steps;
            for (int i = 0; i < steps; i++)
            {
                Vector3 p = Vector3.Lerp(a, b, (i + .5f) / steps);
                p.z = Mathf.Lerp(a.z, b.z, (i + 1f) / steps) - .08f;
                ContextBox(parent, "Tread", p, new Vector3(run + .015f, StairWidth, .16f), contextConcrete);
            }
            var soffit = ContextBox(parent, "Stair_soffit", (a + b) / 2 - Vector3.forward * .18f,
                new Vector3((b - a).magnitude, StairWidth, .16f), contextConcrete);
            soffit.transform.localRotation = Quaternion.FromToRotation(Vector3.right, b - a);
            foreach (float side in new[] { -1f, 1f })
            {
                Vector3 offset = Vector3.up * side * StairWidth / 2;
                Vector3 delta = b - a;
                var panel = ContextBox(parent, "Orange_stair_side", (a + b) / 2 + offset + Vector3.forward * .36f,
                    new Vector3(delta.magnitude, .09f, .70f), facadeOrange);
                panel.transform.localRotation = Quaternion.FromToRotation(Vector3.right, delta);
                ContextRail(parent, "Stair_handrail", a + offset + Vector3.forward, b + offset + Vector3.forward, .045f, contextFrame);
                for (int i = 0; i <= 6; i++)
                {
                    Vector3 p = Vector3.Lerp(a, b, i / 6f) + offset;
                    ContextRail(parent, "Stair_rail_post", p, p + Vector3.forward, .035f, contextFrame);
                }
            }
        }

        void AddLevelRails(Transform parent, float xmin, float xmax, float ymin, float ymax, float z)
        {
            foreach (float y in new[] { ymin, ymax })
            {
                ContextRail(parent, "Platform_handrail", new Vector3(xmin, y, z + 1), new Vector3(xmax, y, z + 1), .04f, contextFrame);
                ContextRail(parent, "Platform_midrail", new Vector3(xmin, y, z + .55f), new Vector3(xmax, y, z + .55f), .035f, contextFrame);
                int n = Mathf.Max(1, Mathf.CeilToInt((xmax - xmin) / 2));
                for (int i = 0; i <= n; i++)
                {
                    float x = Mathf.Lerp(xmin, xmax, (float)i / n);
                    ContextRail(parent, "Platform_post", new Vector3(x, y, z), new Vector3(x, y, z + 1), .035f, contextFrame);
                }
            }
        }

        void BuildLandscapeContext()
        {
            if (visualSiteBounds.size.x < 1) return;
            Transform landscape = ContextGroup("LANDSCAPE_GRASS_EARTH", "landscape", null);
            float ground = visualSiteBounds.max.z + .025f;
            ContextBox(landscape, "Earth_border", new Vector3(visualSiteBounds.center.x, visualSiteBounds.min.y + 2, ground),
                new Vector3(visualSiteBounds.size.x - 4, 3, .05f), contextEarth);
            foreach (Vector3 p in new[] {
                new Vector3(visualSiteBounds.min.x + 5, visualSiteBounds.min.y + 5, ground),
                new Vector3(visualSiteBounds.min.x + 9, visualSiteBounds.max.y - 4, ground),
                new Vector3(lowerTerrainBounds.min.x + 4, visualSiteBounds.min.y + 4, lowerTerrainElevation + .03f) })
            {
                ContextRail(landscape, "Tree_trunk", p, p + Vector3.forward * 2.6f, .20f, contextEarth);
                ContextPrimitive(PrimitiveType.Sphere, "Tree_crown", landscape, p + Vector3.forward * 3.2f, new Vector3(2.6f, 2.6f, 3.2f), contextLeaves);
            }
            Bounds frame;
            if (!TryContextFrame("EDIFICIO_1", "P3", out frame)) return;
            Transform figures = ContextGroup("THREE_PEOPLE_FOR_SCALE", "figures");
            for (int i = 0; i < 3; i++)
            {
                Vector3 p = new Vector3(frame.max.x + 3 + i * 1.4f, frame.center.y + (i % 2), accessTerrainElevation + .12f);
                ContextRail(figures, "Person_body", p + Vector3.forward * .75f, p + Vector3.forward * 1.35f, .30f, contextPeople);
                ContextPrimitive(PrimitiveType.Sphere, "Person_head", figures, p + Vector3.forward * 1.58f, Vector3.one * .24f, contextEarth);
                foreach (float side in new[] { -1f, 1f })
                {
                    Vector3 hip = p + new Vector3(side * .10f, 0, .75f);
                    ContextRail(figures, "Person_leg", hip, p + new Vector3(side * .16f, 0, .03f), .09f, contextFrame);
                    ContextRail(figures, "Person_arm", p + new Vector3(side * .18f, 0, 1.28f), p + new Vector3(side * .28f, 0, .86f), .075f, contextPeople);
                }
            }
        }

        bool ContextIsPassive()
        {
            if (architecturalContextRoot == null) return false;
            foreach (var child in architecturalContextRoot.GetComponentsInChildren<Transform>(true))
                if (child.gameObject.layer != 2 || child.GetComponent<ElementInfo>() != null ||
                    (child.GetComponent<Collider>() != null && child.GetComponent<Collider>().enabled)) return false;
            return true;
        }

        void UpdateArchitecturalContextVisibility()
        {
            if (architecturalContextRoot == null) return;
            bool resultOverlay = hideArchitectureForResults && (activeDeformationVisible || diagramMode != 0 || localAxesVisible || structuralFailureVisualizationEnabled);
            architecturalContextRoot.SetActive(architecturalContextVisible && diagnosticViewMode == 0 && !isolateSelected && !resultOverlay);
            foreach (var group in visualContextGroups)
            {
                bool visible = group.kind == "facade" ? facadeSkinVisible : group.kind == "glass" ? glazingVisible :
                    group.kind == "stairs" ? exteriorStairsVisible : group.kind == "roof" ? roofVisible : group.kind == "figures" ? scaleFiguresVisible : landscapeVisible;
                if (group.building != null && buildingVisible.TryGetValue(group.building, out var buildingOn)) visible &= buildingOn;
                if (group.floor != null && floorVisible.TryGetValue(group.floor, out var floorOn)) visible &= floorOn;
                if (group.kind == "landscape" || group.kind == "figures") visible &= visualTerrainVisible;
                group.root.SetActive(visible);
            }
        }

        void LateUpdate() => UpdateArchitecturalContextVisibility();

        void DrawArchitecturalContextControls()
        {
            architecturalContextVisible = GUILayout.Toggle(architecturalContextVisible, "Arquitectura de referencia · SOLO VISUAL", GUILayout.Height(25));
            facadeSkinVisible = GUILayout.Toggle(facadeSkinVisible, "Fachadas naranjas y aleros", GUILayout.Height(25));
            roofVisible = GUILayout.Toggle(roofVisible, "Cubierta gris completa · solo visual", GUILayout.Height(25));
            glazingVisible = GUILayout.Toggle(glazingVisible, "Vidrio y cajas sobresalientes", GUILayout.Height(25));
            exteriorStairsVisible = GUILayout.Toggle(exteriorStairsVisible, "Escalera exterior y descansos", GUILayout.Height(25));
            landscapeVisible = GUILayout.Toggle(landscapeVisible, "Explanadas, barandas y vegetación", GUILayout.Height(25));
            scaleFiguresVisible = GUILayout.Toggle(scaleFiguresVisible, "Personas de escala · 3", GUILayout.Height(25));
            hideArchitectureForResults = GUILayout.Toggle(hideArchitectureForResults, "Despejar arquitectura al ver resultados", GUILayout.Height(25));
            GUILayout.Label("Interpretación visual de fotos; niveles y cajas apoyados en el modelo. No son fachadas ni escaleras medidas. Sin participación FE; clic atraviesa la piel.", currentBody);
            UpdateArchitecturalContextVisibility();
        }

        void OnDestroy()
        {
            foreach (var material in architecturalContextMaterials) if (material != null) Destroy(material);
        }

        public void RunArchitecturalContextReview()
        {
            if (Application.isPlaying) StartCoroutine(ArchitecturalContextReview());
        }

        IEnumerator ArchitecturalContextReview()
        {
            var checks = new List<WallReviewCheck>();
            Action<string, bool> check = (name, pass) => checks.Add(new WallReviewCheck { check = name, pass = pass });
            string folder = Path.Combine(Application.dataPath, "..", "Temp", "architecture_visual_revision");
            Directory.CreateDirectory(folder);
            ResetPresentation();
            int registered = allElements.Count;
            check("CURRENT remains available", currentResultsAvailable);
            check("passive context has no structural identities or enabled colliders", ContextIsPassive());
            check("glass transparent and no depth write", contextGlass.renderQueue == 3000 && contextGlass.GetInt("_ZWrite") == 0);
            check("two outboard boxes use model columns", visualContextGroups.FindAll(g => g.root.name.Contains("PROJECTING_GLASS_BOX")).Count == 2);
            check("two rising stair flights and one horizontal link", visualContextGroups.FindAll(g => g.kind == "stairs").Count == 3 &&
                architecturalContextRoot.GetComponentsInChildren<Transform>(true).Length > 0 && visualStairRoute?.Length == 4);
            check("roof panels cover both wings and share one edge", mainVisualRoofs.Count == 2 &&
                Mathf.Abs(mainVisualRoofs[0].max.x - mainVisualRoofs[1].min.x) < .001f &&
                Mathf.Abs(mainVisualRoofs[0].max.z - mainVisualRoofs[1].max.z) < .001f &&
                model.solids.TrueForAll(s => s.floor != "P4" || s.category != "beam" || s.start == null || s.end == null ||
                    (Mathf.Min(V(s.start).x, V(s.end).x) >= mainVisualRoofs[0].min.x &&
                     Mathf.Max(V(s.start).x, V(s.end).x) <= mainVisualRoofs[1].max.x)));
            check("stair start follows C021 bottom", visualStairRoute != null &&
                Mathf.Abs(visualStairRoute[0].x - (float)TerrainReference("E1-P2-C-021").center[0]) < .001f &&
                Mathf.Abs(visualStairRoute[0].z - ((float)TerrainReference("E1-P2-C-021").center[2] - (float)TerrainReference("E1-P2-C-021").height_m / 2)) < .001f);
            check("first rise ends at C012 bottom", visualStairRoute != null &&
                Mathf.Abs(visualStairRoute[1].x - (float)TerrainReference("E1-P3-C-012").center[0]) < .001f &&
                Mathf.Abs(visualStairRoute[1].z - ((float)TerrainReference("E1-P3-C-012").center[2] - (float)TerrainReference("E1-P3-C-012").height_m / 2)) < .001f);
            check("middle walkway horizontal", visualStairRoute != null && Mathf.Abs(visualStairRoute[1].z - visualStairRoute[2].z) < .001f);
            check("second rise ends at V027 top", visualStairRoute != null &&
                Mathf.Abs(visualStairRoute[3].x - (float)TerrainReference("E1-P3-V-027").start[0]) < .001f &&
                Mathf.Abs(visualStairRoute[3].z - ((float)TerrainReference("E1-P3-V-027").start[2] + (float)TerrainReference("E1-P3-V-027").height_m / 2)) < .001f);
            check("arrival platform touches stair with no gap", visualArrivalPlatform != null && visualStairRoute != null &&
                Mathf.Abs(visualArrivalPlatform.transform.localPosition.z + visualArrivalPlatform.transform.localScale.z / 2 - visualStairRoute[3].z) < .001f &&
                Mathf.Abs(visualArrivalPlatform.transform.localPosition.x + visualArrivalPlatform.transform.localScale.x / 2 - visualStairRoute[3].x) < .001f);
            check("transverse path spans complete terrace Y", transverseAccessWalk != null &&
                Mathf.Abs(transverseAccessWalk.transform.localScale.y - visualSiteBounds.size.y) < .001f &&
                Mathf.Abs(transverseAccessWalk.transform.localPosition.y - visualSiteBounds.center.y) < .001f);
            check("path and entrance use same paving material", transverseAccessWalk != null && transverseAccessWalk.GetComponent<Renderer>().sharedMaterial == contextConcrete);
            check("old floating paving and lower box cap removed", Array.TrueForAll(architecturalContextRoot.GetComponentsInChildren<Transform>(true), t =>
                t.name != "VISUAL_ONLY_Future_context_free_paved_area" && t.name != "VISUAL_ONLY_Lower_exterior_promenade" && t.name != "VISUAL_ONLY_Visual_box_cap"));
            check("old longitudinal terrain path removed", visualTerrainRoot.transform.Find("VISUAL_ONLY_LEVEL_2_ACCESS_V106_V107/VISUAL_ONLY_ENTRY_PATH_TO_V106_V107") == null);
            foreach (string kind in new[] { "facade", "glass", "stairs", "roof", "landscape", "figures" })
                check("visual group " + kind, visualContextGroups.Exists(g => g.kind == kind));
            architecturalContextVisible = false; UpdateArchitecturalContextVisibility();
            check("context master OFF", !architecturalContextRoot.activeSelf);
            yaw = 35; pitch = 24; uiHidden = true;
            yield return new WaitForEndOfFrame(); SaveVisualFrame(folder, "before.png");
            architecturalContextVisible = true; UpdateArchitecturalContextVisibility();
            check("context master ON", architecturalContextRoot.activeSelf);
            yield return new WaitForEndOfFrame(); SaveVisualFrame(folder, "orange_facade.png");
            yaw = 145;
            yield return new WaitForEndOfFrame(); SaveVisualFrame(folder, "glazing_and_stairs.png");
            SetQuickView("Frente");
            yield return new WaitForEndOfFrame(); SaveVisualFrame(folder, "stair_front.png");
            SetQuickView("Planta");
            yield return new WaitForEndOfFrame(); SaveVisualFrame(folder, "roof_and_path_top.png");
            SetQuickView("Lateral");
            yield return new WaitForEndOfFrame(); SaveVisualFrame(folder, "right_access.png");
            uiHidden = false;
            buildingVisible["EDIFICIO_1"] = false; ReapplyAll();
            check("ED1 visual building filter", visualContextGroups.TrueForAll(g => g.building != "EDIFICIO_1" || !g.root.activeSelf));
            buildingVisible["EDIFICIO_1"] = true;
            floorVisible["P2"] = false; ReapplyAll();
            check("P2 visual floor filter", visualContextGroups.TrueForAll(g => g.floor != "P2" || !g.root.activeSelf));
            floorVisible["P2"] = true; ReapplyAll();
            SelectElementById("E1-P2-V-041", false);
            check("existing beam selection", lastSelected != null && lastSelected.humanId == "E1-P2-V-041");
            check("selected beam has saved R results", lastSelected != null && ResultsForSelection(lastSelected, lastSelected.humanId).Count > 0);
            activeDeformationVisible = true; UpdateArchitecturalContextVisibility();
            check("architecture clears deformation", !architecturalContextRoot.activeSelf);
            activeDeformationVisible = false; diagramMode = 1; UpdateArchitecturalContextVisibility();
            check("architecture clears diagrams", !architecturalContextRoot.activeSelf);
            diagramMode = 0; isolateSelected = true; UpdateArchitecturalContextVisibility();
            check("architecture clears isolated element", !architecturalContextRoot.activeSelf);
            isolateSelected = false; diagnosticViewMode = 1; UpdateArchitecturalContextVisibility();
            check("architecture clears FE view", !architecturalContextRoot.activeSelf);
            diagnosticViewMode = 0; UpdateArchitecturalContextVisibility();
            check("registry unchanged throughout review", allElements.Count == registered);
            check("passive context after toggles", ContextIsPassive());
            ResetPresentation(); yaw = 145; pitch = 24;
            openGroups.Clear(); openGroups.Add("CONTEXTO");
            var report = new WallReviewReport { status = checks.TrueForAll(c => c.pass) ? "PASS" : "FAIL", dataset = currentGateStatus, checks = checks };
            File.WriteAllText(Path.Combine(folder, "QA.json"), JsonUtility.ToJson(report, true));
            Debug.Log($"[ARCHITECTURAL CONTEXT REVIEW] {report.status}: {checks.Count} checks; output in Temp/architecture_visual_revision. No dataset changed.");
        }
    }
}
