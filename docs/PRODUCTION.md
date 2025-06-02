# Production Deployment Guide 🚀

This guide covers deploying PollenPal API to production using Docker and our automated scripts.

## Quick Start

```bash
# 1. Build production image
python scripts/run.py build

# 2. Deploy to production
python scripts/run.py deploy

# 3. Check status
python scripts/run.py status
```

## Prerequisites

- Docker and Docker Compose installed
- Python 3.10+ (for running scripts)
- Git (for version control)
- Domain name and SSL certificates (for HTTPS)

## Environment Setup

1. **Copy environment configuration:**
   ```bash
   cp env.example .env
   ```

2. **Configure production settings in `.env`:**
   ```bash
   POLLENPAL_ENV=production
   DEBUG=false
   PROD_API_WORKERS=4
   SECRET_KEY=your-secure-secret-key
   ALLOWED_HOSTS=["your-domain.com", "www.your-domain.com"]
   ```

## SSL/HTTPS Setup

1. **Create SSL directory:**
   ```bash
   mkdir -p nginx/ssl
   ```

2. **Add your SSL certificates:**
   ```bash
   # Copy your certificates
   cp your-cert.pem nginx/ssl/cert.pem
   cp your-key.pem nginx/ssl/key.pem
   ```

3. **Update nginx configuration:**
   - Edit `nginx/nginx.conf`
   - Uncomment the HTTPS server block
   - Update `server_name` with your domain

## Deployment Commands

### Available Scripts

Our script runner provides npm-like commands:

```bash
# Development
python scripts/run.py dev              # Start development server
python scripts/run.py dev:docker       # Start dev server in Docker
python scripts/run.py install          # Install dependencies

# Testing
python scripts/run.py test             # Run all tests
python scripts/run.py test:unit        # Unit tests only
python scripts/run.py test:docker      # Docker container tests
python scripts/run.py lint             # Code quality checks
python scripts/run.py lint:fix         # Fix formatting

# Build & Deploy
python scripts/run.py build            # Build production image
python scripts/run.py build:no-cache   # Build without cache
python scripts/run.py deploy           # Deploy to production
python scripts/run.py deploy:dev       # Deploy development

# Management
python scripts/run.py start            # Start services
python scripts/run.py stop             # Stop services
python scripts/run.py restart          # Restart services
python scripts/run.py logs             # View logs
python scripts/run.py status           # Service status
python scripts/run.py health           # Health check
python scripts/run.py clean            # Clean Docker resources
```

### Step-by-Step Deployment

1. **Prepare the environment:**
   ```bash
   # Install dependencies
   python scripts/run.py install
   
   # Run tests
   python scripts/run.py test
   
   # Check code quality
   python scripts/run.py lint
   ```

2. **Build production image:**
   ```bash
   # Build with automatic versioning
   python scripts/run.py build
   
   # Or build without cache
   python scripts/run.py build:no-cache
   ```

3. **Deploy to production:**
   ```bash
   # Deploy with health checks
   python scripts/run.py deploy
   
   # Or deploy with custom scaling
   python scripts/deploy.py --scale 4
   ```

4. **Verify deployment:**
   ```bash
   # Check service status
   python scripts/run.py status
   
   # Check health
   python scripts/run.py health
   
   # View logs
   python scripts/run.py logs
   ```

## Production Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   PollenPal     │    │     Redis       │
│  (Load Balancer)│────│   API (x4)      │────│   (Caching)     │
│   Port 80/443   │    │   Port 8000     │    │   Port 6379     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components

- **Nginx**: Reverse proxy, SSL termination, rate limiting
- **PollenPal API**: FastAPI application (multiple workers)
- **Redis**: Caching layer (optional)

## Configuration

### Docker Compose Profiles

- **`dev`**: Development environment with hot reload
- **`prod`**: Production environment with Nginx and Redis
- **`cache`**: Adds Redis caching to any profile

```bash
# Start development
docker-compose --profile dev up

# Start production
docker-compose --profile prod up

# Start production with caching
docker-compose --profile prod --profile cache up
```

### Environment Variables

Key production environment variables:

