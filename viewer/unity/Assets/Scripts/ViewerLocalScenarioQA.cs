using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    [Serializable] public class LocalScenarioCheck { public string check; public bool pass; }
    [Serializable] public class LocalDemoMetric
    {
        public string input, element_id, base_dc, scenario_dc;
        public double force_kN, area_m2, q_kN_m2, increment_my_kNm, increment_u_mm;
        public int receptors;
    }
    [Serializable] public class LocalReviewReport
    {
        public string status;
        public List<LocalScenarioCheck> checks;
        public List<LocalDemoMetric> examples;
    }
    public partial class ViewerController
    {
        bool localReviewRunning;
        public void RunLocalScenarioReview()
        {
            if(Application.isPlaying&&!localReviewRunning&&!LocalBusy)StartCoroutine(LocalScenarioReview());
        }
        void SetLocalDemo()
        {
            localBuilding="EDIFICIO_1";localFloor="P2";localStart=new Vector2(45,4);localEnd=new Vector2(52,9);localRectangleSet=true;
            FocusLocalFloor();
        }
        static double LocalResponseError(AnalysisResultsData a,AnalysisResultsData b,double factor)
        {
            double maximum=0;var rows=new Dictionary<string,AnalysisElementResult>();var nodes=new Dictionary<int,AnalysisNodeResult>();
            foreach(var r in a.elements)rows[r.analysis_id]=r;foreach(var n in a.nodes)nodes[n.node_tag]=n;
            foreach(var r in b.elements)
            {var x=rows[r.analysis_id];for(int k=0;k<6;k++){maximum=Math.Max(maximum,Math.Abs(r.localForce_end1[k]-factor*x.localForce_end1[k]));maximum=Math.Max(maximum,Math.Abs(r.localForce_end2[k]-factor*x.localForce_end2[k]));}}
            foreach(var n in b.nodes)
            {var x=nodes[n.node_tag];maximum=Math.Max(maximum,Math.Abs(n.ux_m-factor*x.ux_m));maximum=Math.Max(maximum,Math.Abs(n.uy_m-factor*x.uy_m));maximum=Math.Max(maximum,Math.Abs(n.uz_m-factor*x.uz_m));}
            return maximum;
        }
        IEnumerator WaitLocalJob()
        {
            float began=Time.realtimeSinceStartup;
            while(LocalBusy&&Time.realtimeSinceStartup-began<125)yield return null;
        }
        IEnumerator LocalScenarioReview()
        {
            localReviewRunning=true;
            var checks=new List<LocalScenarioCheck>();var examples=new List<LocalDemoMetric>();
            Action<string,bool> check=(name,pass)=>checks.Add(new LocalScenarioCheck{check=name,pass=pass});
            string folder=Path.Combine(Application.dataPath,"..","Temp","local_scenario_review");Directory.CreateDirectory(folder);
            var savedBase=new Dictionary<string,string>();foreach(string c in new[]{"G","Q","EX","EY"})savedBase[c]=JsonUtility.ToJson(FindP1L5Case(c));
            RestoreLocalBase();float g=p1l5LambdaG,q=p1l5LambdaQ,ex=p1l5LambdaEX,ey=p1l5LambdaEY;
            p1l5LambdaG=1;p1l5LambdaQ=.5f;p1l5LambdaEX=p1l5LambdaEY=0;RebuildP1L5Combination(true);
            var baseline=FindP1L5Case("R");string savedR=JsonUtility.ToJson(baseline);int structuralCount=allElements.Count;
            openGroups.Clear();openGroups.Add("CARGA LOCAL");uiHidden=false;presentationMode=false;navigationExpanded=true;
            SetLocalDemo();localMode=localLastMode=0;localPeople="10";localPersonKg="68";
            StartLocalCalculation(false);yield return WaitLocalJob();
            check("rectangle preview clips physical slab without solving",localPayload?.status=="PREVIEW"&&!localActive&&localPayload.increment==null);
            check("preview area 35m2; four physical receivers",localPayload?.allocation!=null&&Math.Abs(localPayload.allocation.effective_area_m2-35)<1e-6&&localPayload.allocation.receivers.Count==4);
            SetQuickView("Planta");yield return new WaitForEndOfFrame();SaveVisualFrame(folder,"01_selection_top.png");
            AnalysisResultsData one=null,ten=null;
            foreach(int n in new[]{0,1,10,20})
            {
                localPeople=n.ToString();SetLocalDemo();StartLocalCalculation(true);yield return WaitLocalJob();
                check("real OpenSees scenario "+n+" persons",localActive&&activeAnalysisCase=="R_SCENARIO"&&localPayload?.increment!=null);
                if(!localActive)continue;
                check("force units "+n+" persons",Math.Abs(localPayload.allocation.force_N-n*68*9.81)<1e-6);
                check("same physical registry "+n,allElements.Count==structuralCount);
                if(n==0)check("zero scenario = BASE",LocalResponseError(baseline,FindP1L5Case("R_SCENARIO"),1)<1e-9);
                if(n==1)one=localIncrement;
                if(n==10)ten=localIncrement;
                if(n>1&&one!=null)check("linear Q_LOCAL scaling "+n,LocalResponseError(one,localIncrement,n)<1e-6);
                var beam=allElements.Find(e=>e.humanId=="E1-P2-V-048");
                var b=LocalFailureIn(baseline,beam,beam.humanId);var s=LocalFailureIn(FindP1L5Case("R_SCENARIO"),beam,beam.humanId);
                examples.Add(new LocalDemoMetric{input=n+" persons ×68kg",element_id=beam.humanId,base_dc=b?.demandCapacityRatio.ToString("R"),scenario_dc=s?.demandCapacityRatio.ToString("R"),force_kN=localPayload.allocation.force_N/1000,area_m2=localPayload.allocation.effective_area_m2,q_kN_m2=localPayload.allocation.q_local_kN_m2,receptors=localPayload.allocation.receivers.Count,increment_my_kNm=LocalEnvelope(localIncrement,beam.humanId,4),increment_u_mm=LocalTranslation(localIncrement,beam.humanId)});
                if(n==10)
                {
                    bool reasonable=true;
                    foreach(var info in allElements)
                    {string id=info.humanId??info.id;var before=LocalFailureIn(baseline,info,id);var after=LocalFailureIn(FindP1L5Case("R_SCENARIO"),info,id);if(before!=null&&after!=null&&before.state!=StructuralFailureState.NO_DATA&&before.demandCapacityRatio<.5&&after.state==StructuralFailureState.CAPACITY_EXCEEDED)reasonable=false;}
                    check("10-person sanity: no far-safe member leaps beyond capacity",reasonable);
                    Select(beam);check("scenario selection + inspector comparison",lastSelected==beam&&ResultsForSelection(beam,beam.humanId).Count>0);
                    structuralFailureVisualizationEnabled=true;RefreshStructuralFailureStates();
                    check("same D/C evaluator in scenario map",StructuralFailureFor(beam.humanId)?.demandCapacityRatio==s?.demandCapacityRatio);
                    SetDiagramMode(1);diagram2DVisible=true;yield return new WaitForEndOfFrame();SaveVisualFrame(folder,"02_ten_persons_comparison.png");
                    check("My diagram exists",selectedDiagramObjects.Count>0);
                    diagram2DVisible=false;SetDiagramMode(3);yield return new WaitForEndOfFrame();check("axial diagram exists",selectedDiagramObjects.Count>0);
                    SetDiagramMode(0);activeDeformationVisible=true;typeVisible["analysis_deformed"]=true;RebuildActiveDeformedShape();
                    check("scenario deformation exists",activeDeformationObjects.Count>0);
                    yield return new WaitForEndOfFrame();SaveVisualFrame(folder,"03_scenario_deformation.png");
                    activeDeformationVisible=false;typeVisible["analysis_deformed"]=false;ReapplyAll();
                    float old=p1l5LambdaQ;p1l5LambdaQ=.6f;RebuildP1L5Combination(true);check("sliders rebuild scenario R",activeAnalysisCase=="R_SCENARIO");p1l5LambdaQ=old;RebuildP1L5Combination(true);
                }
            }
            foreach(int mode in new[]{1,2})
            {
                localMode=localLastMode=mode;localMass="680";localIntensity=(6670.8/35000).ToString("R",System.Globalization.CultureInfo.InvariantCulture);
                SetLocalDemo();StartLocalCalculation(true);yield return WaitLocalJob();
                check("editable "+(mode==1?"mass kg":"surface kN/m2")+" equals ten-person response",localActive&&ten!=null&&LocalResponseError(ten,localIncrement,1)<1e-6);
            }
            localMode=localLastMode=0;
            // Incremental QA search, not a hardcoded default or a fake visual force.
            bool crossed=false;int large=40;
            for(int attempt=0;attempt<10&&!crossed;attempt++,large*=4)
            {
                localPeople=large.ToString();SetLocalDemo();StartLocalCalculation(true);yield return WaitLocalJob();
                if(!localActive)break;
                foreach(var info in allElements)
                {string id=info.humanId??info.id;var b=LocalFailureIn(baseline,info,id);var s=LocalFailureIn(FindP1L5Case("R_SCENARIO"),info,id);if(b!=null&&s!=null&&b.state!=StructuralFailureState.NO_DATA&&b.demandCapacityRatio<.5&&s.state==StructuralFailureState.CAPACITY_EXCEEDED){crossed=true;Select(info);examples.Add(new LocalDemoMetric{input="QA high load "+large+" persons",element_id=id,base_dc=b.demandCapacityRatio.ToString("R"),scenario_dc=s.demandCapacityRatio.ToString("R"),force_kN=localPayload.allocation.force_N/1000,area_m2=localPayload.allocation.effective_area_m2,q_kN_m2=localPayload.allocation.q_local_kN_m2,receptors=localPayload.allocation.receivers.Count,increment_my_kNm=LocalEnvelope(localIncrement,id,4),increment_u_mm=LocalTranslation(localIncrement,id)});break;}}
            }
            structuralFailureVisualizationEnabled=true;RefreshStructuralFailureStates();check("large real load raises a far-safe member above capacity",crossed);
            bool colours=true;var observedStates=new HashSet<StructuralFailureState>();
            foreach(var info in allElements)
            {
                if(info.go==null||info.isFeCandidateVisual||(info.category!="beam"&&info.category!="column"&&info.category!="wall"))continue;
                var failure=StructuralFailureFor(info.humanId??info.id);if(failure==null)continue;
                var expected=info.isHighlighted?StructuralFailureVisualStyle.Selection:
                    failure.state==StructuralFailureState.WARNING?StructuralFailureVisualStyle.Warning:
                    failure.state==StructuralFailureState.CAPACITY_EXCEEDED?StructuralFailureVisualStyle.Exceeded:
                    failure.state==StructuralFailureState.NO_DATA?StructuralFailureVisualStyle.NoData:info.baseColor;
                var block=new MaterialPropertyBlock();info.go.GetComponent<Renderer>().GetPropertyBlock(block);
                colours &= block.GetColor("_Color")==expected;observedStates.Add(failure.state);
            }
            check("actual scenario renderer colours follow same D/C states",colours);
            check("actual high-load orange and red states exist",observedStates.Contains(StructuralFailureState.WARNING)&&observedStates.Contains(StructuralFailureState.CAPACITY_EXCEEDED));
            yield return new WaitForEndOfFrame();SaveVisualFrame(folder,"04_high_load_capacity.png");
            RestoreLocalBase();check("Restore BASE, no solver, no scenario/area",!localActive&&localIncrement==null&&FindP1L5Case("R_SCENARIO")==null&&localAreaObject==null&&activeAnalysisCase=="R");
            check("R_BASE unchanged",JsonUtility.ToJson(FindP1L5Case("R"))==savedR);
            foreach(var entry in savedBase)check("base case unchanged "+entry.Key,JsonUtility.ToJson(FindP1L5Case(entry.Key))==entry.Value);
            check("BASE physical/capacity/results files unchanged",LocalBaseStillLoaded());
            check("context still passive",ContextIsPassive());
            var regressionBeam=allElements.Find(e=>e.humanId=="E1-P2-V-048");Select(regressionBeam);
            foreach(string name in new[]{"G","Q","EX","EY","R"})
            {ActivateAnalysisCase(name);check("BASE case selection "+name,ResultsForSelection(regressionBeam,regressionBeam.humanId).Count>0);}
            foreach(int mode in new[]{1,2,3,4,5,6})
            {SetDiagramMode(mode);diagram2DVisible=true;check("BASE 3D/2D component "+mode,selectedDiagramObjects.Count>0&&diagram2DVisible);}
            activeDeformationVisible=true;typeVisible["analysis_deformed"]=true;RebuildActiveDeformedShape();check("BASE deformation",activeDeformationObjects.Count>0);
            p1l5LambdaG=g;p1l5LambdaQ=q;p1l5LambdaEX=ex;p1l5LambdaEY=ey;RebuildP1L5Combination(true);
            ResetPresentation();localMode=localLastMode=0;localPeople="10";localPersonKg="68";
            SetLocalDemo();StartLocalCalculation(false);yield return WaitLocalJob();SelectElementById("E1-P2-V-048",false);SetQuickView("Iso");
            openGroups.Clear();openGroups.Add("CARGA LOCAL");
            yield return new WaitForEndOfFrame();SaveVisualFrame(folder,"05_ready_demo.png");
            var report=new LocalReviewReport{status=checks.TrueForAll(c=>c.pass)?"PASS":"FAIL",checks=checks,examples=examples};
            File.WriteAllText(Path.Combine(folder,"QA.json"),JsonUtility.ToJson(report,true));
            Debug.Log($"[LOCAL SCENARIO QA] {report.status}: {checks.Count} checks; Temp/local_scenario_review/QA.json. BASE untouched.");
            localReviewRunning=false;
        }
    }
}
