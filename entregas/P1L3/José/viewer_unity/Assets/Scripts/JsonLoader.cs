using System.IO;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    /// <summary>
    /// Carga el contract JSON "model_viewer.json" (formato P1L2) desde StreamingAssets.
    /// Los datos estructurales viven en JSON independiente de la escena (ver enunciado).
    /// </summary>
    public static class JsonLoader
    {
        public static ModelData LoadModel(string fileName = "model_viewer.json")
        {
            string path = Path.Combine(Application.streamingAssetsPath, fileName);
            if (!File.Exists(path))
            {
                Debug.LogError($"[JsonLoader] No existe el archivo: {path}");
                return null;
            }
            string json = File.ReadAllText(path);
            try
            {
                ModelData data = JsonUtility.FromJson<ModelData>(json);
                data.colors = JsonUtility.FromJson<ModelColors>(ExtractObject(json, "colors"));
                Debug.Log($"[JsonLoader] Modelo cargado: {data.model}. Solidos: {data.solids?.Count}");
                return data;
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"[JsonLoader] Error al parsear: {ex.Message}");
                return null;
            }
        }

        private static string ExtractObject(string json, string field)
        {
            string key = "\"" + field + "\":";
            int start = json.IndexOf(key);
            if (start < 0) return "{}";
            start += key.Length;
            int depth = 0;
            bool inString = false;
            for (int i = start; i < json.Length; i++)
            {
                char c = json[i];
                if (c == '"' && (i == 0 || json[i - 1] != '\\')) inString = !inString;
                if (inString) continue;
                if (c == '{') depth++;
                else if (c == '}') { depth--; if (depth == 0) return json.Substring(start, i - start + 1); }
            }
            return "{}";
        }

        public static TributaryData LoadTributaries(string fileName = "tributary_areas.json")
        {
            string path = Path.Combine(Application.streamingAssetsPath, fileName);
            if (!File.Exists(path))
            {
                Debug.LogWarning($"[JsonLoader] No existe tributary_areas.json: {path}");
                return null;
            }
            string json = File.ReadAllText(path);
            try
            {
                TributaryData data = JsonUtility.FromJson<TributaryData>(json);
                data.buildings = JsonUtility.FromJson<TributaryFloorMap>(ExtractObject(json, "buildings"));
                Debug.Log($"[JsonLoader] Tributarias cargadas: {data.areas?.Count} areas, carga total {data.total_load_kN:F1} kN");
                return data;
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"[JsonLoader] Error al parsear tributary_areas.json: {ex.Message}");
                return null;
            }
        }

        public static SeismicData LoadSeismic(string fileName = "seismic_ex_ey.json")
        {
            string path = Path.Combine(Application.streamingAssetsPath, fileName);
            if (!File.Exists(path))
            {
                Debug.LogWarning($"[JsonLoader] No existe seismic_ex_ey.json: {path}");
                return null;
            }
            string json = File.ReadAllText(path);
            try
            {
                SeismicData data = JsonUtility.FromJson<SeismicData>(json);
                Debug.Log($"[JsonLoader] Sismico cargado: {data.floors?.Count} pisos");
                return data;
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"[JsonLoader] Error al parsear seismic_ex_ey.json: {ex.Message}");
                return null;
            }
        }

        public static ArchitecturalVisualModelData LoadArchitecture(string fileName = "architectural_visual_model.json")
        {
            return LoadOptional<ArchitecturalVisualModelData>(fileName, "modelo visual arquitectonico");
        }

        public static VisualLinesData LoadVisualLines(string fileName = "visual_lines.json")
        {
            return LoadOptional<VisualLinesData>(fileName, "lineas visuales compatibles");
        }

        public static AnalysisResultsData LoadAnalysisResults(string fileName = "analysis_results.json")
        {
            return LoadOptional<AnalysisResultsData>(fileName, "resultados de analisis");
        }

        public static AnalysisCasesData LoadAnalysisCases(string fileName = "analysis_cases.json")
        {
            return LoadOptional<AnalysisCasesData>(fileName, "casos G/Q/EX/EY/R");
        }

        public static P1L3DeliveryData LoadDelivery(string fileName = "p1l3_delivery.json")
        {
            return LoadOptional<P1L3DeliveryData>(fileName, "resumen P1L3");
        }

        public static CapacityData LoadCapacity(string fileName = "capacity_ha.json")
        {
            return LoadOptional<CapacityData>(fileName, "capacidad HA");
        }

        public static Texture2D LoadPng(string fileName)
        {
            string path = Path.Combine(Application.streamingAssetsPath, fileName);
            if (!File.Exists(path))
            {
                Debug.LogWarning($"[JsonLoader] No existe imagen: {path}");
                return null;
            }
            try
            {
                var texture = new Texture2D(2, 2, TextureFormat.RGBA32, false);
                if (!texture.LoadImage(File.ReadAllBytes(path))) return null;
                texture.name = fileName;
                return texture;
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"[JsonLoader] Error al cargar imagen {fileName}: {ex.Message}");
                return null;
            }
        }

        private static T LoadOptional<T>(string fileName, string label) where T : class
        {
            string path = Path.Combine(Application.streamingAssetsPath, fileName);
            if (!File.Exists(path))
            {
                Debug.LogWarning($"[JsonLoader] No existe {label}: {path}");
                return null;
            }
            try
            {
                return JsonUtility.FromJson<T>(File.ReadAllText(path));
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"[JsonLoader] Error al parsear {label}: {ex.Message}");
                return null;
            }
        }
    }
}
