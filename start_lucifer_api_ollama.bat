@echo off
setlocal
title LuciferOS API - Ollama
cd /d "%~dp0"

echo ========================================
echo LuciferOS API - Ollama provider
echo ========================================
echo.
echo Project: %cd%
echo Provider: ollama
echo URL: http://127.0.0.1:8787
echo.
echo Press Ctrl+C to stop.
echo.

set LUCIFER_PROVIDER=ollama
py -m lucifer_os.interfaces.api_server

endlocal
