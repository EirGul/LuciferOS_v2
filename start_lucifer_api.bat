@echo off
cd /d "C:\Users\Eirik Gulbrandsen\developer\luciferos_v2"
echo Starting LuciferOS API on http://127.0.0.1:8787
py -m lucifer_os.interfaces.api_server
pause
