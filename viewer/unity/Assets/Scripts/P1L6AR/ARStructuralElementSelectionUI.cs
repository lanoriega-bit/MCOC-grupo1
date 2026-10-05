using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

namespace Mcoc.UnityViewer.P1L6AR
{
    [DisallowMultipleComponent]
    public sealed class ARStructuralElementSelectionUI : MonoBehaviour
    {
        ARStructuralElementController controller;
        ARDatasetRepository repository;
        GameObject canvasObject;
        RectTransform safeArea;
        InputField elementId;
        Button showButton;
        Text status;
        bool seenAnchor;
        bool wasReady;
        bool subscribed;
        Rect lastSafeArea;
        Vector2Int lastScreenSize;
        string shownId;
        string shownState;
        BaseInputModule inputModule;
        ARSelectionTextInput textInput;
        GameObject searchPanel, compactPanel;
        Text compactTitle;
        Button changeButton;
        bool expanded = true;
        float statusUntil;
        public bool SearchExpanded => expanded;
        public void ExpandSearch()
        {
            GetComponent<LuisARDiagrams>()?.Close();
            GetComponent<LuisARTrackingUI>()?.CloseInformation();
            expanded = true;
            if (elementId != null) elementId.SetTextWithoutNotify(controller.SelectedElement?.element_id ?? "");
            if (status != null) status.text = "";
        }

        void Start()
        {
            controller = GetComponent<ARStructuralElementController>();
            if (controller == null) controller = FindAnyObjectByType<ARStructuralElementController>();
            repository = controller != null ? controller.Repository : null;
            if (repository == null) repository = FindAnyObjectByType<ARDatasetRepository>();
            InstallTextInput();
            BuildUI();
            Subscribe();
            InstallTextInput();
            if (controller?.SelectedElement != null)
                elementId.SetTextWithoutNotify(controller.SelectedElement.element_id);
            RefreshAvailability();
        }

        void OnEnable()
        {
            Subscribe();
            if (canvasObject != null) RefreshAvailability();
        }

        void Subscribe()
        {
            if (subscribed || controller == null) return;
            controller.ElementShown += OnElementShown;
            subscribed = true;
        }

        void OnDisable()
        {
            if (subscribed && controller != null) controller.ElementShown -= OnElementShown;
            subscribed = false;
            if (inputModule != null && inputModule.inputOverride == textInput)
                inputModule.inputOverride = null;
            if (canvasObject != null) canvasObject.SetActive(false);
        }

        void OnDestroy()
        {
            if (canvasObject != null) Destroy(canvasObject);
        }

        void Update()
        {
            if (canvasObject == null) return;
            InstallTextInput();
            RefreshAvailability();
            ApplySafeArea();
            RefreshLayout();
        }

        void InstallTextInput()
        {
            EventSystem events = EventSystem.current;
            if (events == null) return;
            BaseInputModule module = events.currentInputModule != null
                ? events.currentInputModule : events.GetComponent<BaseInputModule>();
            if (module == null || module.GetType().FullName != "UnityEngine.InputSystem.UI.InputSystemUIInputModule") return;
            if (module.inputOverride != null) return;
            if (textInput == null) textInput = gameObject.AddComponent<ARSelectionTextInput>();
            inputModule = module;
            inputModule.inputOverride = textInput;
        }

        void RefreshAvailability()
        {
            bool tracked = controller != null && controller.CanSelectElement;
            seenAnchor |= tracked;
            canvasObject.SetActive(controller != null && controller.SurfacePlacement != null || seenAnchor);
            bool ready = tracked && repository != null && repository.IsCurrent;
            showButton.interactable = ready;
            elementId.interactable = ready;
            if (!ready)
            {
                statusUntil = float.PositiveInfinity;
                status.text = !tracked ? controller?.SurfacePlacement != null
                    ? "Espera al tracking AR del entorno."
                    : "Vuelve a enfocar ImagenPrueba para mostrar el elemento."
                    : !string.IsNullOrEmpty(repository?.Error) ? repository.Error : "Cargando dataset CURRENT...";
            }
            else if (!wasReady)
                status.text = "";
            wasReady = ready;
        }

