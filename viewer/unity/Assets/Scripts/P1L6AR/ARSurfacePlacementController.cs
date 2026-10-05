using System;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

namespace Mcoc.UnityViewer.P1L6AR
{
    public enum ARPlacementState { Choosing, Preview, Fixing, Placed }

    [DisallowMultipleComponent]
    public sealed class ARSurfacePlacementController : MonoBehaviour
    {
        ARStructuralElementController controller;
        IARSurfacePlacementBackend backend;
        ARPlacementPreview preview, placed;
        Transform placementAnchor;
        ARSurfaceHit lastHit;
        ARSurfacePlacementPose lastPose;
        Vector3 initialRight;
        int revision;
        float yawDegrees;
        Vector3 freeDepth;
        public bool FreePlacement { get; private set; }
        public bool CanAdjustFree => FreePlacement && State == ARPlacementState.Preview && SessionReady;
        bool validHit, previewFromSurface, placementVisible, placedFree;
        public bool SurfaceMode { get; private set; }
        public ARPlacementState State { get; private set; }
        public string Message { get; private set; } = "Elige VISTA RÁPIDA o COLOCAR EN SUPERFICIE.";
        public bool SessionReady => isActiveAndEnabled && backend != null && backend.IsTracking;
        public bool IsCommitting => State == ARPlacementState.Fixing;
        public bool CanFix => State == ARPlacementState.Preview && validHit && SessionReady;
        public bool CanRotate => CanFix && lastPose.canRotate;
        public bool HasTrackedPlacement => isActiveAndEnabled && SurfaceMode && State == ARPlacementState.Placed && placed != null &&
            placed.ElementId == controller?.SelectedElement?.element_id && backend.IsAnchorTracked(placementAnchor);
        public Transform PlacedRoot => placed != null ? placed.transform : null;
        public Transform PlacementAnchor => placementAnchor;
        public float PlacedUniformScale => placed != null ? placed.UniformScale : 0;
        public ARPlacementPreview Preview => preview;
        public bool CanChangeScale => State==ARPlacementState.Preview && SessionReady;
        public ARGeometryScaleMode ScaleMode => (State==ARPlacementState.Preview || IsCommitting) && preview!=null
            ? preview.ScaleMode : placed!=null && placed.ElementId==controller?.SelectedElement?.element_id ? placed.ScaleMode : ARGeometryScaleMode.Auto;

        void Awake()
        {
            controller = GetComponent<ARStructuralElementController>();
            if (controller == null) return;
            ARPlaneManager planes = GetComponent<ARPlaneManager>();
            if (planes == null) planes = gameObject.AddComponent<ARPlaneManager>();
            planes.requestedDetectionMode = PlaneDetectionMode.Horizontal | PlaneDetectionMode.Vertical;
            ARRaycastManager raycasts = GetComponent<ARRaycastManager>();
            if (raycasts == null) raycasts = gameObject.AddComponent<ARRaycastManager>();
            ARAnchorManager anchors = GetComponent<ARAnchorManager>();
            // The image tracker already has an anchor manager. Never replace it.
            backend = new ARFoundationSurfaceBackend(planes, raycasts, anchors);
            controller.RegisterSurfacePlacement(this);
            if (GetComponent<ARSurfacePlacementUI>() == null) gameObject.AddComponent<ARSurfacePlacementUI>();
        }

        // Same controller and dataset in tests, with only the hardware boundary substituted.
        public void SetBackend(IARSurfacePlacementBackend value) { backend = value; }

        public void StageSelection()
        {
            revision++;
            if (preview != null) preview.gameObject.SetActive(false);
            validHit = false; SurfaceMode = true;
            State = placed != null && placed.ElementId == controller.SelectedElement.element_id
                ? ARPlacementState.Placed : ARPlacementState.Choosing;
            Message = "Seleccionado " + controller.SelectedElement.element_id + ". Elige el modo de colocación.";
        }

        public void BeginPreview()
            => BeginPreview(ARGeometryScaleMode.Auto);

        void BeginPreview(ARGeometryScaleMode scaleMode)
        {
            if (IsCommitting || controller?.SelectedElement == null) return;
            if (!SessionReady) { Message = "Espera a que ARCore recupere el tracking del entorno."; return; }
            previewFromSurface = SurfaceMode;
            SurfaceMode = true; revision++;
            if (preview == null)
                preview = new GameObject("StructuralPlacementPreview").AddComponent<ARPlacementPreview>();
            preview.Configure(controller.SelectedElement,scaleMode);
            preview.gameObject.SetActive(false);
            Camera camera = Camera.main;
            initialRight = ARSurfacePlacementMath.InitialRight(camera != null ? camera.transform.forward : Vector3.forward);
            yawDegrees = 0; FreePlacement = false; validHit = false; State = ARPlacementState.Preview;
            Message = "Busca una superficie. Centro de pantalla = objetivo.";
        }

