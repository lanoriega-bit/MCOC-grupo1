using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEngine;

namespace Mcoc.UnityViewer
{
    [Serializable] public class CurrentDatasetUnits
    { public string length,force,moment,stress,mass,rotation; }
    [Serializable] public class CurrentDatasetContract
    {
        public string format,geometry_version,fe_version,loads_version,analysis_version,git_commit,timestamp,status;
        public string geometry_stream_sha256,payload_file,payload_sha256;
        public string analysis_settings_sha256;
        public bool analysis_available,fe_approved,loads_approved,linear_verified;
        public CurrentDatasetUnits units;
        public List<string> cases,basis_cases;
    }
    // The archived loader never uses this type. Future CURRENT import MUST pass
    // this gate plus payload/schema/equilibrium checks; changing a label cannot authorize it.
    public static class CurrentVersionGate
    {
        public static string Check(CurrentDatasetContract expected,CurrentDatasetContract result,string geometryStreamHash)
        {
            if(expected==null||result==null)return "CONTRACT_MISSING";
            if(result.format!="MCOC_CURRENT_DATASET_V1"||expected.format!=result.format)return "FORMAT_MISMATCH";
            if(!expected.fe_approved||!expected.loads_approved)return "CURRENT_INPUTS_NOT_APPROVED";
            if(result.status!="CURRENT_VERIFIED"||!result.analysis_available||!result.fe_approved||!result.loads_approved||!result.linear_verified)return "RESULTS_NOT_VERIFIED";
            if(string.IsNullOrEmpty(result.analysis_version)||result.analysis_version=="NONE_NOT_RUN")return "NO_ANALYSIS_VERSION";
            if(string.IsNullOrEmpty(result.git_commit)||string.IsNullOrEmpty(result.timestamp))return "PROVENANCE_MISSING";
            if(string.IsNullOrEmpty(expected.geometry_version)||expected.geometry_version!=result.geometry_version)return "GEOMETRY_MISMATCH";
            if(string.IsNullOrEmpty(expected.fe_version)||expected.fe_version!=result.fe_version)return "FE_MISMATCH";
            if(string.IsNullOrEmpty(expected.loads_version)||expected.loads_version!=result.loads_version)return "LOADS_MISMATCH";
            if(string.IsNullOrEmpty(geometryStreamHash)||result.geometry_stream_sha256!=geometryStreamHash||expected.geometry_stream_sha256!=geometryStreamHash)return "GEOMETRY_FILE_MISMATCH";
            var u=result.units;
            if(u==null||u.length!="m"||u.force!="N"||u.moment!="N.m"||u.stress!="Pa"||u.mass!="kg"||u.rotation!="rad")return "UNITS_MISMATCH";
            if(result.cases==null||result.cases.Count!=5||new HashSet<string>(result.cases).Count!=5)return "CASES_MISSING";
            foreach(string c in new[]{"G","Q","EX","EY","R"})if(!result.cases.Contains(c))return "CASES_MISSING";
            if(result.basis_cases==null||string.Join(",",result.basis_cases)!="G,Q,EX,EY")return "BASIS_ORDER_MISMATCH";
            if(string.IsNullOrEmpty(result.payload_file)||string.IsNullOrEmpty(result.payload_sha256))return "PAYLOAD_MISSING";
            return "IDENTITY_MATCH_REQUIRES_PAYLOAD_QA";
        }
        public static string HashFile(string path)
        {using(var sha=SHA256.Create())using(var stream=File.OpenRead(path))return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-","").ToLowerInvariant();}
        public static string CheckRuntime(CurrentDatasetContract contract,string geometryStreamHash,string payloadHash)
        {
            string identity=Check(contract,contract,geometryStreamHash);
            if(identity!="IDENTITY_MATCH_REQUIRES_PAYLOAD_QA")return identity;
            if(string.IsNullOrEmpty(payloadHash)||payloadHash!=contract.payload_sha256)return "PAYLOAD_FILE_MISMATCH";
            return "CURRENT_VERIFIED";
        }
    }
    // Pure numerical preparation, not a P1L5 slider or a new FE analysis.
    public static class LinearBasisResponse
    {
        public static double[] Combine(double[][] basis,double[] alpha)
        {
            if(basis==null||basis.Length!=4||alpha==null||alpha.Length!=4)throw new ArgumentException("G,Q,EX,EY required");
            if(basis[0]==null)throw new ArgumentException("Missing basis");
            int n=basis[0].Length;var sum=new double[n];
            for(int k=0;k<4;k++)
            {
                if(basis[k]==null||basis[k].Length!=n||double.IsNaN(alpha[k])||double.IsInfinity(alpha[k]))throw new ArgumentException("Incompatible basis or coefficients");
                for(int i=0;i<n;i++)
                {if(double.IsNaN(basis[k][i])||double.IsInfinity(basis[k][i]))throw new ArgumentException("Non-finite response");sum[i]+=alpha[k]*basis[k][i];}
            }
            foreach(double value in sum)if(double.IsNaN(value)||double.IsInfinity(value))throw new ArgumentException("Response overflow");
            return sum;
        }
    }
    public partial class ViewerController
    {
        CurrentDatasetContract currentContract;bool currentContractLoaded;string currentGateStatus="CONTRACT_NOT_CHECKED";
        void LoadCurrentContract()
        {
            if(currentContractLoaded)return;currentContractLoaded=true;
            string path=Path.Combine(Application.streamingAssetsPath,"current_dataset_contract.json");
            if(File.Exists(path))try
            {
                currentContract=JsonUtility.FromJson<CurrentDatasetContract>(File.ReadAllText(path));
                string geometryPath=Path.Combine(Application.streamingAssetsPath,jsonFileName);
                string geometryHash=File.Exists(geometryPath)?CurrentVersionGate.HashFile(geometryPath):"";
                string payloadPath=string.IsNullOrEmpty(currentContract.payload_file)?"":Path.Combine(Application.streamingAssetsPath,currentContract.payload_file);
                string payloadHash=!string.IsNullOrEmpty(payloadPath)&&File.Exists(payloadPath)?CurrentVersionGate.HashFile(payloadPath):"";
                currentGateStatus=CurrentVersionGate.CheckRuntime(currentContract,geometryHash,payloadHash);
                if(currentGateStatus=="CURRENT_VERIFIED" && (currentContract.analysis_version??"").StartsWith("WEEK7_"))
                {
                    string settingsPath=Path.Combine(Application.streamingAssetsPath,"week7_analysis_settings.json");
                    if(!File.Exists(settingsPath)||CurrentVersionGate.HashFile(settingsPath)!=currentContract.analysis_settings_sha256)
                        currentGateStatus="SETTINGS_MISMATCH_REANALYSIS_REQUIRED";
                    string repository=FindRepositoryRoot();
                    if(repository!=null)
                    {
                        string sourcePath=Path.Combine(repository,"config","analysis_settings.json");
                        if(!File.Exists(sourcePath)||CurrentVersionGate.HashFile(sourcePath)!=currentContract.analysis_settings_sha256)
                            currentGateStatus="SOURCE_SETTINGS_MODIFIED_REANALYSIS_REQUIRED";
                    }
                }
                if(currentGateStatus!="CURRENT_VERIFIED")Debug.LogWarning("CURRENT bloqueado: "+currentGateStatus);
            }
            catch(Exception ex){Debug.LogWarning("Current contract unavailable: "+ex.Message);}
        }
        bool ReloadCurrentContractAndCheck()
        {currentContractLoaded=false;currentContract=null;currentGateStatus="CONTRACT_NOT_CHECKED";LoadCurrentContract();return currentGateStatus=="CURRENT_VERIFIED";}
        string CurrentVersionDiagnostic()
        {
            LoadCurrentContract();
            if(currentContract==null)return "Contrato de resultados actuales: no disponible; acceso bloqueado.";
            return "Versión geometría: "+currentContract.geometry_version+"\nVersión FE: "+currentContract.fe_version+
                "\nVersión cargas: "+currentContract.loads_version+"\nAnálisis: "+currentContract.analysis_version+
                "\nEstado: "+currentContract.status+" · gate: "+currentGateStatus+" · payload: "+currentContract.payload_file;
        }
    }
}
