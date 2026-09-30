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
        Dictionary<string,CurrentElementLoadData> currentElementLoads;
        Dictionary<string,CurrentMaterialData> currentMaterials;
        Dictionary<string,CurrentMemberIdentity> currentMemberIdentities;

        CurrentMemberIdentity CurrentMember(string id)
        {
            if(currentMemberIdentities==null)
            {
                currentMemberIdentities=new Dictionary<string,CurrentMemberIdentity>();
                var data=JsonLoader.LoadP1L6CurrentMemberIdentity();
                if(data?.members!=null)foreach(var row in data.members)
                    if(row!=null&&!string.IsNullOrEmpty(row.element_id))currentMemberIdentities[row.element_id]=row;
            }
            return id!=null&&currentMemberIdentities.TryGetValue(id,out var rowIdentity)?rowIdentity:null;
        }

        CurrentMaterialData CurrentMaterial(string materialId)
        {
            if(currentMaterials==null)
            {
                currentMaterials=new Dictionary<string,CurrentMaterialData>();
                var data=JsonLoader.LoadP1L6CurrentMaterials();
                if(data?.materials!=null)foreach(var row in data.materials)
                    if(row!=null&&!string.IsNullOrEmpty(row.material_id))currentMaterials[row.material_id]=row;
            }
            return materialId!=null&&currentMaterials.TryGetValue(materialId,out var material)?material:null;
        }

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
        CurrentElementLoadData CurrentElementLoad(string id)
        {
            if(currentElementLoads==null)
            {
                currentElementLoads=new Dictionary<string,CurrentElementLoadData>();
                var data=JsonLoader.LoadP1L5CurrentElementLoads();
                if(data?.elements!=null)foreach(var row in data.elements)
                    if(row!=null&&!string.IsNullOrEmpty(row.element_id))currentElementLoads[row.element_id]=row;
            }
            return id!=null&&currentElementLoads.TryGetValue(id,out var load)?load:null;
        }
        string CurrentElementLoadText(string id,CurrentElementContext context)
        {
            if(!currentResultsAvailable)return context?.load_status??"NO DATA CURRENT: falta una base de cargas compatible.";
            var row=CurrentElementLoad(id);
            if(row==null)return "NO DATA: este elemento no tiene un registro en el contrato de cargas CURRENT. No se interpreta como carga cero.";
            var lines=new List<string>();
            if(row.Q!=null&&row.Q.status!="NO_DATA")
            {
                lines.Add($"Q · {row.Q.status}");
                lines.Add($"Área tributaria: {row.Q.tributary_area_m2:F3} m² · ancho equivalente: {row.Q.equivalent_width_m:F3} m");
                lines.Add($"qQ medio: {row.Q.average_surface_intensity_kN_m2:F3} kN/m² · wQ: {row.Q.equivalent_line_load_N_m/1000.0:F3} kN/m");
                lines.Add($"Q transferida: {row.Q.surface_force_N/1000.0:F3} kN");
                if(row.Q.zone_ids!=null&&row.Q.zone_ids.Count>0)lines.Add("Zonas: "+string.Join(", ",row.Q.zone_ids));
            }
            else lines.Add("Q: NO DATA para este elemento; no equivale a una carga cero confirmada.");
            if(row.G!=null)
            {
                lines.Add($"G · {row.G.status}");
                lines.Add($"Peso propio: {row.G.self_weight_N/1000.0:F3} kN · carga muerta tributaria: {row.G.tributary_dead_N/1000.0:F3} kN");
                lines.Add($"G asociada total: {row.G.total_associated_N/1000.0:F3} kN");
                if(row.Q!=null&&row.Q.tributary_area_m2>0)
                    lines.Add($"qG tributario medio: {row.G.tributary_dead_N/1000.0/row.Q.tributary_area_m2:F3} kN/m²");
                double length=lastSelected!=null?lastSelected.lengthM:0;
                if(length>0)
                    lines.Add($"wG equivalente: total {row.G.total_associated_N/1000.0/length:F3} kN/m · peso propio {row.G.self_weight_N/1000.0/length:F3} kN/m · adicional {row.G.tributary_dead_N/1000.0/length:F3} kN/m");
            }
            if(row.source_load_ids!=null&&row.source_load_ids.Count>0)
            {
                lines.Add("Fuentes: "+string.Join(", ",row.source_load_ids));
                bool point=row.source_load_ids.Exists(x=>(x??"").Contains("POINT"));
                bool line=row.source_load_ids.Exists(x=>(x??"").Contains("LINE"));
                lines.Add("Cargas puntuales asociadas: "+(point?"ver IDs fuente":"NO DATA / ninguna en el contrato del elemento"));
                lines.Add("Cargas lineales especiales asociadas: "+(line?"ver IDs fuente":"NO DATA / ninguna en el contrato del elemento"));
            }
            return string.Join("\n",lines);
        }
        string CurrentSectionText(SolidData s)
        {
            if(s==null)return "Dimensiones no disponibles";
            if(s.category=="wall")return $"Espesor: {s.width_m*100:F1} cm · largo {s.length_m:F2} m";
            if(s.category=="slab")return "Superficie visual provisional; perímetro y huecos por revisar";
            double b=s.section_width_m>0?s.section_width_m:s.width_m;
            double h=s.category=="column"?(s.section_depth_m>0?s.section_depth_m:s.depth_m):(s.section_height_m>0?s.section_height_m:s.height_m);
            double length=s.length_m>0?s.length_m:(lastSelected!=null?lastSelected.lengthM:0);
            return (b>0&&h>0?$"Sección: {b*100:F0} × {h*100:F0} cm":"Sección resistente: por confirmar")+
                (s.category=="column"?$" · altura {length:F2} m":$" · largo {length:F2} m");
        }
        string CurrentMaterialText(SolidData s)
        {
            if(s==null||string.IsNullOrEmpty(s.material)||s.material=="UNKNOWN")return "Material: por confirmar";
            var material=CurrentMaterial(s.material_id);
            string steel=material?.resistance?.reinforcement_grade?.value;
            if(s.material=="M.H.A.")return "Hormigón armado · grado por confirmar";
            return "Hormigón "+s.material.Replace("_10","")+(string.IsNullOrEmpty(steel)?"":" · Acero "+steel);
        }
        string CurrentMaterialStatus(SolidData s)
        {
            var material=CurrentMaterial(s?.material_id);
            string status=material?.resistance?.concrete_fc_pa?.status;
            return string.IsNullOrEmpty(status)?"Grado resistente: NO DATA":"Material: "+ConfidenceFriendly(status);
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
            var s=CurrentSolid(e);var context=ElementContext(id);var feRows=MetadataForSelection(e,id);
            Rect r=CurrentInspectorRect();PanelBackground(r);
            GUILayout.BeginArea(new Rect(r.x+10,r.y+8,r.width-20,r.height-16));
            GUILayout.BeginHorizontal();GUILayout.Label("FICHA ESTRUCTURAL",currentHeading);
            if(GUILayout.Button("×",currentButton,GUILayout.Width(30)))
            {inspectorVisible=false;if(isolateSelected){isolateSelected=false;ReapplyAll();}}
            GUILayout.EndHorizontal();
            GUILayout.BeginHorizontal();
            if(GUILayout.Button(isolateSelected?"Mostrar edificio":"Aislar elemento",currentButton,GUILayout.Height(28)))
            {
                isolateSelected=!isolateSelected;
                Vector3 c=(e.nodeI+e.nodeJ)*0.5f;
                if(c==Vector3.zero)c=e.coordCenter;
                orbitTarget=transform.TransformPoint(c);
                orbitDist=Mathf.Clamp(isolateSelected?Mathf.Max(12f,(float)e.lengthM*3f):60f,minZoom,maxZoom);
                ReapplyAll();ApplyStructuralFailureVisualization();
            }
            if(GUILayout.Button("Centrar",currentButton,GUILayout.Width(70),GUILayout.Height(28)))
            {Vector3 c=(e.nodeI+e.nodeJ)*0.5f;if(c==Vector3.zero)c=e.coordCenter;orbitTarget=transform.TransformPoint(c);orbitDist=Mathf.Clamp(22f,minZoom,maxZoom);}
            GUILayout.EndHorizontal();
            currentInspectorScroll=GUILayout.BeginScrollView(currentInspectorScroll);
            DrawPendingPlanCard(id);
            if(InspectorSection("RESUMEN"))
            {
                GUILayout.Label(TypeFriendly(e.category).ToUpperInvariant()+" · "+id,currentHeading);
                GUILayout.Label((e.building??"Sin edificio").Replace("EDIFICIO_","Edificio ")+" · "+FloorFriendly(e.floor),currentBody);
                GUILayout.Label($"elementTag: {id}\nsolidTag: {(s?.solidTag??e.elementTag??"NO DATA")}\nOpenSees: {(feRows.Count>0?feRows[0].opensees_tag.ToString():"NO DATA")} · segmentos FE: {feRows.Count}",currentBody);
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
                    var material=CurrentMaterial(s.material_id);
                    GUILayout.Label($"section_id: {s.section_id??"NO DATA"}\nmaterial_id: {s.material_id??"NO DATA"}",currentBody);
                    string sectionStatus=feRows.Count>0&&feRows[0].section!=null?feRows[0].section.source:s.section_confidence;
                    GUILayout.Label("Sección: "+ConfidenceFriendly(sectionStatus),currentBody);
                    if(material?.resistance?.concrete_fc_pa!=null)GUILayout.Label($"f'c: {material.resistance.concrete_fc_pa.value/1e6:F0} MPa · {material.resistance.concrete_fc_pa.status}",currentBody);
                    else GUILayout.Label("f'c: NO DATA",currentBody);
                    if(material?.elastic?.E_pa!=null)GUILayout.Label($"E: {material.elastic.E_pa.value/1e9:F2} GPa · {material.elastic.E_pa.status}",currentBody);
                    else GUILayout.Label("E: NO DATA",currentBody);
                    if(material?.resistance?.reinforcement_fy_pa!=null)GUILayout.Label($"Acero {material.resistance.reinforcement_grade?.value??"NO DATA"} · fy {material.resistance.reinforcement_fy_pa.value/1e6:F0} MPa · {material.resistance.reinforcement_fy_pa.status}",currentBody);
                    else GUILayout.Label("Acero / fy: NO DATA",currentBody);
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
                GUILayout.Label(CurrentElementLoadText(id,context),currentBody);
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
                var member=CurrentMember(id);
                GUILayout.Label($"ID: {id}\nsolidTag: {(s?.solidTag??e.elementTag??"NO DATA")}\nEjes CAD: {e.axisX} / {e.axisY}\nNodos físicos i/j: {member?.physical_node_i??"NO DATA"} / {member?.physical_node_j??"NO DATA"}\nExtremo i [m]: {P(e.nodeI)}\nExtremo j [m]: {P(e.nodeJ)}\nOrientación geométrica: {(e.nodeJ-e.nodeI).normalized}\nLayer: {e.sourceLayer}",currentBody);
                if(s?.merged_from!=null&&s.merged_from.Count>0)GUILayout.Label("merged_from: "+string.Join(", ",s.merged_from),currentBody);
                if(e.crosswalk!=null)foreach(var x in e.crosswalk)GUILayout.Label($"FE {(currentResultsAvailable?"CURRENT":"PROPUESTO · NO EJECUTADO")}\n{x.analysis_id} · tag {x.opensees_element_tag}\nNodos FE {x.opensees_node_i}–{x.opensees_node_j}",currentBody);
                GUILayout.Label("Convención OpenSees local: [N, Vy, Vz, T, My, Mz]. Fuerzas del elemento sobre los nodos i/j; el extremo j se invierte solo al dibujar ambos extremos sobre una cara interna común.",currentBody);
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
