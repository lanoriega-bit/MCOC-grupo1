Shader "MCOC/TechnicalSurface"
{
    Properties
    {
        _Color ("Presentation colour", Color) = (0.6,0.6,0.6,1)
        _EmissionColor ("Selection emission", Color) = (0,0,0,1)
        _Metallic ("Metallic", Range(0,1)) = 0
        _Glossiness ("Smoothness", Range(0,1)) = 0.3
        _Pattern ("0 plain, 1 brick, 2 concrete", Float) = 0
        _PatternStrength ("Presentation pattern strength", Range(0,1)) = 0.5
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 200
        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows
        #pragma target 3.0
        struct Input { float3 worldPos; float3 worldNormal; };
        fixed4 _Color, _EmissionColor;
        half _Metallic, _Glossiness, _Pattern, _PatternStrength;
        float noise(float3 p) { return frac(sin(dot(p,float3(12.9898,78.233,37.719)))*43758.5453); }
        void surf(Input IN, inout SurfaceOutputStandard o)
        {
            float3 n=abs(IN.worldNormal);
            float2 uv=n.x>n.z ? IN.worldPos.zy : IN.worldPos.xy;
            if(n.y>max(n.x,n.z)) uv=IN.worldPos.xz;
            float detail=1;
            if(_Pattern>0.5 && _Pattern<1.5)
            {
                // World metre spacing is a visual key, not a structural property.
                float row=floor(uv.y/0.075);
                float2 brick=frac(float2(uv.x/0.24+fmod(row,2)*0.5,uv.y/0.075));
                float2 edge=min(brick,1-brick);
                float2 aa=max(fwidth(brick),float2(0.005,0.005));
                float mortar=1-min(smoothstep(0.014,0.014+aa.x,edge.x),smoothstep(0.045,0.045+aa.y,edge.y));
                detail=lerp(1.0,0.64,mortar);
            }
            else if(_Pattern>1.5)
                detail=0.94+0.12*noise(floor(IN.worldPos*45));
            o.Albedo=_Color.rgb*lerp(1,detail,_PatternStrength);
            o.Metallic=_Metallic; o.Smoothness=_Glossiness;
            o.Emission=_EmissionColor.rgb; o.Alpha=1;
        }
        ENDCG
    }
    FallBack "Standard"
}
