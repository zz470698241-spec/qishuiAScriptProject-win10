@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Qishui Win10 - Run
echo.
echo  ============================================================
echo   Qishui Music auto-ad script (Win10 Edition)
echo  ============================================================
echo.
echo  Before running, make sure:
echo   1. config.py is set correctly (backend / ADB path / package)
echo   2. Android emulator is ON, or desktop window is ready
echo.
echo  Press Ctrl+C in this window to stop the script.
echo.
python run.py
echo.
echo  Script exited.
pause
