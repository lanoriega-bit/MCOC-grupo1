@echo off
setlocal

set "ROOT=%~dp0"
cd /d "%ROOT%"

where python >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=python"
) else (
    set "PYTHON_CMD=py"
)

start "Servidor Viewer Semana 2" /min %PYTHON_CMD% -m http.server 8000
timeout /t 2 /nobreak >nul
start "" "http://localhost:8000/entregas/P1L2/viewer/"

endlocal
