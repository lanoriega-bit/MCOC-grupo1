using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    [Serializable] public class CurrentElementContext
    {
        public string element_id, connection_status, load_status, special_role;
        public List<string> candidate_neighbors;
    }
    [Serializable] public class CurrentInspectorContext
    {
        public string geometry_version;
        public List<CurrentElementContext> elements;
    }
    public partial class ViewerController
    {
        readonly HashSet<string> inspectorGroups = new HashSet<string>{"RESUMEN","RESULTADOS"};
        string inspectorSelection;
        Dictionary<string,CurrentElementContext> currentContexts;

        bool InspectorSection(string title)
        {
            bool open=inspectorGroups.Contains(title);
            if(GUILayout.Button((open?"−  ":"+  ")+title,currentButton))
            {if(open)inspectorGroups.Remove(title);else inspectorGroups.Add(title);open=!open;}
            return open;
        }
        void ResetInspectorSections(ElementInfo e)
        {
            inspectorSelection=e?.humanId??e?.id;
            inspectorGroups.Clear();inspectorGroups.Add("RESUMEN");inspectorGroups.Add("RESULTADOS");
            technicalDetail=false;currentInspectorScroll=Vector2.zero;
        }
        CurrentElementContext ElementContext(string id)
        {
            if(currentContexts==null)
            {
                currentContexts=new Dictionary<string,CurrentElementContext>();
                string path=Path.Combine(Application.streamingAssetsPath,"current_inspector_context.json");
                if(File.Exists(path))try
                {
                    var data=JsonUtility.FromJson<CurrentInspectorContext>(File.ReadAllText(path));
                    LoadProjectState();
                    if(data==null||projectState==null||data.geometry_version!=projectState.geometry_sha256)return null;
                    if(data?.elements!=null)foreach(var row in data.elements)currentContexts[row.element_id]=row;
                }
                catch(Exception ex){Debug.LogWarning("Inspector context unavailable: "+ex.Message);}
            }
            return id!=null&&currentContexts.TryGetValue(id,out var context)?context:null;
        }
        string CurrentSectionText(SolidData s)
        {
            if(s==null)return "Dimensiones no disponibles";
            if(s.category=="wall")return $"Espesor: {s.width_m*100:F1} cm · largo {s.length_m:F2} m";
            if(s.category=="slab")return "Superficie visual provisional; perímetro y huecos por revisar";
            double h=s.category=="column"?s.section_depth_m:s.section_height_m;
            return (s.section_width_m>0&&h>0?$"Sección: {s.section_width_m*100:F0} × {h*100:F0} cm":"Sección resistente: por confirmar")+
                (s.category=="column"?$" · altura {s.height_m:F2} m":$" · largo {s.length_m:F2} m");
        }
        string CurrentMaterialText(SolidData s)
        {
            if(s==null||string.IsNullOrEmpty(s.material)||s.material=="UNKNOWN")return "Material: por confirmar";
            if(s.material=="M.H.A.")return "Hormigón armado · grado por confirmar";
            return "Hormigón "+s.material.Replace("_10","")+(string.IsNullOrEmpty(s.reinforcement_grade)?"":" · Acero "+s.reinforcement_grade);
        }
        string CurrentMaterialStatus(SolidData s)
        {
            if(s==null||s.concrete_fc_pa<=0)return "Grado resistente: POR CONFIRMAR";
            return "Material: "+ConfidenceFriendly(s.material_confidence);
        }
        static string StructuralRole(ElementInfo e,CurrentElementContext context)
        {
            if(!string.IsNullOrEmpty(context?.special_role))return context.special_role;
            if(e.category=="beam")return "Elemento horizontal que transmite cargas hacia sus apoyos; receptores efectivos por validar.";
            if(e.category=="column")return "Elemento vertical que transmite cargas hacia niveles inferiores.";
            if(e.category=="wall")return "Muro estructural: aporta rigidez y resistencia vertical/lateral. Su idealización de análisis requiere validación.";
            if(e.category=="slab")return "Referencia visual del piso. No es una placa FE ni un perímetro de carga aprobado.";
            return "Elemento de referencia; participación estructural según fuente y revisión.";
        }
        void DrawStructuralInspector()
        {
            var e=lastSelected;if(e==null)return;
            string id=e.humanId??e.id;
            if(inspectorSelection!=id)ResetInspectorSections(e);
            var s=CurrentSolid(e);var context=ElementContext(id);
            Rect r=CurrentInspectorRect();PanelBackground(r);
            GUILayout.BeginArea(new Rect(r.x+10,r.y+8,r.width-20,r.height-16));
            GUILayout.BeginHorizontal();GUILayout.Label("FICHA ESTRUCTURAL",currentHeading);
            if(GUILayout.Button("×",currentButton,GUILayout.Width(30)))inspectorVisible=false;
            GUILayout.EndHorizontal();
            currentInspectorScroll=GUILayout.BeginScrollView(currentInspectorScroll);
            DrawPendingPlanCard(id);
            if(InspectorSection("RESUMEN"))
            {
                GUILayout.Label(TypeFriendly(e.category).ToUpperInvariant()+" · "+id,currentHeading);
                GUILayout.Label((e.building??"Sin edificio").Replace("EDIFICIO_","Edificio ")+" · "+FloorFriendly(e.floor),currentBody);
                GUILayout.Label(CurrentSectionText(s),currentBody);
                GUILayout.Label(CurrentMaterialText(s),currentBody);
                GUILayout.Label(StructuralRole(e,context),currentBody);
                GUILayout.Label("Geometría: "+ConfidenceFriendly(s?.confidence??e.confidence),currentBody);
                if(s!=null&&s.category!="slab")GUILayout.Label(CurrentMaterialStatus(s),currentBody);
            }
            if(InspectorSection("PROPIEDADES"))
            {
                GUILayout.Label(CurrentSectionText(s),currentBody);
                if(s!=null)
                {
                    GUILayout.Label("Sección: "+ConfidenceFriendly(s.section_confidence),currentBody);
                    if(s.concrete_fc_pa>0)GUILayout.Label($"f'c de plano: {s.concrete_fc_pa/1e6:F0} MPa",currentBody);
                    if(s.reinforcement_fy_pa>0)GUILayout.Label($"fy de acero: {s.reinforcement_fy_pa/1e6:F0} MPa",currentBody);
                    GUILayout.Label("Grado de material ≠ módulo elástico ni disposición de armaduras. No usar tamaño visual como sección resistente confirmada.",currentBody);
                }
            }
            if(InspectorSection("CONEXIONES"))
            {
                GUILayout.Label(context?.connection_status??"Conectividad efectiva por validar; no inferir receptor por proximidad.",currentBody);
                if(context?.candidate_neighbors!=null&&context.candidate_neighbors.Count>0)
                {GUILayout.Label("Incidencias propuestas, no apoyos confirmados:",currentBody);foreach(string neighbor in context.candidate_neighbors)GUILayout.Label(neighbor,currentBody);}
            }
            if(InspectorSection("RESULTADOS"))
            {
                GUILayout.Label("RESULTADOS ACTUALES",currentHeading);
                GUILayout.Label(currentResultsAvailable ? BuildP1L4ResultsText(e,id) : "No disponibles todavía.\nLa estructura fue actualizada después de la última corrida OpenSees.\nSe requiere un nuevo análisis validado.",currentBody);
            }
            if(InspectorSection("CARGAS"))
                GUILayout.Label(context?.load_status??"Asignación actual no aprobada. No hay carga cero confirmada: faltan áreas/receptores o validación del catálogo.",currentBody);
            if(InspectorSection("EJES"))
            {
                bool show=GUILayout.Toggle(localAxesVisible,"Mostrar flechas x / y / z",GUILayout.Height(27));
                if(show!=localAxesVisible){localAxesVisible=show;RebuildCurrentLocalAxes();}
                GUILayout.Label("x = longitudinal del elemento\ny / z = transversales locales\nN → dirección x\nT → alrededor de x\nVy → dirección y · Vz → dirección z\nMy → alrededor de y · Mz → alrededor de z",currentBody);
                GUILayout.Label(e.category=="wall"?"En este muro, x geométrico recorre su longitud en planta. No equivale al eje de la barra FE vertical.":"Triada geométrica actual. La corrida deberá exportar y verificar sus propios ejes FE.",currentBody);
            }
            if(InspectorSection("CAPACIDAD"))
                GUILayout.Label(currentResultsAvailable ? BuildDemandCapacityText(id) : "Demanda actual no disponible. La capacidad requiere sección, material y armadura compatibles. Cambiar la combinación mueve la demanda; cambiar sección/material obliga a revisar también la capacidad.",currentBody);
            if(InspectorSection("FUENTE / CONFIANZA"))
            {
                GUILayout.Label("Geometría: "+e.sourceDxf+"\nConfianza: "+ConfidenceFriendly(e.confidence),currentBody);
                if(s!=null)GUILayout.Label("Material: "+(s.material_source??"Por confirmar")+"\n"+ConfidenceFriendly(s.material_confidence),currentBody);
            }
            technicalDetail=InspectorSection("DETALLE TÉCNICO");
            if(technicalDetail)
            {
                GUILayout.Label($"ID: {id}\ngeometry_elementTag: {e.elementTag}\nEjes CAD: {e.axisX} / {e.axisY}\nExtremo i [m]: {P(e.nodeI)}\nExtremo j [m]: {P(e.nodeJ)}\nLayer: {e.sourceLayer}",currentBody);
                if(e.crosswalk!=null)foreach(var x in e.crosswalk)GUILayout.Label($"FE PROPUESTO · NO EJECUTADO\n{x.analysis_id} · tag {x.opensees_element_tag}\nNodos {x.opensees_node_i}–{x.opensees_node_j}",currentBody);
                GUILayout.Label("N/Vy/Vz [N], T/My/Mz [N·m], desplazamientos [m]: sin valores i/j actuales. Ejes geométricos no sustituyen vectores FE.",currentBody);
                if(!string.IsNullOrEmpty(e.correctionType))GUILayout.Label($"Auditoría: {e.correctionType}\n{e.correctionReason}\n{e.correctionPrimarySource}\n{e.correctionExternalClue}",currentBody);
                if(s?.property_correction!=null)GUILayout.Label(s.material_scope_note,currentBody);
                GUILayout.Label(CurrentVersionDiagnostic(),currentBody);
            }
            if(InspectorSection("MODIFICACIONES · P1L5"))
            {
                if(currentResultsAvailable)DrawP1L5ModificationControls(e);
                else GUILayout.Label("Carga · sección: disponibles después de una base CURRENT.",currentBody);
            }
            GUILayout.EndScrollView();GUILayout.EndArea();
        }
    }
}
