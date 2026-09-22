using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    public partial class ViewerController
    {
        static void CaptureReviewFrame(string path)
        {
            var frame=new Texture2D(Screen.width,Screen.height,TextureFormat.RGB24,false);
            frame.ReadPixels(new Rect(0,0,Screen.width,Screen.height),0,0);frame.Apply();
            File.WriteAllBytes(path,frame.EncodeToPNG());Destroy(frame);
        }
        IEnumerator RunUxReview()
        {
            string output=Path.Combine(Application.dataPath,"..","QA");Directory.CreateDirectory(output);
            var failures=new List<string>();
            LoadProjectState();
            if(projectState==null||projectState.deliveries==null||projectState.deliveries.Count!=4)failures.Add("Delivery metadata missing");
            if(projectState!=null&&projectState.geometry_count!=model.solids.Count)failures.Add("Metadata geometry mismatch");
            ResetPresentation();
            // Try to activate every archived layer without opting in: none may render.
            foreach(string key in new List<string>(typeVisible.Keys))if(IsHistoricalLayer(key))typeVisible[key]=true;
            ReapplyAll();
            foreach(var pair in byType)if(IsHistoricalLayer(pair.Key))foreach(var go in pair.Value)if(go!=null&&go.activeSelf)failures.Add("Historical leak "+pair.Key);
            ResetPresentation();
            buildingVisible["EDIFICIO_2"]=false;ReapplyAll();
            foreach(var e in allElements)if(e!=null&&e.building=="EDIFICIO_2"&&e.go.activeSelf)failures.Add("Building filter "+e.id);
            ResetPresentation();floorVisible["P2"]=false;ReapplyAll();
            foreach(var go in byFloor["P2"])if(go.activeSelf)failures.Add("Floor filter");
            ResetPresentation();
            ElementInfo beam=allElements.Find(e=>e!=null&&e.category=="beam"&&e.humanId=="E1-P2-V-075");
            if(beam==null)failures.Add("Review beam missing");
            foreach(var size in new[]{new Vector2Int(1366,768),new Vector2Int(1920,1080)})
            {
                Screen.SetResolution(size.x,size.y,FullScreenMode.Windowed);
                yield return new WaitForSecondsRealtime(2);
                ResetPresentation();if(beam!=null)Select(beam);
                localAxesVisible=true;RebuildCurrentLocalAxes();SetGlobalAxesVisible(true);
                yield return new WaitForEndOfFrame();
                if(Screen.width!=size.x||Screen.height!=size.y)failures.Add($"Resolution requested {size}, actual {Screen.width}x{Screen.height}");
                if(SemanticPanelRect().Overlaps(CurrentInspectorRect())||CurrentInspectorRect().Overlaps(OrientationRect()))failures.Add("Panel overlap");
                if(CurrentInspectorRect().yMax>Screen.height-36||SemanticPanelRect().yMax>Screen.height-36)failures.Add("Panel clipped");
                if(selectedLocalAxisObjects.Count!=3)failures.Add("Local axes missing");
                CaptureReviewFrame(Path.Combine(output,$"current_{size.x}x{size.y}.png"));
                openGroups.Clear();openGroups.Add("ENTREGAS");openGroups.Add("P1L4");semanticScroll=Vector2.zero;
                yield return new WaitForEndOfFrame();
                if(ResultsAllowed||historicalResultsEnabled)failures.Add("Delivery summary enabled archive");
                CaptureReviewFrame(Path.Combine(output,$"deliveries_{size.x}x{size.y}.png"));
                openGroups.Clear();openGroups.Add("ESTADO DEL PROYECTO");
                yield return new WaitForEndOfFrame();CaptureReviewFrame(Path.Combine(output,$"state_{size.x}x{size.y}.png"));
                openGroups.Clear();openGroups.Add("MODELO");
                SetHistoricalResults(true);ActivateAnalysisCase("R");
                var archivedBeam=allElements.Find(e=>e!=null&&e.category=="beam"&&analysisByElementId.ContainsKey(e.humanId??e.id));
                if(archivedBeam==null)failures.Add("Archived beam missing");
                else
                {
                    Select(archivedBeam);SetDiagramMode(1);diagram2DVisible=true;
                    yield return new WaitForEndOfFrame();
                    if(CurrentPlotRect().Overlaps(CurrentInspectorRect())||CurrentPlotRect().Overlaps(SemanticPanelRect()))failures.Add("Historic plot overlap");
                    CaptureReviewFrame(Path.Combine(output,$"historical_My_{size.x}x{size.y}.png"));
                    SetDiagramMode(3);yield return new WaitForEndOfFrame();
                    CaptureReviewFrame(Path.Combine(output,$"historical_N_{size.x}x{size.y}.png"));
                }
                var capacityColumn=FindSelectableCapacityElement("column");
                if(capacityColumn==null)failures.Add("Archived capacity column missing");
                else
                {
                    Select(capacityColumn);diagram2DVisible=false;demandCapacityPlotVisible=true;
                    yield return new WaitForEndOfFrame();CaptureReviewFrame(Path.Combine(output,$"historical_PM_{size.x}x{size.y}.png"));
                }
                SetHistoricalResults(false);
                yield return new WaitForSecondsRealtime(1);
            }
            SetHistoricalResults(true);typeVisible["tributary"]=true;ReapplyAll();
            if(!byType["tributary"].Exists(go=>go.activeSelf))failures.Add("History opt-in unavailable");
            SetPresentationMode(true);
            yield return new WaitForSecondsRealtime(2);
            if(ResultsAllowed||historicalResultsEnabled||navigationExpanded)failures.Add("Presentation isolation");
            foreach(var pair in byType)if(IsHistoricalLayer(pair.Key))foreach(var go in pair.Value)if(go!=null&&go.activeSelf)failures.Add("Presentation historic leak");
            if(!Application.isEditor&&!Screen.fullScreen)failures.Add("Fullscreen unavailable");
            yield return new WaitForEndOfFrame();CaptureReviewFrame(Path.Combine(output,"presentation.png"));
            yield return new WaitForSecondsRealtime(1);
            SetPresentationMode(false);ResetPresentation();SetGlobalAxesVisible(false);
            string report=failures.Count==0?"PASS: current model; archived layers blocked; building/floor filters; 1366x768 and 1920x1080; non-overlapping panels; local axes; historical opt-in; presentation isolation; fullscreen.":"FAIL: "+string.Join("; ",failures);
            File.WriteAllText(Path.Combine(output,"UX_QA.txt"),report);
            Debug.Log("[UX REVIEW QA] "+report);
        }
    }
}
