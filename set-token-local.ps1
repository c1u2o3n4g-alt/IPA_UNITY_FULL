# Script: Set GitHub Token riêng cho project này
# Không ảnh hưởng đến các project khác

Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "🔑 SET GITHUB TOKEN CHO PROJECT NÀY" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# Nhập token mới
$token = Read-Host "Nhập GitHub Token mới (ghp_...)" -MaskInput

if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Host "❌ Token không được để trống!" -ForegroundColor Red
    exit 1
}

# Validate token format
if (-not $token.StartsWith("ghp_") -and -not $token.StartsWith("github_pat_")) {
    Write-Host "⚠️  Cảnh báo: Token không đúng định dạng GitHub (ghp_... hoặc github_pat_...)" -ForegroundColor Yellow
    $confirm = Read-Host "Bạn có chắc muốn tiếp tục? (y/n)"
    if ($confirm -ne "y") {
        Write-Host "❌ Đã hủy!" -ForegroundColor Red
        exit 1
    }
}

# Lưu token vào file .env (sẽ được gitignore)
$envContent = "GITHUB_TOKEN=$token"
$envContent | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline

Write-Host ""
Write-Host "✅ Đã lưu token vào file .env" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Để chạy build với token mới:" -ForegroundColor Cyan
Write-Host "   .\run-with-local-token.ps1" -ForegroundColor White
Write-Host ""
Write-Host "💡 Token này CHỈ áp dụng cho project này, không ảnh hưởng các project khác!" -ForegroundColor Yellow
