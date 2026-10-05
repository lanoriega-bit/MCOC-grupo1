using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    /// <summary>
    /// Transformación modelo -> Unity -> AR para elementos seleccionados.
    ///
    /// El ARAnchor funciona como padre del elemento renderizado.
    /// Por eso aquí trabajamos en coordenadas locales respecto al anchor
    /// y no volvemos a aplicar su pose global.
    ///
    /// Para la visualización individual de un elemento:
    /// - el centro del propio elemento se usa como origen;
    /// - se conserva su orientación;
    /// - se aplica la escala de visualización;
    /// - queda centrado respecto al anchor AR.
    /// </summary>
    public sealed class TrackedModelToARTransformBehaviour
        : MonoBehaviour, IModelToARTransform
    {
        [SerializeField]
        LuisAnchorProviderAdapter anchorProvider;

        // Se mantiene por compatibilidad con el sistema general,
        // aunque para la visualización individual usamos
        // elementUnityOrigin como origen dinámico.
        [SerializeField]
        Vector3 modelOriginUnityMetres =
            new Vector3(7.502f, 3.96f, -0.001f);

        [SerializeField]
        Vector3 calibrationEulerDegrees =
            Vector3.zero;

        [SerializeField]
        Vector3 calibrationOffsetMetres =
            Vector3.zero;

        [SerializeField, Min(0.0001f)]
        float calibrationScale = 1f;

        ModelToARTransformAdapter adapter;

        public Vector3 ModelOriginUnityMetres =>
            modelOriginUnityMetres;

        public bool HasTrackedAnchor =>
            anchorProvider != null &&
            anchorProvider.TryGetAnchor(
                out AnchorPoseData _
            );

        void Awake()
        {
            if (anchorProvider == null)
            {
                anchorProvider =
                    FindAnyObjectByType<
                        LuisAnchorProviderAdapter
                    >();
            }

            RebuildAdapter();
        }

        void OnValidate()
        {
            calibrationScale =
                Mathf.Max(
                    0.0001f,
                    calibrationScale
                );

            RebuildAdapter();
        }

        public Vector3 ToAnchorLocalPoint(
            Vector3 datasetUnityPoint,
            Vector3 elementUnityOrigin,
            float scale)
        {
            EnsureAdapter();

            // IMPORTANTE:
            // usamos el centro del propio elemento
            // como origen local.
            //
            // El renderer actualmente llama:
            //
            // ToAnchorLocalPoint(
            //     centre,
            //     centre,
            //     scale
            // )
            //
            // Por lo tanto:
            // centre - centre = 0
            //
            // y el elemento queda centrado
            // directamente respecto al anchor AR.
            return adapter.ToAnchorLocalPoint(
                datasetUnityPoint,
                elementUnityOrigin,
                scale
            );
        }

        public Quaternion ToAnchorLocalRotation(
            Vector3 datasetUnityDirection)
        {
            EnsureAdapter();

            // Conserva la orientación estructural
            // entregada por el dataset.
            return adapter.ToAnchorLocalRotation(
                datasetUnityDirection
            );
        }

        public Vector3 ToAnchorLocalScale(
            Vector3 sizeMetres,
            float scale)
        {
            EnsureAdapter();

            // Mantiene las proporciones reales
            // del elemento y aplica la escala AR.
            return adapter.ToAnchorLocalScale(
                sizeMetres,
                scale
            );
        }

        void EnsureAdapter()
        {
            if (adapter == null)
            {
                RebuildAdapter();
            }
        }

        void RebuildAdapter()
        {
            adapter =
                new ModelToARTransformAdapter(
                    calibrationOffsetMetres,
                    Quaternion.Euler(
                        calibrationEulerDegrees
                    ),
                    calibrationScale
                );
        }
    }
}