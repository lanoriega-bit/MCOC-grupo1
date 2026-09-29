using System;
using System.Collections.Generic;

namespace Mcoc.UnityViewer
{
    public enum StructuralFailureState { OK, WARNING, CAPACITY_EXCEEDED, NO_DATA }

    [Serializable]
    public sealed class CurrentElementDemand
    {
        public string elementTag;
        public string elementType;
        public string caseName;
        public string controllingAnalysisId;
        public int controllingOpenSeesTag;
        public double N_kN;
        public double Vy_kN;
        public double Vz_kN;
        public double My_kNm;
        public double Mz_kNm;
    }

    [Serializable]
    public sealed class FailureResult
    {
        public string elementTag;
        public string elementType;
        public string caseName;
        public StructuralFailureState state;
        public string governingMode;
        public double demandCapacityRatio;
        public double governingDemand;
        public double governingCapacity;
        public string demandUnit;
        public CurrentElementDemand demand;
        public string controllingAnalysisId;
        public int controllingOpenSeesTag;
        public string message;
    }

    /// <summary>
    /// Pure capacity check. It has no Unity rendering dependency and can therefore
    /// be reused by the desktop viewer and a future AR presentation.
    /// </summary>
    public static class StructuralFailureEvaluator
    {
        public const double WarningThreshold = 0.80;
        public const double ExceededThreshold = 1.00;

