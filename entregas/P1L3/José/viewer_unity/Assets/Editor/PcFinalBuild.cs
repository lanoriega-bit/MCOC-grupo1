using UnityEditor;
using UnityEditor.Build.Reporting;
using System.IO;

namespace Mcoc.UnityViewer.EditorTools
{
    public static class PcFinalBuild
    {
        public static void Build()
        {
            string output = Path.GetFullPath("Builds/FinalReview/StructuralReview_Final.exe");
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { "Assets/Main.unity" },
                locationPathName = output,
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.Development
            });
            if (report.summary.result != BuildResult.Succeeded)
                throw new System.Exception("Final desktop build failed: " + report.summary.result);
            UnityEngine.Debug.Log("[FINAL BUILD] PASS: " + output);
        }
    }
}