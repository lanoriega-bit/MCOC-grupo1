using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    public sealed class StructuralARElementRenderer : MonoBehaviour
    {
        [SerializeField, Range(0.2f, 1f)] float opacity = 0.78f;
        GameObject rendered;

        public Transform RenderedTransform => rendered != null ? rendered.transform : null;
        public string RenderedElementTag { get; private set; }

        // Shared dimensions for automatic scale and information; rendering
        // continues to use the validated geometry and local orientation.
        public static Vector3 GetSizeMetres(StructuralElementARData data)
        {
            GeometryFor(data, out _, out Vector3 size);
            return size;
        }

        public void Render(StructuralElementARData data, Transform anchor, IModelToARTransform transformAdapter, float scale)
        {
            Clear();
            rendered = GameObject.CreatePrimitive(PrimitiveType.Cube);
            rendered.name = "AR_ELEMENT_" + data.elementTag;
            rendered.transform.SetParent(anchor, false);
            GeometryFor(data, out Vector3 centre, out Vector3 size);
            bool presentation = data.type == "beam" || data.type == "column" || data.type == "wall";
            // BEAM keeps its validated anchor-local presentation unchanged.
            // COLUMN/WALL use camera Right/Up/Depth, independently of the
            // tracked image's tilt. All types remain centred on the anchor.
            rendered.transform.localPosition = presentation ? Vector3.zero
                : transformAdapter.ToAnchorLocalPoint(centre, centre, scale);
            rendered.transform.localRotation = presentation ? Quaternion.identity
                : transformAdapter.ToAnchorLocalRotation(ArrayVector(data.orientation_unity, Vector3.up));
            rendered.transform.localScale = transformAdapter.ToAnchorLocalScale(size, scale);
            if (data.type == "column" || data.type == "wall")
                ApplyInitialPresentationRotation();
            Renderer meshRenderer = rendered.GetComponent<Renderer>();
            meshRenderer.sharedMaterial = BuildMaterial(ColorFor(data.type));
            RenderedElementTag = data.elementTag;
        }

        public void Clear()
        {
            if (rendered != null) Destroy(rendered);
            rendered = null;
            RenderedElementTag = null;
        }

        public void SetVisible(bool visible)
        {
            if (rendered != null) rendered.SetActive(visible);
        }

        void ApplyInitialPresentationRotation()
        {
            // Sample the camera once, only when creating this placement.
            Camera presentationCamera = Camera.main;
            if (presentationCamera == null) return;

            // Cube X/Y/Z explicitly map to presentation Right/Up/Depth.
            // Cancel the parent's rotation before applying the world frame;
            // the ARAnchor still owns the position and is never modified.
            Quaternion worldPresentation = Quaternion.LookRotation(
                presentationCamera.transform.forward, presentationCamera.transform.up);
            Transform anchor = rendered.transform.parent;
            rendered.transform.localRotation = anchor != null
                ? Quaternion.Inverse(anchor.rotation) * worldPresentation
                : worldPresentation;
        }

        static void GeometryFor(StructuralElementARData data, out Vector3 centre,
            out Vector3 size)
        {
            ARSectionDimensions dimensions = data.section?.dimensions;
            ARSectionDimensions physicalDimensions = data.dimensions;
            ARPhysicalGeometry geometry = data.geometry;
            Vector3 start = Vector3.zero;
            Vector3 end = Vector3.zero;
            bool hasAxis = HasVector(geometry?.start_m) && HasVector(geometry?.end_m);
            if (hasAxis)
            {
                start = ArTransformMath.ModelToUnity(ArrayVector(geometry.start_m, Vector3.zero));
                end = ArTransformMath.ModelToUnity(ArrayVector(geometry.end_m, Vector3.zero));
            }
            else if (HasVector(data.unity_coordinates_m?.start) && HasVector(data.unity_coordinates_m?.end))
            {
                start = ArrayVector(data.unity_coordinates_m.start, Vector3.zero);
                end = ArrayVector(data.unity_coordinates_m.end, Vector3.zero);
                hasAxis = true;
            }
            centre = hasAxis ? (start + end) * 0.5f : ArrayVector(data.unity_coordinates_m?.center, Vector3.zero);
            Vector3 axis = hasAxis ? end - start : Vector3.zero;
            float length = axis.magnitude > 1e-5f ? axis.magnitude : Value(geometry?.length_m, Value(data.length_m, 0.01));
            if (data.type == "column")
            {
                float height = VerticalExtent(geometry, ref centre);
                // X = width, Y = physical height/length, Z = depth.
                size = new Vector3(Value(physicalDimensions?.width_m, Value(dimensions?.width_m, 0.30)),
                    height > 0f ? height : length,
                    Value(physicalDimensions?.depth_m, Value(dimensions?.depth_m, 0.30)));
                return;
            }
            if (data.type == "wall")
            {
                Vector3 planAxis = Vector3.ProjectOnPlane(axis, Vector3.up);
                // X = plan length, Y = physical height, Z = thickness.
                // A vertical FE segment does not describe wall plan length.
                length = planAxis.magnitude > 1e-5f ? planAxis.magnitude
                    : Value(geometry?.length_m, Value(physicalDimensions?.length_m, Value(dimensions?.length_m, 0.30)));
                float height = VerticalExtent(geometry, ref centre);
                size = new Vector3(length,
                    height > 0f ? height : Value(physicalDimensions?.height_m,
                        Value(dimensions?.height_m, Mathf.Abs(axis.y) > 1e-5f ? Mathf.Abs(axis.y) : 3.0)),
                    Value(physicalDimensions?.thickness_m, Value(dimensions?.thickness_m, 0.20)));
                return;
            }
            if (data.type == "beam")
            {
                // Validated mapping: X = length, Y = height, Z = width.
                size = new Vector3(length,
                    Value(physicalDimensions?.height_m, Value(dimensions?.height_m, 0.50)),
                    Value(physicalDimensions?.width_m, Value(dimensions?.width_m, 0.30)));
                return;
            }
            // Preserve the previous fallback for types outside this change.
            centre = ArrayVector(data.unity_coordinates_m?.center, Vector3.zero);
            size = new Vector3(0.20f, Value(data.length_m, 0.01), 0.20f);
        }

        static float VerticalExtent(ARPhysicalGeometry geometry, ref Vector3 centre)
        {
            if (geometry == null || geometry.z_top_m <= geometry.z_bottom_m) return 0f;
            centre.y = (float)((geometry.z_bottom_m + geometry.z_top_m) * 0.5);
            return (float)(geometry.z_top_m - geometry.z_bottom_m);
        }

        static bool HasVector(double[] values) => values != null && values.Length >= 3;

        Material BuildMaterial(Color baseColor)
        {
            Shader shader = Shader.Find("Standard");
            Material material = new Material(shader) { name = "P1L6_AR_" + baseColor };
            Color color = new Color(baseColor.r, baseColor.g, baseColor.b, opacity);
            material.color = color;
            material.SetFloat("_Mode", 3f);
            material.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
            material.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
            material.SetInt("_ZWrite", 0);
            material.DisableKeyword("_ALPHATEST_ON");
            material.EnableKeyword("_ALPHABLEND_ON");
            material.renderQueue = 3000;
            return material;
        }

        static Color ColorFor(string type)
        {
            if (type == "column") return new Color(0.12f, 0.75f, 1f);
            if (type == "beam") return new Color(1f, 0.55f, 0.12f);
            if (type == "wall") return new Color(0.45f, 0.92f, 0.45f);
            return Color.white;
        }

        static Vector3 ArrayVector(double[] values, Vector3 fallback)
        {
            return values != null && values.Length >= 3
                ? new Vector3((float)values[0], (float)values[1], (float)values[2])
                : fallback;
        }

        static float Value(double? value, double fallback)
        {
            return Mathf.Max(0.01f, (float)(value.GetValueOrDefault() > 0 ? value.Value : fallback));
        }
    }
}
