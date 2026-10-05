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
        [SerializeField] bool automaticVisualizationScale = true;
        [SerializeField, Range(0.60f, 0.70f)] float targetVisibleSizeMetres = 0.65f;

        IAnchorProvider anchorProvider;
        IModelToARTransform transformAdapter;
        Transform directAnchor;

        public StructuralElementARData SelectedElement { get; private set; }
        public string State { get; private set; } = "NO DATA";
        public ARDatasetRepository Repository => repository;
        public ARSurfacePlacementController SurfacePlacement { get; private set; }
        public bool CanSelectElement => SurfacePlacement != null && SurfacePlacement.IsCommitting ? false
            : HasQuickViewAnchor || (SurfacePlacement != null && SurfacePlacement.SessionReady);
        public float AppliedVisualizationScale { get; private set; }
        public bool HasTrackedAnchor => SurfacePlacement != null && SurfacePlacement.SurfaceMode
            ? SurfacePlacement.HasTrackedPlacement : HasQuickViewAnchor;
        public bool HasQuickViewAnchor => anchorProvider != null &&
            anchorProvider.TryGetAnchor(out AnchorPoseData pose) &&
            pose.trackingState == AnchorTrackingState.Tracking && anchorProvider.AnchorTransform != null;
        public event Action<StructuralElementARData, string, AnchorPoseData> ElementShown;

        void Start()
        {
            // Only install on the existing AR scene; desktop/fake-anchor usage
            // retains its original behavior and has no hardware dependency.
            if (GetComponent<LuisARImageAnchor>() != null && GetComponent<ARSurfacePlacementController>() == null)
                gameObject.AddComponent<ARSurfacePlacementController>();
        }
        public void RegisterSurfacePlacement(ARSurfacePlacementController placement) { SurfacePlacement = placement; }
        public void SuspendQuickView() { elementRenderer?.SetVisible(false); }
        public void NotifySurfacePlacement(float uniformScale)
        {
            AppliedVisualizationScale = uniformScale;
            State = "CURRENT / SURFACE PLACED";
            Transform anchor = SurfacePlacement.PlacementAnchor;
            ElementShown?.Invoke(SelectedElement, State, new AnchorPoseData
            {
                position = anchor.position, rotation = anchor.rotation, scale = anchor.lossyScale,
                trackingState = AnchorTrackingState.Tracking, referenceImageName = "SURFACE_PLACEMENT"
            });
        }

        void Awake()
        {
            if (anchorProviderBehaviour == null)
                anchorProviderBehaviour = (MonoBehaviour)FindAnyObjectByType<LuisAnchorProviderAdapter>() ??
                    (MonoBehaviour)FindAnyObjectByType<FakeAnchorProvider>();
            anchorProvider = anchorProviderBehaviour as IAnchorProvider;
            transformAdapter = transformBehaviour as IModelToARTransform;
            directAnchor = new GameObject("DirectAnchorAdapter").transform;
            directAnchor.SetParent(transform, false);
            if (repository == null) repository = FindAnyObjectByType<ARDatasetRepository>();
            if (elementRenderer == null) elementRenderer = FindAnyObjectByType<StructuralARElementRenderer>();
            if (transformAdapter == null)
                transformAdapter = (IModelToARTransform)FindAnyObjectByType<TrackedModelToARTransformBehaviour>() ??
                    (IModelToARTransform)FindAnyObjectByType<IdentityModelToARTransform>();
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

        public bool ShowElement(string elementTag) => ShowElement(elementTag, false);

        // UI flow only: skip the legacy mode choice without changing placement.
        public bool ShowElement(string elementTag, bool startSurfacePreview)
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
            SelectedElement = row;
            if (SurfacePlacement != null && (startSurfacePreview || SurfacePlacement.SurfaceMode ||
                (!HasQuickViewAnchor && SurfacePlacement.SessionReady)))
            {
                SurfacePlacement.StageSelection();
                State = "CURRENT / CHOOSE PLACEMENT";
                ElementShown?.Invoke(row, State, default);
                if (startSurfacePreview) SurfacePlacement.BeginPreview();
                return true;
            }
            AnchorPoseData pose;
            Transform anchor = directAnchor;
            if (anchorProvider != null)
            {
                if (!anchorProvider.TryGetAnchor(out pose) ||
                    pose.trackingState != AnchorTrackingState.Tracking ||
                    anchorProvider.AnchorTransform == null)
                {
                    State = pose.trackingState == AnchorTrackingState.Limited
                        ? "TRACKING LIMITED / ELEMENT HIDDEN"
                        : "TRACKING UNAVAILABLE / ELEMENT HIDDEN";
                    elementRenderer?.SetVisible(false);
                    ElementShown?.Invoke(row, State, pose);
                    return false;
                }
                anchor = anchorProvider.AnchorTransform;
            }
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
            SelectedElement = row;
            if (anchorPose.trackingState != AnchorTrackingState.Tracking)
            {
                State = anchorPose.trackingState == AnchorTrackingState.Limited
                    ? "TRACKING LIMITED / ELEMENT HIDDEN" : "TRACKING UNAVAILABLE / ELEMENT HIDDEN";
                elementRenderer?.SetVisible(false);
                ElementShown?.Invoke(row, State, anchorPose);
                return false;
            }
            return RenderRow(row, directAnchor, anchorPose);
        }

        public void OnAnchorReady(AnchorPoseData anchorPose)
        {
            if (SurfacePlacement != null && SurfacePlacement.SurfaceMode) return;
            string tag = SelectedElement != null ? SelectedElement.elementTag : initialElementTag;
            ShowElement(tag, anchorPose);
        }

        bool RenderRow(StructuralElementARData row, Transform anchor, AnchorPoseData pose)
        {
            if (elementRenderer == null || transformAdapter == null) return false;
            SelectedElement = row;
            State = row.data_state == "CURRENT_VERIFIED" ? "CURRENT" : "CURRENT GEOMETRY / NO FE RESULT";
            // Repeated tracking callbacks (including recovery) must reuse the
            // placement. Its local position, rotation and scale stay frozen.
            Transform existing = elementRenderer.RenderedTransform;
            if (existing != null && elementRenderer.RenderedElementTag == row.elementTag && existing.parent == anchor)
            {
                elementRenderer.SetVisible(true);
                ElementShown?.Invoke(row, State, pose);
                return true;
            }
            AppliedVisualizationScale = visualizationScale;
            if (automaticVisualizationScale && (row.type == "beam" || row.type == "column" || row.type == "wall"))
            {
                Vector3 unitSize = transformAdapter.ToAnchorLocalScale(StructuralARElementRenderer.GetSizeMetres(row), 1f);
                Vector3 worldSize = Vector3.Scale(unitSize, anchor.lossyScale);
                float largest = Mathf.Max(Mathf.Abs(worldSize.x), Mathf.Abs(worldSize.y), Mathf.Abs(worldSize.z));
                if (largest > 1e-6f)
                    AppliedVisualizationScale = Mathf.Clamp(targetVisibleSizeMetres, 0.60f, 0.70f) / largest;
            }
            elementRenderer.Render(row, anchor, transformAdapter, AppliedVisualizationScale);
            ElementShown?.Invoke(row, State, pose);
            return elementRenderer.RenderedElementTag == row.elementTag;
        }

        void OnAnchorUpdated(AnchorPoseData pose)
        {
            // Image tracking continues normally, but must not render or hide
            // anything owned by the independent surface placement mode.
            if (SurfacePlacement != null && SurfacePlacement.SurfaceMode) return;
            if (pose.trackingState == AnchorTrackingState.Tracking)
            {
                string tag = SelectedElement != null ? SelectedElement.elementTag : initialElementTag;
                ShowElement(tag);
                return;
            }

            elementRenderer?.SetVisible(false);
            State = pose.trackingState == AnchorTrackingState.Limited
                ? "TRACKING LIMITED / ELEMENT HIDDEN"
                : "TRACKING UNAVAILABLE / ELEMENT HIDDEN";
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
