using UnityEngine;
using UnityEngine.UI;

namespace Mcoc.UnityViewer.P1L6AR
{
    // Center-screen raycasts + explicit buttons; no touch-to-place handler can
    // accidentally interpret keyboard or UI touches as placement confirmation.
    public sealed class ARSurfacePlacementUI : MonoBehaviour
    {
        ARSurfacePlacementController placement;
        ARStructuralElementController controller;
        GameObject canvasObject, previewActions, placedActions;
        RectTransform safeArea;
        Text status;
        Button rotate, fix, yawLeft, yawRight, mode, raise, lower, near, far;
        Text modeLabel, scaleLabel;
        Button scaleButton;
        RectTransform previewRect, modeRow, statusRect;
        GameObject freeMotion;
        Font font;
        string lastMessage;
        ARPlacementState lastState;
        float toastUntil;
        void Start()
        {
            placement = GetComponent<ARSurfacePlacementController>();
            controller = GetComponent<ARStructuralElementController>();
            font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            canvasObject = new GameObject("SurfacePlacementUI", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            Canvas canvas = canvasObject.GetComponent<Canvas>(); canvas.renderMode = RenderMode.ScreenSpaceOverlay; canvas.sortingOrder = 22;
            CanvasScaler scaler = canvasObject.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1080, 1920); scaler.matchWidthOrHeight = 0;
            safeArea = Rect("SafeArea", canvasObject.transform, Vector2.zero, Vector2.one);
            statusRect = Bottom("PlacementStatus", 190, 68);
            statusRect.gameObject.AddComponent<Image>().color = new Color(.03f, .05f, .08f, .94f);
            status = Text("Message", statusRect, Vector2.zero, Vector2.one, "");
            previewRect = Bottom("PreviewActions", 12, 230);
            previewActions = previewRect.gameObject;
            RectTransform confirmation = Row("PreviewConfirmation", previewRect, 0, 72);
            fix = Button("FIJAR", confirmation, Vector2.zero, new Vector2(.49f, 1), placement.FixFromUI);
            Button("CANCELAR", confirmation, new Vector2(.51f, 0), Vector2.one, placement.Cancel);
            RectTransform yaw = Row("PreviewYaw", previewRect, 82, 72);
            yawLeft = Button("−5°", yaw, Vector2.zero, new Vector2(.24f, 1), () => placement.RotateYaw(-5));
            rotate = Button("GIRAR 90°", yaw, new Vector2(.26f, 0), new Vector2(.74f, 1), placement.Rotate90);
            yawRight = Button("+5°", yaw, new Vector2(.76f, 0), Vector2.one, () => placement.RotateYaw(5));
            RectTransform motion = Row("FreeMotion", previewRect, 164, 72); freeMotion = motion.gameObject;
            raise = Button("SUBIR", motion, Vector2.zero, new Vector2(.235f, 1), () => placement.MoveHeight(.05f));
            lower = Button("BAJAR", motion, new Vector2(.255f, 0), new Vector2(.49f, 1), () => placement.MoveHeight(-.05f));
            near = Button("ACERCAR", motion, new Vector2(.51f, 0), new Vector2(.745f, 1), () => placement.MoveDepth(-.05f));
            far = Button("ALEJAR", motion, new Vector2(.765f, 0), Vector2.one, () => placement.MoveDepth(.05f));
            modeRow = Row("PreviewMode", previewRect, 164, 66);
            mode = Button("COLOCACIÓN LIBRE", modeRow, Vector2.zero, new Vector2(.49f,1), () =>
            {
                if (placement.FreePlacement) placement.UseSurfacePlacement(); else placement.UseFreePlacement();
            });
            modeLabel = mode.GetComponentInChildren<Text>();
            scaleButton=Button("ESCALA: AUTO",modeRow,new Vector2(.51f,0),Vector2.one,placement.CycleScale);
            scaleLabel=scaleButton.GetComponentInChildren<Text>();
            RectTransform placedRect = Bottom("PlacedActions", 12, 164);
            placedActions = placedRect.gameObject;
            Button("VER INFORMACIÓN", placedRect, new Vector2(0, .51f), new Vector2(.49f, 1), () =>
            {
                GetComponent<LuisARDiagrams>()?.Close();
                GetComponent<LuisARTrackingUI>()?.OpenInformation();
            });
            Button("VER DIAGRAMAS", placedRect, new Vector2(.51f, .51f), Vector2.one, () =>
            {
                GetComponent<LuisARTrackingUI>()?.CloseInformation();
                GetComponent<LuisARDiagrams>()?.Open();
            });
            Button("REUBICAR", placedRect, Vector2.zero, new Vector2(1, .44f), placement.Relocate);
        }
        void Update()
        {
            if (canvasObject == null || placement == null || controller == null) return;
            canvasObject.SetActive(controller.SelectedElement != null && (controller.CanSelectElement || placement.SurfaceMode));
            Rect safe = Screen.safeArea;
            if (Screen.width > 0 && Screen.height > 0)
            {
                safeArea.anchorMin = new Vector2(safe.xMin / Screen.width, safe.yMin / Screen.height);
                safeArea.anchorMax = new Vector2(safe.xMax / Screen.width, safe.yMax / Screen.height);
            }
            bool preview = placement.SurfaceMode && (placement.State == ARPlacementState.Preview || placement.IsCommitting);
            rotate.interactable = placement.CanRotate;
            yawLeft.interactable = yawRight.interactable = placement.CanRotate;
            fix.interactable = placement.CanFix;
            mode.interactable = placement.State == ARPlacementState.Preview && placement.SessionReady;
            modeLabel.text = placement.FreePlacement ? "USAR SUPERFICIE" : "COLOCACIÓN LIBRE";
            bool physicalAvailable=placement.Preview!=null && placement.Preview.HasPhysicalDimensions;
            scaleButton.interactable=placement.CanChangeScale && physicalAvailable;
            scaleLabel.text="ESCALA: "+ARGeometryScale.Label(placement.ScaleMode);
            raise.interactable = lower.interactable = near.interactable = far.interactable = placement.CanAdjustFree;
            freeMotion.SetActive(placement.FreePlacement);
            previewRect.sizeDelta = new Vector2(-32, placement.FreePlacement ? 312 : 230);
            modeRow.anchoredPosition = new Vector2(0, placement.FreePlacement ? 246 : 164);
            statusRect.anchoredPosition = new Vector2(0, preview ? (placement.FreePlacement ? 336 : 254) : 190);
            bool detailsOpen = (GetComponent<LuisARTrackingUI>()?.InformationOpen ?? false) || (GetComponent<LuisARDiagrams>()?.IsOpen ?? false);
            previewActions.SetActive(preview && !detailsOpen);
            placedActions.SetActive(placement.HasTrackedPlacement && !detailsOpen &&
                !(GetComponent<ARStructuralElementSelectionUI>()?.SearchExpanded ?? false));
            if (lastMessage != placement.Message || lastState != placement.State)
            {
                lastMessage = placement.Message; lastState = placement.State;
                toastUntil = Time.unscaledTime + 2.5f;
                status.text = placement.State == ARPlacementState.Placed
                    ? lastMessage.StartsWith("Reubicación") ? "Reubicación cancelada · colocación anterior conservada" : "Elemento fijado"
                    : placement.State == ARPlacementState.Choosing && lastMessage.StartsWith("Preview cancelado")
                        ? "Colocación cancelada · selecciona un elemento" : "";
            }
            bool waiting = preview && !placement.CanFix;
            if (waiting) status.text = placement.IsCommitting ? "Fijando elemento…" : !placement.SessionReady
                ? "Espera al tracking AR del entorno" : "Busca una superficie";
            else if (placement.State == ARPlacementState.Preview)
                status.text = placement.FreePlacement ? "Libre nivelada · sin superficie confirmada" : "";
            bool trackingLost = placement.SurfaceMode && !placement.SessionReady;
            if (trackingLost) status.text = "Espera al tracking AR del entorno";
            bool scaleUnavailable=placement.State==ARPlacementState.Preview && !physicalAvailable;
            if(scaleUnavailable && !waiting && !trackingLost)status.text=ARGeometryScale.Unavailable;
            status.transform.parent.gameObject.SetActive(!detailsOpen && (waiting || trackingLost || scaleUnavailable ||
                (!string.IsNullOrEmpty(status.text) && Time.unscaledTime < toastUntil)));
        }
        RectTransform Bottom(string name, float bottom, float height)
        {
            RectTransform rect = Rect(name, safeArea, Vector2.zero, Vector2.right);
            rect.pivot = new Vector2(.5f, 0); rect.anchoredPosition = new Vector2(0, bottom);
            rect.sizeDelta = new Vector2(-32, height); return rect;
        }
        static RectTransform Row(string name, Transform parent, float bottom, float height)
        {
            RectTransform rect = Rect(name, parent, Vector2.zero, Vector2.right);
            rect.pivot = new Vector2(.5f, 0); rect.anchoredPosition = new Vector2(0, bottom);
            rect.sizeDelta = new Vector2(0, height); return rect;
        }
        void OnDisable() { if (canvasObject != null) canvasObject.SetActive(false); }
        void OnDestroy() { if (canvasObject != null) Destroy(canvasObject); }
        static RectTransform Rect(string name, Transform parent, Vector2 min, Vector2 max)
        {
            RectTransform rect = new GameObject(name, typeof(RectTransform)).GetComponent<RectTransform>();
            rect.SetParent(parent, false); rect.anchorMin = min; rect.anchorMax = max;
            rect.offsetMin = rect.offsetMax = Vector2.zero; return rect;
        }
        Text Text(string name, Transform parent, Vector2 min, Vector2 max, string value)
        {
            Text text = Rect(name, parent, min, max).gameObject.AddComponent<Text>();
            text.font = font; text.text = value; text.fontSize = 29; text.color = Color.white;
            text.alignment = TextAnchor.MiddleCenter; text.supportRichText = false;
            text.resizeTextForBestFit = true; text.resizeTextMinSize = 23; text.resizeTextMaxSize = 29;
            text.raycastTarget = false; return text;
        }
        Button Button(string value, Transform parent, Vector2 min, Vector2 max, UnityEngine.Events.UnityAction action)
        {
            RectTransform rect = Rect(value, parent, min, max);
            rect.gameObject.AddComponent<Image>().color = new Color(.12f, .30f, .47f, .98f);
            Button button = rect.gameObject.AddComponent<Button>(); button.targetGraphic = rect.GetComponent<Image>();
            Text("Label", rect, new Vector2(.015f, .03f), new Vector2(.985f, .97f), value);
            button.onClick.AddListener(action); return button;
        }
    }
}
