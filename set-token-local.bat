@echo off
chcp 65001 >nul
cls
echo ============================================================
echo 🔑 SET GITHUB TOKEN CHO PROJECT NAY
echo ============================================================
echo.

set /p "token=Nhap GitHub Token moi (ghp_...): "

if "%token%"=="" (
    echo ❌ Token khong duoc de trong!
    pause
    exit /b 1
)

echo GITHUB_TOKEN=%token%> .env

echo.
echo ✅ Da luu token vao file .env
echo.
echo 📝 De chay build voi token moi:
echo    run-with-local-token.bat
echo.
echo 💡 Token nay CHI ap dung cho project nay!
echo.
pause
