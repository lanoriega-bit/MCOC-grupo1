using System;
using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    public readonly struct ARResultSummary
    {
        public readonly double PkN;
        public readonly double VkN;
        public readonly double MkNm;
        public readonly double DisplacementMm;
        public readonly double DemandCapacity;
        public readonly bool HasDemandCapacity;

        ARResultSummary(double p, double v, double m, double displacement, double dc, bool hasDc)
        {
            PkN = p;
            VkN = v;
            MkNm = m;
            DisplacementMm = displacement;
            DemandCapacity = dc;
            HasDemandCapacity = hasDc;
        }

        public static bool TryCreate(StructuralElementARData data, out ARResultSummary summary)
        {
            summary = default;
            if (data?.current_result_R?.segments == null || data.current_result_R.segments.Length == 0)
                return false;

            double p = 0, vy = 0, vz = 0, my = 0, mz = 0;
            foreach (ARResultSegment segment in data.current_result_R.segments)
            {
                Accumulate(segment.localForce_end1_N_Nm, ref p, ref vy, ref vz, ref my, ref mz);
                Accumulate(segment.localForce_end2_N_Nm, ref p, ref vy, ref vz, ref my, ref mz);
            }
            double displacement = 0;
            if (data.current_result_R.node_displacements != null)
                foreach (ARNodeDisplacement node in data.current_result_R.node_displacements)
                    displacement = Math.Max(displacement, Math.Abs(node.magnitude_m) * 1000.0);

            double dc = 0;
            bool hasDc = TryDemandCapacity(data, p / 1000.0, my / 1000.0, mz / 1000.0,
                vy / 1000.0, vz / 1000.0, out dc);
            summary = new ARResultSummary(p / 1000.0, Math.Max(vy, vz) / 1000.0,
                Math.Max(my, mz) / 1000.0, displacement, dc, hasDc);
            return true;
        }

        static void Accumulate(double[] forces, ref double p, ref double vy, ref double vz, ref double my, ref double mz)
        {
            if (forces == null || forces.Length < 6) return;
            p = Math.Max(p, Math.Abs(forces[0]));
            vy = Math.Max(vy, Math.Abs(forces[1]));
            vz = Math.Max(vz, Math.Abs(forces[2]));
            my = Math.Max(my, Math.Abs(forces[4]));
            mz = Math.Max(mz, Math.Abs(forces[5]));
        }

        static bool TryDemandCapacity(StructuralElementARData data, double p, double my, double mz,
            double vy, double vz, out double dc)
        {
            dc = 0;
            ARElementCapacity wrapper = data.capacity;
            if (wrapper == null) return false;
            if (wrapper.beam_capacity != null)
            {
                ARBeamCapacity c = wrapper.beam_capacity;
                dc = MaxRatio(my, c.phi_Mny_kNm, mz, c.phi_Mnz_kNm,
                    vy, c.phi_Vy_kN, vz, c.phi_Vz_kN);
                return true;
            }
            ARPMPoint[] points = wrapper.capacity?.points_my ?? wrapper.capacity?.points;
            if (points == null || points.Length < 2) return false;
            double mCapacity = InterpolatedMomentCapacity(points, p);
            dc = mCapacity > 1e-9 ? Math.Max(my, mz) / mCapacity : double.PositiveInfinity;
            return true;
        }

        static double InterpolatedMomentCapacity(ARPMPoint[] points, double compression)
        {
            if (compression <= points[0].compression_magnitude_kN) return points[0].M_kNm;
            for (int i = 1; i < points.Length; i++)
            {
                double p1 = points[i].compression_magnitude_kN;
                if (compression > p1) continue;
                double p0 = points[i - 1].compression_magnitude_kN;
                double t = Math.Abs(p1 - p0) < 1e-9 ? 0 : (compression - p0) / (p1 - p0);
                return points[i - 1].M_kNm + (points[i].M_kNm - points[i - 1].M_kNm) * t;
            }
            return 0;
        }

        static double MaxRatio(double a, double ca, double b, double cb, double c, double cc, double d, double cd)
        {
            double ratio = 0;
            if (ca > 0) ratio = Math.Max(ratio, a / ca);
            if (cb > 0) ratio = Math.Max(ratio, b / cb);
            if (cc > 0) ratio = Math.Max(ratio, c / cc);
            if (cd > 0) ratio = Math.Max(ratio, d / cd);
            return ratio;
        }
    }
}
