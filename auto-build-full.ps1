# AUTO BUILD IPA - FULL AUTOMATION
# Tự động: Push code → Trigger workflow → Monitor → Download IPA

param(
    [string]$CommitMessage = "Auto build: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    [string]$BuildConfig = "Release",
    [string]$Branch = ""
)

$ErrorActionPreference = "Stop"

# ============================================================
# FUNCTIONS
# ============================================================

function Write-Step {
    param([string]$Message, [string]$Color = "Cyan")
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $Color
    Write-Host "  $Message" -ForegroundColor $Color
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $Color
}

function Write-Info {
    param([string]$Message)
    Write-Host "  ℹ️  $Message" -ForegroundColor White
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "  ❌ $Message" -ForegroundColor Red
}

function Write-Progress {
    param([string]$Message)
    Write-Host "  ⏳ $Message" -ForegroundColor Yellow
}

function Get-LocalToken {
    if (Test-Path ".env") {
        $envContent = Get-Content ".env" -Raw
        if ($envContent -match "GITHUB_TOKEN=(.+)") {
            return $matches[1].Trim()
        }
    }
    
    $globalToken = $env:GITHUB_TOKEN
    if ($globalToken) {
        return $globalToken
    }
    
    Write-Error "Không tìm thấy GitHub Token!"
    Write-Info "Chạy: .\set-token-local.ps1"
    exit 1
}

function Invoke-GitHubAPI {
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [object]$Body = $null,
        [string]$Token
    )
    
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Accept" = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
    }
    
    $params = @{
        Uri = $Uri
        Method = $Method
        Headers = $headers
    }
    
    if ($Body) {
        $params.Body = ($Body | ConvertTo-Json)
        $params.ContentType = "application/json"
    }
    
    try {
        return Invoke-RestMethod @params
    } catch {
        Write-Error "API Error: $($_.Exception.Message)"
        if ($_.ErrorDetails.Message) {
            Write-Host $_.ErrorDetails.Message -ForegroundColor Red
        }
        throw
    }
}

# ============================================================
# MAIN SCRIPT
# ============================================================

Clear-Host
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║     🚀 AUTO BUILD IPA - FULL AUTOMATION 🚀              ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

# Config
$REPO_OWNER = "c1u2o3n4g-alt"
$REPO_NAME = "IPA_UNITY_FULL"
$WORKFLOW_FILE = "build-ipa.yml"

# Auto-detect branch if not specified
if ([string]::IsNullOrWhiteSpace($Branch)) {
    $Branch = (git branch --show-current).Trim()
    Write-Info "Auto-detected branch: $Branch"
}

Write-Info "Repository: $REPO_OWNER/$REPO_NAME"
Write-Info "Branch: $Branch"
Write-Info "Build Config: $BuildConfig"
Write-Info "Commit Message: $CommitMessage"
Write-Host ""

# ============================================================
# STEP 1: LOAD TOKEN
# ============================================================

Write-Step "BƯỚC 1: LOAD GITHUB TOKEN" "Cyan"
$TOKEN = Get-LocalToken
Write-Success "Đã load token từ local environment"

# ============================================================
# STEP 2: PUSH CODE
# ============================================================

Write-Step "BƯỚC 2: PUSH CODE LÊN GITHUB" "Cyan"

Write-Progress "Kiểm tra git status..."
$gitStatus = git status --porcelain
if ([string]::IsNullOrWhiteSpace($gitStatus)) {
    Write-Info "Không có thay đổi mới"
} else {
    Write-Info "Có thay đổi, đang commit..."
    git add .
    git commit -m $CommitMessage
    
    Write-Progress "Đang push lên GitHub..."
    
    # Check if branch has upstream
    $upstream = git rev-parse --abbrev-ref "$Branch@{upstream}" 2>$null
    if (-not $upstream) {
        Write-Info "Branch chưa có upstream, đang set upstream..."
        git push --set-upstream origin $Branch
    } else {
        git push origin $Branch
    }
    
    Write-Success "Đã push code lên GitHub"
}

Start-Sleep -Seconds 2

# ============================================================
# STEP 3: TRIGGER WORKFLOW
# ============================================================

Write-Step "BƯỚC 3: TRIGGER WORKFLOW" "Cyan"

$triggerBody = @{
    ref = $Branch
    inputs = @{
        build_configuration = $BuildConfig
    }
}

$triggerUri = "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/workflows/$WORKFLOW_FILE/dispatches"

Write-Progress "Đang trigger workflow..."
try {
    Invoke-GitHubAPI -Uri $triggerUri -Method "POST" -Body $triggerBody -Token $TOKEN
    Write-Success "Đã trigger workflow thành công!"
} catch {
    Write-Error "Không thể trigger workflow"
    exit 1
}

Start-Sleep -Seconds 5

# ============================================================
# STEP 4: MONITOR WORKFLOW
# ============================================================

Write-Step "BƯỚC 4: THEO DÕI TIẾN TRÌNH BUILD" "Cyan"

Write-Progress "Đang tìm workflow run..."

$maxRetries = 10
$retryCount = 0
$runId = $null

