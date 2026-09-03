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
    }
}
