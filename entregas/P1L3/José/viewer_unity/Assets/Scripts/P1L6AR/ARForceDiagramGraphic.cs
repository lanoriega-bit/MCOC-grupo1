using UnityEngine;
using UnityEngine.UI;

namespace Mcoc.UnityViewer.P1L6AR
{
    // Shared visual palette only; indices follow the existing N/Vy/Vz/T/My/Mz order.
    public static class ARForceDiagramPalette
    {
        static readonly Color32[] colors = {
            new Color32(255, 45, 149, 255), new Color32(0, 229, 255, 255),
            new Color32(255, 212, 0, 255), new Color32(255, 122, 0, 255),
            new Color32(124, 255, 0, 255), new Color32(179, 136, 255, 255)
        };
        public static Color ForComponent(int component) => colors[component];
    }

    // A native UGUI graph: no textures, camera reads or 3D transforms.
    [RequireComponent(typeof(CanvasRenderer))]
    public sealed class ARForceDiagramGraphic : MaskableGraphic
    {
        double endI, endJ;
        bool available;
        public void SetComponent(int component)
        {
            color = ARForceDiagramPalette.ForComponent(component);
        }
        public void SetValues(bool valid, double i, double j)
        {
            available = valid; endI = i; endJ = j; SetVerticesDirty();
        }

        protected override void OnPopulateMesh(VertexHelper mesh)
        {
            mesh.Clear();
            Rect area = rectTransform.rect;
            float left = area.xMin + 24, right = area.xMax - 24, baseline = area.center.y;
            Line(mesh, new Vector2(left, baseline), new Vector2(right, baseline), 4, new Color(.20f, .23f, .28f));
            if (!available) return;
            double maximum = System.Math.Max(System.Math.Abs(endI), System.Math.Abs(endJ));
            double scale = maximum > 0 ? (area.height * .38) / maximum : 0;
            Vector2 i = new Vector2(left, baseline + (float)(endI * scale));
            Vector2 j = new Vector2(right, baseline + (float)(endJ * scale));
            // Dark backing keeps the bright yellow/lime readable on the light panel.
            Color outline = new Color(.08f, .10f, .14f);
            Line(mesh, new Vector2(left, baseline), i, 5, outline);
            Line(mesh, new Vector2(right, baseline), j, 5, outline);
            Line(mesh, i, j, 8, outline);
            Line(mesh, new Vector2(left, baseline), i, 3, color);
            Line(mesh, new Vector2(right, baseline), j, 3, color);
            Line(mesh, i, j, 6, color);
        }

        static void Line(VertexHelper mesh, Vector2 start, Vector2 end, float width, Color tint)
        {
            Vector2 normal = new Vector2(-(end - start).y, (end - start).x).normalized * width * .5f;
            if ((end - start).sqrMagnitude < .001f) return;
            int offset = mesh.currentVertCount;
            mesh.AddVert(start - normal, tint, Vector2.zero);
            mesh.AddVert(start + normal, tint, Vector2.zero);
            mesh.AddVert(end + normal, tint, Vector2.zero);
            mesh.AddVert(end - normal, tint, Vector2.zero);
            mesh.AddTriangle(offset, offset + 1, offset + 2);
            mesh.AddTriangle(offset, offset + 2, offset + 3);
        }
    }
}
