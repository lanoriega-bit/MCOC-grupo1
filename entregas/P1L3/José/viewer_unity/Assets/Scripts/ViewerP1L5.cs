using System;
using System.Collections.Generic;
using System.IO;
using System.Globalization;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    [Serializable] public class P1L5ModificationOperation { public string type, element_id, section_id; public float value; }
    [Serializable] public class P1L5ModificationRequest { public string format, request_id, status, created_utc; public List<P1L5ModificationOperation> operations; }
    [Serializable] public class Week7LiveLoad { public float intensity_kN_m2, default_intensity_kN_m2; public string source, description; }
    [Serializable] public class Week7Settings { public Week7LiveLoad live_load; }
    /// <summary>P1L5 CURRENT superposition and transparent analysis-state UI.</summary>
    public partial class ViewerController
    {
        private bool currentResultsAvailable;
        private float p1l5LambdaG = 1.0f, p1l5LambdaQ = 0.5f, p1l5LambdaEX = 0.0f, p1l5LambdaEY = 0.0f;
        private bool p1l5ModelModified;
        private bool p1l5ReanalysisRequired;
        private string week7QInput;
        private Week7Settings week7Settings;
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
            else RefreshStructuralFailureStates();
        }

        internal static string LoadCaseExplanation(string name)
        {
            switch ((name ?? "").ToUpperInvariant())
            {
                case "G": return "G · Carga permanente: peso propio y cargas muertas permanentes del edificio.";
                case "Q": return "Q · Sobrecarga de uso: cargas variables de ocupación, transferidas por áreas tributarias.";
                case "EX": return "EX · Acción horizontal en X: caso lateral/sísmico en el eje global X.";
                case "EY": return "EY · Acción horizontal en Y: caso lateral/sísmico en el eje global Y.";
                case "R": return "R · Respuesta combinada\nR = λG·G + λQ·Q + λEX·EX + λEY·EY\nλ: coeficientes adimensionales sobre resultados ya calculados. No reejecuta OpenSees.";
                default: return "Seleccione un caso base o la respuesta combinada R.";
            }
        }

        float DrawCoefficient(string label, float value)
        {
            GUILayout.BeginHorizontal();
            GUILayout.Label(new GUIContent("λ" + label + " = " + value.ToString("F2"),CoefficientExplanation(label)), currentBody, GUILayout.Width(82));
            bool gravity = label == "G" || label == "Q";
            float next = GUILayout.HorizontalSlider(value, gravity ? 0f : -5f, 5f, GUILayout.Width(130));
            GUILayout.EndHorizontal();
            return Mathf.Round(next * 100f) / 100f;
        }

        internal static string CoefficientExplanation(string name)
        {
            return LoadCaseExplanation(name)+"\nλ"+name+" = 1,00 usa exactamente la respuesta del caso base calculado.\nλ"+name+" = 2,00 aporta dos veces esa respuesta a R; λ"+name+" = 0 la excluye de R.\nModificar λ"+name+" no vuelve a ejecutar OpenSees ni cambia el caso base. Una carga equivalente de R no es una nueva corrida estructural.";
        }

        void DrawP1L5CurrentResultsControls()
        {
            GUILayout.Label(new GUIContent("CURRENT · Caso "+activeAnalysisCase,"OpenSees verificado. R combina bases compatibles sin reanálisis."), currentHeading);
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
                if (GUILayout.Toggle(activeAnalysisCase==name,new GUIContent(name,LoadCaseExplanation(name)), currentButton,GUILayout.Width(44))!= (activeAnalysisCase==name))
                { ActivateAnalysisCase(name); ShowCaseHelp(name); }
            GUILayout.EndHorizontal();
            if(activeAnalysisCase=="R")GUILayout.Label(new GUIContent("R = λG·G + λQ·Q + λEX·EX + λEY·EY","Superposición de respuestas compatibles ya calculadas; los cuatro coeficientes visibles arriba pertenecen a R, no alteran los casos base."),currentBody);
            bool deform = VisualToggle(activeDeformationVisible, "Deformada CURRENT","Desplazamientos del caso activo, amplificados solo visualmente.");
            if (deform != activeDeformationVisible) { activeDeformationVisible = deform; typeVisible["analysis_deformed"] = deform; ReapplyAll(); }
            GUILayout.Label("Amplificación visual ×" + activeDeformationScale.ToString("F0"), currentBody);
            float scale = GUILayout.HorizontalSlider(activeDeformationScale, 1, 250);
            if (Mathf.Abs(scale - activeDeformationScale) > 0.1f) { activeDeformationScale = scale; RebuildActiveDeformedShape(); }
            GUILayout.BeginHorizontal();
            string[] diagramNames = { "OFF", "My", "Mz", "N", "Vy", "Vz", "T" };
            for (int i = 0; i < diagramNames.Length; i++)
            {
                if(i==4){GUILayout.EndHorizontal();GUILayout.BeginHorizontal();}
                if (GUILayout.Button(new GUIContent(diagramNames[i],"Diagrama 3D "+diagramNames[i]+" del caso activo; fuerzas de extremos OpenSees."),currentButton,GUILayout.Width(58))) SetDiagramMode(i);
            }
            GUILayout.EndHorizontal();
            bool plot = VisualToggle(diagram2DVisible, "Gráfico 2D","Gráfico del elemento seleccionado. Mantiene convención de signos, unidades y END_FORCES_INTERPOLATION.");
            if (plot != diagram2DVisible) { diagram2DVisible = plot; if (plot) demandCapacityPlotVisible = false; }
            bool pm = VisualToggle(demandCapacityPlotVisible, "P–M y D/C dinámico","Demanda del caso activo sobre capacidad compatible. Armaduras y capacidad de laboratorio asumidas, no diseño certificado.");
            if (pm != demandCapacityPlotVisible) { demandCapacityPlotVisible = pm; if (pm) diagram2DVisible = false; }
            bool failureView = VisualToggle(structuralFailureVisualizationEnabled,
                "Mapa de capacidad", "OK: material normal. WARNING: naranja. Excedido: rojo. Sin datos: gris. Umbrales existentes sin cambios.");
            if (failureView != structuralFailureVisualizationEnabled)
            { structuralFailureVisualizationEnabled = failureView; ApplyStructuralFailureVisualization(); }
            bool damage = VisualToggle(structuralDamageOverlayEnabled,
                "Daño visual (no analítico)","Ilustración visual. No simula grietas reales ni cambia rigidez o capacidad.");
            if (damage != structuralDamageOverlayEnabled)
            { structuralDamageOverlayEnabled = damage; ApplyStructuralFailureVisualization(); }
            GUILayout.Label(new GUIContent("OK · normal   WARNING · naranja   EXCEEDS · rojo", "Umbrales actuales: 0,80 y 1,00. Gris = NO DATA. Selección cyan tiene prioridad visual."), currentBody);
            GUILayout.Space(4);
            GUILayout.Label(ProjectAnalysisState(), currentBody);
        }

        string ProjectAnalysisState()
        {
            if (p1l5ReanalysisRequired) return "MODELO MODIFICADO · REANÁLISIS REQUERIDO\nQ / EX / EY / R / D-C: STALE";
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
            if (FindRepositoryRoot() == null)
            { p1l5ModificationMessage = "Build de consulta: el reanálisis necesita el repositorio y Python en el PC."; return; }
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
            p1l5ModificationMessage = "MODELO MODIFICADO · REANÁLISIS REQUERIDO. Solicitud qQ pendiente; G/Q/EX/EY/R y D/C STALE.";
            currentResultsAvailable = false;
            analysisResults = null;
            LoadCurrentContract();
            if (currentContract != null)
            {
                currentContract.status = "STALE_REANALYSIS_REQUIRED";
                currentContract.analysis_available = false;
                File.WriteAllText(Path.Combine(Application.streamingAssetsPath, "current_dataset_contract.json"), JsonUtility.ToJson(currentContract, true));
            }
            RefreshStructuralFailureStates();
        }

        void ReanalyseP1L5()
        {
            string root = FindRepositoryRoot();
            if (string.IsNullOrEmpty(root)) { p1l5ModificationMessage = "No se encontró la raíz del repositorio. Usa build_and_validate.ps1."; return; }
            string script = Path.Combine(root, "entregas", "P1L7", "reanalyse_current.ps1");
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
                if (!ReloadCurrentContractAndCheck()) throw new Exception("Contrato CURRENT no válido después del pipeline.");
                // Reload all data/capacity/load meshes, not only result vectors.
                UnityEngine.SceneManagement.SceneManager.LoadScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene().name);
            }
            catch (Exception ex) { p1l5ModificationMessage = "Reanálisis FAIL: " + ex.Message; }
        }

        void DrawP1L5ModificationControls(ElementInfo selected)
        {
            GUILayout.Label(ProjectAnalysisState(), currentBody);
            if (week7Settings == null)
            {
                string path = Path.Combine(Application.streamingAssetsPath, "week7_analysis_settings.json");
                if (File.Exists(path)) week7Settings = JsonUtility.FromJson<Week7Settings>(File.ReadAllText(path));
                if (week7Settings?.live_load != null) week7QInput = week7Settings.live_load.intensity_kN_m2.ToString("G", CultureInfo.InvariantCulture);
                string pendingPath = Path.Combine(Application.streamingAssetsPath, "p1l5_modification_request.json");
                if (File.Exists(pendingPath))
                {
                    var pending = JsonUtility.FromJson<P1L5ModificationRequest>(File.ReadAllText(pendingPath));
                    if (pending?.status == "PENDING" || (currentContract?.status ?? "").Contains("STALE"))
                    { p1l5ReanalysisRequired = true; p1l5ModelModified = true; }
                }
            }
            if (week7Settings?.live_load == null) { GUILayout.Label("qQ: NO DATA; falta configuración CURRENT.", currentBody); return; }
            GUILayout.Label(new GUIContent("qQ · Intensidad física [kN/m²]", "Se aplica a las áreas tributarias CURRENT. " + week7Settings.live_load.description + " Cambiar qQ requiere reanálisis; λQ solo combina resultados."), currentHeading);
            week7QInput = GUILayout.TextField(week7QInput ?? "", currentBody);
            if (GUILayout.Button("Volver al valor inicial del proyecto", currentButton))
                week7QInput = week7Settings.live_load.default_intensity_kN_m2.ToString("G", CultureInfo.InvariantCulture);
            bool validQ = double.TryParse((week7QInput ?? "").Replace(',', '.'), NumberStyles.Float, CultureInfo.InvariantCulture, out double requestedQ)
                && !double.IsNaN(requestedQ) && !double.IsInfinity(requestedQ) && requestedQ >= 0;
            GUI.enabled = validQ;
            if (GUILayout.Button("Guardar qQ · invalidar resultados", currentButton))
                SaveP1L5Request(new P1L5ModificationOperation { type = "SET_Q_INTENSITY", value = requestedQ });
            GUI.enabled = true;
            if (!validQ) GUILayout.Label("Introduce un decimal no negativo en kN/m².", currentBody);
            GUILayout.Label("λQ = " + p1l5LambdaQ.ToString("F2") + " · multiplicador de combinación, no intensidad física.", currentBody);
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
            axis = "MY"; status = "NO CAPACITY DATA";
            var rows = analysisByElementId.TryGetValue(id, out var available) ? available : null;
            if (rows == null || rows.Count == 0 || item?.capacity == null)
                return false;
            double momentMy=0,momentMz=0;
            foreach (var row in rows)
            {
                var i = ForceVector(row, true); var j = ForceVector(row, false);
                if (i == null || j == null) continue;
                p = Math.Max(p, Math.Max(Math.Abs(i[0]), Math.Abs(j[0])) / 1000.0);
                momentMy = Math.Max(momentMy, Math.Max(Math.Abs(i[4]), Math.Abs(j[4])) / 1000.0);
                momentMz = Math.Max(momentMz, Math.Max(Math.Abs(i[5]), Math.Abs(j[5])) / 1000.0);
            }
            double axialDemand=p;
            double CapacityAt(List<DemandCapacityPoint> source)
            {
                if(source==null)return double.NaN;
                var points = new List<DemandCapacityPoint>();
                foreach (var point in source) if (point.valid && point.M_kNm >= 0) points.Add(point);
                points.Sort((a, b) => a.compression_magnitude_kN.CompareTo(b.compression_magnitude_kN));
                for (int k = 0; k < points.Count - 1; k++)
                {
                    double p0 = points[k].compression_magnitude_kN, p1 = points[k + 1].compression_magnitude_kN;
                    if (axialDemand < p0 || axialDemand > p1) continue;
                    double t = Math.Abs(p1 - p0) < 1e-9 ? 0 : (axialDemand - p0) / (p1 - p0);
                    return points[k].M_kNm + t * (points[k + 1].M_kNm - points[k].M_kNm);
                }
                return double.NaN;
            }
            var myPoints=item.capacity.points_my??item.capacity.points;
            var mzPoints=item.capacity.points_mz??item.capacity.points;
            double capacityMy=CapacityAt(myPoints),capacityMz=CapacityAt(mzPoints);
            double ratioMy=capacityMy>0?momentMy/capacityMy:double.NaN;
            double ratioMz=capacityMz>0?momentMz/capacityMz:double.NaN;
            if(double.IsNaN(ratioMy)&&double.IsNaN(ratioMz))return false;
            bool useMz=double.IsNaN(ratioMy)||(!double.IsNaN(ratioMz)&&ratioMz>ratioMy);
            axis=useMz?"MZ":"MY";
            moment=useMz?momentMz:momentMy;
            capacityM=useMz?capacityMz:capacityMy;
            ratio=useMz?ratioMz:ratioMy;
            if (double.IsNaN(capacityM) || capacityM <= 0) return false;
            status = ratio > 1.0 ? "EXCEEDS" : ratio > 0.85 ? "WARNING" : "OK";
            return true;
        }

        string BuildP1L5DemandCapacityText(string id, DemandCapacityElement item)
        {
            if (item?.beam_capacity != null) return BuildP1L5BeamCapacityText(id, item);
            string text = BuildStructuralFailureText(id);
            string assumption = item?.beam_capacity != null ? item.beam_capacity.assumption_status : item?.capacity?.assumption_status;
            string signature = item?.beam_capacity != null ? item.beam_capacity.capacity_signature : item?.capacity?.capacity_signature;
            return text + $"\nSupuesto: {assumption ?? "-"}\nFirma: {signature ?? "-"}";
        }

        string BuildP1L5BeamCapacityText(string id, DemandCapacityElement item)
        {
            if (!analysisByElementId.TryGetValue(id, out var rows) || rows == null || rows.Count == 0)
                return "NO CURRENT DEMAND DATA para esta viga.";
            double my=0,mz=0,vy=0,vz=0;
            foreach(var row in rows)
            {
                var i=ForceVector(row,true);var j=ForceVector(row,false);if(i==null||j==null)continue;
                vy=Math.Max(vy,Math.Max(Math.Abs(i[1]),Math.Abs(j[1]))/1000.0);
                vz=Math.Max(vz,Math.Max(Math.Abs(i[2]),Math.Abs(j[2]))/1000.0);
                my=Math.Max(my,Math.Max(Math.Abs(i[4]),Math.Abs(j[4]))/1000.0);
                mz=Math.Max(mz,Math.Max(Math.Abs(i[5]),Math.Abs(j[5]))/1000.0);
            }
            var c=item.beam_capacity;
            double rMy=c.phi_Mny_kNm>0?my/c.phi_Mny_kNm:double.NaN;
            double rMz=c.phi_Mnz_kNm>0?mz/c.phi_Mnz_kNm:double.NaN;
            double rVy=c.phi_Vy_kN>0?vy/c.phi_Vy_kN:double.NaN;
            double rVz=c.phi_Vz_kN>0?vz/c.phi_Vz_kN:double.NaN;
            double ratio=Math.Max(Math.Max(rMy,rMz),Math.Max(rVy,rVz));
            string[] modes={"My","Mz","Vy","Vz"};double[] ratios={rMy,rMz,rVy,rVz};
            int control=0;for(int k=1;k<ratios.Length;k++)if(ratios[k]>ratios[control])control=k;
            string state=ratio>=1.0?"CAPACIDAD EXCEDIDA":ratio>=0.8?"WARNING":"OK";
            return $"CAPACIDAD DE VIGA · CASO {activeAnalysisCase} · CURRENT\n"+
                $"My  {my:F2} / {c.phi_Mny_kNm:F2} kN·m   D/C {rMy:F3}\n"+
                $"Mz  {mz:F2} / {c.phi_Mnz_kNm:F2} kN·m   D/C {rMz:F3}\n"+
                $"Vy  {vy:F2} / {c.phi_Vy_kN:F2} kN      D/C {rVy:F3}\n"+
                $"Vz  {vz:F2} / {c.phi_Vz_kN:F2} kN      D/C {rVz:F3}\n"+
                "Axial: NO DATA (sin capacidad axial de viga en el contrato)\n"+
                $"CONTROL: {modes[control]} · D/C GLOBAL {ratio:F3}\nESTADO: {state}\n"+
                $"{c.status} · {c.assumption_status}\n{c.note}\nFirma: {c.capacity_signature}";
        }

        void RunE1P2V041SelfCheck()
        {
            const string id="E1-P2-V-041";
            var failures=new List<string>();
            var info=allElements.Find(e=>e!=null&&!e.isFeCandidateVisual&&(e.humanId??e.id)==id);
            if(info==null){Debug.LogError("[E1-P2-V-041 QA] FAIL: elemento no seleccionable");return;}
            var solid=CurrentSolid(info);
            var metadata=MetadataForSelection(info,id);
            var load=CurrentElementLoad(id);
            if(solid==null)failures.Add("solid CURRENT ausente");
            else
            {
                double geometric=Vector3.Distance(info.nodeI,info.nodeJ);
                if(Math.Abs(geometric-info.lengthM)>1e-4)failures.Add("longitud no coincide");
                if(Math.Abs(solid.width_m-0.6)>1e-6||Math.Abs(solid.height_m-0.8)>1e-6)failures.Add("sección no coincide");
                var material=CurrentMaterial(solid.material_id);
                if(solid.material!="G35_10"||material?.resistance?.concrete_fc_pa?.value!=35e6||
                    material?.resistance?.reinforcement_fy_pa?.value!=420e6)failures.Add("material incompleto");
            }
            // FE node numbering changes after central topology regeneration.
            // Verify the actual CURRENT crosswalk, not historical numeric tags.
            // Candidate diagnostics retain pre-adapter node tags; the analysed
            // result and its metadata must agree after retained-node mapping.
            var currentResult=FindP1L5Case("G")?.elements?.Find(x=>x.element_id==id);
            if(metadata.Count!=1||currentResult==null||
               metadata[0].analysis_id!=currentResult.analysis_id||metadata[0].opensees_tag!=currentResult.opensees_tag||
               metadata[0].node_i!=currentResult.node_i||metadata[0].node_j!=currentResult.node_j)
                failures.Add("crosswalk FE no coincide");
            var identity=CurrentMember(id);
            if(identity?.physical_node_i!="N-00985"||identity?.physical_node_j!="N-00986")
                failures.Add("nodos físicos no coinciden");
            if(load?.Q==null||Math.Abs(load.Q.tributary_area_m2-5.208903)>1e-6||load.G==null)
                failures.Add("carga tributaria no coincide");
            foreach(string name in new[]{"G","Q","EX","EY"})
            {
                ActivateAnalysisCase(name);
                if(ResultsForSelection(info,id).Count!=1)failures.Add("resultado "+name+" ausente");
            }
            RebuildP1L5Combination(true);
            var rRows=ResultsForSelection(info,id);
            if(rRows.Count!=1)failures.Add("R ausente");
            else
            {
                var r=ForceVector(rRows[0],true);
                var gCase=FindP1L5Case("G");var qCase=FindP1L5Case("Q");
                var g=gCase?.elements?.Find(x=>x.element_id==id);var q=qCase?.elements?.Find(x=>x.element_id==id);
                var gv=ForceVector(g,true);var qv=ForceVector(q,true);
                if(r==null||gv==null||qv==null)failures.Add("vectores R incompletos");
                else for(int k=0;k<6;k++)if(Math.Abs(r[k]-(p1l5LambdaG*gv[k]+p1l5LambdaQ*qv[k]))>1e-5)
                {failures.Add("superposición R no coincide");break;}
            }
            if(!demandCapacityByElementId.TryGetValue(id,out var cap)||cap?.beam_capacity==null)
                failures.Add("capacidad de viga ausente");
            var failure=StructuralFailureFor(id);
            if(failure==null||failure.state==StructuralFailureState.NO_DATA)failures.Add("D/C dinámico ausente");
            float initialG=p1l5LambdaG;
            p1l5LambdaG=2.5f;RebuildP1L5Combination(true);
            if(StructuralFailureFor(id)?.state!=StructuralFailureState.WARNING)
                failures.Add("transición WARNING ausente");
            p1l5LambdaG=3.0f;RebuildP1L5Combination(true);
            if(StructuralFailureFor(id)?.state!=StructuralFailureState.CAPACITY_EXCEEDED)
                failures.Add("transición CAPACITY_EXCEEDED ausente");
            p1l5LambdaG=initialG;RebuildP1L5Combination(true);
            ShowInfo(info);
            SetDiagramMode(1);
            if(selectedDiagramObjects.Count==0||!diagramCaption.Contains("END_FORCES_INTERPOLATION"))
                failures.Add("diagrama My no trazable");
            ClearSelectedDiagram();diagramMode=0;diagram2DVisible=false;
            ActivateAnalysisCase("R");
            Debug.Log(failures.Count==0
                ?"[E1-P2-V-041 QA] PASS: identidad; geometría; sección; material; cargas; G/Q/EX/EY/R; superposición; D/C; OK/WARNING/CAPACITY_EXCEEDED; END_FORCES_INTERPOLATION."
                :"[E1-P2-V-041 QA] FAIL: "+string.Join(", ",failures));
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
            var g = FindP1L5Case("G");
            int expectedElements=g?.elements?.Count??0, expectedNodes=g?.nodes?.Count??0;
            if (expectedElements==0||expectedNodes==0)failures.Add("caso base G vacío");
            if (p1l4Metadata?.elements == null || p1l4Metadata.elements.Count != expectedElements) failures.Add("metadata CURRENT no coincide con segmentos analizados");
            if (p1l4Metadata?.qa == null || !p1l4Metadata.qa.all_nodes_exist || !p1l4Metadata.qa.all_local_axes_unit_and_orthogonal) failures.Add("QA ejes/nodos CURRENT");
            var r = FindP1L5Case("R");
            if (r?.nodes == null || r.nodes.Count != expectedNodes || r.elements == null || r.elements.Count != expectedElements) failures.Add("R CURRENT incompleto");
            Debug.Log(failures.Count == 0
                ? $"[P1L5 QA] PASS: G/Q/EX/EY/R CURRENT; {expectedElements} segmentos; {expectedNodes} nodos; ejes locales; superposición lista."
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
                foreach (int mode in new[] { 1, 2, 3, 4, 5, 6 })
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
