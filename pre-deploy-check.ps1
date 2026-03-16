#!/usr/bin/env pwsh
# ============================================================================
# Pre-Deployment Verification Script for Task Tracker
# ============================================================================
# Validates Python 3.11, Node 25.8, Azure CLI, and project setup
# Run BEFORE executing deploy-to-azure.ps1
# ============================================================================

param(
    [switch]$Verbose = $false
)

# ------- Color Output Helpers -----------------------------------------------
function Write-Success {
    param([string]$Message)
    Write-Host "OK: $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "FAIL: $Message" -ForegroundColor Red
}

function Write-Warn {
    param([string]$Message)
    Write-Host "WARN: $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "INFO: $Message" -ForegroundColor Cyan
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "===================================================================" `
        -ForegroundColor Magenta
    Write-Host "  $Message" -ForegroundColor Magenta
    Write-Host "===================================================================" `
        -ForegroundColor Magenta
}

# ------- Test Result Tracking ------------------------------------------------
$script:testsPassed = 0
$script:testsFailed = 0
$script:testsWarning = 0

function Test-Condition {
    param(
        [string]$TestName,
        [bool]$Condition,
        [string]$SuccessMessage,
        [string]$FailureMessage,
        [string]$WarningMessage = $null
    )

    if ($Condition) {
        Write-Success $SuccessMessage
        $script:testsPassed++
        return $true
    }
    else {
        Write-Error-Custom $FailureMessage
        $script:testsFailed++
        return $false
    }
}

# ============================================================================
# Phase 1: Python 3.11 Verification
# ============================================================================
Write-Header "Phase 1: Python 3.11 Verification"

$pythonExists = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
$pythonVersionOutput = $(python --version 2>&1 | Out-String).Trim

if ($pythonExists) {
    $pythonVersion = [regex]::Match($pythonVersionOutput, '(\d+\.\d+)').Groups[1].Value

    if ($pythonVersion -like "3.11*" -or $pythonVersionOutput -like "*3.11*") {
        Write-Success "Python 3.11 detected: $pythonVersionOutput"
        $script:testsPassed++
    }
    else {
        Write-Warn "Python version mismatch"
        Write-Info "Expected: Python 3.11.x"
        Write-Info "Found: $pythonVersionOutput"
        $script:testsWarning++
    }
}
else {
    Write-Error-Custom "Python not found in PATH"
    Write-Info "Install Python 3.11 from: https://www.python.org/"
    $script:testsFailed++
}

$pipExists = $null -ne (Get-Command pip -ErrorAction SilentlyContinue)
Test-Condition "pip" $pipExists `
    "pip is installed and available" `
    "pip not found in PATH"

# ============================================================================
# Phase 2: Node 25.8 & npm Verification
# ============================================================================
Write-Header "Phase 2: Node.js 25.8 Verification"

$nodeExists = $null -ne (Get-Command node -ErrorAction SilentlyContinue)
$nodeVersionOutput = $(node --version 2>&1 | Out-String).Trim

if ($nodeExists) {
    $nodeVersion = [regex]::Match($nodeVersionOutput, 'v(\d+\.\d+)').Groups[1].Value
    Write-Info "Node version detected: $nodeVersionOutput"

    $major = [int]($nodeVersion -split "\.")[0]

    if ($major -ge 25) {
        Write-Success "Node 25.8+ detected (compatible)"
        $script:testsPassed++
    }
    elseif ($major -ge 18) {
        Write-Warn "Node $nodeVersion detected (older than 25.8)"
        $script:testsWarning++
    }
    else {
        Write-Error-Custom "Node version too old: $nodeVersion"
        $script:testsFailed++
    }
}
else {
    Write-Error-Custom "Node.js not found in PATH"
    Write-Info "Install from: https://nodejs.org/"
    $script:testsFailed++
}

$npmExists = $null -ne (Get-Command npm -ErrorAction SilentlyContinue)
if ($npmExists) {
    $npmVersion = npm --version 2>&1
    Write-Success "npm $npmVersion detected"
    $script:testsPassed++
}
else {
    Write-Error-Custom "npm not found"
    $script:testsFailed++
}

# ============================================================================
# Phase 3: Git Repository Verification
# ============================================================================
Write-Header "Phase 3: Git Repository Verification"

$gitExists = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
Test-Condition "Git CLI" $gitExists `
    "Git is installed" `
    "Git not found - Install from https://git-scm.com/"

