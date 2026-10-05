using System.Collections.Generic;
using System.Globalization;
using System.Text;
using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    public static class ARSelectedElementInfo
    {
        static string Number(double value) => value.ToString("0.00", CultureInfo.InvariantCulture);
        static string Available(string value) => string.IsNullOrWhiteSpace(value) ? "No disponible" : value;

        public static string Format(StructuralElementARData data, ARGeometryScaleMode scaleMode=ARGeometryScaleMode.Auto, float scaleFactor=0)
        {
            if (data == null) return "Selecciona un element_id del dataset CURRENT.";
            Vector3 size = StructuralARElementRenderer.GetSizeMetres(data);
            StringBuilder text = new StringBuilder();
            text.AppendLine("ID: " + data.element_id);
            text.AppendLine("Tipo: " + Available(data.type).ToUpperInvariant());
            text.AppendLine("Edificio: " + Available(data.building) + "  |  Piso: " + Available(data.floor));
            text.AppendLine("Nodos FE: " + FENodes(data));
            text.AppendLine("OpenSees: " + (data.opensees_tags != null && data.opensees_tags.Length > 0
                ? string.Join(", ", data.opensees_tags) : "No disponible"));
            text.AppendLine((data.type == "column" ? "Largo / altura: " : "Largo: ") +
                Number(data.type == "column" ? size.y : size.x) + " m");
            if (data.type == "wall")
            {
                text.AppendLine("Altura: " + Number(size.y) + " m");
                text.AppendLine("Espesor: " + Number(size.z) + " m");
            }
            else if (data.type == "column")
                text.AppendLine("Sección (ancho × profundidad): " + Number(size.x) + " × " + Number(size.z) + " m");
            else
                text.AppendLine("Sección (ancho × altura): " + Number(size.z) + " × " + Number(size.y) + " m");
            text.AppendLine("Material: " + Available(data.material?.name ?? data.material?.material_id));
            text.AppendLine("section_id: " + Available(data.section?.section_id));
            text.AppendLine("Estado: " + Available(data.data_state));
            if(scaleFactor<=0)scaleFactor=ARGeometryScale.Factor(scaleMode,size);
            bool physical=ARGeometryScale.TryVerifiedDimensions(data,out Vector3 verified);
            text.AppendLine("Escala AR: "+ARGeometryScale.Description(scaleMode,scaleFactor));
            if(physical)
            {
                text.AppendLine("Dimensiones reales: "+Dimensions(data.type,verified));
                text.AppendLine("Dimensiones mostradas: "+Dimensions(data.type,verified*scaleFactor));
            }
            else text.AppendLine(ARGeometryScale.Unavailable);

            bool current = data.data_state == "CURRENT_VERIFIED" && ARResultSummary.TryCreate(data, out _);
            text.AppendLine("CURRENT / CASE_R: " + (current ? "disponible" : "sin resultados disponibles"));
            if (current && ARResultSummary.TryCreate(data, out ARResultSummary result))
            {
                ARResultCoefficients c = data.current_result_R.coefficients;
                if (c != null)
                    text.AppendLine("R = " + Number(c.G) + "G + " + Number(c.Q) + "Q + " +
                        Number(c.EX) + "EX + " + Number(c.EY) + "EY");
                text.AppendLine("|P|max: " + Number(result.PkN) + " kN");
                text.AppendLine("|V|max: " + Number(result.VkN) + " kN");
                text.AppendLine("|M|max: " + Number(result.MkNm) + " kN·m");
                if (data.current_result_R.node_displacements != null && data.current_result_R.node_displacements.Length > 0)
                    text.AppendLine("Desplazamiento máximo: " + Number(result.DisplacementMm) + " mm");
            }
            return text.ToString().TrimEnd();
        }

        static string Dimensions(string type,Vector3 size)
        {
            Vector3 ordered=type=="beam" ? new Vector3(size.x,size.z,size.y) : type=="column" ? new Vector3(size.x,size.z,size.y) : size;
            return ordered.x.ToString("0.###",CultureInfo.InvariantCulture)+" × "+ordered.y.ToString("0.###",CultureInfo.InvariantCulture)+" × "+ordered.z.ToString("0.###",CultureInfo.InvariantCulture)+" m";
        }

        static string FENodes(StructuralElementARData data)
        {
            SortedSet<int> nodes = new SortedSet<int>();
            if (data.fe_node_tags != null)
                foreach (int node in data.fe_node_tags) nodes.Add(node);
            if (data.current_result_R?.segments != null)
                foreach (ARResultSegment segment in data.current_result_R.segments)
                {
                    if (segment == null) continue;
                    if (segment.node_i > 0) nodes.Add(segment.node_i);
                    if (segment.node_j > 0) nodes.Add(segment.node_j);
                }
            return nodes.Count > 0 ? string.Join(", ", nodes) : "No disponibles";
        }
    }
}
