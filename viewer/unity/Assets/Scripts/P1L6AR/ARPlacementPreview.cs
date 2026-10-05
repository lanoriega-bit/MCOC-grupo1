using UnityEngine;
using UnityEngine.Rendering;

namespace Mcoc.UnityViewer.P1L6AR
{
    // Presentation mesh for surface placement only. Dimensions remain owned by
    // the validated renderer; its quick-view instance is never reconfigured.
    public sealed class ARPlacementPreview : MonoBehaviour
    {
        Transform mesh, reticle;
        Material material, reticleMaterial;
        StructuralElementARData element;
        bool isPreview;
        public ARGeometryScaleMode ScaleMode { get; private set; }
        public bool HasPhysicalDimensions => ARGeometryScale.TryVerifiedDimensions(element,out _);
        public float UniformScale { get; private set; }
        public string ElementId { get; private set; }
        public Transform StructuralMesh => mesh;

        public void Configure(StructuralElementARData row, ARGeometryScaleMode scaleMode = ARGeometryScaleMode.Auto)
        {
            if (mesh == null)
            {
                mesh = GameObject.CreatePrimitive(PrimitiveType.Cube).transform;
                mesh.name = "StructuralMesh"; mesh.SetParent(transform, false);
                Destroy(mesh.GetComponent<Collider>());
                material = new Material(Shader.Find("Standard"));
                mesh.GetComponent<Renderer>().sharedMaterial = material;
                reticle = GameObject.CreatePrimitive(PrimitiveType.Quad).transform;
                reticle.name = "SurfaceReticle"; reticle.SetParent(transform, false);
                Destroy(reticle.GetComponent<Collider>());
                reticleMaterial = new Material(Shader.Find("Standard"));
                reticleMaterial.color = new Color(.05f, 1f, .45f, 1f);
                reticle.GetComponent<Renderer>().sharedMaterial = reticleMaterial;
            }
            Vector3 dimensions = StructuralARElementRenderer.GetSizeMetres(row);
            element=row;
            ScaleMode=scaleMode==ARGeometryScaleMode.Auto || HasPhysicalDimensions ? scaleMode : ARGeometryScaleMode.Auto;
            UniformScale = ARGeometryScale.Factor(ScaleMode,dimensions);
            mesh.localPosition = Vector3.zero; mesh.localRotation = Quaternion.identity;
            mesh.localScale = dimensions * UniformScale;
            Color color = row.type == "beam" ? new Color(1f, .55f, .12f) : row.type == "column"
                ? new Color(.12f, .75f, 1f) : new Color(.45f, .92f, .45f);
            material.color = color;
            ElementId = row.element_id;
            SetPreview(true);
        }
        public bool SetScaleMode(ARGeometryScaleMode mode)
        {
            if(!isPreview || (int)mode<0 || (int)mode>4 || (mode!=ARGeometryScaleMode.Auto && !HasPhysicalDimensions))return false;
            ScaleMode=mode;
            Vector3 dimensions=StructuralARElementRenderer.GetSizeMetres(element);
            UniformScale=ARGeometryScale.Factor(mode,dimensions);
            mesh.localScale=dimensions*UniformScale;
            return true;
        }
        public void Apply(ARSurfaceHit hit, ARSurfacePlacementPose placement)
        {
            transform.SetPositionAndRotation(placement.pose.position, placement.pose.rotation);
            reticle.gameObject.SetActive(true);
            reticle.SetPositionAndRotation(hit.point + placement.visibleNormal * .003f,
                Quaternion.FromToRotation(Vector3.back, placement.visibleNormal));
            reticle.localScale = Vector3.one * .045f;
        }
        public void ApplyFree(Pose placement)
        {
            transform.SetPositionAndRotation(placement.position, placement.rotation);
            // Free placement makes no claim that a physical surface was hit.
            reticle.gameObject.SetActive(false);
        }
        public void SetPreview(bool preview)
        {
            isPreview=preview;
            Color color = material.color; color.a = preview ? .32f : 1f; material.color = color;
            material.SetFloat("_Mode", preview ? 3 : 0);
            material.SetInt("_SrcBlend", (int)(preview ? BlendMode.SrcAlpha : BlendMode.One));
            material.SetInt("_DstBlend", (int)(preview ? BlendMode.OneMinusSrcAlpha : BlendMode.Zero));
            material.SetInt("_ZWrite", preview ? 0 : 1);
            material.DisableKeyword("_ALPHATEST_ON");
            if (preview) material.EnableKeyword("_ALPHABLEND_ON"); else material.DisableKeyword("_ALPHABLEND_ON");
            material.renderQueue = preview ? 3000 : 2000;
            reticle.gameObject.SetActive(preview);
        }
        void OnDestroy()
        {
            if (material != null) Destroy(material);
            if (reticleMaterial != null) Destroy(reticleMaterial);
        }
    }
}
