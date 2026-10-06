using System;
using System.Collections.Generic;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    // Presentation state is separate from archived analysis contracts.
    public partial class ViewerController
    {
        private bool historicalResultsEnabled;
        private bool historicalArchiveLoaded;
        private bool presentationMode;
        private bool navigationExpanded = true;
        private bool technicalDetail;
        private bool correctionsOnly;
        private bool isolateSelected;
        private bool globalAxesVisible;
        private FullScreenMode previousScreenMode;
        private Vector2 semanticScroll, currentInspectorScroll;
        private readonly HashSet<string> openGroups = new HashSet<string> { "MODELO" };
        private readonly Dictionary<string, bool> buildingVisible = new Dictionary<string, bool> { { "EDIFICIO_1", true }, { "EDIFICIO_2", true } };
        private readonly Dictionary<string, bool> contextVisible = new Dictionary<string, bool>();
        private readonly List<GameObject> globalAxisObjects = new List<GameObject>();
        private GUIStyle currentBody, currentTitle, currentButton, currentHeading, currentChip;
        private bool ResultsAllowed => currentResultsAvailable || (historicalResultsEnabled && !presentationMode);

        static bool IsHistoricalLayer(string type)
        {
            return type.StartsWith("seismic_", StringComparison.Ordinal) || type == "analysis_deformed" ||
                type == "analysis_diagram" || type == "p1l4_support" || type == "tributary" || type == "tributary_point";
        }

        void SetHistoricalResults(bool enabled)
        {
            if (enabled && !currentResultsAvailable && !historicalArchiveLoaded) LoadHistoricalArchiveExplicitly();
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

        void LoadHistoricalArchiveExplicitly()
        {
            historicalArchiveLoaded = true;
            delivery = JsonLoader.LoadDelivery();
            capacity = JsonLoader.LoadCapacity();
            p1l4Metadata = JsonLoader.LoadP1L4StructuralMetadata();
            demandCapacity = JsonLoader.LoadDemandCapacity();
            p1l4LoadCatalog = JsonLoader.LoadP1L4LoadCatalog();
            fiberTexture = JsonLoader.LoadPng("fiber_section.png");
            momentCurvatureTexture = JsonLoader.LoadPng("moment_curvature.png");
            pmInteractionTexture = JsonLoader.LoadPng("pm_interaction.png");
            joseSupports = JsonLoader.LoadJoseSupports();
            analysisCases = JsonLoader.LoadAnalysisCases();
            BuildP1L4Indexes();
            ActivateAnalysisCase("R");
            tributaries = JsonLoader.LoadTributaries("tributary_areas.json");
            if (tributaries != null) BuildTributaries();
            BuildP1L4Supports();
            BuildP1L4Loads();
            seismic = JsonLoader.LoadSeismic();
            if (seismic != null) BuildSeismic();
            Debug.Log("[HISTÓRICO] Archivo P1L3/P1L4 cargado por solicitud explícita; no es CURRENT.");
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

        Rect SemanticPanelRect() => new Rect(12, 82, 294, Mathf.Max(160, Screen.height - 128));
        Rect CurrentInspectorRect() => new Rect(Screen.width - 358, 82, 346, Mathf.Max(140, Screen.height - 280));
        Rect OrientationRect() => new Rect(Screen.width - 230, Screen.height - 192, 218, 148);
        Rect CurrentPlotRect() => new Rect(320, 86, Mathf.Max(240, Screen.width - 700), Mathf.Max(220, Screen.height - 145));

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
            currentButton = new GUIStyle(GUI.skin.button) { fontSize = 13, padding = new RectOffset(10,10,6,6), wordWrap = true };
            StyleVisualControl(currentButton);
            currentChip=new GUIStyle(currentButton) { alignment=TextAnchor.MiddleLeft, fontSize=12 };
        }

        void PanelBackground(Rect r)
        {
            Color old = GUI.color;
            GUI.color = new Color(0.045f, 0.068f, 0.095f, 0.97f);
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
            GUI.Label(new Rect(17,37,600,26), new GUIContent((p1l5ReanalysisRequired?"STALE · REANÁLISIS REQUERIDO":"CURRENT")+"  ·  Edificios 1 y 2  ·  Caso "+activeAnalysisCase,
                "Modelo canónico vigente. Los estilos ladrillo/acero son claves visuales, no materiales estructurales."), currentBody);
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
            DrawStructuralFailureSelectedOverlay();
            if (ResultsAllowed)
            {
                DrawElementDiagram2D();
                DrawDemandCapacityPlot();
                DrawExpandedGraph();
            }
            PanelBackground(new Rect(0,Screen.height-36,Screen.width,36));
            GUI.Label(new Rect(12,Screen.height-32,Screen.width-24,28),
                CurrentStatusLine(), currentBody);
            DrawVisualTooltip();
        }

        bool Accordion(string name)
        {
            bool on = openGroups.Contains(name);
            if (GUILayout.Toggle(on, new GUIContent((on ? "−  " : "+  ") + name, "Abrir/cerrar "+name.ToLowerInvariant()),currentButton, GUILayout.Height(34))!=on)
            {
                if (on) openGroups.Remove(name); else openGroups.Add(name);
                on = !on;
            }
            return on;
        }

        void LayerToggle(string title, params string[] keys)
        {
            bool was = keys.Length > 0 && typeVisible.TryGetValue(keys[0], out var first) && first;
            bool available=false;
            foreach(string key in keys)if(byType.ContainsKey(key)&&byType[key].Count>0)available=true;
            bool enabled=GUI.enabled;GUI.enabled=enabled&&available;
            bool now = VisualToggle(was,title,available?HelpForControl(title):"NO DATA: esta capa no existe en el dataset cargado. No se usa el histórico como reemplazo.");
            GUI.enabled=enabled;
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
                GUILayout.Label("EDIFICIOS Y PISOS", currentHeading);
                foreach (string key in new List<string>(buildingVisible.Keys))
                {
                    bool on = VisualToggle(buildingVisible[key], key == "EDIFICIO_1" ? "Edificio 1" : "Edificio 2","Mostrar u ocultar esta ala; no cambia el modelo ni su FE.");
                    if (on != buildingVisible[key]) { buildingVisible[key]=on; ReapplyAll(); }
                }
                foreach (string floor in new[] { "S1", "P1", "P2", "P3", "P4" })
                {
                    GUILayout.BeginHorizontal();
                    bool was = floorVisible.TryGetValue(floor, out var fv) && fv;
                    bool now = VisualToggle(was, FloorFriendly(floor),"Visibilidad del piso; no activa ni excluye elementos del cálculo.");
                    if (was != now) { floorVisible[floor]=now; ReapplyAll(); }
                    if (GUILayout.Button("Solo", currentButton, GUILayout.Width(54)))
                    { foreach (string f in new List<string>(floorVisible.Keys)) floorVisible[f]=f==floor; ReapplyAll(); }
                    GUILayout.EndHorizontal();
                }
                if (GUILayout.Button("Todos los pisos", currentButton)) { foreach (string f in new List<string>(floorVisible.Keys)) floorVisible[f]=true; ReapplyAll(); }
                GUILayout.Space(6); GUILayout.Label("ELEMENTOS",currentHeading);
                LayerToggle("Columnas", "column"); LayerToggle("Vigas", "beam"); LayerToggle("Muros", "wall");
                LayerToggle("Nodos", "node");
                LayerToggle("Losas", "slab");
                bool fe = GUILayout.Toggle(diagnosticViewMode==2, "Mostrar malla FE candidata", GUILayout.Height(25));
                if (fe != (diagnosticViewMode==2)) { diagnosticViewMode=fe?2:0; typeVisible["fe_candidate"]=fe; ReapplyAll(); }
                bool axes = GUILayout.Toggle(globalAxesVisible,"Mostrar GLOBAL X/Y/Z",GUILayout.Height(25));
                if (axes != globalAxesVisible) SetGlobalAxesVisible(axes);
                DrawQuickViews();
                GUILayout.Space(5);
                GUILayout.Label("Elemento de demostración", currentHeading);
                if (GUILayout.Button("Seleccionar E1-P2-V-041", currentButton, GUILayout.Height(32)))
                    SelectElementById("E1-P2-V-041", true);
                GUILayout.BeginHorizontal();
                searchText=GUILayout.TextField(searchText,40,GUILayout.Height(27));
                if(GUILayout.Button("Buscar ID",currentButton,GUILayout.Width(72)))DoSearch();
                GUILayout.EndHorizontal();
                if(!string.IsNullOrEmpty(searchResult))GUILayout.Label(searchResult,currentBody);
                if (GUILayout.Button("Restablecer modelo · R",currentButton)) ResetPresentation();
            }
            DrawDeliveryPanels();
            if (Accordion("RESULTADOS"))
            {
                if (currentResultsAvailable) DrawP1L5CurrentResultsControls();
                else
                {
                    GUILayout.Label("SIN RESULTADOS ACTUALES PARA ESTA GEOMETRÍA",currentHeading);
                    GUILayout.Label("Se habilitarán al validar el nuevo modelo FE y su corrida compatible.",currentBody);
                    GUI.enabled=false; GUILayout.Button("Caso · Deformada · N / V / T / M",currentButton); GUI.enabled=true;
                }
            }
            if (Accordion("CARGAS"))
            {
                GUILayout.Label(currentResultsAvailable ? "Cargas CURRENT aplicadas" : "Catálogo auditado · aún no aplicado",currentHeading);
                LayerToggle("Cargas superficiales", "p1l4_load_surface"); LayerToggle("Cargas lineales", "p1l4_load_line");
                if(p1l4LoadCatalog==null)GUILayout.Label(new GUIContent("Zonas/líneas 3D · NO DATA CURRENT", "Los controles heredados no tienen geometría de cargas CURRENT. Consulte Cargas en la ficha; no cargar el catálogo histórico como si fuera actual."),currentBody);
                LayerToggle("Áreas tributarias CURRENT","tributary","tributary_point");
                GUILayout.Label(new GUIContent("Puntuales · pendientes de receptor", "No se dibujan ni aplican en la posición del texto CAD. Revisar las cargas unresolved."),currentBody);
                LayerToggle("Apoyos geométricos", "support");
                GUILayout.Label(new GUIContent(currentResultsAvailable ? "CURRENT · con supuestos documentados" : "Pendiente de base FE actual", "G/Q y zonas provienen del contrato CURRENT; PP.LOSA conserva espesor académico de 0,15 m. Las cargas unresolved se excluyen, no equivalen a cero confirmado."),currentBody);
            }
            if (Accordion("ANÁLISIS"))
            {
                GUILayout.Label(currentResultsAvailable ? "OpenSees CURRENT · PASS\nG / Q / EX / EY\nSuperposición lineal instantánea" : "Resultados CURRENT bloqueados · consultar estado de reanálisis",currentBody);
                DrawP1L5ModificationControls(null);
                GUILayout.Label(new GUIContent("Modelo académico · ver trazabilidad", "Materiales inferidos y cargas excluidas están documentados en las fuentes CURRENT. No es un modelo de diseño certificado."),currentBody);
            }
            if (Accordion("CAPACIDAD"))
            {
                if (currentResultsAvailable) DrawStructuralFailureGlobalPanel();
                else GUILayout.Label("P–M representa resistencia de una sección. La demanda actual estará disponible después de la nueva corrida. Los estudios anteriores están en Avanzado → Histórico.",currentBody);
            }
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
                DrawVisualTerrainControls();
                LayerToggle("Contexto físico · solo visual","physical_context");
                if (contextVisible.Count==0)
                    foreach(var item in allElements) if(!string.IsNullOrEmpty(item.physicalCluster)) contextVisible[item.physicalCluster]=true;
                foreach(string cluster in new List<string>(contextVisible.Keys))
                {
                    string friendly=cluster.Contains("STAIR_ACCESS_B")?"Escalera y acceso B":cluster.Contains("STAIR_ACCESS_D")?"Escalera y acceso D":cluster.Contains("CORE")?"Núcleo de ascensores":cluster.Replace('_',' ');
                    bool next=GUILayout.Toggle(contextVisible[cluster],friendly,GUILayout.Height(25));
                    if(next!=contextVisible[cluster]){contextVisible[cluster]=next;ReapplyAll();}
                }
                GUILayout.Label("Escaleras y accesos: contexto. Terreno nuevo esquemático, sin participación FE; no representa una topografía medida.",currentBody);
                if(GUILayout.Button("Inspeccionar núcleo · Piso 4",currentButton))
                {var core=allElements.Find(e=>e!=null&&e.humanId=="E1-P4-M-007");if(core!=null)Select(core);}
            }
            if (!presentationMode && Accordion("AVANZADO"))
            {
                labelsVisible=GUILayout.Toggle(labelsVisible,"IDs técnicos",GUILayout.Height(25));
                LayerToggle("Referencia arquitectónica P4 histórica","architectural_slab", "architectural_slab_edge"); LayerToggle("Nodos geométricos","node");
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
            string[] names={"OFF","My","Mz","N","Vy","Vz","T"};
            for(int i=0;i<names.Length;i++)if(GUILayout.Button(names[i]))SetDiagramMode(i);
            GUILayout.EndHorizontal();
            bool plot2d=GUILayout.Toggle(diagram2DVisible,currentResultsAvailable?"Gráfico 2D CURRENT":"Gráfico 2D histórico",GUILayout.Height(25));
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

        void SelectElementById(string id, bool focus)
        {
            var hit=allElements.Find(e=>e!=null&&e.go!=null&&
                string.Equals(e.humanId??e.id,id,StringComparison.OrdinalIgnoreCase));
            if(hit==null){searchResult="Sin resultado: "+id;return;}
            isolateSelected=false;
            if(buildingVisible.ContainsKey(hit.building))buildingVisible[hit.building]=true;
            if(floorVisible.ContainsKey(hit.floor))floorVisible[hit.floor]=true;
            if(typeVisible.ContainsKey(hit.category))typeVisible[hit.category]=true;
            ReapplyAll();
            Select(hit);
            searchResult="Encontrado CURRENT: "+id;
            if(focus)
            {
                Vector3 c=(hit.nodeI+hit.nodeJ)*0.5f;
                if(c==Vector3.zero)c=hit.coordCenter;
                orbitTarget=transform.TransformPoint(c);
                // Approach from the facade at a useful framing distance: the
                // top slab otherwise fills the camera when focusing a P2 beam.
                pitch=8f;
                orbitDist=Mathf.Clamp(60f,minZoom,maxZoom);
            }
        }

        void DrawUsageHelp()
        {
            GUILayout.Label("1. Selecciona edificio y piso.\n2. Haz clic en un elemento.\n3. Lee su resumen y fuente.\n4. Abre Detalle técnico si lo necesitas.\n5. Los resultados se habilitarán tras una corrida compatible.\n6. Usa XYZ y las vistas rápidas para orientarte.",currentBody);
            GUILayout.Label("Arrastrar: orbitar · Rueda: zoom\nBotón central: desplazar\nR: restablecer · H: solo modelo\nF11: presentación\nGLOBAL Z es vertical; x/y/z locales pertenecen al elemento.",currentBody);
        }

        public void RunCurrentUiSelfCheck()
        {
            var errors=new List<string>();
            if(historicalResultsEnabled)errors.Add("historico activo por defecto");
            foreach(var pair in byType)if(IsHistoricalLayer(pair.Key))foreach(var go in pair.Value)if(go!=null&&go.activeSelf){errors.Add("capa historica visible: "+pair.Key);break;}
            if(model?.solids==null||model.solids.Count==0)errors.Add("modelo actual ausente");
            if(!currentResultsAvailable&&(diagram2DVisible||demandCapacityPlotVisible||activeDeformationVisible))errors.Add("resultado visible sin corrida actual");
            Debug.Log((errors.Count==0?(currentResultsAvailable?"[CURRENT UI QA] PASS: modelo actual; histórico apagado; resultados CURRENT disponibles.":"[CURRENT UI QA] PASS: modelo actual; historico apagado; resultados actuales NONE; FE NOT RUN."):"[CURRENT UI QA] FAIL: "+string.Join(", ",errors)));
        }
    }
}
