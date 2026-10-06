using System;
using System.Collections;
using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    public sealed class ARPrototypeSelfCheck : MonoBehaviour
    {
        IEnumerator Start()
        {
            ARDatasetRepository repository = FindAnyObjectByType<ARDatasetRepository>();
            ARStructuralElementController controller = FindAnyObjectByType<ARStructuralElementController>();
            StructuralARElementRenderer renderer = FindAnyObjectByType<StructuralARElementRenderer>();
            FakeAnchorProvider anchor = FindAnyObjectByType<FakeAnchorProvider>();
            float deadline = Time.realtimeSinceStartup + 12f;
            while (repository != null && !repository.IsCurrent && string.IsNullOrEmpty(repository.Error) && Time.realtimeSinceStartup < deadline)
                yield return null;

            string failure = null;
            if (repository == null || controller == null || renderer == null || anchor == null) failure = "componentes ausentes";
            else if (!repository.IsCurrent) failure = repository.Error ?? "dataset no CURRENT";
            else if (!controller.ShowElement("E2-P1-C-002")) failure = "no se pudo mostrar candidato principal";
            else if (controller.SelectedElement.elementTag != "E2-P1-C-002" ||
                     controller.SelectedElement.element_id != "E2-P1-C-002" ||
                     renderer.RenderedElementTag != "E2-P1-C-002") failure = "identidad elementTag rota";
            else if (controller.SelectedElement.opensees_tags == null || controller.SelectedElement.opensees_tags.Length == 0)
                failure = "crosswalk OpenSees ausente";
            else if (!ARResultSummary.TryCreate(controller.SelectedElement, out _)) failure = "resultados CURRENT ausentes";
            else
            {
                Vector3 before = renderer.RenderedTransform.position;
                anchor.SetPose(new Vector3(0.4f, 0.2f, 0.1f), Quaternion.Euler(0, 25, 0), Vector3.one * 0.35f);
                yield return null;
                if ((renderer.RenderedTransform.position - before).sqrMagnitude < 0.01f) failure = "el elemento no siguió al anchor";
                else if (controller.ShowElement("ELEMENTO_INEXISTENTE") || controller.State != "STALE / NO DATA")
                    failure = "fail-closed no bloqueó identidad inexistente";
                else if (!controller.ShowElement("E2-P1-V-032")) failure = "candidato de respaldo no disponible";
            }

            if (failure == null)
                Debug.Log("[P1L6 AR QA] PASS: identidad; CURRENT; crosswalk; P/M/V/desplazamiento; D/C; FakeAnchor; fail-closed; columna y viga.");
            else
                Debug.LogError("[P1L6 AR QA] FAIL: " + failure);

#if UNITY_EDITOR
            if (Array.IndexOf(Environment.GetCommandLineArgs(), "--quit-after-ar-smoke") >= 0)
                UnityEditor.EditorApplication.Exit(failure == null ? 0 : 1);
#endif
        }
    }
}
