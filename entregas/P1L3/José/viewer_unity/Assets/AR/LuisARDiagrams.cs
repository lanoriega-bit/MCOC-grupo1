using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.XR.ARSubsystems;

public class LuisARDiagrams : MonoBehaviour
{
    [SerializeField] LuisARImageAnchor arTracking;
    [SerializeField] GameObject infoPanel;

    const string ElementId = "E1-P2-V-041";

    bool trackingOk = false;
    bool showDiagrams = false;

    string selectedCase = "CASE_R";
    string selectedComponent = "My";

    AnalysisCasesRoot data;

    Texture2D lineTexture;
    Texture2D panelTexture;

    [Serializable]
    public class AnalysisCasesRoot
    {
        public string format;
        public string default_case;
        public List<AnalysisCase> cases;
    }

    [Serializable]
    public class AnalysisCase
    {
        public string case_name;
        public List<AnalysisElement> elements;
    }

    [Serializable]
    public class AnalysisElement
    {
        public string case_name;
        public string element_id;
        public string analysis_id;
        public int opensees_tag;

        public List<double> localForce_end1;
        public List<double> localForce_end2;
    }

    void Awake()
    {
        if (arTracking == null)
            arTracking = GetComponent<LuisARImageAnchor>();

        // Textura negra para las líneas de los diagramas.
        lineTexture = new Texture2D(1, 1);
        lineTexture.SetPixel(0, 0, Color.black);
        lineTexture.Apply();

        // Fondo blanco sólido para que la información
        // se vea bien sobre la cámara AR.
        panelTexture = new Texture2D(1, 1);
        panelTexture.SetPixel(0, 0, Color.white);
        panelTexture.Apply();

        StartCoroutine(LoadResults());
    }

    void OnEnable()
    {
        if (arTracking != null)
            arTracking.TrackingUpdated += OnTrackingUpdated;
    }

    void OnDisable()
    {
        if (arTracking != null)
            arTracking.TrackingUpdated -= OnTrackingUpdated;
    }

    void OnTrackingUpdated(
        string referenceImageName,
        Pose anchorPose,
        TrackingState trackingState)
    {
        trackingOk =
            trackingState == TrackingState.Tracking &&
            arTracking != null &&
            arTracking.HasAnchor;

        if (!trackingOk)
            showDiagrams = false;
    }

    IEnumerator LoadResults()
    {
        string path =
            Application.streamingAssetsPath +
            "/analysis_cases.json";

        using (UnityWebRequest request =
               UnityWebRequest.Get(path))
        {
            yield return request.SendWebRequest();

            if (request.result !=
                UnityWebRequest.Result.Success)
            {
                Debug.LogError(
                    "LuisARDiagrams: error leyendo resultados: " +
                    request.error
                );

                yield break;
            }

            string json =
                request.downloadHandler.text;

            data =
                JsonUtility.FromJson<AnalysisCasesRoot>(
                    json
                );

            if (data == null ||
                data.cases == null)
            {
                Debug.LogError(
                    "LuisARDiagrams: JSON inválido."
                );

                yield break;
            }

            Debug.Log(
                "LuisARDiagrams: " +
                data.cases.Count +
                " casos cargados correctamente."
            );
        }
    }

    AnalysisElement GetSelectedResult()
    {
        if (data == null || data.cases == null)
            return null;

        foreach (var analysisCase in data.cases)
        {
            if (analysisCase == null ||
                analysisCase.case_name != selectedCase ||
                analysisCase.elements == null)
                continue;

            foreach (var element in analysisCase.elements)
            {
                if (element != null &&
                    element.element_id == ElementId)
                    return element;
            }
        }

        return null;
    }

    int ComponentIndex()
    {
        if (selectedComponent == "N")
            return 0;

        if (selectedComponent == "Vy")
            return 1;

        if (selectedComponent == "Vz")
            return 2;

        if (selectedComponent == "My")
            return 4;

        if (selectedComponent == "Mz")
            return 5;

        return 4;
    }

    string Units()
    {
        if (selectedComponent == "My" ||
            selectedComponent == "Mz")
            return "kN·m";

        return "kN";
    }

    void OnGUI()
    {
        if (!trackingOk)
            return;

        // Solo mostramos diagramas si el panel
        // de información de la viga está abierto.
        if (infoPanel != null &&
            !infoPanel.activeInHierarchy)
            return;

        GUIStyle button =
            new GUIStyle(GUI.skin.button);

        button.fontSize = 25;
        button.normal.textColor = Color.black;
        button.hover.textColor = Color.black;
        button.active.textColor = Color.black;
        button.focused.textColor = Color.black;

        GUIStyle label =
            new GUIStyle(GUI.skin.label);

        label.fontSize = 25;
        label.normal.textColor = Color.black;
        label.alignment = TextAnchor.MiddleCenter;

        float w =
            Mathf.Min(
                Screen.width - 40f,
                950f
            );

        Rect toggleRect =
            new Rect(
                (Screen.width - w) * 0.5f,
                Screen.height - 170f,
                w,
                70f
            );

        if (!showDiagrams)
        {
            if (GUI.Button(
                toggleRect,
                "Ver diagramas",
                button))
            {
                showDiagrams = true;
            }

            return;
        }

        float panelHeight = 720f;

        Rect panel =
            new Rect(
                (Screen.width - w) * 0.5f,
                Mathf.Max(
                    20f,
                    Screen.height -
                    panelHeight -
                    40f
                ),
                w,
                panelHeight
            );

        // Fondo blanco completamente sólido.
        GUI.DrawTexture(
            panel,
            panelTexture,
            ScaleMode.StretchToFill
        );

        GUI.Box(panel, "");

        if (GUI.Button(
            new Rect(
                panel.x +
                panel.width -
                70f,
                panel.y + 15f,
                50f,
                45f
            ),
            "X",
            button))
        {
            showDiagrams = false;
            return;
        }

        GUI.Label(
            new Rect(
                panel.x + 20f,
                panel.y + 15f,
                panel.width - 100f,
                45f
            ),
            "Diagramas · " +
            ElementId,
            label
        );

        DrawCaseButtons(
            panel,
            button
        );

        DrawComponentButtons(
            panel,
            button
        );

        DrawDiagram(
            panel,
            label
        );
    }

