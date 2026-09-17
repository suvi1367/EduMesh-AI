# EduMesh AI Classroom Hub Startup Script for PowerShell

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "             EduMesh AI Classroom Hub              " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# 1. Check Python installation
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python is not installed or not in system PATH!" -ForegroundColor Red
    Write-Host "Please install Python 3.9 or higher." -ForegroundColor Yellow
    Exit 1
}

# 2. Check required directories
$dataDir = Join-Path $PSScriptRoot "..\data"
$configDir = Join-Path $PSScriptRoot "..\config"

if (-not (Test-Path $dataDir)) { New-Item -ItemType Directory -Path $dataDir | Out-Null }
if (-not (Test-Path $configDir)) { New-Item -ItemType Directory -Path $configDir | Out-Null }

$configFile = Join-Path $configDir "infrastructure_config.json"
if (-not (Test-Path $configFile)) {
    Write-Host "[INFO] Initializing default infrastructure configuration..." -ForegroundColor Yellow
    @{
        hub = @{ host = "0.0.0.0"; port = 8000 }
        cache = @{ similarity_threshold = 0.85; require_approval = $true }
        sync = @{ enabled = $true; auto_install = $false }
    } | ConvertTo-Json -Depth 3 | Out-File -FilePath $configFile -Encoding utf8
}

Write-Host "[INFO] Environment verified cleanly." -ForegroundColor Green
Write-Host "[INFO] Starting Hub service bound to 0.0.0.0:8000..." -ForegroundColor Green
Write-Host ""

# 3. Launch Backend
$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $projectRoot
python -m backend.main
