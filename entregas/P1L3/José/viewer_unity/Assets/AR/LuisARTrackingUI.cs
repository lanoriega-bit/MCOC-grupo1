using UnityEngine;
using UnityEngine.XR.ARSubsystems;
using UnityEngine.UI;
using TMPro;
using Mcoc.UnityViewer.P1L6AR;

public class LuisARTrackingUI : MonoBehaviour
{
    [SerializeField] GameObject beamTitle;
    [SerializeField] GameObject infoButton;
    [SerializeField] GameObject infoPanel;

    LuisARImageAnchor arTracking;
    ARStructuralElementController controller;
    TMP_Text titleText;
    TMP_Text infoText;
    string displayedInfo;

    void Awake()
    {
        arTracking = GetComponent<LuisARImageAnchor>();
        titleText = beamTitle != null ? beamTitle.GetComponentInChildren<TMP_Text>(true) : null;
        if (infoPanel != null)
            foreach (TMP_Text text in infoPanel.GetComponentsInChildren<TMP_Text>(true))
                if (text.name == "InfoText") { infoText = text; break; }
        if (titleText != null) titleText.text = "ELEMENTO ESTRUCTURAL";
        if (infoText != null)
        {
            infoText.text = ARSelectedElementInfo.Format(null);
            BuildInformationScroll();
        }
        // Installed at runtime; Luis_AR_Test needs no new scene assignments.
        if (GetComponent<ARStructuralElementSelectionUI>() == null)
            gameObject.AddComponent<ARStructuralElementSelectionUI>();

        // Al abrir la app, la información estructural
        // permanece oculta hasta detectar la imagen.
        if (beamTitle != null)
            beamTitle.SetActive(false);

        if (infoButton != null)
            infoButton.SetActive(false);

        if (infoPanel != null)
            infoPanel.SetActive(false);
    }

    void OnEnable()
    {
        if (arTracking != null)
            arTracking.TrackingUpdated += OnTrackingUpdated;
        if (controller != null) controller.ElementShown += OnElementShown;
    }

    void Start()
    {
        controller = GetComponent<ARStructuralElementController>();
        if (controller == null) controller = FindAnyObjectByType<ARStructuralElementController>();
        if (controller != null)
        {
            controller.ElementShown += OnElementShown;
            UpdateInformation(controller.SelectedElement);
        }
    }

    void OnDisable()
    {
        if (arTracking != null)
            arTracking.TrackingUpdated -= OnTrackingUpdated;
        if (controller != null) controller.ElementShown -= OnElementShown;
    }

    void OnElementShown(StructuralElementARData data, string state, AnchorPoseData anchor)
    {
        UpdateInformation(data);
    }

    void UpdateInformation(StructuralElementARData data)
    {
        if (titleText != null) titleText.text = data?.element_id ?? "ELEMENTO ESTRUCTURAL";
        var placement=controller?.SurfacePlacement;
        float factor=controller!=null ? controller.AppliedVisualizationScale : 0;
        if(placement!=null && placement.SurfaceMode && data!=null)
        {
            var preview=placement.Preview;
            var placed=placement.PlacedRoot!=null ? placement.PlacedRoot.GetComponent<ARPlacementPreview>() : null;
            factor=preview!=null && preview.ElementId==data.element_id && placement.State==ARPlacementState.Preview
                ? preview.UniformScale : placed!=null && placed.ElementId==data.element_id ? placed.UniformScale
                : ARSurfacePlacementMath.AutoScale(StructuralARElementRenderer.GetSizeMetres(data));
        }
        string next = ARSelectedElementInfo.Format(data,
            placement!=null && placement.SurfaceMode ? placement.ScaleMode : ARGeometryScaleMode.Auto,
            factor);
        if (infoText == null || next == displayedInfo) return;
        displayedInfo = next;
        infoText.text = next;
        if (infoText.rectTransform.parent != null)
        {
            ScrollRect scroll = infoText.GetComponentInParent<ScrollRect>(true);
            if (scroll != null) scroll.verticalNormalizedPosition = 1f;
        }
    }

    void BuildInformationScroll()
    {
        GameObject viewport = new GameObject("DynamicInfoScroll", typeof(RectTransform),
            typeof(Image), typeof(RectMask2D), typeof(ScrollRect));
        RectTransform rect = viewport.GetComponent<RectTransform>();
        rect.SetParent(infoPanel.transform, false);
        rect.SetAsFirstSibling();
        rect.anchorMin = new Vector2(0.04f, 0.12f);
        rect.anchorMax = new Vector2(0.96f, 0.90f);
        rect.offsetMin = rect.offsetMax = Vector2.zero;
        viewport.GetComponent<Image>().color = new Color(1, 1, 1, 0);
        RectTransform content = infoText.rectTransform;
        content.SetParent(rect, false);
        content.anchorMin = new Vector2(0, 1);
        content.anchorMax = new Vector2(1, 1);
        content.pivot = new Vector2(0.5f, 1);
        content.anchoredPosition = Vector2.zero;
        content.sizeDelta = Vector2.zero;
        infoText.alignment = TextAlignmentOptions.TopLeft;
        infoText.overflowMode = TextOverflowModes.Overflow;
        infoText.richText = false;
        ContentSizeFitter fitter = infoText.gameObject.AddComponent<ContentSizeFitter>();
        fitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;
        ScrollRect scroll = viewport.GetComponent<ScrollRect>();
        scroll.viewport = rect;
        scroll.content = content;
        scroll.horizontal = false;
        scroll.vertical = true;
        scroll.movementType = ScrollRect.MovementType.Clamped;
        scroll.scrollSensitivity = 35f;
    }

    void OnTrackingUpdated(
        string referenceImageName,
        Pose anchorPose,
        TrackingState trackingState)
    {
        if (controller != null && controller.SurfacePlacement != null && controller.SurfacePlacement.SurfaceMode)
            return;
        bool showUI =
            trackingState == TrackingState.Tracking &&
            arTracking != null &&
            arTracking.HasAnchor;

        if (beamTitle != null)
            beamTitle.SetActive(showUI);

        if (infoButton != null)
            infoButton.SetActive(showUI);

        // Si se pierde el tracking, también cerramos
        // el panel de información.
        if (!showUI && infoPanel != null)
            infoPanel.SetActive(false);
    }

    void Update()
    {
        if (controller == null || controller.SurfacePlacement == null) return;
        bool visible = controller.HasTrackedAnchor;
        if (beamTitle != null) beamTitle.SetActive(false);
        if (infoButton != null) infoButton.SetActive(false);
        if (!visible && infoPanel != null) infoPanel.SetActive(false);
    }
    public void OpenInformation()
    {
        if (controller != null && controller.HasTrackedAnchor && infoPanel != null) infoPanel.SetActive(true);
    }
    public bool InformationOpen => infoPanel != null && infoPanel.activeSelf;
    public void CloseInformation() { if (infoPanel != null) infoPanel.SetActive(false); }
}
