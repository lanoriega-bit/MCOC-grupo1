using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class AndroidScaleBuild
{
    public static void Run()
    {
        // Run only in the isolated snapshot created by BuildAndroid.ps1.
        if(!Path.GetFullPath(Directory.GetCurrentDirectory()).EndsWith(".scale-android-check",StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Android scale validation requires the isolated snapshot");
        string output=Path.GetFullPath("ARScaleValidation.apk");
        var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions{
            scenes=new[]{"Assets/Scenes/Luis_AR_Test.unity"},locationPathName=output,
            target=BuildTarget.Android,options=BuildOptions.None});
        if(report.summary.result!=BuildResult.Succeeded)throw new Exception("Android scale build failed: "+report.summary.result);
        Debug.Log("ANDROID_SCALE_BUILD_PASSED: "+output);
        EditorApplication.Exit(0);
    }
}
