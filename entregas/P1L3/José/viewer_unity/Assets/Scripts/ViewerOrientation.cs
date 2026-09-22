using UnityEngine;

namespace Mcoc.UnityViewer
{
    public partial class ViewerController
    {
        Vector3 localAxisOrigin, localAxisX, localAxisY, localAxisZ;

        void FitCurrentModel()
        {
            bool any=false; Bounds b=new Bounds();
            foreach(var e in allElements)
            {
                if(e==null||e.go==null||!e.go.activeSelf||e.isFeCandidateVisual)continue;
                if(e.category!="beam"&&e.category!="column"&&e.category!="wall")continue;
                var renderer=e.go.GetComponent<Renderer>();if(renderer==null)continue;
                if(!any){b=renderer.bounds;any=true;}else b.Encapsulate(renderer.bounds);
            }
            if(any){orbitTarget=b.center;orbitDist=Mathf.Max(30,b.size.magnitude*1.35f);}
            velYaw=velPitch=0;
        }

        void SetQuickView(string view)
        {
            FitCurrentModel();
            // Canonical +Z maps to Unity +Y, canonical +Y to Unity -Z.
            switch(view)
            {
                case "Planta":yaw=180;pitch=89;break;
                case "Frente":yaw=180;pitch=0;break;
                case "Lateral":yaw=90;pitch=0;break;
                default:yaw=30;pitch=25;break;
            }
            velYaw=velPitch=0;
        }

        void DrawQuickViews()
        {
            GUILayout.BeginHorizontal();
            foreach(string v in new[]{"Planta","Frente"})if(GUILayout.Button(v,currentButton))SetQuickView(v);
            GUILayout.EndHorizontal();GUILayout.BeginHorizontal();
            foreach(string v in new[]{"Lateral","Iso"})if(GUILayout.Button(v,currentButton))SetQuickView(v);
            GUILayout.EndHorizontal();
        }

        void DrawOrientationGizmo()
        {
            if(cam==null)return;Rect r=OrientationRect();PanelBackground(r);
            GUI.Label(new Rect(r.x+8,r.y+3,r.width-16,22),"GLOBAL X / Y / Z",currentHeading);
            Vector2 center=new Vector2(r.x+67,r.y+77);
            Vector3[] axes={Vector3.right,Vector3.up,Vector3.forward};
            Color[] colors={new Color(1,.3f,.3f),new Color(.25f,1,.45f),new Color(.25f,.6f,1)};
            string[] names={"X","Y","Z"};
            for(int i=0;i<3;i++)
            {
                Vector3 cameraAxis=cam.transform.InverseTransformDirection(transform.TransformDirection(axes[i]));
                Vector2 end=center+new Vector2(cameraAxis.x,-cameraAxis.y)*36;
                DrawGuiLine(center,end,colors[i],3);
                Color old=GUI.color;GUI.color=colors[i];
                if(GUI.Button(new Rect(end.x-10,end.y-10,23,22),names[i]))SetQuickView(i==0?"Lateral":i==1?"Frente":"Planta");
                GUI.color=old;
            }
            string[] views={"Planta","Frente","Lateral","Iso"};
            for(int i=0;i<4;i++)if(GUI.Button(new Rect(r.x+122,r.y+29+i*27,86,25),views[i]))SetQuickView(views[i]);
            GUI.Label(new Rect(r.x+8,r.y+121,112,22),"Z = vertical",currentBody);
        }

        void SetGlobalAxesVisible(bool show)
        {
            globalAxesVisible=show;
            if(globalAxisObjects.Count==0)
            {
                Vector3[] axes={Vector3.right,Vector3.up,Vector3.forward};Color[] colors={Color.red,Color.green,Color.blue};
                for(int i=0;i<3;i++)
                {
                    var go=new GameObject("GLOBAL_"+"XYZ"[i]);go.transform.SetParent(transform,false);
                    var line=go.AddComponent<LineRenderer>();line.useWorldSpace=false;line.positionCount=5;
                    Vector3 end=axes[i]*10, side=axes[(i+1)%3]*.6f;
                    line.SetPositions(new[]{Vector3.zero,end,end-axes[i]*1.2f+side,end,end-axes[i]*1.2f-side});
                    line.startWidth=.13f;line.endWidth=.13f;line.material=SeismicLineMat(colors[i]);globalAxisObjects.Add(go);
                }
            }
            foreach(var go in globalAxisObjects)go.SetActive(show);
        }

        void RebuildCurrentLocalAxes()
        {
            ClearSelectedLocalAxes();if(!localAxesVisible||lastSelected==null)return;
            var s=CurrentSolid(lastSelected);Vector3 a=lastSelected.nodeI,b=lastSelected.nodeJ;
            if(s!=null)
            {
                if(s.start!=null&&s.end!=null){a=V(s.start);b=V(s.end);}
                else{Vector3 center=V(s.center);float half=Mathf.Max(.1f,(float)s.height_m)*.5f;a=center-Vector3.forward*half;b=center+Vector3.forward*half;}
            }
            if((b-a).sqrMagnitude<.000001f)return;
            localAxisOrigin=(a+b)*.5f;localAxisX=(b-a).normalized;
            Vector3 reference=Mathf.Abs(Vector3.Dot(localAxisX,Vector3.forward))>.95f?Vector3.up:Vector3.forward;
            localAxisY=Vector3.Cross(reference,localAxisX).normalized;
            localAxisZ=Vector3.Cross(localAxisX,localAxisY).normalized;
            CreateSelectedAxis(localAxisOrigin,localAxisX,Color.red,"x",lastSelected.floor);
            CreateSelectedAxis(localAxisOrigin,localAxisY,Color.green,"y",lastSelected.floor);
            CreateSelectedAxis(localAxisOrigin,localAxisZ,Color.blue,"z",lastSelected.floor);
            typeVisible["selected_local_axes"]=true;ReapplyAll();
        }

        void DrawAxisLabel(Vector3 canonical,string label,Color color)
        {
            if(cam==null)return;Vector3 p=cam.WorldToScreenPoint(transform.TransformPoint(canonical));if(p.z<=0)return;
            Color old=GUI.color;GUI.color=color;GUI.Label(new Rect(p.x+6,Screen.height-p.y-14,145,24),label,currentHeading);GUI.color=old;
        }

        void DrawCurrentAxisLabels()
        {
            if(globalAxesVisible){DrawAxisLabel(Vector3.right*10,"GLOBAL +X",Color.red);DrawAxisLabel(Vector3.up*10,"GLOBAL +Y",Color.green);DrawAxisLabel(Vector3.forward*10,"GLOBAL +Z",new Color(.3f,.65f,1));}
            if(localAxesVisible&&lastSelected!=null&&lastSelected.go.activeSelf)
            {DrawAxisLabel(localAxisOrigin+localAxisX*2,"x local",Color.red);DrawAxisLabel(localAxisOrigin+localAxisY*2,"y local",Color.green);DrawAxisLabel(localAxisOrigin+localAxisZ*2,"z local",new Color(.3f,.65f,1));}
        }
    }
}
