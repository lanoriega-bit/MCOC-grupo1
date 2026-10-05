using System.Globalization;
using UnityEngine;
using UnityEngine.UI;
using Mcoc.UnityViewer.P1L6AR;

public class LuisARDiagrams : MonoBehaviour
{
    // Preserve the existing scene assignments. Tracking is read through the
    // controller's existing provider; this component never changes AR state.
    [SerializeField] LuisARImageAnchor arTracking;
    [SerializeField] GameObject infoPanel;

    ARStructuralElementController controller;
    StructuralElementARData selected;
    GameObject canvasObject, panel;
    RectTransform safeArea;
    Text title, metadata, values, axis, description;
    Button launcher, previous, next;
    Text caseLabel;
    readonly Button[] components = new Button[6];
    ARForceDiagramGraphic graph;
    int segmentIndex, componentIndex = 4;
    bool subscribed, restoreInfo;
    Font font;
    public bool IsOpen => panel != null && panel.activeSelf;
    ARStructuralResultOverlay3D overlay;
    GameObject overlayActions;
    Button overlayToggle;
    Text overlayCaption, overlayNote;

    void Start()
    {
        controller = GetComponent<ARStructuralElementController>();
        if (controller == null) controller = FindAnyObjectByType<ARStructuralElementController>();
        overlay = GetComponent<ARStructuralResultOverlay3D>();
        if (overlay == null) overlay = gameObject.AddComponent<ARStructuralResultOverlay3D>();
        BuildUI();
        Subscribe();
        Select(controller?.SelectedElement);
        RefreshVisibility();
    }

    void OnEnable() { Subscribe(); }
    void Subscribe()
    {
        if (subscribed || controller == null) return;
        controller.ElementShown += OnElementShown;
        subscribed = true;
        Select(controller.SelectedElement);
    }
    void OnDisable()
    {
        if (subscribed && controller != null) controller.ElementShown -= OnElementShown;
        subscribed = false;
        Close();
        if (canvasObject != null) canvasObject.SetActive(false);
    }
    void OnDestroy() { if (canvasObject != null) Destroy(canvasObject); }
    void OnElementShown(StructuralElementARData row, string state, AnchorPoseData pose) { Select(row); }
    void Select(StructuralElementARData row)
    {
        if (selected == row) return; // Tracking notifications retain UI selection.
        selected = row;
        segmentIndex = 0;
        if (title != null) RefreshDiagram();
    }

    void Update()
    {
        if (canvasObject == null) return;
        RefreshVisibility();
        Rect safe = Screen.safeArea;
        if (Screen.width > 0 && Screen.height > 0)
        {
            safeArea.anchorMin = new Vector2(safe.xMin / Screen.width, safe.yMin / Screen.height);
            safeArea.anchorMax = new Vector2(safe.xMax / Screen.width, safe.yMax / Screen.height);
        }
        if (panel.activeSelf && infoPanel != null && infoPanel.activeSelf)
        {
            restoreInfo = true;
            infoPanel.SetActive(false);
        }
    }
    void RefreshVisibility()
    {
        bool tracked = controller != null && controller.HasTrackedAnchor;
        if (!tracked) { restoreInfo = false; Close(); }
        canvasObject.SetActive(tracked);
        launcher.interactable = selected != null;
        RefreshOverlayControls();
        if (controller != null && controller.SurfacePlacement != null) launcher.gameObject.SetActive(false);
    }

    public void Open()
    {
        if (panel == null || selected == null || controller == null || !controller.HasTrackedAnchor) return;
        if (!panel.activeSelf) restoreInfo = infoPanel != null && infoPanel.activeSelf;
        if (infoPanel != null) infoPanel.SetActive(false);
        RefreshDiagram();
        panel.SetActive(true);
        launcher.gameObject.SetActive(false);
        RefreshOverlayControls();
    }
    public void Close()
    {
        if (panel == null) return;
        panel.SetActive(false);
        if (overlayActions != null) overlayActions.SetActive(false);
        launcher.gameObject.SetActive(true);
        if (restoreInfo && infoPanel != null && controller != null && controller.HasTrackedAnchor)
            infoPanel.SetActive(true);
        restoreInfo = false;
    }
    void MoveSegment(int step)
    {
        segmentIndex = Mathf.Clamp(segmentIndex + step, 0, ARCurrentDiagramData.SegmentCount(selected) - 1);
        RefreshDiagram();
    }
    bool CurrentDataset => controller?.Repository != null && controller.Repository.IsCurrent &&
        controller.Repository.Dataset?.format == "MCOC_P1L6_AR_CURRENT_ELEMENTS_V1";

