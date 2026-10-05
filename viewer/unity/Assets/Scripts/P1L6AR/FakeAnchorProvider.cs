using System;
using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    /// <summary>
    /// Development-only anchor. It deliberately has no AR Foundation
    /// dependency and can be replaced through IAnchorProvider.
    /// </summary>
    public sealed class FakeAnchorProvider : MonoBehaviour, IAnchorProvider
    {
        [SerializeField] Transform anchorTransform;
        [SerializeField] string referenceImageName = "FAKE_P1L6_REFERENCE";
        [SerializeField] AnchorTrackingState trackingState = AnchorTrackingState.Tracking;

        Vector3 previousPosition;
        Quaternion previousRotation;
        Vector3 previousScale;

        public Transform AnchorTransform => anchorTransform != null ? anchorTransform : transform;
        public AnchorPoseData CurrentPose => BuildPose();
        public event Action<AnchorPoseData> AnchorUpdated;

        void Awake()
        {
            if (anchorTransform == null) anchorTransform = transform;
            RememberPose();
        }

        void Update()
        {
            Transform target = AnchorTransform;
            if (target.position == previousPosition &&
                target.rotation == previousRotation &&
                target.localScale == previousScale) return;
            RememberPose();
            AnchorUpdated?.Invoke(BuildPose());
        }

        public bool TryGetAnchor(out AnchorPoseData pose)
        {
            pose = BuildPose();
            return trackingState != AnchorTrackingState.NotAvailable;
        }

        public void SetPose(Vector3 position, Quaternion rotation, Vector3 scale)
        {
            Transform target = AnchorTransform;
            target.SetPositionAndRotation(position, rotation);
            target.localScale = scale;
            RememberPose();
            AnchorUpdated?.Invoke(BuildPose());
        }

        public void SetTracking(AnchorTrackingState state, string imageName = null)
        {
            trackingState = state;
            if (!string.IsNullOrWhiteSpace(imageName)) referenceImageName = imageName;
            AnchorUpdated?.Invoke(BuildPose());
        }

        AnchorPoseData BuildPose()
        {
            Transform target = AnchorTransform;
            return new AnchorPoseData
            {
                position = target.position,
                rotation = target.rotation,
                scale = target.lossyScale,
                trackingState = trackingState,
                referenceImageName = referenceImageName
            };
        }

        void RememberPose()
        {
            Transform target = AnchorTransform;
            previousPosition = target.position;
            previousRotation = target.rotation;
            previousScale = target.localScale;
        }
    }
}
