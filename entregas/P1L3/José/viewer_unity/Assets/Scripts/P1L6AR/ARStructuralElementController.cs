using System;
using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    public sealed class ARStructuralElementController : MonoBehaviour
    {
        [SerializeField] ARDatasetRepository repository;
        [SerializeField] StructuralARElementRenderer elementRenderer;
        [SerializeField] MonoBehaviour anchorProviderBehaviour;
        [SerializeField] MonoBehaviour transformBehaviour;
        [SerializeField] string initialElementTag = "E2-P1-C-002";
        [SerializeField, Range(0.02f, 2f)] float visualizationScale = 0.25f;

        IAnchorProvider anchorProvider;
        IModelToARTransform transformAdapter;
        Transform directAnchor;

        public StructuralElementARData SelectedElement { get; private set; }
        public string State { get; private set; } = "NO DATA";
        public event Action<StructuralElementARData, string, AnchorPoseData> ElementShown;

        void Awake()
        {
            anchorProvider = anchorProviderBehaviour as IAnchorProvider;
            transformAdapter = transformBehaviour as IModelToARTransform;
            directAnchor = new GameObject("DirectAnchorAdapter").transform;
            directAnchor.SetParent(transform, false);
            if (repository == null) repository = FindAnyObjectByType<ARDatasetRepository>();
            if (elementRenderer == null) elementRenderer = FindAnyObjectByType<StructuralARElementRenderer>();
            if (transformAdapter == null) transformAdapter = FindAnyObjectByType<IdentityModelToARTransform>();
        }

        void OnEnable()
        {
            if (repository != null) repository.DatasetLoaded += OnDatasetLoaded;
            if (anchorProvider != null) anchorProvider.AnchorUpdated += OnAnchorUpdated;
        }

        void OnDisable()
        {
            if (repository != null) repository.DatasetLoaded -= OnDatasetLoaded;
            if (anchorProvider != null) anchorProvider.AnchorUpdated -= OnAnchorUpdated;
        }

        void OnDatasetLoaded()
        {
            if (repository.IsCurrent) ShowElement(initialElementTag);
            else State = "STALE / NO DATA";
        }

        public bool ShowElement(string elementTag)
        {
            if (repository == null || !repository.IsCurrent || !repository.TryGet(elementTag, out StructuralElementARData row))
            {
                State = "STALE / NO DATA";
                elementRenderer?.Clear();
                return false;
            }
            if (row.elementTag != elementTag || row.element_id != elementTag)
            {
                State = "IDENTITY ERROR";
                elementRenderer?.Clear();
                return false;
            }
            AnchorPoseData pose;
            Transform anchor = directAnchor;
            if (anchorProvider != null && anchorProvider.TryGetAnchor(out pose)) anchor = anchorProvider.AnchorTransform;
            else pose = DirectPose();
            return RenderRow(row, anchor, pose);
        }

        // Integration point for a tracking module that prefers direct events.
        public bool ShowElement(string elementTag, AnchorPoseData anchorPose)
        {
            directAnchor.SetPositionAndRotation(anchorPose.position, anchorPose.rotation);
            directAnchor.localScale = anchorPose.scale == Vector3.zero ? Vector3.one : anchorPose.scale;
            if (repository == null || !repository.IsCurrent || !repository.TryGet(elementTag, out StructuralElementARData row))
            {
                State = "STALE / NO DATA";
                return false;
            }
            return RenderRow(row, directAnchor, anchorPose);
        }

        public void OnAnchorReady(AnchorPoseData anchorPose)
        {
            string tag = SelectedElement != null ? SelectedElement.elementTag : initialElementTag;
            ShowElement(tag, anchorPose);
        }

        bool RenderRow(StructuralElementARData row, Transform anchor, AnchorPoseData pose)
        {
            if (elementRenderer == null || transformAdapter == null) return false;
            SelectedElement = row;
            State = row.data_state == "CURRENT_VERIFIED" ? "CURRENT" : "CURRENT GEOMETRY / NO FE RESULT";
            elementRenderer.Render(row, anchor, transformAdapter, visualizationScale);
            ElementShown?.Invoke(row, State, pose);
            return elementRenderer.RenderedElementTag == row.elementTag;
        }

        void OnAnchorUpdated(AnchorPoseData pose)
        {
            if (SelectedElement != null) ElementShown?.Invoke(SelectedElement, State, pose);
        }

        AnchorPoseData DirectPose() => new AnchorPoseData
        {
            position = directAnchor.position,
            rotation = directAnchor.rotation,
            scale = directAnchor.lossyScale,
            trackingState = AnchorTrackingState.NotAvailable,
            referenceImageName = "DIRECT_ADAPTER"
        };
    }
}
