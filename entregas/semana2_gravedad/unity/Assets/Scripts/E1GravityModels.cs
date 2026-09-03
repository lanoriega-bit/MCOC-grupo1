using System;
using System.Collections.Generic;

namespace Mcoc.Semana2.UnityE1
{
    [Serializable]
    public class E1GravityData
    {
        public string formato;
        public string building_id;
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
}
