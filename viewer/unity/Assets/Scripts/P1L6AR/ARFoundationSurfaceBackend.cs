using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

namespace Mcoc.UnityViewer.P1L6AR
{
    // This boundary also allows deterministic tests without pretending the
    // Editor can detect a physical ceiling or establish a real ARCore anchor.
    public interface IARSurfacePlacementBackend
    {
        bool IsTracking { get; }
        bool TryHit(out ARSurfaceHit hit);
        Task<Transform> CreateAnchorAsync(Pose pose);
        bool IsAnchorTracked(Transform anchor);
        void RemoveAnchor(Transform anchor);
    }

    public sealed class ARFoundationSurfaceBackend : IARSurfacePlacementBackend
    {
        readonly ARPlaneManager planes;
        readonly ARRaycastManager raycasts;
        readonly ARAnchorManager anchors;
        readonly List<ARRaycastHit> hits = new List<ARRaycastHit>();
        public bool IsTracking => ARSession.state == ARSessionState.SessionTracking;

        public ARFoundationSurfaceBackend(ARPlaneManager planes, ARRaycastManager raycasts, ARAnchorManager anchors)
        { this.planes = planes; this.raycasts = raycasts; this.anchors = anchors; }

        public bool TryHit(out ARSurfaceHit hit)
        {
            hit = default;
            if (!IsTracking || planes == null || raycasts == null || !planes.enabled || !raycasts.enabled ||
                !raycasts.Raycast(new Vector2(Screen.width * .5f, Screen.height * .5f), hits, TrackableType.PlaneWithinPolygon)) return false;
            foreach (ARRaycastHit candidate in hits)
            {
                ARPlane plane = planes.GetPlane(candidate.trackableId);
                if (plane == null || plane.trackingState != TrackingState.Tracking || plane.subsumedBy != null) continue;
                ARSurfaceKind kind;
                switch (plane.alignment)
                {
                    case PlaneAlignment.HorizontalUp: kind = ARSurfaceKind.Floor; break;
                    case PlaneAlignment.HorizontalDown: kind = ARSurfaceKind.Ceiling; break;
                    case PlaneAlignment.Vertical: kind = ARSurfaceKind.Wall; break;
                    default: continue;
                }
                hit = new ARSurfaceHit { point = candidate.pose.position, normal = plane.normal, kind = kind };
                return true;
            }
            return false;
        }

        public async Task<Transform> CreateAnchorAsync(Pose pose)
        {
            if (!IsTracking || anchors == null || !anchors.enabled || anchors.subsystem == null || !anchors.subsystem.running) return null;
            // A free anchor, deliberately not attached to the detected ARPlane.
            var result = await anchors.TryAddAnchorAsync(pose);
            return result.status.IsSuccess() && result.value != null ? result.value.transform : null;
        }
        public bool IsAnchorTracked(Transform anchor) => IsTracking && anchor != null &&
            anchor.TryGetComponent(out ARAnchor component) && component.trackingState == TrackingState.Tracking;
        public void RemoveAnchor(Transform anchor)
        {
            if (anchor == null) return;
            if (anchors != null && anchors.isActiveAndEnabled && anchors.subsystem != null && anchors.subsystem.running &&
                anchor.TryGetComponent(out ARAnchor component) && anchors.TryRemoveAnchor(component)) return;
            Object.Destroy(anchor.gameObject);
        }
    }
}
