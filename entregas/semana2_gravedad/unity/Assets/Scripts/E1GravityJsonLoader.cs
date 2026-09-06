using System.IO;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Mcoc.Semana2.UnityE1
{
    public static class E1GravityJsonLoader
    {
        public const string DefaultFileName = "edificio1_unity.json";
        public const string DefaultResponseFileName = "edificio1_unity_response.json";
        public const string DefaultMappingFileName = "e1_structural_mapping_coverage.json";
        public const string IntegratedFileName = "edificios12_unity.json";
        public const string IntegratedResponseFileName = "edificios12_unity_response.json";
        private const string ResultsDirectoryName = "results";

        private static bool IsIntegratedScene()
        {
            return SceneManager.GetActiveScene().name.IndexOf("E12", System.StringComparison.OrdinalIgnoreCase) >= 0;
        }

        public static string ActiveGravityFileName()
        {
            return IsIntegratedScene() ? IntegratedFileName : DefaultFileName;
        }

        public static string ActiveResponseFileName()
        {
            return IsIntegratedScene() ? IntegratedResponseFileName : DefaultResponseFileName;
        }

        private static void LogLoadTarget(string what, string path)
        {
            Debug.Log("[E1GravityJsonLoader] Escena=" + SceneManager.GetActiveScene().name
                + " | Cargando " + what + "=" + Path.GetFileName(path)
                + " | Ruta absoluta=" + path);
        }

        public static string DefaultExternalPath()
        {
            return Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "results", ActiveGravityFileName()));
        }

        public static E1GravityData Load(string overridePath = null)
        {
            string path = string.IsNullOrWhiteSpace(overridePath) ? DefaultExternalPath() : overridePath;
            LogLoadTarget("edificio", path);
            if (!File.Exists(path))
            {
                string streamingAssetsPath = Path.Combine(Application.streamingAssetsPath, ActiveGravityFileName());
                if (File.Exists(streamingAssetsPath)) path = streamingAssetsPath;
            }

            if (!File.Exists(path))
            {
                Debug.LogError("[E1GravityJsonLoader] No existe " + ActiveGravityFileName() + ". Ruta esperada: " + path);
                return null;
            }

            try
            {
                string json = File.ReadAllText(path);
                E1GravityData data = JsonConvert.DeserializeObject<E1GravityData>(json);
                Debug.Log("[E1GravityJsonLoader] JSON cargado: " + path);
                return data;
            }
            catch (System.Exception ex)
            {
                Debug.LogError("[E1GravityJsonLoader] Error al parsear JSON (" + ActiveGravityFileName() + "): " + ex.Message);
                return null;
            }
        }

        public static string DefaultResponsePath()
        {
            return Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ResultsDirectoryName, ActiveResponseFileName()));
        }

        public static E1StructuralResponse LoadResponse(string overridePath = null)
        {
            string path = string.IsNullOrWhiteSpace(overridePath) ? DefaultResponsePath() : overridePath;
            LogLoadTarget("response", path);
            if (!File.Exists(path))
            {
                string streamingAssetsPath = Path.Combine(Application.streamingAssetsPath, ActiveResponseFileName());
                if (File.Exists(streamingAssetsPath)) path = streamingAssetsPath;
            }

            if (!File.Exists(path))
            {
                Debug.LogError("[E1GravityJsonLoader] No existe " + ActiveResponseFileName() + ". Ruta esperada: " + path);
                return null;
            }

            try
            {
                string json = File.ReadAllText(path);
                E1StructuralResponse response = JsonConvert.DeserializeObject<E1StructuralResponse>(json);
                Debug.Log("[E1GravityJsonLoader] Response JSON cargado: " + path);
                return response;
            }
            catch (System.Exception ex)
            {
                Debug.LogError("[E1GravityJsonLoader] Error al parsear response JSON (" + ActiveResponseFileName() + "): " + ex.Message);
                return null;
            }
        }

        public static string DefaultMappingPath()
        {
            return Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ResultsDirectoryName, DefaultMappingFileName));
        }

        public static string E2MappingPath()
        {
            return Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ResultsDirectoryName, "e2_structural_mapping_coverage.json"));
        }

        public static E1StructuralMappingCoverage LoadMapping(string overridePath = null)
        {
            string path = string.IsNullOrWhiteSpace(overridePath) ? DefaultMappingPath() : overridePath;
            if (!File.Exists(path))
            {
                string streamingAssetsPath = Path.Combine(Application.streamingAssetsPath, DefaultMappingFileName);
                if (File.Exists(streamingAssetsPath)) path = streamingAssetsPath;
            }

            if (!File.Exists(path))
            {
                Debug.LogWarning("[E1GravityJsonLoader] No existe " + DefaultMappingFileName + ". Se usara matching geometrico conservador.");
                return null;
            }

            try
            {
                string json = File.ReadAllText(path);
                E1StructuralMappingCoverage mapping = JsonConvert.DeserializeObject<E1StructuralMappingCoverage>(json);
                Debug.Log("[E1GravityJsonLoader] Mapping JSON cargado: " + path);
                return mapping;
            }
            catch (System.Exception ex)
            {
                Debug.LogError("[E1GravityJsonLoader] Error al parsear mapping JSON: " + ex.Message);
                return null;
            }
        }
    }
}
