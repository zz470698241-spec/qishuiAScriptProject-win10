@echo off
cd /d "%~dp0"
echo ============================================
echo  Install dependencies - Qishui Win10 Edition
echo ============================================
echo.
python -m pip install --upgrade pip
echo.
python -m pip install -r requirements.txt
echo.
echo ============================================
echo  Done. Now run:  python run.py
echo ============================================
pause
