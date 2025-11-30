@echo off
chcp 65001 >nul
cls
echo 🚀 Dang chay build voi token rieng...
echo.

if not exist .env (
    echo ❌ Chua co file .env!
    echo 📝 Chay lenh nay truoc: set-token-local.bat
    pause
    exit /b 1
)

for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="GITHUB_TOKEN" set "GITHUB_TOKEN=%%b"
)

if "%GITHUB_TOKEN%"=="" (
    echo ❌ File .env khong dung dinh dang!
    echo 📝 Chay lai: set-token-local.bat
    pause
    exit /b 1
)

echo ✅ Da load token tu .env
echo 💡 Token nay CHI ap dung cho lan chay nay!
echo.

python auto_build_ipa.py

pause
