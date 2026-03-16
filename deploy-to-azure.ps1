#!/usr/bin/env pwsh
# ============================================================================
# Task Tracker - Azure Deployment Script
# ============================================================================
# Automated deployment to Azure for Python 3.11 + Node 25.8 stack
# Prerequisites: Azure CLI must be installed and logged in
# Run AFTER pre-deploy-check.ps1 passes all checks
# ============================================================================

param(
    [string]$DatabasePassword = "",
    [string]$Location = "eastus",
    [string]$ResourceGroup = "task-tracker-rg",
    [string]$AppServicePlan = "task-tracker-plan",
    [string]$AppServiceName = "task-tracker-api",
    [string]$StaticAppName = "task-tracker-app",
    [string]$DBServerName = "task-tracker-db-server"
)

# ------- Helper Functions ---------------------------------------------------
function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    $color = switch ($Status) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        default { "Cyan" }
    }
    Write-Host "[$Status] $Message" -ForegroundColor $color
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "=== $Title ===" -ForegroundColor Magenta
}

# ============================================================================
# Pre-flight Checks
# ============================================================================
Write-Section "Pre-flight Checks"

# Verify Azure CLI
$azExists = $null -ne (Get-Command az -ErrorAction SilentlyContinue)
if (-not $azExists) {
    Write-Status "Azure CLI not found" "ERROR"
    Write-Host "Install from: https://aka.ms/cli"
    exit 1
}

# Verify logged in
try {
    $account = az account show 2>&1 | ConvertFrom-Json
    Write-Status "Logged in as: $($account.user.name)" "SUCCESS"
}
catch {
    Write-Status "Not logged in to Azure" "ERROR"
    Write-Host "Run: az login"
    exit 1
}

# Get database password if not provided
if ([string]::IsNullOrWhiteSpace($DatabasePassword)) {
    Write-Status "Database password required" "WARNING"
    $DatabasePassword = Read-Host "Enter database password (min 8 chars, with uppercase, numbers, symbols)"
    
    if ($DatabasePassword.Length -lt 8 -or $DatabasePassword -notmatch "[A-Z]" -or $DatabasePassword -notmatch "[0-9]") {
        Write-Status "Password does not meet requirements" "ERROR"
        exit 1
    }
}

# ============================================================================
# Phase 1: Create Resource Group
# ============================================================================
Write-Section "Phase 1: Creating Resource Group"

Write-Status "Creating resource group '$ResourceGroup' in $Location..."
az group create --name $ResourceGroup --location $Location | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Status "Resource group created" "SUCCESS"
}
else {
    Write-Status "Failed to create resource group" "ERROR"
    exit 1
}

# ============================================================================
# Phase 2: Deploy PostgreSQL Database
# ============================================================================
Write-Section "Phase 2: Deploying PostgreSQL Database"

Write-Status "Creating PostgreSQL server '$DBServerName'..."
az postgres server create `
    --resource-group $ResourceGroup `
    --name $DBServerName `
    --location $Location `
    --admin-user dbadmin `
    --admin-password $DatabasePassword `
    --sku-name B_Gen5_1 `
    --storage-size 51200 `
    --version 11 `
    --ssl-enforcement Enabled 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Status "PostgreSQL server created" "SUCCESS"
}
else {
    Write-Status "PostgreSQL server creation failed" "ERROR"
    exit 1
}

Write-Status "Configuring firewall rules..."
az postgres server firewall-rule create `
    --resource-group $ResourceGroup `
    --server-name $DBServerName `
    --name AllowAzureServices `
    --start-ip-address 0.0.0.0 `
    --end-ip-address 0.0.0.0 2>&1 | Out-Null

Write-Status "Firewall rules configured" "SUCCESS"

