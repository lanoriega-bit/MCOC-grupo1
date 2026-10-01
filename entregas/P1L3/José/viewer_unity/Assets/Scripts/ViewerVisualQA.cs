using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    public partial class ViewerController
    {
        public void RunVisualUxReview() { if(Application.isPlaying)StartCoroutine(VisualUxReview()); }

        IEnumerator VisualUxReview(string outputFolder = null)
        {
            var checks=new List<WallReviewCheck>();
            Action<string,bool> check=(name,pass)=>checks.Add(new WallReviewCheck { check=name,pass=pass });
            check("CURRENT verified",currentResultsAvailable&&ReloadCurrentContractAndCheck());
            check("startup nodes ON",typeVisible["node"]);
            check("startup slabs OFF",!typeVisible["slab"]&&(!typeVisible.ContainsKey("architectural_slab")||!typeVisible["architectural_slab"]));
            check("startup capacity OFF",!structuralFailureVisualizationEnabled);
            string folder=outputFolder??Path.Combine(FindRepositoryRoot(),"entregas","P1L6","visual_ux");
            Directory.CreateDirectory(folder);
            ResetPresentation();SetQuickView("Iso");
            foreach(string type in new[]{"beam","column","wall"})
            {
                var material=MatFor(type);
                check(type+" shader supported",material!=null&&material.shader.isSupported&&material.shader.name=="MCOC/TechnicalSurface");
                check(type+" category pattern",material.GetFloat("_Pattern")== (type=="column"?1:type=="wall"?2:0));
            }
            check("slab white transparent",MatFor("architectural_slab").color==new Color(1,1,1,0.18f)&&MatFor("architectural_slab").renderQueue==3000);
            foreach(string type in new[]{"beam","column","wall","node","slab","support","tributary"})
            {
                ToggleType(type,true);
                check(type+" layer available",byType.ContainsKey(type)&&byType[type].Exists(go=>go!=null&&go.activeSelf));
                ToggleType(type,false);
                check(type+" layer hides",!byType.ContainsKey(type)||byType[type].TrueForAll(go=>go==null||!go.activeSelf));
                ToggleType(type,DefaultTypeVisibility(type));
            }
            foreach(string floor in new List<string>(floorVisible.Keys))
            {
                ToggleFloor(floor,false);
                check("floor hides "+floor,allElements.TrueForAll(e=>e==null||e.floor!=floor||e.go==null||!e.go.activeSelf));
                ToggleFloor(floor,true);
            }
            foreach(string building in new List<string>(buildingVisible.Keys))
            {
                buildingVisible[building]=false;ReapplyAll();
                check("building hides "+building,allElements.TrueForAll(e=>e==null||e.go==null||e.building!=building||!e.go.activeSelf));
                buildingVisible[building]=true;ReapplyAll();
            }
            foreach(string view in new[]{"Iso","Planta","Frente","Lateral"})
            {SetQuickView(view);yield return null;check("view "+view,!float.IsNaN(orbitDist)&&orbitDist>0);}
            foreach(string id in new[]{"E1-P2-V-041","E2-P4-C-004","E1-P4-M-007"})
            {
                SelectElementById(id,false);
                check("selection "+id,lastSelected!=null&&lastSelected.humanId==id&&lastSelected.isHighlighted);
                if(lastSelected==null)continue;
                var renderer=lastSelected.go.GetComponent<Renderer>();
                var block=new MaterialPropertyBlock();renderer.GetPropertyBlock(block);
                check("cyan "+id,block.GetColor("_Color")==StructuralFailureVisualStyle.Selection);
                foreach(string name in new[]{"G","Q","EX","EY","R"})
                {ActivateAnalysisCase(name);check(id+" results "+name,ResultsForSelection(lastSelected,id).Count>0);}
                check(id+" inspector section",!string.IsNullOrEmpty(CurrentSectionText(CurrentSolid(lastSelected))));
                if(lastSelected.category=="column")check("column displayed height matches solid",CurrentSectionText(CurrentSolid(lastSelected)).Contains(CurrentSolid(lastSelected).height_m.ToString("F2"))&&CurrentSolid(lastSelected).height_m>0);
                check(id+" capacity",!string.IsNullOrEmpty(BuildDemandCapacityText(id))&&StructuralFailureFor(id)!=null);
            }
            SelectElementById("E1-P2-V-041",false);
            p1l5LambdaG=1.25f;p1l5LambdaQ=0.75f;p1l5LambdaEX=0.2f;p1l5LambdaEY=-0.1f;
            RebuildP1L5Combination(true);
            var sample=FindP1L5Case("R").elements[0];
            double expected=0;float[] factors={1.25f,0.75f,0.2f,-0.1f};string[] names={"G","Q","EX","EY"};
            for(int i=0;i<4;i++)expected+=factors[i]*FindP1L5Case(names[i]).elements.Find(e=>e.analysis_id==sample.analysis_id).localForce_end1[4];
            check("slider R My equals manual sum",Math.Abs(sample.localForce_end1[4]-expected)<1e-6);
            p1l5LambdaG=1;p1l5LambdaQ=0.5f;p1l5LambdaEX=p1l5LambdaEY=0;RebuildP1L5Combination(true);
            activeDeformationVisible=true;typeVisible["analysis_deformed"]=true;RebuildActiveDeformedShape();ReapplyAll();
            check("CURRENT deformation",byType.ContainsKey("analysis_deformed")&&byType["analysis_deformed"].Exists(go=>go!=null&&go.activeSelf));
            activeDeformationVisible=false;typeVisible["analysis_deformed"]=false;ReapplyAll();
            for(int i=1;i<=6;i++)
            {SetDiagramMode(i);diagram2DVisible=true;yield return null;check("3D and 2D component "+i,selectedDiagramObjects.Count>0&&diagram2DVisible);}
            diagram2DVisible=false;SetDiagramMode(0);
            // Synthetic states test colours only, never change capacity or demand data.
            RestoreHighlight();
            var beam=allElements.Find(e=>e!=null&&e.category=="beam"&&e.go!=null);
            var visualizer=beam.go.GetComponent<ElementFailureVisualizer>();var beamRenderer=beam.go.GetComponent<Renderer>();
            StructuralFailureState[] states={StructuralFailureState.OK,StructuralFailureState.WARNING,StructuralFailureState.CAPACITY_EXCEEDED,StructuralFailureState.NO_DATA};
            Color[] stateColours={beam.baseColor,StructuralFailureVisualStyle.Warning,StructuralFailureVisualStyle.Exceeded,StructuralFailureVisualStyle.NoData};
            for(int i=0;i<states.Length;i++)
            {visualizer.Apply(new FailureResult { state=states[i] },true,false,false);var b=new MaterialPropertyBlock();beamRenderer.GetPropertyBlock(b);check("state colour "+states[i],b.GetColor("_Color")==stateColours[i]);}
            structuralFailureVisualizationEnabled=true;ApplyStructuralFailureVisualization();
            structuralFailureVisualizationEnabled=false;ApplyStructuralFailureVisualization();
            bool restored=true;
            foreach(var e in allElements)if(e!=null&&e.go!=null&&!e.isFeCandidateVisual&&(e.category=="beam"||e.category=="column"||e.category=="wall"))
            {var b=new MaterialPropertyBlock();e.go.GetComponent<Renderer>().GetPropertyBlock(b);
             if(b.GetColor("_Color")!=e.baseColor) { restored=false; Debug.LogWarning("[VISUAL RESTORE] "+e.humanId+" highlighted="+e.isHighlighted+" fe="+e.isFeCandidateVisual+" expected="+e.baseColor+" actual="+b.GetColor("_Color")); }}
            check("normal colours restored",restored);
            foreach(string name in names)check("case help "+name,LoadCaseExplanation(name).StartsWith(name+" ·"));
            check("R help no solver",LoadCaseExplanation("R").Contains("No reejecuta OpenSees"));
            ResetPresentation();SetQuickView("Iso");
            yield return new WaitForEndOfFrame();SaveVisualFrame(folder,"default.png");
            SelectElementById("E1-P2-V-041",false);openGroups.Clear();openGroups.Add("RESULTADOS");inspectorVisible=true;
            yield return new WaitForEndOfFrame();SaveVisualFrame(folder,"inspector.png");
            SelectElementById("E2-P4-C-004",false);demandCapacityPlotVisible=true;
            yield return new WaitForEndOfFrame();SaveVisualFrame(folder,"capacity.png");
            demandCapacityPlotVisible=false;ResetPresentation();SetQuickView("Iso");
            var report=new WallReviewReport { status=checks.TrueForAll(c=>c.pass)?"PASS":"FAIL",dataset=currentGateStatus,checks=checks };
            File.WriteAllText(Path.Combine(folder,"UNITY_VISUAL_RUNTIME_QA.json"),JsonUtility.ToJson(report,true));
            Debug.Log("[VISUAL UX QA] "+report.status+": "+checks.Count+" checks. No structural sources changed.");
        }

        static void SaveVisualFrame(string folder,string name)
        {
            var frame=new Texture2D(Screen.width,Screen.height,TextureFormat.RGB24,false);
            frame.ReadPixels(new Rect(0,0,Screen.width,Screen.height),0,0);frame.Apply();
            File.WriteAllBytes(Path.Combine(folder,name),frame.EncodeToPNG());Destroy(frame);
        }
    }
}
