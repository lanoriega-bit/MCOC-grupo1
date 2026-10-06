using UnityEngine;

namespace Mcoc.UnityViewer
{
    public partial class ViewerController
    {
        string visualClickHelp;
        float visualClickHelpUntil;

        void StyleVisualControl(GUIStyle style)
        {
            style.normal.background=MakeTex(2,2,new Color(0.12f,0.17f,0.22f));
            style.hover.background=MakeTex(2,2,new Color(0.18f,0.26f,0.33f));
            style.active.background=MakeTex(2,2,new Color(0.10f,0.34f,0.40f));
            style.onNormal.background=MakeTex(2,2,new Color(0.10f,0.28f,0.34f));
            style.onHover.background=style.active.background;
            style.normal.textColor=new Color(0.86f,0.91f,0.95f);
            style.hover.textColor=Color.white; style.active.textColor=Color.white;
            style.onNormal.textColor=new Color(0.45f,0.93f,1f); style.onHover.textColor=Color.white;
            style.border=new RectOffset(0,0,0,0);
            style.margin=new RectOffset(2,2,3,3);
        }

        bool VisualToggle(bool value,string label,string help)
            => GUILayout.Toggle(value,new GUIContent((value?"●  ":"○  ")+label,help),currentChip,GUILayout.Height(27));

        static string HelpForControl(string title)
        {
            if(title.Contains("Losas"))return "Referencia visual blanca/semitransparente. Cobertura incompleta pendiente de revisión; no cambia el área tributaria ni el FE.";
            if(title.Contains("Columnas"))return "Ladrillo = clave visual de columnas. El material estructural real sigue en la ficha.";
            if(title.Contains("Vigas"))return "Gris azulado = clave visual de vigas; no indica que el elemento sea de acero.";
            if(title.Contains("Muros"))return "Hormigón gris = clave visual de muros. Sección y material permanecen en el contrato CURRENT.";
            if(title.Contains("Nodos"))return "Nodos del modelo. Mostrar/ocultar no modifica la conectividad.";
            return "Mostrar/ocultar "+title.ToLowerInvariant()+". Control de presentación, sin modificar el análisis.";
        }

        void ShowCaseHelp(string name)
        { visualClickHelp=LoadCaseExplanation(name); visualClickHelpUntil=Time.realtimeSinceStartup+4f; }

        void DrawVisualTooltip()
        {
            string message=GUI.tooltip;
            bool hover=!string.IsNullOrEmpty(message);
            if(!hover&&Time.realtimeSinceStartup<visualClickHelpUntil)message=visualClickHelp;
            if(string.IsNullOrEmpty(message))return;
            float width=Mathf.Min(380,Screen.width-32);
            float height=currentBody.CalcHeight(new GUIContent(message),width-20)+20;
            Vector2 pointer=Event.current.mousePosition;
            float x=hover?pointer.x+18:SemanticPanelRect().xMax+14;
            float y=hover?pointer.y+20:92;
            Rect rect=new Rect(Mathf.Clamp(x,12,Screen.width-width-12),Mathf.Clamp(y,80,Screen.height-height-42),width,height);
            GUI.depth=-100; PanelBackground(rect);
            GUI.Label(new Rect(rect.x+10,rect.y+10,width-20,height-20),message,currentBody);
        }
    }
}
