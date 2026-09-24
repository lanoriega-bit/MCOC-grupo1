@echo off
setlocal

rem PowerShell conserva correctamente la ruta Unicode del proyecto.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Abrir_Unity.ps1"
exit /b %ERRORLEVEL%