        public static FailureResult Evaluate(CurrentElementDemand demand, DemandCapacityElement capacity)
        {
            if (demand == null) return NoData(null, "NO CURRENT DEMAND DATA");
            if (capacity == null) return NoData(demand, "NO CAPACITY DATA");
            if (string.Equals(demand.elementType, "beam", StringComparison.OrdinalIgnoreCase))
                return EvaluateBeam(demand, capacity.beam_capacity);
            if (string.Equals(demand.elementType, "column", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(demand.elementType, "wall", StringComparison.OrdinalIgnoreCase))
                return EvaluateInteraction(demand, capacity.capacity);
            return NoData(demand, "UNSUPPORTED ELEMENT TYPE");
        }

        static FailureResult EvaluateBeam(CurrentElementDemand d, BeamCapacityData c)
        {
            if (c == null || !string.Equals(c.status, "PASS", StringComparison.OrdinalIgnoreCase))
                return NoData(d, "NO VALID BEAM CAPACITY DATA");
            var checks = new List<ModeCheck>();
            Add(checks, "MOMENT_Y", Math.Abs(d.My_kNm), c.phi_Mny_kNm, "kN·m");
            Add(checks, "MOMENT_Z", Math.Abs(d.Mz_kNm), c.phi_Mnz_kNm, "kN·m");
            Add(checks, "SHEAR_Y", Math.Abs(d.Vy_kN), c.phi_Vy_kN, "kN");
            Add(checks, "SHEAR_Z", Math.Abs(d.Vz_kN), c.phi_Vz_kN, "kN");
            // The CURRENT beam contract has no axial capacity. Do not invent DC_N.
            if (checks.Count == 0) return NoData(d, "NO POSITIVE BEAM CAPACITY");
            ModeCheck governing = checks[0];
            foreach (var check in checks) if (check.ratio > governing.ratio) governing = check;
            return Result(d, governing.mode, governing.ratio, governing.demand, governing.capacity, governing.unit);
        }

        static FailureResult EvaluateInteraction(CurrentElementDemand d, DemandCapacityCurve curve)
        {
            if (curve == null) return NoData(d, "NO P-M CAPACITY CURVE");
            double axial = Math.Abs(d.N_kN);
            var checks = new List<ModeCheck>();
            AddInteraction(checks, "PM_INTERACTION_MY", axial, Math.Abs(d.My_kNm), curve.points_my ?? curve.points);
            AddInteraction(checks, "PM_INTERACTION_MZ", axial, Math.Abs(d.Mz_kNm), curve.points_mz ?? curve.points);
            if (checks.Count == 0) return NoData(d, "DEMAND OUTSIDE VALID P-M DATA RANGE");
            ModeCheck governing = checks[0];
            foreach (var check in checks) if (check.ratio > governing.ratio) governing = check;
            return Result(d, "PM_INTERACTION" + (governing.mode.EndsWith("MZ") ? "_MZ" : "_MY"),
                governing.ratio, governing.demand, governing.capacity, "kN·m");
        }

        static void AddInteraction(List<ModeCheck> checks, string mode, double axial, double moment,
            List<DemandCapacityPoint> source)
        {
            if (source == null) return;
            var points = new List<DemandCapacityPoint>();
            foreach (var p in source)
                if (p != null && p.valid && p.compression_magnitude_kN >= 0 && p.M_kNm >= 0) points.Add(p);
            points.Sort((a, b) => a.compression_magnitude_kN.CompareTo(b.compression_magnitude_kN));
            if (points.Count < 2) return;
            double capacity;
            if (axial > points[points.Count - 1].compression_magnitude_kN)
            {
                // Demand beyond the verified compression envelope is an exceedance,
                // not an apparently safe point and not an extrapolated capacity.
                checks.Add(new ModeCheck(mode, moment, 0, double.PositiveInfinity, "kN·m"));
                return;
            }
            if (axial < points[0].compression_magnitude_kN) return;
            for (int i = 0; i < points.Count - 1; i++)
            {
                double p0 = points[i].compression_magnitude_kN;
                double p1 = points[i + 1].compression_magnitude_kN;
                if (axial < p0 || axial > p1) continue;
                double t = Math.Abs(p1 - p0) < 1e-12 ? 0 : (axial - p0) / (p1 - p0);
                capacity = points[i].M_kNm + t * (points[i + 1].M_kNm - points[i].M_kNm);
                if (capacity > 0) checks.Add(new ModeCheck(mode, moment, capacity, moment / capacity, "kN·m"));
                return;
            }
        }

        static void Add(List<ModeCheck> checks, string mode, double demand, double capacity, string unit)
        {
            if (capacity > 0 && !double.IsNaN(capacity) && !double.IsInfinity(capacity))
                checks.Add(new ModeCheck(mode, demand, capacity, demand / capacity, unit));
        }

        static FailureResult Result(CurrentElementDemand d, string mode, double ratio, double demand,
            double capacity, string unit)
        {
            var state = ratio >= ExceededThreshold ? StructuralFailureState.CAPACITY_EXCEEDED
                : ratio >= WarningThreshold ? StructuralFailureState.WARNING : StructuralFailureState.OK;
            return new FailureResult {
                elementTag = d.elementTag, elementType = d.elementType, caseName = d.caseName,
                state = state, governingMode = mode, demandCapacityRatio = ratio,
                governingDemand = demand, governingCapacity = capacity, demandUnit = unit,
                demand = d, controllingAnalysisId = d.controllingAnalysisId,
                controllingOpenSeesTag = d.controllingOpenSeesTag,
                message = state == StructuralFailureState.CAPACITY_EXCEEDED
                    ? "La demanda lineal combinada excede la capacidad calculada; no simula post-colapso."
                    : "Evaluación algebraica sobre resultados CURRENT."
            };
        }

        static FailureResult NoData(CurrentElementDemand d, string message)
        {
            return new FailureResult {
                elementTag = d != null ? d.elementTag : "", elementType = d != null ? d.elementType : "",
                caseName = d != null ? d.caseName : "", state = StructuralFailureState.NO_DATA,
                governingMode = "NO_DATA", demandCapacityRatio = double.NaN,
                governingDemand = double.NaN, governingCapacity = double.NaN,
                demand = d, controllingAnalysisId = d != null ? d.controllingAnalysisId : "",
                controllingOpenSeesTag = d != null ? d.controllingOpenSeesTag : 0, message = message
            };
        }

        sealed class ModeCheck
        {
            public readonly string mode, unit;
            public readonly double demand, capacity, ratio;
            public ModeCheck(string mode, double demand, double capacity, double ratio, string unit)
            { this.mode = mode; this.demand = demand; this.capacity = capacity; this.ratio = ratio; this.unit = unit; }
        }
    }
}
