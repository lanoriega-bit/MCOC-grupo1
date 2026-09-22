using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    [Serializable] public class DeliverySummary
    {
        public string id,title,tag,commit,objective,original_status,current_status,changes,qa,statistics,model_path,source_path,url,unknown_metrics;
    }
    [Serializable] public class ProjectStateData
    {
        public string format,geometry,properties,fe,results,unity,geometry_sha256,fe_sha256,geometry_path,fe_path,baseline_status;
        public int pending,floating_components,geometry_count,fe_members,beam_heights_pending;
        public List<string> blockers;
        public List<DeliverySummary> deliveries;
    }
    public partial class ViewerController
    {
        private ProjectStateData projectState;
        private bool projectStateLoaded;
        private string historicalDelivery="P1L4 / fuente P1L3";

        void LoadProjectState()
        {
            if(projectStateLoaded)return;
            projectStateLoaded=true;
            try
            {
                var path=Path.Combine(Application.streamingAssetsPath,"project_state.json");
                if(File.Exists(path))projectState=JsonUtility.FromJson<ProjectStateData>(File.ReadAllText(path));
            }
            catch(Exception e){Debug.LogWarning("Project metadata unavailable: "+e.Message);}
        }

        string CurrentStatusLine()
        {
            LoadProjectState();
            if(projectState==null)return "ESTADO: metadata no disponible; no habilitar resultados actuales";
            return $"GEOMETRÍA: {projectState.geometry} | FE: {projectState.fe} | RESULTADOS: "+
                (ResultsAllowed?"HISTORICAL · "+historicalDelivery:projectState.results);
        }

        void DrawDeliveryPanels()
        {
            LoadProjectState();
            if(Accordion("ESTADO DEL PROYECTO"))
            {
                if(projectState==null)GUILayout.Label("Metadata no disponible",currentBody);
                else
                {
                    GUILayout.Label($"Geometría: {projectState.geometry}\nSólidos: {projectState.geometry_count}\nPropiedades: {projectState.properties}\nFE: {projectState.fe}\nMiembros: {projectState.fe_members}\nResultados: {projectState.results}\nUnity: {projectState.unity}\nPendientes FE: {projectState.pending}\nComponentes flotantes: {projectState.floating_components}\nPRE-P1L5: {projectState.baseline_status}",currentBody);
                    if(projectState.blockers!=null)foreach(var note in projectState.blockers)GUILayout.Label("• "+note,currentBody);
                }
            }
            if(!Accordion("ENTREGAS"))return;
            GUILayout.Label("Historia entregada ≠ modelo actual. Abrir un resumen no cambia la geometría ni activa resultados.",currentBody);
            if(projectState?.deliveries==null){GUILayout.Label("Sin catálogo de entregas",currentBody);return;}
            foreach(var delivery in projectState.deliveries)
            {
                if(!Accordion(delivery.title))continue;
                GUILayout.Label(delivery.objective,currentBody);
                GUILayout.Label("ESTADO ORIGINAL",currentHeading);GUILayout.Label(delivery.original_status,currentBody);
                GUILayout.Label(delivery.statistics,currentBody);
                if(!string.IsNullOrEmpty(delivery.tag))GUILayout.Label("Tag: "+delivery.tag+"\nCommit: "+delivery.commit,currentBody);
                GUILayout.Label("ACTUAL CORREGIDO",currentHeading);GUILayout.Label(delivery.current_status,currentBody);
                GUILayout.Label("Cambios posteriores: "+delivery.changes,currentBody);
                GUILayout.Label("QA: "+delivery.qa,currentBody);
                GUILayout.Label("Modelo: "+delivery.model_path+"\nFuente: "+delivery.source_path,currentBody);
                if(GUILayout.Button("Abrir informe de "+delivery.id,currentButton))Application.OpenURL(delivery.url);
                if((delivery.id=="P1L3"||delivery.id=="P1L4")&&!presentationMode)
                {
                    GUILayout.Label("RESULTADO HISTÓRICO "+delivery.id+"\nNO CORRESPONDE A LA GEOMETRÍA POST-P1L4 ACTUAL",currentHeading);
                    if(GUILayout.Button("Abrir histórico explícitamente",currentButton))
                    {historicalDelivery=delivery.id;SetHistoricalResults(true);}
                    if(ResultsAllowed&&historicalDelivery==delivery.id)
                    {
                        DrawHistoricalControls();
                        if(GUILayout.Button("Cerrar histórico",currentButton))SetHistoricalResults(false);
                    }
                }
            }
            if(Accordion("EVOLUCIÓN · ANTES / AHORA"))
            {
                foreach(var delivery in projectState.deliveries)
                {GUILayout.Label(delivery.title,currentHeading);GUILayout.Label(delivery.statistics+"\n"+delivery.changes+"\n"+delivery.unknown_metrics,currentBody);}
                GUILayout.Label("Las categorías y discretizaciones cambiaron: menos prismas no significa menor estructura. Los conteos provienen de cada snapshot Git, no de cuatro modelos cargados.",currentBody);
            }
        }
    }
}
