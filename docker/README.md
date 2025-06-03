# PollenPal Docker Setup 🐳

This directory contains Docker configuration for running PollenPal API in containers.

## Quick Start

### Using Deployment Scripts (Easiest)

**Linux/macOS:**
```bash
# Development deployment
./scripts/deploy.sh

# Production deployment with nginx
./scripts/deploy.sh prod --build

# Rebuild from scratch
./scripts/deploy.sh dev --rebuild
```

**Windows (PowerShell - Recommended):**
```powershell
# Development deployment
.\scripts\deploy.ps1

# Production deployment with nginx
.\scripts\deploy.ps1 prod -Build

# Rebuild from scratch
.\scripts\deploy.ps1 dev -Rebuild
```

**Windows (Command Prompt):**
```cmd
REM Development deployment
scripts\deploy.bat

REM Production deployment with nginx
scripts\deploy.bat prod --build

REM Rebuild from scratch
scripts\deploy.bat dev --rebuild
```

### Using Docker Compose (Manual)

```bash
# Build and start the API
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f pollenpal-api

# Stop the services
docker-compose down
```

The API will be available at `http://localhost:3000`

### Using Docker directly

```bash
# Build the image
docker build -t pollenpal-api .

# Run the container
docker run -d \
  --name pollenpal-api \
  -p 3000:3000 \
  --restart unless-stopped \
  pollenpal-api

# View logs
docker logs -f pollenpal-api

# Stop and remove
docker stop pollenpal-api
docker rm pollenpal-api
```

## Configuration

### Environment Variables

The container supports the following environment variables:

- `PYTHONUNBUFFERED=1` - Ensures Python output is sent straight to terminal
- `PORT` - Override the default port (3000)

### Health Checks

The container includes built-in health checks that monitor the `/health` endpoint:

- **Interval**: 30 seconds
- **Timeout**: 30 seconds  
- **Retries**: 3
- **Start Period**: 5 seconds

### Security

The container runs as a non-root user (`pollenpal`) for enhanced security.

## Production Deployment

### With Nginx Reverse Proxy

Uncomment the nginx service in `docker-compose.yml` and configure the nginx files in the `nginx/` directory:

```bash
# Enable nginx proxy
vim docker-compose.yml  # Uncomment nginx service

# Start with nginx
docker-compose up -d --build
```

### Resource Limits

For production, consider adding resource limits:

```yaml
services:
  pollenpal-api:
    # ... existing config
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Scaling

Scale the API service:

```bash
# Scale to 3 instances
docker-compose up -d --scale pollenpal-api=3

# With load balancer, you'll need to configure nginx accordingly
```

## Development

### Development with Volume Mounts

For development with live code reloading:

```yaml
services:
  pollenpal-api:
    # ... existing config
    volumes:
      - ./src:/app/src:ro
    command: ["uv", "run", "uvicorn", "pollenpal.api.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]
```

### Building Different Variants

```bash
# Build with specific Python version
docker build --build-arg PYTHON_VERSION=3.12 -t pollenpal-api:py312 .

# Build development version with dev dependencies
docker build --target development -t pollenpal-api:dev .
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 3000
   lsof -i :3000
   
   # Use different port
   docker-compose up -d -p 3001:3000
   ```

2. **Build failures**
   ```bash
   # Clean build without cache
   docker-compose build --no-cache
   
   # Remove old images
   docker system prune -a
   ```

3. **Health check failures**
   ```bash
   # Check container logs
   docker-compose logs pollenpal-api
   
   # Test health endpoint manually
   docker exec pollenpal-api curl http://localhost:3000/health
   ```

### Logs and Monitoring

```bash
# Follow logs
docker-compose logs -f

# Check container stats
docker stats pollenpal-api

# Inspect container
docker inspect pollenpal-api
```

## API Endpoints

Once running, the following endpoints are available:

- **API Root**: `http://localhost:3000/`
- **Documentation**: `http://localhost:3000/docs`
- **Health Check**: `http://localhost:3000/health`
- **Pollen Data**: `http://localhost:3000/pollen/{city}`

## Support

For issues with the Docker setup, please check:

1. Docker and Docker Compose versions are up to date
2. Port 3000 is available
3. Container logs for error messages
4. Health check status

Example API test:
```bash
curl http://localhost:3000/pollen/London
``` 