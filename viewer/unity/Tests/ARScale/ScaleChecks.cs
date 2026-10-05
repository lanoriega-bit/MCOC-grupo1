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

public class ScaleChecks : MonoBehaviour
{
    sealed class Backend : IARSurfacePlacementBackend
    {
        public bool tracking=true,hitValid=true;
        public int anchors,rays;
        public ARSurfaceHit hit;
        public bool IsTracking=>tracking;
        public bool TryHit(out ARSurfaceHit h){rays++;h=hit;return hitValid;}
        public Task<Transform> CreateAnchorAsync(Pose pose)
        {
            anchors++;var root=new GameObject("ScaleAnchor").transform;
            root.SetPositionAndRotation(pose.position+Vector3.right*.02f,Quaternion.Euler(0,13,0)*pose.rotation);
            root.localScale=Vector3.one*2;return Task.FromResult(root);
        }
        public bool IsAnchorTracked(Transform root)=>tracking && root!=null;
        public void RemoveAnchor(Transform root){if(root!=null)Destroy(root.gameObject);}
    }
    static void Check(bool ok,string message){if(!ok)throw new Exception(message);}
    static void Set(object target,string name,object value)=>target.GetType().GetField(name,BindingFlags.Instance|BindingFlags.NonPublic).SetValue(target,value);
    static object Field(object target,string name)=>target.GetType().GetField(name,BindingFlags.Instance|BindingFlags.NonPublic).GetValue(target);
    static void Dimensions(Transform member,Vector3 expected)
    {
        var mesh=member.GetComponent<ARPlacementPreview>().StructuralMesh;
        Check(Vector3.Distance(mesh.lossyScale,expected)<.00005f,"metric mesh world dimensions "+expected);
        // Renderer AABB cannot measure longitudinal lengths after yaw. Transform
        // all actual mesh-bounds corners into member's orthonormal world frame.
        Bounds local=mesh.GetComponent<MeshFilter>().sharedMesh.bounds;
        Vector3 min=Vector3.one*float.MaxValue,max=Vector3.one*float.MinValue;
        for(int x=-1;x<=1;x+=2)for(int y=-1;y<=1;y+=2)for(int z=-1;z<=1;z+=2)
        {
            Vector3 world=mesh.TransformPoint(local.center+Vector3.Scale(local.extents,new Vector3(x,y,z)))-member.position;
            Vector3 p=Quaternion.Inverse(member.rotation)*world;min=Vector3.Min(min,p);max=Vector3.Max(max,p);
        }
        Check(Vector3.Distance(max-min,expected)<.00005f,"actual rendered oriented bounds metric");
        Check(Vector3.Dot(member.up,Vector3.up)>.99999f,"scale never tilts worldUp");
    }
    static void Overlay(ARForceDiagram3DRenderer diagram,StructuralElementARData row,int component)
    {
        Check(diagram!=null&&diagram.Component==component,"selected overlay exists");
        bool vertical=row.type!="beam",depth=component==2||component==5;
        Vector3 axis=depth?Vector3.forward:vertical?Vector3.right:Vector3.up;
        var member=diagram.transform.parent;var mesh=member.GetComponent<ARPlacementPreview>().StructuralMesh;
        Check(ARCurrentDiagramData.TryValues(row,0,component,out double i,out double j)&&diagram.EndI==i&&diagram.EndJ==j,"CASE_R unchanged");
        Vector3 baseSpan=member.TransformVector(diagram.BaseJ-diagram.BaseI);
        Check(Mathf.Abs(baseSpan.magnitude-(vertical?mesh.lossyScale.y:mesh.lossyScale.x))<.00005f,"overlay spans full scaled physical member");
        double max=Math.Max(Math.Abs(i),Math.Abs(j));float amplitude=0;
        foreach(var p in diagram.Curve)
        {
            float t=Vector3.Dot(p-diagram.BaseI,diagram.BaseJ-diagram.BaseI)/(diagram.BaseJ-diagram.BaseI).sqrMagnitude;
            Vector3 baseline=Vector3.Lerp(diagram.BaseI,diagram.BaseJ,t);
            float metres=member.TransformVector(p-baseline).magnitude;amplitude=Mathf.Max(amplitude,metres);
            float signed=Vector3.Dot(p-baseline,axis)*member.TransformVector(axis).magnitude;
            float wanted=max==0?0:(float)(((1-t)*i+t*j)/max)*.20f;
            Check(Mathf.Abs(signed-wanted)<.00005f,"independent signed .20 m graphical interpolation");
            Vector3 clearAxis=depth?(vertical?Vector3.right:Vector3.up):Vector3.forward;
            float half=depth?(vertical?mesh.localScale.x:mesh.localScale.y)*.5f:mesh.localScale.z*.5f;
            float distance=(Mathf.Abs(Vector3.Dot(p,clearAxis))-half)*member.TransformVector(clearAxis).magnitude;
            Check(Mathf.Abs(distance-.015f)<.00005f,"independent 15 mm exterior offset");
        }
        Check(Mathf.Abs(amplitude-(max==0?0:.20f))<.00005f,"amplitude independent of geometry scale");
        foreach(var line in diagram.GetComponentsInChildren<LineRenderer>())
            Check(Mathf.Abs(line.widthMultiplier*member.TransformVector(axis).magnitude-.003f)<.00001f,"independent 3 mm line width");
    }
    static void Contact(Transform member,ARSurfaceHit hit,Vector3 visibleNormal)
    {
        var mesh=member.GetComponent<ARPlacementPreview>().StructuralMesh;
        Bounds bounds=mesh.GetComponent<MeshFilter>().sharedMesh.bounds;float nearest=float.MaxValue;
        for(int x=-1;x<=1;x+=2)for(int y=-1;y<=1;y+=2)for(int z=-1;z<=1;z+=2)
        {
            Vector3 corner=mesh.TransformPoint(bounds.center+Vector3.Scale(bounds.extents,new Vector3(x,y,z)));
            float distance=Vector3.Dot(corner-hit.point,visibleNormal);nearest=Mathf.Min(nearest,distance);
            Check(distance>=-.00005f,"actual mesh corner does not penetrate contact plane");
        }
        Check(Mathf.Abs(nearest)<.00005f,"actual mesh face touches floor/ceiling/wall");
    }
    IEnumerator Start()
    {
        var run=Run();while(true)
        {
            object next;try{if(!run.MoveNext())break;next=run.Current;}
            catch(Exception e){Debug.LogError("SCALE_CHECKS_FAILED: "+e);UnityEditor.EditorApplication.Exit(1);yield break;}
            yield return next;
        }
        Debug.Log("SCALE_CHECKS_PASSED: all 5 scales/3 types exact metric rendered bounds, unchanged AUTO/support, free pose/control steps, fixed 1200 updates, .20/.015/.003 m overlays, reset/relocation/cancel/tracking, invalid dimensions, UI safeArea and dataset audit.");
        UnityEditor.EditorApplication.Exit(0);
    }
    IEnumerator Run()
    {
        new GameObject("Events",typeof(EventSystem),typeof(InputSystemUIInputModule)).GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
        var camera=new GameObject("Camera",typeof(Camera)).GetComponent<Camera>();camera.tag="MainCamera";
        camera.transform.position=new Vector3(0,1.5f,-2);camera.transform.rotation=Quaternion.identity;
        var provider=new GameObject("ImageAnchor").AddComponent<FakeAnchorProvider>();provider.SetTracking(AnchorTrackingState.NotAvailable);
        var root=new GameObject("AR Origin");root.SetActive(false);var origin=root.AddComponent<XROrigin>();
        var offset=new GameObject("CameraOffset");offset.transform.SetParent(root.transform,false);origin.CameraFloorOffsetObject=offset;camera.transform.SetParent(offset.transform,false);origin.Camera=camera;
        root.AddComponent<ARAnchorManager>();root.AddComponent<LuisARImageAnchor>();
        var repository=root.AddComponent<ARDatasetRepository>();var renderer=root.AddComponent<StructuralARElementRenderer>();
        var adapter=root.AddComponent<IdentityModelToARTransform>();var controller=root.AddComponent<ARStructuralElementController>();
        Set(controller,"repository",repository);Set(controller,"elementRenderer",renderer);Set(controller,"anchorProviderBehaviour",provider);Set(controller,"transformBehaviour",adapter);
        var selector=root.AddComponent<ARStructuralElementSelectionUI>();var diagrams=root.AddComponent<LuisARDiagrams>();root.AddComponent<LuisARTrackingUI>();
        root.SetActive(true);yield return null;yield return null;
        var placement=controller.SurfacePlacement;var backend=new Backend();placement.SetBackend(backend);
        var service=root.GetComponent<ARStructuralResultOverlay3D>();var ui=root.GetComponent<ARSurfacePlacementUI>();
        foreach(string id in new[]{"E1-P2-V-041","E1-P2-C-001","E2-P2-M-007"})
        {
            Check(selector.TryShowElement(id),"select priority id");
            backend.hit=new ARSurfaceHit{kind=id.Contains("-V-")?ARSurfaceKind.Ceiling:ARSurfaceKind.Floor,point=new Vector3(0,id.Contains("-V-")?5:0,0),normal=Vector3.up};
            camera.transform.position=new Vector3(0,1.5f,-2);yield return null;
            var row=controller.SelectedElement;
            Check(ARGeometryScale.TryVerifiedDimensions(row,out Vector3 real),"verified CURRENT dimensions");
            Check(placement.ScaleMode==ARGeometryScaleMode.Auto,"new ID defaults AUTO");
            int anchors=backend.anchors;
            for(int n=1;n<=5;n++)
            {
                ((Button)Field(ui,"scaleButton")).onClick.Invoke();yield return null;
                Check(placement.ScaleMode==(ARGeometryScaleMode)(n%5),"compact UI cycles five modes then AUTO");
            }
            for(int mode=0;mode<5;mode++)
            {
                Check(placement.SetScaleMode((ARGeometryScaleMode)mode),"preview scale change allowed");
                float factor=ARGeometryScale.Factor((ARGeometryScaleMode)mode,real);Dimensions(placement.Preview.transform,real*factor);
                Check(backend.anchors==anchors,"scale creates no anchor");
                Check(Mathf.Abs(placement.Preview.transform.position.y-backend.hit.point.y-(id.Contains("-V-")?-1:1)*real.y*factor*.5f)<.00001f,"immediate support at same floor/ceiling point");
                Contact(placement.Preview.transform,backend.hit,id.Contains("-V-")?Vector3.down:Vector3.up);
                if(row.type=="wall")
                {
                    var floorHit=backend.hit;
                    backend.hit=new ARSurfaceHit{kind=ARSurfaceKind.Wall,point=new Vector3(0,2,0),normal=Vector3.back};yield return null;yield return null;
                    Dimensions(placement.Preview.transform,real*factor);
                    Contact(placement.Preview.transform,backend.hit,Vector3.back);
                    Check(Mathf.Abs(Vector3.Dot(placement.Preview.transform.position-backend.hit.point,Vector3.back)-real.z*factor*.5f)<.00001f,"all five scales wall half-thickness contact");
                    backend.hit=floorHit;yield return null;yield return null;
                }
                if(mode==0)
                {
                    Check(ValidatedAutoPlacementMath.TryPose(row.type,real,backend.hit,camera.transform.position,Vector3.right,0f,out var before),"original AUTO available");
                    Check(ARSurfacePlacementMath.TryPose(row.type,real,backend.hit,camera.transform.position,Vector3.right,0f,out var after),"new AUTO available");
                    Check(before.pose.position==after.pose.position&&before.pose.rotation==after.pose.rotation&&before.scale==after.scale,"AUTO bit-identical to protected baseline");
                }
                placement.UseFreePlacement();yield return null;
                Vector3 centre=placement.Preview.transform.position;Quaternion rotation=placement.Preview.transform.rotation;
                Check(placement.SetScaleMode((ARGeometryScaleMode)mode),"free scale allowed");
                Check(placement.Preview.transform.position==centre&&placement.Preview.transform.rotation==rotation,"free scale preserves centre/orientation");
                Dimensions(placement.Preview.transform,real*factor);
                // FIX each scale so graphical amplitude/offset can be checked with
                // a non-unit returned anchor, not merely a unit test root.
                Check(placement.ConfirmAsync().Result,"FIX");yield return null;
                Check(backend.anchors==++anchors,"exactly one anchor per FIX");
                Dimensions(placement.PlacedRoot,real*factor);
                Check(!((Button)Field(ui,"scaleButton")).gameObject.activeInHierarchy,"scale control hidden after FIX");
                diagrams.Open();var buttons=(Button[])Field(diagrams,"components");
                if(!service.Requested)((Button)Field(diagrams,"overlayToggle")).onClick.Invoke();
                foreach(int component in new[]{1,2,3,4,5,0}) {buttons[component].onClick.Invoke();yield return null;Overlay(service.Current,row,component);}
                diagrams.Close();
                Check(ARSelectedElementInfo.Format(row,(ARGeometryScaleMode)mode,factor).Contains("Dimensiones mostradas:"),"dynamic scale info");
                if(mode==4)
                {
                    var member=placement.PlacedRoot;Vector3 lp=member.localPosition,ls=member.localScale;Quaternion lq=member.localRotation;
                    var graph=service.Current;var curve=(Vector3[])graph.Curve.Clone();int rays=backend.rays;
                    for(int n=0;n<400;n++)
                    {
                        camera.transform.SetPositionAndRotation(new Vector3(n*.01f,2,-2),Quaternion.Euler(n,n*17,n*3));yield return null;
                        Check(member.localPosition==lp&&member.localScale==ls&&Quaternion.Angle(member.localRotation,lq)<.001f,"fixed scale/pose 400 updates");
                        Check(!placement.SetScaleMode(ARGeometryScaleMode.Auto)&&!member.GetComponent<ARPlacementPreview>().SetScaleMode(ARGeometryScaleMode.Auto),"fixed geometry scale immutable");
                        for(int k=0;k<curve.Length;k++)Check(graph.Curve[k]==curve[k],"fixed overlay geometry immutable");
                        Check(backend.rays==rays&&backend.anchors==anchors,"fixed creates no rays/anchors");
                    }
                }
                placement.Relocate();yield return null;
                Check(placement.ScaleMode==(ARGeometryScaleMode)mode,"REUBICAR retains scale");
                var old=placement.PlacedRoot;var oldOverlay=service.Current;
                placement.SetScaleMode(ARGeometryScaleMode.OneToTen);placement.Cancel();yield return null;
                Check(placement.PlacedRoot==old&&service.Current==oldOverlay&&placement.ScaleMode==(ARGeometryScaleMode)mode,"CANCELAR restores committed scale/overlay");
                placement.Relocate();yield return null;Check(placement.ScaleMode==(ARGeometryScaleMode)mode,"second relocation committed scale");
                placement.UseSurfacePlacement();yield return null;
                if(mode==4)
                {
                    placement.RotateYaw(5);placement.RotateYaw(-5);placement.Rotate90();yield return null;
                    Dimensions(placement.Preview.transform,real);
                    if(row.type=="wall")
                    {
                        backend.hit=new ARSurfaceHit{kind=ARSurfaceKind.Wall,point=new Vector3(0,2,0),normal=Vector3.back};yield return null;
                        Check(Mathf.Abs(Vector3.Dot(placement.Preview.transform.position-backend.hit.point,Vector3.back)-.125f)<.00001f,"wall 1:1 half thickness contact");
                    }
                    Check(placement.ConfirmAsync().Result,"scaled relocation surface FIX");yield return null;
                    Check(old==null&&oldOverlay==null&&placement.ScaleMode==ARGeometryScaleMode.Real,"surface relocation transfers real scale and cleans old");
                    Dimensions(placement.PlacedRoot,real);Overlay(service.Current,row,0);
                    Contact(placement.PlacedRoot,backend.hit,row.type=="wall"?Vector3.back:row.type=="beam"?Vector3.down:Vector3.up);
                    placement.Relocate();yield return null;
                }
                backend.tracking=false;var preview=placement.Preview;centre=preview.transform.position;rotation=preview.transform.rotation;
                Vector3 ms=preview.StructuralMesh.localScale;var stored=preview.ScaleMode;yield return null;
                backend.tracking=true;yield return null;
                Check(preview.ScaleMode==stored&&preview.StructuralMesh.localScale==ms&&Quaternion.Angle(preview.transform.rotation,rotation)<.001f,"tracking preserves scale/yaw/dimensions");
                if(mode<4)backend.hit=new ARSurfaceHit{kind=id.Contains("-V-")?ARSurfaceKind.Ceiling:ARSurfaceKind.Floor,point=new Vector3(0,id.Contains("-V-")?5:0,0),normal=Vector3.up};
            }
            placement.UseFreePlacement();yield return null;
            placement.SetScaleMode(ARGeometryScaleMode.Real);
            Vector3 position=placement.Preview.transform.position;
            placement.MoveHeight(.05f);Check(Vector3.Distance(placement.Preview.transform.position-position,Vector3.up*.05f)<.00001f,"height remains 5 cm at real scale");
            placement.MoveHeight(-.05f);placement.MoveDepth(.05f);Check(Mathf.Abs(Vector3.Distance(placement.Preview.transform.position,position)-.05f)<.00001f,"depth remains 5 cm");
            placement.MoveDepth(-.05f);placement.RotateYaw(5);placement.RotateYaw(-5);placement.Rotate90();
            Check(Vector3.Distance(placement.Preview.transform.position,position)<.00001f,"yaw never alters free position");
            var frozenPreview=placement.Preview;var frozenRotation=frozenPreview.transform.rotation;
            backend.tracking=false;yield return null;backend.tracking=true;yield return null;
            Check(frozenPreview.transform.position==position&&frozenPreview.transform.rotation==frozenRotation&&frozenPreview.ScaleMode==ARGeometryScaleMode.Real,"free tracking recovery preserves pose/yaw/real scale");
            yield return null;yield return null;
            Check(((Button)Field(ui,"scaleButton")).interactable&&((Text)Field(ui,"scaleLabel")).text=="ESCALA: 1:1 REAL","scale UI enabled and current after tracking recovery");
            Check(placement.CanRotate&&((Button)Field(ui,"yawLeft")).interactable&&((Button)Field(ui,"rotate")).interactable,"free yaw controls available after surface relocation/tracking recovery");
            typeof(SurfaceChecks).GetMethod("CaptureLayout",BindingFlags.Static|BindingFlags.NonPublic).Invoke(null,new object[]{camera,selector,"scale-preview-"+row.type});
            var invalid=JsonUtility.FromJson<StructuralElementARData>(JsonUtility.ToJson(row));invalid.dimensions=null;invalid.section=null;
            var go=new GameObject("UnverifiedDimensionFixture");var fixture=go.AddComponent<ARPlacementPreview>();fixture.Configure(invalid);
            Check(!fixture.HasPhysicalDimensions&&!fixture.SetScaleMode(ARGeometryScaleMode.Real)&&fixture.ScaleMode==ARGeometryScaleMode.Auto,"physical scale refuses renderer fallback");Destroy(go);
        }
        int verified=0;foreach(var row in repository.Dataset.elements)if(ARGeometryScale.TryVerifiedDimensions(row,out _))verified++;
        Debug.Log("SCALE_DIMENSION_AUDIT: "+verified+" / "+repository.Dataset.elements.Length+" CURRENT rows have verified physical dimensions");
    }
}
