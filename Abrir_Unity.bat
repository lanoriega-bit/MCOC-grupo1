@echo off
setlocal
set "UNITY_EXE=C:\Program Files\Unity\Hub\Editor\6000.6.0f1\Editor\Unity.exe"
set "UNITY_PROJECT=%~dp0entregas\P1L3\José\viewer_unity"

if not exist "%UNITY_EXE%" (
  echo No se encontro Unity 6000.6.0f1 en la ruta esperada.
  echo Abre Unity Hub y agrega manualmente: %UNITY_PROJECT%
  pause
  exit /b 1
)

echo Abriendo la interfaz principal del proyecto...
start "" "%UNITY_EXE%" -projectPath "%UNITY_PROJECT%"
exit /b 0
