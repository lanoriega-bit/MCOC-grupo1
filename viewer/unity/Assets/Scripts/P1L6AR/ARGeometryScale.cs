using System;
using System.Globalization;
using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    public enum ARGeometryScaleMode { Auto, OneToTen, OneToFive, OneToTwo, Real }

    public static class ARGeometryScale
    {
        public const string Unavailable = "Escala física no disponible: dimensiones no verificadas";
        public static float Factor(ARGeometryScaleMode mode, Vector3 realSize)
        {
            switch(mode)
            {
                case ARGeometryScaleMode.OneToTen: return .10f;
                case ARGeometryScaleMode.OneToFive: return .20f;
                case ARGeometryScaleMode.OneToTwo: return .50f;
                case ARGeometryScaleMode.Real: return 1f;
                default: return ARSurfacePlacementMath.AutoScale(realSize);
            }
        }
        public static string Label(ARGeometryScaleMode mode)
        {
            switch(mode)
            {
                case ARGeometryScaleMode.OneToTen: return "1:10";
                case ARGeometryScaleMode.OneToFive: return "1:5";
                case ARGeometryScaleMode.OneToTwo: return "1:2";
                case ARGeometryScaleMode.Real: return "1:1 REAL";
                default: return "AUTO";
            }
        }
        public static string Description(ARGeometryScaleMode mode, float factor) => mode == ARGeometryScaleMode.Auto && factor > 0
            ? "AUTO (~1:" + (1.0/factor).ToString("0.##",CultureInfo.InvariantCulture) + ")" : Label(mode);

        // Validate the actual sources used by the protected renderer, without
        // accepting its default dimensions or .01 m clamping for physical modes.
        public static bool TryVerifiedDimensions(StructuralElementARData row, out Vector3 dimensions)
        {
            dimensions=Vector3.zero;
            if(row==null || row.data_state!="CURRENT_VERIFIED" || row.element_id!=row.elementTag || string.IsNullOrEmpty(row.element_id))return false;
            var g=row.geometry; var p=row.dimensions; var s=row.section?.dimensions;
            double x,y,z;
            if(row.type=="beam")
            {
                if(!Vector(g?.start_m) || !Vector(g?.end_m))return false;
                double length2=0;for(int a=0;a<3;a++) {double d=g.end_m[a]-g.start_m[a];length2+=d*d;}
                x=Math.Sqrt(length2);y=Value(p?.height_m,s?.height_m);z=Value(p?.width_m,s?.width_m);
            }
            else if(row.type=="column")
            {
                if(g==null || !Finite(g.z_bottom_m) || !Finite(g.z_top_m))return false;
                x=Value(p?.width_m,s?.width_m);y=g.z_top_m-g.z_bottom_m;z=Value(p?.depth_m,s?.depth_m);
            }
            else if(row.type=="wall")
            {
                if(!Vector(g?.start_m) || !Vector(g?.end_m) || !Finite(g.z_bottom_m) || !Finite(g.z_top_m))return false;
                double dx=g.end_m[0]-g.start_m[0],dy=g.end_m[1]-g.start_m[1];
                x=Math.Sqrt(dx*dx+dy*dy);y=g.z_top_m-g.z_bottom_m;z=Value(p?.thickness_m,s?.thickness_m);
            }
            else return false;
            if(!Physical(x) || !Physical(y) || !Physical(z))return false;
            Vector3 verified=new Vector3((float)x,(float)y,(float)z);
            Vector3 rendered=StructuralARElementRenderer.GetSizeMetres(row);
            for(int a=0;a<3;a++)if(Math.Abs(rendered[a]-verified[a])>Math.Max(.0001,verified[a]*.00001))return false;
            dimensions=rendered;return true;
        }
        static double Value(double? physical,double? section) => physical.GetValueOrDefault()>0 ? physical.Value : section.GetValueOrDefault();
        static bool Physical(double v) => Finite(v) && v>=.01 && v<float.MaxValue;
        static bool Vector(double[] p) => p?.Length==3 && Finite(p[0]) && Finite(p[1]) && Finite(p[2]);
        static bool Finite(double v) => !double.IsNaN(v) && !double.IsInfinity(v);
    }
}
