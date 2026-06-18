@echo off
title LuciferOS API Server
cd /d "C:\Users\Eirik Gulbrandsen\developer\luciferos_v2"
echo.
echo ========================================
echo  LuciferOS API Server
echo ========================================
echo.
echo URL:
echo   http://127.0.0.1:8787
echo.
echo Health check from another PowerShell window:
echo   py -m lucifer_os.interfaces.cli --api-health
echo.
echo Chat through API from another PowerShell window:
echo   py -m lucifer_os.interfaces.cli --api "Hei Lucifer"
echo.
echo Press CTRL+C to stop the API server.
echo.
py -m lucifer_os.interfaces.api_server
echo.
echo LuciferOS API server stopped.
pause