    void RefreshDiagram()
    {
        title.text = "Diagramas · " + (selected?.element_id ?? "Sin selección");
        int count = ARCurrentDiagramData.SegmentCount(selected);
        bool anyValid = false;
        for (int component = 0; component < 6; component++)
        {
            bool valid = CurrentDataset && ARCurrentDiagramData.TryValues(selected, segmentIndex, component, out _, out _);
            components[component].gameObject.SetActive(valid);
            components[component].GetComponent<Image>().color = component == componentIndex
                ? new Color(.12f, .38f, .66f) : new Color(.28f, .31f, .36f);
            anyValid |= valid;
        }
        if (anyValid && !ARCurrentDiagramData.TryValues(selected, segmentIndex, componentIndex, out _, out _))
            for (int component = 0; component < 6; component++)
                if (ARCurrentDiagramData.TryValues(selected, segmentIndex, component, out _, out _)) { componentIndex = component; break; }
        caseLabel.gameObject.SetActive(anyValid);
        previous.gameObject.SetActive(count > 1);
        next.gameObject.SetActive(count > 1);
        previous.interactable = segmentIndex > 0;
        next.interactable = segmentIndex < count - 1;
        ARResultSegment segment = count > 0 ? selected.current_result_R.segments[segmentIndex] : null;
        metadata.text = segment == null ? "Sin segmentos FE CURRENT disponibles."
            : "Segmento " + (segmentIndex + 1) + " / " + count + " · " + selected.type.ToUpperInvariant() +
                "\n" + segment.analysis_id + " · OpenSees " + segment.opensees_tag +
                "\nNodo i: " + segment.node_i + "    →    Nodo j: " + segment.node_j;
        double i = double.NaN, j = double.NaN;
        bool available = CurrentDataset && ARCurrentDiagramData.TryValues(selected, segmentIndex, componentIndex, out i, out j);
        graph.SetComponent(componentIndex);
        graph.SetValues(available, i, j);
        string unit = ARCurrentDiagramData.Units(componentIndex);
        values.text = available ? ARCurrentDiagramData.Components[componentIndex] + " · CASE_R · " + unit +
            "\ni: " + Number(i) + "    |    j: " + Number(j) : "Resultados CURRENT no disponibles para este segmento.";
        double length = ARCurrentDiagramData.SegmentLength(selected, segmentIndex);
        axis.text = double.IsNaN(length) ? "i  →  j · Longitud FE no disponible" : "i · 0 m                         j · " + Number(length) + " m";
        description.text = available
            ? "Interpolación lineal de fuerzas en extremos; no es una distribución interna calculada.\n" +
              "Ejes locales FE, independientes de la orientación AR.\n" +
              "Convención de sección: i = acción i; j = −acción j.\n" +
              "Acciones originales: i " + Number(i) + "; j " + Number(-j) + " " + unit + ".\nFuente: dataset AR CURRENT · CASE_R."
            : "No se sustituyen datos ausentes por ceros. Solo se muestran resultados CASE_R del dataset AR CURRENT.";
        overlay?.SelectDiagram(selected, segmentIndex, componentIndex);
        RefreshOverlayControls();
    }
    void RefreshOverlayControls()
    {
        if (overlayToggle == null) return;
        overlayActions.SetActive(IsOpen);
        bool available = overlay != null && overlay.CanShow(out _);
        overlayToggle.interactable = overlay != null && (overlay.Requested || available);
        overlayCaption.text = overlay != null && overlay.Requested ? "OCULTAR DEL ELEMENTO" : "MOSTRAR SOBRE ELEMENTO";
        if (overlay != null) { overlay.CanShow(out string reason); overlayNote.text = reason; }
    }
    static string Number(double value) => value.ToString("0.###", CultureInfo.InvariantCulture);