    void DrawCaseButtons(
        Rect panel,
        GUIStyle button)
    {
        string[] cases =
        {
            "CASE_G",
            "CASE_Q",
            "CASE_EX",
            "CASE_EY",
            "CASE_R"
        };

        string[] names =
        {
            "G",
            "Q",
            "EX",
            "EY",
            "R"
        };

        float y =
            panel.y + 80f;

        float spacing = 10f;

        float bw =
            (
                panel.width -
                40f -
                4f * spacing
            ) / 5f;

        for (int i = 0;
             i < cases.Length;
             i++)
        {
            if (GUI.Button(
                new Rect(
                    panel.x +
                    20f +
                    i * (bw + spacing),
                    y,
                    bw,
                    50f
                ),
                names[i],
                button))
            {
                selectedCase =
                    cases[i];
            }
        }
    }

    void DrawComponentButtons(
        Rect panel,
        GUIStyle button)
    {
        string[] components =
        {
            "N",
            "Vy",
            "Vz",
            "My",
            "Mz"
        };

        float y =
            panel.y + 150f;

        float spacing = 10f;

        float bw =
            (
                panel.width -
                40f -
                4f * spacing
            ) / 5f;

        for (int i = 0;
             i < components.Length;
             i++)
        {
            string component =
                components[i];

            if (GUI.Button(
                new Rect(
                    panel.x +
                    20f +
                    i * (bw + spacing),
                    y,
                    bw,
                    50f
                ),
                component,
                button))
            {
                selectedComponent =
                    component;
            }
        }
    }

    void DrawDiagram(
        Rect panel,
        GUIStyle label)
    {
        AnalysisElement result =
            GetSelectedResult();

        if (result == null ||
            result.localForce_end1 == null ||
            result.localForce_end2 == null)
        {
            GUI.Label(
                new Rect(
                    panel.x + 20f,
                    panel.y + 240f,
                    panel.width - 40f,
                    80f
                ),
                "Sin resultados para este caso.",
                label
            );

            return;
        }

        int component =
            ComponentIndex();

        if (result.localForce_end1.Count <= component ||
            result.localForce_end2.Count <= component)
        {
            return;
        }

        // Mismo criterio usado por ViewerController:
        // extremo i se conserva.
        // extremo j se invierte para trabajar
        // sobre una cara interna común.
        double valueI =
            result.localForce_end1[component] /
            1000.0;

        double valueJ =
            -result.localForce_end2[component] /
            1000.0;

        Rect graph =
            new Rect(
                panel.x + 60f,
                panel.y + 260f,
                panel.width - 120f,
                300f
            );

        // Fondo blanco del gráfico.
        GUI.DrawTexture(
            graph,
            panelTexture,
            ScaleMode.StretchToFill
        );

        GUI.Box(graph, "");

        float centerY =
            graph.y +
            graph.height * 0.5f;

        // Eje horizontal negro.
        DrawLine(
            new Vector2(
                graph.x,
                centerY
            ),
            new Vector2(
                graph.xMax,
                centerY
            ),
            2f
        );

        double maxAbs =
            Math.Max(
                Math.Abs(valueI),
                Math.Abs(valueJ)
            );

        if (maxAbs < 1e-12)
            maxAbs = 1.0;

        float scale =
            (
                graph.height *
                0.38f
            ) /
            (float)maxAbs;

        Vector2 p0 =
            new Vector2(
                graph.x,
                centerY -
                (float)valueI *
                scale
            );

        Vector2 p1 =
            new Vector2(
                graph.xMax,
                centerY -
                (float)valueJ *
                scale
            );

        // Línea desde el eje hasta extremo i.
        DrawLine(
            new Vector2(
                graph.x,
                centerY
            ),
            p0,
            4f
        );

        // Diagrama.
        DrawLine(
            p0,
            p1,
            5f
        );

        // Línea desde extremo j al eje.
        DrawLine(
            p1,
            new Vector2(
                graph.xMax,
                centerY
            ),
            4f
        );

        GUI.Label(
            new Rect(
                panel.x + 30f,
                panel.y + 580f,
                panel.width - 60f,
                45f
            ),
            selectedComponent +
            " · " +
            selectedCase +
            " · " +
            result.analysis_id,
            label
        );

        GUI.Label(
            new Rect(
                panel.x + 30f,
                panel.y + 625f,
                panel.width - 60f,
                60f
            ),
            "i = " +
            valueI.ToString("F3") +
            " " +
            Units() +
            "     |     j = " +
            valueJ.ToString("F3") +
            " " +
            Units(),
            label
        );
    }

    void DrawLine(
        Vector2 start,
        Vector2 end,
        float width)
    {
        Matrix4x4 oldMatrix =
            GUI.matrix;

        Vector2 delta =
            end - start;

        float angle =
            Mathf.Atan2(
                delta.y,
                delta.x
            ) *
            Mathf.Rad2Deg;

        GUIUtility.RotateAroundPivot(
            angle,
            start
        );

        GUI.DrawTexture(
            new Rect(
                start.x,
                start.y -
                width * 0.5f,
                delta.magnitude,
                width
            ),
            lineTexture
        );

        GUI.matrix =
            oldMatrix;
    }
}