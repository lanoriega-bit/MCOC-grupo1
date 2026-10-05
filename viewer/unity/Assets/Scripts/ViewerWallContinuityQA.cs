using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    public partial class ViewerController
    {
        [Serializable] public class WallReviewCheck { public string check; public bool pass; }
        [Serializable] public class WallReviewReport { public string status, dataset; public List<WallReviewCheck> checks; }

        public void RunWallContinuityReview()
        {
            if (!Application.isPlaying) return;
            StartCoroutine(WallContinuityReviewRoutine());
        }

        IEnumerator WallContinuityReviewRoutine()
        {
            ResetPresentation();
            var checks = new List<WallReviewCheck>();
            Action<string, bool> check = (name, pass) => checks.Add(new WallReviewCheck { check = name, pass = pass });
            check("CURRENT dataset", currentResultsAvailable && ReloadCurrentContractAndCheck());
            check("nodes ON", typeVisible.ContainsKey("node") && typeVisible["node"]);
            check("visual slabs OFF", !typeVisible["architectural_slab"]);
            check("capacity and damage OFF", !structuralFailureVisualizationEnabled && !structuralDamageOverlayEnabled);
            foreach (string type in new[] { "beam", "column", "wall", "node" })
            {
                check(type + " default ON", typeVisible.ContainsKey(type) && typeVisible[type]);
                ToggleType(type, false);
                bool hidden = true;
                if (byType.ContainsKey(type)) foreach (var go in byType[type]) if (go != null && go.activeSelf) hidden = false;
                check(type + " filter", hidden);
                ToggleType(type, true);
            }
            foreach (string floor in new List<string>(floorVisible.Keys))
            {
                ToggleFloor(floor, false);
                bool hidden = true;
                foreach (var e in allElements) if (e != null && e.floor == floor && e.go != null && e.go.activeSelf) hidden = false;
                check("floor filter " + floor, hidden);
                ToggleFloor(floor, true);
            }
            foreach (string building in new List<string>(buildingVisible.Keys))
            {
                buildingVisible[building] = false; ReapplyAll();
                bool hidden = true;
                foreach (var e in allElements)
                    if (e != null && e.go != null && e.go.activeSelf && (e.category == "beam" || e.category == "column" || e.category == "wall") && e.humanId != null && e.humanId.StartsWith(building == "EDIFICIO_1" ? "E1-" : "E2-")) hidden = false;
                check("building filter " + building, hidden);
                buildingVisible[building] = true; ReapplyAll();
            }
            foreach (string id in new[] { "E1-P2-V-041", "E2-P4-C-004", "E2-P4-C-007", "E1-P4-M-007", "E2-P4-M-009" })
            {
                var element = allElements.Find(e => e != null && (e.humanId == id || e.id == id));
                check("select " + id, element != null);
                if (element == null) continue;
                ShowInfo(element);
                foreach (string name in new[] { "G", "Q", "EX", "EY", "R" })
                {
                    ActivateAnalysisCase(name);
                    check(id + " result " + name, ResultsForSelection(element, id).Count > 0);
                    check("case explanation " + name, LoadCaseExplanation(name).StartsWith(name + " ·"));
                }
            }
            // Compare actual renderer colours before/after D/C, without selection highlight.
            ResetPresentation();
            var colors = new Dictionary<Renderer, Color>();
            foreach (var e in allElements)
                if (e != null && e.go != null && (e.category == "beam" || e.category == "column" || e.category == "wall"))
                { var renderer = e.go.GetComponent<Renderer>(); if (renderer != null) colors[renderer] = renderer.material.color; }
            structuralFailureVisualizationEnabled = true; ApplyStructuralFailureVisualization();
            structuralFailureVisualizationEnabled = false; ApplyStructuralFailureVisualization();
            bool restored = true;
            foreach (var pair in colors) if (pair.Key.material.color != pair.Value) restored = false;
            check("D/C colours restore", restored);
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "../../../../.."));
            string folder = Path.Combine(root, "results", "validation", "wall_continuity");
            Directory.CreateDirectory(folder);
            foreach (string view in new[] { "Iso", "Planta", "Frente", "Lateral" })
            {
                SetQuickView(view);
                yield return null;
                yield return new WaitForEndOfFrame();
                // Use the rendered Game framebuffer; no optional ScreenCapture module.
                var frame = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, false);
                frame.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0);
                frame.Apply();
                File.WriteAllBytes(Path.Combine(folder, "unity_" + view + ".png"), frame.EncodeToPNG());
                Destroy(frame);
                yield return null;
            }
            bool pass = checks.TrueForAll(c => c.pass);
            var report = new WallReviewReport { status = pass ? "PASS" : "FAIL", dataset = currentGateStatus, checks = checks };
            File.WriteAllText(Path.Combine(folder, "UNITY_RUNTIME_QA.json"), JsonUtility.ToJson(report, true));
            Debug.Log("[WALL CONTINUITY UNITY QA] " + report.status + ": " + checks.Count + " checks; captures ISO/TOP/FRONT/RIGHT.");
            ResetPresentation(); SetQuickView("Planta");
        }
    }
}
