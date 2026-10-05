using System;
using System.Collections;
using System.Reflection;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using Mcoc.UnityViewer.P1L6AR;

public class ARDiagramChecks : MonoBehaviour
{
    static void Check(bool condition, string message) { if (!condition) throw new Exception(message); }
    static object Field(object target, string name) => target.GetType().GetField(name, BindingFlags.Instance | BindingFlags.NonPublic).GetValue(target);
    static void Set(object target, string name, object value) => target.GetType().GetField(name, BindingFlags.Instance | BindingFlags.NonPublic).SetValue(target, value);
    static void Equal(double a, double b, string message) => Check(Math.Abs(a-b)<1e-8,message);
    IEnumerator Start()
    {
        IEnumerator checks = Run();
        while(true)
        {
            object yielded;
            try { if (!checks.MoveNext()) break; yielded = checks.Current; }
            catch(Exception ex) { Debug.LogError("AR_DIAGRAM_CHECKS_FAILED: " + ex); UnityEditor.EditorApplication.Exit(1); yield break; }
            yield return yielded;
        }
        Debug.Log("AR_DIAGRAM_CHECKS_PASSED: A-F, all CURRENT vectors, multiple segments, missing data, tracking recovery, Input System UGUI, no transform changes.");
        UnityEditor.EditorApplication.Exit(0);
    }
    IEnumerator Run()
    {
        Screen.SetResolution(1080,1920,false);
        new GameObject("Events",typeof(EventSystem),typeof(InputSystemUIInputModule)).GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
        Transform camera = new GameObject("Camera",typeof(Camera)).transform; camera.gameObject.tag="MainCamera";
        camera.position=new Vector3(0,0,-2);
        FakeAnchorProvider provider = new GameObject("Anchor").AddComponent<FakeAnchorProvider>();
        GameObject root=new GameObject("AR"); root.SetActive(false);
        ARDatasetRepository repository=root.AddComponent<ARDatasetRepository>();
        StructuralARElementRenderer renderer=root.AddComponent<StructuralARElementRenderer>();
        IdentityModelToARTransform adapter=root.AddComponent<IdentityModelToARTransform>();
        ARStructuralElementController controller=root.AddComponent<ARStructuralElementController>();
        Set(controller,"repository",repository); Set(controller,"elementRenderer",renderer);
        Set(controller,"anchorProviderBehaviour",provider); Set(controller,"transformBehaviour",adapter);
        ARStructuralElementSelectionUI selector=root.AddComponent<ARStructuralElementSelectionUI>();
        LuisARDiagrams diagrams=root.AddComponent<LuisARDiagrams>();
        GameObject info=new GameObject("Info"); Set(diagrams,"infoPanel",info);
        root.SetActive(true); yield return null; yield return null;
        Check(repository.IsCurrent,"dataset load");
        int rows=0,segments=0,multi=0;
        foreach(var row in repository.Dataset.elements)
        {
            int count=ARCurrentDiagramData.SegmentCount(row); if(count==0) continue;
            rows++; if(count>1)multi++;
            for(int s=0;s<count;s++)
            {
                segments++;
                for(int c=0;c<6;c++)
                {
                    Check(ARCurrentDiagramData.TryValues(row,s,c,out double i,out double j),row.element_id+" valid component "+c);
                    Equal(i,row.current_result_R.segments[s].localForce_end1_N_Nm[c]/1000,"SI end i");
                    Equal(j,-row.current_result_R.segments[s].localForce_end2_N_Nm[c]/1000,"SI opposite end j");
                }
                Check(ARCurrentDiagramData.SegmentLength(row,s)>0,"FE length "+row.element_id);
            }
        }
        Check(rows==669 && multi==4,"expected CURRENT coverage");
        foreach(string id in new[]{"E1-P1-V-002","E1-P1-C-001","E2-P1-M-007"})
        {
            Check(selector.TryShowElement("  "+id.ToLowerInvariant()+"  "),"search "+id);
            diagrams.Open();
            Text title=(Text)Field(diagrams,"title");
            Check(title.text=="Diagramas · "+id,"dynamic title "+id);
            Check(!title.text.Contains("E1-P2-V-041"),"no hardcoded ID");
            Check(!info.activeSelf,"info hidden while diagrams open");
            foreach(Button button in ((GameObject)Field(diagrams,"panel")).GetComponentsInChildren<Button>())
                Check(!string.IsNullOrWhiteSpace(button.GetComponentInChildren<Text>().text),"visible button has label");
            ARForceDiagramGraphic chart=(ARForceDiagramGraphic)Field(diagrams,"graph");
            Check(chart.GetComponent<CanvasRenderer>()!=null,"graph has required CanvasRenderer");
            chart.SetAllDirty(); Canvas.ForceUpdateCanvases();
            Check(chart.canvasRenderer.GetMesh()!=null && chart.canvasRenderer.GetMesh().vertexCount>=8,"graph baseline and force line generated");
            Transform placed=renderer.RenderedTransform;
            Vector3 p=placed.localPosition,scale=placed.localScale; Quaternion rotation=placed.localRotation;
            for(int n=0;n<12;n++)
            {
                diagrams.Close(); diagrams.Open();
                camera.position=Quaternion.Euler(0,n*30,0)*new Vector3(0,0,-2);
                camera.LookAt(placed.position);
                if(n%2==0)diagrams.Close();
                provider.SetPose(new Vector3(.1f*n,0,0),Quaternion.Euler(0,n*5,0),Vector3.one);
                yield return null;
                Check(renderer.RenderedTransform==placed && placed.parent==provider.AnchorTransform,"same object and anchor");
                Check(placed.localPosition==p && placed.localScale==scale && Quaternion.Angle(placed.localRotation,rotation)<.001f,"frozen placement "+id);
            }
            diagrams.Open();
            provider.SetTracking(AnchorTrackingState.Limited); yield return null;
            Check(!((GameObject)Field(diagrams,"canvasObject")).activeSelf,"tracking hides diagrams");
            provider.SetTracking(AnchorTrackingState.Tracking); yield return null;
            Check(renderer.RenderedTransform==placed && Quaternion.Angle(placed.localRotation,rotation)<.001f,"recovery retains placement");
            diagrams.Open();
        }
        Check(!selector.TryShowElement("AAA-123"),"invalid search rejected");
        Check(controller.SelectedElement.element_id=="E2-P1-M-007" && ((Text)Field(diagrams,"title")).text.EndsWith("E2-P1-M-007"),"invalid search retains diagram");
        ARCurrentDiagramData.TryValues(controller.SelectedElement,0,0,out double wallN,out _);
        Equal(wallN,239.55929899999982,"wall actual N");
        Check(ARCurrentDiagramData.TryValues(controller.SelectedElement,0,4,out double zero,out _) && zero==0,"legitimate zero remains available");
        Equal(ARCurrentDiagramData.SegmentLength(controller.SelectedElement,0),3.96,"wall equivalent FE length not plan length");
        Check(selector.TryShowElement("E1-P3-V-112"),"multi search"); diagrams.Open();
        Button next=(Button)Field(diagrams,"next"),previous=(Button)Field(diagrams,"previous");
        Check(next.gameObject.activeSelf && next.interactable && !previous.interactable,"multiple segment controls");
        next.onClick.Invoke();
        Check((int)Field(diagrams,"segmentIndex")==1 && ((Text)Field(diagrams,"metadata")).text.Contains("Segmento 2 / 2"),"second FE segment inspectable");
        previous.onClick.Invoke(); Check((int)Field(diagrams,"segmentIndex")==0,"previous segment");
        Button[] componentButtons=(Button[])Field(diagrams,"components");
        for(int c=0;c<6;c++)
        {
            componentButtons[c].onClick.Invoke();
            Color32[] palette = { new Color32(255,45,149,255), new Color32(0,229,255,255),
                new Color32(255,212,0,255), new Color32(255,122,0,255),
                new Color32(124,255,0,255), new Color32(179,136,255,255) };
            Check(((ARForceDiagramGraphic)Field(diagrams,"graph")).color == (Color)palette[c],
                "2D exact requested component palette");
            Check(ARForceDiagramPalette.ForComponent(c) == (Color)palette[c], "2D/3D palette shared");
            Check(((Text)Field(diagrams,"values")).text.StartsWith(ARCurrentDiagramData.Components[c]+" · CASE_R"),"component button updates diagram");
        }
        var selected=controller.SelectedElement;
        var savedResult=selected.current_result_R;
        selected.current_result_R=null;
        diagrams.Open();
        Check(!((Text)Field(diagrams,"caseLabel")).gameObject.activeSelf,"missing case hidden");
        Check(((Text)Field(diagrams,"values")).text.Contains("no disponibles"),"missing result status");
        selected.current_result_R=savedResult; diagrams.Open();
        var seg=selected.current_result_R.segments[0];
        double saved=seg.localForce_end1_N_Nm[4]; seg.localForce_end1_N_Nm[4]=double.NaN;
        Check(!ARCurrentDiagramData.TryValues(selected,0,4,out double missing,out _) && double.IsNaN(missing),"missing values never fake zero");
        seg.localForce_end1_N_Nm[4]=saved;
        int tag=seg.opensees_tag; seg.opensees_tag=-1;
        Check(!ARCurrentDiagramData.TryValues(selected,0,0,out _,out _),"identity mismatch rejected"); seg.opensees_tag=tag;
        Check(ARCurrentDiagramData.Components[3]=="T" && ARCurrentDiagramData.Units(3)=="kN·m","torsion mapping");
        foreach(var row in repository.Dataset.elements)
            if(ARCurrentDiagramData.SegmentCount(row)==0 && (row.type=="beam" || row.type=="column" || row.type=="wall"))
            {
                Check(selector.TryShowElement(row.element_id),"no-result geometry still selectable"); diagrams.Open();
                Check(!((Text)Field(diagrams,"caseLabel")).gameObject.activeSelf,"unavailable case hidden");
                Check(((Text)Field(diagrams,"values")).text.Contains("no disponibles"),"no-data status"); break;
            }
        Debug.Log("Coverage: "+rows+" elements, "+segments+" FE segments, "+multi+" multi-segment elements, 6 components each.");
        Check(EventSystem.current.currentInputModule is InputSystemUIInputModule,"Input System event module");
    }
}



