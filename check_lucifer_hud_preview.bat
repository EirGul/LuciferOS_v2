@echo off
title LuciferOS HUD Preview Check
cd /d "C:\Users\Eirik Gulbrandsen\developer\luciferos_v2"
echo.
echo ========================================
echo  LuciferOS HUD Preview Check
echo ========================================
echo.
echo Checking API health...
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
echo Checking HUD preview health...
py -m lucifer_os.interfaces.hud_preview health
if errorlevel 1 (
    echo.
    echo FEIL: HUD-preview feilet.
    echo.
    pause
    exit /b 1
)
echo.
echo OK: HUD-preview fungerer mot LuciferOS API.
echo.
pause
