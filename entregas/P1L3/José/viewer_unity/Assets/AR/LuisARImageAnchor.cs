using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

public class LuisARImageAnchor : MonoBehaviour
{
    [SerializeField] ARTrackedImageManager trackedImageManager;
    [SerializeField] ARAnchorManager anchorManager;
    [SerializeField] GameObject cubePrefab;

    ARAnchor currentAnchor;
    GameObject currentCube;
    bool creatingAnchor = false;

    void OnEnable()
    {
        trackedImageManager.trackablesChanged.AddListener(OnTrackablesChanged);
    }

    void OnDisable()
    {
        trackedImageManager.trackablesChanged.RemoveListener(OnTrackablesChanged);
    }

    void OnTrackablesChanged(
        ARTrackablesChangedEventArgs<ARTrackedImage> args)
    {
        foreach (var image in args.added)
        {
            HandleImage(image);
        }

        foreach (var image in args.updated)
        {
            HandleImage(image);
        }
    }

    async void HandleImage(ARTrackedImage image)
    {
        if (image.referenceImage.name != "ImagenPrueba")
            return;

        Debug.Log(
            $"IMAGEN DETECTADA: {image.referenceImage.name}\n" +
            $"Tracking: {image.trackingState}\n" +
            $"Position: {image.transform.position}\n" +
            $"Rotation: {image.transform.rotation}"
        );

        if (image.trackingState != TrackingState.Tracking)
            return;

        if (currentAnchor != null || creatingAnchor)
            return;

        creatingAnchor = true;

        Pose anchorPose = new Pose(
            image.transform.position,
            image.transform.rotation
        );

        var result = await anchorManager.TryAddAnchorAsync(anchorPose);

        creatingAnchor = false;

        if (result.status.IsSuccess())
        {
            currentAnchor = result.value;

            currentCube = Instantiate(
                cubePrefab,
                currentAnchor.transform
            );

            currentCube.transform.localPosition =
                new Vector3(0f, 0.025f, 0f);

            currentCube.transform.localRotation =
                Quaternion.identity;

            Debug.Log(
                $"ANCHOR CREADO\n" +
                $"Position: {currentAnchor.transform.position}\n" +
                $"Rotation: {currentAnchor.transform.rotation}"
            );
        }
        else
        {
            Debug.LogError("No se pudo crear el anchor.");
        }
    }
}