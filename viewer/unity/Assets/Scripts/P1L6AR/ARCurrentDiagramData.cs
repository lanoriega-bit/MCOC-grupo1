using System;

namespace Mcoc.UnityViewer.P1L6AR
{
    // Same localForce order and opposite-end face convention as ViewerController.
    // These are FE local axes, independent of the presentation axes in AR.
    public static class ARCurrentDiagramData
    {
        public static readonly string[] Components = { "N", "Vy", "Vz", "T", "My", "Mz" };
        public static string Units(int component) => component < 3 ? "kN" : "kN·m";
        public static int SegmentCount(StructuralElementARData row) => row?.current_result_R?.segments?.Length ?? 0;

        public static bool TryValues(StructuralElementARData row, int segmentIndex, int component,
            out double endI, out double endJ)
        {
            endI = endJ = double.NaN;
            if (row == null || row.data_state != "CURRENT_VERIFIED" ||
                row.element_id != row.elementTag || string.IsNullOrEmpty(row.element_id) ||
                segmentIndex < 0 || segmentIndex >= SegmentCount(row) || component < 0 || component >= 6) return false;
            ARResultSegment segment = row.current_result_R.segments[segmentIndex];
            if (segment == null || string.IsNullOrEmpty(segment.analysis_id) ||
                !Contains(row.opensees_tags, segment.opensees_tag) ||
                !Contains(row.fe_node_tags, segment.node_i) || !Contains(row.fe_node_tags, segment.node_j) ||
                segment.localForce_end1_N_Nm == null || segment.localForce_end2_N_Nm == null ||
                segment.localForce_end1_N_Nm.Length != 6 || segment.localForce_end2_N_Nm.Length != 6) return false;
            double i = segment.localForce_end1_N_Nm[component];
            double j = segment.localForce_end2_N_Nm[component];
            if (!Finite(i) || !Finite(j)) return false;
            endI = i / 1000.0;
            // OpenSees end actions act on opposite faces. Use a common section
            // face for plotting, retaining raw actions in the explanatory label.
            endJ = -j / 1000.0;
            return true;
        }

        public static double SegmentLength(StructuralElementARData row, int index)
        {
            if (index < 0 || index >= SegmentCount(row)) return double.NaN;
            ARResultSegment segment = row.current_result_R.segments[index];
            if (segment == null) return double.NaN;
            double[] i = Coordinates(row, segment.node_i), j = Coordinates(row, segment.node_j);
            if (i == null || j == null) return double.NaN;
            double squared = 0;
            for (int axis = 0; axis < 3; axis++) squared += (j[axis] - i[axis]) * (j[axis] - i[axis]);
            return squared > 0 && Finite(squared) ? Math.Sqrt(squared) : double.NaN;
        }

        static double[] Coordinates(StructuralElementARData row, int tag)
        {
            if (row.current_result_R.node_displacements != null)
                foreach (ARNodeDisplacement node in row.current_result_R.node_displacements)
                    if (node != null && node.node_tag == tag && node.model_coord_m?.Length == 3 &&
                        Finite(node.model_coord_m[0]) && Finite(node.model_coord_m[1]) && Finite(node.model_coord_m[2]))
                        return node.model_coord_m;
            return null;
        }

        static bool Contains(int[] values, int value) => values != null && Array.IndexOf(values, value) >= 0;
        static bool Finite(double value) => !double.IsNaN(value) && !double.IsInfinity(value);
    }
}
