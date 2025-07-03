@echo off
cd /d C:\Users\pyetr\OneDrive\Desktop\unitypy

:loop
git add .
git commit -m "Auto-commit: %date% %time%"
git push origin main
timeout /t 60 >nul
goto loop
