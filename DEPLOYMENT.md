# 🚀 Deployment Guide - BBW UPC Scanner

Complete guide for deploying the Bath & Body Works UPC Scanner app in various environments.

---

## 📋 Deployment Options

- [Local Docker](#docker-local-deployment)
- [GitHub Actions CI/CD](#github-actions-cicd)
- [Docker Compose](#docker-compose-deployment)
- [Cloud Platforms](#cloud-platform-deployment)

---

## 🐳 Docker Local Deployment

### Build Docker Images

```bash
# Build backend image
docker build -t bbw-upc-scanner:latest ./backend

# Build frontend image
docker build -t bbw-upc-scanner-frontend:latest ./frontend
```

### Run Backend Container

```bash
docker run -d \
  --name bbw-backend \
  -p 8000:8000 \
  -e CORS_ORIGINS=http://localhost:3000 \
  -v $(pwd)/backend/data:/app/data \
  bbw-upc-scanner:latest
```

### Run Frontend Container

```bash
docker run -d \
  --name bbw-frontend \
  -p 3000:3000 \
  -e VITE_API_URL=http://localhost:8000 \
  --link bbw-backend:backend \
  bbw-upc-scanner-frontend:latest
```

### Access the App

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stop Containers

```bash
docker stop bbw-backend bbw-frontend
docker rm bbw-backend bbw-frontend
```

---

## 🐳 Docker Compose Deployment

### Start All Services

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Access the App

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stop Services

```bash
docker-compose down

# Remove volumes too (WARNING: deletes data)
docker-compose down -v
```

### Environment Variables

Edit `docker-compose.yml` to customize:

```yaml
environment:
  - CORS_ORIGINS=http://localhost:3000
  - BBW_MIN_REQUEST_INTERVAL=2.5
  - BBW_PRODUCT_CACHE_TTL=300
  - SESSION_TTL_SECONDS=86400
```

---

## 🔄 GitHub Actions CI/CD

### Automated Testing

The repository includes GitHub Actions workflows that automatically:

1. **Run Tests** on every push and PR
2. **Build Frontend** and deploy to GitHub Pages
3. **Build Docker Images** for both backend and frontend
4. **Create Release Notes** automatically

### View Actions

1. Go to your GitHub repository
2. Click **Actions** tab
3. See all workflow runs and test results

### Workflow Files

- `.github/workflows/test.yml` - Testing pipeline
- `.github/workflows/docker.yml` - Docker build pipeline

### What's Tested

✅ Python syntax and linting  
✅ Backend server startup  
✅ Frontend build  
✅ Docker image builds  
✅ Integration tests  

---

## ☁️ Cloud Platform Deployment

### Heroku Deployment

**Create Heroku app:**

```bash
heroku create bbw-upc-scanner
```

**Add Procfile:**

```
web: cd backend && gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

**Deploy:**

```bash
git push heroku main
```

**Set environment variables:**

```bash
heroku config:set CORS_ORIGINS=https://bbw-upc-scanner.herokuapp.com
```

### AWS Deployment

**Option 1: EC2 Instance**

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Clone repository
git clone https://github.com/yourusername/upc_lookup.git
cd upc_lookup

# Run Docker Compose
docker-compose up -d
```

**Option 2: ECS (Elastic Container Service)**

1. Create ECR repositories for backend and frontend
2. Push Docker images to ECR
3. Create ECS task definitions
4. Create ECS service
5. Set up Application Load Balancer

**Option 3: App Runner**

```bash
aws apprunner create-service \
  --service-name bbw-upc-scanner \
  --source-configuration '{"ImageRepository": {"ImageRepositoryType": "ECR", "ImageIdentifier": "your-ecr-uri"}}'
```

### Google Cloud Deployment

**Cloud Run (Serverless):**

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/bbw-backend ./backend
gcloud builds submit --tag gcr.io/PROJECT_ID/bbw-frontend ./frontend

# Deploy backend
gcloud run deploy bbw-backend \
  --image gcr.io/PROJECT_ID/bbw-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy frontend
gcloud run deploy bbw-frontend \
  --image gcr.io/PROJECT_ID/bbw-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### DigitalOcean Deployment

**Using App Platform:**

1. Connect your GitHub repository
2. Create app from `docker-compose.yml`
3. Set environment variables
4. Deploy

**Using Droplet:**

```bash
# SSH into Droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and deploy
git clone https://github.com/yourusername/upc_lookup.git
cd upc_lookup
docker-compose up -d
```

---

## 🔒 Production Configuration

### Environment Variables

Set these in production:

```bash
# Disable debug mode
DEBUG=False

# Production CORS origins
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate limiting
BBW_MIN_REQUEST_INTERVAL=3.0

# Session timeout
SESSION_TTL_SECONDS=604800  # 7 days

# Logging
LOG_LEVEL=INFO
```

### Security

1. **HTTPS/SSL**
   - Use Let's Encrypt for free SSL
   - Configure reverse proxy (nginx/traefik)

2. **Database**
   - Store session files in persistent volume
   - Regular backups

3. **API Security**
   - Rate limiting (already built-in)
   - CORS properly configured
   - Input validation

4. **Monitoring**
   - Health checks configured
   - Error logging
   - Performance monitoring

### Nginx Reverse Proxy

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API docs
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
```

---

## 🔍 Health Checks & Monitoring

### Container Health

Both Docker containers include health checks:

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# View health logs
docker inspect --format='{{json .State.Health}}' container-name | jq
```

### API Health Endpoint

```bash
curl http://localhost:8000/docs
```

Should return 200 status.

### Monitor Logs

```bash
# Docker Compose logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Docker logs
docker logs -f container-name
```

---

## 📦 Scaling Considerations

### Horizontal Scaling

For multiple instances:

1. **Load Balancer** - Distribute traffic
2. **Shared Storage** - Session files on network drive
3. **Database** - Move from local files to database

### Performance Optimization

1. **Caching** - Already implemented (5 min TTL)
2. **Rate Limiting** - Already implemented (2.5s min)
3. **Compression** - Enable gzip in nginx
4. **CDN** - Cache static frontend assets

---

## 🚨 Troubleshooting Deployment

### Issue: Backend can't reach bathandbodyworks.com

**Solution:** Ensure outbound HTTPS is allowed in firewall

### Issue: Frontend can't reach backend API

**Solution:** Check CORS_ORIGINS environment variable matches domain

### Issue: Docker image build fails

**Solution:** 
```bash
# Clean and rebuild
docker system prune -a
docker-compose build --no-cache
```

### Issue: Health checks failing

**Solution:**
```bash
# Check logs
docker logs container-name

# Increase timeout in docker-compose.yml
```

---

## ✅ Pre-Deployment Checklist

Before deploying to production:

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] HTTPS/SSL certificate ready
- [ ] Firewall rules configured
- [ ] Health checks working
- [ ] Error logging enabled
- [ ] Monitoring set up
- [ ] Backups configured
- [ ] Documentation updated
- [ ] Team trained on deployment

---

## 📚 Related Documentation

- [QUICK_START.md](QUICK_START.md) - Local development
- [DEVELOPER.md](DEVELOPER.md) - Development setup
- [README.md](README.md) - Project overview

---

## 🆘 Getting Help

**Common Issues:**

1. **Port already in use**
   ```bash
   # Find and kill process
   lsof -i :8000
   kill -9 PID
   ```

2. **Docker permission denied**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Out of disk space**
   ```bash
   docker system prune -a
   ```

---

## 🎯 Next Steps

1. **Test locally** with Docker Compose
2. **Verify all tests pass** in GitHub Actions
3. **Choose deployment platform**
4. **Configure environment variables**
5. **Deploy and monitor**

---

**Deployment Status:** Ready for production ✅

For questions, refer to [DEVELOPER.md](DEVELOPER.md) or check GitHub Issues.

Happy deploying! 🚀
