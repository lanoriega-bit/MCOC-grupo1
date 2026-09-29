using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    public sealed class ARDatasetRepository : MonoBehaviour
    {
        [SerializeField] string datasetFileName = "p1l6_current_ar_elements.json";

        readonly Dictionary<string, StructuralElementARData> byTag = new Dictionary<string, StructuralElementARData>();
        public ARDatasetRoot Dataset { get; private set; }
        public bool IsCurrent { get; private set; }
        public string Error { get; private set; }
        public event Action DatasetLoaded;

        void Awake() => StartCoroutine(Load());

        public bool TryGet(string elementTag, out StructuralElementARData data)
        {
            return byTag.TryGetValue(elementTag ?? string.Empty, out data);
        }

        IEnumerator Load()
        {
            string path = Path.Combine(Application.streamingAssetsPath, datasetFileName);
            // Desktop prototype: Android packaging/transport will be supplied
            // by the final phone integration without changing this data contract.
            string json;
            if (!path.Contains("://") && !path.Contains(":///"))
            {
                if (!File.Exists(path))
                {
                    Fail("Dataset AR ausente: " + path);
                    yield break;
                }
                json = File.ReadAllText(path);
            }
            else
            {
                Fail("La ruta StreamingAssets requiere el adaptador móvil P1L6: " + path);
                yield break;
            }

            try
            {
                Dataset = JsonUtility.FromJson<ARDatasetRoot>(json);
                IsCurrent = Dataset != null &&
                    Dataset.status == "READY_PRECOMPUTED_PHONE_DOES_NOT_RUN_OPENSEES" &&
                    Dataset.elements != null && Dataset.elements.Length > 0;
                if (!IsCurrent)
                {
                    Fail("Dataset AR STALE/NO DATA: contrato CURRENT no verificado.");
                    yield break;
                }
                foreach (StructuralElementARData row in Dataset.elements)
                {
                    if (row == null || string.IsNullOrWhiteSpace(row.elementTag)) continue;
                    if (row.elementTag != row.element_id)
                        throw new InvalidDataException("Identidad inconsistente: " + row.elementTag + " != " + row.element_id);
                    if (byTag.ContainsKey(row.elementTag))
                        throw new InvalidDataException("elementTag duplicado: " + row.elementTag);
                    byTag.Add(row.elementTag, row);
                }
                DatasetLoaded?.Invoke();
            }
            catch (Exception exception)
            {
                Fail("Dataset AR inválido: " + exception.Message);
            }
        }

        void Fail(string message)
        {
            IsCurrent = false;
            Error = message;
            Debug.LogError("[P1L6 AR] " + message);
            DatasetLoaded?.Invoke();
        }
    }
}
