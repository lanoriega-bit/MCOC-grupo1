using System;
using System.Collections.Generic;

namespace Mcoc.Semana2.UnityE1
{
    [Serializable]
    public class E1GravityData
    {
        public string formato;
        public string building_id;
        public List<string> buildings;
        public E1Units units;
        public string qG_definicion;
        public List<int> pisos_presentes;
        public string alcance;
        public List<int> gravedad_verificada_pisos;
        public List<E1Blocker> geometric_blockers;
        public List<E1Slab> losas;
        public List<E1Beam> vigas;
        public List<E1GenericElement> nodes;
        public List<E1GenericElement> columns;
        public List<E1GenericElement> walls;
        public List<E1GenericElement> supports;
        public List<E1GenericElement> diaphragms;
        public E1Verification verificacion;
    }

    [Serializable]
    public class E1Units
    {
        public string length;
        public string force;
        public string load;
    }

    [Serializable]
    public class E1Slab
    {
        public string building_id;
        public string slab_id;
        public int floor_id;
        public List<List<double>> vertices;
        public double? area_efectiva_m2;
        public double? openings_area_m2;
        public double? thickness_m;
        public double? pp_kN_m2;
        public double? pm_adic_kN_m2;
        public double? qG_kN_m2;
        public double? total_carga_kN;
        public string load_type_id;
        public double? sc_kN_m2;
        public string source_plan;
        public string load_status;
        public List<string> receiver_beam_ids;
        public double? tributary_area_m2;
        public List<E1TributaryPolygon> tributary_polygons;
        public double? transferred_load_kN;
        public List<E1LineLoad> line_loads_kN_m;
        public bool gravity_verified;
        public string status;
        public List<string> member_slab_ids;
        public List<string> pending_reasons;
        public bool geometry_blocked;
        public string final_reason;
    }

    [Serializable]
    public class E1Beam
    {
        public string building_id;
        public string beam_id;
        public int floor_id;
        public List<double> node_i;
        public List<double> node_j;
        public E1Coordinates coordenadas;
        public double longitud_m;
        public List<string> slab_ids;
        public List<string> member_slab_ids;
        public List<E1TributaryPolygon> poligonos_tributarios;
        public double area_tributaria_m2;
        public double? qG_kN_m2;
        public double P_kN;
        public double w_lineal_kN_m;
        public bool gravity_verified;
        public E1Section section;
    }

    [Serializable]
    public class E1Coordinates
    {
        public List<double> node_i;
        public List<double> node_j;
    }

    [Serializable]
    public class E1Section
    {
        public double? width_m;
        public double? height_m;
        public double? b;
        public double? h;
    }

    [Serializable]
    public class E1TributaryPolygon
    {
        public string slab_id;
        public string beam_id;
        public double area_m2;
        public List<List<double>> polygon;
    }

    [Serializable]
    public class E1LineLoad
    {
        public string beam_id;
        public double w_lineal_kN_m;
    }

    [Serializable]
    public class E1Blocker
    {
        public string building_id;
        public string slab_id;
        public string floor;
        public int floor_id;
        public List<string> reasons;
        public double area_m2;
        public string status;
        public List<E1ResolutionAttempt> resolution_attempts;
        public string final_reason;
    }

    [Serializable]
    public class E1ResolutionAttempt
    {
        public string strategy;
        public string result;
        public List<double> tolerances_m;
        public List<double> gaps_m;
        public double? candidate_area_m2;
        public string reason;
    }

    [Serializable]
    public class E1Verification
    {
        public double suma_tributarias_m2;
        public double suma_area_efectiva_cargada_m2;
        public double diferencia_area_m2;
        public double suma_P_kN;
        public double suma_qG_area_efectiva_kN;
        public double diferencia_carga_kN;
        public int num_vigas_cargadas;
        public int num_losas_cargadas;
    }

