using System;
using System.Collections.Generic;
using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    // Graphical axes belong to the rendered member, not the camera or global model.
    // FE transverse axes are not inferred from the presentation frame.
    public sealed class ValidatedBeamDiagram3DRenderer : MonoBehaviour
    {
        Material lineMaterial, ribbonMaterial;
        Mesh ribbon;
        readonly List<GameObject> graphics = new List<GameObject>();
        public int Component { get; private set; }
        public int Segment { get; private set; }
        public double EndI { get; private set; }
        public double EndJ { get; private set; }
        public Vector3[] Curve { get; private set; }
        public Vector3 BaseI { get; private set; }
        public Vector3 BaseJ { get; private set; }
        public float AmplitudeWorldMetres => .20f;

        public static bool TrySegmentRange(StructuralElementARData row, int index, out float start, out float end)
        {
            start = end = 0;
            if (row?.type != "beam" || index < 0 || index >= ARCurrentDiagramData.SegmentCount(row)) return false;
            double[] a = row.geometry?.start_m ?? row.model_coordinates_m?.start;
            double[] b = row.geometry?.end_m ?? row.model_coordinates_m?.end;
            ARResultSegment segment = row.current_result_R.segments[index];
            double[] i = Node(row, segment?.node_i ?? -1), j = Node(row, segment?.node_j ?? -1);
            if (!Vector(a) || !Vector(b) || !Vector(i) || !Vector(j)) return false;
            double length2 = 0, pi = 0, pj = 0, di = 0, dj = 0;
            for (int axis = 0; axis < 3; axis++)
            {
                double d = b[axis] - a[axis]; length2 += d * d;
                pi += (i[axis] - a[axis]) * d; pj += (j[axis] - a[axis]) * d;
            }
            if (!Finite(length2) || length2 < 1e-10) return false;
            pi /= length2; pj /= length2;
            // A common transverse offset of the FE line is allowed (beam top vs
            // physical centre). A skew segment or out-of-member range is not.
            for (int axis = 0; axis < 3; axis++)
            {
                double d = b[axis] - a[axis];
                double residual = (j[axis] - i[axis]) - (pj - pi) * d;
                di += residual * residual;
                double offset = i[axis] - a[axis] - pi * d; dj += offset * offset;
            }
            Vector3 dimensions = StructuralARElementRenderer.GetSizeMetres(row);
            double tolerance = Math.Max(.002, Math.Sqrt(length2) * .0001);
            double maxOffset = Math.Sqrt(dimensions.y * dimensions.y + dimensions.z * dimensions.z) * .5 + .02;
            if (di > tolerance * tolerance || dj > maxOffset * maxOffset ||
                pi < -.001 || pi > 1.001 || pj < -.001 || pj > 1.001 || Math.Abs(pi-pj) < 1e-7) return false;
            start = Mathf.Clamp01((float)pi); end = Mathf.Clamp01((float)pj);
            return true;
        }
        static double[] Node(StructuralElementARData row, int tag)
        {
            if (row.current_result_R?.node_displacements != null)
                foreach (ARNodeDisplacement node in row.current_result_R.node_displacements)
                    if (node != null && node.node_tag == tag) return node.model_coord_m;
            return null;
        }
        static bool Vector(double[] value) => value?.Length == 3 && Finite(value[0]) && Finite(value[1]) && Finite(value[2]);
        static bool Finite(double value) => !double.IsNaN(value) && !double.IsInfinity(value);

        public bool Render(StructuralElementARData row, Transform mesh, int segment, int component)
        {
            if (!ARCurrentDiagramData.TryValues(row, segment, component, out double i, out double j) ||
                !TrySegmentRange(row, segment, out float from, out float to) || mesh == null) return false;
            Shader shader = Resources.Load<Shader>("ARForceOverlay");
            if (shader == null) return false; // Never silently substitute an unsupported material.
            Clear();
            lineMaterial = new Material(shader);
            ribbonMaterial = new Material(shader);
            Color color = new[] { Color.cyan, new Color(.1f,1,.4f), new Color(1,.65f,.1f),
                new Color(1,.3f,1), new Color(.15f,.7f,1), new Color(1,.3f,.3f) }[component];
            lineMaterial.color = color; color.a = .20f; ribbonMaterial.color = color;
            Component = component; Segment = segment; EndI = i; EndJ = j;
            Transform member = transform.parent;
            Vector3 size = mesh.localScale;
            bool horizontal = component == 2 || component == 5;
            Vector3 amplitudeAxis = horizontal ? Vector3.forward : Vector3.up;
            Vector3 clearanceAxis = horizontal ? Vector3.up : Vector3.forward;
            float axisScale = member.TransformVector(amplitudeAxis).magnitude;
            float clearanceScale = member.TransformVector(clearanceAxis).magnitude;
            if (axisScale < 1e-6f || clearanceScale < 1e-6f) { Clear(); return false; }
            Vector3 offset = -clearanceAxis * ((horizontal ? size.y : size.z) * .5f + .015f / clearanceScale);
            BaseI = Vector3.right * ((from - .5f) * size.x) + offset;
            BaseJ = Vector3.right * ((to - .5f) * size.x) + offset;
            double max = Math.Max(Math.Abs(i), Math.Abs(j));
            float amplitude = .20f / axisScale;
            var stations = new List<float>();
            for (int n = 0; n <= 8; n++) stations.Add(n / 8f);
            if (i != 0 && j != 0 && Math.Sign(i) != Math.Sign(j))
            {
                // Normalized endpoints avoid overflow and split the ribbon at zero.
                float zero = (float)((i / max) / (i / max - j / max));
                if (!stations.Exists(t => Mathf.Abs(t-zero) < 1e-6f)) stations.Add(zero);
                stations.Sort();
            }
            Curve = new Vector3[stations.Count];
            var vertices = new Vector3[stations.Count * 2];
            var triangles = new int[(stations.Count-1) * 6];
            for (int n = 0; n < stations.Count; n++)
            {
                float t = stations[n];
                Vector3 baseline = Vector3.Lerp(BaseI, BaseJ, t);
                float relative = max == 0 ? 0 : (float)((1-t) * (i/max) + t * (j/max));
                Curve[n] = baseline + amplitudeAxis * (relative * amplitude);
                vertices[2*n] = baseline; vertices[2*n+1] = Curve[n];
                Line("Ordinate" + n, new[] {baseline, Curve[n]}, horizontal);
                if (n == stations.Count-1) continue;
                int k = n*6, v = n*2;
                triangles[k]=v; triangles[k+1]=v+1; triangles[k+2]=v+2;
                triangles[k+3]=v+1; triangles[k+4]=v+3; triangles[k+5]=v+2;
            }
            Line("Baseline", new[] {BaseI,BaseJ}, horizontal);
            Line("EndInterpolation", Curve, horizontal);
            var fill = new GameObject("ResultRibbon",typeof(MeshFilter),typeof(MeshRenderer));
            fill.transform.SetParent(transform,false);graphics.Add(fill);
            ribbon = new Mesh { name = "FE end interpolation ribbon" };
            ribbon.vertices=vertices; ribbon.triangles=triangles; ribbon.RecalculateBounds();
            fill.GetComponent<MeshFilter>().sharedMesh=ribbon;
            fill.GetComponent<MeshRenderer>().sharedMaterial=ribbonMaterial;
            return true;
        }
        void Line(string name, Vector3[] points, bool horizontal)
        {
            var go = new GameObject(name,typeof(LineRenderer)); go.transform.SetParent(transform,false); graphics.Add(go);
            go.transform.localRotation = horizontal ? Quaternion.Euler(90,0,0) : Quaternion.identity;
            var line=go.GetComponent<LineRenderer>(); line.useWorldSpace=false;
            line.alignment=LineAlignment.TransformZ; // Fixed ribbons, never camera-facing.
            line.sharedMaterial=lineMaterial; line.positionCount=points.Length;
            float widthScale=transform.parent.TransformVector(horizontal ? Vector3.forward : Vector3.up).magnitude;
            line.widthMultiplier=.003f/widthScale;
            for(int n=0;n<points.Length;n++)line.SetPosition(n,Quaternion.Inverse(go.transform.localRotation)*points[n]);
            line.numCapVertices=0;line.numCornerVertices=0;
        }
        void Clear()
        {
            foreach(GameObject go in graphics) if(go!=null) {go.SetActive(false);Destroy(go);}
            graphics.Clear();
            if(ribbon!=null)Destroy(ribbon);
            if(lineMaterial!=null)Destroy(lineMaterial);
            if(ribbonMaterial!=null)Destroy(ribbonMaterial);
        }
        void OnDestroy() { Clear(); }
    }
}

