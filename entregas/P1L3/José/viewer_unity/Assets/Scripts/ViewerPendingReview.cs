using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    [Serializable] public class PendingReviewRow
    {
        public string id,label,building,floor,priority,axes,problem,plan,question;
        public List<string> neighbors;
        public float level_z;
    }
    [Serializable] public class PendingGridAxis { public string building,direction,name; public float coordinate; }
    [Serializable] public class PendingReviewData { public string geometry_version; public List<PendingReviewRow> rows; public List<PendingGridAxis> axes; }
    public partial class ViewerController
    {
        PendingReviewData pendingReviewData;
        PendingReviewRow pendingReviewRow;
        readonly HashSet<string> pendingReviewIds=new HashSet<string>();
        readonly List<GameObject> pendingGridObjects=new List<GameObject>();
        readonly List<KeyValuePair<Vector3,string>> pendingGridLabels=new List<KeyValuePair<Vector3,string>>();
        bool pendingReviewExpanded,pendingGridVisible=true;
        Vector2 pendingListScroll;
        string pendingReviewError;

        void LoadPendingReview()
        {
            if(pendingReviewData!=null||pendingReviewError!=null)return;
            try
            {
                var data=JsonUtility.FromJson<PendingReviewData>(File.ReadAllText(Path.Combine(Application.streamingAssetsPath,"fe_pending_review.json")));
                LoadProjectState();
                if(data==null||projectState==null||data.geometry_version!=projectState.geometry_sha256)throw new Exception("Expediente de otra geometría; regenerar antes de revisar.");
                pendingReviewData=data;
            }
            catch(Exception ex){pendingReviewError=ex.Message;Debug.LogWarning("Pending review: "+ex.Message);}
        }
        public void OpenPendingReviewFirst()
        {
            LoadPendingReview();
            if(pendingReviewData?.rows?.Count>0)SelectPendingReview(pendingReviewData.rows[0]);
        }
        void ExitPendingReview()
        {
            pendingReviewRow=null;pendingReviewIds.Clear();
            foreach(var go in pendingGridObjects)if(go!=null)Destroy(go);
            pendingGridObjects.Clear();pendingGridLabels.Clear();
        }
        void SelectPendingReview(PendingReviewRow row)
        {
            ResetPresentation();presentationMode=false;navigationExpanded=true;
            openGroups.Clear();openGroups.Add("DIAGNÓSTICO");pendingReviewExpanded=true;
            pendingReviewRow=row;pendingGridVisible=true;
            foreach(string id in row.neighbors)pendingReviewIds.Add(id);
            pendingReviewIds.Add(row.id);ReapplyAll();
            var selected=allElements.Find(e=>e!=null&&!e.isFeCandidateVisual&&e.humanId==row.id);
            if(selected==null)return;
            Select(selected);localAxesVisible=false;ClearSelectedLocalAxes();inspectorVisible=true;ResetInspectorSections(selected);inspectorGroups.Clear();
            FitCurrentModel();orbitDist=Mathf.Max(25,orbitDist);yaw=30;pitch=55;velYaw=velPitch=0;
            BuildPendingGrid();
        }
        void DrawPendingReviewControls()
        {
            LoadPendingReview();
            if(GUILayout.Button((pendingReviewExpanded?"− ":"+ ")+"Pendientes FE",currentButton))pendingReviewExpanded=!pendingReviewExpanded;
            if(!pendingReviewExpanded)return;
            if(pendingReviewData==null){GUILayout.Label(pendingReviewError??"Expediente no disponible",currentBody);return;}
            GUILayout.Label(pendingReviewData.rows.Count+" casos · diagnóstico sin correcciones",currentBody);
            bool grid=GUILayout.Toggle(pendingGridVisible,"Ejes estructurales del plano",GUILayout.Height(25));
            if(grid!=pendingGridVisible){pendingGridVisible=grid;foreach(var go in pendingGridObjects)go.SetActive(grid);}
            if(pendingReviewRow!=null&&GUILayout.Button("Salir del aislamiento · R",currentButton))ResetPresentation();
            pendingListScroll=GUILayout.BeginScrollView(pendingListScroll,GUILayout.Height(210));
            foreach(var row in pendingReviewData.rows)
            {
                string text=(pendingReviewRow==row?"▶ ":"")+row.label+" · "+row.id+" · "+row.priority;
                if(GUILayout.Button(text,currentButton,GUILayout.Height(32)))SelectPendingReview(row);
            }
            GUILayout.EndScrollView();
        }
        void DrawPendingPlanCard(string selectedId)
        {
            if(pendingReviewRow==null||pendingReviewRow.id!=selectedId)return;
            var r=pendingReviewRow;
            GUILayout.Label("REVISIÓN DE PLANO · "+r.label,currentHeading);
            GUILayout.Label(r.id+" · Prioridad "+r.priority,currentHeading);
            GUILayout.Label("EJES: "+r.axes,currentBody);
            GUILayout.Label("PROBLEMA: "+r.problem,currentBody);
            GUILayout.Label("REVISAR: "+r.plan,currentBody);
            GUILayout.Label("BUSCAR / RESPONDER: "+r.question,currentBody);
            GUILayout.Label("Vecinos visibles ≠ conexiones confirmadas. Candidato no ejecutado. No se aplican correcciones.",currentBody);
            GUILayout.Space(8);
        }
        void BuildPendingGrid()
        {
            if(pendingReviewRow==null)return;
            float minX=float.MaxValue,minY=float.MaxValue,maxX=float.MinValue,maxY=float.MinValue;
            foreach(var e in allElements)
            {
                if(e==null||!pendingReviewIds.Contains(e.humanId??"")||e.isFeCandidateVisual)continue;
                var s=CurrentSolid(e);if(s==null)continue;
                foreach(var p in new[]{s.start,s.end,s.center})if(p!=null&&p.Count>=3)
                {minX=Mathf.Min(minX,(float)p[0]);maxX=Mathf.Max(maxX,(float)p[0]);minY=Mathf.Min(minY,(float)p[1]);maxY=Mathf.Max(maxY,(float)p[1]);}
            }
            if(minX==float.MaxValue)return;
            minX-=2;maxX+=2;minY-=2;maxY+=2;
            // Include nearest grid outside the region, needed for outboard elements.
            var keep=new List<PendingGridAxis>();
            foreach(string d in new[]{"X","Y"})
            {
                var candidates=pendingReviewData.axes.FindAll(a=>a.building==pendingReviewRow.building&&a.direction==d);
                var selectedSolid=CurrentSolid(lastSelected);
                Vector3 selectedCenter=selectedSolid.center!=null&&selectedSolid.center.Count>=3?V(selectedSolid.center):(V(selectedSolid.start)+V(selectedSolid.end))*.5f;
                float mid=d=="X"?selectedCenter.x:selectedCenter.y;
                candidates.Sort((a,b)=>Mathf.Abs(a.coordinate-mid).CompareTo(Mathf.Abs(b.coordinate-mid)));
                for(int i=0;i<Mathf.Min(2,candidates.Count);i++)keep.Add(candidates[i]);
            }
            foreach(var a in keep){if(a.direction=="X"){minX=Mathf.Min(minX,a.coordinate-1);maxX=Mathf.Max(maxX,a.coordinate+1);}else{minY=Mathf.Min(minY,a.coordinate-1);maxY=Mathf.Max(maxY,a.coordinate+1);}}
            foreach(var a in keep)
            {
                float z=pendingReviewRow.level_z+.06f;
                Vector3 from=a.direction=="X"?new Vector3(a.coordinate,minY,z):new Vector3(minX,a.coordinate,z);
                Vector3 to=a.direction=="X"?new Vector3(a.coordinate,maxY,z):new Vector3(maxX,a.coordinate,z);
                var go=new GameObject("PLAN_AXIS_"+a.building+"_"+a.name);go.transform.SetParent(transform,false);
                var lr=go.AddComponent<LineRenderer>();lr.useWorldSpace=false;lr.positionCount=2;lr.SetPositions(new[]{from,to});
                lr.startWidth=lr.endWidth=.035f;lr.material=SeismicLineMat(new Color(.2f,.8f,1));pendingGridObjects.Add(go);
                pendingGridLabels.Add(new KeyValuePair<Vector3,string>(from,a.name));
            }
        }
        void DrawPendingGridLabels()
        {
            if(pendingReviewRow==null||!pendingGridVisible||cam==null)return;
            var occupied=new List<Rect>();
            float left=navigationExpanded?SemanticPanelRect().xMax+8:12;
            float right=inspectorVisible?CurrentInspectorRect().x-8:Screen.width-12;
            foreach(var item in pendingGridLabels)
            {
                Vector3 p=cam.WorldToScreenPoint(transform.TransformPoint(item.Key));if(p.z<=0)continue;
                Rect r=new Rect(Mathf.Clamp(p.x+6,left,right-85),Mathf.Clamp(Screen.height-p.y-12,90,Screen.height-190),85,24);
                for(int tries=0;tries<8&&occupied.Exists(o=>o.Overlaps(r));tries++)r.y+=r.y<Screen.height-220?25:-50;
                occupied.Add(r);PanelBackground(r);
                Color old=GUI.color;GUI.color=new Color(.35f,.9f,1);GUI.Label(r,"EJE "+item.Value,currentHeading);GUI.color=old;
            }
        }
    }
}
