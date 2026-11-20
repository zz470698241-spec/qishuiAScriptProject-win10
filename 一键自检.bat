@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Qishui Win10 - Selftest
echo.
echo  ============================================================
echo   Self-test: verify code works (no phone/emulator needed)
echo  ============================================================
echo.
python selftest.py
echo.
pause
