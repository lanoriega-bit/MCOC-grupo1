using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    public sealed class StructuralARElementRenderer : MonoBehaviour
    {
        [SerializeField, Range(0.2f, 1f)] float opacity = 0.78f;
        GameObject rendered;

        public Transform RenderedTransform => rendered != null ? rendered.transform : null;
        public string RenderedElementTag { get; private set; }

        public void Render(StructuralElementARData data, Transform anchor, IModelToARTransform transformAdapter, float scale)
        {
            Clear();
            rendered = GameObject.CreatePrimitive(PrimitiveType.Cube);
            rendered.name = "AR_ELEMENT_" + data.elementTag;
            rendered.transform.SetParent(anchor, false);
            Vector3 direction = ArrayVector(data.orientation_unity, Vector3.up);
            rendered.transform.localPosition = Vector3.zero;
            rendered.transform.localRotation = transformAdapter.ToAnchorLocalRotation(direction);
            rendered.transform.localScale = transformAdapter.ToAnchorLocalScale(SizeFor(data), scale);
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

        static Vector3 SizeFor(StructuralElementARData data)
        {
            ARSectionDimensions dimensions = data.section?.dimensions;
            float length = Mathf.Max(0.01f, (float)data.length_m);
            if (data.type == "column")
                return new Vector3(Value(dimensions?.width_m, 0.30), length, Value(dimensions?.depth_m, 0.30));
            if (data.type == "beam")
                return new Vector3(Value(dimensions?.width_m, 0.30), length, Value(dimensions?.height_m, 0.50));
            if (data.type == "wall")
            {
                float thickness = Value(dimensions?.thickness_m, 0.20);
                return new Vector3(thickness, length, thickness);
            }
            return new Vector3(0.20f, length, 0.20f);
        }

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
