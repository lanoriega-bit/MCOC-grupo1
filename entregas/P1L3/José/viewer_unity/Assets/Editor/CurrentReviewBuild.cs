using UnityEditor;
using UnityEditor.Build.Reporting;
using System.IO;

namespace Mcoc.UnityViewer.EditorTools
{
    public static class CurrentReviewBuild
    {
        public static void OpenForReview()
        {
            UnityEditor.SceneManagement.EditorSceneManager.OpenScene("Assets/Main.unity");
            var gameType=typeof(EditorWindow).Assembly.GetType("UnityEditor.GameView");
            if(gameType!=null){var game=EditorWindow.GetWindow(gameType);game.maximized=true;game.Focus();}
            EditorApplication.isPlaying=true;
        }

        public static void Build()
        {
            string output=Path.GetFullPath("Builds/CurrentReview/StructuralReview.exe");
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                scenes=new[]{"Assets/Main.unity"}, locationPathName=output,
                target=BuildTarget.StandaloneWindows64, options=BuildOptions.Development
            });
            if(report.summary.result!=BuildResult.Succeeded)throw new System.Exception("Current review build failed: "+report.summary.result);
            UnityEngine.Debug.Log("[CURRENT BUILD] PASS: "+output);
        }
    }
}
