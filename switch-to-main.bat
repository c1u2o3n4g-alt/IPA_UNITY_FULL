@echo off
chcp 65001 >nul
cls

echo ╔══════════════════════════════════════════════════════════╗
echo ║         🔄 CHUYỂN SANG BRANCH MAIN 🔄                    ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Script nay se:
echo   1. Commit thay doi hien tai
echo   2. Checkout branch main
echo   3. Merge code tu branch hien tai vao main
echo   4. Push main len GitHub
echo.
pause

powershell -ExecutionPolicy Bypass -File switch-to-main.ps1

pause
