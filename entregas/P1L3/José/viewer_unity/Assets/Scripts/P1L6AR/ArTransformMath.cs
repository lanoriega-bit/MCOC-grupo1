using System;
using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    /// <summary>
    /// Pure rigid-transform math for the model -> Unity -> AR placement of the
    /// P1L6 AR bridge. Mirror of the reference implementation
    /// entregas/P1L6/transform/ar_math.py (see AR_TRANSFORM_CONTRACT.md).
    ///
    /// Canonical maps (SI units: m, N, N.m, rad):
    ///   model -> unity : [x, y, z] -> [x, z, -y]   (proper rotation, det=+1)
    ///   unity -> model : [X, Y, Z] -> [X, -Z, Y]
    ///   unity -> ar    : p_ar = R_anchor * (s * p_unity) + t_anchor
    ///   ar    -> unity : p_unity = R_anchor^T * (p_ar - t_anchor) / s
    ///
    /// Additive utility: it does not touch AR Foundation, image tracking or UI.
    /// </summary>
    public static class ArTransformMath
    {
        /// <summary>model -> Unity: [x, y, z] -> [x, z, -y].</summary>
        public static Vector3 ModelToUnity(Vector3 p_model)
        {
            return new Vector3(p_model.x, p_model.z, -p_model.y);
        }

        /// <summary>Unity -> model: [X, Y, Z] -> [X, -Z, Y] (inverse).</summary>
        public static Vector3 UnityToModel(Vector3 p_unity)
        {
            return new Vector3(p_unity.x, -p_unity.z, p_unity.y);
        }

        /// <summary>Unity -> anchor-local AR: p_ar = R * (s * p_unity) + t.</summary>
        public static Vector3 UnityToAnchor(Vector3 p_unity, Vector3 tAnchor, Quaternion rAnchor, float scale = 1f)
        {
            return rAnchor * (scale * p_unity) + tAnchor;
        }

        /// <summary>Anchor-local -> Unity (inverse, anchor assumed rigid, scale != 0).</summary>
        public static Vector3 AnchorToUnity(Vector3 p_ar, Vector3 tAnchor, Quaternion rAnchor, float scale = 1f)
        {
            return Quaternion.Inverse(rAnchor) * (p_ar - tAnchor) / (scale == 0f ? 1f : scale);
        }

        /// <summary>model -> anchor-local AR through the canonical chain.</summary>
        public static Vector3 ModelToAnchor(Vector3 p_model, Vector3 tAnchor, Quaternion rAnchor, float scale = 1f)
        {
            return UnityToAnchor(ModelToUnity(p_model), tAnchor, rAnchor, scale);
        }

        /// <summary>anchor-local -> model (inverse of ModelToAnchor).</summary>
        public static Vector3 AnchorToModel(Vector3 p_ar, Vector3 tAnchor, Quaternion rAnchor, float scale = 1f)
        {
            return UnityToModel(AnchorToUnity(p_ar, tAnchor, rAnchor, scale));
        }

        /// <summary>Direction vectors map with the same rotation (no translation).</summary>
        public static Vector3 ModelToUnityDirection(Vector3 d_model)
        {
            return ModelToUnity(d_model);
        }

        /// <summary>Fake pose to develop and validate without a phone: id placement.</summary>
        public static void FakeAnchor(out Vector3 t, out Quaternion r, out float scale)
        {
            t = Vector3.zero;
            r = Quaternion.identity;
            scale = 1f;
        }

        /// <summary>True if r is a proper (right-handed) rigid rotation.</summary>
        public static bool IsRigidRotation(Quaternion r, float tol = 1e-6f)
        {
            float len = r.x * r.x + r.y * r.y + r.z * r.z + r.w * r.w;
            return Mathf.Abs(len - 1f) < tol;
        }

        /// <summary>Max relative distance-preservation error of a rigid placement.</summary>
        public static float DistanceErrorMax(Vector3[] modelA, Vector3[] unityA, Vector3[] modelB, Vector3[] unityB, float tol = 1e-6f)
        {
            if (modelA.Length != modelB.Length) throw new ArgumentException("pairs must have equal length");
            float worst = 0f;
            for (int i = 0; i < modelA.Length; ++i)
            {
                float dA = Vector3.Distance(modelA[i], unityA[i]);
                float dB = Vector3.Distance(modelB[i], unityB[i]);
                float base_ = Mathf.Max(dA, dB, 1e-12f);
                worst = Mathf.Max(worst, Mathf.Abs(dA - dB) / base_);
            }
            return worst;
        }
    }

    /// <summary>
    /// Optional adapter implementing the existing IModelToARTransform boundary
    /// with the canonical transform + fake (identity) anchor, so every part of
    /// the pipeline can be exercised before an AR anchor is live. Purely
    /// additive: swap in a tracking-base adapter later without touching here.
    /// </summary>
    public sealed class ModelToARTransformAdapter : IModelToARTransform
    {
        private readonly Vector3 _anchorT;
        private readonly Quaternion _anchorR;
        private readonly float _scale;

        public ModelToARTransformAdapter(Vector3 anchorT, Quaternion anchorR, float scale = 1f)
        {
            _anchorT = anchorT;
            _anchorR = anchorR;
            _scale = scale;
        }

        public static ModelToARTransformAdapter FakeAnchor()
        {
            ArTransformMath.FakeAnchor(out Vector3 t, out Quaternion r, out float s);
            return new ModelToARTransformAdapter(t, r, s);
        }

        public Vector3 ToAnchorLocalPoint(Vector3 datasetUnityPoint, Vector3 elementUnityOrigin, float scale)
        {
            return ArTransformMath.UnityToAnchor(datasetUnityPoint - elementUnityOrigin, _anchorT, _anchorR, scale * _scale);
        }

        public Quaternion ToAnchorLocalRotation(Vector3 datasetUnityDirection)
        {
            if (datasetUnityDirection.sqrMagnitude < 1e-8f) return _anchorR;
            // orientation_unity is already expressed in Unity coordinates.
            // The structural primitive stores its length on local +Y.
            return _anchorR * Quaternion.FromToRotation(Vector3.up, datasetUnityDirection.normalized);
        }

        public Vector3 ToAnchorLocalScale(Vector3 sizeMetres, float scale)
        {
            return sizeMetres * (scale * _scale);
        }
    }
}
