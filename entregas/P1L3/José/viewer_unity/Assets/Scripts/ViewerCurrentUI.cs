using System;
using System.Collections.Generic;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    // Presentation state is separate from archived analysis contracts.
    public partial class ViewerController
    {
        private bool historicalResultsEnabled;
        private bool presentationMode;
        private bool navigationExpanded = true;
        private bool technicalDetail;
        private bool correctionsOnly;
        private bool globalAxesVisible;
        private FullScreenMode previousScreenMode;
        private Vector2 semanticScroll, currentInspectorScroll;
        private readonly HashSet<string> openGroups = new HashSet<string> { "MODELO" };
        private readonly Dictionary<string, bool> buildingVisible = new Dictionary<string, bool> { { "EDIFICIO_1", true }, { "EDIFICIO_2", true } };
        private readonly Dictionary<string, bool> contextVisible = new Dictionary<string, bool>();
        private readonly List<GameObject> globalAxisObjects = new List<GameObject>();
        private GUIStyle currentBody, currentTitle, currentButton, currentHeading;
        private bool ResultsAllowed => historicalResultsEnabled && !presentationMode;

        static bool IsHistoricalLayer(string type)
        {
            return type.StartsWith("seismic_", StringComparison.Ordinal) || type == "analysis_deformed" ||
                type == "analysis_diagram" || type == "p1l4_support" || type == "tributary" || type == "tributary_point";
        }

        void SetHistoricalResults(bool enabled)
        {
            historicalResultsEnabled = enabled && !presentationMode;
            activeDeformationVisible = false;
            diagramMode = 0;
            diagram2DVisible = false;
            demandCapacityPlotVisible = false;
            expandedGraph = null;
            deliveryPanelVisible = false;
            foreach (string key in new List<string>(typeVisible.Keys))
                if (IsHistoricalLayer(key)) typeVisible[key] = false;
            ClearSelectedDiagram();
            ReapplyAll();
        }

        void SetPresentationMode(bool enabled)
        {
            if(enabled&&pendingReviewRow!=null)ResetPresentation();
            presentationMode = enabled;
            uiHidden = false;
            navigationExpanded = !enabled;
            if (enabled)
            {
                SetHistoricalResults(false);
                diagnosticColorsVisible = diagnosticProblemsOnly = correctionsOnly = false;
                diagnosticViewMode = 0;
                diagnosticWalls = diagnosticBeams = diagnosticColumns = true;
                diagnosticEd2Only = false;
                labelsVisible = false;
                localAxesVisible = false;
                ClearSelectedLocalAxes();
                technicalDetail = false;
                inspectorVisible = false;
                foreach (string key in new[] { "fe_candidate", "cad_reference", "column_plan", "node", "diaphragm" })
                    typeVisible[key] = false;
                previousScreenMode = Screen.fullScreenMode;
                if (!Application.isEditor) Screen.fullScreenMode = FullScreenMode.FullScreenWindow;
            }
            else
            {
                inspectorVisible = true;
                if (!Application.isEditor) Screen.fullScreenMode = previousScreenMode;
            }
            ReapplyAll();
        }

        Rect SemanticPanelRect() => new Rect(12, 82, 274, Mathf.Max(160, Screen.height - 128));
        Rect CurrentInspectorRect() => new Rect(Screen.width - 358, 82, 346, Mathf.Max(140, Screen.height - 280));
        Rect OrientationRect() => new Rect(Screen.width - 230, Screen.height - 192, 218, 148);
        Rect CurrentPlotRect() => new Rect(300, 86, Mathf.Max(240, Screen.width - 680), Mathf.Max(220, Screen.height - 145));

        bool IsPointerOverCurrentUi()
        {
            if (uiHidden) return false;
            Vector2 p = Input.mousePosition; p.y = Screen.height - p.y;
            if (p.y < 76 || p.y > Screen.height - 36 || OrientationRect().Contains(p)) return true;
            if (navigationExpanded && SemanticPanelRect().Contains(p)) return true;
            if (lastSelected != null && inspectorVisible && CurrentInspectorRect().Contains(p)) return true;
            if (ResultsAllowed && (diagram2DVisible || demandCapacityPlotVisible || expandedGraph != null)) return true;
            return false;
        }

        void InitCurrentStyles()
        {
            if (currentBody != null) return;
            currentBody = new GUIStyle(GUI.skin.label) { fontSize = 13, wordWrap = true, richText = false, padding = new RectOffset(4,4,4,4) };
            currentBody.normal.textColor = new Color(0.88f, 0.93f, 0.98f);
            currentTitle = new GUIStyle(currentBody) { fontSize = 19, fontStyle = FontStyle.Bold };
            currentHeading = new GUIStyle(currentBody) { fontSize = 14, fontStyle = FontStyle.Bold };
            currentButton = new GUIStyle(GUI.skin.button) { fontSize = 13, padding = new RectOffset(8,8,6,6), wordWrap = true };
        }

        void PanelBackground(Rect r)
        {
            Color old = GUI.color;
            GUI.color = new Color(0.035f, 0.065f, 0.10f, 0.96f);
            GUI.DrawTexture(r, whiteTex);
            GUI.color = old;
        }

        void DrawCurrentUi()
        {
            if (whiteTex == null) whiteTex = MakeTex(2,2,Color.white);
            InitCurrentStyles();
            if (uiHidden) return;
            PanelBackground(new Rect(0,0,Screen.width,72));
            GUI.Label(new Rect(16,8,400,28), "LABORATORIO ESTRUCTURAL", currentTitle);
            GUI.Label(new Rect(17,37,600,26), "MODELO ACTUAL  ·  Edificios 1 y 2  ·  Revisión estructural", currentBody);
            float bx = Screen.width - 515;
            if (GUI.Button(new Rect(bx,17,108,34), navigationExpanded ? "Paneles  −" : "Paneles  +", currentButton)) navigationExpanded = !navigationExpanded;
            if (GUI.Button(new Rect(bx+116,17,226,34), presentationMode ? "Salir de presentación · F11" : "MODO PRESENTACIÓN · F11", currentButton)) SetPresentationMode(!presentationMode);
            if (GUI.Button(new Rect(bx+350,17,150,34), "Modo limpio · H", currentButton)) uiHidden = true;
            if (navigationExpanded) DrawSemanticPanels();
            if (lastSelected != null && inspectorVisible) DrawCurrentInspector();
            DrawOrientationGizmo();
            DrawCurrentAxisLabels();
            DrawPendingGridLabels();
            if (labelsVisible && !presentationMode) DrawLabels();
            if (ResultsAllowed)
            {
                DrawElementDiagram2D();
                DrawDemandCapacityPlot();
                DrawExpandedGraph();
            }
            PanelBackground(new Rect(0,Screen.height-36,Screen.width,36));
            GUI.Label(new Rect(12,Screen.height-32,Screen.width-24,28),
                CurrentStatusLine(), currentBody);
            if (!string.IsNullOrEmpty(GUI.tooltip))
            {
                Rect tip = new Rect(300,Screen.height-103,Mathf.Min(520,Screen.width-620),60);
                PanelBackground(tip); GUI.Label(tip, GUI.tooltip, currentBody);
            }
        }

        bool Accordion(string name)
        {
            bool on = openGroups.Contains(name);
            if (GUILayout.Button((on ? "−  " : "+  ") + name, currentButton, GUILayout.Height(32)))
            {
                if (on) openGroups.Remove(name); else openGroups.Add(name);
                on = !on;
            }
            return on;
        }

        void LayerToggle(string title, params string[] keys)
        {
            bool was = keys.Length > 0 && typeVisible.TryGetValue(keys[0], out var first) && first;
            bool now = GUILayout.Toggle(was, title, GUILayout.Height(25));
            if (was == now) return;
            foreach (string key in keys) typeVisible[key] = now;
            ReapplyAll();
        }

        void DrawSemanticPanels()
        {
            Rect r = SemanticPanelRect(); PanelBackground(r);
            GUILayout.BeginArea(new Rect(r.x+8,r.y+8,r.width-16,r.height-16));
            semanticScroll = GUILayout.BeginScrollView(semanticScroll);
            if (Accordion("MODELO"))
            {
                GUILayout.Label("Modelo actual", currentHeading);
                foreach (string key in new List<string>(buildingVisible.Keys))
                {
                    bool on = GUILayout.Toggle(buildingVisible[key], key == "EDIFICIO_1" ? "Edificio 1" : "Edificio 2", GUILayout.Height(23));
                    if (on != buildingVisible[key]) { buildingVisible[key]=on; ReapplyAll(); }
                }
                foreach (string floor in new[] { "S1", "P1", "P2", "P3", "P4" })
                {
                    GUILayout.BeginHorizontal();
                    bool was = floorVisible.TryGetValue(floor, out var fv) && fv;
                    bool now = GUILayout.Toggle(was, FloorFriendly(floor), GUILayout.Height(25));
                    if (was != now) { floorVisible[floor]=now; ReapplyAll(); }
                    if (GUILayout.Button("Solo", currentButton, GUILayout.Width(54)))
                    { foreach (string f in new List<string>(floorVisible.Keys)) floorVisible[f]=f==floor; ReapplyAll(); }
                    GUILayout.EndHorizontal();
                }
                if (GUILayout.Button("Todos los pisos", currentButton)) { foreach (string f in new List<string>(floorVisible.Keys)) floorVisible[f]=true; ReapplyAll(); }
                LayerToggle("Columnas", "column"); LayerToggle("Vigas", "beam"); LayerToggle("Muros", "wall");
                LayerToggle("Losas visuales · alcance parcial", "architectural_slab", "architectural_slab_edge");
                LayerToggle("Bordes de losa CAD", "slab_edge");
                bool fe = GUILayout.Toggle(diagnosticViewMode==2, "Mostrar malla FE candidata", GUILayout.Height(25));
                if (fe != (diagnosticViewMode==2)) { diagnosticViewMode=fe?2:0; typeVisible["fe_candidate"]=fe; ReapplyAll(); }
                bool axes = GUILayout.Toggle(globalAxesVisible,"Mostrar GLOBAL X/Y/Z",GUILayout.Height(25));
                if (axes != globalAxesVisible) SetGlobalAxesVisible(axes);
                DrawQuickViews();
                if (GUILayout.Button("Restablecer modelo · R",currentButton)) ResetPresentation();
            }
            DrawDeliveryPanels();
            if (Accordion("RESULTADOS"))
            {
                GUILayout.Label("SIN RESULTADOS ACTUALES PARA ESTA GEOMETRÍA",currentHeading);
                GUILayout.Label("Se habilitarán al validar el nuevo modelo FE y su corrida compatible.",currentBody);
                GUI.enabled=false; GUILayout.Button("Caso · Deformada · N / V / T / M",currentButton); GUI.enabled=true;
            }
            if (Accordion("CARGAS"))
            {
                GUILayout.Label("Catálogo auditado · aún no aplicado",currentHeading);
                LayerToggle("Cargas superficiales", "p1l4_load_surface"); LayerToggle("Cargas lineales", "p1l4_load_line");
                GUILayout.Label("Cargas puntuales: posición/receptor pendientes; no se dibujan en la posición del texto CAD.",currentBody);
                LayerToggle("Apoyos geométricos", "support");
                GUILayout.Label("G, Q y áreas tributarias actuales: pendientes de la nueva base FE. Referencias anteriores en Avanzado.",currentBody);
            }
            if (Accordion("ANÁLISIS"))
            {
                GUILayout.Label($"FE candidato · NO EJECUTADO\n{feDiagnostic?.summary?.fe_element_count ?? 0} miembros\n{feDiagnostic?.summary?.candidate_floating_geometry_elements ?? 0} geometrías flotantes",currentBody);
                GUILayout.Label("Las incidencias propuestas requieren revisión estructural antes de calcular fuerzas o desplazamientos.",currentBody);
            }
            if (Accordion("CAPACIDAD"))
                GUILayout.Label("P–M representa resistencia de una sección. La demanda actual estará disponible después de la nueva corrida. Los estudios anteriores están en Avanzado → Histórico.",currentBody);
            if (!presentationMode && Accordion("DIAGNÓSTICO"))
            {
                DrawRevisionChanges();
                DrawColumnStacks();
                DrawPendingReviewControls();
                bool colors=GUILayout.Toggle(diagnosticColorsVisible,"Colores de conectividad",GUILayout.Height(25));
                bool problems=GUILayout.Toggle(diagnosticProblemsOnly,"Solo problemas / no resueltos",GUILayout.Height(25));
                bool changes=GUILayout.Toggle(correctionsOnly,"Solo correcciones POST-P1L4",GUILayout.Height(25));
                if(colors!=diagnosticColorsVisible||problems!=diagnosticProblemsOnly||changes!=correctionsOnly)
                { diagnosticColorsVisible=colors;diagnosticProblemsOnly=problems;correctionsOnly=changes;ReapplyAll(); }
                GUILayout.Label("Verde: conexión esperada\nAzul: extremo libre esperado\nRojo: desconexión\nAmarillo: requiere revisión",currentBody);
            }
            if (Accordion("CONTEXTO"))
            {
                LayerToggle("Contexto físico · solo visual","physical_context");
                if (contextVisible.Count==0)
                    foreach(var item in allElements) if(!string.IsNullOrEmpty(item.physicalCluster)) contextVisible[item.physicalCluster]=true;
                foreach(string cluster in new List<string>(contextVisible.Keys))
                {
                    string friendly=cluster.Contains("STAIR_ACCESS_B")?"Escalera y acceso B":cluster.Contains("STAIR_ACCESS_D")?"Escalera y acceso D":cluster.Contains("CORE")?"Núcleo de ascensores":cluster.Replace('_',' ');
                    bool next=GUILayout.Toggle(contextVisible[cluster],friendly,GUILayout.Height(25));
                    if(next!=contextVisible[cluster]){contextVisible[cluster]=next;ReapplyAll();}
                }
                GUILayout.Label("Escaleras y accesos son contexto documentado. Terreno métrico y superficies no confirmadas siguen pendientes.",currentBody);
                if(GUILayout.Button("Inspeccionar núcleo · Piso 4",currentButton))
                {var core=allElements.Find(e=>e!=null&&e.humanId=="E1-P4-M-007");if(core!=null)Select(core);}
            }
            if (!presentationMode && Accordion("AVANZADO"))
            {
                labelsVisible=GUILayout.Toggle(labelsVisible,"IDs técnicos",GUILayout.Height(25));
                LayerToggle("Referencias CAD","cad_reference"); LayerToggle("Ejes CAD","axis");
                LayerToggle("Cajas provisionales de losa","slab"); LayerToggle("Nodos geométricos","node");
                GUILayout.BeginHorizontal(); searchText=GUILayout.TextField(searchText,40,GUILayout.Height(27));
                if(GUILayout.Button("Buscar",currentButton,GUILayout.Width(64))) DoSearch(); GUILayout.EndHorizontal();
                if(!string.IsNullOrEmpty(searchResult))GUILayout.Label(searchResult,currentBody);
                bool hist=GUILayout.Toggle(historicalResultsEnabled,"Abrir Histórico / Legacy",GUILayout.Height(28));
                if(hist!=historicalResultsEnabled)SetHistoricalResults(hist);
                if(ResultsAllowed)DrawHistoricalControls();
            }
            if(Accordion("AYUDA / CÓMO USAR"))DrawUsageHelp();
            GUILayout.EndScrollView(); GUILayout.EndArea();
        }

        void DrawHistoricalControls()
        {
            GUILayout.Label("HISTÓRICO P1L4\nNo corresponde a la geometría actual",currentHeading);
            GUILayout.BeginHorizontal();
            foreach(string c in new[]{"G","Q","EX","EY","R"}) if(GUILayout.Button(c,currentButton))ActivateAnalysisCase(c);
            GUILayout.EndHorizontal(); GUILayout.Label("Caso histórico: "+activeAnalysisCase,currentBody);
            bool deform=GUILayout.Toggle(activeDeformationVisible,"Deformada histórica",GUILayout.Height(25));
            if(deform!=activeDeformationVisible){activeDeformationVisible=deform;typeVisible["analysis_deformed"]=deform;ReapplyAll();}
            GUILayout.Label("Amplificación visual ×"+activeDeformationScale.ToString("F0"),currentBody);
            float scale=GUILayout.HorizontalSlider(activeDeformationScale,1,250);
            if(Mathf.Abs(scale-activeDeformationScale)>0.1f){activeDeformationScale=scale;RebuildActiveDeformedShape();}
            GUILayout.BeginHorizontal();
            string[] names={"OFF","My","Mz","N","Vy","Vz"};
            for(int i=0;i<names.Length;i++)if(GUILayout.Button(names[i]))SetDiagramMode(i);
            GUILayout.EndHorizontal();
            bool plot2d=GUILayout.Toggle(diagram2DVisible,"Gráfico 2D histórico",GUILayout.Height(25));
            if(plot2d!=diagram2DVisible){diagram2DVisible=plot2d;if(plot2d)demandCapacityPlotVisible=false;}
            bool pm=GUILayout.Toggle(demandCapacityPlotVisible,"P–M histórico / demanda",GUILayout.Height(25));
            if(pm!=demandCapacityPlotVisible){demandCapacityPlotVisible=pm;if(pm)diagram2DVisible=false;}
            LayerToggle("Apoyos FE históricos","p1l4_support"); LayerToggle("Áreas tributarias históricas","tributary","tributary_point");
            if(lastSelected!=null)
            {
                GUILayout.Label("SELECCIÓN EN EL ARCHIVO · NO ACTUAL",currentHeading);
                GUILayout.Label(inspectorAnalysis+"\n"+inspectorCapacity,currentBody);
            }
        }

        static string FloorFriendly(string floor) => floor=="S1" ? "Subterráneo 1" : floor!=null && floor.StartsWith("P") ? "Piso "+floor.Substring(1) : floor ?? "Sin piso";
        static string TypeFriendly(string type)
        {
            switch(type){case "beam":return "Viga";case "column":return "Columna";case "wall":return "Muro";case "slab":case "architectural_slab":return "Losa";case "support":case "p1l4_support":return "Apoyo";default:return type??"Elemento";}
        }

        SolidData CurrentSolid(ElementInfo e)
        {
            if(e==null||model?.solids==null)return null;
            return model.solids.Find(s=>s!=null&&((!string.IsNullOrEmpty(e.elementTag)&&(s.elementTag==e.elementTag||s.solidTag==e.elementTag))||s.id==e.humanId));
        }

        string ConfidenceFriendly(string raw)
        {
            string c=(raw??"").ToUpperInvariant();
            if(c.Contains("UNRESOLVED")||c.Contains("REVIEW")||c.Contains("LOW")||c==""||c.Contains("UNKNOWN"))return "REQUIERE REVISIÓN";
            if(c.Contains("PLAN")||c.Contains("PRIMARY"))return "CONFIRMADO POR PLANO";
            if(c.Contains("CONFIRMED")||c.Contains("CAD")||c.Contains("GEOMETRY"))return "CONFIRMADO POR CAD";
            return "INFERIDO / " + raw;
        }

        void DrawCurrentInspector() => DrawStructuralInspector();

        void DrawUsageHelp()
        {
            GUILayout.Label("1. Selecciona edificio y piso.\n2. Haz clic en un elemento.\n3. Lee su resumen y fuente.\n4. Abre Detalle técnico si lo necesitas.\n5. Los resultados se habilitarán tras una corrida compatible.\n6. Usa XYZ y las vistas rápidas para orientarte.",currentBody);
            GUILayout.Label("Arrastrar: orbitar · Rueda: zoom\nBotón central: desplazar\nR: restablecer · H: solo modelo\nF11: presentación\nGLOBAL Z es vertical; x/y/z locales pertenecen al elemento.",currentBody);
        }

        public void RunCurrentUiSelfCheck()
        {
            var errors=new List<string>();
            if(historicalResultsEnabled||ResultsAllowed)errors.Add("historico activo por defecto");
            foreach(var pair in byType)if(IsHistoricalLayer(pair.Key))foreach(var go in pair.Value)if(go!=null&&go.activeSelf){errors.Add("capa historica visible: "+pair.Key);break;}
            if(model?.solids==null||model.solids.Count==0)errors.Add("modelo actual ausente");
            if(diagram2DVisible||demandCapacityPlotVisible||activeDeformationVisible)errors.Add("resultado visible sin corrida actual");
            Debug.Log((errors.Count==0?"[CURRENT UI QA] PASS: modelo actual; historico apagado; resultados actuales NONE; FE NOT RUN.":"[CURRENT UI QA] FAIL: "+string.Join(", ",errors)));
        }
    }
}
