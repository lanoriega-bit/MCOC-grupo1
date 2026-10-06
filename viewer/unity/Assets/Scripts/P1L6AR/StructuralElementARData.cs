using System;

namespace Mcoc.UnityViewer.P1L6AR
{
    [Serializable] public sealed class ARDatasetRoot
    {
        public string format;
        public string status;
        public ARDatasetHashes hashes;
        public ARDemoElement[] demo_elements;
        public StructuralElementARData[] elements;
    }

    [Serializable] public sealed class ARDatasetHashes
    {
        public string model_master_sha256;
        public string analysis_sha256;
        public string capacity_sha256;
        public string loads_sha256;
    }

    [Serializable] public sealed class ARDemoElement
    {
        public string element_id;
        public string purpose;
        public bool has_results;
        public bool has_capacity;
        public bool has_load_contract;
    }

    [Serializable] public sealed class StructuralElementARData
    {
        public string element_id;
        public string elementTag;
        public string solidTag;
        public int[] opensees_tags;
        public int[] fe_node_tags;
        public string type;
        public string building;
        public string floor;
        public ARCoordinates model_coordinates_m;
        public ARCoordinates unity_coordinates_m;
        public double[] orientation_model;
        public double[] orientation_unity;
        public double length_m;
        public ARPhysicalGeometry geometry;
        public ARSectionDimensions dimensions;
        public ARSection section;
        public ARMaterial material;
        public ARCurrentResult current_result_R;
        public ARElementCapacity capacity;
        public string data_state;
    }

    // Physical geometry is in model coordinates: model Z is Unity Y.
    [Serializable] public sealed class ARPhysicalGeometry
    {
        public double[] start_m;
        public double[] end_m;
        public double[] center_m;
        public double z_bottom_m;
        public double z_top_m;
        public double length_m;
        public double[] direction_unit;
    }

    [Serializable] public sealed class ARCoordinates
    {
        public double[] start;
        public double[] end;
        public double[] center;
    }

    [Serializable] public sealed class ARSection
    {
        public string section_id;
        public string type;
        public string units;
        public string status;
        public ARSectionDimensions dimensions;
    }

    [Serializable] public sealed class ARSectionDimensions
    {
        public double width_m;
        public double height_m;
        public double depth_m;
        public double thickness_m;
        public double length_m;
    }

    [Serializable] public sealed class ARMaterial
    {
        public string material_id;
        public string name;
        public string scope;
    }

    [Serializable] public sealed class ARCurrentResult
    {
        public ARResultCoefficients coefficients;
        public ARResultSegment[] segments;
        public ARNodeDisplacement[] node_displacements;
    }

    [Serializable] public sealed class ARResultCoefficients
    {
        public double G;
        public double Q;
        public double EX;
        public double EY;
    }

    [Serializable] public sealed class ARResultSegment
    {
        public string analysis_id;
        public int opensees_tag;
        public int node_i;
        public int node_j;
        public double[] localForce_end1_N_Nm;
        public double[] localForce_end2_N_Nm;
    }

    [Serializable] public sealed class ARNodeDisplacement
    {
        public int node_tag;
        public double[] model_coord_m;
        public double[] unity_coord_m;
        public double[] displacement_model_m;
        public double[] displacement_unity_m;
        public double magnitude_m;
    }

    [Serializable] public sealed class ARElementCapacity
    {
        public string element_id;
        public string structural_id;
        public string type;
        public int opensees_tag;
        public string geometry_elementTag;
        public string analysis_id;
        public string section_id;
        public ARPMCapacity capacity;
        public ARBeamCapacity beam_capacity;
    }

    [Serializable] public sealed class ARPMCapacity
    {
        public string status;
        public string pm_axis;
        public string assumption_status;
        public ARPMPoint[] points;
        public ARPMPoint[] points_my;
        public ARPMPoint[] points_mz;
    }

    [Serializable] public sealed class ARPMPoint
    {
        public string point_id;
        public double P_kN;
        public double compression_magnitude_kN;
        public double M_kNm;
        public bool valid;
        public string status;
    }

    [Serializable] public sealed class ARBeamCapacity
    {
        public string status;
        public string assumption_status;
        public double phi_Mny_kNm;
        public double phi_Mnz_kNm;
        public double phi_Vy_kN;
        public double phi_Vz_kN;
    }
}
