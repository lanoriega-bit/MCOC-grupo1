Shader "MCOC/ARForceOverlay"
{
    Properties { _Color ("Color", Color) = (1,1,1,1) }
    SubShader
    {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" }
        Cull Off
        ZWrite Off
        Blend SrcAlpha OneMinusSrcAlpha
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            fixed4 _Color;
            struct input { float4 vertex : POSITION; };
            struct output { float4 position : SV_POSITION; };
            output vert(input v) { output o; o.position = UnityObjectToClipPos(v.vertex); return o; }
            fixed4 frag(output v) : SV_Target { return _Color; }
            ENDCG
        }
    }
}
