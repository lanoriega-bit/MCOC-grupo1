using UnityEngine;
using UnityEngine.Rendering;

namespace Mcoc.UnityViewer
{
    public partial class ViewerController
    {
        // Appearance only. Brick/steel are category keys, NOT engineering materials.
        static Material VisualSurface(string category, Color colour, float pattern, float metallic, float smoothness)
        {
            var shader=Resources.Load<Shader>("TechnicalSurface") ?? Shader.Find("Standard");
            var material=new Material(shader) { name="VISUAL_ONLY_"+category, color=colour };
            material.SetFloat("_Metallic",metallic); material.SetFloat("_Glossiness",smoothness);
            if(material.HasProperty("_Pattern"))material.SetFloat("_Pattern",pattern);
            if(material.HasProperty("_PatternStrength"))material.SetFloat("_PatternStrength",pattern==1?0.7f:0.35f);
            return material;
        }

        static Material VisualSlab()
        {
            var material=new Material(Shader.Find("Standard")) { name="VISUAL_ONLY_SLAB", color=new Color(1,1,1,0.18f) };
            material.SetFloat("_Mode",3); material.SetFloat("_Metallic",0); material.SetFloat("_Glossiness",0.15f);
            material.SetInt("_SrcBlend",(int)BlendMode.SrcAlpha);
            material.SetInt("_DstBlend",(int)BlendMode.OneMinusSrcAlpha);
            material.SetInt("_ZWrite",0);
            material.DisableKeyword("_ALPHATEST_ON"); material.EnableKeyword("_ALPHABLEND_ON");
            material.DisableKeyword("_ALPHAPREMULTIPLY_ON"); material.renderQueue=3000;
            return material;
        }

        void ConfigureVisualEnvironment()
        {
            if(cam!=null) { cam.clearFlags=CameraClearFlags.SolidColor; cam.backgroundColor=new Color(0.075f,0.10f,0.135f); }
            RenderSettings.ambientMode=AmbientMode.Trilight;
            RenderSettings.ambientSkyColor=new Color(0.68f,0.74f,0.81f);
            RenderSettings.ambientEquatorColor=new Color(0.40f,0.46f,0.53f);
            RenderSettings.ambientGroundColor=new Color(0.23f,0.27f,0.32f);
            foreach(var light in Object.FindObjectsByType<Light>(FindObjectsSortMode.None))
                if(light.type==LightType.Directional)
                { light.color=new Color(1f,0.96f,0.90f); light.intensity=1.05f; light.shadows=LightShadows.Soft; light.shadowStrength=0.35f; }
        }
    }
}
