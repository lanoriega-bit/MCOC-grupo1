using System;
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

public class LuisARImageAnchor : MonoBehaviour
{
    [SerializeField] ARTrackedImageManager trackedImageManager;
    [SerializeField] ARAnchorManager anchorManager;
    [SerializeField] GameObject cubePrefab;

    public string ReferenceImageName { get; private set; }

    public Pose AnchorPose { get; private set; }

    public TrackingState TrackingStatus { get; private set; }

    public bool HasAnchor =>
        currentAnchor != null;

    // Permite que los nuevos scripts AR utilicen
    // exactamente el mismo anchor creado por este módulo.
    public Transform AnchorTransform =>
        currentAnchor != null
            ? currentAnchor.transform
            : null;

    public event Action<string, Pose, TrackingState>
        TrackingUpdated;

    ARAnchor currentAnchor;
    GameObject currentCube;

    bool creatingAnchor = false;

    void OnEnable()
    {
        if (trackedImageManager != null)
        {
            trackedImageManager.trackablesChanged
                .AddListener(OnTrackablesChanged);
        }
    }

    void OnDisable()
    {
        if (trackedImageManager != null)
        {
            trackedImageManager.trackablesChanged
                .RemoveListener(OnTrackablesChanged);
        }
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

    async void HandleImage(
        ARTrackedImage image)
    {
        if (image == null)
            return;

        if (image.referenceImage.name != "ImagenPrueba")
            return;

        ReferenceImageName =
            image.referenceImage.name;

        TrackingStatus =
            image.trackingState;

        Pose detectedPose =
            new Pose(
                image.transform.position,
                image.transform.rotation
            );

        // Si ya existe un anchor usamos su pose.
        // Si todavía no existe, usamos temporalmente
        // la pose detectada de la imagen.
        AnchorPose =
            currentAnchor != null
                ? new Pose(
                    currentAnchor.transform.position,
                    currentAnchor.transform.rotation
                )
                : detectedPose;

        TrackingUpdated?.Invoke(
            ReferenceImageName,
            AnchorPose,
            TrackingStatus
        );

        Debug.Log(
            $"IMAGEN DETECTADA: {ReferenceImageName}\n" +
            $"Tracking: {TrackingStatus}\n" +
            $"Position: {AnchorPose.position}\n" +
            $"Rotation: {AnchorPose.rotation}"
        );

        // Solo intentamos crear el anchor cuando
        // AR Foundation confirma tracking real.
        if (image.trackingState != TrackingState.Tracking)
            return;

        // Evita crear anchors duplicados.
        if (currentAnchor != null ||
            creatingAnchor)
            return;

        creatingAnchor = true;

        var result =
            await anchorManager.TryAddAnchorAsync(
                detectedPose
            );

        creatingAnchor = false;

        if (result.status.IsSuccess())
        {
            currentAnchor =
                result.value;

            AnchorPose =
                new Pose(
                    currentAnchor.transform.position,
                    currentAnchor.transform.rotation
                );

            // Mantiene el objeto de prueba que ya
            // utilizábamos para comprobar el anchor.
            if (cubePrefab != null)
            {
                currentCube =
                    Instantiate(
                        cubePrefab,
                        currentAnchor.transform
                    );

                currentCube.transform.localPosition =
                    new Vector3(
                        0f,
                        0.025f,
                        0f
                    );

                currentCube.transform.localRotation =
                    Quaternion.identity;
            }

            TrackingUpdated?.Invoke(
                ReferenceImageName,
                AnchorPose,
                TrackingStatus
            );

            Debug.Log(
                $"ANCHOR CREADO\n" +
                $"Position: {AnchorPose.position}\n" +
                $"Rotation: {AnchorPose.rotation}"
            );
        }
        else
        {
            Debug.LogError(
                "No se pudo crear el anchor."
            );
        }
    }
}