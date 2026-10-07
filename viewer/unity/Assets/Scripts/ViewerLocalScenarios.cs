using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Threading.Tasks;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    [Serializable] public class LocalScenarioRequest
    {
        public string scenario_id, base_sha256, building, floor, mode;
        public List<double> rectangle_xy;
        public double persons, mass_per_person_kg, total_mass_kg, q_local_kN_m2;
    }
    [Serializable] public class LocalReceiver
    {
        public string element_id;
        public double intersection_area_m2, force_N;
        public int node_i, node_j;
    }
    [Serializable] public class LocalAllocation
    {
        public double drawn_area_m2, effective_area_m2, q_local_kN_m2, force_N, z_m;
        public List<LocalReceiver> receivers;
        public List<double> surface_vertices_xy_flat;
        public List<int> surface_triangles;
    }
    [Serializable] public class LocalScenarioPayload
    {
        public string status, scenario_id, base_sha256, error;
        public LocalAllocation allocation;
        public AnalysisResultsData increment;
    }

    /// <summary>Desktop-only, asynchronous temporary Q_LOCAL. BASE is never edited.</summary>
    public partial class ViewerController
    {
        string localBuilding = "EDIFICIO_1", localFloor = "P2";
        int localMode;
        string localPeople = "10", localPersonKg = "68", localMass = "680", localIntensity = "0.334";
        bool localSelecting, localDragging, localAreaVisible = true, localActive;
        Vector2 localStart, localEnd;
        double localPlaneZ;
        bool localRectangleSet;
        string localMessage = "Carga temporal adicional: no cambia qQ ni CURRENT BASE.";
        LocalScenarioPayload localPayload;
        LocalScenarioRequest localRequest;
        AnalysisResultsData localIncrement;
        GameObject localAreaObject, localBorderObject;
        Material localAreaMaterial;
        System.Diagnostics.Process localProcess;
        Task<string> localStdout, localStderr;
        string localPhase, localOutputPath;
        bool localWantsAnalysis;
        int localRevision, localJobRevision;
        float localJobStarted;
        readonly Dictionary<string, string> localLoadedBase = new Dictionary<string, string>();
        string localSignificantSummary;
        string localCriticalId;
        Dictionary<string,bool> localSavedFloors, localSavedBuildings;
        bool localSavedSlabs;
        bool LocalBusy => localProcess != null;

        static string LocalFileHash(string path)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(path))).Replace("-", "").ToLowerInvariant();
        }
        void InitializeLocalScenarioBase()
        {
            string root = FindRepositoryRoot();
            if (root == null) return;
            foreach (string path in new[] { "model/model_master.json", "model/loads.json", "model/sections.json", "model/materials.json",
                "config/analysis_settings.json", "results/manifest.json", "results/capacity/current_capacity.json",
                "viewer/unity/Assets/StreamingAssets/p1l5_current_analysis_cases.json",
                "viewer/unity/Assets/StreamingAssets/p1l6_current_capacity.json" })
                if (File.Exists(Path.Combine(root, path))) localLoadedBase[path] = LocalFileHash(Path.Combine(root, path));
        }
        bool LocalBaseStillLoaded()
        {
            string root = FindRepositoryRoot();
            if (root == null || localLoadedBase.Count == 0) return false;
            foreach (var entry in localLoadedBase)
                if (!File.Exists(Path.Combine(root, entry.Key)) || LocalFileHash(Path.Combine(root, entry.Key)) != entry.Value) return false;
            return true;
        }
        static bool LocalNumber(string text, out double value)
        {
            bool valid = double.TryParse((text ?? "").Replace(',', '.'), NumberStyles.Float, CultureInfo.InvariantCulture, out value)
                && !double.IsNaN(value) && !double.IsInfinity(value) && value >= 0;
            if (!valid) value = 0;
            return valid;
        }
        bool LocalInputValid()
        {
            if (localMode == 0) return LocalNumber(localPeople, out var n) && Math.Floor(n) == n && LocalNumber(localPersonKg, out _);
            return LocalNumber(localMode == 1 ? localMass : localIntensity, out _);
        }
        LocalScenarioRequest MakeLocalRequest()
        {
            if (!LocalInputValid() || !localRectangleSet) throw new Exception("Define una carga válida y un rectángulo.");
            LocalNumber(localPeople, out var n); LocalNumber(localPersonKg, out var kg);
            LocalNumber(localMass, out var total); LocalNumber(localIntensity, out var q);
            return new LocalScenarioRequest {
                scenario_id = "local_" + DateTime.UtcNow.ToString("yyyyMMddTHHmmssfff") + "_" + Guid.NewGuid().ToString("N").Substring(0, 8),
                building = localBuilding, floor = localFloor, mode = new[] { "persons", "mass", "surface" }[localMode],
                persons = n, mass_per_person_kg = kg, total_mass_kg = total, q_local_kN_m2 = q,
                rectangle_xy = new List<double> { localStart.x, localStart.y, localEnd.x, localEnd.y }
            };
        }
        void LaunchLocalProcess(string arguments, string phase)
        {
            string root = FindRepositoryRoot();
            string python = Path.Combine(root, ".venv-p1l5", "Scripts", "python.exe");
            if (!File.Exists(python)) throw new Exception("Falta el Python del proyecto (.venv-p1l5). Consulta tools/README.md.");
            var start = new System.Diagnostics.ProcessStartInfo {
                FileName = python, Arguments = "-B \"" + Path.Combine(root, "tools", "run_local_scenario.py") + "\" " + arguments,
                WorkingDirectory = root, UseShellExecute = false, CreateNoWindow = true,
                RedirectStandardOutput = true, RedirectStandardError = true
            };
            start.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";
            localPhase = phase; localJobStarted = Time.realtimeSinceStartup;
            localProcess = System.Diagnostics.Process.Start(start);
            localStdout = localProcess.StandardOutput.ReadToEndAsync();
            localStderr = localProcess.StandardError.ReadToEndAsync();
        }
        void StartLocalCalculation(bool analyze)
        {
            if (LocalBusy) return;
            try
            {
                if (!currentResultsAvailable || p1l5ReanalysisRequired || !LocalBaseStillLoaded())
                    throw new Exception("BASE cambió/no está verificado. Recarga Main antes de analizar.");
                DeactivateLocalResults();
                localPayload = null;
                localRequest = MakeLocalRequest(); localWantsAnalysis = analyze;
                localJobRevision = ++localRevision;
                localMessage = analyze ? "ANALIZANDO CARGA LOCAL… BASE sigue disponible." : "Comprobando área efectiva y receptores…";
                LaunchLocalProcess("--fingerprint", "fingerprint");
            }
            catch (Exception ex) { localMessage = ex.Message; }
        }
        void PollLocalCalculation()
        {
            if (!LocalBusy) return;
            if (Time.realtimeSinceStartup - localJobStarted > 120)
            {
                try { localProcess.Kill(); } catch { }
                localProcess.Dispose(); localProcess = null;
                localMessage = "Tiempo de espera agotado. BASE intacto; puedes volver a intentar."; return;
            }
            if (!localProcess.HasExited || !localStdout.IsCompleted || !localStderr.IsCompleted) return;
            string stdout = localStdout.Result, stderr = localStderr.Result;
            int exit = localProcess.ExitCode;
            localProcess.Dispose(); localProcess = null;
            if (localJobRevision != localRevision) return; // Restore/edit discards late results.
            try
            {
                if (localPhase == "fingerprint")
                {
                    if (exit != 0 || !LocalBaseStillLoaded()) throw new Exception("BASE/Python no disponible: " + stderr);
                    localRequest.base_sha256 = stdout.Trim();
                    string directory = Path.Combine(FindRepositoryRoot(), "results", "scenarios");
                    Directory.CreateDirectory(directory);
                    string path = Path.Combine(directory, localRequest.scenario_id + "_request.json");
                    File.WriteAllText(path, JsonUtility.ToJson(localRequest, true));
                    localOutputPath = Path.Combine(directory, localRequest.scenario_id + (localWantsAnalysis ? "_result.json" : "_preview.json"));
                    LaunchLocalProcess("--request \"" + path + "\"" + (localWantsAnalysis ? "" : " --preview"), "calculate");
                    return;
                }
                if (!File.Exists(localOutputPath)) throw new Exception("El worker no devolvió el escenario: " + stderr);
                var payload = JsonUtility.FromJson<LocalScenarioPayload>(File.ReadAllText(localOutputPath));
                if (exit != 0 || payload.status == "FAIL") throw new Exception(payload.error ?? stderr);
                if (payload.scenario_id != localRequest.scenario_id || payload.base_sha256 != localRequest.base_sha256 || !LocalBaseStillLoaded())
                    throw new Exception("Resultado de escenario incompatible con BASE; descartado.");
                localPayload = payload;
                // JsonUtility can instantiate an omitted reference field. Preview is not a response.
                if(payload.status == "PREVIEW") payload.increment = null;
                DrawLocalArea(payload.allocation);
                if (localWantsAnalysis)
                {
                    localIncrement = payload.increment;
                    ValidateLocalIncrement();
                    localActive = true;
                    RebuildLocalCombination();
                    ActivateAnalysisCase("R");
                    if (diagramMode != 0) RebuildSelectedDiagram();
                    localMessage = "ESCENARIO ACTIVO · R_BASE + Q_LOCAL\nBASE permanece intacto.";
                    double maxIncrement = 0;
                    foreach(var node in localIncrement.nodes) maxIncrement = Math.Max(maxIncrement,
                        Math.Sqrt(node.ux_m*node.ux_m+node.uy_m*node.uy_m+node.uz_m*node.uz_m));
                    if(maxIncrement >= 1) localMessage += "\nADVERTENCIA: desplazamiento ≥1 m. Modelo lineal; no simula colapso ni redistribución.";
                    RefreshLocalSummary();
                }
                else localMessage = "Zona válida. Lista para analizar; no hay resultados de escenario todavía.";
            }
            catch (Exception ex) { DeactivateLocalResults(); localPayload = null; localMessage = "CARGA LOCAL: " + ex.Message; }
        }
        void ValidateLocalIncrement()
        {
            var baseline = FindP1L5Case("R");
            if (localIncrement?.elements == null || localIncrement?.nodes == null || baseline?.elements == null || baseline?.nodes == null)
                throw new Exception("Respuesta Q_LOCAL incompleta");
            var ids = new HashSet<string>(); var tags = new HashSet<int>();
            foreach (var r in localIncrement.elements)
            {
                if (!ids.Add(r.analysis_id) || r.localForce_end1?.Count != 6 || r.localForce_end2?.Count != 6) throw new Exception("Crosswalk Q_LOCAL inválido");
                foreach (var f in r.localForce_end1) if (double.IsNaN(f) || double.IsInfinity(f)) throw new Exception("Fuerza no finita");
                foreach (var f in r.localForce_end2) if (double.IsNaN(f) || double.IsInfinity(f)) throw new Exception("Fuerza no finita");
            }
            foreach (var n in localIncrement.nodes)
                if (!tags.Add(n.node_tag) || double.IsNaN(n.ux_m+n.uy_m+n.uz_m) || double.IsInfinity(n.ux_m+n.uy_m+n.uz_m)) throw new Exception("Nodo Q_LOCAL inválido");
            if (ids.Count != baseline.elements.Count || tags.Count != baseline.nodes.Count) throw new Exception("BASE y Q_LOCAL no comparten el mismo FE");
            var localRows = new Dictionary<string, AnalysisElementResult>();
            foreach (var row in localIncrement.elements) localRows[row.analysis_id] = row;
            foreach (var r in baseline.elements)
                if (!localRows.TryGetValue(r.analysis_id, out var q) || r.element_id != q.element_id || r.node_i != q.node_i || r.node_j != q.node_j || r.opensees_tag != q.opensees_tag)
                    throw new Exception("Identidad BASE/Q_LOCAL incompatible");
            foreach (var n in baseline.nodes) if (!tags.Contains(n.node_tag)) throw new Exception("Nodo BASE/Q_LOCAL ausente");
        }
        void RebuildLocalCombination()
        {
            if (!localActive || localIncrement == null) return;
            var baseline = FindP1L5Case("R");
            var rows = new Dictionary<string, AnalysisElementResult>();
            var nodes = new Dictionary<int, AnalysisNodeResult>();
            foreach (var r in localIncrement.elements) rows[r.analysis_id] = r;
            foreach (var n in localIncrement.nodes) nodes[n.node_tag] = n;
            // Clone, never change base lists/vectors, even in memory.
            var combined = JsonUtility.FromJson<AnalysisResultsData>(JsonUtility.ToJson(baseline));
            combined.case_name = "R_SCENARIO"; combined.run_id = localRequest.scenario_id;
            foreach (var r in combined.elements)
            {
                var q = rows[r.analysis_id]; r.case_name = "R_SCENARIO";
                r.localForce_end1 = SumVector(new[] { r.localForce_end1, q.localForce_end1 }, new[] { 1f, 1f });
                r.localForce_end2 = SumVector(new[] { r.localForce_end2, q.localForce_end2 }, new[] { 1f, 1f });
            }
            foreach (var n in combined.nodes) { var q = nodes[n.node_tag]; n.ux_m += q.ux_m; n.uy_m += q.uy_m; n.uz_m += q.uz_m; }
            var prior = FindP1L5Case("R_SCENARIO"); if (prior != null) analysisCases.cases.Remove(prior);
            analysisCases.cases.Add(combined);
        }
        void DeactivateLocalResults()
        {
            bool wasScenario = activeAnalysisCase == "R_SCENARIO";
            localActive = false; localIncrement = null;
            var prior = FindP1L5Case("R_SCENARIO"); if (prior != null) analysisCases.cases.Remove(prior);
            if (wasScenario) { ActivateAnalysisCase("R"); if (diagramMode != 0) RebuildSelectedDiagram(); }
            localSignificantSummary = null; localCriticalId = null;
        }
        void RestoreLocalBase()
        {
            ++localRevision; localSelecting = localDragging = false;
            DeactivateLocalResults(); localPayload = null; localRectangleSet = false;
            ClearLocalArea();
            if(localSavedFloors != null)
            {
                foreach(var item in localSavedFloors)floorVisible[item.Key]=item.Value;
                foreach(var item in localSavedBuildings)buildingVisible[item.Key]=item.Value;
                typeVisible["slab"]=localSavedSlabs;
                localSavedFloors=localSavedBuildings=null;
                ReapplyAll();
            }
            if (currentResultsAvailable) ActivateAnalysisCase("R");
            localMessage = "BASE RESTAURADO · sin ejecutar OpenSees.";
        }
        void ClearLocalArea()
        {
            if (localAreaObject != null) { var mesh = localAreaObject.GetComponent<MeshFilter>()?.sharedMesh; if (mesh != null) Destroy(mesh); Destroy(localAreaObject); }
            if (localBorderObject != null) Destroy(localBorderObject);
            if (localAreaMaterial != null) Destroy(localAreaMaterial);
            localAreaObject = localBorderObject = null; localAreaMaterial = null;
        }
        void DrawLocalArea(LocalAllocation a)
        {
            ClearLocalArea();
            localPlaneZ = a.z_m;
            var vertices = new Vector3[a.surface_vertices_xy_flat.Count/2];
            for (int i = 0; i < vertices.Length; i++) vertices[i] = new Vector3((float)a.surface_vertices_xy_flat[2*i], (float)a.surface_vertices_xy_flat[2*i+1], (float)a.z_m+.08f);
            var triangles = new List<int>();
            for (int i = 0; i < a.surface_triangles.Count; i+=3) { triangles.AddRange(new[] { a.surface_triangles[i],a.surface_triangles[i+1],a.surface_triangles[i+2],a.surface_triangles[i+2],a.surface_triangles[i+1],a.surface_triangles[i] }); }
            var mesh = new Mesh { vertices = vertices, triangles = triangles.ToArray() }; mesh.RecalculateNormals();
            localAreaObject = new GameObject("TEMPORARY_Q_LOCAL_EFFECTIVE_AREA"); localAreaObject.transform.SetParent(transform,false);
            localAreaObject.AddComponent<MeshFilter>().sharedMesh = mesh;
            localAreaMaterial = new Material(Shader.Find("Sprites/Default")) { color = new Color(.9f,.78f,.23f,.32f) };
            localAreaObject.AddComponent<MeshRenderer>().sharedMaterial = localAreaMaterial;
            localAreaObject.layer = 2; localAreaObject.SetActive(localAreaVisible); // Ignore raycast, no collider/ElementInfo.
            DrawLocalRectangle();
        }
        void DrawLocalRectangle()
        {
            if (localBorderObject == null)
            {
                localBorderObject = new GameObject("TEMPORARY_Q_LOCAL_DRAWN_RECTANGLE"); localBorderObject.transform.SetParent(transform,false); localBorderObject.layer = 2;
                var line = localBorderObject.AddComponent<LineRenderer>(); line.useWorldSpace=false; line.loop=true; line.positionCount=4;
                line.startWidth=line.endWidth=.10f; line.sharedMaterial=SeismicLineMat(new Color(.9f,.78f,.23f));
            }
            float z=(float)localPlaneZ+.10f;
            localBorderObject.GetComponent<LineRenderer>().SetPositions(new[] { new Vector3(localStart.x,localStart.y,z),new Vector3(localEnd.x,localStart.y,z),new Vector3(localEnd.x,localEnd.y,z),new Vector3(localStart.x,localEnd.y,z) });
            localBorderObject.SetActive(localAreaVisible);
        }
        bool LocalMousePoint(Vector2 screenPosition,out Vector2 xy)
        {
            xy=default; if(cam==null)return false;
            var plane=new Plane(transform.TransformDirection(Vector3.forward),transform.TransformPoint(new Vector3(0,0,(float)localPlaneZ)));
            var ray=cam.ScreenPointToRay(screenPosition);
            if(!plane.Raycast(ray,out float distance))return false;
            var point=transform.InverseTransformPoint(ray.GetPoint(distance));xy=new Vector2(point.x,point.y);return true;
        }
        bool UpdateLocalSelection()
        {
            if(!localSelecting)return false;
            if(Input.GetKeyDown(KeyCode.Escape)){RestoreLocalBase();localMessage="Selección cancelada.";}
            return true; // No structural picking/orbit while drawing; wheel/middle pan remain available.
        }
        void HandleLocalSelectionGui(Event evt)
        {
            // Event coordinates retain press/release positions even when both arrive in one frame.
            // Polling Input.mousePosition alone can collapse a fast drag to a zero-area rectangle.
            if(!localSelecting||evt==null||evt.button!=0)return;
            Vector2 screen=new Vector2(evt.mousePosition.x,Screen.height-evt.mousePosition.y);
            if(evt.type==EventType.MouseDown&&!IsPointerOverCurrentUi(evt.mousePosition)&&LocalMousePoint(screen,out var start))
            {localStart=localEnd=start;localDragging=true;clickPending=false;DrawLocalRectangle();evt.Use();}
            else if(localDragging&&(evt.type==EventType.MouseDrag||evt.type==EventType.MouseUp)&&LocalMousePoint(screen,out var end))
            {
                localEnd=end;DrawLocalRectangle();
                if(evt.type==EventType.MouseUp)
                {
                    localDragging=localSelecting=false;localRectangleSet=true;
                    if(Math.Abs((localEnd.x-localStart.x)*(localEnd.y-localStart.y))<1e-6)
                    {localRectangleSet=false;ClearLocalArea();localMessage="Arrastra un rectángulo con área; un clic no define una zona.";}
                    else StartLocalCalculation(false);
                }
                evt.Use();
            }
        }
        void StartLocalSelection()
        {
            if(LocalBusy)return;
            RestoreLocalBase();
            SetDiagramMode(0);diagram2DVisible=false;demandCapacityPlotVisible=false;expandedGraph=null;
            bool found=false;
            foreach(var s in model.solids)if(s.category=="slab"&&s.building==localBuilding&&s.floor==localFloor)
            {localPlaneZ=(s.center!=null&&s.center.Count>=3?s.center[2]:s.model_z_m)+(s.height_m*.5);found=true;break;}
            if(!found){localMessage="No hay losa física CURRENT en este edificio/piso.";return;}
            FocusLocalFloor();
            localSelecting=true; localAreaVisible=true;
            localMessage="TOP · arrastra un rectángulo sobre "+localBuilding+" / "+localFloor+". Esc cancela.";
        }
        void FocusLocalFloor()
        {
            if(localSavedFloors==null)
            {
                localSavedFloors=new Dictionary<string,bool>(floorVisible);
                localSavedBuildings=new Dictionary<string,bool>(buildingVisible);
                localSavedSlabs=typeVisible.TryGetValue("slab",out bool slabs)&&slabs;
            }
            SetQuickView("Planta");
            foreach(string floor in new List<string>(floorVisible.Keys))floorVisible[floor]=floor==localFloor;
            foreach(string building in new List<string>(buildingVisible.Keys))buildingVisible[building]=building==localBuilding;
            typeVisible["slab"]=true; ReapplyAll();
        }
        void DrawLocalScenarioControls()
        {
            GUILayout.Label(new GUIContent("CARGA LOCAL · TEMPORAL","Añade peso a una zona del piso; OpenSees analiza Q_LOCAL sin cambiar CURRENT. Personas: 68 kg iniciales, editables."),currentHeading);
            bool enabled=GUI.enabled;GUI.enabled=enabled&&!LocalBusy;
            int mode=GUILayout.Toolbar(localMode,new[]{"Personas","Peso [kg]","kN/m²"});
            GUILayout.BeginHorizontal();
            int b=localBuilding=="EDIFICIO_1"?0:1;
            int next=GUILayout.Toolbar(b,new[]{"Edificio 1","Edificio 2"});
            GUILayout.EndHorizontal();
            string[] floors={"S1","P1","P2","P3","P4"};int fi=Array.IndexOf(floors,localFloor);
            int nf=GUILayout.Toolbar(fi,floors);
            string oldValues=localPeople+"|"+localPersonKg+"|"+localMass+"|"+localIntensity;
            localMode=mode;
            if(localMode==0)
            {GUILayout.Label("Personas · kg/persona",currentBody);GUILayout.BeginHorizontal();localPeople=GUILayout.TextField(localPeople);localPersonKg=GUILayout.TextField(localPersonKg);GUILayout.EndHorizontal();}
            else {GUILayout.Label(localMode==1?"Masa total [kg]":"qLocal adicional [kN/m²]",currentBody);if(localMode==1)localMass=GUILayout.TextField(localMass);else localIntensity=GUILayout.TextField(localIntensity);}
            if(next!=b||nf!=fi){localBuilding=next==0?"EDIFICIO_1":"EDIFICIO_2";localFloor=floors[nf];RestoreLocalBase();}
            else if(oldValues!=localPeople+"|"+localPersonKg+"|"+localMass+"|"+localIntensity||mode!=localLastMode)
            {DeactivateLocalResults();localPayload=null;++localRevision;localMessage="Entrada modificada: vuelve a analizar.";}
            localLastMode=mode;
            bool valid=LocalInputValid();
            if(valid&&localMode<2)
            {
                LocalNumber(localPeople,out var count);LocalNumber(localPersonKg,out var kg);LocalNumber(localMass,out var mass);
                GUILayout.Label($"Peso adicional: {(localMode==0?count*kg:mass)*9.81/1000:F4} kN",currentBody);
            }
            if(!valid)GUILayout.Label("Solo valores finitos no negativos; personas enteras.",currentBody);
            if(GUILayout.Button(localSelecting?"Seleccionando · Esc cancela":"Seleccionar zona · TOP",currentButton))StartLocalSelection();
            if(GUILayout.Button("Zona demo · ED1 P2",currentButton))
            {RestoreLocalBase();localBuilding="EDIFICIO_1";localFloor="P2";FocusLocalFloor();localStart=new Vector2(45,4);localEnd=new Vector2(52,9);localRectangleSet=true;StartLocalCalculation(false);}
            if(localPayload?.allocation!=null)
            {var a=localPayload.allocation;GUILayout.Label($"Dibujada {a.drawn_area_m2:F2} m² · efectiva {a.effective_area_m2:F2} m²\nq adicional {a.q_local_kN_m2:F4} kN/m²\nCarga {a.force_N/1000:F4} kN · vigas receptoras {a.receivers.Count}",currentBody);}
            else if(localRectangleSet)GUILayout.Label("Área efectiva se comprueba al analizar; no se cargan huecos/exterior.",currentBody);
            GUI.enabled=enabled&&!LocalBusy&&valid&&localRectangleSet&&currentResultsAvailable&&!p1l5ReanalysisRequired;
            if(GUILayout.Button("ANALIZAR ESCENARIO",currentButton,GUILayout.Height(32)))StartLocalCalculation(true);
            GUI.enabled=enabled;
            if(GUILayout.Button("RESTAURAR BASE",currentButton))RestoreLocalBase();
            bool visible=GUILayout.Toggle(localAreaVisible,"Mostrar zona local",GUILayout.Height(24));
            if(visible!=localAreaVisible){localAreaVisible=visible;if(localAreaObject!=null)localAreaObject.SetActive(visible);if(localBorderObject!=null)localBorderObject.SetActive(visible);}
            GUILayout.Label(localMessage,currentBody);
            if(localActive)
            {
                GUILayout.Label("Caso visible: "+activeAnalysisCase,currentBody);
                if(activeAnalysisCase!="R_SCENARIO"&&GUILayout.Button("Ver R + Q_LOCAL",currentButton))ActivateAnalysisCase("R");
                GUILayout.Label(localSignificantSummary??"",currentBody);
                if(!string.IsNullOrEmpty(localCriticalId)&&GUILayout.Button("Seleccionar mayor D/C",currentButton))SelectElementById(localCriticalId,true);
            }
            GUILayout.Label(new GUIContent("Q_LOCAL se suma; no sustituye qQ base.","λLOCAL=1. Solo gravedad local; masas y EX/EY no se recalculan. BASE/ESCENARIO en la ficha del elemento. Umbrales de capacidad existentes: 0,80/1,00."),currentBody);
        }
        int localLastMode;

        FailureResult LocalFailureIn(AnalysisResultsData dataset,ElementInfo info,string id)
        {
            if(!demandCapacityByElementId.TryGetValue(id,out var capacity))return null;
            FailureResult governing=null;
            foreach(var row in dataset.elements)if(row.element_id==id||row.geometry_elementTag==info.elementTag)
            {governing=MoreCritical(governing,EvaluateResultEnd(info,id,row,true,capacity));governing=MoreCritical(governing,EvaluateResultEnd(info,id,row,false,capacity));}
            if(governing!=null)governing.caseName=dataset.case_name;
            return governing;
        }
        void RefreshLocalSummary()
        {
            if(!localActive)return;
            var baseline=FindP1L5Case("R");var scenario=FindP1L5Case("R_SCENARIO");int count=0;FailureResult critical=null;
            foreach(var info in allElements)
            {
                if(info.isFeCandidateVisual||(info.category!="beam"&&info.category!="column"&&info.category!="wall"))continue;
                string id=info.humanId??info.id;var b=LocalFailureIn(baseline,info,id);var s=LocalFailureIn(scenario,info,id);
                if(s==null||s.state==StructuralFailureState.NO_DATA)continue;
                if(b!=null&&s.demandCapacityRatio-b.demandCapacityRatio>=.01)count++;
                critical=MoreCritical(critical,s);
            }
            localCriticalId=critical?.elementTag;
            localSignificantSummary=$"Aumento ΔD/C ≥0,01: {count}\nMayor D/C: {localCriticalId??"NO DATA"} · {critical?.demandCapacityRatio:F3}";
        }
        static double LocalEnvelope(AnalysisResultsData dataset,string id,int component)
        {
            double maximum=0;
            foreach(var r in dataset.elements)if(r.element_id==id)
                maximum=Math.Max(maximum,Math.Max(Math.Abs(r.localForce_end1[component]),Math.Abs(r.localForce_end2[component])));
            return maximum/1000;
        }
        static double LocalTranslation(AnalysisResultsData dataset,string id)
        {
            var tags=new HashSet<int>();foreach(var r in dataset.elements)if(r.element_id==id){tags.Add(r.node_i);tags.Add(r.node_j);}
            double maximum=0;foreach(var n in dataset.nodes)if(tags.Contains(n.node_tag))maximum=Math.Max(maximum,Math.Sqrt(n.ux_m*n.ux_m+n.uy_m*n.uy_m+n.uz_m*n.uz_m));
            return maximum*1000;
        }
        void DrawLocalComparison(ElementInfo info,string id)
        {
            if(!localActive)return;
            var b=FindP1L5Case("R");var s=FindP1L5Case("R_SCENARIO");
            GUILayout.Label("R_BASE / R_SCENARIO / Δ",currentHeading);
            GUILayout.Label("Máx. |extremos| del mismo elemento físico; Δ de envolventes, no de un único extremo.",currentBody);
            LocalCompareRow("My [kN·m]",LocalEnvelope(b,id,4),LocalEnvelope(s,id,4));
            LocalCompareRow("Vz [kN]",LocalEnvelope(b,id,2),LocalEnvelope(s,id,2));
            LocalCompareRow("|u| [mm]",LocalTranslation(b,id),LocalTranslation(s,id));
            var bf=LocalFailureIn(b,info,id);var sf=LocalFailureIn(s,info,id);
            if(bf!=null&&sf!=null&&bf.state!=StructuralFailureState.NO_DATA&&sf.state!=StructuralFailureState.NO_DATA)LocalCompareRow("D/C",bf.demandCapacityRatio,sf.demandCapacityRatio);
            else GUILayout.Label("D/C: NO DATA (no se inventa capacidad).",currentBody);
        }
        void LocalCompareRow(string label,double baseline,double scenario)
        {
            double delta=scenario-baseline;
            string change=delta==0?"0":(delta>0?"+":"")+delta.ToString("G5");
            GUILayout.Label($"{label}\n{baseline:G5}  →  {scenario:G5}  · Δ {change}",currentBody);
        }
    }
}
