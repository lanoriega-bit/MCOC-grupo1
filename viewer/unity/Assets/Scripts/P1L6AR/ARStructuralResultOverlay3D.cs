using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    [DisallowMultipleComponent]
    public sealed class ARStructuralResultOverlay3D : MonoBehaviour
    {
        ARStructuralElementController controller;
        StructuralElementARData selected;
        int component=4, segment;
        bool subscribed;
        public bool Requested { get; private set; }
        public ARForceDiagram3DRenderer Current { get; private set; }

        void Awake() { controller=GetComponent<ARStructuralElementController>(); }
        void OnEnable()
        {
            if(controller!=null && !subscribed) {controller.ElementShown+=OnElementShown;subscribed=true;}
        }
        void OnDisable()
        {
            if(controller!=null && subscribed)controller.ElementShown-=OnElementShown;
            subscribed=false;Remove();
        }
        void OnElementShown(StructuralElementARData row,string state,AnchorPoseData pose)
        {
            if(selected!=row) {selected=row;segment=0;}
            Apply();
        }
        public void SelectDiagram(StructuralElementARData row,int segmentIndex,int componentIndex)
        {
            bool changed=selected!=row || segment!=segmentIndex || component!=componentIndex;
            selected=row;segment=segmentIndex;component=componentIndex;
            if(changed || Current==null)Apply();
        }
        public bool CanShow(out string reason)
        {
            reason="Tipo sin representación lineal 3D; disponible en 2D";
            if(selected?.type!="beam" && selected?.type!="column" && selected?.type!="wall")return false;
            var placement=controller?.SurfacePlacement;
            reason="Fija el elemento para mostrar el overlay";
            if(placement==null || !placement.HasTrackedPlacement || placement.PlacedRoot==null ||
                placement.PlacedRoot.GetComponent<ARPlacementPreview>()?.ElementId!=selected.element_id)return false;
            reason="Resultados CURRENT o correspondencia longitudinal FE no disponibles para este segmento";
            if(controller.Repository?.IsCurrent!=true || controller.Repository.Dataset?.format!="MCOC_P1L6_AR_CURRENT_ELEMENTS_V1" ||
                !ARCurrentDiagramData.TryValues(selected,segment,component,out _,out _))return false;
            if(selected.type!="beam")
            {
                if(!ARVerticalResultMapping.TryRange(selected,segment,out _,out _,out reason))return false;
            }
            else if(!ARForceDiagram3DRenderer.TrySegmentRange(selected,segment,out _,out _))return false;
            reason="Visualización interpolada entre resultados de extremos FE · escala gráfica automática";
            if(selected.type=="column")reason="Resultado a lo largo del eje de la columna · "+reason;
            if(selected.type=="wall")reason="Resultado lineal del segmento FE equivalente · "+reason;
            return true;
        }
        public void Toggle()
        {
            if(Requested) {Requested=false;Remove();return;}
            if(!CanShow(out _))return;
            Requested=true;Apply();
        }
        void Apply()
        {
            if(!Requested)return;
            var placement=controller?.SurfacePlacement;
            // During selection/relocation preview the previous root and its overlay
            // remain untouched. Only a confirmed replacement transfers the overlay.
            if(placement==null || placement.State!=ARPlacementState.Placed)return;
            if(!placement.HasTrackedPlacement)return;
            if(!CanShow(out _)) {Requested=false;Remove();return;}
            Transform root=placement.PlacedRoot;
            if(Current!=null && Current.transform.parent!=root)Remove();
            if(Current==null)
            {
                var overlay=new GameObject("ResultOverlay3D");overlay.transform.SetParent(root,false);
                Current=overlay.AddComponent<ARForceDiagram3DRenderer>();
            }
            if(!Current.Render(selected,root.GetComponent<ARPlacementPreview>().StructuralMesh,segment,component))Remove();
        }
        void Remove()
        {
            if(Current!=null) {Current.gameObject.SetActive(false);Destroy(Current.gameObject);}
            Current=null;
        }
    }
}
