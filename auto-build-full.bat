@echo off
chcp 65001 >nul
cls

echo ╔══════════════════════════════════════════════════════════╗
echo ║     🚀 AUTO BUILD IPA - FULL AUTOMATION 🚀              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

set /p "commit=Nhap commit message (Enter = auto): "
set /p "config=Build config [Release/Debug] (Enter = Release): "
set /p "branch=Branch (Enter = main): "

if "%commit%"=="" set "commit=Auto build: %date% %time%"
if "%config%"=="" set "config=Release"
if "%branch%"=="" set "branch=main"

echo.
echo Dang chay build automation...
echo.

powershell -ExecutionPolicy Bypass -File auto-build-full.ps1 -CommitMessage "%commit%" -BuildConfig "%config%" -Branch "%branch%"

pause
