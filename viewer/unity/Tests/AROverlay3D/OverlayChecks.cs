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

public class OverlayChecks : MonoBehaviour
{
    sealed class Backend : IARSurfacePlacementBackend
    {
        public int creations,raycasts;
        public ARSurfaceHit hit=new ARSurfaceHit{kind=ARSurfaceKind.Ceiling,point=new Vector3(0,3,0),normal=Vector3.up};
        public bool IsTracking=>true;
        public bool TryHit(out ARSurfaceHit value) {raycasts++;value=hit;return true;}
        public Task<Transform> CreateAnchorAsync(Pose pose)
        {
            creations++;
            Transform a=new GameObject("OverlayTestAnchor").transform;
            a.SetPositionAndRotation(pose.position+Vector3.right*.02f,Quaternion.Euler(0,13,0)*pose.rotation);
            a.localScale=Vector3.one*2;
            return Task.FromResult(a);
        }
        public bool IsAnchorTracked(Transform a)=>a!=null;
        public void RemoveAnchor(Transform a){if(a!=null)UnityEngine.Object.Destroy(a.gameObject);}
    }
    static object Field(object target,string name)=>target.GetType().GetField(name,BindingFlags.Instance|BindingFlags.NonPublic).GetValue(target);
    static void Set(object target,string name,object value)=>target.GetType().GetField(name,BindingFlags.Instance|BindingFlags.NonPublic).SetValue(target,value);
    static void Check(bool value,string why){if(!value)throw new Exception(why);}
    static void Same(Transform t,Vector3 p,Quaternion r,Vector3 s,string why)
    {Check(t.localPosition==p&&Quaternion.Angle(t.localRotation,r)<.001f&&t.localScale==s,why);}
    static void Capture(Camera camera,ARStructuralElementSelectionUI selector,string name)
    {typeof(SurfaceChecks).GetMethod("CaptureLayout",BindingFlags.Static|BindingFlags.NonPublic).Invoke(null,new object[]{camera,selector,name});}
    static void CaptureComponent(Camera camera, ARStructuralElementSelectionUI selector, LuisARDiagrams diagrams,
        Transform member, string type, int component)
    {
        if (Array.IndexOf(Environment.GetCommandLineArgs(), "-uiScreenshots") < 0) return;
        camera.transform.position = member.position - member.forward * 1.6f + member.right * .35f;
        camera.transform.LookAt(member.position);
        Capture(camera, selector, "palette-" + type + "-" + ARCurrentDiagramData.Components[component] + "-panel");
        diagrams.Close();
        Capture(camera, selector, "palette-" + type + "-" + ARCurrentDiagramData.Components[component] + "-member");
        diagrams.Open();
    }
    static void Values(ARForceDiagram3DRenderer renderer,StructuralElementARData row,int segment,int component)
    {
        Check(ARCurrentDiagramData.TryValues(row,segment,component,out double i,out double j),"CURRENT values available");
        Check(renderer.Segment==segment&&renderer.Component==component&&renderer.EndI==i&&renderer.EndJ==j,"exact same i/j as 2D");
        Color expectedColor = ARForceDiagramPalette.ForComponent(component);
        foreach (var line in renderer.GetComponentsInChildren<LineRenderer>())
        {
            Check(line.sharedMaterial.color == expectedColor, "3D shared component palette, opaque outline");
            Check(line.sharedMaterial.shader.name == "MCOC/ARForceOverlay", "existing Unlit shader");
        }
        expectedColor.a = .35f;
        Check(renderer.GetComponentInChildren<MeshRenderer>().sharedMaterial.color == expectedColor,
            "translucent ribbon contrast");
        double max=Math.Max(Math.Abs(i),Math.Abs(j));
        bool vertical=row.type!="beam";
        Vector3 axis=component==2||component==5?Vector3.forward:(vertical?Vector3.right:Vector3.up);
        float localAmplitude=.20f/renderer.transform.parent.TransformVector(axis).magnitude;
        var curve=renderer.Curve;
        for(int n=0;n<curve.Length;n++)
        {
            float t=vertical?(curve[n].y-renderer.BaseI.y)/(renderer.BaseJ.y-renderer.BaseI.y):
                (curve[n].x-renderer.BaseI.x)/(renderer.BaseJ.x-renderer.BaseI.x);
            float expected=max==0?0:(float)((1-t)*(i/max)+t*(j/max))*localAmplitude;
            Vector3 baseline=Vector3.Lerp(renderer.BaseI,renderer.BaseJ,t);
            Check(Vector3.Distance(curve[n],baseline+axis*expected)<1e-5f,"signed linear interpolation, no parabola");
        }
        Transform mesh=renderer.transform.parent.GetComponent<ARPlacementPreview>().StructuralMesh;
        bool horizontal=component==2||component==5;
        foreach(Vector3 point in curve)
            Check(horizontal?(vertical?point.x > mesh.localScale.x*.5f:point.y < -mesh.localScale.y*.5f):
                point.z < -mesh.localScale.z*.5f,"diagram stays outside member for either sign");
        if(vertical)
        {
            Check(renderer.BaseI.x==renderer.BaseJ.x&&renderer.BaseI.z==renderer.BaseJ.z,"COLUMN/WALL base parallel to local Y");
            Check(ARVerticalResultMapping.TryRange(row,segment,out float from,out float to,out _),"vertical range valid");
            Check(Mathf.Abs(Mathf.Abs(renderer.BaseJ.y-renderer.BaseI.y)-mesh.localScale.y*Mathf.Abs(to-from))<1e-5f,"dataset FE span occupies actual rendered height fraction");
        }
        foreach(LineRenderer line in renderer.GetComponentsInChildren<LineRenderer>())
            Check(!line.useWorldSpace&&line.alignment==LineAlignment.TransformZ,"fixed line alignment, no billboard");
    }
    static void BeamRegression(ARForceDiagram3DRenderer current,StructuralElementARData row,Transform mesh,int component)
    {
        var go=new GameObject("ValidatedBeamBaseline");go.transform.SetParent(current.transform.parent,false);
        var baseline=go.AddComponent<ValidatedBeamDiagram3DRenderer>();
        Check(baseline.Render(row,mesh,0,component),"original BEAM renders");
        Check(current.BaseI==baseline.BaseI&&current.BaseJ==baseline.BaseJ&&current.EndI==baseline.EndI&&current.EndJ==baseline.EndJ,"BEAM exact unchanged bases and values");
        Check(current.Curve.Length==baseline.Curve.Length,"BEAM stations unchanged");
        for(int n=0;n<current.Curve.Length;n++)Check(current.Curve[n]==baseline.Curve[n],"BEAM exact unchanged signed geometry");
        foreach(var line in current.GetComponentsInChildren<LineRenderer>())
        {
            var old=baseline.transform.Find(line.name).GetComponent<LineRenderer>();
            Check(line.transform.localRotation==old.transform.localRotation&&line.widthMultiplier==old.widthMultiplier&&
                line.positionCount==old.positionCount,"BEAM line frame/width unchanged; palette checked separately");
            for(int n=0;n<line.positionCount;n++)Check(line.GetPosition(n)==old.GetPosition(n),"BEAM line vertices unchanged");
        }
        var a=current.GetComponentInChildren<MeshFilter>().sharedMesh;var b=baseline.GetComponentInChildren<MeshFilter>().sharedMesh;
        Check(a.vertexCount==b.vertexCount&&a.triangles.Length==b.triangles.Length,"BEAM ribbon unchanged");
        for(int n=0;n<a.vertexCount;n++)Check(a.vertices[n]==b.vertices[n],"BEAM ribbon vertices identical");
        for(int n=0;n<a.triangles.Length;n++)Check(a.triangles[n]==b.triangles[n],"BEAM ribbon triangles identical");
        go.SetActive(false);Destroy(go);
    }
    IEnumerator Start()
    {
        IEnumerator run=Run();
        while(true)
        {
            object next;
            try {if(!run.MoveNext())break;next=run.Current;}
            catch(Exception e){Debug.LogError("OVERLAY_CHECKS_FAILED: "+e);UnityEditor.EditorApplication.Exit(1);yield break;}
            yield return next;
        }
        Debug.Log("OVERLAY_CHECKS_PASSED: exact BEAM baseline geometry all six components/all 446 mappings, COLUMN/WALL six components, 1200 fixed updates, free/wall placement, relocation/cancel/type change, vertical split fixtures/zero crossing, ambiguous rejection, CURRENT audit and 2D persistence.");
        UnityEditor.EditorApplication.Exit(0);
    }
    IEnumerator Run()
    {
        new GameObject("Events",typeof(EventSystem),typeof(InputSystemUIInputModule)).GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
        Camera camera=new GameObject("Camera",typeof(Camera)).GetComponent<Camera>();camera.tag="MainCamera";
        camera.transform.position=new Vector3(0,1.5f,-2);camera.transform.LookAt(new Vector3(0,3,0));
        var provider=new GameObject("ImageAnchor").AddComponent<FakeAnchorProvider>();provider.SetTracking(AnchorTrackingState.NotAvailable);
        var root=new GameObject("AR Origin");root.SetActive(false);
        var origin=root.AddComponent<XROrigin>();
        var offset=new GameObject("CameraOffset");offset.transform.SetParent(root.transform,false);
        origin.CameraFloorOffsetObject=offset;camera.transform.SetParent(offset.transform,false);origin.Camera=camera;
        root.AddComponent<ARAnchorManager>();root.AddComponent<LuisARImageAnchor>();
        var repository=root.AddComponent<ARDatasetRepository>();var renderer=root.AddComponent<StructuralARElementRenderer>();
        var adapter=root.AddComponent<IdentityModelToARTransform>();var controller=root.AddComponent<ARStructuralElementController>();
        Set(controller,"repository",repository);Set(controller,"elementRenderer",renderer);Set(controller,"anchorProviderBehaviour",provider);Set(controller,"transformBehaviour",adapter);
        var selector=root.AddComponent<ARStructuralElementSelectionUI>();var diagrams=root.AddComponent<LuisARDiagrams>();root.AddComponent<LuisARTrackingUI>();
        root.SetActive(true);yield return null;yield return null;
        var placement=controller.SurfacePlacement;var backend=new Backend();placement.SetBackend(backend);
        var overlay=root.GetComponent<ARStructuralResultOverlay3D>();
        Check(overlay!=null,"overlay installed automatically");
        Check(selector.TryShowElement("E1-P2-V-041"),"beam P2 selected");yield return null;
        Check(!overlay.CanShow(out _) && overlay.Current==null,"preview cannot get overlay or new anchor");
        placement.Rotate90();yield return null;
        Check(placement.ConfirmAsync().Result,"fixed beam under ceiling");yield return null;
        var member=placement.PlacedRoot;var mesh=member.GetComponent<ARPlacementPreview>().StructuralMesh;
        Vector3 p=member.localPosition,s=member.localScale,mp=mesh.localPosition,ms=mesh.localScale;
        Quaternion q=member.localRotation,mq=mesh.localRotation;
        diagrams.Open();yield return null;
        ((Button)Field(diagrams,"overlayToggle")).onClick.Invoke();yield return null;
        Check(overlay.Current!=null && overlay.Current.transform.parent==member && overlay.Current.name=="ResultOverlay3D","A overlay is member child");
        Values(overlay.Current,controller.SelectedElement,0,4);
        BeamRegression(overlay.Current,controller.SelectedElement,mesh,4);
        var original=overlay.Current;Vector3 op=original.transform.localPosition,os=original.transform.localScale;Quaternion oq=original.transform.localRotation;
        Check(op==Vector3.zero&&os==Vector3.one&&oq==Quaternion.identity,"overlay identity local pose");
        Capture(camera,selector,"overlay-panel");diagrams.Close();yield return null;
        // Fixture camera moved solely to make an unobstructed view of a fixed 3D object.
        camera.transform.position=member.position+member.right*.12f-member.forward*1.6f-member.up*.4f;
        camera.transform.LookAt(member.position);
        Capture(camera,selector,"overlay-member");
        int anchors=backend.creations,raycasts=backend.raycasts;
        Vector3[] curve=(Vector3[])original.Curve.Clone();
        for(int n=0;n<400;n++)
        {
            camera.transform.SetPositionAndRotation(new Vector3(n*.01f,1,-2),Quaternion.Euler(n%110,n*17,n%80));
            backend.hit.point=new Vector3(n,4,2);provider.SetPose(new Vector3(n,2,1),camera.transform.rotation,Vector3.one);
            yield return null;
            Same(member,p,q,s,"B member unchanged");Same(original.transform,op,oq,os,"B overlay local pose unchanged");
            Same(mesh,mp,mq,ms,"base mesh unchanged");
            Check(backend.creations==anchors&&backend.raycasts==raycasts,"overlay has no anchors or raycasts");
            for(int k=0;k<curve.Length;k++)Check(original.Curve[k]==curve[k],"no geometry recalculation with camera");
        }
        diagrams.Open();
        Button[] buttons=(Button[])Field(diagrams,"components");
        for(int c=0;c<6;c++) {buttons[c].onClick.Invoke();Values(overlay.Current,controller.SelectedElement,0,c);BeamRegression(overlay.Current,controller.SelectedElement,mesh,c);Same(member,p,q,s,"C component does not move member");yield return null;CaptureComponent(camera,selector,diagrams,member,"beam",c);}
        ((Button)Field(diagrams,"overlayToggle")).onClick.Invoke();yield return null;
        Check(!overlay.Requested&&overlay.Current==null&&original==null,"D hide removes overlay only");Same(member,p,q,s,"hide preserves member");
        ((Button)Field(diagrams,"overlayToggle")).onClick.Invoke();yield return null;
        original=overlay.Current;placement.Relocate();yield return null;
        Check(overlay.Current==original,"old overlay remains in relocation preview");placement.Cancel();yield return null;
        Check(overlay.Current==original&&placement.PlacedRoot==member,"F cancel keeps original overlay");
        placement.Relocate();backend.hit=new ARSurfaceHit{kind=ARSurfaceKind.Floor,point=Vector3.zero,normal=Vector3.up};
        camera.transform.position=new Vector3(0,1,-2);camera.transform.rotation=Quaternion.identity;yield return null;
        Check(placement.ConfirmAsync().Result,"E relocation to floor");yield return null;
        Check(member==null && original==null && overlay.Current!=null&&overlay.Current.transform.parent==placement.PlacedRoot,"new root recreates overlay and cleans old");
        Check(overlay.Current.Component==5,"relocation retains component");Values(overlay.Current,controller.SelectedElement,0,5);
        original=overlay.Current;member=placement.PlacedRoot;
        selector.ExpandSearch();Check(!selector.TryShowElement("AAA-123"),"H invalid ID rejected");yield return null;
        Check(member==placement.PlacedRoot&&original==overlay.Current,"invalid ID keeps overlay and element");
        Check(selector.TryShowElement("E1-P3-V-112"),"G multi beam selected");yield return null;
        Check(overlay.Current==original&&placement.PlacedRoot==member,"old overlay kept until new fix");
        Check(placement.ConfirmAsync().Result,"new multi beam fixed");yield return null;
        Check(member==null&&original==null&&overlay.Current.transform.parent==placement.PlacedRoot,"no orphan overlays after ID change");
        diagrams.Open();yield return null;
        Check(ARForceDiagram3DRenderer.TrySegmentRange(controller.SelectedElement,0,out float a,out float b)&&Mathf.Abs(a)<1e-6f&&Mathf.Abs(b-2.2f/4.25f)<1e-5f,"first FE segment physically mapped");
        ((Button)Field(diagrams,"next")).onClick.Invoke();
        Values(overlay.Current,controller.SelectedElement,1,5);
        Check(ARForceDiagram3DRenderer.TrySegmentRange(controller.SelectedElement,1,out a,out b)&&Mathf.Abs(a-2.2f/4.25f)<1e-5f&&Mathf.Abs(b-1)<1e-6f,"second segment uses remaining physical span");
        ((Button)Field(diagrams,"previous")).onClick.Invoke();Values(overlay.Current,controller.SelectedElement,0,5);
        original=overlay.Current;op=original.transform.localPosition;oq=original.transform.localRotation;os=original.transform.localScale;
        for(int n=0;n<5;n++)
        {
            diagrams.Close();Check(!((GameObject)Field(diagrams,"overlayActions")).activeSelf,"overlay UI closes immediately");yield return null;
            diagrams.Open();Check(((GameObject)Field(diagrams,"overlayActions")).activeSelf,"overlay UI opens immediately");yield return null;
            Check(overlay.Current==original,"J open/close does not rebuild overlay");Same(original.transform,op,oq,os,"J pose invariant");
        }
        // Edge cases modify only a detached fixture copy, never the repository.
        var copy=JsonUtility.FromJson<StructuralElementARData>(JsonUtility.ToJson(controller.SelectedElement));
        int ni=copy.current_result_R.segments[0].node_i,nj=copy.current_result_R.segments[0].node_j;
        copy.current_result_R.segments[0].node_i=nj;copy.current_result_R.segments[0].node_j=ni;
        Check(ARForceDiagram3DRenderer.TrySegmentRange(copy,0,out a,out b)&&a>b,"reversed i/j preserves spatial order");
        copy.current_result_R.segments[0].localForce_end1_N_Nm[0]=0;copy.current_result_R.segments[0].localForce_end2_N_Nm[0]=0;
        Check(original.Render(copy,placement.PlacedRoot.GetComponent<ARPlacementPreview>().StructuralMesh,0,0),"zero forces render without invented values");Values(original,copy,0,0);
        copy.current_result_R.segments[0].localForce_end1_N_Nm[0]=double.NaN;
        Check(!original.Render(copy,mesh,0,0),"nonfinite data rejected");
        copy=JsonUtility.FromJson<StructuralElementARData>(JsonUtility.ToJson(controller.SelectedElement));
        copy.current_result_R.segments[0].localForce_end1_N_Nm=null;
        Check(!original.Render(copy,placement.PlacedRoot.GetComponent<ARPlacementPreview>().StructuralMesh,0,0),"missing force data is not replaced by zero");
        copy.current_result_R.node_displacements=null;
        Check(!ARForceDiagram3DRenderer.TrySegmentRange(copy,0,out _,out _),"missing coordinates are not invented");
        copy=JsonUtility.FromJson<StructuralElementARData>(JsonUtility.ToJson(controller.SelectedElement));
        foreach(var node in copy.current_result_R.node_displacements)
            if(node.node_tag==copy.current_result_R.segments[0].node_j)node.model_coord_m[1]+=.5;
        Check(!ARForceDiagram3DRenderer.TrySegmentRange(copy,0,out _,out _),"skew FE mapping rejected rather than invented");
        int mapped=0,total=0;
        foreach(var row in repository.Dataset.elements)
            if(row.type=="beam")for(int n=0;n<ARCurrentDiagramData.SegmentCount(row);n++)
            {
                total++;bool valid=ARForceDiagram3DRenderer.TrySegmentRange(row,n,out float from,out float to);
                Check(valid==ValidatedBeamDiagram3DRenderer.TrySegmentRange(row,n,out float oldFrom,out float oldTo)&&from==oldFrom&&to==oldTo,"all BEAM ranges unchanged");
                if(valid)mapped++;
            }
        Debug.Log("OVERLAY_MAPPING_AUDIT: "+mapped+" / "+total+" beam FE segments have unambiguous longitudinal mapping");
        foreach(string id in new[]{"E1-P2-C-001","E2-P2-M-007"})
        {
            original=overlay.Current;member=placement.PlacedRoot;
            Check(selector.TryShowElement(id),"nonbeam selection unchanged");yield return null;
            Check(overlay.Current==original,"type change preview preserves previous overlay");
            placement.UseFreePlacement();yield return null;
            Check(placement.ConfirmAsync().Result,"nonbeam placement unchanged");yield return null;
            diagrams.Open();yield return null;
            Check(member==null&&original==null&&overlay.Current!=null,"type change cleans old root/overlay");
            Check(overlay.CanShow(out string reason)&&!reason.Contains("actualmente para BEAM"),"vertical overlay supported");
            Check(overlay.Requested&&((Button)Field(diagrams,"overlayToggle")).interactable,"overlay intent persists between types");
            Check(((Text)Field(diagrams,"values")).text.Contains("CASE_R"),"nonbeam 2D still works");
            if(id.Contains("-M-"))Check(reason.Contains("segmento FE equivalente"),"wall equivalent-line notice");
            for(int c=0;c<6;c++) {buttons[c].onClick.Invoke();Values(overlay.Current,controller.SelectedElement,0,c);yield return null;CaptureComponent(camera,selector,diagrams,placement.PlacedRoot,controller.SelectedElement.type,c);}
            buttons[4].onClick.Invoke();yield return null;
            Capture(camera,selector,id.Contains("-M-")?"wall-overlay-panel":"column-overlay-panel");
            original=overlay.Current;member=placement.PlacedRoot;
            p=member.localPosition;q=member.localRotation;s=member.localScale;
            curve=(Vector3[])original.Curve.Clone();anchors=backend.creations;raycasts=backend.raycasts;
            for(int n=0;n<400;n++)
            {
                camera.transform.SetPositionAndRotation(new Vector3(n*.01f,1,-2),Quaternion.Euler(n%110,n*17,n%80));yield return null;
                Same(member,p,q,s,"vertical member stable during 400 updates");
                Same(original.transform,Vector3.zero,Quaternion.identity,Vector3.one,"vertical overlay local pose fixed");
                for(int k=0;k<curve.Length;k++)Check(original.Curve[k]==curve[k],"vertical geometry fixed");
                Check(backend.creations==anchors&&backend.raycasts==raycasts,"no overlay anchors/raycasts");
            }
            placement.Relocate();yield return null;Check(overlay.Current==original,"vertical relocation preserves overlay");
            placement.Cancel();yield return null;Check(overlay.Current==original,"vertical cancel preserves same overlay instance");
            placement.Relocate();yield return null;
            if(id.Contains("-M-"))
            {
                placement.UseSurfacePlacement();backend.hit=new ARSurfaceHit{kind=ARSurfaceKind.Wall,point=new Vector3(0,1,1),normal=Vector3.back};
                camera.transform.position=new Vector3(0,1,-2);camera.transform.rotation=Quaternion.identity;yield return null;
            }
            Check(placement.ConfirmAsync().Result,"vertical relocation fixes free or wall surface");yield return null;
            Check(member==null&&original==null&&overlay.Current.Component==4,"vertical relocation cleanup and component persistence");
            Values(overlay.Current,controller.SelectedElement,0,4);
            Capture(camera,selector,id.Contains("-M-")?"wall-surface-overlay":"column-relocated-overlay");
            Check(FindObjectsByType<ARForceDiagram3DRenderer>(FindObjectsSortMode.None).Length==1,"no orphan overlays");
            var verticalCopy=JsonUtility.FromJson<StructuralElementARData>(JsonUtility.ToJson(controller.SelectedElement));
            var nodes=verticalCopy.current_result_R.node_displacements;
            nodes[1].model_coord_m[0]+=.5;
            Check(!ARVerticalResultMapping.TryRange(verticalCopy,0,out _,out _,out _),"skew vertical FE rejected");
            nodes[1].model_coord_m[0]-=.5;nodes[1].model_coord_m[2]=verticalCopy.geometry.z_top_m+1;
            Check(!ARVerticalResultMapping.TryRange(verticalCopy,0,out _,out _,out _),"outside physical height rejected");
            verticalCopy.current_result_R.node_displacements=null;
            Check(!ARVerticalResultMapping.TryRange(verticalCopy,0,out _,out _,out _),"missing FE coordinates rejected");
            // Synthetic split fixture exercises fractions and selection without
            // adding results to the repository (current vertical rows are single-segment).
            verticalCopy=JsonUtility.FromJson<StructuralElementARData>(JsonUtility.ToJson(controller.SelectedElement));
            nodes=verticalCopy.current_result_R.node_displacements;
            var midpoint=JsonUtility.FromJson<ARNodeDisplacement>(JsonUtility.ToJson(nodes[0]));
            midpoint.node_tag=999999;midpoint.model_coord_m[2]=(verticalCopy.geometry.z_bottom_m+verticalCopy.geometry.z_top_m)*.5;
            verticalCopy.current_result_R.node_displacements=new[]{nodes[0],midpoint,nodes[1]};
            verticalCopy.fe_node_tags=new[]{nodes[0].node_tag,midpoint.node_tag,nodes[1].node_tag};
            var first=verticalCopy.current_result_R.segments[0];
            var second=JsonUtility.FromJson<ARResultSegment>(JsonUtility.ToJson(first));
            first.node_j=midpoint.node_tag;second.node_i=midpoint.node_tag;
            verticalCopy.current_result_R.segments=new[]{first,second};
            for(int n=0;n<2;n++)
            {
                overlay.SelectDiagram(verticalCopy,n,4);
                Check(overlay.Current!=null&&overlay.Current.Segment==n,"vertical selected segment updates overlay");
                Values(overlay.Current,verticalCopy,n,4);
                Check(ARVerticalResultMapping.TryRange(verticalCopy,n,out a,out b,out _)&&Mathf.Abs(a-n*.5f)<1e-6f&&Mathf.Abs(b-(n+1)*.5f)<1e-6f,"vertical subsegments map only their span");
                yield return null;
            }
            first.localForce_end1_N_Nm[4]=1000;first.localForce_end2_N_Nm[4]=1000;
            Check(overlay.Current.Render(verticalCopy,placement.PlacedRoot.GetComponent<ARPlacementPreview>().StructuralMesh,0,4),"synthetic sign-changing vertical force renders");
            Values(overlay.Current,verticalCopy,0,4);
            bool zero=false;
            foreach(var point in overlay.Current.Curve)
                if(Mathf.Abs(point.x-overlay.Current.BaseI.x)<1e-6f&&Mathf.Abs(point.y-(overlay.Current.BaseI.y+overlay.Current.BaseJ.y)*.5f)<1e-6f)zero=true;
            Check(zero,"vertical zero crossing explicitly sampled");
            verticalCopy.current_result_R.node_displacements=new[]{nodes[0],nodes[0],nodes[1]};
            Check(!ARVerticalResultMapping.TryRange(verticalCopy,0,out _,out _,out _),"ambiguous duplicate FE coordinate rejected");
            overlay.SelectDiagram(controller.SelectedElement,0,4);
        }
        foreach(string type in new[]{"column","wall"})
        {
            mapped=total=0;int multi=0;
            foreach(var row in repository.Dataset.elements)if(row.type==type)
            {
                if(ARCurrentDiagramData.SegmentCount(row)>1)multi++;
                for(int n=0;n<ARCurrentDiagramData.SegmentCount(row);n++)
                {
                    total++;if(ARVerticalResultMapping.TryRange(row,n,out _,out _,out string reason)&&ARCurrentDiagramData.TryValues(row,n,0,out _,out _))mapped++;
                    else Debug.Log("VERTICAL_MAPPING_REJECTED: "+row.element_id+" segment "+n+" "+reason);
                }
            }
            Debug.Log("VERTICAL_MAPPING_AUDIT: "+type+" "+mapped+" / "+total+"; multi-segment elements="+multi);
        }
        Check(selector.TryShowElement("E2-P4-C-008"),"ambiguous real column still selectable");yield return null;
        placement.UseFreePlacement();yield return null;
        Check(placement.ConfirmAsync().Result,"ambiguous FE column physical placement unchanged");yield return null;
        diagrams.Open();yield return null;
        Check(overlay.Current==null&&!overlay.Requested&&!overlay.CanShow(out string unavailable)&&unavailable.Contains("no vertical"),"ambiguous column clearly rejected for 3D only");
        Check(((Text)Field(diagrams,"values")).text.Contains("CASE_R"),"ambiguous column retains 2D values");
    }
}
