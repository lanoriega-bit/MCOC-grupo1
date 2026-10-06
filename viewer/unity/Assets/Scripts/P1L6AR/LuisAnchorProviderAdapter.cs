using System;
using UnityEngine;
using UnityEngine.XR.ARSubsystems;

namespace Mcoc.UnityViewer.P1L6AR
{
    /// <summary>
    /// Adapts Luis's AR Foundation image tracker to the visualization contract.
    /// Only Tracking is considered spatially trustworthy. Limited and None are
    /// reported to consumers, but TryGetAnchor returns false so stale geometry
    /// is never presented as if it were registered.
    /// </summary>
    public sealed class LuisAnchorProviderAdapter : MonoBehaviour, IAnchorProvider
    {
        [SerializeField] LuisARImageAnchor source;

        AnchorPoseData currentPose;

        public Transform AnchorTransform => source != null ? source.AnchorTransform : null;
        public AnchorPoseData CurrentPose => currentPose;
        public event Action<AnchorPoseData> AnchorUpdated;

        void Awake()
        {
            if (source == null) source = FindAnyObjectByType<LuisARImageAnchor>();
            currentPose = BuildPose();
        }

        void OnEnable()
        {
            if (source == null) source = FindAnyObjectByType<LuisARImageAnchor>();
            if (source != null) source.TrackingUpdated += OnTrackingUpdated;
        }

        void OnDisable()
        {
            if (source != null) source.TrackingUpdated -= OnTrackingUpdated;
        }

        public bool TryGetAnchor(out AnchorPoseData pose)
        {
            pose = currentPose;
            return source != null &&
                source.HasAnchor &&
                source.AnchorTransform != null &&
                currentPose.trackingState == AnchorTrackingState.Tracking;
        }

        void OnTrackingUpdated(string imageName, Pose pose, TrackingState state)
        {
            currentPose = new AnchorPoseData
            {
                position = pose.position,
                rotation = pose.rotation,
                scale = Vector3.one,
                trackingState = Map(state),
                referenceImageName = string.IsNullOrWhiteSpace(imageName)
                    ? "NO_REFERENCE_IMAGE"
                    : imageName
            };
            AnchorUpdated?.Invoke(currentPose);
        }

        AnchorPoseData BuildPose()
        {
            Pose pose = source != null
                ? source.AnchorPose
                : new Pose(Vector3.zero, Quaternion.identity);
            return new AnchorPoseData
            {
                position = pose.position,
                rotation = pose.rotation,
                scale = Vector3.one,
                trackingState = source != null ? Map(source.TrackingStatus) : AnchorTrackingState.NotAvailable,
                referenceImageName = source != null && !string.IsNullOrWhiteSpace(source.ReferenceImageName)
                    ? source.ReferenceImageName
                    : "NO_REFERENCE_IMAGE"
            };
        }

        static AnchorTrackingState Map(TrackingState state)
        {
            switch (state)
            {
                case TrackingState.Tracking:
                    return AnchorTrackingState.Tracking;
                case TrackingState.Limited:
                    return AnchorTrackingState.Limited;
                default:
                    return AnchorTrackingState.NotAvailable;
            }
        }
    }
}
