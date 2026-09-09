using System;
using System.Collections.Generic;

namespace Mcoc.UnityViewer
{
    [Serializable]
    public class ModelData
    {
        public string model;
        public string units;
        public List<string> availableToggles;
        public ModelColors colors;
        public List<SolidData> solids;
        public List<SegmentData> segments;
        public List<LabelData> labels;
        public List<DiaphragmData> diaphragms;
    }

    [Serializable]
    public class ModelColors
    {
        public string beam;
        public string wall;
        public string column;
        public string column_plan;
        public string slab_edge;
        public string slab;
        public string slab_label;
        public string axis;
        public string diaphragm;
        public string support;
        public string cad_reference;
        public string node;
    }

    [Serializable]
    public class SolidData
    {
        public string solidTag;
        public string category;
        public string kind;
        public string floor;
        public string sourceTag;
        public string source_layer;
        public string source_dxf;
        public List<double> start;
        public List<double> end;
        public List<double> center;
        public double width_m;
        public double height_m;
        public double depth_m;
        public double length_m;
        public string confidence;
        public string material;
        public string id;
        public string human_id;
        public string elementTag;
        public string building;
        public string axis_x;
        public string axis_y;
        public string source_elevation_m;
        public double model_z_m;
    }

    [Serializable]
    public class SegmentData
    {
        public string elementTag;
        public string floor;
        public string floor_label;
        public string source_dxf;
        public string source_layer;
        public string category;
        public List<List<double>> points;
        public double length_m;
        public string confidence;
    }

    [Serializable]
    public class LabelData
    {
        public string labelTag;
        public string floor;
        public string floor_label;
        public string source_dxf;
        public string source_layer;
        public string category;
        public string text;
        public List<double> point;
        public SectionHint section_hint;
    }

    [Serializable]
    public class SectionHint
    {
        public string kind;
        public double width_m;
        public double height_m;
    }

    [Serializable]
    public class DiaphragmData
    {
        public string floor;
        public string category;
        public List<List<double>> points;
    }

    [Serializable]
    public class NodeData
    {
        public string id;
        public List<double> point;
        public string floor;
    }

    [Serializable]
    public class TributaryData
    {
        public string units;
        public double qG_kN_m2;
        public double total_area_m2;
        public double total_load_kN;
        public TributaryFloorMap buildings;
        public List<TributaryArea> areas;
        public List<TributaryPointArea> point_areas;
    }

    [Serializable]
    public class TributaryFloorMap
    {
        public TributaryBuildingMap EDIFICIO_1;
        public TributaryBuildingMap EDIFICIO_2;
    }

    [Serializable]
    public class TributaryBuildingMap
    {
        public TributaryFloor S1;
        public TributaryFloor P1;
        public TributaryFloor P2;
        public TributaryFloor P3;
        public TributaryFloor P4;
    }

    [Serializable]
    public class TributaryFloor
    {
        public double area_m2;
        public double load_kN;
    }

    [Serializable]
    public class TributaryArea
    {
        public string building;
        public string floor;
        public string beam_id;
        public string elementTag;
        public List<double> start;
        public List<double> end;
        public List<double> mid;
        public double area_m2;
        public double load_kN;
        public List<Point2D> polygon;
    }

    [Serializable]
    public class TributaryPointArea
    {
        public string building;
        public string floor;
        public string member_category;
        public string member_id;
        public string elementTag;
        public double area_m2;
        public double load_kN;
        public List<Point2D> polygon;
    }

    [Serializable]
    public class Point2D
    {
        public double x;
        public double y;
    }

    [Serializable]
    public class SeismicData
    {
        public string units;
        public double qG_kN_m2;
        public double psi_Q;
        public double base_shear_coefficient;
        public List<SeismicBuilding> buildings;
        public List<SeismicFloor> floors;
    }

    [Serializable]
    public class SeismicBuilding
    {
        public string building;
        public double total_w_seismic_kN;
        public double total_mass_ton;
        public double cm_x_m;
        public double cm_y_m;
        public double V_EX_kN;
        public double V_EY_kN;
        public List<SeismicFloor> floors_EX;
        public List<SeismicFloor> floors_EY;
    }

    [Serializable]
    public class SeismicFloor
    {
        public string building;
        public string floor;
        public double z_m;
        public double area_m2;
        public double wG_kN;
        public double wQ_kN;
        public double w_seismic_kN;
        public double mass_ton;
        public double cm_x;
        public double cm_y;
        public double Lx_m;
        public double Ly_m;
        public double F_kN;
        public double F_EX_kN;
        public double F_EY_kN;
        public double story_shear_EX_kN;
        public double story_shear_EY_kN;
        public double e_accidental_m;
        public double M_torsion_EX_kNm;
        public double M_torsion_EY_kNm;
        public double M_torsion_accidental_kNm;
    }

    [Serializable]
    public class AnalysisResultsData
    {
        public string format;
        public string run_id;
        public string case_name;
        public List<AnalysisElementResult> elements;
        public List<ExcludedAnalysisElement> excluded_elements;
    }

    [Serializable]
    public class AnalysisElementResult
    {
        public string case_name;
        public string element_id;
        public string analysis_id;
        public string geometry_elementTag;
        public int opensees_tag;
        public string type;
        public string floor;
        public int node_i;
        public int node_j;
        public List<double> localForce_end1;
        public List<double> localForce_end2;
    }

    [Serializable]
    public class ExcludedAnalysisElement
    {
        public string element_id;
        public string analysis_id;
        public string geometry_elementTag;
        public string reason;
    }

    [Serializable]
    public class CapacityData
    {
        public string format;
        public string section_id;
        public string building_column_id;
        public string building_column_origin;
        public string mapped_element_id;
        public double b_m;
        public double h_m;
        public double cover_m;
        public int num_bars;
        public double bar_diameter_m;
        public double fc_pa;
        public double fy_pa;
        public double Es_pa;
        public int num_fibers_y;
        public int num_fibers_z;
        public List<PMPoint> pm_interaction;
        public string disclaimer;
    }

    [Serializable]
    public class PMPoint
    {
        public string case_name;
        public double axial_load_kN;
        public double compression_magnitude_kN;
        public double max_moment_kNm;
        public double curvature_at_max_1_per_m;
        public double converged_steps;
        public string status;
    }
}
