using System;
using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    // Only establishes the FE longitudinal range. Graphical transverse directions
    // are presentation-local, not an inferred OpenSees transverse frame.
    public static class ARVerticalResultMapping
    {
        public static bool TryRange(StructuralElementARData row, int index,
            out float start, out float end, out string reason)
        {
            start = end = 0;
            reason = "Coordenadas FE ausentes, duplicadas o no finitas; disponible en 2D";
            if (row == null || (row.type != "column" && row.type != "wall") ||
                index < 0 || index >= ARCurrentDiagramData.SegmentCount(row)) return false;
            var segment = row.current_result_R.segments[index];
            if (segment == null || !Node(row, segment.node_i, out double[] i) ||
                !Node(row, segment.node_j, out double[] j)) return false;
            var geometry = row.geometry;
            reason = "Altura física no verificable con los extremos FE; disponible en 2D";
            if (geometry == null || !Finite(geometry.z_bottom_m) || !Finite(geometry.z_top_m)) return false;
            double height = geometry.z_top_m - geometry.z_bottom_m;
            reason = "Dimensiones físicas incompletas; disponible en 2D";
            if (row.type == "column" && (!Dimension(row.dimensions?.width_m,row.section?.dimensions?.width_m) ||
                !Dimension(row.dimensions?.depth_m,row.section?.dimensions?.depth_m))) return false;
            if (row.type == "wall" && !Dimension(row.dimensions?.thickness_m,row.section?.dimensions?.thickness_m)) return false;
            reason = "Altura física no verificable con los extremos FE; disponible en 2D";
            Vector3 size = StructuralARElementRenderer.GetSizeMetres(row);
            double tolerance = Math.Max(.002, height * .0001);
            if (height <= 1e-7 || Math.Abs(size.y - height) > tolerance) return false;
            double pi = (i[2] - geometry.z_bottom_m) / height;
            double pj = (j[2] - geometry.z_bottom_m) / height;
            if (pi < -.001 || pi > 1.001 || pj < -.001 || pj > 1.001 || Math.Abs(pi-pj) < 1e-7) return false;
            reason = "Segmento FE no vertical; correspondencia 3D ambigua, disponible en 2D";
            if (Math.Abs(i[0]-j[0]) > tolerance || Math.Abs(i[1]-j[1]) > tolerance) return false;
            reason = "Segmento FE fuera de la sección física; disponible en 2D";
            if (row.type == "column")
            {
                double[] centre = geometry.center_m ?? row.model_coordinates_m?.center;
                if (!Vector(centre) || !InsideColumn(i, centre, size) || !InsideColumn(j, centre, size)) return false;
            }
            else
            {
                double[] a = geometry.start_m, b = geometry.end_m;
                if (!Vector(a) || !Vector(b) || Math.Abs(a[2]-b[2]) > tolerance) return false;
                double dx=b[0]-a[0], dy=b[1]-a[1], length=Math.Sqrt(dx*dx+dy*dy);
                if (length < 1e-7 || Math.Abs(size.x-length) > tolerance ||
                    !InsideWall(i,a,dx,dy,length,size.z) || !InsideWall(j,a,dx,dy,length,size.z)) return false;
            }
            start = Mathf.Clamp01((float)pi); end = Mathf.Clamp01((float)pj);
            reason = null;
            return true;
        }
        static bool InsideColumn(double[] p, double[] centre, Vector3 size) =>
            Math.Abs(p[0]-centre[0]) <= size.x*.5+.002 && Math.Abs(p[1]-centre[1]) <= size.z*.5+.002;
        static bool InsideWall(double[] p, double[] a, double dx, double dy, double length, double thickness)
        {
            double along=((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length;
            double across=Math.Abs((p[0]-a[0])*dy-(p[1]-a[1])*dx)/length;
            return along >= -.002 && along <= length+.002 && across <= thickness*.5+.002;
        }
        static bool Node(StructuralElementARData row, int tag, out double[] coordinates)
        {
            coordinates=null; int matches=0;
            if (row.current_result_R.node_displacements != null)
                foreach (var node in row.current_result_R.node_displacements)
                    if (node != null && node.node_tag == tag) { matches++; coordinates=node.model_coord_m; }
            return matches == 1 && Vector(coordinates);
        }
        static bool Vector(double[] p) => p?.Length == 3 && Finite(p[0]) && Finite(p[1]) && Finite(p[2]);
        static bool Dimension(double? physical, double? section)
        {
            double value = physical.GetValueOrDefault() > 0 ? physical.Value : section.GetValueOrDefault();
            return Finite(value) && value >= .01; // Reject the renderer's default/clamped fallback dimensions.
        }
        static bool Finite(double v) => !double.IsNaN(v) && !double.IsInfinity(v);
    }
}
