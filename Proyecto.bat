@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0.venv-p1l5\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
set "PYTHONUTF8=1"
if "%~1"=="" (
  "%PYTHON_EXE%" "%~dp0main.py" menu
) else (
  "%PYTHON_EXE%" "%~dp0main.py" %*
)
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" pause
exit /b %RESULT%
