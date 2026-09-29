using System;
using System.Collections.Generic;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    /// <summary>Bridges CURRENT OpenSees result contracts to the pure evaluator.</summary>
    public partial class ViewerController
    {
        private readonly Dictionary<string, FailureResult> structuralFailureByElementId =
            new Dictionary<string, FailureResult>();
        private bool structuralFailureVisualizationEnabled = true;
        private bool structuralDamageOverlayEnabled;

        FailureResult StructuralFailureFor(string elementId)
        {
            structuralFailureByElementId.TryGetValue(elementId ?? "", out var result);
            return result;
        }

        void RefreshStructuralFailureStates()
        {
            structuralFailureByElementId.Clear();
            if (!currentResultsAvailable || p1l5ReanalysisRequired || analysisResults == null) return;
            var visited = new HashSet<string>();
            foreach (var info in allElements)
            {
                if (info == null || info.isFeCandidateVisual ||
                    (info.category != "beam" && info.category != "column" && info.category != "wall")) continue;
                string id = string.IsNullOrEmpty(info.humanId) ? info.id : info.humanId;
                if (string.IsNullOrEmpty(id) || !visited.Add(id)) continue;
                structuralFailureByElementId[id] = EvaluatePhysicalElementFailure(info, id);
            }
            ApplyStructuralFailureVisualization();
            if (lastSelected != null) ShowInfo(lastSelected);
        }

        FailureResult EvaluatePhysicalElementFailure(ElementInfo info, string id)
        {
            if (!demandCapacityByElementId.TryGetValue(id, out var capacity))
                return StructuralFailureEvaluator.Evaluate(new CurrentElementDemand {
                    elementTag = id, elementType = info.category, caseName = activeAnalysisCase
                }, null);
            var rows = ResultsForSelection(info, id);
            FailureResult governing = null;
            foreach (var row in rows)
            {
                governing = MoreCritical(governing, EvaluateResultEnd(info, id, row, true, capacity));
                governing = MoreCritical(governing, EvaluateResultEnd(info, id, row, false, capacity));
            }
            if (governing != null) return governing;
            return StructuralFailureEvaluator.Evaluate(new CurrentElementDemand {
                elementTag = id, elementType = info.category, caseName = activeAnalysisCase
            }, capacity);
        }

        FailureResult EvaluateResultEnd(ElementInfo info, string id, AnalysisElementResult row, bool atI,
            DemandCapacityElement capacity)
        {
            var f = ForceVector(row, atI);
            if (f == null || f.Count < 6) return null;
            return StructuralFailureEvaluator.Evaluate(new CurrentElementDemand {
                elementTag = id,
                elementType = info.category,
                caseName = activeAnalysisCase,
                controllingAnalysisId = row.analysis_id + (atI ? ":i" : ":j"),
                controllingOpenSeesTag = row.opensees_tag,
                N_kN = f[0] / 1000.0,
                Vy_kN = f[1] / 1000.0,
                Vz_kN = f[2] / 1000.0,
                My_kNm = f[4] / 1000.0,
                Mz_kNm = f[5] / 1000.0
            }, capacity);
        }

        static FailureResult MoreCritical(FailureResult current, FailureResult candidate)
        {
            if (candidate == null) return current;
            if (current == null) return candidate;
            if (current.state == StructuralFailureState.NO_DATA) return candidate;
            if (candidate.state == StructuralFailureState.NO_DATA) return current;
            return candidate.demandCapacityRatio > current.demandCapacityRatio ? candidate : current;
        }

        string BuildStructuralFailureText(string id)
        {
            if (p1l5ReanalysisRequired) return "ESTADO ESTRUCTURAL\nRESULTS STALE\nSe requiere reanálisis antes de evaluar capacidad.";
            var result = StructuralFailureFor(id);
            if (result == null || result.state == StructuralFailureState.NO_DATA)
                return "ESTADO ESTRUCTURAL\nNO CAPACITY DATA\n" + (result != null ? result.message : "Sin correspondencia CURRENT.");
            string title = result.state == StructuralFailureState.CAPACITY_EXCEEDED ? "CAPACIDAD EXCEDIDA"
                : result.state == StructuralFailureState.WARNING ? "ADVERTENCIA" : "OK";
            string capacity = double.IsInfinity(result.demandCapacityRatio)
                ? "fuera de la envolvente P–M" : result.governingCapacity.ToString("F2") + " " + result.demandUnit;
            return $"ESTADO ESTRUCTURAL\n{title}\nD/C = {result.demandCapacityRatio:F2}\n" +
                $"Control: {result.governingMode}\nDemanda: {result.governingDemand:F2} {result.demandUnit}\n" +
                $"Capacidad: {capacity}\nCaso activo: {result.caseName}\n" +
                $"Segmento controlador: {result.controllingAnalysisId} | OpenSees {result.controllingOpenSeesTag}";
        }

        void DrawStructuralFailureSelectedOverlay()
        {
            if (!structuralFailureVisualizationEnabled || lastSelected == null || uiHidden) return;
            string id = string.IsNullOrEmpty(lastSelected.humanId) ? lastSelected.id : lastSelected.humanId;
            var result = StructuralFailureFor(id);
            if (result == null || (result.state != StructuralFailureState.WARNING &&
                result.state != StructuralFailureState.CAPACITY_EXCEEDED)) return;
            string title = result.state == StructuralFailureState.CAPACITY_EXCEEDED
                ? "⚠ CAPACIDAD EXCEDIDA" : "⚠ ADVERTENCIA DE CAPACIDAD";
            Rect box = new Rect(Screen.width * 0.5f - 175f, 82f, 350f, 64f);
            Color old = GUI.color;
            GUI.color = result.state == StructuralFailureState.CAPACITY_EXCEEDED
                ? new Color(0.55f, 0.02f, 0.02f, 0.95f) : new Color(0.58f, 0.25f, 0.01f, 0.95f);
            GUI.DrawTexture(box, whiteTex);
            GUI.color = old;
            var centered = new GUIStyle(currentHeading) { alignment = TextAnchor.MiddleCenter };
            GUI.Label(new Rect(box.x + 6, box.y + 4, box.width - 12, 25), title, centered);
            GUI.Label(new Rect(box.x + 6, box.y + 29, box.width - 12, 28),
                $"{id}  ·  D/C {result.demandCapacityRatio:F2}  ·  {result.governingMode}", centered);
        }

        partial void ApplyStructuralFailureVisualization()
        {
            foreach (var info in allElements)
            {
                if (info == null || info.go == null || info.isFeCandidateVisual ||
                    (info.category != "beam" && info.category != "column" && info.category != "wall")) continue;
                string id = string.IsNullOrEmpty(info.humanId) ? info.id : info.humanId;
                var visualizer = info.go.GetComponent<ElementFailureVisualizer>();
                if (visualizer == null)
                {
                    visualizer = info.go.AddComponent<ElementFailureVisualizer>();
                    visualizer.Initialize(info.baseColor);
                }
                visualizer.Apply(StructuralFailureFor(id), structuralFailureVisualizationEnabled,
                    structuralDamageOverlayEnabled, info.isHighlighted);
            }
        }
    }
}