        void Update()
        {
            // Visibility can follow anchor tracking. The stored local pose never
            // follows plane changes, camera motion, or tracking recovery.
            if (placed != null) placed.gameObject.SetActive(placementVisible && backend.IsAnchorTracked(placementAnchor));
            if (State != ARPlacementState.Preview) return;
            if (FreePlacement)
            {
                // No camera reads or raycasts: reuse the manually adjusted pose.
                validHit = SessionReady;
                preview.gameObject.SetActive(validHit);
                Message = validHit ? "Colocación libre nivelada · sin superficie confirmada."
                    : "Tracking del entorno no disponible.";
                return;
            }
            validHit = false;
            Camera camera = Camera.main;
            if (SessionReady && camera != null && backend.TryHit(out ARSurfaceHit hit) &&
                ARSurfacePlacementMath.TryPose(controller.SelectedElement.type,
                    StructuralARElementRenderer.GetSizeMetres(controller.SelectedElement), hit,
                    camera.transform.position, initialRight, yawDegrees, preview.UniformScale, out ARSurfacePlacementPose pose))
            {
                lastHit = hit; lastPose = pose; validHit = true;
                preview.Apply(hit, pose); preview.gameObject.SetActive(true);
                Message = hit.kind == ARSurfaceKind.Ceiling ? "Techo · preview bajo la superficie."
                    : hit.kind == ARSurfaceKind.Wall ? "Pared · altura vertical. Giro en planta no aplicable aquí."
                    : "Piso / mesa · preview apoyado.";
                return;
            }
            if (preview != null) preview.gameObject.SetActive(false);
            Message = !SessionReady ? "Tracking del entorno no disponible."
                : controller?.SelectedElement?.type == "column" ? "Busca piso / mesa para apoyar la columna."
                : controller?.SelectedElement?.type == "wall" ? "Busca piso / mesa o pared."
                : "Busca techo o piso / mesa, o activa COLOCACIÓN LIBRE.";
        }

        public void Rotate90()
        { RotateYaw(90f); }

        public bool SetScaleMode(ARGeometryScaleMode mode)
        {
            if(!CanChangeScale || preview==null)return false;
            if(!preview.SetScaleMode(mode)) {Message=ARGeometryScale.Unavailable;return false;}
            lastPose.scale=preview.UniformScale;
            if(FreePlacement)preview.ApplyFree(lastPose.pose);
            else if(validHit && ARSurfacePlacementMath.TryPose(controller.SelectedElement.type,
                StructuralARElementRenderer.GetSizeMetres(controller.SelectedElement),lastHit,
                lastHit.point+lastPose.visibleNormal,initialRight,yawDegrees,preview.UniformScale,out var pose))
            {lastPose=pose;preview.Apply(lastHit,lastPose);}
            return true;
        }
        public void CycleScale()
        {
            if(!CanChangeScale || preview==null)return;
            if(!preview.HasPhysicalDimensions) {Message=ARGeometryScale.Unavailable;return;}
            SetScaleMode((ARGeometryScaleMode)(((int)preview.ScaleMode+1)%5));
        }

        public void RotateYaw(float degrees)
        {
            if (!CanRotate) return;
            yawDegrees = Mathf.Repeat(yawDegrees + degrees, 360f);
            lastPose.pose.rotation = ARSurfacePlacementMath.LevelRotation(initialRight, yawDegrees);
            if (FreePlacement) preview.ApplyFree(lastPose.pose);
            else preview.Apply(lastHit, lastPose);
        }

        public void UseFreePlacement()
        {
            if (State != ARPlacementState.Preview || !SessionReady || FreePlacement) return;
            Camera camera = Camera.main;
            if (camera == null) return;
            // Camera position/view ray is sampled once, including where the user
            // aims. Its pitch/roll never enters the structural rotation.
            initialRight = ARSurfacePlacementMath.InitialRight(camera.transform.forward);
            freeDepth = Vector3.Cross(initialRight, Vector3.up).normalized;
            yawDegrees = 0;
            lastPose = new ARSurfacePlacementPose
            {
                pose = new Pose(camera.transform.position + camera.transform.forward * 1.2f,
                    ARSurfacePlacementMath.LevelRotation(initialRight, 0)),
                scale = preview.UniformScale, canRotate = true, visibleNormal = Vector3.up
            };
            FreePlacement = true; validHit = true;
            preview.ApplyFree(lastPose.pose); preview.gameObject.SetActive(true);
            Message = "Colocación libre nivelada · ajusta altura y yaw antes de FIJAR.";
        }

        public void UseSurfacePlacement()
        {
            if (State != ARPlacementState.Preview || !SessionReady || !FreePlacement) return;
            FreePlacement = false; validHit = false; preview.gameObject.SetActive(false);
            Message = "Busca una superficie. Centro de pantalla = objetivo.";
        }

