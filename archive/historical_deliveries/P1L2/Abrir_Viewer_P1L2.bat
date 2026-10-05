@echo off
setlocal

set "P1L2_DIR=%~dp0"
cd /d "%P1L2_DIR%"

where python >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=python"
) else (
    set "PYTHON_CMD=py"
)

start "Servidor Viewer P1L2" /min %PYTHON_CMD% -m http.server 8000
timeout /t 2 /nobreak >nul
start "" "http://localhost:8000/viewer/?model=model_combined_viewer.json"

endlocal
