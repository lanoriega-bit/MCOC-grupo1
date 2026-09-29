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
        private readonly HashSet<string> previouslyExceededElementIds = new HashSet<string>();
        private FailureResult firstExceededEvent;
        private FailureResult currentCriticalFailure;
        private int failureOkCount, failureWarningCount, failureExceededCount, failureNoDataCount;

        FailureResult StructuralFailureFor(string elementId)
        {
            structuralFailureByElementId.TryGetValue(elementId ?? "", out var result);
            return result;
        }

        void RefreshStructuralFailureStates()
        {
            structuralFailureByElementId.Clear();
            failureOkCount = failureWarningCount = failureExceededCount = failureNoDataCount = 0;
            currentCriticalFailure = null;
            if (!currentResultsAvailable || p1l5ReanalysisRequired || analysisResults == null)
            { previouslyExceededElementIds.Clear(); ApplyStructuralFailureVisualization(); return; }
            var visited = new HashSet<string>();
            var exceededNow = new HashSet<string>();
            FailureResult newlyExceeded = null;
            foreach (var info in allElements)
            {
                if (info == null || info.isFeCandidateVisual ||
                    (info.category != "beam" && info.category != "column" && info.category != "wall")) continue;
                string id = string.IsNullOrEmpty(info.humanId) ? info.id : info.humanId;
                if (string.IsNullOrEmpty(id) || !visited.Add(id)) continue;
                var result = EvaluatePhysicalElementFailure(info, id);
                structuralFailureByElementId[id] = result;
                if (result.state == StructuralFailureState.OK) failureOkCount++;
                else if (result.state == StructuralFailureState.WARNING) failureWarningCount++;
                else if (result.state == StructuralFailureState.CAPACITY_EXCEEDED)
                {
                    failureExceededCount++; exceededNow.Add(id);
                    if (currentCriticalFailure == null || result.demandCapacityRatio > currentCriticalFailure.demandCapacityRatio)
                        currentCriticalFailure = result;
                    if (!previouslyExceededElementIds.Contains(id) &&
                        (newlyExceeded == null || result.demandCapacityRatio < newlyExceeded.demandCapacityRatio))
                        newlyExceeded = result;
                }
                else failureNoDataCount++;
            }
            if (newlyExceeded != null)
            {
                newlyExceeded.lambdaG = p1l5LambdaG; newlyExceeded.lambdaQ = p1l5LambdaQ;
                newlyExceeded.lambdaEX = p1l5LambdaEX; newlyExceeded.lambdaEY = p1l5LambdaEY;
                firstExceededEvent = newlyExceeded;
            }
            else if (exceededNow.Count == 0) firstExceededEvent = null;
            previouslyExceededElementIds.Clear();
            foreach (string id in exceededNow) previouslyExceededElementIds.Add(id);
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

        void DrawStructuralFailureGlobalPanel()
        {
            GUILayout.Label("CAPACIDAD ESTRUCTURAL · CURRENT", currentHeading);
            if (p1l5ReanalysisRequired)
            {
                GUILayout.Label("RESULTS STALE · evaluación bloqueada hasta reanálisis.", currentBody);
                return;
            }
            int evaluated = failureOkCount + failureWarningCount + failureExceededCount;
            GUILayout.Label($"{evaluated} elementos evaluados\n" +
                $"{failureOkCount} OK  ·  {failureWarningCount} WARNING\n" +
                $"{failureExceededCount} CAPACITY_EXCEEDED  ·  {failureNoDataCount} NO_DATA", currentBody);
            if (firstExceededEvent != null)
            {
                GUILayout.Label("PRIMERA CAPACIDAD EXCEDIDA", currentHeading);
                GUILayout.Label($"{firstExceededEvent.elementTag}\nD/C {firstExceededEvent.demandCapacityRatio:F2} · {firstExceededEvent.governingMode}\n" +
                    $"λG={firstExceededEvent.lambdaG:F2}  λQ={firstExceededEvent.lambdaQ:F2}  λEX={firstExceededEvent.lambdaEX:F2}  λEY={firstExceededEvent.lambdaEY:F2}", currentBody);
            }
            if (currentCriticalFailure != null && GUILayout.Button("Ver elemento crítico", currentButton))
            {
                var target = allElements.Find(e => e != null && !e.isFeCandidateVisual &&
                    (e.humanId ?? e.id) == currentCriticalFailure.elementTag);
                if (target != null) Select(target);
            }
            GUILayout.Label("La marca indica demanda/capacidad en el análisis lineal. No simula redistribución ni colapso progresivo.", currentBody);
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
