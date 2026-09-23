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
            LoadPendingReview();
            LoadProjectState();
            if(pendingReviewData?.rows?.Count!=projectState?.pending)failures.Add("Pending dossier count/version");
            else foreach(var row in pendingReviewData.rows)
            {
                SelectPendingReview(row);
                if(lastSelected?.humanId!=row.id||!lastSelected.go.activeSelf)failures.Add("Pending selection "+row.id);
                if(pendingGridObjects.Count<4)failures.Add("Structural grid missing "+row.id);
                foreach(var e in allElements)if(e!=null&&e.go.activeSelf&&(e.isFeCandidateVisual||!pendingReviewIds.Contains(e.humanId??"")))failures.Add("Isolation leak "+row.id+" / "+e.id);
            }
            foreach(var resolution in new[]{new Vector2Int(1366,768),new Vector2Int(1920,1080)})
            {
                Screen.SetResolution(resolution.x,resolution.y,FullScreenMode.Windowed);yield return new WaitForSecondsRealtime(2);
                foreach(string id in new[]{"E1-P1-M-016","E1-P2-M-005","E2-P4-V-004"})
                {
                    var row=pendingReviewData?.rows?.Find(r=>r.id==id);if(row==null)continue;
                    SelectPendingReview(row);yield return new WaitForSecondsRealtime(.3f);yield return new WaitForEndOfFrame();
                    CaptureReviewFrame(Path.Combine(output,$"pending_{id}_{resolution.x}.png"));
                }
            }
            ResetPresentation();
            if(pendingReviewRow!=null||pendingGridObjects.Count!=0)failures.Add("Pending review reset");
            LoadCurrentContract();
            if(currentContract==null||currentContract.analysis_available||currentContract.status!="BLOCKED_NOT_RUN")failures.Add("Current dataset must remain unavailable until approved run");
            var expected=new CurrentDatasetContract{format="MCOC_CURRENT_DATASET_V1",geometry_version="geo",fe_version="fe",loads_version="loads",geometry_stream_sha256="file",fe_approved=true,loads_approved=true};
            var fixture=new CurrentDatasetContract{format=expected.format,geometry_version="geo",fe_version="fe",loads_version="loads",geometry_stream_sha256="file",analysis_version="run",git_commit="test",timestamp="test",status="CURRENT_VERIFIED",analysis_available=true,fe_approved=true,loads_approved=true,linear_verified=true,payload_file="test.json",payload_sha256="test",units=new CurrentDatasetUnits{length="m",force="N",moment="N.m",stress="Pa",mass="kg",rotation="rad"},cases=new List<string>{"G","Q","EX","EY","R"},basis_cases=new List<string>{"G","Q","EX","EY"}};
            if(CurrentVersionGate.Check(expected,fixture,"file")!="IDENTITY_MATCH_REQUIRES_PAYLOAD_QA")failures.Add("Valid identity gate");
            fixture.geometry_version="other";if(CurrentVersionGate.Check(expected,fixture,"file")!="GEOMETRY_MISMATCH")failures.Add("Geometry mismatch accepted");fixture.geometry_version="geo";
            fixture.fe_version="other";if(CurrentVersionGate.Check(expected,fixture,"file")!="FE_MISMATCH")failures.Add("FE mismatch accepted");fixture.fe_version="fe";
            fixture.loads_version="other";if(CurrentVersionGate.Check(expected,fixture,"file")!="LOADS_MISMATCH")failures.Add("Loads mismatch accepted");fixture.loads_version="loads";
            fixture.units.force="kN";if(CurrentVersionGate.Check(expected,fixture,"file")!="UNITS_MISMATCH")failures.Add("Unit mismatch accepted");fixture.units.force="N";
            fixture.status="HISTORICAL";if(CurrentVersionGate.Check(expected,fixture,"file")!="RESULTS_NOT_VERIFIED")failures.Add("History accepted as current");fixture.status="CURRENT_VERIFIED";
            if(CurrentVersionGate.Check(expected,fixture,"changed-file")!="GEOMETRY_FILE_MISMATCH")failures.Add("Actual geometry file mismatch accepted");
            var combined=LinearBasisResponse.Combine(new[]{new double[]{1,2},new double[]{3,4},new double[]{5,6},new double[]{7,8}},new double[]{1,2,-1,.5});
            if(System.Math.Abs(combined[0]-5.5)>1e-12||System.Math.Abs(combined[1]-8)>1e-12)failures.Add("Signed linear basis combination");
            bool nanRejected=false;try{LinearBasisResponse.Combine(new[]{new double[]{1},new double[]{2},new double[]{3},new double[]{4}},new[]{double.NaN,0,0,0});}catch(System.ArgumentException){nanRejected=true;}if(!nanRejected)failures.Add("NaN accepted");
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
            var slab=allElements.Find(e=>e!=null&&e.category=="slab");
            if(slab==null)failures.Add("Floor slab unavailable");
            else {Select(slab);ResetInspectorSections(slab);if(!CurrentSectionText(CurrentSolid(slab)).Contains("provisional"))failures.Add("Slab must disclose provisional geometry");}
            ResetPresentation();
            LoadRevisionChanges();
            if(revisionChanges==null)failures.Add("Current revision ledger/version missing");
            else foreach(var change in revisionChanges.rows)
            {
                if((change.type=="REMOVED"||change.type=="BEAM_REMOVED"||change.type=="WALL_REMOVED"||change.type=="WALL_SUPPORT_REMOVED")&&model.solids.Exists(s=>s.id==change.id))failures.Add("Excluded geometry present "+change.id);
                if(change.type=="MERGED"||change.type=="BEAM_MERGED")
                {
                    if(model.solids.FindAll(s=>s.id==change.id).Count!=1)failures.Add("Merged canonical count "+change.id);
                    foreach(var oldId in change.historical_ids)if(oldId!=change.id&&model.solids.Exists(s=>s.id==oldId))failures.Add("Merged retired ID present "+oldId);
                }
            }
            LoadColumnStacks();
            if(columnStackData==null)failures.Add("Column stacks missing/version mismatch");
            else foreach(var stack in columnStackData.stacks)
            {
                SelectColumnStack(stack);
                foreach(string id in stack.member_ids)
                    if(!allElements.Exists(e=>e!=null&&!e.isFeCandidateVisual&&e.humanId==id&&e.go.activeSelf))failures.Add("Stack column missing "+id);
                foreach(var e in allElements)if(e!=null&&e.go.activeSelf&&!stack.member_ids.Contains(e.humanId??""))failures.Add("Stack isolation leak "+e.id);
                floorVisible["S1"]=false;ReapplyAll();
                foreach(var e in allElements)if(e!=null&&e.go.activeSelf&&e.floor=="S1")failures.Add("Stack S1 toggle");
            }
            ResetPresentation();
            if(stackReviewActive)failures.Add("Stack reset");
            if(model.solids.Exists(s=>s.building=="EDIFICIO_1"&&s.category=="wall"))failures.Add("ED1 wall remained active");
            ElementInfo beam=allElements.Find(e=>e!=null&&e.category=="beam"&&e.humanId=="E2-P4-V-049");
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
                foreach(string targetId in new[]{"E2-P4-V-009","E2-P1-C-001","E2-P4-M-003","E1-P4-C-001"})
                {
                    var target=allElements.Find(e=>e!=null&&e.humanId==targetId);
                    if(target==null){failures.Add("Inspector target missing "+targetId);continue;}
                    Select(target);ResetInspectorSections(target);
                    yield return new WaitForEndOfFrame();
                    if(inspectorGroups.Count!=2||!inspectorGroups.Contains("RESUMEN")||!inspectorGroups.Contains("RESULTADOS"))failures.Add("Inspector defaults "+targetId);
                    if(selectedLocalAxisObjects.Count!=3)failures.Add("Selected axes "+targetId);
                    if(targetId=="E1-P4-C-001"&&!CurrentMaterialStatus(CurrentSolid(target)).Contains("POR CONFIRMAR"))failures.Add("Generic RC must not certify concrete grade");
                    CaptureReviewFrame(Path.Combine(output,$"inspector_{targetId}_{size.x}x{size.y}.png"));
                }
                var exampleStack=columnStackData?.stacks?.Find(s=>s.confirmed&&s.building=="EDIFICIO_1"&&s.member_ids.Count==5);
                if(exampleStack!=null)
                {
                    SelectColumnStack(exampleStack);semanticScroll=Vector2.zero;
                    yield return new WaitForEndOfFrame();
                    foreach(var e in allElements)
                    {
                        if(e==null||e.isFeCandidateVisual||!exampleStack.member_ids.Contains(e.humanId??""))continue;
                        var renderer=e.go.GetComponent<Renderer>();if(renderer==null)continue;
                        var bounds=renderer.bounds;
                        foreach(float y in new[]{bounds.min.y,bounds.max.y})
                        {
                            var screen=cam.WorldToScreenPoint(new Vector3(bounds.center.x,y,bounds.center.z));
                            if(screen.z<=0||screen.y<45||screen.y>Screen.height-82)failures.Add("Stack vertically clipped "+e.humanId);
                        }
                    }
                    CaptureReviewFrame(Path.Combine(output,$"column_stack_{size.x}x{size.y}.png"));
                }
                ResetPresentation();
                openGroups.Clear();openGroups.Add("ENTREGAS");openGroups.Add("P1L4");semanticScroll=Vector2.zero;
                yield return new WaitForEndOfFrame();
                if(ResultsAllowed||historicalResultsEnabled)failures.Add("Delivery summary enabled archive");
                CaptureReviewFrame(Path.Combine(output,$"deliveries_{size.x}x{size.y}.png"));
                openGroups.Clear();openGroups.Add("ESTADO DEL PROYECTO");
                yield return new WaitForEndOfFrame();CaptureReviewFrame(Path.Combine(output,$"state_{size.x}x{size.y}.png"));
                openGroups.Clear();openGroups.Add("MODELO");
                var materialElement=allElements.Find(e=>e!=null&&e.humanId=="E2-P1-C-001");
                if(materialElement==null)failures.Add("Material review element missing");
                else
                {
                    Select(materialElement);ResetInspectorSections(materialElement);inspectorGroups.Add("PROPIEDADES");
                    var materialSolid=CurrentSolid(materialElement);
                    if(materialSolid==null||materialSolid.concrete_fc_pa!=35000000||materialSolid.material_confidence!="CONFIRMED_FROM_PLAN")failures.Add("Primary material missing");
                    if(string.IsNullOrEmpty(materialElement.correctionType)||!materialElement.correctionType.Contains("PROPERTY_UPDATED"))failures.Add("Property correction filter trace missing");
                    yield return new WaitForEndOfFrame();CaptureReviewFrame(Path.Combine(output,$"material_{size.x}x{size.y}.png"));
                    technicalDetail=false;
                }
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
            string report=failures.Count==0?"PASS: current model; archived layers blocked; beam/column/wall/slab inspector; summary/results defaults; current identity negative gates; signed basis/NaN tests; building/floor filters; 1366x768 and 1920x1080; non-overlapping panels; local axes; historical opt-in; presentation isolation; fullscreen.":"FAIL: "+string.Join("; ",failures);
            File.WriteAllText(Path.Combine(output,"UX_QA.txt"),report);
            Debug.Log("[UX REVIEW QA] "+report);
        }
    }
}