        public bool TryShowElement(string input)
        {
            string id = (input ?? string.Empty).Trim().ToUpperInvariant();
            if (elementId != null) elementId.SetTextWithoutNotify(id);
            if (id.Length == 0) return ReportError("Escribe un element_id.");
            if (controller == null || repository == null || !repository.IsCurrent)
                return ReportError("El dataset CURRENT todavía no está disponible.");
            if (!controller.CanSelectElement)
                return ReportError(controller.SurfacePlacement != null
                    ? "Espera al tracking AR. Se conserva la selección."
                    : "Vuelve a enfocar ImagenPrueba. No se ha cambiado la selección.");
            if (!repository.TryGet(id, out StructuralElementARData row))
                return ReportError("ID no encontrado: " + id + ". Se conserva el elemento anterior.");
            if (row.type != "beam" && row.type != "column" && row.type != "wall")
                return ReportError("Selecciona un BEAM, COLUMN o WALL. Se conserva el elemento anterior.");
            if (controller.SurfacePlacement != null && !controller.SurfacePlacement.SessionReady)
                return ReportError("Espera al tracking AR del entorno. Se conserva el elemento anterior.");
            GetComponent<LuisARDiagrams>()?.Close();
            GetComponent<LuisARTrackingUI>()?.CloseInformation();
            if (!controller.ShowElement(row.element_id, controller.SurfacePlacement != null))
                return ReportError("No se pudo mostrar " + id + ": " + controller.State);
            elementId?.DeactivateInputField();
            EventSystem.current?.SetSelectedGameObject(null);
            expanded = controller.SurfacePlacement == null;
            if (status != null) status.text = "";
            RefreshLayout();
            return true;
        }

        bool ReportError(string message)
        {
            if (status != null) status.text = message;
            statusUntil = float.PositiveInfinity;
            return false;
        }

        void OnElementShown(StructuralElementARData data, string state, AnchorPoseData anchor)
        {
            if (data == null || elementId == null) return;
            if (shownId == data.element_id && shownState == state) return;
            shownId = data.element_id;
            shownState = state;
            if (!elementId.isFocused) elementId.SetTextWithoutNotify(data.element_id);
            if (controller.SurfacePlacement == null) status.text = "Mostrando " + data.element_id;
            if (controller.SurfacePlacement != null && controller.SurfacePlacement.State == ARPlacementState.Placed)
                expanded = false;
        }

        void BuildUI()
        {
            canvasObject = new GameObject("ARStructuralElementSelector", typeof(RectTransform),
                typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            Canvas canvas = canvasObject.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 20;
            CanvasScaler scaler = canvasObject.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1080, 1920);
            scaler.matchWidthOrHeight = 0f;
            safeArea = new GameObject("SafeArea", typeof(RectTransform)).GetComponent<RectTransform>();
            safeArea.SetParent(canvasObject.transform, false);
            RectTransform panel = MakeRect("ElementSearch", safeArea, new Vector2(0, 1), new Vector2(1, 1),
                new Vector2(0.5f, 1), new Vector2(0, -12), new Vector2(-32, 100));
            searchPanel = panel.gameObject;
            panel.gameObject.AddComponent<Image>().color = new Color(0.03f, 0.05f, 0.08f, 0.96f);
            RectTransform inputRect = MakeRect("ElementId", panel, new Vector2(0, 1), new Vector2(1, 1),
                new Vector2(0, 1), new Vector2(12, -10), new Vector2(-232, 80));
            Image inputBackground = inputRect.gameObject.AddComponent<Image>();
            inputBackground.color = Color.white;
            elementId = inputRect.gameObject.AddComponent<InputField>();
            elementId.targetGraphic = inputBackground;
            elementId.lineType = InputField.LineType.SingleLine;
            elementId.characterLimit = 64;
            Text inputText = AddText(inputRect, "Text", "", 38, new Vector2(16, -10), new Vector2(-32, -20), true);
            inputText.color = Color.black;
            inputText.supportRichText = false;
            elementId.textComponent = inputText;
            Text placeholder = AddText(inputRect, "Placeholder", "element_id", 34,
                new Vector2(16, -10), new Vector2(-32, -20), true);
            placeholder.color = new Color(0.4f, 0.4f, 0.4f);
            elementId.placeholder = placeholder;
            RectTransform buttonRect = MakeRect("Show", panel, new Vector2(1, 1), new Vector2(1, 1),
                new Vector2(1, 1), new Vector2(-12, -10), new Vector2(196, 80));
            Image buttonImage = buttonRect.gameObject.AddComponent<Image>();
            buttonImage.color = new Color(0.13f, 0.45f, 0.72f);
            showButton = buttonRect.gameObject.AddComponent<Button>();
            showButton.targetGraphic = buttonImage;
            Text buttonText = AddText(buttonRect, "Label", "MOSTRAR", 32, Vector2.zero, Vector2.zero, true);
            buttonText.alignment = TextAnchor.MiddleCenter;
            showButton.onClick.AddListener(() => TryShowElement(elementId.text));
            RectTransform statusRect = MakeRect("SearchStatus", safeArea, new Vector2(0, 1), new Vector2(1, 1),
                new Vector2(.5f, 1), new Vector2(0, -120), new Vector2(-32, 72));
            statusRect.gameObject.AddComponent<Image>().color = new Color(.03f, .05f, .08f, .85f);
            status = AddText(statusRect, "Status", "", 28, Vector2.zero, Vector2.zero, true);
            status.alignment = TextAnchor.MiddleCenter;
            RectTransform compact = MakeRect("SelectedElementBar", safeArea, new Vector2(0, 1), new Vector2(1, 1),
                new Vector2(.5f, 1), new Vector2(0, -12), new Vector2(-32, 80));
            compactPanel = compact.gameObject;
            compact.gameObject.AddComponent<Image>().color = new Color(.03f, .05f, .08f, .85f);
            compactTitle = AddText(compact, "SelectedId", "", 32, new Vector2(16, -8), new Vector2(-240, -16), true);
            compactTitle.alignment = TextAnchor.MiddleLeft;
            RectTransform change = MakeRect("Change", compact, Vector2.one, Vector2.one, Vector2.one,
                new Vector2(-12, -8), new Vector2(196, 64));
            Image changeImage = change.gameObject.AddComponent<Image>(); changeImage.color = new Color(.13f, .45f, .72f);
            changeButton = change.gameObject.AddComponent<Button>(); changeButton.targetGraphic = changeImage;
            AddText(change, "Label", "CAMBIAR", 28, Vector2.zero, Vector2.zero, true).alignment = TextAnchor.MiddleCenter;
            changeButton.onClick.AddListener(ExpandSearch);
            ApplySafeArea();
            canvasObject.SetActive(false);
        }

