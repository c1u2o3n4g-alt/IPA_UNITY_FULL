# Script để set GitHub token tự động
# Sử dụng: .\set_token.ps1

$env:GITHUB_TOKEN='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d'

Write-Host "✅ GitHub token đã được set!" -ForegroundColor Green
Write-Host "Bạn có thể chạy: python auto_build_ipa.py" -ForegroundColor Cyan

