using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    
    struct UnusedARSurfaceHit
    {
        public Vector3 point, normal;
        public ARSurfaceKind kind;
    }
    struct UnusedARSurfacePlacementPose
    {
        public Pose pose;
        public Vector3 visibleNormal;
        public float scale;
        public bool canRotate;
    }

    public static class ValidatedAutoPlacementMath
    {
        public static float AutoScale(Vector3 realSize) => .65f / Mathf.Max(realSize.x, realSize.y, realSize.z);
        public static Vector3 InitialRight(Vector3 cameraForward)
        {
            Vector3 forward = Vector3.ProjectOnPlane(cameraForward, Vector3.up).normalized;
            if (forward.sqrMagnitude < .5f) forward = Vector3.forward;
            return Vector3.Cross(Vector3.up, forward).normalized;
        }

        public static bool TryPose(string type, Vector3 realSize, ARSurfaceHit hit, Vector3 cameraPosition,
            Vector3 initialRight, int quarterTurns, out ARSurfacePlacementPose result)
            => TryPose(type, realSize, hit, cameraPosition, initialRight, 90f * quarterTurns, out result);

        public static Quaternion LevelRotation(Vector3 initialRight, float yawDegrees)
        {
            Vector3 right = Vector3.ProjectOnPlane(initialRight, Vector3.up).normalized;
            if (right.sqrMagnitude < .5f) right = Vector3.right;
            right = Quaternion.AngleAxis(yawDegrees, Vector3.up) * right;
            return Quaternion.LookRotation(Vector3.Cross(right, Vector3.up), Vector3.up);
        }

        public static bool TryPose(string type, Vector3 realSize, ARSurfaceHit hit, Vector3 cameraPosition,
            Vector3 initialRight, float yawDegrees, out ARSurfacePlacementPose result)
        {
            result = default;
            if (type != "beam" && type != "column" && type != "wall") return false;
            if ((type == "column" && hit.kind != ARSurfaceKind.Floor) ||
                (type == "beam" && hit.kind == ARSurfaceKind.Wall) ||
                (type == "wall" && hit.kind == ARSurfaceKind.Ceiling)) return false;
            Vector3 normal = hit.normal.normalized;
            if (normal.sqrMagnitude < .5f) return false;
            if (Vector3.Dot(normal, cameraPosition - hit.point) < 0) normal = -normal;
            float scale = AutoScale(realSize);
            Vector3 size = realSize * scale;
            Vector3 right, up = Vector3.up;
            bool vertical = hit.kind == ARSurfaceKind.Wall;
            if (vertical)
            {
                // The wall's small normal imperfections never tilt its height.
                Vector3 depth = Vector3.ProjectOnPlane(normal, up).normalized;
                if (depth.sqrMagnitude < .5f) return false;
                right = Vector3.Cross(up, depth).normalized;
            }
            else
            {
                if (Mathf.Abs(Vector3.Dot(normal, up)) < .98f) return false;
                // All structural types stay exactly level, even when the
                // measured floor/ceiling has a small angular imperfection.
                right = LevelRotation(initialRight, yawDegrees) * Vector3.right;
            }
            Vector3 forward = Vector3.Cross(right, up).normalized;
            Quaternion rotation = Quaternion.LookRotation(forward, up);
            // Support distance of the entire scaled box prevents penetration,
            // even if a measured plane has a small angular imperfection.
            float support = (Mathf.Abs(Vector3.Dot(right, normal)) * size.x +
                Mathf.Abs(Vector3.Dot(up, normal)) * size.y +
                Mathf.Abs(Vector3.Dot(forward, normal)) * size.z) * .5f;
            Vector3 offset;
            if (!vertical)
            {
                float verticalProjection = Vector3.Dot(normal, up);
                if (hit.kind == ARSurfaceKind.Floor && verticalProjection < .98f) return false;
                // A yaw-independent horizontal bounding radius avoids penetration
                // on imperfect planes without moving the centre during manual yaw.
                float radius = Mathf.Sqrt(size.x * size.x + size.z * size.z) * .5f;
                support = Mathf.Abs(verticalProjection) * size.y * .5f +
                    Vector3.ProjectOnPlane(normal, up).magnitude * radius;
                offset = up * (support / verticalProjection);
            }
            else offset = normal * support;
            result = new ARSurfacePlacementPose
            {
                pose = new Pose(hit.point + offset, rotation), visibleNormal = normal,
                scale = scale, canRotate = !vertical
            };
            return true;
        }
    }
}

