using System;
using System.IO;
using System.Text.Json;
using UnityEngine;
using Mcoc.UnityViewer.P1L6AR;

// Executes only managed dimension/factor/data code. It does not substitute for
// Unity scene, bounds, contact, anchor, UI, or Android tests.
public static class OfflineMetricChecks
{
    static void Check(bool ok,string reason){if(!ok)throw new Exception(reason);}
    public static void Main(string[] args)
    {
        var options=new JsonSerializerOptions{IncludeFields=true};
        var dataset=JsonSerializer.Deserialize<ARDatasetRoot>(File.ReadAllText(args[0]),options);
        int verified=0,beam=0,column=0,wall=0;
        foreach(var row in dataset.elements)
        {
            if(ARGeometryScale.TryVerifiedDimensions(row,out var real))
            {
                verified++;
                Check(ARGeometryScale.Factor(ARGeometryScaleMode.Auto,real)==ARSurfacePlacementMath.AutoScale(real),"AUTO exact preserved");
                Check(Math.Abs(Math.Max(real.x,Math.Max(real.y,real.z))*ARGeometryScale.Factor(ARGeometryScaleMode.Auto,real)-.65)<.000001,"AUTO target .65");
                float[] factors={ARSurfacePlacementMath.AutoScale(real),.1f,.2f,.5f,1f};
                for(int n=0;n<5;n++)Check(ARGeometryScale.Factor((ARGeometryScaleMode)n,real)==factors[n],"uniform factor exact");
                if(row.element_id=="E1-P2-V-041" || row.element_id=="E1-P2-C-001" || row.element_id=="E2-P2-M-007")
                {
                    Vector3 expected=row.type=="beam"?new Vector3(3.47f,.8f,.6f):row.type=="column"?new Vector3(.7f,3.96f,.7f):new Vector3(2.82f,3.96f,.25f);
                    Check(Vector3.Distance(real,expected)<.00001f,"priority real dimensions");
                    for(int n=0;n<5;n++)
                    {
                        Vector3 size=real*factors[n];
                        Console.WriteLine(row.element_id+" "+ARGeometryScale.Description((ARGeometryScaleMode)n,factors[n])+" X/Y/Z="+size.x+"/"+size.y+"/"+size.z+" m");
                        Check(ARSelectedElementInfo.Format(row,(ARGeometryScaleMode)n,factors[n]).Contains("Dimensiones mostradas:"),"dynamic metric information");
                    }
                    var clone=JsonSerializer.Deserialize<StructuralElementARData>(JsonSerializer.Serialize(row,options),options);
                    clone.dimensions=null;clone.section=null;
                    Check(!ARGeometryScale.TryVerifiedDimensions(clone,out _),"reject defaults");
                    clone=JsonSerializer.Deserialize<StructuralElementARData>(JsonSerializer.Serialize(row,options),options);
                    clone.geometry=null;
                    Check(!ARGeometryScale.TryVerifiedDimensions(clone,out _),"reject absent physical geometry");
                }
            }
            for(int n=0;n<ARCurrentDiagramData.SegmentCount(row);n++)
            {
                if(ARForceDiagram3DRenderer.TrySegmentRange(row,n,out _,out _))
                {if(row.type=="beam")beam++;else if(row.type=="column")column++;else if(row.type=="wall")wall++;}
                for(int c=0;c<6;c++)Check(ARCurrentDiagramData.TryValues(row,n,c,out _,out _),"CURRENT data remains available");
            }
        }
        Check(beam==446&&column==142&&wall==84,"protected mapping audit unchanged");
        Console.WriteLine("OFFLINE_METRIC_CHECKS_PASSED: verified dimensions="+verified+"/"+dataset.elements.Length+"; FE mappings="+beam+"/"+column+"/"+wall+"; factors and CURRENT values verified. Scene/placement tests still require licensed Unity.");
    }
}
