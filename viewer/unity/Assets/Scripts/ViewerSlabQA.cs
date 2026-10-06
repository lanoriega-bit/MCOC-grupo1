using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    public partial class ViewerController
    {
        public void RunSlabReview() { if(Application.isPlaying) StartCoroutine(SlabReview()); }
        public void RunSlabLoadReview() { if(Application.isPlaying) StartCoroutine(SlabLoadReview()); }
        IEnumerator SlabLoadReview()
        {
            var checks=new List<WallReviewCheck>();
            Action<string,bool> check=(name,pass)=>checks.Add(new WallReviewCheck{check=name,pass=pass});
            string folder=Path.Combine(FindRepositoryRoot(),"results","validation","slabs_lateral");
            Directory.CreateDirectory(folder);
            check("CURRENT results verified",currentResultsAvailable);
            check("CAD layers not constructed",!allElements.Exists(e=>e.category=="axis"||e.category=="slab_edge"||e.category=="cad_reference"));
            float g=p1l5LambdaG,q=p1l5LambdaQ,ex=p1l5LambdaEX,ey=p1l5LambdaEY;
            p1l5LambdaG=p1l5LambdaEX=p1l5LambdaEY=0;
            foreach(string id in new[]{"E1-P1-V-002","E1-P2-V-041","E2-P3-V-001"})
            {
                var load=CurrentElementLoad(id);
                check(id+" Q tributary data",load?.Q!=null&&load.Q.tributary_area_m2>0);
                if(load?.Q==null)continue;
                check(id+" qQ weighted mean",Math.Abs(load.Q.average_surface_intensity_kN_m2-load.Q.surface_force_N/load.Q.tributary_area_m2/1000)<1e-6);
                foreach(float factor in new[]{0f,1f,2f})
                {
                    p1l5LambdaQ=factor;RebuildP1L5Combination(true);
                    bool pass=true;int count=0;
                    foreach(var row in FindP1L5Case("Q").elements)
                    {
                        if(row.element_id!=id)continue;
                        var combined=FindP1L5Case("R").elements.Find(e=>e.analysis_id==row.analysis_id);
                        count++;
                        for(int i=0;i<6;i++)pass &= combined!=null&&Math.Abs(combined.localForce_end1[i]-factor*row.localForce_end1[i])<1e-6&&Math.Abs(combined.localForce_end2[i]-factor*row.localForce_end2[i])<1e-6;
                    }
                    check(id+" lambdaQ "+factor+" exact end responses",pass&&count>0);
                }
                ResetPresentation();
                p1l5LambdaG=p1l5LambdaEX=p1l5LambdaEY=0;p1l5LambdaQ=1;RebuildP1L5Combination(true);
                SelectElementById(id,false);
                check(id+" selection",lastSelected!=null&&(lastSelected.humanId??lastSelected.id)==id);
                if(lastSelected!=null)
                {
                    check(id+" equivalent width",Math.Abs(load.Q.equivalent_width_m-load.Q.tributary_area_m2/lastSelected.lengthM)<1e-4);
                    check(id+" equivalent line load",Math.Abs(load.Q.equivalent_line_load_N_m-load.Q.surface_force_N/lastSelected.lengthM)<.1);
                }
                inspectorVisible=lastSelected!=null;
                inspectorSelection=id;inspectorGroups.Clear();inspectorGroups.Add("CARGAS");
                openGroups.Clear();openGroups.Add("RESULTADOS");
                check(id+" explanatory text",CurrentElementLoadText(id,null).Contains("qQ base")&&CoefficientExplanation("Q").Contains("OpenSees"));
                yield return new WaitForEndOfFrame();SaveVisualFrame(folder,id+"_Q.png");
            }
            p1l5LambdaG=g;p1l5LambdaQ=q;p1l5LambdaEX=ex;p1l5LambdaEY=ey;RebuildP1L5Combination(true);
            var report=new WallReviewReport{status=checks.TrueForAll(c=>c.pass)?"PASS":"FAIL",dataset=currentGateStatus,checks=checks};
            File.WriteAllText(Path.Combine(folder,"UNITY_Q_QA.json"),JsonUtility.ToJson(report,true));
            Debug.Log("[Q UI QA] "+report.status+": "+checks.Count+" checks");
            yield return StartCoroutine(SlabReview(folder));
        }
        IEnumerator SlabReview(string outputFolder=null)
        {
            var checks=new List<WallReviewCheck>();
            Action<string,bool> check=(name,pass)=>checks.Add(new WallReviewCheck{check=name,pass=pass});
            string folder=outputFolder??Path.Combine(FindRepositoryRoot(),"results","validation","slabs_unity");
            Directory.CreateDirectory(folder);
            ResetPresentation();
            check("slabs default OFF",!typeVisible["slab"]);
            check("no historical pilot duplicate",!byType.ContainsKey("architectural_slab"));
            check("10 physical slab polygons",model.solids.FindAll(s=>s.kind=="slab_polygon").Count==10);
            foreach(string building in new[]{"EDIFICIO_1","EDIFICIO_2"})
            foreach(string floor in new[]{"S1","P1","P2","P3","P4"})
            {
                foreach(string b in new List<string>(buildingVisible.Keys)) buildingVisible[b]=b==building;
                foreach(string f in new List<string>(floorVisible.Keys)) floorVisible[f]=f==floor;
                foreach(string t in new List<string>(typeVisible.Keys)) typeVisible[t]=t=="slab"||t=="beam"||t=="wall";
                ReapplyAll();
                var slab=allElements.Find(e=>e.category=="slab"&&e.building==building&&e.floor==floor);
                check(building+" "+floor+" visible",slab!=null&&slab.go.activeSelf);
                check(building+" "+floor+" exclusive filter",allElements.TrueForAll(e=>e.go==null||!e.go.activeSelf||e.building==building&&e.floor==floor));
                if(slab==null)continue;
                var mesh=slab.go.GetComponent<MeshFilter>().sharedMesh;
                check(building+" "+floor+" valid mesh",mesh!=null&&mesh.vertexCount>=3&&mesh.triangles.Length>=3);
                var material=slab.go.GetComponent<Renderer>().sharedMaterial;
                check(building+" "+floor+" white transparent",material.color==new Color(1,1,1,.18f)&&material.renderQueue==3000);
                SetQuickView("Planta");
                var bounds=slab.go.GetComponent<Renderer>().bounds;
                orbitTarget=bounds.center;orbitDist=Mathf.Max(bounds.size.x,bounds.size.z)*1.4f+10f;
                openGroups.Clear();inspectorVisible=false;
                yield return new WaitForEndOfFrame();
                SaveVisualFrame(folder,building+"_"+floor+"_TOP.png");
            }
            ResetPresentation();
            yield return StartCoroutine(VisualUxReview(folder));
            string regression=Path.Combine(folder,"UNITY_VISUAL_RUNTIME_QA.json");
            check("viewer regression completed PASS",File.Exists(regression)&&JsonUtility.FromJson<WallReviewReport>(File.ReadAllText(regression)).status=="PASS");
            var report=new WallReviewReport{status=checks.TrueForAll(c=>c.pass)?"PASS":"FAIL",dataset=currentGateStatus,checks=checks};
            File.WriteAllText(Path.Combine(folder,"UNITY_SLAB_QA.json"),JsonUtility.ToJson(report,true));
            Debug.Log("[SLAB QA] "+report.status+": "+checks.Count+" checks plus viewer regression; primary boundaries still REVIEW_REQUIRED.");
            ResetPresentation();SetQuickView("Iso");openGroups.Clear();openGroups.Add("MODELO");
        }
    }
}
