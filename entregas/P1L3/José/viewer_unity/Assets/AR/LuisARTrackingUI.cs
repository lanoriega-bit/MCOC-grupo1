using UnityEngine;
using UnityEngine.XR.ARSubsystems;

public class LuisARTrackingUI : MonoBehaviour
{
    [SerializeField] GameObject beamTitle;
    [SerializeField] GameObject infoButton;
    [SerializeField] GameObject infoPanel;

    LuisARImageAnchor arTracking;

    void Awake()
    {
        arTracking = GetComponent<LuisARImageAnchor>();

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
    }

    void OnDisable()
    {
        if (arTracking != null)
            arTracking.TrackingUpdated -= OnTrackingUpdated;
    }

    void OnTrackingUpdated(
        string referenceImageName,
        Pose anchorPose,
        TrackingState trackingState)
    {
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
}