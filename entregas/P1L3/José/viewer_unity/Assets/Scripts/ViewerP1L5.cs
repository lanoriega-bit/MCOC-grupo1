using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    [Serializable] public class P1L5ModificationOperation { public string type, element_id, section_id; public float value; }
    [Serializable] public class P1L5ModificationRequest { public string format, request_id, status, created_utc; public List<P1L5ModificationOperation> operations; }
    /// <summary>P1L5 CURRENT superposition and transparent analysis-state UI.</summary>
    public partial class ViewerController
    {
        private bool currentResultsAvailable;
        private float p1l5LambdaG = 1.0f, p1l5LambdaQ = 0.5f, p1l5LambdaEX = 0.0f, p1l5LambdaEY = 0.0f;
        private bool p1l5ModelModified;
        private bool p1l5ReanalysisRequired;
        private float p1l5RequestedQScale = 1.30f;
        private string p1l5ModificationMessage = "Sin cambios pendientes.";

        AnalysisResultsData FindP1L5Case(string name)
        {
            if (analysisCases?.cases == null) return null;
            foreach (var row in analysisCases.cases)
                if (row != null && string.Equals((row.case_name ?? "").Replace("CASE_", ""), name, StringComparison.OrdinalIgnoreCase)) return row;
            return null;
        }

        static List<double> SumVector(List<double>[] vectors, float[] factors)
        {
            var answer = new List<double>();
            for (int i = 0; i < 6; i++)
            {
                double value = 0;
                for (int j = 0; j < vectors.Length; j++)
                    if (vectors[j] != null && vectors[j].Count > i) value += factors[j] * vectors[j][i];
                answer.Add(value);
            }
            return answer;
        }

        void InitializeP1L5Superposition()
        {
            if (!currentResultsAvailable) return;
            RebuildP1L5Combination(false);
        }

        void RebuildP1L5Combination(bool activate)
        {
            var names = new[] { "G", "Q", "EX", "EY" };
            var factors = new[] { p1l5LambdaG, p1l5LambdaQ, p1l5LambdaEX, p1l5LambdaEY };
            var basis = new AnalysisResultsData[4];
            for (int i = 0; i < 4; i++) basis[i] = FindP1L5Case(names[i]);
            if (basis[0]?.elements == null || basis[0]?.nodes == null) return;

            var elementMaps = new Dictionary<string, AnalysisElementResult>[4];
            var nodeMaps = new Dictionary<int, AnalysisNodeResult>[4];
            for (int i = 0; i < 4; i++)
            {
                elementMaps[i] = new Dictionary<string, AnalysisElementResult>();
                nodeMaps[i] = new Dictionary<int, AnalysisNodeResult>();
                if (basis[i]?.elements != null) foreach (var row in basis[i].elements) elementMaps[i][row.analysis_id] = row;
                if (basis[i]?.nodes != null) foreach (var row in basis[i].nodes) nodeMaps[i][row.node_tag] = row;
            }
            var combined = new AnalysisResultsData
            {
                format = "MCOC_P1L5_UNITY_LINEAR_SUPERPOSITION_V1",
                run_id = "P1L5_CURRENT_APPROX_V1",
                case_name = "R",
                elements = new List<AnalysisElementResult>(),
                nodes = new List<AnalysisNodeResult>(),
                excluded_elements = basis[0].excluded_elements
            };
            foreach (var seed in basis[0].elements)
            {
                var rows = new AnalysisElementResult[4];
                bool complete = true;
                for (int i = 0; i < 4; i++) complete &= elementMaps[i].TryGetValue(seed.analysis_id, out rows[i]);
                if (!complete) continue;
                combined.elements.Add(new AnalysisElementResult
                {
                    case_name = "R", element_id = seed.element_id, analysis_id = seed.analysis_id,
                    geometry_elementTag = seed.geometry_elementTag, opensees_tag = seed.opensees_tag,
                    type = seed.type, floor = seed.floor, node_i = seed.node_i, node_j = seed.node_j,
                    localForce_end1 = SumVector(new[] { rows[0].localForce_end1, rows[1].localForce_end1, rows[2].localForce_end1, rows[3].localForce_end1 }, factors),
                    localForce_end2 = SumVector(new[] { rows[0].localForce_end2, rows[1].localForce_end2, rows[2].localForce_end2, rows[3].localForce_end2 }, factors)
                });
            }
            foreach (var seed in basis[0].nodes)
            {
                var rows = new AnalysisNodeResult[4];
                bool complete = true;
                for (int i = 0; i < 4; i++) complete &= nodeMaps[i].TryGetValue(seed.node_tag, out rows[i]);
                if (!complete) continue;
                combined.nodes.Add(new AnalysisNodeResult
                {
                    node_tag = seed.node_tag, floor = seed.floor, coord = seed.coord,
                    ux_m = factors[0] * rows[0].ux_m + factors[1] * rows[1].ux_m + factors[2] * rows[2].ux_m + factors[3] * rows[3].ux_m,
                    uy_m = factors[0] * rows[0].uy_m + factors[1] * rows[1].uy_m + factors[2] * rows[2].uy_m + factors[3] * rows[3].uy_m,
                    uz_m = factors[0] * rows[0].uz_m + factors[1] * rows[1].uz_m + factors[2] * rows[2].uz_m + factors[3] * rows[3].uz_m
                });
            }
            var prior = FindP1L5Case("R");
            if (prior != null) analysisCases.cases.Remove(prior);
            analysisCases.cases.Add(combined);
            if (activate)
            {
                ActivateAnalysisCase("R");
                if (diagramMode != 0) RebuildSelectedDiagram();
            }
        }

        float DrawCoefficient(string label, float value)
        {
            GUILayout.BeginHorizontal();
            GUILayout.Label(label + " = " + value.ToString("F2"), currentBody, GUILayout.Width(82));
            float next = GUILayout.HorizontalSlider(value, -1.5f, 1.5f, GUILayout.Width(130));
            GUILayout.EndHorizontal();
            return Mathf.Round(next * 100f) / 100f;
        }

        void DrawP1L5CurrentResultsControls()
        {
            GUILayout.Label("RESULTADOS CURRENT · OpenSees PASS", currentHeading);
            GUILayout.Label("R = λG·G + λQ·Q + λEX·EX + λEY·EY", currentBody);
            float g = DrawCoefficient("G", p1l5LambdaG);
            float q = DrawCoefficient("Q", p1l5LambdaQ);
            float ex = DrawCoefficient("EX", p1l5LambdaEX);
            float ey = DrawCoefficient("EY", p1l5LambdaEY);
            if (g != p1l5LambdaG || q != p1l5LambdaQ || ex != p1l5LambdaEX || ey != p1l5LambdaEY)
            {
                p1l5LambdaG = g; p1l5LambdaQ = q; p1l5LambdaEX = ex; p1l5LambdaEY = ey;
                RebuildP1L5Combination(true);
            }
            GUILayout.BeginHorizontal();
            foreach (string name in new[] { "G", "Q", "EX", "EY", "R" })
                if (GUILayout.Button(name, currentButton)) ActivateAnalysisCase(name);
            GUILayout.EndHorizontal();
            GUILayout.Label("Caso activo: " + activeAnalysisCase + " · CURRENT_APPROX_FALLBACK", currentBody);
            bool deform = GUILayout.Toggle(activeDeformationVisible, "Deformada CURRENT", GUILayout.Height(25));
            if (deform != activeDeformationVisible) { activeDeformationVisible = deform; typeVisible["analysis_deformed"] = deform; ReapplyAll(); }
            GUILayout.Label("Amplificación visual ×" + activeDeformationScale.ToString("F0"), currentBody);
            float scale = GUILayout.HorizontalSlider(activeDeformationScale, 1, 250);
            if (Mathf.Abs(scale - activeDeformationScale) > 0.1f) { activeDeformationScale = scale; RebuildActiveDeformedShape(); }
            GUILayout.BeginHorizontal();
            string[] diagramNames = { "OFF", "My", "Mz", "N", "Vy", "Vz" };
            for (int i = 0; i < diagramNames.Length; i++) if (GUILayout.Button(diagramNames[i])) SetDiagramMode(i);
            GUILayout.EndHorizontal();
            bool plot = GUILayout.Toggle(diagram2DVisible, "Gráfico 2D", GUILayout.Height(25));
            if (plot != diagram2DVisible) { diagram2DVisible = plot; if (plot) demandCapacityPlotVisible = false; }
            bool pm = GUILayout.Toggle(demandCapacityPlotVisible, "P–M y D/C dinámico", GUILayout.Height(25));
            if (pm != demandCapacityPlotVisible) { demandCapacityPlotVisible = pm; if (pm) diagram2DVisible = false; }
            GUILayout.Space(4);
            GUILayout.Label(ProjectAnalysisState(), currentBody);
        }

        string ProjectAnalysisState()
        {
            if (!currentResultsAvailable) return "MODEL: CURRENT\nOPENSees: NOT RUN\nRESULTS: NONE";
            return "MODEL: " + (p1l5ModelModified ? "MODIFIED" : "CURRENT") +
                "\nOPENSees: PASS\nRESULTS: " + (p1l5ReanalysisRequired ? "STALE" : "CURRENT") +
                "\nREANALYSIS REQUIRED: " + (p1l5ReanalysisRequired ? "YES" : "NO");
        }

        string FindRepositoryRoot()
        {
            var directory = new DirectoryInfo(Application.dataPath);
            while (directory != null)
            {
                if (File.Exists(Path.Combine(directory.FullName, "entregas", "P1L5", "build_and_validate.ps1"))) return directory.FullName;
                directory = directory.Parent;
            }
            return null;
        }

        void SaveP1L5Request(P1L5ModificationOperation operation)
        {
            var request = new P1L5ModificationRequest
            {
                format = "MCOC_P1L5_MODIFICATION_REQUEST_V1",
                request_id = DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffZ"),
                status = "PENDING", created_utc = DateTime.UtcNow.ToString("o"),
                operations = new List<P1L5ModificationOperation> { operation }
            };
            string path = Path.Combine(Application.streamingAssetsPath, "p1l5_modification_request.json");
            File.WriteAllText(path, JsonUtility.ToJson(request, true));
            p1l5ModelModified = true; p1l5ReanalysisRequired = true;
            p1l5ModificationMessage = "Cambio guardado en la fuente de solicitudes. Resultados STALE.";
        }

        void ReanalyseP1L5()
        {
            string root = FindRepositoryRoot();
            if (string.IsNullOrEmpty(root)) { p1l5ModificationMessage = "No se encontró la raíz del repositorio. Usa build_and_validate.ps1."; return; }
            string script = Path.Combine(root, "entregas", "P1L5", "build_and_validate.ps1");
            try
            {
                p1l5ModificationMessage = "Reanalizando... Unity puede quedar inmóvil unos segundos.";
                var start = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "powershell.exe",
                    Arguments = "-ExecutionPolicy Bypass -File \"" + script + "\"",
                    WorkingDirectory = root,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                using (var process = System.Diagnostics.Process.Start(start))
                {
                    process.WaitForExit(120000);
                    if (!process.HasExited || process.ExitCode != 0) throw new Exception("El pipeline terminó con error.");
                }
                analysisCases = JsonLoader.LoadP1L5CurrentAnalysisCases();
                p1l4Metadata = JsonLoader.LoadP1L5CurrentStructuralMetadata();
                currentResultsAvailable = analysisCases?.cases != null && analysisCases.cases.Count >= 4;
                BuildP1L4Indexes(); InitializeP1L5Superposition(); ActivateAnalysisCase("R");
                p1l5ModelModified = false; p1l5ReanalysisRequired = false;
                p1l5ModificationMessage = "Reanálisis PASS. Resultados CURRENT recargados.";
            }
            catch (Exception ex) { p1l5ModificationMessage = "Reanálisis FAIL: " + ex.Message; }
        }

        void DrawP1L5ModificationControls(ElementInfo selected)
        {
            GUILayout.Label(ProjectAnalysisState(), currentBody);
            GUILayout.Label("A. Intensidad real de Q", currentHeading);
            GUILayout.Label("Factor Q = " + p1l5RequestedQScale.ToString("F2"), currentBody);
            p1l5RequestedQScale = Mathf.Round(GUILayout.HorizontalSlider(p1l5RequestedQScale, 0.50f, 2.00f) * 100f) / 100f;
            if (GUILayout.Button("Guardar factor Q en modelo central", currentButton))
                SaveP1L5Request(new P1L5ModificationOperation { type = "SET_Q_SCALE", value = p1l5RequestedQScale });
            if (selected != null && (selected.category == "beam" || selected.category == "column"))
            {
                string id = selected.humanId ?? selected.id;
                string target = selected.category == "beam" ? "SEC_BEAM_RECT_0.400x0.800" : "SEC_COLUMN_RECT_0.700x0.700";
                GUILayout.Label("B. Sección real del elemento seleccionado", currentHeading);
                GUILayout.Label(id + " → " + target, currentBody);
                if (GUILayout.Button("Guardar cambio de sección", currentButton))
                    SaveP1L5Request(new P1L5ModificationOperation { type = "SET_SECTION", element_id = id, section_id = target });
            }
            else GUILayout.Label("Selecciona una viga o columna para cambiar su sección.", currentBody);
            GUI.enabled = p1l5ReanalysisRequired;
            if (GUILayout.Button("REANALIZAR · OpenSees · Recargar", currentButton, GUILayout.Height(34))) ReanalyseP1L5();
            GUI.enabled = true;
            GUILayout.Label(p1l5ModificationMessage, currentBody);
            GUILayout.Label("Mover sliders NO requiere reanálisis. Cambiar carga/sección SÍ lo requiere.", currentBody);
        }

        bool TryP1L5DemandCapacity(string id, DemandCapacityElement item, out double p, out double moment,
            out double capacityM, out double ratio, out string axis, out string status)
        {
            p = 0; moment = 0; capacityM = double.NaN; ratio = double.NaN;
            axis = (item?.capacity?.pm_axis ?? "My").ToUpperInvariant(); status = "NO CAPACITY DATA";
            var rows = analysisByElementId.TryGetValue(id, out var available) ? available : null;
            if (rows == null || rows.Count == 0 || item?.capacity?.points == null)
                return false;
            int component = axis == "MZ" ? 5 : 4;
            foreach (var row in rows)
            {
                var i = ForceVector(row, true); var j = ForceVector(row, false);
                if (i == null || j == null) continue;
                p = Math.Max(p, Math.Max(Math.Abs(i[0]), Math.Abs(j[0])) / 1000.0);
                moment = Math.Max(moment, Math.Max(Math.Abs(i[component]), Math.Abs(j[component])) / 1000.0);
            }
            var points = new List<DemandCapacityPoint>();
            foreach (var point in item.capacity.points) if (point.valid && point.M_kNm >= 0) points.Add(point);
            points.Sort((a, b) => a.compression_magnitude_kN.CompareTo(b.compression_magnitude_kN));
            if (points.Count < 2) return false;
            for (int k = 0; k < points.Count - 1; k++)
            {
                double p0 = points[k].compression_magnitude_kN, p1 = points[k + 1].compression_magnitude_kN;
                if (p < p0 || p > p1) continue;
                double t = Math.Abs(p1 - p0) < 1e-9 ? 0 : (p - p0) / (p1 - p0);
                capacityM = points[k].M_kNm + t * (points[k + 1].M_kNm - points[k].M_kNm);
                break;
            }
            if (double.IsNaN(capacityM) || capacityM <= 0) return false;
            ratio = moment / capacityM;
            status = ratio > 1.0 ? "EXCEEDS" : ratio > 0.85 ? "WARNING" : "OK";
            return true;
        }

        string BuildP1L5DemandCapacityText(string id, DemandCapacityElement item)
        {
            if (!TryP1L5DemandCapacity(id, item, out double p, out double moment,
                out double capacityM, out double ratio, out string axis, out string status))
                return "NO CAPACITY DATA o demanda CURRENT fuera del rango/crosswalk compatible.";
            return $"CURRENT R DINÁMICO\nP={p:F2} kN · {axis}={moment:F2} kN·m\nCapacidad interpolada={capacityM:F2} kN·m\nD/C={ratio:F2} · {status}\nCapacidad histórica compatible; demanda CURRENT superpuesta.";
        }

        public void RunActiveDemoSequenceCheck()
        {
            if (currentResultsAvailable) RunP1L5DemoSequenceCheck(); else RunP1L4DemoSequenceCheck();
        }

        void RunP1L5SelfCheck()
        {
            var failures = new List<string>();
            if (analysisCases?.cases == null) failures.Add("contrato de casos ausente");
            else foreach (string name in new[] { "G", "Q", "EX", "EY", "R" }) if (FindP1L5Case(name) == null) failures.Add("caso " + name + " ausente");
            if (p1l4Metadata?.elements == null || p1l4Metadata.elements.Count != 642) failures.Add("metadata CURRENT != 642 segmentos");
            if (p1l4Metadata?.qa == null || !p1l4Metadata.qa.all_nodes_exist || !p1l4Metadata.qa.all_local_axes_unit_and_orthogonal) failures.Add("QA ejes/nodos CURRENT");
            var r = FindP1L5Case("R");
            if (r?.nodes == null || r.nodes.Count != 1124 || r.elements == null || r.elements.Count != 642) failures.Add("R CURRENT incompleto");
            Debug.Log(failures.Count == 0
                ? "[P1L5 QA] PASS: G/Q/EX/EY/R CURRENT; 642 segmentos; 1124 nodos; ejes locales; superposición lista."
                : "[P1L5 QA] FAIL: " + string.Join(", ", failures));
        }

        void RunP1L5DemoSequenceCheck()
        {
            var failures = new List<string>();
            ElementInfo beam = null;
            foreach (var candidate in allElements)
            {
                if (candidate == null || candidate.category != "beam") continue;
                string id = candidate.humanId ?? candidate.id;
                if (analysisByElementId.ContainsKey(id) && p1l4MetadataByElementId.ContainsKey(id)) { beam = candidate; break; }
            }
            if (beam == null) failures.Add("viga CURRENT seleccionable ausente");
            else
            {
                ShowInfo(beam);
                foreach (string name in new[] { "G", "Q", "EX", "EY", "R" })
                {
                    ActivateAnalysisCase(name);
                    if (ResultsForSelection(beam, beam.humanId ?? beam.id).Count == 0) failures.Add("sin resultado " + name);
                }
                foreach (int mode in new[] { 1, 2, 3, 4, 5 })
                {
                    SetDiagramMode(mode);
                    if (selectedDiagramObjects.Count == 0) failures.Add("diagrama CURRENT modo " + mode);
                }
                activeDeformationVisible = true; typeVisible["analysis_deformed"] = true; ReapplyAll();
                if (activeDeformationObjects.Count == 0) failures.Add("deformada CURRENT ausente");
            }
            float oldQ = p1l5LambdaQ;
            p1l5LambdaQ = oldQ + 0.1f; RebuildP1L5Combination(true);
            if (activeAnalysisCase != "R") failures.Add("superposición no activa R");
            p1l5LambdaQ = oldQ; RebuildP1L5Combination(true);
            Debug.Log(failures.Count == 0
                ? "[P1L5 DEMO QA] PASS: selección; casos; deformada; My/Mz/N/Vy/Vz; sliders y R instantánea."
                : "[P1L5 DEMO QA] FAIL: " + string.Join(", ", failures));
        }
    }
}