```bash
# Application
POLLENPAL_ENV=production
DEBUG=false

# API
PROD_API_HOST=0.0.0.0
PROD_API_PORT=8000
PROD_API_WORKERS=4

# Security
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=["your-domain.com"]

# External APIs
POLLEN_API_TIMEOUT=30
POLLEN_API_RETRIES=3

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## Monitoring and Logging

### Health Checks

The application includes built-in health checks:

```bash
# Manual health check
curl http://localhost:8000/health

# Automated health check
python scripts/run.py health
```

### Viewing Logs

```bash
# All services
python scripts/run.py logs

# Specific service
docker-compose logs -f pollenpal-prod

# Nginx logs
docker-compose logs -f nginx
```

### Log Locations

- **Application logs**: `/app/logs/pollenpal.log` (inside container)
- **Nginx logs**: `/var/log/nginx/` (inside nginx container)
- **Docker logs**: `docker-compose logs`

## Scaling

### Horizontal Scaling

Scale the API service:

```bash
# Scale to 4 instances
python scripts/deploy.py --scale 4

# Or manually
docker-compose --profile prod up -d --scale pollenpal-prod=4
```

### Vertical Scaling

Update resource limits in `docker-compose.yml`:

```yaml
pollenpal-prod:
  # ... other config
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
```

## Security Best Practices

### Container Security

- ✅ Non-root user in containers
- ✅ Multi-stage builds for smaller images
- ✅ Minimal base images (Python slim)
- ✅ No secrets in images
- ✅ Health checks enabled

### Network Security

- ✅ Internal Docker network
- ✅ Only necessary ports exposed
- ✅ Nginx rate limiting
- ✅ HTTPS with strong ciphers

### Application Security

- ✅ Environment-based configuration
- ✅ Input validation with Pydantic
- ✅ CORS configuration
- ✅ Security headers

## Backup and Recovery

### Database Backup (if applicable)

```bash
# Backup (when database is added)
docker exec pollenpal-db pg_dump -U user pollenpal > backup.sql

# Restore
docker exec -i pollenpal-db psql -U user pollenpal < backup.sql
```

### Configuration Backup

```bash
# Backup configuration
tar -czf pollenpal-config-$(date +%Y%m%d).tar.gz \
  docker-compose.yml nginx/ .env
```

## Troubleshooting

### Common Issues

1. **Service won't start:**
   ```bash
   # Check logs
   python scripts/run.py logs
   
   # Check Docker status
   docker ps -a
   ```

2. **Health check failing:**
   ```bash
   # Test manually
   curl -v http://localhost:8000/health
   
   # Check container logs
   docker logs pollenpal-prod
   ```

3. **High memory usage:**
   ```bash
   # Check resource usage
   docker stats
   
   # Reduce workers
   python scripts/deploy.py --scale 2
   ```

### Performance Tuning

1. **Adjust worker count:**
   ```bash
   # Formula: (2 x CPU cores) + 1
   python scripts/deploy.py --scale 4
   ```

2. **Enable caching:**
   ```bash
   # Start with Redis
   docker-compose --profile prod --profile cache up
   ```

3. **Optimise Nginx:**
   - Adjust `worker_connections` in `nginx/nginx.conf`
   - Tune rate limiting parameters
   - Enable gzip compression

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: python scripts/run.py install
      
      - name: Run tests
        run: python scripts/run.py test
      
      - name: Build and deploy
        run: |
          python scripts/run.py build
          python scripts/run.py deploy
```

## Maintenance

### Regular Tasks

1. **Update dependencies:**
   ```bash
   uv sync --upgrade
   python scripts/run.py test
   python scripts/run.py build
   ```

2. **Clean up Docker:**
   ```bash
   python scripts/run.py clean
   ```

3. **Monitor logs:**
   ```bash
   python scripts/run.py logs | grep ERROR
   ```

### Updates and Rollbacks

1. **Deploy new version:**
   ```bash
   git pull origin main
   python scripts/run.py build
   python scripts/run.py deploy
   ```

2. **Rollback (if needed):**
   ```bash
   python scripts/deploy.py --rollback
   ```

## Support

For issues or questions:

1. Check the logs: `python scripts/run.py logs`
2. Verify health: `python scripts/run.py health`
3. Review this documentation
4. Open an issue on the repository

---

**Remember**: Always test deployments in a staging environment first! 