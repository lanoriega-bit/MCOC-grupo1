using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    /// <summary>
    /// Temporary P1L6 adapter. The dataset already supplies Unity-space points,
    /// so this implementation only recentres the selected element under the
    /// anchor. José can replace this component through IModelToARTransform.
    /// </summary>
    public sealed class IdentityModelToARTransform : MonoBehaviour, IModelToARTransform
    {
        public Vector3 ToAnchorLocalPoint(Vector3 datasetUnityPoint, Vector3 elementUnityOrigin, float scale)
        {
            return (datasetUnityPoint - elementUnityOrigin) * scale;
        }

        public Quaternion ToAnchorLocalRotation(Vector3 datasetUnityDirection)
        {
            if (datasetUnityDirection.sqrMagnitude < 1e-8f) return Quaternion.identity;
            return Quaternion.FromToRotation(Vector3.up, datasetUnityDirection.normalized);
        }

        public Vector3 ToAnchorLocalScale(Vector3 sizeMetres, float scale)
        {
            return sizeMetres * scale;
        }
    }
}
