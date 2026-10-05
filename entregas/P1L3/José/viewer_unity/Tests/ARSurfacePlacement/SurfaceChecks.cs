using System;
using System.Collections;
using System.Reflection;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.XR.ARFoundation;
using Unity.XR.CoreUtils;
using Mcoc.UnityViewer.P1L6AR;

public class SurfaceChecks : MonoBehaviour
{
    sealed class Backend : IARSurfacePlacementBackend
    {
        public bool tracking=true, hitValid=true, failNext;
        public int raycasts, creations, removals;
        public ARSurfaceHit hit;
        public TaskCompletionSource<Transform> pending;
        public bool IsTracking => tracking;
        public bool TryHit(out ARSurfaceHit value) { raycasts++; value=hit; return hitValid; }
        public Transform NewAnchor(Pose pose)
        {
            var anchor=new GameObject("TestSurfaceAnchor").transform;
            anchor.SetPositionAndRotation(pose.position+new Vector3(.02f,0,0),Quaternion.Euler(0,13,0)*pose.rotation);
            anchor.localScale=Vector3.one*2; // World-stays conversion must preserve AUTO scale.
            return anchor;
        }
        public Task<Transform> CreateAnchorAsync(Pose pose)
        {
            creations++;
            if(pending!=null)return pending.Task;
            if(failNext){failNext=false; return Task.FromResult<Transform>(null);}
            return Task.FromResult(NewAnchor(pose));
        }
        public bool IsAnchorTracked(Transform anchor) => tracking && anchor!=null;
        public void RemoveAnchor(Transform anchor) { removals++; if(anchor!=null)Destroy(anchor.gameObject); }
    }
    static object Field(object target,string name)=>target.GetType().GetField(name,BindingFlags.Instance|BindingFlags.NonPublic).GetValue(target);
    static void Set(object target,string name,object value)=>target.GetType().GetField(name,BindingFlags.Instance|BindingFlags.NonPublic).SetValue(target,value);
    static void Check(bool value,string message){if(!value)throw new Exception(message);}
    static void Same(Transform root,Vector3 p,Quaternion q,Vector3 s,string message)
    { Check(root.localPosition==p && Quaternion.Angle(root.localRotation,q)<.001f && root.localScale==s,message); }
    static void Outside(ARSurfacePlacementPose pose,Vector3 size,ARSurfaceHit hit)
    {
        for(int x=-1;x<=1;x+=2)for(int y=-1;y<=1;y+=2)for(int z=-1;z<=1;z+=2)
        {
            Vector3 corner=pose.pose.position+pose.pose.rotation*Vector3.Scale(size*pose.scale*.5f,new Vector3(x,y,z));
            Check(Vector3.Dot(corner-hit.point,pose.visibleNormal)>-1e-5f,"box does not penetrate surface");
        }
    }
    static bool Visual => Array.IndexOf(Environment.GetCommandLineArgs(), "-uiScreenshots") >= 0;
    static void CaptureLayout(Camera camera, ARStructuralElementSelectionUI selector, string state)
    {
        if (!Visual) return;
        foreach (int height in new[] {1920,2400})
        {
            int width=1080;
            Rect safe=new Rect(0,60,width,height-140); // gesture area + top camera cutout
            var target=new RenderTexture(width,height,24);
            camera.targetTexture=target;
            Canvas[] canvases=UnityEngine.Object.FindObjectsByType<Canvas>(FindObjectsInactive.Include,FindObjectsSortMode.None);
            foreach(Canvas canvas in canvases)
            {
                var scaler=canvas.GetComponent<CanvasScaler>(); if(scaler!=null)scaler.enabled=false;
                canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=camera;canvas.planeDistance=1;
                canvas.scaleFactor=1;
                var safeRect=canvas.transform.Find("SafeArea") as RectTransform;
                if(safeRect!=null)
                {
                    safeRect.anchorMin=new Vector2(safe.xMin/width,safe.yMin/height);
                    safeRect.anchorMax=new Vector2(safe.xMax/width,safe.yMax/height);
                }
            }
            typeof(ARStructuralElementSelectionUI).GetMethod("ApplySafeArea",BindingFlags.Instance|BindingFlags.NonPublic,null,
                new[]{typeof(Rect),typeof(Vector2Int)},null).Invoke(selector,new object[]{safe,new Vector2Int(width,height)});
            Canvas.ForceUpdateCanvases();
            foreach(string panelName in new[]{"searchPanel","compactPanel"})
            {
                var panel=(GameObject)Field(selector,panelName);if(!panel.activeInHierarchy)continue;
                Vector3[] corners=new Vector3[4];panel.GetComponent<RectTransform>().GetWorldCorners(corners);
                foreach(Vector3 corner in corners)
                { Vector3 point=camera.WorldToScreenPoint(corner);Check(point.x>=safe.xMin-.5f&&point.x<=safe.xMax+.5f&&point.y>=safe.yMin-.5f&&point.y<=safe.yMax+.5f,"top UI within safe area "+height); }
            }
            var ui=selector.GetComponent<ARSurfacePlacementUI>();
            foreach(string panelName in new[]{"previewActions","placedActions"})
            {
                var panel=(GameObject)Field(ui,panelName);if(!panel.activeInHierarchy)continue;
                Vector3[] corners=new Vector3[4];panel.GetComponent<RectTransform>().GetWorldCorners(corners);
                foreach(Vector3 corner in corners)
                {Vector3 point=camera.WorldToScreenPoint(corner);Check(point.y>=safe.yMin-.5f&&point.y<=safe.yMax+.5f,"bottom actions within safe area "+height);}
            }
            camera.Render();RenderTexture.active=target;
            var pixels=new Texture2D(width,height,TextureFormat.RGB24,false);
            pixels.ReadPixels(new Rect(0,0,width,height),0,0);pixels.Apply();
            System.IO.File.WriteAllBytes(Application.dataPath+"/../ui-"+state+"-"+height+".png",pixels.EncodeToPNG());
            RenderTexture.active=null;camera.targetTexture=null;
            UnityEngine.Object.Destroy(pixels);UnityEngine.Object.Destroy(target);
            foreach(Canvas canvas in canvases)
            {
                canvas.renderMode=RenderMode.ScreenSpaceOverlay;canvas.worldCamera=null;
                var scaler=canvas.GetComponent<CanvasScaler>();if(scaler!=null)scaler.enabled=true;
            }
        }
    }
    IEnumerator Start()
    {
        IEnumerator checks=Run();
        while(true)
        {
            object next;
            try {if(!checks.MoveNext())break;next=checks.Current;}
            catch(Exception ex){Debug.LogError("SURFACE_CHECKS_FAILED: "+ex);UnityEditor.EditorApplication.Exit(1);yield break;}
            yield return next;
        }
        Debug.Log("SURFACE_CHECKS_PASSED: A-H, 1200 fixed camera/plane/image updates, no-marker selection, geometry offsets, re-placement, failure/cancel races, quick-view fallback, R label.");
        UnityEditor.EditorApplication.Exit(0);
    }
    IEnumerator Run()
    {
        new GameObject("Events",typeof(EventSystem),typeof(InputSystemUIInputModule)).GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
        var camera=new GameObject("Camera",typeof(Camera)).transform;camera.gameObject.tag="MainCamera";
        var provider=new GameObject("ImageAnchor").AddComponent<FakeAnchorProvider>();provider.SetTracking(AnchorTrackingState.NotAvailable);
        var root=new GameObject("AR Origin");root.SetActive(false);
        var origin=root.AddComponent<XROrigin>();
        var offset=new GameObject("CameraOffset");offset.transform.SetParent(root.transform,false);
        origin.CameraFloorOffsetObject=offset;camera.SetParent(offset.transform,false);origin.Camera=camera.GetComponent<Camera>();
        root.AddComponent<ARAnchorManager>();root.AddComponent<LuisARImageAnchor>();
        var repository=root.AddComponent<ARDatasetRepository>();
        var renderer=root.AddComponent<StructuralARElementRenderer>();
        var adapter=root.AddComponent<IdentityModelToARTransform>();
        var controller=root.AddComponent<ARStructuralElementController>();
        Set(controller,"repository",repository);Set(controller,"elementRenderer",renderer);
        Set(controller,"anchorProviderBehaviour",provider);Set(controller,"transformBehaviour",adapter);
        var selector=root.AddComponent<ARStructuralElementSelectionUI>();
        var diagrams=root.AddComponent<LuisARDiagrams>();
        var legacyUI=root.AddComponent<LuisARTrackingUI>();
        var info=new GameObject("InfoPanel");Set(diagrams,"infoPanel",info);Set(legacyUI,"infoPanel",info);
        root.SetActive(true);yield return null;yield return null;
        var placement=controller.SurfacePlacement;
        Check(placement!=null && root.GetComponent<ARPlaneManager>()!=null && root.GetComponent<ARRaycastManager>()!=null,"automatic installation");
        Check(root.GetComponent<ARPlaneManager>().requestedDetectionMode==(UnityEngine.XR.ARSubsystems.PlaneDetectionMode.Horizontal|UnityEngine.XR.ARSubsystems.PlaneDetectionMode.Vertical),"horizontal and vertical requested");
        var backend=new Backend();placement.SetBackend(backend);yield return null;
        Check(!((Text)Field(root.GetComponent<ARSurfacePlacementUI>(),"status")).transform.parent.gameObject.activeSelf,"no false cancellation toast at startup");
        Check(!Array.Exists(UnityEngine.Object.FindObjectsByType<Text>(FindObjectsInactive.Include,FindObjectsSortMode.None),
            t=>t.text=="VISTA RÁPIDA"||t.text=="COLOCAR EN SUPERFICIE"),"no mode choice buttons in UI");
        Check(controller.CanSelectElement && !controller.HasQuickViewAnchor,"selection without marker");
        string[] ids={"E1-P2-V-041","E1-P2-C-001","E2-P2-M-007","E2-P2-M-007"};
        ARSurfaceKind[] kinds={ARSurfaceKind.Ceiling,ARSurfaceKind.Floor,ARSurfaceKind.Floor,ARSurfaceKind.Wall};
        for(int test=0;test<4;test++)
        {
            Check(selector.TryShowElement(ids[test]),"select "+ids[test]);
            Check(placement.State==ARPlacementState.Preview && !selector.SearchExpanded,"MOSTRAR enters preview directly and collapses search");
            backend.hit=new ARSurfaceHit {kind=kinds[test],point=kinds[test]==ARSurfaceKind.Ceiling?new Vector3(0,3,0):kinds[test]==ARSurfaceKind.Wall?new Vector3(0,1,0):Vector3.zero,
                normal=kinds[test]==ARSurfaceKind.Wall?Vector3.forward:Vector3.up};
            camera.position=new Vector3(0,1.5f,-2);camera.LookAt(backend.hit.point);
            int anchorsBefore=backend.creations;
            placement.BeginPreview();yield return null;
            Check(placement.CanFix && placement.Preview.gameObject.activeSelf,"valid preview "+test);
            if(test==0)CaptureLayout(camera.GetComponent<Camera>(),selector,"preview");
            var selected=controller.SelectedElement;
            Vector3 real=StructuralARElementRenderer.GetSizeMetres(selected);
            Vector3 expected=test==0?new Vector3(3.47f,.8f,.6f):test==1?new Vector3(.7f,3.96f,.7f):new Vector3(2.82f,3.96f,.25f);
            Check(Vector3.Distance(real,expected)<1e-5f,"validated real dimensions unchanged");
            var preview=placement.Preview;var mesh=preview.StructuralMesh;
            float scale=preview.UniformScale;
            Check(Mathf.Abs(Mathf.Max(mesh.localScale.x,mesh.localScale.y,mesh.localScale.z)-.65f)<1e-5f,"AUTO .65");
            Check(Vector3.Distance(mesh.localScale,real*scale)<1e-5f,"uniform proportions");
            Check(Mathf.Abs(mesh.GetComponent<Renderer>().sharedMaterial.color.a-.32f)<.001f,"translucent preview");
            Transform reticle=preview.transform.Find("SurfaceReticle");
            Vector3 quadNormal=reticle.GetComponent<MeshFilter>().sharedMesh.normals[0];
            Check(Vector3.Dot(reticle.TransformDirection(quadNormal),camera.position-backend.hit.point)>0,"reticle faces visible side");
            Check(Vector3.Dot(preview.transform.up,Vector3.up)>.99999f,"worldUp independent of camera pitch");
            Check(ARSurfacePlacementMath.TryPose(selected.type,real,backend.hit,camera.position,ARSurfacePlacementMath.InitialRight(camera.forward),0,out var pose),"pose math");
            Outside(pose,real,backend.hit);
            if(test==0)
            {
                Check(pose.visibleNormal.y<-.99f,"visible ceiling normal into room");
                Check(Mathf.Abs(preview.transform.position.y-(3f-real.y*scale*.5f))<1e-5f,"ceiling beam half-height offset");
                Check(Mathf.Abs(Vector3.Dot(preview.transform.right,Vector3.up))<1e-6f,"beam axis in ceiling plane");
            }
            if(test==1||test==2)Check(Mathf.Abs(preview.transform.position.y-real.y*scale*.5f)<1e-5f,"floor base touches plane");
            if(test==3)Check(Mathf.Abs(preview.transform.position.z+real.z*scale*.5f)<1e-5f,"wall half-thickness offset toward user");
            Vector3 before=preview.transform.position,oldRight=preview.transform.right;Vector3 oldScale=mesh.localScale;
            placement.Rotate90();yield return null;
            if(test!=3)Check(Mathf.Abs(Vector3.Dot(oldRight,preview.transform.right))<1e-5f,"90 degree rotation");
            else Check(Vector3.Dot(oldRight,preview.transform.right)>.999f && !placement.CanRotate,"wall rotation cannot tilt height");
            Check(preview.transform.position==before && mesh.localScale==oldScale,"turn preserves contact point offset and scale");
            backend.hitValid=false;yield return null;Check(!placement.CanFix && !preview.gameObject.activeSelf,"no hit hides reused preview");
            backend.hitValid=true;yield return null;Check(placement.Preview==preview && backend.creations==anchorsBefore,"no frame anchors or preview rebuilds");
            var task=placement.ConfirmAsync();while(!task.IsCompleted)yield return null;
            Check(task.Result && backend.creations==anchorsBefore+1 && placement.HasTrackedPlacement,"one anchor on FIX");
            Transform fixedRoot=placement.PlacedRoot,anchor=placement.PlacementAnchor;
            Check(fixedRoot.parent==anchor && fixedRoot.Find("StructuralMesh")!=null,"overlay-ready child structure");
            Check(Vector3.Distance(mesh.lossyScale,real*scale)<1e-5f,"commit preserves preview world dimensions under scaled anchor");
            Check(fixedRoot.GetComponent<ARPlacementPreview>().StructuralMesh.GetComponent<Renderer>().sharedMaterial.color.a==1,"opaque fixed mesh");
            Vector3 p=fixedRoot.localPosition,s=fixedRoot.localScale;Quaternion q=fixedRoot.localRotation;
            yield return null;
            Check(!selector.SearchExpanded && ((GameObject)Field(selector,"compactPanel")).activeSelf,"FIX collapses to ID/type bar");
            Check(((Text)Field(selector,"compactTitle")).text==ids[test]+" · "+selected.type.ToUpperInvariant(),"compact bar uses selected ID/type");
            if(test==0)
            {
                CaptureLayout(camera.GetComponent<Camera>(),selector,"fixed");
                yield return new WaitForSecondsRealtime(2.6f);
                var toast=((Text)Field(root.GetComponent<ARSurfacePlacementUI>(),"status")).transform.parent.gameObject;
                Check(!toast.activeSelf,"confirmation toast expires after 2.5 seconds");
            }
            ((Button)Field(selector,"changeButton")).onClick.Invoke();yield return null;
            Check(selector.SearchExpanded && ((GameObject)Field(selector,"searchPanel")).activeSelf,"CAMBIAR expands search");
            if(test==0)CaptureLayout(camera.GetComponent<Camera>(),selector,"search");
            Same(fixedRoot,p,q,s,"CAMBIAR preserves old placement");
            Check(!selector.TryShowElement("invalid-id") && placement.State==ARPlacementState.Placed && placement.PlacedRoot==fixedRoot,"invalid ID does not start preview or remove object");
            yield return null;
            Check(((Text)Field(selector,"status")).text.Contains("ID no encontrado"),"invalid ID error remains readable");
            ((InputField)Field(selector,"elementId")).ActivateInputField();yield return null;
            ((InputField)Field(selector,"elementId")).DeactivateInputField();yield return null;
            Check(selector.SearchExpanded,"closing text input preserves expanded layout");
            var searchRect=((GameObject)Field(selector,"searchPanel")).GetComponent<RectTransform>();
            Check(searchRect.anchoredPosition.y==-12 && searchRect.sizeDelta.y==100,"search has compact safe top margin");
            int raycastsAfter=backend.raycasts;
            for(int frame=0;frame<300;frame++)
            {
                camera.position=Quaternion.Euler(frame%90,frame*13,frame%60)*new Vector3(0,1,-2);
                camera.rotation=Quaternion.Euler(frame%140,frame*17,frame%160);
                backend.hit.point=new Vector3(frame*.01f,5,4);backend.hit.normal=Quaternion.Euler(frame,frame,frame)*Vector3.up;
                provider.SetPose(new Vector3(1,2,frame*.01f),Quaternion.Euler(frame,frame,frame),Vector3.one);
                controller.OnAnchorReady(new AnchorPoseData { position=Vector3.one*frame,rotation=camera.rotation,scale=Vector3.one,trackingState=AnchorTrackingState.Tracking });
                yield return null;
                Same(fixedRoot,p,q,s,"frozen local TRS "+test+" frame "+frame);
                Check(placement.PlacementAnchor==anchor && backend.raycasts==raycastsAfter,"no fixed raycasts or anchor changes");
            }
            for(int n=0;n<5;n++)
            {
                legacyUI.OpenInformation();Check(info.activeSelf,"surface information available");
                yield return null;
                Check(!((GameObject)Field(selector,"searchPanel")).activeSelf,"information hides expanded search");
                diagrams.Open();Check(!info.activeSelf,"information does not cover diagrams");
                yield return null;
                Check(!((GameObject)Field(selector,"searchPanel")).activeSelf && !((GameObject)Field(selector,"compactPanel")).activeSelf,"diagrams hide search and header");
                if(test==0 && n==0)CaptureLayout(camera.GetComponent<Camera>(),selector,"diagrams");
                diagrams.Close();info.SetActive(false);
                Same(fixedRoot,p,q,s,"UI does not move placement");
            }
            Text label=(Text)Field(diagrams,"caseLabel");
            Check(label.text=="Caso: R · CURRENT" && label.GetComponent<Button>()==null,"R is text not button");
            foreach(Button component in (Button[])Field(diagrams,"components"))
            { component.onClick.Invoke();Check(((Text)Field(diagrams,"values")).text.Contains("CASE_R"),"force components remain functional"); }
            backend.tracking=false;yield return null;Check(!controller.HasTrackedAnchor,"surface tracking unavailable");
            backend.tracking=true;yield return null;Same(fixedRoot,p,q,s,"tracking recovery retains TRS");
            Check(!selector.TryShowElement("AAA-123") && controller.SelectedElement==selected,"invalid ID retains surface selection");
            backend.hit=new ARSurfaceHit{kind=ARSurfaceKind.Floor,point=new Vector3(.7f,0,.2f),normal=Vector3.up};
            camera.position=new Vector3(0,1,-2);camera.rotation=Quaternion.identity;
            placement.Relocate();yield return null;
            Check(controller.SelectedElement==selected && placement.PlacementAnchor==anchor,"relocate preserves ID and old anchor until confirm");
            Same(fixedRoot,p,q,s,"old object untouched in preview");
            placement.Cancel();Check(placement.PlacedRoot==fixedRoot && placement.HasTrackedPlacement,"cancel preserves old placement");
        }
        var wallSize=new Vector3(2.82f,3.96f,.25f);
        for(int pitch=-80;pitch<=80;pitch+=20)for(int roll=-80;roll<=80;roll+=20)
        {
            Vector3 heading=ARSurfacePlacementMath.InitialRight(Quaternion.Euler(pitch,32,roll)*Vector3.forward);
            ARSurfaceHit imperfect=new ARSurfaceHit {kind=ARSurfaceKind.Wall,point=Vector3.zero,normal=Quaternion.Euler(5,0,0)*Vector3.forward};
            Check(ARSurfacePlacementMath.TryPose("wall",wallSize,imperfect,new Vector3(0,1,-2),heading,0,out var upright),"imperfect wall supported");
            Check(Vector3.Dot(upright.pose.rotation*Vector3.up,Vector3.up)>.99999f,"phone tilt never tilts wall");Outside(upright,wallSize,imperfect);
        }
        var inclinedCeiling=new ARSurfaceHit {kind=ARSurfaceKind.Ceiling,point=new Vector3(0,3,0),normal=Quaternion.Euler(5,0,0)*Vector3.up};
        Check(ARSurfacePlacementMath.TryPose("beam",new Vector3(8.2f,.8f,.6f),inclinedCeiling,new Vector3(0,1,-2),Vector3.right,0,out var beam0),"slightly imperfect ceiling");
        Check(ARSurfacePlacementMath.TryPose("beam",new Vector3(8.2f,.8f,.6f),inclinedCeiling,new Vector3(0,1,-2),Vector3.right,1,out var beam90),"ceiling quarter-turn");
        Check(Vector3.Distance(beam0.pose.position,beam90.pose.position)<1e-5f,"ceiling turn preserves exact offset");
        Check(Vector3.Dot(beam90.pose.rotation*Vector3.up,Vector3.up)>.99999f,"beam is level despite imperfect ceiling");
        Check(Mathf.Abs((beam90.pose.rotation*Vector3.right).y)<1e-5f,"beam length structurally horizontal");
        Check(Mathf.Abs((beam90.pose.rotation*Vector3.forward).y)<1e-5f,"beam width structurally horizontal");
        Check(beam0.pose.position.y < inclinedCeiling.point.y && beam0.pose.position.x==inclinedCeiling.point.x && beam0.pose.position.z==inclinedCeiling.point.z,"ceiling offset stays vertical toward room");
        Check(ARSurfacePlacementMath.TryPose("beam",new Vector3(8.2f,.8f,.6f),inclinedCeiling,new Vector3(0,1,-2),Vector3.right,5f,out var beam5),"five-degree correction on imperfect ceiling");
        Check(beam5.pose.position==beam0.pose.position,"manual yaw does not change support position");
        Outside(beam5,new Vector3(8.2f,.8f,.6f),inclinedCeiling);
        Outside(beam90,new Vector3(8.2f,.8f,.6f),inclinedCeiling);
        var oldAnchor=placement.PlacementAnchor;var oldRoot=placement.PlacedRoot;
        placement.Relocate();yield return null;backend.failNext=true;
        var failed=placement.ConfirmAsync();while(!failed.IsCompleted)yield return null;
        Check(!failed.Result && placement.PlacedRoot==oldRoot && placement.PlacementAnchor==oldAnchor,"anchor failure preserves previous placement");
        yield return null;
        var retry=placement.ConfirmAsync();while(!retry.IsCompleted)yield return null;
        Check(retry.Result && placement.PlacementAnchor!=oldAnchor && controller.SelectedElement.element_id=="E2-P2-M-007","reposition commits new anchor same ID");
        yield return null;
        Check(oldAnchor==null && backend.removals>=4,"only previous placement anchor removed");
        placement.Relocate();yield return null;
        backend.pending=new TaskCompletionSource<Transform>();
        var pending=placement.ConfirmAsync();int count=backend.creations;
        Check(!placement.ConfirmAsync().Result && backend.creations==count,"double FIX guarded");
        var retained=placement.PlacementAnchor;placement.Cancel();
        backend.pending.SetResult(backend.NewAnchor(new Pose(Vector3.zero,Quaternion.identity)));
        while(!pending.IsCompleted)yield return null;
        Check(!pending.Result && placement.PlacementAnchor==retained,"late cancelled anchor cleaned up");backend.pending=null;
        provider.SetTracking(AnchorTrackingState.Tracking);yield return null;
        placement.QuickView();yield return null;
        Check(!placement.SurfaceMode && renderer.RenderedTransform!=null && renderer.RenderedTransform.parent==provider.AnchorTransform,"original quick fallback");
        var quickRoot=renderer.RenderedTransform;var qp=quickRoot.localPosition;var qq=quickRoot.localRotation;var qs=quickRoot.localScale;
        placement.BeginPreview();yield return null;placement.Cancel();yield return null;
        Check(renderer.RenderedTransform==quickRoot && !placement.SurfaceMode,"quick preview cancel returns same quick instance");Same(quickRoot,qp,qq,qs,"quick orientation preserved");
        Check(!ARSurfacePlacementMath.TryPose("column",new Vector3(.7f,3.96f,.7f),new ARSurfaceHit{kind=ARSurfaceKind.Wall,normal=Vector3.forward},new Vector3(0,1,-2),Vector3.right,0,out _),"column on wall rejected");
        var disabledManager=root.GetComponent<ARAnchorManager>();disabledManager.enabled=false;
        var cleanupObject=new GameObject("PlacementCleanup");cleanupObject.SetActive(false);cleanupObject.AddComponent<ARAnchor>();
        var nativeBoundary=new ARFoundationSurfaceBackend(root.GetComponent<ARPlaneManager>(),root.GetComponent<ARRaycastManager>(),disabledManager);
        nativeBoundary.RemoveAnchor(cleanupObject.transform);yield return null;
        Check(cleanupObject==null,"cleanup safe with disabled native anchor manager");
        foreach(string floor in new[]{"P1","P2","P3","P4","S1"})
        {
            StructuralElementARData row=Array.Find(repository.Dataset.elements, e=>e.floor==floor && (e.type=="beam"||e.type=="column"||e.type=="wall"));
            Check(row!=null && selector.TryShowElement(row.element_id),"all CURRENT floors remain searchable: "+floor);
            Check(placement.State==ARPlacementState.Preview,"all floors use direct preview");placement.Cancel();
        }
        Debug.Log("Surface numerical cases A-D: all corners outside plane; offsets .5 H / .5 thickness; worldUp; uniform AUTO scale. Stability: 4 x 300 updates. Old quick geometry renderer untouched.");
    }
}