    [Serializable]
    public class E1GenericElement
    {
        public string building_id;
        public string id;
        public string node_id;
        public string column_id;
        public string wall_id;
        public string support_id;
        public string diaphragm_id;
        public string category;
        public string kind;
        public string floor;
        public string sourceTag;
        public string source_layer;
        public string source_dxf;
        public string confidence;
        public string visual_source;
        public string implementation;
        public string notes;
        public int floor_id;
        public List<double> node_i;
        public List<double> node_j;
        public List<double> point;
        public List<double> center;
        public List<List<double>> points;
        public List<List<double>> vertices;
        public E1Section section;
        public double? length_m;
        public double? width_m;
        public double? height_m;
        public double? depth_m;
        public List<int> restrained_dofs;
        public string master_node;
        public List<string> slave_nodes;
        public bool gravity_verified;
    }

    // ------------------------------------------------------------------
    // Edificio 1 Unity Structural Response (analysis results) DTOs
    // Contract: E1_UNITY_STRUCTURAL_RESPONSE_v1 (edificio1_unity_response.json)
    // ------------------------------------------------------------------

    [Serializable]
    public class E1StructuralResponse
    {
        public string formato;
        public string building_id;
        public E1Units units;
        public E1GlobalQa global_qa;
        public E1MaxDisplacement max_displacement;
        public E1StatusCounts status_counts;
        public List<string> floating_column_stacks;
        public Dictionary<string, E1ResponseElement> elements;
        public Dictionary<string, string> node_analysis_status;
        public Dictionary<string, E1ElementForcesResponse> element_forces_kN;
        public Dictionary<string, E1SupportRestraintResponse> support_restraints;
        public Dictionary<string, E1ReactionResponse> reactions_kN;
        public Dictionary<string, E1DisplacementResponse> displacements_m;
        public string blocker_warning_text;
    }

    [Serializable]
    public class E1GlobalQa
    {
        public double? applied_gravity_kN;
        public double? sum_support_reaction_z_kN;
        public double? residual_fz_kN;
        public double? relative_error_pct;
        public string status;
        public double? E1_applied_gravity_kN;
        public double? E2_applied_gravity_kN;
        public double? TOTAL_applied_gravity_kN;
        public double? E1_support_reactions_kN;
        public double? E2_support_reactions_kN;
        public double? TOTAL_support_reactions_kN;
        public double? global_residual_kN;
        public double? relative_error_pct_combined;
        public string interface_status;
        public double? E1_verified_max_displacement_m;
        public double? E2_verified_max_displacement_m;
        public double? combined_verified_max_displacement_m;
    }

    [Serializable]
    public class E1MaxDisplacement
    {
        public double? numerical_global_max_m;
        public string numerical_global_max_status;
        public string numerical_global_max_reason;
        public double? verified_connected_region_max_m;
        public string verified_region_node;
        public string verified_region_floor;
    }

    [Serializable]
    public class E1StatusCounts
    {
        public int? VERIFIED_CONNECTED_RESPONSE;
        public int? FLOATING_LOAD_PATH_BLOCKER;
        public int? RECONCILED_SCOPING_RESPONSE;
        public int? UNMATCHED_STRUCTURAL_RESPONSE;
    }

    [Serializable]
    public class E1ResponseElement
    {
        public string kind;
        public string floor;
        public string bm_id;
        public string visual_beam_id;
        public string analysis_status;
        public string stub_status;
        public List<double> node_i;
        public List<double> node_j;
        public string element_type;
        public E1ResponseSection section;
        public E1ResponseMaterial material;
        public E1ResponseGeomTransf geomTransf;
        public E1ResponseConnectivity connectivity;
    }

    [Serializable]
    public class E1ResponseSection
    {
        public string section_id;
        public double? b_m;
        public double? h_m;
        public double? A_m2;
        public double? Iy_m4;
        public double? Iz_m4;
        public double? J_m4;
    }

    [Serializable]
    public class E1ResponseMaterial
    {
        public string name;
        public double? E_Pa;
        public double? G_Pa;
        public double? poisson;
    }

    [Serializable]
    public class E1ResponseGeomTransf
    {
        public int? id;
        public string type;
        public string description;
    }

