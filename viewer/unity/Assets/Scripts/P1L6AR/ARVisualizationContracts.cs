using System;
using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    public enum AnchorTrackingState
    {
        NotAvailable,
        Limited,
        Tracking
    }

    [Serializable]
    public struct AnchorPoseData
    {
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 scale;
        public AnchorTrackingState trackingState;
        public string referenceImageName;

        public Matrix4x4 LocalToWorldMatrix => Matrix4x4.TRS(position, rotation, scale);
    }

    /// <summary>
    /// Boundary owned by the tracking implementation. Luis can provide an
    /// ARTrackedImageAnchorProvider without changing the visualization code.
    /// </summary>
    public interface IAnchorProvider
    {
        Transform AnchorTransform { get; }
        AnchorPoseData CurrentPose { get; }
        event Action<AnchorPoseData> AnchorUpdated;
        bool TryGetAnchor(out AnchorPoseData pose);
    }

    /// <summary>
    /// Boundary owned by the spatial-registration implementation. The current
    /// prototype consumes Unity coordinates already stored in the dataset.
    /// José can replace this adapter with the definitive registration.
    /// </summary>
    public interface IModelToARTransform
    {
        Vector3 ToAnchorLocalPoint(Vector3 datasetUnityPoint, Vector3 elementUnityOrigin, float scale);
        Quaternion ToAnchorLocalRotation(Vector3 datasetUnityDirection);
        Vector3 ToAnchorLocalScale(Vector3 sizeMetres, float scale);
    }
}
