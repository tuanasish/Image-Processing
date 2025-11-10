@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   Web UI - Nhan dang bien so xe
echo ========================================
echo.
echo Dang khoi dong server...
echo.
echo Mo trinh duyet va truy cap: http://127.0.0.1:5000
echo.
echo Nhan Ctrl+C de dung server
echo.
cd web
python app.py
pause