    [Serializable]
    public class E1ResponseConnectivity
    {
        public int? node_i;
        public int? node_j;
        public List<double> node_i_coords;
        public List<double> node_j_coords;
        public List<string> connected_element_ids_at_i;
        public List<string> connected_element_ids_at_j;
        public string diaphragm_floor;
        public int? diaphragm_master_node;
        public string end_releases;
        public string connection_model;
    }

    [Serializable]
    public class E1ElementForcesResponse : E1ResponseElement
    {
        public Dictionary<string, double> forces_kN;
    }

    [Serializable]
    public class E1SupportRestraintResponse
    {
        public List<double> coords;
        public List<string> dof_order;
        public List<int> fixity;
        public string source;
    }

    [Serializable]
    public class E1ReactionResponse
    {
        public List<double> coords;
        public double? Rx_kN;
        public double? Ry_kN;
        public double? Rz_kN;
        public double? Mx;
        public double? My;
        public double? Mz;
    }

    [Serializable]
    public class E1DisplacementResponse
    {
        public List<double> coords;
        public double? ux_m;
        public double? uy_m;
        public double? uz_m;
        public double? rx_rad;
        public double? ry_rad;
        public double? rz_rad;
    }

    // Analysis status string constants (shared by response DTOs)
    public static class E1AnalysisStatus
    {
        public const string Verified = "VERIFIED_CONNECTED_RESPONSE";
        public const string FloatingBlocker = "FLOATING_LOAD_PATH_BLOCKER";
        public const string Scoping = "RECONCILED_SCOPING_RESPONSE";
        public const string Unmatched = "UNMATCHED_STRUCTURAL_RESPONSE";

        public static bool IsVerified(string status)
        {
            return string.Equals(status, Verified, StringComparison.OrdinalIgnoreCase);
        }

        public static bool IsBlocking(string status)
        {
            return string.Equals(status, FloatingBlocker, StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(status, Unmatched, StringComparison.OrdinalIgnoreCase);
        }

        public static bool IsScopingOrBlocking(string status)
        {
            return string.Equals(status, FloatingBlocker, StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(status, Scoping, StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(status, Unmatched, StringComparison.OrdinalIgnoreCase);
        }
    }

    [Serializable]
    public class E1StructuralMappingCoverage
    {
        public string formato;
        public string building_id;
        public E1StructuralMappingGroups mappings;
        public E1L101MappingStatus L101;
    }

    [Serializable]
    public class E1StructuralMappingGroups
    {
        public Dictionary<string, E1StructuralElementMapping> elements;
        public Dictionary<string, E1StructuralNodeMapping> nodes;
        public Dictionary<string, E1StructuralSupportMapping> supports;
    }

    [Serializable]
    public class E1StructuralElementMapping
    {
        public string visual_id;
        public string type;
        public string fe_element_id;
        public string fe_status;
        public string mapping_confidence;
        public string classification;
        public string stack_id;
        public string reason;
        public double? score;
        public double? xy_distance_m;
        public double? transformed_xy_distance_m;
        public double? transformed_distance_m;
        public double? endpoint_avg_distance_m;
        public double? midpoint_distance_m;
        public double? angle_deg;
        public double? height_delta_m;
        public double? nearest_xy_distance_m;
        public double? nearest_transformed_distance_m;
        public string nearest_fe_element_id;
        public string transform_region;
        public string raw_fe_status;
    }

    [Serializable]
    public class E1StructuralNodeMapping
    {
        public string visual_id;
        public string type;
        public string fe_node_id;
        public string fe_status;
        public string reason;
        public double? distance_m;
        public double? transformed_distance_m;
        public string transform_region;
        public string nearest_fe_node_id;
        public double? nearest_distance_m;
    }

    [Serializable]
    public class E1StructuralSupportMapping
    {
        public string visual_id;
        public string type;
        public string fe_node_id;
        public string fe_status;
        public string reason;
        public double? distance_m;
        public double? transformed_distance_m;
        public string transform_region;
        public string nearest_fe_node_id;
        public double? nearest_distance_m;
    }

    [Serializable]
    public class E1L101MappingStatus
    {
        public string status;
        public bool? new_source_since_last_review;
        public string reason;
    }
}
