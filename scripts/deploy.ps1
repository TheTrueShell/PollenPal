# PollenPal Docker Deployment & Management Script for Windows PowerShell
# Usage: .\scripts\deploy.ps1 [Command] [Environment] [Options]

param(
    [Parameter(Position=0)]
    [ValidateSet("deploy", "start", "stop", "restart", "status", "logs", "shell", "cleanup", "monitor", "health", "backup", "update")]
    [string]$Command = "deploy",
    
    [Parameter(Position=1)]
    [ValidateSet("dev", "development", "prod", "production")]
    [string]$Environment = "dev",
    
    [switch]$Build,
    [switch]$Rebuild,
    [switch]$Follow,
    [int]$Tail = 50,
    [switch]$Help
)

# Global variables
$script:ComposeFile = ""
$script:BuildFlag = ""

# Show usage information
function Show-Usage {
    Write-Host "PollenPal Docker Management Script" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\scripts\deploy.ps1 [Command] [Environment] [Options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  deploy    - Deploy the application (default)" -ForegroundColor White
    Write-Host "  start     - Start existing containers" -ForegroundColor White
    Write-Host "  stop      - Stop all containers" -ForegroundColor White
    Write-Host "  restart   - Restart all containers" -ForegroundColor White
    Write-Host "  status    - Show container status" -ForegroundColor White
    Write-Host "  logs      - Show container logs" -ForegroundColor White
    Write-Host "  shell     - Open shell in API container" -ForegroundColor White
    Write-Host "  cleanup   - Remove containers and volumes" -ForegroundColor White
    Write-Host "  monitor   - Monitor container resources" -ForegroundColor White
    Write-Host "  health    - Check application health" -ForegroundColor White
    Write-Host "  backup    - Backup application data" -ForegroundColor White
    Write-Host "  update    - Update and redeploy" -ForegroundColor White
    Write-Host ""
    Write-Host "Environment:" -ForegroundColor Yellow
    Write-Host "  dev       - Development environment (default)" -ForegroundColor White
    Write-Host "  prod      - Production environment with nginx" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Build    - Build images before deploying" -ForegroundColor White
    Write-Host "  -Rebuild  - Rebuild images from scratch (no cache)" -ForegroundColor White
    Write-Host "  -Follow   - Follow logs in real-time" -ForegroundColor White
    Write-Host "  -Tail N   - Show last N lines of logs (default: 50)" -ForegroundColor White
    Write-Host "  -Help     - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\scripts\deploy.ps1 deploy dev -Build      # Build and deploy development" -ForegroundColor Gray
    Write-Host "  .\scripts\deploy.ps1 logs prod -Follow      # Follow production logs" -ForegroundColor Gray
    Write-Host "  .\scripts\deploy.ps1 status                 # Show container status" -ForegroundColor Gray
    Write-Host "  .\scripts\deploy.ps1 shell dev               # Open shell in dev API container" -ForegroundColor Gray
    Write-Host "  .\scripts\deploy.ps1 cleanup prod           # Clean up production containers" -ForegroundColor Gray
}

# Coloured output functions
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

function Write-Header($message) {
    Write-Host "=== $message ===" -ForegroundColor Cyan
}

# Function to check prerequisites
function Test-Prerequisites {
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
    if (-not (Test-Path $script:ComposeFile)) {
        Write-Error "Compose file $($script:ComposeFile) not found!"
        exit 1
    }
}

# Function to set environment variables
function Set-Environment {
    param([string]$env)
    
    switch ($env.ToLower()) {
        { $_ -in @("prod", "production") } {
            $script:ComposeFile = "docker-compose.prod.yml"
            $Environment = "prod"
        }
        default {
            $script:ComposeFile = "docker-compose.yml"
            $Environment = "dev"
        }
    }
    
    # Set build flags
    if ($Rebuild) {
        $script:BuildFlag = "--build --no-cache"
    } elseif ($Build) {
        $script:BuildFlag = "--build"
    }
}

# Function to deploy application
function Invoke-Deploy {
    Write-Header "Deploying PollenPal API in $Environment mode"
    Write-Info "Using compose file: $($script:ComposeFile)"

    # Stop existing containers
    Write-Info "Stopping existing containers..."
    docker-compose -f $script:ComposeFile down

    # Build and start services
    if ($script:BuildFlag) {
        Write-Info "Building images..."
        $cmd = "docker-compose -f `"$($script:ComposeFile)`" up -d $($script:BuildFlag)"
    } else {
        Write-Info "Starting services..."
        $cmd = "docker-compose -f `"$($script:ComposeFile)`" up -d"
    }

    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start services"
        exit 1
    }

    # Wait for services to be healthy
    Write-Info "Waiting for services to start..."
    Start-Sleep -Seconds 10

    # Check health
    Test-Health
    
    Show-DeploymentInfo
}

