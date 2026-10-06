using System.Globalization;
using System.Text;
using UnityEngine;
using UnityEngine.UI;

namespace Mcoc.UnityViewer.P1L6AR
{
    public sealed class ARResultPanel : MonoBehaviour
    {
        [SerializeField] ARStructuralElementController controller;
        Text title;
        Text body;
        Text status;

        void Awake()
        {
            if (controller == null) controller = FindAnyObjectByType<ARStructuralElementController>();
            BuildUI();
            ShowNoData("CARGANDO CURRENT...");
        }

        void OnEnable()
        {
            if (controller != null) controller.ElementShown += OnElementShown;
        }

        void OnDisable()
        {
            if (controller != null) controller.ElementShown -= OnElementShown;
        }

        void OnElementShown(StructuralElementARData data, string state, AnchorPoseData anchor)
        {
            ARResultSummary result = default;
            bool current = state == "CURRENT" && ARResultSummary.TryCreate(data, out result);
            title.text = data.elementTag;
            status.text = current ? "CURRENT" : "STALE / NO DATA";
            status.color = current ? new Color(0.25f, 1f, 0.48f) : new Color(1f, 0.35f, 0.25f);
            if (!current)
            {
                ShowNoData(state);
                return;
            }

            NumberFormatInfo format = CultureInfo.InvariantCulture.NumberFormat;
            StringBuilder text = new StringBuilder();
            text.AppendLine(data.type.ToUpperInvariant() + "  |  " + data.building + " / " + data.floor);
            text.AppendLine("Sección  " + SectionText(data));
            text.AppendLine("Material " + (data.material?.name ?? "NO DATA"));
            text.AppendLine("Caso     R = 1.0G + 0.5Q");
            text.AppendLine();
            text.AppendLine("|P|max   " + result.PkN.ToString("N1", format) + " kN");
            text.AppendLine("|M|max   " + result.MkNm.ToString("N1", format) + " kN·m");
            text.AppendLine("|V|max   " + result.VkN.ToString("N1", format) + " kN");
            text.AppendLine("Despl.   " + result.DisplacementMm.ToString("N2", format) + " mm");
            text.AppendLine(result.HasDemandCapacity
                ? "D/C      " + result.DemandCapacity.ToString("N2", format) + (result.DemandCapacity <= 1 ? "  OK" : "  REVISAR")
                : "D/C      NO DATA");
            text.AppendLine();
            text.AppendLine("solidTag " + data.solidTag);
            text.AppendLine("OpenSees " + OpenSeesTags(data));
            text.AppendLine("Anchor   " + anchor.trackingState + " / " + anchor.referenceImageName);
            text.AppendLine("Capacidad APPROX / ASSUMED_FOR_LAB");
            body.text = text.ToString();
        }

        void ShowNoData(string message)
        {
            if (title != null && string.IsNullOrEmpty(title.text)) title.text = "P1L6 AR";
            if (status != null) status.text = "STALE / NO DATA";
            if (body != null) body.text = message + "\nNo se muestran resultados históricos.";
        }

        void BuildUI()
        {
            Canvas canvas = GetComponent<Canvas>();
            if (canvas == null) canvas = gameObject.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            gameObject.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            gameObject.AddComponent<GraphicRaycaster>();

            GameObject panel = new GameObject("ARResultCard", typeof(RectTransform), typeof(Image));
            panel.transform.SetParent(transform, false);
            RectTransform rect = (RectTransform)panel.transform;
            rect.anchorMin = new Vector2(0, 1);
            rect.anchorMax = new Vector2(0, 1);
            rect.pivot = new Vector2(0, 1);
            rect.anchoredPosition = new Vector2(24, -24);
            rect.sizeDelta = new Vector2(430, 540);
            panel.GetComponent<Image>().color = new Color(0.025f, 0.045f, 0.075f, 0.92f);

            title = AddText(panel.transform, "ElementTag", 28, FontStyle.Bold, new Vector2(20, -18), new Vector2(390, 45));
            status = AddText(panel.transform, "State", 19, FontStyle.Bold, new Vector2(20, -65), new Vector2(390, 34));
            body = AddText(panel.transform, "Results", 18, FontStyle.Normal, new Vector2(20, -108), new Vector2(390, 410));
        }

        static Text AddText(Transform parent, string name, int size, FontStyle style, Vector2 position, Vector2 dimensions)
        {
            GameObject row = new GameObject(name, typeof(RectTransform), typeof(Text));
            row.transform.SetParent(parent, false);
            RectTransform rect = (RectTransform)row.transform;
            rect.anchorMin = new Vector2(0, 1);
            rect.anchorMax = new Vector2(0, 1);
            rect.pivot = new Vector2(0, 1);
            rect.anchoredPosition = position;
            rect.sizeDelta = dimensions;
            Text text = row.GetComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = size;
            text.fontStyle = style;
            text.color = Color.white;
            text.alignment = TextAnchor.UpperLeft;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Overflow;
            return text;
        }

        static string OpenSeesTags(StructuralElementARData data)
        {
            if (data.opensees_tags == null || data.opensees_tags.Length == 0) return "NO DATA";
            return string.Join(", ", data.opensees_tags);
        }

        static string SectionText(StructuralElementARData data)
        {
            ARSectionDimensions d = data.section?.dimensions;
            if (d == null) return data.section?.section_id ?? "NO DATA";
            double a = d.width_m > 0 ? d.width_m : d.thickness_m;
            double b = d.depth_m > 0 ? d.depth_m : d.height_m > 0 ? d.height_m : d.length_m;
            return a > 0 && b > 0
                ? (a * 100).ToString("0") + " × " + (b * 100).ToString("0") + " cm"
                : data.section.section_id;
        }
    }
}
