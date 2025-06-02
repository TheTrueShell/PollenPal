# Docker Setup Guide 🐳

Quick guide to get PollenPal API running with Docker.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.10+ (for running scripts)

## Quick Commands

```bash
# Development
python scripts/run.py dev:docker    # Start in Docker with hot reload
make docker-dev                     # Alternative using Makefile

# Production
python scripts/run.py build         # Build production image
python scripts/run.py deploy        # Deploy with health checks
make build && make deploy           # Alternative using Makefile

# Management
python scripts/run.py status        # Check service status
python scripts/run.py logs          # View logs
python scripts/run.py health        # Health check
python scripts/run.py stop          # Stop all services
```

## Docker Compose Profiles

### Development Profile (`dev`)
```bash
docker-compose --profile dev up
```
- Hot reload enabled
- Port 3000 exposed
- Source code mounted as volumes
- Single API instance

### Production Profile (`prod`)
```bash
docker-compose --profile prod up
```
- Nginx reverse proxy
- Port 80/443 exposed
- Multiple API workers
- Health checks enabled
- Automatic restarts

### With Caching (`cache`)
```bash
docker-compose --profile prod --profile cache up
```
- Adds Redis for caching
- Improved performance
- Session storage

## Manual Docker Commands

### Build Image
```bash
# Development build
docker build --target builder -t pollenpal:dev .

# Production build
docker build --target production -t pollenpal:prod .
```

### Run Container
```bash
# Development
docker run -p 3000:3000 -v $(pwd)/src:/app/src pollenpal:dev

# Production
docker run -p 8000:8000 pollenpal:prod
```

### Health Check
```bash
# Check if container is healthy
docker ps --filter "name=pollenpal"

# Manual health check
curl http://localhost:8000/health
```

## Environment Configuration

Copy and configure environment:
```bash
cp env.example .env
# Edit .env with your settings
```

Key Docker environment variables:
```bash
POLLENPAL_ENV=production
PROD_API_WORKERS=4
PROD_API_PORT=8000
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs pollenpal-prod

# Check if port is in use
netstat -tulpn | grep :8000

# Rebuild without cache
docker build --no-cache -t pollenpal:prod .
```

### Permission Issues
```bash
# On Linux/Mac, fix file permissions
sudo chown -R $USER:$USER .

# Check container user
docker exec pollenpal-prod whoami
```

### Network Issues
```bash
# Check Docker networks
docker network ls

# Inspect network
docker network inspect pollenpal_pollenpal-network
```

## Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates in place (nginx/ssl/)
- [ ] Domain name configured in nginx.conf
- [ ] Health checks passing
- [ ] Logs being written
- [ ] Rate limiting configured
- [ ] Backup strategy in place

## Next Steps

For detailed production deployment, see [PRODUCTION.md](PRODUCTION.md).

For development setup, see the main [README.md](../README.md). 