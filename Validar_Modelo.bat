@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
  echo No se encontro el entorno Python del proyecto.
  pause
  exit /b 1
)

"%PYTHON_EXE%" "entregas\P1L3\scripts\validate_unity_integration.py"
set "RESULT=%ERRORLEVEL%"
echo.
if "%RESULT%"=="0" echo Validacion terminada correctamente.
if not "%RESULT%"=="0" echo La validacion encontro errores. Revisa el detalle anterior.
pause
exit /b %RESULT%