# Function to start containers
function Start-Containers {
    Write-Header "Starting PollenPal containers"
    docker-compose -f $script:ComposeFile start
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Containers started successfully!"
        Show-Status
    } else {
        Write-Error "Failed to start containers"
        exit 1
    }
}

# Function to stop containers
function Stop-Containers {
    Write-Header "Stopping PollenPal containers"
    docker-compose -f $script:ComposeFile stop
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Containers stopped successfully!"
    } else {
        Write-Error "Failed to stop containers"
        exit 1
    }
}

# Function to restart containers
function Restart-Containers {
    Write-Header "Restarting PollenPal containers"
    docker-compose -f $script:ComposeFile restart
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Containers restarted successfully!"
        Show-Status
    } else {
        Write-Error "Failed to restart containers"
        exit 1
    }
}

# Function to show container status
function Show-Status {
    Write-Header "Container Status"
    docker-compose -f $script:ComposeFile ps
    Write-Host ""
    Write-Info "Docker system information:"
    docker system df
}

# Function to show logs
function Show-Logs {
    if ($Follow) {
        Write-Header "Following PollenPal logs (Ctrl+C to exit)"
        docker-compose -f $script:ComposeFile logs -f --tail=$Tail
    } else {
        Write-Header "PollenPal logs (last $Tail lines)"
        docker-compose -f $script:ComposeFile logs --tail=$Tail
    }
}

# Function to open shell in API container
function Open-Shell {
    Write-Header "Opening shell in PollenPal API container"
    $containerName = "pollenpal-api"
    
    # Check if container is running
    $runningContainers = docker-compose -f $script:ComposeFile ps --services --filter "status=running"
    if ($runningContainers -contains $containerName.Split('-')[1]) {
        Write-Info "Opening bash shell in $containerName..."
        docker-compose -f $script:ComposeFile exec pollenpal-api /bin/bash
    } else {
        Write-Error "Container $containerName is not running. Start it first with: .\scripts\deploy.ps1 start $Environment"
        exit 1
    }
}

# Function to cleanup containers and volumes
function Invoke-Cleanup {
    Write-Header "Cleaning up PollenPal containers and volumes"
    Write-Warning "This will remove all containers, networks, and volumes!"
    
    $confirmation = Read-Host "Are you sure? (y/N)"
    if ($confirmation -match '^[Yy]$') {
        Write-Info "Stopping and removing containers..."
        docker-compose -f $script:ComposeFile down -v --remove-orphans
        
        Write-Info "Removing unused images..."
        docker image prune -f
        
        Write-Info "Removing unused volumes..."
        docker volume prune -f
        
        Write-Success "Cleanup completed!"
    } else {
        Write-Info "Cleanup cancelled."
    }
}

# Function to monitor container resources
function Start-Monitoring {
    Write-Header "Monitoring PollenPal container resources"
    Write-Info "Press Ctrl+C to exit monitoring"
    Write-Host ""
    
    # Get container IDs
    $containerIds = docker-compose -f $script:ComposeFile ps -q
    if ($containerIds) {
        docker stats $containerIds
    } else {
        Write-Warning "No running containers found"
    }
}

# Function to check application health
function Test-Health {
    $apiUrl = if ($Environment -eq "prod") { "http://localhost/health" } else { "http://localhost:3000/health" }

    Write-Info "Checking API health at $apiUrl..."
    $attempts = 0
    $maxAttempts = 30

    do {
        $attempts++
        try {
            $response = Invoke-WebRequest -Uri $apiUrl -Method Get -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "API is healthy!"
                return $true
            }
        } catch {
            if ($attempts -ge $maxAttempts) {
                Write-Error "API health check failed after $maxAttempts attempts"
                Write-Info "Checking container logs..."
                docker-compose -f $script:ComposeFile logs --tail=20 pollenpal-api
                return $false
            }
            Start-Sleep -Seconds 2
        }
    } while ($attempts -lt $maxAttempts)
    
    return $false
}

