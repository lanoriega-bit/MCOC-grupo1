using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    /// <summary>
    /// Inspector-facing wrapper for Jose's tested model/Unity/AR transform.
    /// The tracked ARAnchor is the parent transform; this component therefore
    /// returns coordinates local to that anchor and does not apply its world
    /// pose a second time.
    ///
    /// Physical calibration is deliberately separate from the axis mapping:
    /// modelOriginUnityMetres is the model point represented by the image
    /// centre, calibrationEulerDegrees rotates model axes within the image,
    /// and calibrationOffsetMetres is an optional local marker offset.
    /// </summary>
    public sealed class TrackedModelToARTransformBehaviour : MonoBehaviour, IModelToARTransform
    {
        [SerializeField] LuisAnchorProviderAdapter anchorProvider;
        [SerializeField] Vector3 modelOriginUnityMetres = new Vector3(7.502f, 3.96f, -0.001f);
        [SerializeField] Vector3 calibrationEulerDegrees = Vector3.zero;
        [SerializeField] Vector3 calibrationOffsetMetres = Vector3.zero;
        [SerializeField, Min(0.0001f)] float calibrationScale = 1f;

        ModelToARTransformAdapter adapter;

        public Vector3 ModelOriginUnityMetres => modelOriginUnityMetres;
        public bool HasTrackedAnchor => anchorProvider != null &&
            anchorProvider.TryGetAnchor(out AnchorPoseData _);

        void Awake()
        {
            if (anchorProvider == null) anchorProvider = FindAnyObjectByType<LuisAnchorProviderAdapter>();
            RebuildAdapter();
        }

        void OnValidate()
        {
            calibrationScale = Mathf.Max(0.0001f, calibrationScale);
            RebuildAdapter();
        }

        public Vector3 ToAnchorLocalPoint(Vector3 datasetUnityPoint, Vector3 elementUnityOrigin, float scale)
        {
            EnsureAdapter();
            return adapter.ToAnchorLocalPoint(datasetUnityPoint, modelOriginUnityMetres, scale);
        }

        public Quaternion ToAnchorLocalRotation(Vector3 datasetUnityDirection)
        {
            EnsureAdapter();
            return adapter.ToAnchorLocalRotation(datasetUnityDirection);
        }

        public Vector3 ToAnchorLocalScale(Vector3 sizeMetres, float scale)
        {
            EnsureAdapter();
            return adapter.ToAnchorLocalScale(sizeMetres, scale);
        }

        void EnsureAdapter()
        {
            if (adapter == null) RebuildAdapter();
        }

        void RebuildAdapter()
        {
            adapter = new ModelToARTransformAdapter(
                calibrationOffsetMetres,
                Quaternion.Euler(calibrationEulerDegrees),
                calibrationScale);
        }
    }
}
