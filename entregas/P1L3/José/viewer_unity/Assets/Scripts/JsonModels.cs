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
    public class VisualLinesData
    {
        public string format;
        public string units;
        public List<SegmentData> segments;
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
        public string id;
        public string human_id;
        public string building;
        public string elementTag;
        public string floor;
        public string floor_label;
        public string source_dxf;
        public string source_layer;
        public string category;
        public List<List<double>> points;
        public List<double> points_flat;
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
        public string id;
        public string human_id;
        public string building;
        public string floor;
        public string category;
        public List<List<double>> points;
        public List<double> points_flat;
    }

    [Serializable]
    public class ArchitecturalVisualModelData
    {
        public string format;
        public string units;
        public string scope;
        public string analysis_contract;
        public bool participates_in_FE;
        public List<ArchitecturalObjectData> objects;
    }

    [Serializable]
    public class ArchitecturalObjectData
    {
        public string id;
        public string building;
        public string floor;
        public string category;
        public string type;
        public string source;
        public string source_sheet;
        public string source_layer;
        public string confidence;
        public bool participates_in_FE;
        public double top_z_m;
        public double thickness_m;
        public double area_m2;
        public List<List<double>> outline_xy;
        public List<List<double>> surface_vertices_xy;
        public List<double> outline_xy_flat;
        public List<double> surface_vertices_xy_flat;
        public List<int> surface_triangles;
        public List<string> confirmed_source_segment_ids;
        public List<string> supporting_beam_ids;
        public List<ArchitecturalClosureData> inferred_closures;
        public List<string> notes;
    }

    [Serializable]
    public class ArchitecturalClosureData
    {
        public List<double> start;
        public List<double> end;
        public double length_m;
        public string confidence;
        public string reason;
        public string evidence;
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
        public List<AnalysisNodeResult> nodes;
        public List<ExcludedAnalysisElement> excluded_elements;
    }

    [Serializable]
    public class AnalysisCasesData
    {
        public string format;
        public string default_case;
        public List<AnalysisResultsData> cases;
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
    public class AnalysisNodeResult
    {
        public int node_tag;
        public string floor;
        public List<double> coord;
        public double ux_m;
        public double uy_m;
        public double uz_m;
    }

    [Serializable]
    public class ExcludedAnalysisElement
    {
        public string element_id;
        public string analysis_id;
        public string geometry_elementTag;
        public string reason;
    }

    // ---------- P1L4 Jose: exportador OpenSees -> JSON/CSV ----------
    // Contrato P1L4_JOSE_INTERNAL_FORCES_v1 (fuerzas_internas/{CASE}.json)

    [Serializable]
    public class JoseInternalForcesData
    {
        public string format;
        public string run_id;
        public string case_name;
        public string status;
        public int element_count;
        public List<JoseElementForce> elements;
    }

    [Serializable]
    public class JoseElementForce
    {
        public string case_name;
        public int opensees_element_tag;
        public string element_id;
        public string analysis_id;
        public string geometry_elementTag;
        public string type;
        public string floor;
        public int node_i;
        public int node_j;
        public double N_end1;
        public double Vy_end1;
        public double Vz_end1;
        public double T_end1;
        public double My_end1;
        public double Mz_end1;
        public double N_end2;
        public double Vy_end2;
        public double Vz_end2;
        public double T_end2;
        public double My_end2;
        public double Mz_end2;
    }

    [Serializable]
    public class JoseDisplacementsData
    {
        public string format;
        public string run_id;
        public string case_name;
        public string status;
        public int node_count;
        public List<JoseNodeDisplacement> nodes;
    }

    [Serializable]
    public class JoseNodeDisplacement
    {
        public int node_tag;
        public string floor;
        public double ux_m;
        public double uy_m;
        public double uz_m;
        public double rx_rad;
        public double ry_rad;
        public double rz_rad;
    }

    [Serializable]
    public class JoseSupportsData
    {
        public string format;
        public string status;
        public int support_count;
        public List<JoseSupport> supports;
    }

    [Serializable]
    public class JoseSupport
    {
        public int node_tag;
        public string level;
        public int UX;
        public int UY;
        public int UZ;
        public int RX;
        public int RY;
        public int RZ;
    }

    // ---------- P1L4 Luis: demanda-capacidad P-M ----------
    // Contrato P1L4_UNITY_DEMAND_CAPACITY_v1 (demanda_capacidad.json)

    [Serializable]
    public class DemandaCapacidadData
    {
        public string format;
        public string active_case;
        public List<DemandaCapacidadElement> elements;
    }

    [Serializable]
    public class DemandaCapacidadElement
    {
        public string element_id;
        public string structural_id;
        public string type;
        public int opensees_tag;
        public string geometry_elementTag;
        public string analysis_id;
        public List<int> nodes;
        public DemandaCapacidadDemand demand;
        public DemandaCapacidadCapacity capacity;
        public DemandaCapacidadResult demand_capacity;
    }

    [Serializable]
    public class DemandaCapacidadDemand
    {
        public string case_name;
        public string selected_end;
        public string pm_component;
        public double P_kN;
        public double Vy_kN;
        public double Vz_kN;
        public double T_kNm;
        public double My_kNm;
        public double Mz_kNm;
    }

    [Serializable]
    public class DemandaCapacidadCapacity
    {
        public string status;
        public string pm_axis;
        public string source;
    }

    [Serializable]
    public class DemandaCapacidadResult
    {
        public double P_kN;
        public double compression_magnitude_kN;
        public double M_kNm;
        public double M_abs_kNm;
        public string pm_axis;
        public bool inside_envelope;
        public double interpolated_capacity_M_abs_kNm;
        public string method;
    }

    [Serializable]
    public class FeDiagnosticData
    {
        public string format;
        public string status;
        public string source_candidate;
        public FeDiagnosticSummary summary;
        public List<FeDiagnosticElement> elements;
        public List<FeCandidateMember> members;
    }

    [Serializable]
    public class FeDiagnosticSummary
    {
        public int baseline_floating_elements;
        public int baseline_components;
        public int candidate_floating_fe_segments;
        public int candidate_floating_geometry_elements;
        public int candidate_floating_components;
        public int node_count;
        public int fe_element_count;
        public int constraint_count;
        public int geometry_elements_split_into_multiple_fe;
        public int max_fe_segments_per_geometry;
        public int focus_elements;
        public int mapped_geometry_elements;
    }

    [Serializable]
    public class FeDiagnosticElement
    {
        public string element_id;
        public string type;
        public string building;
        public string floor;
        public string structural_classification;
        public string validation;
        public bool connected_in_candidate;
        public bool diagnostic_focus;
        public string component_id;
        public string motive;
        public string expected_connection;
        public string evidence;
        public List<string> connection_types;
        public string source_dxf;
        public string source_layer;
        public string prior_diagnosis;
        public List<FeCrosswalkEntry> crosswalk;
    }

    [Serializable]
    public class FeCrosswalkEntry
    {
        public string analysis_id;
        public int opensees_element_tag;
        public string element_id;
        public string geometryElementTag;
        public int geometry_segment_index;
        public string type;
        public string building;
        public string floor;
        public int node_i;
        public int node_j;
        public int opensees_node_i;
        public int opensees_node_j;
    }

    [Serializable]
    public class FeCandidateMember
    {
        public string analysis_id;
        public int opensees_element_tag;
        public string element_id;
        public string geometryElementTag;
        public int geometry_segment_index;
        public string type;
        public string building;
        public string floor;
        public int node_i;
        public int node_j;
        public bool diagnostic_focus;
        public string validation;
        public List<double> start;
        public List<double> end;
    }

    [Serializable]
    public class CapacityData
    {
        public string format;
        public string section_id;
        public string building_column_id;
        public string building_column_origin;
        public string mapped_element_id;
        public string mapped_analysis_id;
        public double mapping_distance_m;
        public string mapping_status;
        public string mapping_note;
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
        public List<MomentCurvaturePoint> moment_curvature;
        public List<PMPoint> pm_interaction;
        public string disclaimer;
    }

    [Serializable]
    public class MomentCurvaturePoint
    {
        public double step;
        public double curvature_1_per_m;
        public double moment_kNm;
        public bool converged;
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

    [Serializable]
    public class P1L3DeliveryData
    {
        public string format;
        public string status;
        public List<string> limitations;
        public DeliveryGravity gravity;
        public DeliverySeismic seismic;
        public DeliverySuperposition superposition;
        public List<DeliveryCase> cases;
    }

    [Serializable]
    public class DeliveryGravity
    {
        public int panel_count;
        public double G_transferred_kN;
        public double Q_transferred_kN;
        public double Q_expected_kN;
        public double Q_conservation_rel_error;
        public string status;
    }

    [Serializable]
    public class DeliverySeismic
    {
        public double base_shear_coefficient;
        public double total_EX_kN;
        public double total_EY_kN;
        public double base_shear_EX_kN;
        public double base_shear_EY_kN;
        public double EX_rel_error;
        public double EY_rel_error;
        public string EX_deformed_status;
        public string EY_deformed_status;
        public double max_application_point_error_m;
        public string status;
    }

    [Serializable]
    public class DeliverySuperposition
    {
        public double lambda_G;
        public double lambda_Q;
        public double lambda_EX;
        public double lambda_EY;
        public double displacement_rel_error;
        public double reaction_rel_error;
        public double internal_force_rel_error;
        public string status;
    }

    [Serializable]
    public class DeliveryCase
    {
        public string case_name;
        public double max_displacement_m;
        public int max_node_tag;
        public string max_floor;
        public double ux_m;
        public double uy_m;
        public double uz_m;
        public double sum_Rx_kN;
        public double sum_Ry_kN;
        public double sum_Rz_kN;
    }

    [Serializable]
    public class P1L4StructuralMetadataData
    {
        public string format;
        public string data_state;
        public string source;
        public P1L4Units units;
        public P1L4Material material;
        public List<P1L4CaseDescriptor> cases;
        public List<P1L4ElementMetadata> elements;
        public List<P1L4SupportData> supports;
        public P1L4MetadataQa qa;
    }

    [Serializable]
    public class P1L4Units
    {
        public string length;
        public string force;
        public string moment;
        public string stress;
    }

    [Serializable]
    public class P1L4Material
    {
        public string material_id;
        public string model;
        public double E_pa;
        public double nu;
        public double G_pa;
        public string source;
    }

    [Serializable]
    public class P1L4CaseDescriptor
    {
        public string case_id;
        public string folder;
        public int element_count;
        public int node_count;
        public string manifest_source;
        public string elements_source;
        public string nodes_source;
    }

    [Serializable]
    public class P1L4ElementMetadata
    {
        public string element_id;
        public string geometry_elementTag;
        public string analysis_id;
        public int opensees_tag;
        public string type;
        public string building;
        public string floor;
        public int node_i;
        public int node_j;
        public List<double> node_i_coord_m;
        public List<double> node_j_coord_m;
        public string section_id;
        public P1L4Section section;
        public string material_id;
        public P1L4LocalAxes local_axes;
        public string source_layer;
        public string source_dxf;
    }

    [Serializable]
    public class P1L4Section
    {
        public double A_m2;
        public double Iy_m4;
        public double Iz_m4;
        public double J_m4;
        public double dim_local_y_m;
        public double dim_local_z_m;
        public string source;
    }

    [Serializable]
    public class P1L4LocalAxes
    {
        public List<double> x;
        public List<double> y;
        public List<double> z;
        public List<double> vecxz;
        public string source;
    }

    [Serializable]
    public class P1L4SupportData
    {
        public string support_id;
        public int node_tag;
        public string floor;
        public List<double> coord_m;
        public bool UX;
        public bool UY;
        public bool UZ;
        public bool RX;
        public bool RY;
        public bool RZ;
    }

    [Serializable]
    public class P1L4MetadataQa
    {
        public int element_count;
        public int unique_opensees_tags;
        public int unique_analysis_ids;
        public int support_count;
        public bool all_nodes_exist;
        public bool all_local_axes_unit_and_orthogonal;
    }

    [Serializable]
    public class DemandCapacityData
    {
        public string format;
        public string active_case;
        public DemandCapacityValidation validation;
        public List<DemandCapacityElement> elements;
    }

    [Serializable]
    public class DemandCapacityValidation
    {
        public string status;
        public List<int> required_tags;
        public int wall_valid_pm_points;
        public int wall_invalid_pm_points;
    }

    [Serializable]
    public class DemandCapacityElement
    {
        public string element_id;
        public string structural_id;
        public string type;
        public int opensees_tag;
        public string geometry_elementTag;
        public string analysis_id;
        public List<int> nodes;
        public string section_id;
        public DemandCapacityDemand demand;
        public DemandCapacityCurve capacity;
        public DemandCapacityCheck demand_capacity;
        public DemandCapacityTraceability traceability;
    }

    [Serializable]
    public class DemandCapacityDemand
    {
        public string case_name;
        public string source_file;
        public string selection_rule;
        public string selected_end;
        public double P_kN;
        public double Vy_kN;
        public double Vz_kN;
        public double T_kNm;
        public double My_kNm;
        public double Mz_kNm;
        public string pm_component;
    }

    [Serializable]
    public class DemandCapacityCurve
    {
        public string status;
        public string pm_axis;
        public string source;
        public string note;
        public List<DemandCapacityPoint> points;
        public string invalid_points_note;
    }

    [Serializable]
    public class DemandCapacityPoint
    {
        public string point_id;
        public double P_kN;
        public double compression_magnitude_kN;
        public double M_kNm;
        public bool valid;
        public string status;
    }

    [Serializable]
    public class DemandCapacityCheck
    {
        public string @case;
        public double P_kN;
        public double compression_magnitude_kN;
        public double M_kNm;
        public double M_abs_kNm;
        public string pm_axis;
        public bool inside_envelope;
        public double interpolated_capacity_M_abs_kNm;
        public string method;
    }

    [Serializable]
    public class DemandCapacityTraceability
    {
        public string geometry_source;
        public string analysis_source;
        public string demand_source;
        public string capacity_source;
        public string capacity_section_config;
        public string case_manifest;
    }

    [Serializable]
    public class P1L4LoadCatalogData
    {
        public string format;
        public string data_state;
        public string source;
        public bool is_structurally_applied;
        public int entry_count;
        public int drawable_entry_count;
        public List<P1L4LoadEntryData> entries;
    }

    [Serializable]
    public class P1L4LoadEntryData
    {
        public string load_id;
        public string load_type;
        public string building;
        public string floor;
        public string source_sheet;
        public double source_value;
        public string source_unit;
        public double SI_value;
        public string SI_unit;
        public string confidence;
        public string application_status;
        public string geometry_type;
        public List<double> coordinates_xy_flat;
        public List<string> receiver_ids;
        public string receiver_status;
    }

    [Serializable]
    public class PhysicalContextData
    {
        public string format;
        public string status;
        public string data_state;
        public bool participates_in_FE;
        public bool opensees_changed;
        public bool historical_results_changed;
        public bool terrain_surface_generated;
        public string terrain_note;
        public List<PhysicalContextCluster> clusters;
        public List<PhysicalContextLevelMarker> level_markers;
        public List<PhysicalContextClassification> classifications;
    }

    [Serializable]
    public class PhysicalContextCluster
    {
        public string id;
        public string label;
        public string floor;
        public List<double> center;
        public List<double> size;
        public string color;
        public List<string> element_ids;
        public string note;
        public bool participates_in_FE;
    }

    [Serializable]
    public class PhysicalContextLevelMarker
    {
        public string id;
        public string label;
        public string floor;
        public List<double> start;
        public List<double> end;
        public string color;
        public bool participates_in_FE;
    }

    [Serializable]
    public class PhysicalContextClassification
    {
        public string element_id;
        public string cluster;
        public string physical_geometry;
        public string physical_classification;
        public string physical_support;
        public string main_fe_participation;
        public string revised_diagnostic;
        public string duplicate_classification;
        public string evidence;
    }
}
