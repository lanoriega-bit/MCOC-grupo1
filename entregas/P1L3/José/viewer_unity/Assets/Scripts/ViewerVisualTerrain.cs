using System.Collections.Generic;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    public partial class ViewerController
    {
        // Presentation context only. Never registered as elements, nodes, loads or FE members.
        bool visualTerrainVisible = true, lowerTerrainVisible = true, accessTerrainVisible = true;
        GameObject visualTerrainRoot, lowerTerrainObject, accessTerrainObject;
        Bounds lowerTerrainBounds;
        float lowerTerrainElevation, accessTerrainElevation;
        const float TerrainMargin = 1.5f, AccessPlateau = 3f, AccessRun = 8f, TerrainBaseDepth = .6f;

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
            lowerTerrainBounds = new Bounds(
                new Vector3((xmin + xmax) / 2, (ymin + ymax) / 2, (bottom + lowerTerrainElevation) / 2),
                new Vector3(xmax - xmin + 2 * TerrainMargin, ymax - ymin + 2 * TerrainMargin, lowerTerrainElevation - bottom));
            visualTerrainRoot = new GameObject("VISUAL_ONLY_TERRAIN_NO_FE");
            visualTerrainRoot.transform.SetParent(transform, false);
            lowerTerrainObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
            lowerTerrainObject.name = "VISUAL_ONLY_LEVEL_1_S1_C007_C019";
            var collider = lowerTerrainObject.GetComponent<Collider>();
            collider.enabled = false; Destroy(collider);
            lowerTerrainObject.layer = 2; // Ignore Raycast, including the creation frame.
            lowerTerrainObject.transform.SetParent(visualTerrainRoot.transform, false);
            lowerTerrainObject.transform.localPosition = lowerTerrainBounds.center;
            lowerTerrainObject.transform.localScale = lowerTerrainBounds.size;
            lowerTerrainObject.GetComponent<Renderer>().sharedMaterial = VisualSurface("TERRAIN", new Color(.24f, .29f, .22f), 0, 0, .08f);

            // Only the exterior +X side, adjacent to the physical outer column/beam face.
            float near = Mathf.Max(V(beamA.start).x, V(beamA.end).x, V(beamB.start).x, V(beamB.end).x);
            near += Mathf.Max((float)beamA.width_m, (float)beamB.width_m) / 2;
            near = Mathf.Max(near, xmax);
            float accessYmin = Mathf.Min(V(beamA.start).y, V(beamA.end).y, V(beamB.start).y, V(beamB.end).y) - TerrainMargin;
            float accessYmax = Mathf.Max(V(beamA.start).y, V(beamA.end).y, V(beamB.start).y, V(beamB.end).y) + TerrainMargin;
            accessTerrainObject = CreateVisualAccessMass(near, accessYmin, accessYmax, bottom);
            UpdateVisualTerrainVisibility();
            bool covered = columns.TrueForAll(c => {
                Vector3 p = V(c.center);
                return lowerTerrainBounds.Contains(p) && p.z + (float)c.height_m / 2 <= lowerTerrainElevation + .001f;
            });
            bool passive = lowerTerrainObject.GetComponent<ElementInfo>() == null && accessTerrainObject.GetComponent<ElementInfo>() == null &&
                accessTerrainObject.GetComponent<Collider>() == null && !collider.enabled;
            if (covered && passive)
                Debug.Log($"[VISUAL TERRAIN QA] PASS: 13 S1 columns covered; P1 entry={lowerTerrainElevation:F3} m; P2 entry={accessTerrainElevation:F3} m; passive context only.");
            else Debug.LogError("[VISUAL TERRAIN QA] FAIL: coverage/passive context. No structural data changed.");
        }

        GameObject CreateVisualAccessMass(float near, float ymin, float ymax, float bottom)
        {
            // Convex X/Z profile extruded along Y: flat landing, then schematic embankment.
            // Margins/run are visual choices, NOT surveyed terrain or an accessible-ramp design.
            var profile = new[] {
                new Vector2(near, bottom), new Vector2(near + AccessRun, bottom),
                new Vector2(near + AccessRun, lowerTerrainElevation),
                new Vector2(near + AccessPlateau, accessTerrainElevation), new Vector2(near, accessTerrainElevation)
            };
            var vertices = new List<Vector3>(); var triangles = new List<int>();
            System.Action<Vector3, Vector3, Vector3> triangle = (a, b, c) => {
                int first = vertices.Count; vertices.Add(a); vertices.Add(b); vertices.Add(c);
                triangles.Add(first); triangles.Add(first + 1); triangles.Add(first + 2);
            };
            System.Func<int, float, Vector3> point = (i, y) => new Vector3(profile[i].x, y, profile[i].y);
            for (int i = 1; i < profile.Length - 1; i++)
            {
                triangle(point(0, ymin), point(i, ymin), point(i + 1, ymin));
                triangle(point(0, ymax), point(i + 1, ymax), point(i, ymax));
            }
            for (int i = 0; i < profile.Length; i++)
            {
                int j = (i + 1) % profile.Length;
                triangle(point(i, ymin), point(i, ymax), point(j, ymax));
                triangle(point(i, ymin), point(j, ymax), point(j, ymin));
            }
            var mesh = new Mesh { name = "VISUAL_ONLY_P2_ACCESS_MASS" };
            mesh.SetVertices(vertices); mesh.SetTriangles(triangles, 0); mesh.RecalculateNormals(); mesh.RecalculateBounds();
            var go = new GameObject("VISUAL_ONLY_LEVEL_2_ACCESS_V106_V107"); go.layer = 2;
            go.transform.SetParent(visualTerrainRoot.transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterial = VisualSurface("ACCESS_TERRACE", new Color(.38f, .40f, .34f), 0, 0, .08f);
            return go; // No Collider, ElementInfo, registration, load or analysis reference.
        }

        void UpdateVisualTerrainVisibility()
        {
            if (visualTerrainRoot == null) return;
            bool building = !buildingVisible.ContainsKey("EDIFICIO_1") || buildingVisible["EDIFICIO_1"];
            visualTerrainRoot.SetActive(visualTerrainVisible && building && diagnosticViewMode != 1 && !isolateSelected);
            lowerTerrainObject.SetActive(lowerTerrainVisible && (!floorVisible.ContainsKey("S1") || floorVisible["S1"]));
            accessTerrainObject.SetActive(accessTerrainVisible &&
                ((!floorVisible.ContainsKey("P1") || floorVisible["P1"]) || (!floorVisible.ContainsKey("P2") || floorVisible["P2"])));
        }

        void DrawVisualTerrainControls()
        {
            bool all = GUILayout.Toggle(visualTerrainVisible, new GUIContent("Terreno y acceso · SOLO VISUAL", "Sin FE, cargas ni colisiones. Apágalo para inspeccionar columnas enterradas."), GUILayout.Height(25));
            bool lower = GUILayout.Toggle(lowerTerrainVisible, "Nivel 1 · cubre S1 C-007 a C-019", GUILayout.Height(25));
            bool upper = GUILayout.Toggle(accessTerrainVisible, "Nivel 2 · acceso base de P2", GUILayout.Height(25));
            if (all != visualTerrainVisible || lower != lowerTerrainVisible || upper != accessTerrainVisible)
            { visualTerrainVisible = all; lowerTerrainVisible = lower; accessTerrainVisible = upper; UpdateVisualTerrainVisibility(); }
            if (visualTerrainRoot != null)
                GUILayout.Label($"Niveles Z: {lowerTerrainElevation:F2} / {accessTerrainElevation:F2} m\nForma esquemática; no topografía medida.", currentBody);
        }
    }
}