        public void MoveHeight(float metres)
        {
            if (!CanAdjustFree) return;
            lastPose.pose.position += Vector3.up * metres;
            preview.ApplyFree(lastPose.pose);
        }

        public void MoveDepth(float metres)
        {
            if (!CanAdjustFree) return;
            // Depth is the horizontal direction captured on entering free mode,
            // never the continuously changing camera forward or the member yaw.
            lastPose.pose.position += freeDepth * metres;
            preview.ApplyFree(lastPose.pose);
        }

        public async Task<bool> ConfirmAsync()
        {
            if (!CanFix || !isActiveAndEnabled) return false;
            int requestRevision = revision;
            Pose frozenPose = lastPose.pose;
            State = ARPlacementState.Fixing; Message = "Fijando anchor...";
            Transform created = null;
            try { created = await backend.CreateAnchorAsync(frozenPose); }
            catch (Exception exception) { Debug.LogWarning("[Surface placement] " + exception.Message); }
            // Selection, cancel, or lifecycle change may invalidate an async result.
            if (this == null || !isActiveAndEnabled || requestRevision != revision)
            { if (created != null) backend.RemoveAnchor(created); return false; }
            if (created == null)
            {
                State = ARPlacementState.Preview; validHit = false;
                Message = "No se pudo crear el anchor. Revisa el tracking y vuelve a pulsar FIJAR.";
                return false;
            }
            Transform previousAnchor = placementAnchor;
            ARPlacementPreview previousPlaced = placed;
            placementAnchor = created;
            // Preserve the snapshot world pose even if ARCore returns an anchor
            // frame with a slightly different pose; freeze the resulting local TRS.
            preview.transform.SetPositionAndRotation(frozenPose.position, frozenPose.rotation);
            preview.transform.SetParent(created, true);
            preview.name = "PlacedStructuralElementRoot_" + preview.ElementId;
            preview.SetPreview(false);
            placed = preview; preview = null; validHit = false;
            placementVisible = true;
            placedFree = FreePlacement;
            controller.SuspendQuickView();
            State = ARPlacementState.Placed;
            Message = "Fijado · " + placed.ElementId + " · escala " + ARGeometryScale.Label(placed.ScaleMode) + ". Puedes rodearlo.";
            if (previousPlaced != null) Destroy(previousPlaced.gameObject);
            if (previousAnchor != null) backend.RemoveAnchor(previousAnchor);
            controller.NotifySurfacePlacement(placed.UniformScale);
            return true;
        }
        public async void FixFromUI() { await ConfirmAsync(); }
        public void Relocate()
        {
            bool resumeFree = placedFree;
            BeginPreview(placed!=null && placed.ElementId==controller?.SelectedElement?.element_id ? placed.ScaleMode : ARGeometryScaleMode.Auto);
            if (resumeFree && State == ARPlacementState.Preview) UseFreePlacement();
        }
        public void Cancel()
        {
            revision++; validHit = false;
            if (preview != null) preview.gameObject.SetActive(false);
            State = placed != null && placed.ElementId == controller?.SelectedElement?.element_id
                ? ARPlacementState.Placed : ARPlacementState.Choosing;
            if (State == ARPlacementState.Placed) FreePlacement = placedFree;
            Message = State == ARPlacementState.Placed ? "Reubicación cancelada; colocación anterior conservada."
                : "Preview cancelado. Elige el modo de colocación.";
            if (!previewFromSurface && controller != null && controller.HasQuickViewAnchor)
            {
                SurfaceMode = false;
                controller.ShowElement(controller.SelectedElement.element_id);
            }
        }
        public void QuickView()
        {
            if (controller?.SelectedElement == null) return;
            if (IsCommitting) return;
            if (!controller.HasQuickViewAnchor) { Message = "VISTA RÁPIDA: enfoca ImagenPrueba."; return; }
            Cancel(); SurfaceMode = false;
            placementVisible = false;
            if (placed != null) placed.gameObject.SetActive(false);
            controller.ShowElement(controller.SelectedElement.element_id);
            Message = "VISTA RÁPIDA · comportamiento original sobre ImagenPrueba.";
        }
        void OnDisable()
        {
            revision++; validHit = false;
            if (preview != null) preview.gameObject.SetActive(false);
            if (placed != null) placed.gameObject.SetActive(false);
            State = placed != null ? ARPlacementState.Placed : ARPlacementState.Choosing;
        }
        void OnDestroy()
        {
            if (preview != null) Destroy(preview.gameObject);
            if (placed != null) Destroy(placed.gameObject);
            if (placementAnchor != null) backend?.RemoveAnchor(placementAnchor);
        }
    }
}
