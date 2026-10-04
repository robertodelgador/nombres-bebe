@echo off
title Bebe Names Studio
cd /d "%~dp0"

echo ========================================================
echo   🌸 Iniciando Bebe Names Studio...
echo   Directorio: %cd%
echo ========================================================

:: Open browser in 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000"

:: Start python server
python server.py 8000

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo No se pudo iniciar el servidor con python.
    echo Abriendo index.html directamente en el navegador...
    start "" "index.html"
    pause
)