        void ApplySafeArea()
        {
            Rect area = Screen.safeArea;
            Vector2Int screen = new Vector2Int(Screen.width, Screen.height);
            ApplySafeArea(area, screen);
        }

        void ApplySafeArea(Rect area, Vector2Int screen)
        {
            if (screen.x <= 0 || screen.y <= 0 || (area == lastSafeArea && screen == lastScreenSize)) return;
            safeArea.anchorMin = new Vector2(area.xMin / screen.x, area.yMin / screen.y);
            safeArea.anchorMax = new Vector2(area.xMax / screen.x, area.yMax / screen.y);
            safeArea.offsetMin = safeArea.offsetMax = Vector2.zero;
            lastSafeArea = area;
            lastScreenSize = screen;
        }

        void RefreshLayout()
        {
            if (searchPanel == null) return;
            bool details = (GetComponent<LuisARTrackingUI>()?.InformationOpen ?? false) ||
                (GetComponent<LuisARDiagrams>()?.IsOpen ?? false);
            var placement = controller?.SurfacePlacement;
            bool preview = placement != null && (placement.State == ARPlacementState.Preview || placement.IsCommitting);
            if (preview) expanded = false;
            if (placement != null && placement.State == ARPlacementState.Choosing && !preview) expanded = true;
            searchPanel.SetActive(expanded && !details);
            compactPanel.SetActive(!expanded && !details && controller?.SelectedElement != null);
            compactTitle.text = controller?.SelectedElement == null ? "" : controller.SelectedElement.element_id + " · " + controller.SelectedElement.type.ToUpperInvariant();
            changeButton.gameObject.SetActive(!preview);
            status.transform.parent.gameObject.SetActive(expanded && !details && !string.IsNullOrEmpty(status.text) && Time.unscaledTime <= statusUntil);
        }

        static RectTransform MakeRect(string name, Transform parent, Vector2 min, Vector2 max,
            Vector2 pivot, Vector2 position, Vector2 size)
        {
            RectTransform rect = new GameObject(name, typeof(RectTransform)).GetComponent<RectTransform>();
            rect.SetParent(parent, false);
            rect.anchorMin = min;
            rect.anchorMax = max;
            rect.pivot = pivot;
            rect.anchoredPosition = position;
            rect.sizeDelta = size;
            return rect;
        }

        static Text AddText(Transform parent, string name, string content, int fontSize,
            Vector2 position, Vector2 size, bool stretch = false)
        {
            RectTransform rect = MakeRect(name, parent, stretch ? Vector2.zero : new Vector2(0, 1),
                stretch ? Vector2.one : new Vector2(0, 1), new Vector2(0, 1), position, size);
            Text text = rect.gameObject.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = fontSize;
            text.text = content;
            text.color = Color.white;
            text.raycastTarget = false;
            text.supportRichText = false;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            return text;
        }
    }
}
