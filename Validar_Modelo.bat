@echo off
setlocal
call "%~dp0Proyecto.bat" validar
set "RESULT=%ERRORLEVEL%"
echo.
if "%RESULT%"=="0" echo Validacion terminada correctamente.
if not "%RESULT%"=="0" echo La validacion encontro errores. Revisa el detalle anterior.
pause
exit /b %RESULT%