while ($retryCount -lt $maxRetries) {
    $runsUri = "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/runs?per_page=5"
    $runs = Invoke-GitHubAPI -Uri $runsUri -Token $TOKEN
    
    $latestRun = $runs.workflow_runs | Where-Object { 
        $_.name -eq "Build iOS IPA" -and 
        $_.head_branch -eq $Branch 
    } | Select-Object -First 1
    
    if ($latestRun) {
        $runId = $latestRun.id
        Write-Success "Tìm thấy workflow run: #$runId"
        Write-Info "URL: $($latestRun.html_url)"
        break
    }
    
    $retryCount++
    Write-Progress "Chờ workflow khởi động... ($retryCount/$maxRetries)"
    Start-Sleep -Seconds 3
}

if (-not $runId) {
    Write-Error "Không tìm thấy workflow run sau $maxRetries lần thử"
    exit 1
}

Write-Host ""
Write-Info "Đang theo dõi tiến trình build..."
Write-Info "Ước tính: 20-30 phút"
Write-Host ""

$lastStatus = ""
$startTime = Get-Date

while ($true) {
    $runUri = "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/runs/$runId"
    $run = Invoke-GitHubAPI -Uri $runUri -Token $TOKEN
    
    $status = $run.status
    $conclusion = $run.conclusion
    $elapsed = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)
    
    if ($status -ne $lastStatus) {
        $statusIcon = switch ($status) {
            "queued" { "⏸️" }
            "in_progress" { "🔄" }
            "completed" { "✅" }
            default { "❓" }
        }
        
        Write-Host "  $statusIcon Status: $status (Elapsed: $elapsed min)" -ForegroundColor Yellow
        $lastStatus = $status
    }
    
    # Check steps progress
    $jobsUri = "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/runs/$runId/jobs"
    $jobs = Invoke-GitHubAPI -Uri $jobsUri -Token $TOKEN
    
    foreach ($job in $jobs.jobs) {
        if ($job.status -eq "in_progress" -and $job.steps) {
            $completedSteps = ($job.steps | Where-Object { $_.status -eq "completed" }).Count
            $totalSteps = $job.steps.Count
            $percentage = [math]::Round(($completedSteps / $totalSteps) * 100)
            
            $currentStep = $job.steps | Where-Object { $_.status -eq "in_progress" } | Select-Object -First 1
            if ($currentStep) {
                Write-Host "  🔨 $($currentStep.name) - $percentage% ($completedSteps/$totalSteps steps)" -ForegroundColor Cyan
            }
        }
    }
    
    if ($status -eq "completed") {
        Write-Host ""
        if ($conclusion -eq "success") {
            Write-Success "BUILD THÀNH CÔNG! (Thời gian: $elapsed phút)"
        } else {
            Write-Error "BUILD THẤT BẠI: $conclusion"
            Write-Info "Xem log tại: $($run.html_url)"
            exit 1
        }
        break
    }
    
    Start-Sleep -Seconds 15
}

# ============================================================
# STEP 5: DOWNLOAD IPA
# ============================================================

Write-Step "BƯỚC 5: DOWNLOAD IPA" "Cyan"

Write-Progress "Đang tìm artifacts..."

$artifactsUri = "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/runs/$runId/artifacts"
$artifacts = Invoke-GitHubAPI -Uri $artifactsUri -Token $TOKEN

$ipaArtifact = $artifacts.artifacts | Where-Object { $_.name -eq "NROFLY.ipa" } | Select-Object -First 1

if (-not $ipaArtifact) {
    Write-Error "Không tìm thấy file IPA trong artifacts"
    exit 1
}

Write-Success "Tìm thấy artifact: $($ipaArtifact.name) ($([math]::Round($ipaArtifact.size_in_bytes / 1MB, 2)) MB)"

$downloadUri = $ipaArtifact.archive_download_url
$outputDir = ".\output"
$outputZip = "$outputDir\NROFLY.ipa.zip"
$outputIpa = "$outputDir\NROFLY.ipa"

if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

Write-Progress "Đang download IPA..."

$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Accept" = "application/vnd.github+json"
}

try {
    Invoke-WebRequest -Uri $downloadUri -Headers $headers -OutFile $outputZip
    Write-Success "Đã download artifact"
    
    Write-Progress "Đang giải nén..."
    
    # Extract zip
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($outputZip)
    
    $ipaEntry = $zip.Entries | Where-Object { $_.Name -like "*.ipa" } | Select-Object -First 1
    
    if ($ipaEntry) {
        [System.IO.Compression.ZipFileExtensions]::ExtractToFile($ipaEntry, $outputIpa, $true)
        Write-Success "Đã giải nén IPA"
    }
    
    $zip.Dispose()
    Remove-Item $outputZip -Force
    
    Write-Host ""
    Write-Success "HOÀN TẤT!"
    Write-Host ""
    Write-Info "File IPA: $outputIpa"
    Write-Info "Kích thước: $([math]::Round((Get-Item $outputIpa).Length / 1MB, 2)) MB"
    Write-Host ""
    
    # Open output folder
    Write-Info "Mở thư mục output..."
    Start-Process explorer.exe -ArgumentList (Resolve-Path $outputDir).Path
    
} catch {
    Write-Error "Lỗi khi download: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              🎉 BUILD IPA THÀNH CÔNG! 🎉                ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