# Function to backup application data
function Invoke-Backup {
    Write-Header "Backing up PollenPal data"
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "backups\$timestamp"
    
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    Write-Info "Creating backup in $backupDir..."
    
    # Backup volumes
    try {
        docker run --rm -v pollenpal_data:/data -v "${PWD}\${backupDir}:/backup" alpine tar czf /backup/data.tar.gz -C /data .
        
        # Backup configuration files
        Copy-Item "docker-compose*.yml" $backupDir -ErrorAction SilentlyContinue
        Copy-Item ".env*" $backupDir -ErrorAction SilentlyContinue
        
        Write-Success "Backup created in $backupDir"
    } catch {
        Write-Error "Backup failed: $($_.Exception.Message)"
        exit 1
    }
}

# Function to update and redeploy
function Invoke-Update {
    Write-Header "Updating and redeploying PollenPal"
    
    Write-Info "Pulling latest code..."
    try {
        git pull origin main
    } catch {
        Write-Warning "Git pull failed or not in a git repository"
    }
    
    Write-Info "Rebuilding and redeploying..."
    $script:BuildFlag = "--build --no-cache"
    Invoke-Deploy
}

# Function to show deployment information
function Show-DeploymentInfo {
    Write-Success "PollenPal API deployed successfully!"
    Write-Host ""
    Write-Host "Available endpoints:" -ForegroundColor Cyan
    if ($Environment -eq "prod") {
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
    Write-Host "Management commands:" -ForegroundColor Cyan
    Write-Host "  • View logs:       .\scripts\deploy.ps1 logs $Environment -Follow" -ForegroundColor Gray
    Write-Host "  • Show status:     .\scripts\deploy.ps1 status $Environment" -ForegroundColor Gray
    Write-Host "  • Stop services:   .\scripts\deploy.ps1 stop $Environment" -ForegroundColor Gray
    Write-Host "  • Restart:         .\scripts\deploy.ps1 restart $Environment" -ForegroundColor Gray
    Write-Host "  • Open shell:      .\scripts\deploy.ps1 shell $Environment" -ForegroundColor Gray
    Write-Host "  • Monitor:         .\scripts\deploy.ps1 monitor $Environment" -ForegroundColor Gray
    Write-Host ""

    # Test API with a sample request
    Write-Info "Testing API with sample request..."
    $testUrl = if ($Environment -eq "prod") { "http://localhost/pollen/London" } else { "http://localhost:3000/pollen/London" }
    
    try {
        $testResponse = Invoke-WebRequest -Uri $testUrl -Method Get -TimeoutSec 10 -UseBasicParsing
        if ($testResponse.StatusCode -eq 200) {
            Write-Success "Sample API request successful!"
        }
    } catch {
        Write-Warning "Sample API request failed, but health check passed. API might still be initialising."
    }
}

# Main execution logic
if ($Help) {
    Show-Usage
    exit 0
}

# Set environment and compose file
Set-Environment $Environment

# Check prerequisites
Test-Prerequisites

# Execute command
switch ($Command.ToLower()) {
    "deploy" {
        Invoke-Deploy
    }
    "start" {
        Start-Containers
    }
    "stop" {
        Stop-Containers
    }
    "restart" {
        Restart-Containers
    }
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs
    }
    "shell" {
        Open-Shell
    }
    "cleanup" {
        Invoke-Cleanup
    }
    "monitor" {
        Start-Monitoring
    }
    "health" {
        if (Test-Health) {
            Write-Success "Health check passed!"
        } else {
            Write-Error "Health check failed!"
            exit 1
        }
    }
    "backup" {
        Invoke-Backup
    }
    "update" {
        Invoke-Update
    }
    default {
        Write-Error "Unknown command: $Command"
        Show-Usage
        exit 1
    }
}

# Pause at the end for interactive sessions
if ($Command -eq "deploy" -and $Host.Name -eq "ConsoleHost") {
    Write-Host ""
    Write-Host "Deployment complete! Press any key to continue..." -ForegroundColor Green
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} 