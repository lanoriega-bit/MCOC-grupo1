using UnityEngine;

namespace Mcoc.UnityViewer.P1L6AR
{
    public sealed class ARDesktopSimulator : MonoBehaviour
    {
        [SerializeField] FakeAnchorProvider fakeAnchor;
        [SerializeField] ARStructuralElementController controller;
        [SerializeField] string[] candidates = { "E2-P1-C-002", "E2-P1-V-032", "E1-P1-C-023" };
        [SerializeField] float moveSpeed = 1.2f;
        [SerializeField] float rotationSpeed = 55f;
        [SerializeField] float scaleSpeed = 0.5f;

        int selectedIndex;

        void Awake()
        {
            if (fakeAnchor == null) fakeAnchor = FindAnyObjectByType<FakeAnchorProvider>();
            if (controller == null) controller = FindAnyObjectByType<ARStructuralElementController>();
        }

        void Update()
        {
            if (fakeAnchor == null || controller == null) return;
            if (Input.GetKeyDown(KeyCode.Alpha1)) Select(0);
            if (Input.GetKeyDown(KeyCode.Alpha2)) Select(1);
            if (Input.GetKeyDown(KeyCode.Alpha3)) Select(2);

            Transform anchor = fakeAnchor.AnchorTransform;
            Vector3 movement = new Vector3(Input.GetAxisRaw("Horizontal"), 0,
                Input.GetKey(KeyCode.PageUp) ? 1 : Input.GetKey(KeyCode.PageDown) ? -1 : 0);
            anchor.position += movement * (moveSpeed * Time.deltaTime);
            float yaw = (Input.GetKey(KeyCode.E) ? 1 : 0) - (Input.GetKey(KeyCode.Q) ? 1 : 0);
            anchor.Rotate(Vector3.up, yaw * rotationSpeed * Time.deltaTime, Space.World);
            float scaleDelta = (Input.GetKey(KeyCode.Equals) || Input.GetKey(KeyCode.KeypadPlus) ? 1 : 0) -
                               (Input.GetKey(KeyCode.Minus) || Input.GetKey(KeyCode.KeypadMinus) ? 1 : 0);
            if (scaleDelta != 0)
            {
                float next = Mathf.Clamp(anchor.localScale.x + scaleDelta * scaleSpeed * Time.deltaTime, 0.05f, 2f);
                anchor.localScale = Vector3.one * next;
            }
            if (Input.GetKeyDown(KeyCode.R)) fakeAnchor.SetPose(Vector3.zero, Quaternion.identity, Vector3.one);
        }

        void Select(int index)
        {
            if (candidates == null || index < 0 || index >= candidates.Length) return;
            selectedIndex = index;
            controller.ShowElement(candidates[index]);
        }

        void OnGUI()
        {
            GUI.color = Color.white;
            GUI.Box(new Rect(Screen.width - 365, 20, 345, 160), "SIMULADOR AR — PC");
            GUI.Label(new Rect(Screen.width - 345, 50, 310, 120),
                "1/2/3: candidato\nFlechas: mover X  |  PgUp/PgDn: mover Z\nQ/E: rotar anchor  |  +/-: escala\nR: reset\nActivo: " +
                (candidates != null && candidates.Length > selectedIndex ? candidates[selectedIndex] : "NO DATA"));
        }
    }
}