    void BuildUI()
    {
        font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        canvasObject = new GameObject("CurrentARDiagrams", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
        Canvas canvas = canvasObject.GetComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 30;
        CanvasScaler scaler = canvasObject.GetComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1080, 1920);
        scaler.matchWidthOrHeight = 0;
        safeArea = Rect("SafeArea", canvasObject.transform, Vector2.zero, Vector2.one);
        launcher = MakeButton("Ver diagramas", safeArea, new Vector2(.26f, .115f), new Vector2(.74f, .165f), Open);
        RectTransform panelRect = Rect("DiagramPanel", safeArea, new Vector2(.025f, .19f), new Vector2(.975f, .72f));
        panel = panelRect.gameObject;
        panel.AddComponent<Image>().color = new Color(.98f, .98f, .98f, 1);
        title = Label("Title", panelRect, new Vector2(.04f, .90f), new Vector2(.78f, .99f), 34);
        MakeButton("CERRAR", panelRect, new Vector2(.79f, .92f), new Vector2(.98f, .99f), Close);
        caseLabel = Label("CurrentCase", panelRect, new Vector2(.04f, .82f), new Vector2(.96f, .89f), 30);
        caseLabel.text = "Caso: R · CURRENT";
        for (int index = 0; index < 6; index++)
        {
            int captured = index;
            float x = .04f + index * .154f;
            components[index] = MakeButton(ARCurrentDiagramData.Components[index], panelRect,
                new Vector2(x, .73f), new Vector2(x + .145f, .81f), () => { componentIndex = captured; RefreshDiagram(); });
        }
        metadata = Label("Segment", panelRect, new Vector2(.21f, .58f), new Vector2(.79f, .72f), 29);
        previous = MakeButton("Anterior", panelRect, new Vector2(.02f, .62f), new Vector2(.20f, .70f), () => MoveSegment(-1));
        next = MakeButton("Siguiente", panelRect, new Vector2(.80f, .62f), new Vector2(.98f, .70f), () => MoveSegment(1));
        values = Label("EndValues", panelRect, new Vector2(.03f, .49f), new Vector2(.97f, .58f), 32);
        RectTransform plot = Rect("ForceGraph", panelRect, new Vector2(.04f, .23f), new Vector2(.96f, .48f));
        graph = plot.gameObject.AddComponent<ARForceDiagramGraphic>();
        graph.raycastTarget = false;
        axis = Label("LengthAxis", panelRect, new Vector2(.04f, .18f), new Vector2(.96f, .23f), 28);
        description = Label("Explanation", panelRect, new Vector2(.04f, .01f), new Vector2(.96f, .18f), 26);
        description.alignment = TextAnchor.MiddleLeft;
        RectTransform overlayRect = Rect("OverlayActions", safeArea, new Vector2(.025f, .095f), new Vector2(.975f, .17f));
        overlayActions = overlayRect.gameObject;
        overlayToggle = MakeButton("MOSTRAR SOBRE ELEMENTO", overlayRect, new Vector2(0, .42f), Vector2.one,
            () => { overlay?.Toggle(); RefreshOverlayControls(); });
        overlayCaption = overlayToggle.GetComponentInChildren<Text>();
        RectTransform noteRect = Rect("OverlayNoteBackground", overlayRect, Vector2.zero, new Vector2(1, .40f));
        noteRect.gameObject.AddComponent<Image>().color = new Color(.03f, .05f, .08f, .85f);
        overlayNote = Label("OverlayExplanation", noteRect, new Vector2(.01f, .02f), new Vector2(.99f, .98f), 23);
        overlayNote.color = Color.white;
        overlayActions.SetActive(false);
        panel.SetActive(false);
    }
    static RectTransform Rect(string name, Transform parent, Vector2 min, Vector2 max)
    {
        RectTransform rect = new GameObject(name, typeof(RectTransform)).GetComponent<RectTransform>();
        rect.SetParent(parent, false);
        rect.anchorMin = min; rect.anchorMax = max;
        rect.offsetMin = rect.offsetMax = Vector2.zero;
        return rect;
    }
    Text Label(string name, Transform parent, Vector2 min, Vector2 max, int size)
    {
        Text text = Rect(name, parent, min, max).gameObject.AddComponent<Text>();
        text.font = font; text.fontSize = size; text.color = new Color(.10f, .13f, .17f);
        text.alignment = TextAnchor.MiddleCenter;
        text.resizeTextForBestFit = true; text.resizeTextMinSize = 22; text.resizeTextMaxSize = size;
        text.raycastTarget = false; text.supportRichText = false;
        return text;
    }
    Button MakeButton(string label, Transform parent, Vector2 min, Vector2 max, UnityEngine.Events.UnityAction action)
    {
        RectTransform rect = Rect(label, parent, min, max);
        rect.gameObject.AddComponent<Image>().color = new Color(.28f, .31f, .36f);
        Button button = rect.gameObject.AddComponent<Button>();
        button.targetGraphic = rect.GetComponent<Image>();
        Text caption = Label("Caption", rect, new Vector2(.02f, .02f), new Vector2(.98f, .98f), 29);
        caption.text = label;
        caption.color = Color.white;
        button.onClick.AddListener(action);
        return button;
    }
}
