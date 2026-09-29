using UnityEngine;

namespace Mcoc.UnityViewer
{
    public static class StructuralFailureVisualStyle
    {
        public static readonly Color Warning = new Color(1.00f, 0.46f, 0.03f, 1f);
        public static readonly Color Exceeded = new Color(0.92f, 0.035f, 0.025f, 1f);
        public static readonly Color NoData = new Color(0.43f, 0.46f, 0.50f, 1f);
        public static readonly Color Selection = new Color(0.05f, 0.90f, 1.00f, 1f);
        public static readonly Color Crack = new Color(0.22f, 0.015f, 0.01f, 1f);
    }

    /// <summary>Presentation-only consumer of FailureResult. Never changes FE state.</summary>
    public sealed class ElementFailureVisualizer : MonoBehaviour
    {
        Renderer target;
        Color baseColor;
        GameObject damageRoot;

        public void Initialize(Color original)
        {
            target = GetComponent<Renderer>();
            baseColor = original;
        }

        public void Apply(FailureResult result, bool visualizationEnabled, bool damageEnabled, bool selected)
        {
            if (target == null) target = GetComponent<Renderer>();
            if (target == null) return;
            Color color = baseColor;
            bool exceeded = false;
            if (visualizationEnabled && result != null)
            {
                if (result.state == StructuralFailureState.WARNING) color = StructuralFailureVisualStyle.Warning;
                else if (result.state == StructuralFailureState.CAPACITY_EXCEEDED)
                { color = StructuralFailureVisualStyle.Exceeded; exceeded = true; }
                else if (result.state == StructuralFailureState.NO_DATA) color = StructuralFailureVisualStyle.NoData;
            }
            if (selected) color = Color.Lerp(color, StructuralFailureVisualStyle.Selection, 0.42f);
            var block = new MaterialPropertyBlock();
            target.GetPropertyBlock(block);
            block.SetColor("_Color", color);
            block.SetColor("_BaseColor", color);
            Color emission = exceeded ? color * 0.75f : (selected ? StructuralFailureVisualStyle.Selection * 0.22f : Color.black);
            block.SetColor("_EmissionColor", emission);
            target.SetPropertyBlock(block);
            bool showDamage = visualizationEnabled && damageEnabled && exceeded;
            if (showDamage && damageRoot == null) damageRoot = BuildDamageOverlay();
            if (damageRoot != null) damageRoot.SetActive(showDamage);
        }

        GameObject BuildDamageOverlay()
        {
            var root = new GameObject("VISUAL_DAMAGE_OVERLAY");
            root.transform.SetParent(transform, false);
            var info = GetComponent<ElementInfo>();
            if (info != null && info.category == "beam")
            {
                AddBand(root.transform, new Vector3(-0.025f, 0, 0), new Vector3(0.025f, 1.04f, 1.04f), 18f);
                AddBand(root.transform, new Vector3(0.025f, 0, 0), new Vector3(0.025f, 1.04f, 1.04f), -18f);
            }
            else if (info != null && info.category == "column")
            {
                AddBand(root.transform, Vector3.zero, new Vector3(1.04f, 0.035f, 1.04f), 32f);
            }
            else
            {
                AddBand(root.transform, new Vector3(0, 0, -0.08f), new Vector3(1.04f, 0.025f, 0.025f), 32f);
                AddBand(root.transform, new Vector3(0, 0, 0.08f), new Vector3(1.04f, 0.025f, 0.025f), -32f);
            }
            return root;
        }

        static void AddBand(Transform parent, Vector3 localPosition, Vector3 localScale, float rotationZ)
        {
            var band = GameObject.CreatePrimitive(PrimitiveType.Cube);
            band.name = "CRACK_BAND";
            band.transform.SetParent(parent, false);
            band.transform.localPosition = localPosition;
            band.transform.localRotation = Quaternion.Euler(0, 0, rotationZ);
            band.transform.localScale = localScale;
            var collider = band.GetComponent<Collider>();
            if (collider != null) Object.Destroy(collider);
            var renderer = band.GetComponent<Renderer>();
            var shader = Shader.Find("Standard") ?? Shader.Find("Diffuse");
            renderer.material = new Material(shader) { color = StructuralFailureVisualStyle.Crack };
        }
    }
}
