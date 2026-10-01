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
        IEnumerator SlabReview()
        {
            var checks=new List<WallReviewCheck>();
            Action<string,bool> check=(name,pass)=>checks.Add(new WallReviewCheck{check=name,pass=pass});
            string folder=Path.Combine(FindRepositoryRoot(),"entregas","P1L6","slab_reconstruction","unity_qa");
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
