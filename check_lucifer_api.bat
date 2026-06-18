@echo off
title LuciferOS API Health Check
cd /d "C:\Users\Eirik Gulbrandsen\developer\luciferos_v2"
echo.
echo ========================================
echo  LuciferOS API Health Check
echo ========================================
echo.
py -m lucifer_os.interfaces.cli --api-health
if errorlevel 1 (
    echo.
    echo FEIL: LuciferOS API svarer ikke.
    echo Start API-serveren med:
    echo   start_lucifer_api.bat
    echo.
    pause
    exit /b 1
)
echo.
echo OK: LuciferOS API svarer.
echo.
pause
