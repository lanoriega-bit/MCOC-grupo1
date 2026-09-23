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
    [Serializable] public class RevisionChange { public string id,type,reason,source; public List<string> historical_ids; public float gap_m; }
    [Serializable] public class RevisionChanges { public string geometry_version,baseline_commit; public List<RevisionChange> rows; }
    [Serializable] public class ColumnStackRow { public string id,building; public List<string> member_ids,floors; public bool confirmed; }
    [Serializable] public class ColumnStackData { public string geometry_version,registration_policy; public List<ColumnStackRow> stacks; }
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
        RevisionChanges revisionChanges;
        bool revisionChangesExpanded;
        string revisionFilter="BEAM_MERGED";
        Vector2 revisionScroll;
        ColumnStackData columnStackData;
        bool columnStacksExpanded,stackReviewActive;
        Vector2 stackScroll;

        void LoadColumnStacks()
        {
            if(columnStackData!=null)return;
            string path=Path.Combine(Application.streamingAssetsPath,"column_vertical_stacks.json");
            if(!File.Exists(path))return;
            LoadProjectState();var data=JsonUtility.FromJson<ColumnStackData>(File.ReadAllText(path));
            if(data?.geometry_version==projectState?.geometry_sha256)columnStackData=data;
        }
        void SelectColumnStack(ColumnStackRow stack)
        {
            LoadPendingReview();
            var first=allElements.Find(e=>e!=null&&!e.isFeCandidateVisual&&stack.member_ids.Contains(e.humanId));
            if(first==null||pendingReviewData==null)return;
            SelectPendingReview(new PendingReviewRow{id=first.humanId,label=stack.id,building=stack.building,floor=first.floor,
                priority=stack.confirmed?"CONFIRMED":"REVIEW_REQUIRED",axes="Ver ejes de planta; referencia XY de stacks: contorno P2",
                problem="COLUMN STACKS · comparación vertical, no resultado resistente",plan="COLUMN_VERTICAL_STACKS.json",
                question="Comparar continuidad S1–P4. Secciones sin modificar. R restaura el edificio.",neighbors=stack.member_ids,level_z=0});
            stackReviewActive=true;columnStacksExpanded=true;pendingReviewExpanded=false;
            SetGlobalAxesVisible(false);
            yaw=0;pitch=12;ReapplyAll();FitCurrentModel();
            // A slender five-floor stack needs vertical margin, not a building
            // width-based fit that can hide its roof behind the top bar.
            orbitDist=Mathf.Max(42f,orbitDist*1.5f);
        }
        void DrawColumnStacks()
        {
            LoadColumnStacks();
            if(GUILayout.Button((columnStacksExpanded?"− ":"+ ")+"COLUMN STACKS · verticalidad",currentButton))columnStacksExpanded=!columnStacksExpanded;
            if(!columnStacksExpanded)return;
            if(columnStackData==null){GUILayout.Label("Stacks no disponibles para esta geometría.",currentBody);return;}
            GUILayout.Label("Aislar una cadena. Pisos en su altura real, misma vista XY. No se superponen datasets históricos.",currentBody);
            if(stackReviewActive)
            {
                GUILayout.BeginHorizontal();
                foreach(string floor in new[]{"S1","P1","P2","P3","P4"})
                {
                    bool visible=floorVisible.ContainsKey(floor)&&floorVisible[floor];
                    bool next=GUILayout.Toggle(visible,floor);if(next!=visible){floorVisible[floor]=next;ReapplyAll();}
                }
                GUILayout.EndHorizontal();
                if(GUILayout.Button("Vista XZ",currentButton)){yaw=0;pitch=0;velYaw=velPitch=0;}
                if(GUILayout.Button("Vista YZ",currentButton)){yaw=90;pitch=0;velYaw=velPitch=0;}
                if(GUILayout.Button("Volver al edificio · R",currentButton))ResetPresentation();
            }
            stackScroll=GUILayout.BeginScrollView(stackScroll,GUILayout.Height(190));
            foreach(var stack in columnStackData.stacks)
                if(GUILayout.Button(stack.id+" · "+stack.member_ids[0]+" · "+stack.member_ids.Count+" pisos · "+(stack.confirmed?"CONFIRMED":"REVIEW"),currentButton))SelectColumnStack(stack);
            GUILayout.EndScrollView();
        }

        void LoadRevisionChanges()
        {
            if(revisionChanges!=null)return;
            string path=Path.Combine(Application.streamingAssetsPath,"current_review_changes.json");
            if(!File.Exists(path))return;
            var data=JsonUtility.FromJson<RevisionChanges>(File.ReadAllText(path));
            LoadProjectState();
            if(data!=null&&data.geometry_version==projectState?.geometry_sha256)revisionChanges=data;
        }
        void DrawRevisionChanges()
        {
            LoadRevisionChanges();
            if(GUILayout.Button((revisionChangesExpanded?"− ":"+ ")+"Cambios de esta revisión",currentButton))revisionChangesExpanded=!revisionChangesExpanded;
            if(!revisionChangesExpanded)return;
            if(revisionChanges==null){GUILayout.Label("Registro no disponible para esta geometría.",currentBody);return;}
            GUILayout.Label("Exclusiones archivadas, no visibles como estructura actual. Sin resultados nuevos.",currentBody);
            foreach(string kind in new[]{"WALL_REMOVED","WALL_SUPPORT_REMOVED","BEAM_MERGED","COLUMN_ALIGNED","REVIEW_REQUIRED","MERGED","REMOVED","CONNECTIVITY_FIXED"})
            {
                if((kind=="MERGED"||kind=="REMOVED"||kind=="CONNECTIVITY_FIXED")&&!revisionChanges.rows.Exists(r=>r.type==kind))continue;
                if(GUILayout.Button((revisionFilter==kind?"▶ ":"")+kind+" · "+revisionChanges.rows.FindAll(r=>r.type==kind).Count,currentButton))revisionFilter=kind;
            }
            revisionScroll=GUILayout.BeginScrollView(revisionScroll,GUILayout.Height(210));
            foreach(var row in revisionChanges.rows)
            {
                if(row.type!=revisionFilter)continue;
                if(GUILayout.Button(row.id,currentButton))
                {
                    var target=allElements.Find(e=>e!=null&&!e.isFeCandidateVisual&&e.humanId==row.id);
                    if(target!=null){ExitPendingReview();ReapplyAll();Select(target);inspectorVisible=true;ResetInspectorSections(target);}
                }
                if(row.historical_ids!=null&&row.historical_ids.Count>1)GUILayout.Label("IDs históricos: "+string.Join(" + ",row.historical_ids),currentBody);
                GUILayout.Label(row.reason,currentBody);GUILayout.Label("Fuente: "+row.source,currentBody);
            }
            GUILayout.EndScrollView();
        }

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
            pendingReviewRow=null;pendingReviewIds.Clear();stackReviewActive=false;
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
            GUILayout.Label(pendingReviewData.rows.Count+" casos · sin camino FE a apoyo",currentBody);
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
