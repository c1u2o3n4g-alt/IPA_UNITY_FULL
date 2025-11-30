# Script: Chuyển sang branch main và merge code từ okd

Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         🔄 CHUYỂN SANG BRANCH MAIN 🔄                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$currentBranch = (git branch --show-current).Trim()
Write-Host "  Branch hiện tại: $currentBranch" -ForegroundColor Yellow
Write-Host ""

# Step 1: Commit thay đổi hiện tại
Write-Host "  📝 Bước 1: Commit thay đổi trên branch $currentBranch..." -ForegroundColor Cyan

$gitStatus = git status --porcelain
if (-not [string]::IsNullOrWhiteSpace($gitStatus)) {
    Write-Host "  ⏳ Đang commit thay đổi..." -ForegroundColor Yellow
    git add .
    git commit -m "Update auto-build tool and Git LFS setup"
    
    Write-Host "  ⏳ Đang push lên origin/$currentBranch..." -ForegroundColor Yellow
    
    # Check upstream
    $upstream = git rev-parse --abbrev-ref "$currentBranch@{upstream}" 2>$null
    if (-not $upstream) {
        git push --set-upstream origin $currentBranch
    } else {
        git push origin $currentBranch
    }
    
    Write-Host "  ✅ Đã commit và push $currentBranch" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  Không có thay đổi cần commit" -ForegroundColor White
}

Write-Host ""

# Step 2: Checkout main
Write-Host "  📝 Bước 2: Checkout branch main..." -ForegroundColor Cyan
git checkout main

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Không thể checkout main" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Đã checkout main" -ForegroundColor Green
Write-Host ""

# Step 3: Pull latest main
Write-Host "  📝 Bước 3: Pull latest từ origin/main..." -ForegroundColor Cyan
git pull origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ⚠️  Pull có conflict hoặc lỗi" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Merge okd vào main
Write-Host "  📝 Bước 4: Merge $currentBranch vào main..." -ForegroundColor Cyan
$mergeMessage = "Merge $currentBranch - Add auto-build tool and Git LFS setup"
git merge $currentBranch -m $mergeMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Merge có conflict! Cần giải quyết thủ công" -ForegroundColor Red
    Write-Host "  📝 Sau khi resolve conflict:" -ForegroundColor Yellow
    Write-Host "     git add ." -ForegroundColor White
    Write-Host "     git commit" -ForegroundColor White
    Write-Host "     git push origin main" -ForegroundColor White
    exit 1
}

Write-Host "  ✅ Đã merge $currentBranch vào main" -ForegroundColor Green
Write-Host ""

# Step 5: Push main
Write-Host "  📝 Bước 5: Push main lên GitHub..." -ForegroundColor Cyan
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Không thể push main" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Đã push main lên GitHub" -ForegroundColor Green
Write-Host ""

# Done
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ HOÀN TẤT! ✅                             ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  ✅ Đã chuyển sang branch main" -ForegroundColor Green
Write-Host "  ✅ Đã merge tất cả thay đổi từ $currentBranch" -ForegroundColor Green
Write-Host "  ✅ Đã push lên origin/main" -ForegroundColor Green
Write-Host ""
Write-Host "  🚀 Bây giờ bạn có thể chạy:" -ForegroundColor Cyan
Write-Host "     .\auto-build-full.ps1" -ForegroundColor White
Write-Host ""
