using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.Build;
#if UNITY_ANDROID
using UnityEditor.Android;
#endif
using UnityEngine;

namespace Mcoc.UnityViewer.EditorTools
{
    public static class P1L6AndroidBuilder
    {
        public const string OutputPath = "Builds/P1L6/P1L6_AR_Final.apk";

        [MenuItem("MCOC/P1L6/Build Android APK")]
        public static void BuildApk()
        {
            if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.Android, BuildTarget.Android))
                throw new BuildFailedException(
                    "ANDROID_BUILD_SUPPORT_MISSING: install Android Build Support, SDK/NDK Tools and OpenJDK for Unity 6000.6.0f1.");

            string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string jdk = Path.Combine(localAppData, "Unity", "Toolchains", "OpenJDK17");
            if (!File.Exists(Path.Combine(jdk, "bin", "java.exe")))
                throw new BuildFailedException("OPENJDK17_MISSING: " + jdk);
#if UNITY_ANDROID
            AndroidExternalToolsSettings.jdkRootPath = jdk;
#endif

            P1L6ARFinalSceneBuilder.BuildFinalScene();
            P1L6ARFinalSceneBuilder.ValidateFinalScene();

            if (!EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Android, BuildTarget.Android))
                throw new BuildFailedException("No se pudo activar Android como plataforma de build.");

            PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel29;
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;

            string absoluteOutput = Path.GetFullPath(OutputPath);
            Directory.CreateDirectory(Path.GetDirectoryName(absoluteOutput));
            BuildPlayerOptions options = new BuildPlayerOptions
            {
                scenes = new[] { P1L6ARFinalSceneBuilder.FinalScenePath },
                locationPathName = absoluteOutput,
                target = BuildTarget.Android,
                options = BuildOptions.None
            };
            BuildReport report = BuildPipeline.BuildPlayer(options);
            if (report.summary.result != BuildResult.Succeeded)
                throw new BuildFailedException("Build Android P1L6 falló: " + report.summary.result);

            Debug.Log("[P1L6 MOBILE BUILD] PASS apk=" + absoluteOutput +
                " bytes=" + report.summary.totalSize);
        }
    }
}
