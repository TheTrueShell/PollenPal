@echo off
setlocal enabledelayedexpansion

REM PollenPal Docker Deployment Script for Windows
REM Usage: scripts\deploy.bat [dev|prod] [--build|--rebuild]

REM Default values
set ENVIRONMENT=dev
set BUILD_FLAG=
set COMPOSE_FILE=docker-compose.yml

REM Parse arguments
:parse_args
if "%~1"=="" goto :check_docker
if /i "%~1"=="dev" (
    set ENVIRONMENT=dev
    set COMPOSE_FILE=docker-compose.yml
    shift
    goto :parse_args
)
if /i "%~1"=="development" (
    set ENVIRONMENT=dev
    set COMPOSE_FILE=docker-compose.yml
    shift
    goto :parse_args
)
if /i "%~1"=="prod" (
    set ENVIRONMENT=prod
    set COMPOSE_FILE=docker-compose.prod.yml
    shift
    goto :parse_args
)
if /i "%~1"=="production" (
    set ENVIRONMENT=prod
    set COMPOSE_FILE=docker-compose.prod.yml
    shift
    goto :parse_args
)
if /i "%~1"=="--build" (
    set BUILD_FLAG=--build
    shift
    goto :parse_args
)
if /i "%~1"=="--rebuild" (
    set BUILD_FLAG=--build
    set NO_CACHE_FLAG=--no-cache
    shift
    goto :parse_args
)
if /i "%~1"=="-h" goto :show_usage
if /i "%~1"=="--help" goto :show_usage
echo [ERROR] Unknown option: %~1
goto :show_usage

:show_usage
echo Usage: %0 [dev^|prod] [--build^|--rebuild]
echo.
echo Options:
echo   dev     - Deploy development environment (default)
echo   prod    - Deploy production environment with nginx
echo   --build - Build images before deploying
echo   --rebuild - Rebuild images from scratch (no cache)
echo.
echo Examples:
echo   %0                    # Deploy dev environment
echo   %0 prod --build       # Build and deploy production
echo   %0 dev --rebuild      # Rebuild dev from scratch
exit /b 0

:check_docker
REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] docker-compose is not installed. Please install it and try again.
    exit /b 1
)

echo [INFO] Deploying PollenPal API in %ENVIRONMENT% mode...
echo [INFO] Using compose file: %COMPOSE_FILE%

REM Check if compose file exists
if not exist "%COMPOSE_FILE%" (
    echo [ERROR] Compose file %COMPOSE_FILE% not found!
    exit /b 1
)

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker-compose -f "%COMPOSE_FILE%" down

REM Build and start services
if not "%BUILD_FLAG%"=="" (
    if not "%NO_CACHE_FLAG%"=="" (
        echo [INFO] Rebuilding images from scratch...
        docker-compose -f "%COMPOSE_FILE%" build %NO_CACHE_FLAG%
        docker-compose -f "%COMPOSE_FILE%" up -d
    ) else (
        echo [INFO] Building images...
        docker-compose -f "%COMPOSE_FILE%" up -d %BUILD_FLAG%
    )
) else (
    echo [INFO] Starting services...
    docker-compose -f "%COMPOSE_FILE%" up -d
)

REM Wait for services to be healthy
echo [INFO] Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if API is responding
if /i "%ENVIRONMENT%"=="prod" (
    set API_URL=http://localhost/health
) else (
    set API_URL=http://localhost:3000/health
)

echo [INFO] Checking API health at !API_URL!...
set /a attempts=0
:health_check_loop
set /a attempts+=1
curl -f -s "!API_URL!" >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] API is healthy!
    goto :show_status
)
if !attempts! geq 30 (
    echo [ERROR] API health check failed after 30 attempts
    echo [INFO] Checking container logs...
    docker-compose -f "%COMPOSE_FILE%" logs --tail=20 pollenpal-api
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto :health_check_loop

:show_status
REM Show running containers
echo [INFO] Running containers:
docker-compose -f "%COMPOSE_FILE%" ps

REM Show useful URLs
echo [SUCCESS] PollenPal API deployed successfully!
echo.
echo Available endpoints:
if /i "%ENVIRONMENT%"=="prod" (
    echo   • API Root:        http://localhost/
    echo   • Documentation:   http://localhost/docs
    echo   • Health Check:    http://localhost/health
    echo   • Example:         http://localhost/pollen/London
) else (
    echo   • API Root:        http://localhost:3000/
    echo   • Documentation:   http://localhost:3000/docs
    echo   • Health Check:    http://localhost:3000/health
    echo   • Example:         http://localhost:3000/pollen/London
)
echo.
echo Useful commands:
echo   • View logs:       docker-compose -f %COMPOSE_FILE% logs -f
echo   • Stop services:   docker-compose -f %COMPOSE_FILE% down
echo   • Restart:         docker-compose -f %COMPOSE_FILE% restart
echo.

REM Test API with a sample request
echo [INFO] Testing API with sample request...
set TEST_URL=!API_URL:/health=!
curl -f -s "!TEST_URL!/pollen/London" | findstr /r "." >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] Sample API request successful!
) else (
    echo [WARNING] Sample API request failed, but health check passed. API might still be initialising.
)

echo.
echo Press any key to exit...
pause >nul 