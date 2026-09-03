using System.IO;
using Newtonsoft.Json;
using UnityEngine;

namespace Mcoc.Semana2.UnityE1
{
    public static class E1GravityJsonLoader
    {
        public const string DefaultFileName = "edificio1_unity.json";

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
    }
}
