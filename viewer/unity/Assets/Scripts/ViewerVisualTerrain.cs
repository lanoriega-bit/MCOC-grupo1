using System.Collections.Generic;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    public partial class ViewerController
    {
        // Presentation context only. Never registered as elements, nodes, loads or FE members.
        bool visualTerrainVisible = true, lowerTerrainVisible = true, accessTerrainVisible = true, terrainBaseVisible = true;
        GameObject visualTerrainRoot, lowerTerrainObject, accessTerrainObject, terrainBaseObject;
        Bounds lowerTerrainBounds;
        float lowerTerrainElevation, accessTerrainElevation;
        // Schematic presentation dimensions only, not surveyed architecture.
        const float TerrainMargin = 4f, SiteMargin = 12f, AccessRun = 10f, PathWidth = 3f, TerrainBaseDepth = .6f;

        SolidData TerrainReference(string id)
        {
            return model?.solids?.Find(s => s.human_id == id || s.id == id);
        }

        bool TryFloorEntryElevation(string floor, out float elevation)
        {
            var levels = new List<float>();
            foreach (var solid in model.solids)
                if (solid.building == "EDIFICIO_1" && solid.floor == floor && solid.category == "column" &&
                    solid.center != null && solid.center.Count == 3 && solid.height_m > 0)
                    levels.Add((float)(solid.center[2] - solid.height_m / 2));
            levels.Sort();
            elevation = levels.Count == 0 ? 0 : levels[levels.Count / 2];
            return levels.Count > 0;
        }

        void BuildVisualTerrain()
        {
            if (model?.solids == null) return;
            var columns = new List<SolidData>();
            for (int index = 7; index <= 19; index++)
            {
                var solid = TerrainReference("E1-S1-C-" + index.ToString("D3"));
                if (solid == null || solid.category != "column" || solid.floor != "S1" || solid.center == null)
                { Debug.LogWarning("[VISUAL TERRAIN] Missing column reference; terrain not built. No structural element changed."); return; }
                columns.Add(solid);
            }
            var beamA = TerrainReference("E1-P1-V-106");
            var beamB = TerrainReference("E1-P1-V-107");
            if (beamA?.start == null || beamA.end == null || beamB?.start == null || beamB.end == null ||
                !TryFloorEntryElevation("P1", out lowerTerrainElevation) ||
                !TryFloorEntryElevation("P2", out accessTerrainElevation) || accessTerrainElevation <= lowerTerrainElevation)
            { Debug.LogWarning("[VISUAL TERRAIN] Missing level/access references; terrain not built."); return; }

            float xmin = float.PositiveInfinity, xmax = float.NegativeInfinity;
            float ymin = float.PositiveInfinity, ymax = float.NegativeInfinity, bottom = float.PositiveInfinity;
            foreach (var column in columns)
            {
                var c = V(column.center);
                xmin = Mathf.Min(xmin, c.x - (float)column.width_m / 2);
                xmax = Mathf.Max(xmax, c.x + (float)column.width_m / 2);
                ymin = Mathf.Min(ymin, c.y - (float)column.depth_m / 2);
                ymax = Mathf.Max(ymax, c.y + (float)column.depth_m / 2);
                bottom = Mathf.Min(bottom, c.z - (float)column.height_m / 2);
            }
            bottom -= TerrainBaseDepth;
            // Extend ONLY the presentation terrace to the user-specified column line.
            var terraceEdge = TerrainReference("E1-S1-C-004");
            var terraceEdgeB = TerrainReference("E1-S1-C-005");
            var terraceEdgeC = TerrainReference("E1-S1-C-006");
            if (terraceEdge?.center == null || terraceEdgeB?.center == null || terraceEdgeC?.center == null ||
                Mathf.Abs((float)terraceEdge.center[0] - (float)terraceEdgeB.center[0]) > .001f ||
                Mathf.Abs((float)terraceEdge.center[0] - (float)terraceEdgeC.center[0]) > .001f)
            { Debug.LogWarning("[VISUAL TERRAIN] Intermediate edge references unavailable; no invented extension."); return; }
            visualTerrainRoot = new GameObject("VISUAL_ONLY_TERRAIN_NO_FE");
            visualTerrainRoot.transform.SetParent(transform, false);

            // Only the exterior +X side, adjacent to the physical outer column/beam face.
            float near = Mathf.Max(V(beamA.start).x, V(beamA.end).x, V(beamB.start).x, V(beamB.end).x);
            near += Mathf.Max((float)beamA.width_m, (float)beamB.width_m) / 2;
            near = Mathf.Max(near, xmax);
            float accessYmin = Mathf.Min(V(beamA.start).y, V(beamA.end).y, V(beamB.start).y, V(beamB.end).y) - TerrainMargin;
            float accessYmax = Mathf.Max(V(beamA.start).y, V(beamA.end).y, V(beamB.start).y, V(beamB.end).y) + TerrainMargin;
            // A broad lower level supports BOTH wings without hiding their S1 columns.
            // It joins the two raised boxes below grade, rather than introducing a slope.
            float siteXmin = xmin, siteXmax = near + AccessRun, siteYmin = accessYmin, siteYmax = accessYmax;
            float siteBase = bottom;
            foreach (var solid in model.solids)
            {
                if (solid.category != "column" || solid.center == null || solid.center.Count != 3) continue;
                Vector3 p = V(solid.center);
                siteXmin = Mathf.Min(siteXmin, p.x - (float)solid.width_m / 2);
                siteXmax = Mathf.Max(siteXmax, p.x + (float)solid.width_m / 2);
                siteYmin = Mathf.Min(siteYmin, p.y - (float)solid.depth_m / 2);
                siteYmax = Mathf.Max(siteYmax, p.y + (float)solid.depth_m / 2);
                siteBase = Mathf.Min(siteBase, p.z - (float)solid.height_m / 2 - TerrainBaseDepth);
            }
            float baseTop = siteBase + TerrainBaseDepth - .04f;
            var siteBounds = TerrainBox(siteXmin - SiteMargin, siteXmax + SiteMargin, siteYmin - SiteMargin,
                siteYmax + SiteMargin, siteBase - .4f, baseTop);
            terrainBaseObject = CreateTerrainTerrace("VISUAL_ONLY_CONTINUOUS_SITE_FUTURE_CONTEXT", siteBounds);
            // Complete lateral bands reach the site's two Y edges. X separates the
            // levels: retain the low ED2 sector, intermediate ED1, exterior P2 access.
            // Adjacent raised boxes share one boundary, not overlapping interior pieces.
            lowerTerrainBounds = TerrainBox((float)terraceEdge.center[0], near, siteBounds.min.y,
                siteBounds.max.y, bottom, lowerTerrainElevation);
            lowerTerrainObject = CreateTerrainTerrace("VISUAL_ONLY_LEVEL_1_S1_C007_C019", lowerTerrainBounds, true);
            var accessBounds = TerrainBox(near, siteBounds.max.x, siteBounds.min.y,
                siteBounds.max.y, bottom, accessTerrainElevation);
            accessTerrainObject = CreateTerrainTerrace("VISUAL_ONLY_LEVEL_2_ACCESS_V106_V107", accessBounds);
            // Paving is now in the optional architecture/context layer: arrival plaza
            // and a full-width transverse path. Do not retain the old longitudinal strip.
            UpdateVisualTerrainVisibility();
            bool covered = columns.TrueForAll(c => {
                Vector3 p = V(c.center);
                return lowerTerrainBounds.Contains(p) && p.z + (float)c.height_m / 2 <= lowerTerrainElevation + .001f;
            });
            bool passive = true;
            foreach (var child in visualTerrainRoot.GetComponentsInChildren<Transform>(true))
            {
                var collider = child.GetComponent<Collider>();
                if (child.GetComponent<ElementInfo>() != null || (collider != null && collider.enabled)) passive = false;
            }
            bool perimeter = Mathf.Abs(lowerTerrainBounds.min.y - siteBounds.min.y) < .001f &&
                Mathf.Abs(lowerTerrainBounds.max.y - siteBounds.max.y) < .001f &&
                Mathf.Abs(accessBounds.min.y - siteBounds.min.y) < .001f &&
                Mathf.Abs(accessBounds.max.y - siteBounds.max.y) < .001f &&
                Mathf.Abs(accessBounds.max.x - siteBounds.max.x) < .001f &&
                Mathf.Abs(lowerTerrainBounds.max.x - accessBounds.min.x) < .001f;
            if (covered && passive && perimeter)
                Debug.Log($"[VISUAL TERRAIN QA] PASS: 13 S1 columns covered; P1 entry={lowerTerrainElevation:F3} m; P2 entry={accessTerrainElevation:F3} m; passive context only; full-width terraces reach site perimeter and share boundary.");
            else Debug.LogError("[VISUAL TERRAIN QA] FAIL: coverage/passive context. No structural data changed.");
        }

        Bounds TerrainBox(float xmin, float xmax, float ymin, float ymax, float bottom, float top)
        {
            return new Bounds(new Vector3((xmin + xmax) / 2, (ymin + ymax) / 2, (bottom + top) / 2),
                new Vector3(xmax - xmin, ymax - ymin, top - bottom));
        }

        Material TerrainPaving() => VisualSurface("VISUAL_ONLY_PAVING", new Color(.56f, .55f, .49f), 0, 0, .08f);

        GameObject CreateTerrainBox(string name, Transform parent, Bounds bounds, Material material)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name; go.layer = 2;
            var collider = go.GetComponent<Collider>();
            collider.enabled = false; Destroy(collider);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = bounds.center;
            go.transform.localScale = bounds.size;
            go.GetComponent<Renderer>().sharedMaterial = material;
            return go;
        }

        GameObject CreateTerrainTerrace(string name, Bounds bounds, bool concrete = false)
        {
            var group = new GameObject(name); group.layer = 2;
            group.transform.SetParent(visualTerrainRoot.transform, false);
            var bodyBounds = bounds;
            bodyBounds.SetMinMax(bounds.min, new Vector3(bounds.max.x, bounds.max.y, bounds.max.z - .03f));
            CreateTerrainBox(name + "_BODY", group.transform, bodyBounds,
                VisualSurface("VISUAL_ONLY_TERRACE_BODY", concrete ? new Color(.53f, .55f, .55f) : new Color(.29f, .30f, .26f), 0, 0, .08f));
            // A flush grass cap gives a readable green surface and neutral retaining faces.
            var grassBounds = bounds;
            grassBounds.SetMinMax(new Vector3(bounds.min.x, bounds.min.y, bounds.max.z - .03f), bounds.max);
            CreateTerrainBox(name + (concrete ? "_CONCRETE" : "_GRASS"), group.transform, grassBounds,
                VisualSurface(concrete ? "VISUAL_ONLY_TERRACE_CONCRETE" : "VISUAL_ONLY_GRASS",
                    concrete ? new Color(.67f, .68f, .67f) : new Color(.28f, .37f, .24f), 0, 0, .05f));
            return group;
        }

        void UpdateVisualTerrainVisibility()
        {
            if (visualTerrainRoot == null) return;
            bool building = !buildingVisible.ContainsKey("EDIFICIO_1") || buildingVisible["EDIFICIO_1"];
            bool otherBuilding = !buildingVisible.ContainsKey("EDIFICIO_2") || buildingVisible["EDIFICIO_2"];
            visualTerrainRoot.SetActive(visualTerrainVisible && (building || otherBuilding) && diagnosticViewMode != 1 && !isolateSelected);
            terrainBaseObject.SetActive(terrainBaseVisible);
            lowerTerrainObject.SetActive(building && lowerTerrainVisible && (!floorVisible.ContainsKey("S1") || floorVisible["S1"]));
            accessTerrainObject.SetActive(building && accessTerrainVisible &&
                ((!floorVisible.ContainsKey("P1") || floorVisible["P1"]) || (!floorVisible.ContainsKey("P2") || floorVisible["P2"])));
        }

        void DrawVisualTerrainControls()
        {
            bool all = GUILayout.Toggle(visualTerrainVisible, new GUIContent("Terreno y acceso · SOLO VISUAL", "Sin FE, cargas ni colisiones. Apágalo para inspeccionar columnas enterradas."), GUILayout.Height(25));
            bool site = GUILayout.Toggle(terrainBaseVisible, "Base continua · entorno ampliado", GUILayout.Height(25));
            bool lower = GUILayout.Toggle(lowerTerrainVisible, "Nivel 1 · cubre S1 C-007 a C-019", GUILayout.Height(25));
            bool upper = GUILayout.Toggle(accessTerrainVisible, "Nivel 2 · acceso base de P2", GUILayout.Height(25));
            if (all != visualTerrainVisible || site != terrainBaseVisible || lower != lowerTerrainVisible || upper != accessTerrainVisible)
            { visualTerrainVisible = all; terrainBaseVisible = site; lowerTerrainVisible = lower; accessTerrainVisible = upper; UpdateVisualTerrainVisibility(); }
            if (visualTerrainRoot != null)
                GUILayout.Label($"Terrazas Z: {lowerTerrainElevation:F2} / {accessTerrainElevation:F2} m\nIntermedia de hormigón; entorno esquemático.", currentBody);
        }
    }
}
