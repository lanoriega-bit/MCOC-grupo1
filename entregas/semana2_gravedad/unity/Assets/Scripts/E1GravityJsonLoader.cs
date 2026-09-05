using System.IO;
using Newtonsoft.Json;
using UnityEngine;

namespace Mcoc.Semana2.UnityE1
{
    public static class E1GravityJsonLoader
    {
        public const string DefaultFileName = "edificio1_unity.json";
        public const string DefaultResponseFileName = "edificio1_unity_response.json";
        public const string DefaultMappingFileName = "e1_structural_mapping_coverage.json";
        private const string ResultsDirectoryName = "results";

        public static string DefaultExternalPath()
        {
            return Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "results", DefaultFileName));
        }

        public static E1GravityData Load(string overridePath = null)
        {
            string path = string.IsNullOrWhiteSpace(overridePath) ? DefaultExternalPath() : overridePath;
            if (!File.Exists(path))
            {
                string streamingAssetsPath = Path.Combine(Application.streamingAssetsPath, DefaultFileName);
                if (File.Exists(streamingAssetsPath)) path = streamingAssetsPath;
            }

            if (!File.Exists(path))
            {
                Debug.LogError("[E1GravityJsonLoader] No existe edificio1_unity.json. Ruta esperada: " + path);
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
                Debug.LogError("[E1GravityJsonLoader] Error al parsear JSON: " + ex.Message);
                return null;
            }
        }

        public static string DefaultResponsePath()
        {
            return Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ResultsDirectoryName, DefaultResponseFileName));
        }

        public static E1StructuralResponse LoadResponse(string overridePath = null)
        {
            string path = string.IsNullOrWhiteSpace(overridePath) ? DefaultResponsePath() : overridePath;
            if (!File.Exists(path))
            {
                string streamingAssetsPath = Path.Combine(Application.streamingAssetsPath, DefaultResponseFileName);
                if (File.Exists(streamingAssetsPath)) path = streamingAssetsPath;
            }

            if (!File.Exists(path))
            {
                Debug.LogError("[E1GravityJsonLoader] No existe " + DefaultResponseFileName + ". Ruta esperada: " + path);
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
                Debug.LogError("[E1GravityJsonLoader] Error al parsear response JSON: " + ex.Message);
                return null;
            }
        }

        public static string DefaultMappingPath()
        {
            return Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ResultsDirectoryName, DefaultMappingFileName));
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
