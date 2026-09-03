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
}
