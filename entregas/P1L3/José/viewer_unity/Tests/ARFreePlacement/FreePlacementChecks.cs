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

public class FreePlacementChecks : MonoBehaviour
{
    sealed class Backend : IARSurfacePlacementBackend
    {
        public bool tracking=true,hasHit;
        public int rays,creations,removals;
        public ARSurfaceHit hit=new ARSurfaceHit{kind=ARSurfaceKind.Floor,point=Vector3.zero,normal=Vector3.up};
        public bool IsTracking=>tracking;
        public bool TryHit(out ARSurfaceHit value){rays++;value=hit;return hasHit;}
        public Task<Transform> CreateAnchorAsync(Pose pose)
        {
            creations++;Transform anchor=new GameObject("FreeTestAnchor").transform;
            anchor.SetPositionAndRotation(pose.position+Vector3.right*.02f,Quaternion.Euler(0,13,0)*pose.rotation);
            anchor.localScale=Vector3.one*2;return Task.FromResult(anchor);
        }
        public bool IsAnchorTracked(Transform anchor)=>tracking&&anchor!=null;
        public void RemoveAnchor(Transform anchor){removals++;if(anchor!=null)UnityEngine.Object.Destroy(anchor.gameObject);}
    }
    static object Field(object obj,string name)=>obj.GetType().GetField(name,BindingFlags.Instance|BindingFlags.NonPublic).GetValue(obj);
    static void Set(object obj,string name,object value)=>obj.GetType().GetField(name,BindingFlags.Instance|BindingFlags.NonPublic).SetValue(obj,value);
    static void Check(bool condition,string why){if(!condition)throw new Exception(why);}
    static void Same(Transform t,Vector3 p,Quaternion q,Vector3 s,string why)
    {Check(t.localPosition==p&&Quaternion.Angle(t.localRotation,q)<.001f&&t.localScale==s,why);}
    static void Level(Transform t)
    {Check(Vector3.Dot(t.up,Vector3.up)>.99999f&&Mathf.Abs(t.right.y)<1e-5f&&Mathf.Abs(t.forward.y)<1e-5f,"exact worldUp, horizontal transverse axes");}
    static void Capture(Camera camera,ARStructuralElementSelectionUI selector,string name)
    {typeof(SurfaceChecks).GetMethod("CaptureLayout",BindingFlags.Static|BindingFlags.NonPublic).Invoke(null,new object[]{camera,selector,name});}
    IEnumerator Start()
    {
        IEnumerator run=Run();
        while(true)
        {
            object next;try {if(!run.MoveNext())break;next=run.Current;}
            catch(Exception e){Debug.LogError("FREE_PLACEMENT_CHECKS_FAILED: "+e);UnityEditor.EditorApplication.Exit(1);yield break;}
            yield return next;
        }
        Debug.Log("FREE_PLACEMENT_CHECKS_PASSED: no-plane P2 BEAM/COLUMN/WALL, manual yaw/height/depth, exact gravity, preview/fixed invariance, 1200 fixed updates, My overlay, mode switch, relocation/cancel, tracking recovery, level imperfect planes.");
        UnityEditor.EditorApplication.Exit(0);
    }
    IEnumerator Run()
    {
        new GameObject("Events",typeof(EventSystem),typeof(InputSystemUIInputModule)).GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
        Camera camera=new GameObject("Camera",typeof(Camera)).GetComponent<Camera>();camera.tag="MainCamera";
        var provider=new GameObject("ImageAnchor").AddComponent<FakeAnchorProvider>();provider.SetTracking(AnchorTrackingState.NotAvailable);
        var root=new GameObject("AR Origin");root.SetActive(false);var origin=root.AddComponent<XROrigin>();
        var offset=new GameObject("CameraOffset");offset.transform.SetParent(root.transform,false);origin.CameraFloorOffsetObject=offset;
        camera.transform.SetParent(offset.transform,false);origin.Camera=camera;
        root.AddComponent<ARAnchorManager>();root.AddComponent<LuisARImageAnchor>();
        var repo=root.AddComponent<ARDatasetRepository>();var renderer=root.AddComponent<StructuralARElementRenderer>();
        var adapter=root.AddComponent<IdentityModelToARTransform>();var controller=root.AddComponent<ARStructuralElementController>();
        Set(controller,"repository",repo);Set(controller,"elementRenderer",renderer);Set(controller,"anchorProviderBehaviour",provider);Set(controller,"transformBehaviour",adapter);
        var selector=root.AddComponent<ARStructuralElementSelectionUI>();var diagrams=root.AddComponent<LuisARDiagrams>();
        var trackingUI=root.AddComponent<LuisARTrackingUI>();var info=new GameObject("InfoPanel");Set(diagrams,"infoPanel",info);Set(trackingUI,"infoPanel",info);
        root.SetActive(true);yield return null;yield return null;
        var placement=controller.SurfacePlacement;var backend=new Backend();placement.SetBackend(backend);
        var ui=root.GetComponent<ARSurfacePlacementUI>();var overlay=root.GetComponent<ARStructuralResultOverlay3D>();
        foreach(string id in new[]{"E1-P2-V-041","E1-P2-C-001","E2-P2-M-007"})
        {
            camera.transform.SetPositionAndRotation(new Vector3(0,1.5f,-2),Quaternion.Euler(-65,32,48));
            Check(selector.TryShowElement(id),"direct MOSTRAR preview");yield return null;
            Check(!placement.FreePlacement&&!placement.CanFix&&!placement.Preview.gameObject.activeSelf,"no plane hides surface preview");
            int creations=backend.creations;
            ((Button)Field(ui,"mode")).onClick.Invoke();yield return null;
            Check(placement.FreePlacement&&placement.CanFix&&placement.Preview.gameObject.activeSelf,"free placement works without ARPlane");
            Level(placement.Preview.transform);
            Check(Vector3.Distance(placement.Preview.transform.position,camera.transform.position+camera.transform.forward*1.2f)<1e-5f,"camera view sampled only for initial position");
            Check(!placement.Preview.transform.Find("SurfaceReticle").gameObject.activeSelf,"no fake surface reticle");
            var preview=placement.Preview;Vector3 p=preview.transform.position,s=preview.StructuralMesh.localScale;
            Quaternion q=preview.transform.rotation;
            ((Button)Field(ui,"yawRight")).onClick.Invoke();yield return null;
            Check(Mathf.Abs(Quaternion.Angle(q,preview.transform.rotation)-5)<.001f&&preview.transform.position==p&&preview.StructuralMesh.localScale==s,"+5 only changes yaw");
            ((Button)Field(ui,"yawLeft")).onClick.Invoke();yield return null;
            Check(Quaternion.Angle(q,preview.transform.rotation)<.001f,"-5 reverses +5");
            placement.Rotate90();Level(preview.transform);
            Check(Mathf.Abs(Quaternion.Angle(q,preview.transform.rotation)-90)<.001f&&preview.transform.position==p,"90 around gravity, no position change");
            q=preview.transform.rotation;
            ((Button)Field(ui,"raise")).onClick.Invoke();
            Check(Vector3.Distance(preview.transform.position,p+Vector3.up*.05f)<1e-5f&&Quaternion.Angle(q,preview.transform.rotation)<.001f,"SUBIR +5cm without rotation");
            ((Button)Field(ui,"lower")).onClick.Invoke();Check(Vector3.Distance(preview.transform.position,p)<1e-5f,"BAJAR -5cm");
            ((Button)Field(ui,"far")).onClick.Invoke();
            Check(Mathf.Abs(preview.transform.position.y-p.y)<1e-6f&&Mathf.Abs(Vector3.Distance(preview.transform.position,p)-.05f)<1e-5f,"ALEJAR is horizontal +5cm");
            ((Button)Field(ui,"near")).onClick.Invoke();Check(Vector3.Distance(preview.transform.position,p)<1e-5f,"ACERCAR reverses depth");
            int rays=backend.rays;
            for(int n=0;n<50;n++)
            {
                camera.transform.SetPositionAndRotation(new Vector3(n,1,3),Quaternion.Euler(n*7,n*11,n*3));yield return null;
                Check(Vector3.Distance(preview.transform.position,p)<1e-5f&&Quaternion.Angle(q,preview.transform.rotation)<.001f&&preview.StructuralMesh.localScale==s,"free preview never follows camera");
                Check(backend.rays==rays&&backend.creations==creations,"free preview uses no raycast or anchor");
            }
            backend.tracking=false;yield return null;Check(!placement.CanFix&&!preview.gameObject.activeSelf,"tracking loss disables free fix");
            backend.tracking=true;yield return null;Check(placement.CanFix&&preview.gameObject.activeSelf,"free preview recovers");
            Check(Vector3.Distance(preview.transform.position,p)<1e-5f&&Quaternion.Angle(q,preview.transform.rotation)<.001f,"tracking recovery keeps adjusted free pose");
            if(id=="E1-P2-V-041")
            {
                camera.transform.position=p+new Vector3(.12f,-.4f,-1.6f);camera.transform.LookAt(p);
                Capture(camera,selector,"free-preview");
            }
            Check(placement.ConfirmAsync().Result,"FIX creates free anchor");yield return null;
            Check(backend.creations==creations+1&&placement.Preview==null,"one anchor only after FIX");
            var placed=placement.PlacedRoot;Level(placed);
            Check(Vector3.Distance(placed.position,p)<1e-5f&&Quaternion.Angle(placed.rotation,q)<.001f,"free fixed pose matches preview despite anchor frame");
            Check(Vector3.Distance(placed.GetComponent<ARPlacementPreview>().StructuralMesh.lossyScale,s)<1e-5f,"AUTO physical proportions preserved");
            Check(!((GameObject)Field(ui,"previewActions")).activeSelf&&!selector.SearchExpanded,"fixed hides all editing controls and collapses search");
            ARForceDiagram3DRenderer diagram=overlay.Current;
            if(id=="E1-P2-V-041")
            {
                diagrams.Open();((Button[])Field(diagrams,"components"))[4].onClick.Invoke();((Button)Field(diagrams,"overlayToggle")).onClick.Invoke();yield return null;
                diagram=overlay.Current;Check(diagram!=null&&diagram.transform.parent==placed&&diagram.Component==4,"My works with free root");diagrams.Close();yield return null;
                Capture(camera,selector,"free-fixed-overlay");
            }
            Vector3 lp=placed.localPosition,ls=placed.localScale;Quaternion lq=placed.localRotation;
            for(int n=0;n<400;n++)
            {
                camera.transform.SetPositionAndRotation(new Vector3(n,2,4),Quaternion.Euler(n,n*17,n*3));backend.hit.point=new Vector3(n,5,2);
                provider.SetPose(new Vector3(n,1,2),camera.transform.rotation,Vector3.one);yield return null;
                Same(placed,lp,lq,ls,"400 fixed updates keep local pose");
                Check(backend.rays==rays&&backend.creations==creations+1,"fixed does not raycast/create anchors");
                if(diagram!=null)Same(diagram.transform,Vector3.zero,Quaternion.identity,Vector3.one,"overlay stays member child");
            }
            placement.MoveHeight(.05f);placement.MoveDepth(.05f);placement.RotateYaw(5);placement.UseFreePlacement();placement.UseSurfacePlacement();
            Same(placed,lp,lq,ls,"editing API is inert after FIX");
            trackingUI.OpenInformation();diagrams.Open();diagrams.Close();info.SetActive(false);Same(placed,lp,lq,ls,"info/2D do not move free member");
            placement.Relocate();yield return null;placement.UseFreePlacement();yield return null;
            Check(placement.FreePlacement,"REUBICAR resumes free mode automatically");
            Check(placement.PlacedRoot==placed&&overlay.Current==diagram,"relocation preview preserves old free member/overlay");
            placement.Cancel();yield return null;Check(placement.PlacedRoot==placed&&overlay.Current==diagram,"cancel preserves old free member/overlay");
            if(id=="E1-P2-V-041")
            {
                placement.Relocate();yield return null;
                Check(placement.FreePlacement&&placement.ConfirmAsync().Result,"free relocation confirms without a plane");yield return null;
                Check(placed==null&&diagram==null&&overlay.Current!=null&&overlay.Current.Component==4&&overlay.Current.transform.parent==placement.PlacedRoot,"confirmed free relocation cleans old root and recreates My on new root");
            }
        }
        // Switching back to surface uses real hits, never a fabricated plane.
        placement.Relocate();yield return null;placement.UseFreePlacement();yield return null;
        placement.UseSurfacePlacement();yield return null;
        Check(!placement.FreePlacement&&!placement.CanFix&&!placement.Preview.gameObject.activeSelf,"surface mode still requires real valid plane");
        backend.hasHit=true;backend.hit=new ARSurfaceHit{kind=ARSurfaceKind.Floor,point=Vector3.zero,normal=Quaternion.Euler(5,0,0)*Vector3.up};
        camera.transform.position=new Vector3(0,1,-2);yield return null;
        Check(placement.CanFix&&placement.Preview.transform.Find("SurfaceReticle").gameObject.activeSelf,"real surface restores reticle");Level(placement.Preview.transform);
        var surface=placement.Preview.transform;Vector3 sp=surface.position;Quaternion sq=surface.rotation;
        placement.RotateYaw(5);yield return null;
        Check(surface.position==sp&&Mathf.Abs(Quaternion.Angle(sq,surface.rotation)-5)<.001f,"surface yaw adjustment has no position drift on imperfect plane");
        placement.MoveHeight(.05f);Check(surface.position==sp,"height edits restricted to free mode");
        placement.Cancel();Check(placement.FreePlacement,"cancel after switching modes restores committed free mode");
        placement.Relocate();yield return null;Check(placement.FreePlacement,"relocate uses committed mode after cancellation");
        placement.UseSurfacePlacement();yield return null;
        foreach(string type in new[]{"beam","column","wall"})
        foreach(float yaw in new[]{0f,5f,45f,90f,175f})
        {
            Vector3 size=type=="beam"?new Vector3(3.47f,.8f,.6f):type=="column"?new Vector3(.7f,3.96f,.7f):new Vector3(2.82f,3.96f,.25f);
            Check(ARSurfacePlacementMath.TryPose(type,size,backend.hit,camera.transform.position,Vector3.right,yaw,out var pose),"imperfect floor supported");
            Check(Vector3.Dot(pose.pose.rotation*Vector3.up,Vector3.up)>.99999f,"all surface types keep exact gravity");
            for(int x=-1;x<=1;x+=2)for(int y=-1;y<=1;y+=2)for(int z=-1;z<=1;z+=2)
            {Vector3 corner=pose.pose.position+pose.pose.rotation*Vector3.Scale(size*pose.scale*.5f,new Vector3(x,y,z));Check(Vector3.Dot(corner-backend.hit.point,pose.visibleNormal)>-1e-5f,"no penetration with level yaw");}
        }
        for(int pitch=-90;pitch<=90;pitch+=15)for(int roll=-90;roll<=90;roll+=15)
        {
            Quaternion phone=Quaternion.Euler(pitch,32,roll);
            Quaternion level=ARSurfacePlacementMath.LevelRotation(ARSurfacePlacementMath.InitialRight(phone*Vector3.forward),5);
            Check(Vector3.Dot(level*Vector3.up,Vector3.up)>.99999f,"169 phone pitch/roll combinations do not tilt member");
        }
    }
}
