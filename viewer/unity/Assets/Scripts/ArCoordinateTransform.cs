using UnityEngine;

namespace Mcoc.UnityViewer
{
    /// <summary>
    /// Pure coordinate bridge prepared for P1L6. It has no AR Foundation
    /// dependency: the future phone client supplies the tracked anchor matrix.
    /// Structural calculation remains precomputed outside the phone.
    /// </summary>
    public static class ArCoordinateTransform
    {
        // OpenSees/model: Z up. Unity viewer: Y up after Rx(-90 degrees).
        public static Vector3 ModelToUnity(Vector3 model)
        {
            return new Vector3(model.x, model.z, -model.y);
        }

        public static Vector3 UnityToModel(Vector3 unity)
        {
            return new Vector3(unity.x, -unity.z, unity.y);
        }

        // anchorFromUnity comes from image tracking / anchor registration.
        public static Vector3 ModelToAr(Vector3 model, Matrix4x4 anchorFromUnity, float metresScale = 1f)
        {
            return anchorFromUnity.MultiplyPoint3x4(ModelToUnity(model) * metresScale);
        }

        public static Quaternion ModelDirectionToAr(Vector3 modelDirection, Matrix4x4 anchorFromUnity)
        {
            Vector3 unityDirection = ModelToUnity(modelDirection).normalized;
            Vector3 arDirection = anchorFromUnity.MultiplyVector(unityDirection).normalized;
            return arDirection.sqrMagnitude > 1e-8f
                ? Quaternion.LookRotation(arDirection, anchorFromUnity.MultiplyVector(Vector3.up))
                : Quaternion.identity;
        }
    }
}
