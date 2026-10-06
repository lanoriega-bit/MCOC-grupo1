using UnityEngine;
using UnityEngine.EventSystems;

namespace Mcoc.UnityViewer.P1L6AR
{
    // UGUI InputField still queries legacy IME properties through BaseInput.
    // Element IDs are ASCII; Android's native keyboard supplies the text.
    // This bridge keeps those queries safe with Input System-only projects.
    public sealed class ARSelectionTextInput : BaseInput
    {
        public override string compositionString => string.Empty;
        public override IMECompositionMode imeCompositionMode { get; set; }
        public override Vector2 compositionCursorPos { get; set; }
    }
}
