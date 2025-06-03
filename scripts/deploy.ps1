# PollenPal Docker Deployment Script for Windows PowerShell
# Usage: .\scripts\deploy.ps1 [dev|prod] [-Build] [-Rebuild]

param(
    [Parameter(Position=0)]
    [ValidateSet("dev", "development", "prod", "production")]
    [string]$Environment = "dev",
    
    [switch]$Build,
    [switch]$Rebuild,
    [switch]$Help
)

# Show usage information
function Show-Usage {
    Write-Host "Usage: .\scripts\deploy.ps1 [dev|prod] [-Build] [-Rebuild]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor Cyan
    Write-Host "  dev/development  - Deploy development environment (default)" -ForegroundColor White
    Write-Host "  prod/production  - Deploy production environment with nginx" -ForegroundColor White
    Write-Host "  -Build           - Build images before deploying" -ForegroundColor White
    Write-Host "  -Rebuild         - Rebuild images from scratch (no cache)" -ForegroundColor White
    Write-Host "  -Help            - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\scripts\deploy.ps1                    # Deploy dev environment" -ForegroundColor Gray
    Write-Host "  .\scripts\deploy.ps1 prod -Build        # Build and deploy production" -ForegroundColor Gray
    Write-Host "  .\scripts\deploy.ps1 dev -Rebuild       # Rebuild dev from scratch" -ForegroundColor Gray
}

# Colored output functions
function Write-Info($message) {
    Write-Host "[INFO] $message" -ForegroundColor Blue
}

function Write-Success($message) {
    Write-Host "[SUCCESS] $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

# Set environment variables
$env:ENVIRONMENT = if ($Environment -in @("prod", "production")) { "prod" } else { "dev" }
$ComposeFile = if ($env:ENVIRONMENT -eq "prod") { "docker-compose.prod.yml" } else { "docker-compose.yml" }

# Determine build flags
$BuildFlag = ""
if ($Rebuild) {
    $BuildFlag = "--build --no-cache"
} elseif ($Build) {
    $BuildFlag = "--build"
}

Write-Info "Deploying PollenPal API in $($env:ENVIRONMENT) mode..."
Write-Info "Using compose file: $ComposeFile"

# Check if Docker is running
try {
    $null = docker info 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker is not running"
    }
} catch {
    Write-Error "Docker is not running. Please start Docker and try again."
    exit 1
}

# Check if docker-compose is available
try {
    $null = docker-compose --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "docker-compose not found"
    }
} catch {
    Write-Error "docker-compose is not installed. Please install it and try again."
    exit 1
}

# Check if compose file exists
if (-not (Test-Path $ComposeFile)) {
    Write-Error "Compose file $ComposeFile not found!"
    exit 1
}

# Stop existing containers
Write-Info "Stopping existing containers..."
docker-compose -f $ComposeFile down

# Build and start services
if ($BuildFlag) {
    Write-Info "Building images..."
    $cmd = "docker-compose -f `"$ComposeFile`" up -d $BuildFlag"
} else {
    Write-Info "Starting services..."
    $cmd = "docker-compose -f `"$ComposeFile`" up -d"
}

Invoke-Expression $cmd
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start services"
    exit 1
}

# Wait for services to be healthy
Write-Info "Waiting for services to start..."
Start-Sleep -Seconds 10

# Check if API is responding
$ApiUrl = if ($env:ENVIRONMENT -eq "prod") { "http://localhost/health" } else { "http://localhost:3000/health" }

Write-Info "Checking API health at $ApiUrl..."
$attempts = 0
$maxAttempts = 30

do {
    $attempts++
    try {
        $response = Invoke-WebRequest -Uri $ApiUrl -Method Get -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Success "API is healthy!"
            break
        }
    } catch {
        if ($attempts -ge $maxAttempts) {
            Write-Error "API health check failed after $maxAttempts attempts"
            Write-Info "Checking container logs..."
            docker-compose -f $ComposeFile logs --tail=20 pollenpal-api
            exit 1
        }
        Start-Sleep -Seconds 2
    }
} while ($attempts -lt $maxAttempts)

# Show running containers
Write-Info "Running containers:"
docker-compose -f $ComposeFile ps

# Show useful URLs
Write-Success "PollenPal API deployed successfully!"
Write-Host ""
Write-Host "Available endpoints:" -ForegroundColor Cyan
if ($env:ENVIRONMENT -eq "prod") {
    Write-Host "  • API Root:        http://localhost/" -ForegroundColor White
    Write-Host "  • Documentation:   http://localhost/docs" -ForegroundColor White
    Write-Host "  • Health Check:    http://localhost/health" -ForegroundColor White
    Write-Host "  • Example:         http://localhost/pollen/London" -ForegroundColor White
} else {
    Write-Host "  • API Root:        http://localhost:3000/" -ForegroundColor White
    Write-Host "  • Documentation:   http://localhost:3000/docs" -ForegroundColor White
    Write-Host "  • Health Check:    http://localhost:3000/health" -ForegroundColor White
    Write-Host "  • Example:         http://localhost:3000/pollen/London" -ForegroundColor White
}
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  • View logs:       docker-compose -f $ComposeFile logs -f" -ForegroundColor Gray
Write-Host "  • Stop services:   docker-compose -f $ComposeFile down" -ForegroundColor Gray
Write-Host "  • Restart:         docker-compose -f $ComposeFile restart" -ForegroundColor Gray
Write-Host ""

# Test API with a sample request
Write-Info "Testing API with sample request..."
$TestUrl = $ApiUrl -replace "/health", "/pollen/London"
try {
    $testResponse = Invoke-WebRequest -Uri $TestUrl -Method Get -TimeoutSec 10 -UseBasicParsing
    if ($testResponse.StatusCode -eq 200) {
        Write-Success "Sample API request successful!"
    }
} catch {
    Write-Warning "Sample API request failed, but health check passed. API might still be initialising."
}

Write-Host ""
Write-Host "Deployment complete! Press any key to continue..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 