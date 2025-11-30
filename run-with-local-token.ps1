# Script: Chạy build với token riêng của project này

Write-Host "🚀 Đang chạy build với token riêng..." -ForegroundColor Cyan
Write-Host ""

# Kiểm tra file .env
if (-not (Test-Path ".env")) {
    Write-Host "❌ Chưa có file .env!" -ForegroundColor Red
    Write-Host "📝 Chạy lệnh này trước: .\set-token-local.ps1" -ForegroundColor Yellow
    exit 1
}

# Đọc token từ file .env
$envContent = Get-Content ".env" -Raw
if ($envContent -match "GITHUB_TOKEN=(.+)") {
    $localToken = $matches[1].Trim()
    
    # Set token CHỈ cho session này (không ảnh hưởng global)
    $env:GITHUB_TOKEN = $localToken
    
    Write-Host "✅ Đã load token từ .env" -ForegroundColor Green
    Write-Host "💡 Token này CHỈ áp dụng cho lần chạy này!" -ForegroundColor Yellow
    Write-Host ""
    
    # Chạy Python script
    python auto_build_ipa.py
} else {
    Write-Host "❌ File .env không đúng định dạng!" -ForegroundColor Red
    Write-Host "📝 Chạy lại: .\set-token-local.ps1" -ForegroundColor Yellow
    exit 1
}