if ($gitExists) {
    $gitStatus = git status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "In valid git repository"
        $script:testsPassed++

        $gitDiff = git status --porcelain 2>&1
        if ([string]::IsNullOrWhiteSpace($gitDiff)) {
            Write-Success "All changes committed"
            $script:testsPassed++
        }
        else {
            Write-Warn "Uncommitted changes detected"
            $script:testsWarning++
        }

        $currentBranch = git rev-parse --abbrev-ref HEAD 2>&1
        Write-Info "Current branch: $currentBranch"

        if ($currentBranch -eq "main" -or $currentBranch -eq "master") {
            Write-Success "On main/master branch"
            $script:testsPassed++
        }
        else {
            Write-Warn "Not on main/master branch"
            $script:testsWarning++
        }
    }
    else {
        Write-Error-Custom "Not in a git repository"
        $script:testsFailed++
    }
}

# ============================================================================
# Phase 4: Azure CLI Verification
# ============================================================================
Write-Header "Phase 4: Azure CLI Verification"

$azExists = $null -ne (Get-Command az -ErrorAction SilentlyContinue)
Test-Condition "Azure CLI" $azExists `
    "Azure CLI is installed" `
    "Azure CLI not found - Install from: https://aka.ms/cli"

if ($azExists) {
    $azVersion = az --version 2>&1 | Select-Object -First 1
    Write-Info "Azure CLI version: $azVersion"

    try {
        $account = az account show 2>&1 | ConvertFrom-Json
        Write-Success "Logged in to Azure"
        $script:testsPassed++
        Write-Info "Account: $($account.user.name)"
    }
    catch {
        Write-Error-Custom "Not logged in to Azure"
        Write-Info "Run: az login"
        $script:testsFailed++
    }
}

# ============================================================================
# Phase 5: Project Files Verification
# ============================================================================
Write-Header "Phase 5: Project Files Verification"

$requiredFiles = @(
    "backend/requirements.txt",
    "backend/app/main.py",
    "frontend/package.json",
    "frontend/src/main.tsx",
    "deploy-to-azure.ps1",
    "DETAILED_DEPLOYMENT_PLAN.md"
)

foreach ($file in $requiredFiles) {
    $fileExists = Test-Path $file
    if ($fileExists) {
        Write-Success "Found: $file"
        $script:testsPassed++
    }
    else {
        Write-Error-Custom "Missing: $file"
        $script:testsFailed++
    }
}

# ============================================================================
# Phase 6: System Environment Checks
# ============================================================================
Write-Header "Phase 6: System Environment Checks"

Write-Info "Checking internet connectivity..."
try {
    $null = Invoke-WebRequest -Uri "https://www.azure.com" `
        -UseBasicParsing -TimeoutSec 5
    Write-Success "Internet connectivity verified"
    $script:testsPassed++
}
catch {
    Write-Warn "Could not reach Azure website"
    $script:testsWarning++
}

$psVersion = $PSVersionTable.PSVersion
Write-Info "PowerShell version: $($psVersion.Major).$($psVersion.Minor)"
if ($psVersion.Major -ge 5) {
    Write-Success "PowerShell 5+ detected"
    $script:testsPassed++
}
else {
    Write-Warn "PowerShell 5.1+ recommended"
    $script:testsWarning++
}

# ============================================================================
# Summary Report
# ============================================================================
Write-Header "Deployment Readiness Report"

Write-Host ""
Write-Host "Test Results Summary:" -ForegroundColor Cyan
Write-Host "  PASSED:   $($script:testsPassed)" -ForegroundColor Green
Write-Host "  WARNINGS: $($script:testsWarning)" -ForegroundColor Yellow
Write-Host "  FAILED:   $($script:testsFailed)" -ForegroundColor Red
Write-Host ""

if ($script:testsFailed -eq 0 -and $script:testsWarning -eq 0) {
    Write-Success "All checks passed! Ready to deploy."
    Write-Info "Next: Run .\deploy-to-azure.ps1"
    exit 0
}
elseif ($script:testsFailed -eq 0) {
    Write-Warn "Some warnings, but should work."
    Write-Info "Run: .\deploy-to-azure.ps1"
    exit 0
}
else {
    Write-Error-Custom "Fix errors before deploying."
    Write-Info "Review errors and run check again."
    exit 1
}