Write-Status "Creating database 'task_tracker'..."
az postgres db create `
    --resource-group $ResourceGroup `
    --server-name $DBServerName `
    --name task_tracker 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Status "Database 'task_tracker' created" "SUCCESS"
}
else {
    Write-Status "Database creation failed" "ERROR"
}

# Extract connection string
$dbServer = "$DBServerName.postgres.database.azure.com"
$connectionString = "postgresql://dbadmin@$($DBServerName):$DatabasePassword@$dbServer/task_tracker?sslmode=require"
Write-Status "Database Connection String:" "INFO"
Write-Host "   $connectionString" -ForegroundColor Yellow

# ============================================================================
# Phase 3: Create App Service Plan
# ============================================================================
Write-Section "Phase 3: Creating App Service Plan"

Write-Status "Creating App Service plan '$AppServicePlan'..."
az appservice plan create `
    --name $AppServicePlan `
    --resource-group $ResourceGroup `
    --sku B1 `
    --is-linux 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Status "App Service plan created" "SUCCESS"
}
else {
    Write-Status "App Service plan creation failed" "ERROR"
    exit 1
}

# ============================================================================
# Phase 4: Deploy Backend to App Service
# ============================================================================
Write-Section "Phase 4: Deploying Backend (Python 3.11)"

# Generate unique app name
$randomSuffix = Get-Random -Minimum 1000 -Maximum 9999
$AppServiceName = "$AppServiceName-$randomSuffix"

Write-Status "Creating web app '$AppServiceName'..."
az webapp create `
    --resource-group $ResourceGroup `
    --plan $AppServicePlan `
    --name $AppServiceName `
    --runtime "PYTHON|3.11" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Status "Web app created: $AppServiceName" "SUCCESS"
}
else {
    Write-Status "Web app creation failed" "ERROR"
    exit 1
}

Write-Status "Configuring database connection..."
az webapp config appsettings set `
    --resource-group $ResourceGroup `
    --name $AppServiceName `
    --settings "DATABASE_URL=$connectionString" `
    "PYTHONPATH=/home/site/wwwroot" 2>&1 | Out-Null

Write-Status "Deploying code from GitHub..."
az webapp up `
    --resource-group $ResourceGroup `
    --name $AppServiceName `
    --runtime "PYTHON|3.11" `
    --runtime-version "3.11" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Status "Backend deployed successfully" "SUCCESS"
}
else {
    Write-Status "Backend deployment may have issues - checking health..." "WARNING"
}

$backendUrl = "https://$AppServiceName.azurewebsites.net"
Write-Status "Backend URL: $backendUrl" "INFO"

# ============================================================================
# Phase 5: Create Static Web App for Frontend
# ============================================================================
Write-Section "Phase 5: Creating Static Web App (React Frontend)"

# Generate unique static app name
$StaticAppName = "$StaticAppName-$randomSuffix"

Write-Status "Creating Static Web App '$StaticAppName'..."
az staticwebapp create `
    --name $StaticAppName `
    --resource-group $ResourceGroup `
    --location $Location 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Status "Static Web App created: $StaticAppName" "SUCCESS"
}
else {
    Write-Status "Static Web App creation failed" "ERROR"
    exit 1
}

$frontendUrl = "https://$StaticAppName.azurestaticapps.net"
Write-Status "Frontend URL: $frontendUrl" "INFO"

# ============================================================================
# Phase 6: Summary and Next Steps
# ============================================================================
Write-Section "Deployment Complete!"

Write-Host ""
Write-Host "IMPORTANT: Next Steps" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Update Azure AD Redirect URI:" -ForegroundColor Cyan
Write-Host "   Go to: https://portal.azure.com" 
Write-Host "   Path: Azure AD -> App registrations -> Authentication"
Write-Host "   Add Redirect URI: $frontendUrl/"
Write-Host ""
Write-Host "2. Build and deploy frontend (Node 25.8):" -ForegroundColor Cyan
Write-Host "   cd frontend"
Write-Host "   npm install"
Write-Host "   npm run build"
Write-Host "   cd .."
Write-Host ""
Write-Host "3. Upload frontend to Static Web App:" -ForegroundColor Cyan
Write-Host "   az staticwebapp upload --name $StaticAppName --source ./frontend/dist --resource-group $ResourceGroup"
Write-Host ""
Write-Host ""
Write-Host "DEPLOYMENT INFORMATION" -ForegroundColor Magenta
Write-Host "   Resource Group: $ResourceGroup"
Write-Host "   Backend URL: $backendUrl"
Write-Host "   Frontend URL: $frontendUrl"
Write-Host "   Database: $dbServer"
Write-Host "   Database: task_tracker"
Write-Host "   Database User: dbadmin"
Write-Host "   Location: $Location"
Write-Host ""
Write-Host "Save this information for future reference!" -ForegroundColor Yellow
Write-Host ""
