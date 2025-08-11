# 🚀 VPS Deployment Guide - ExploreIndonesia

Complete guide untuk deploy ExploreIndonesia di VPS production server.

## 📋 Prerequisites

### Server Requirements
- **OS:** Ubuntu 20.04 LTS atau lebih baru
- **RAM:** Minimum 2GB, Recommended 4GB
- **Storage:** Minimum 10GB free space
- **CPU:** 2 cores atau lebih
- **Bandwidth:** Tidak terbatas untuk optimal performance

### Software Requirements
- Docker & Docker Compose
- Git
- Nginx (opsional jika tidak menggunakan Docker Nginx)
- SSL Certificate (untuk HTTPS)

## 🛠️ Installation Steps

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git vim htop

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 2. Clone Repository

```bash
# Clone repository
git clone <your-repository-url> exploreindo
cd exploreindo

# Make deploy script executable
chmod +x deploy.sh
```

### 3. Environment Configuration

```bash
# Copy environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Environment Variables:**
```env
# Production settings
ENV=production
DEBUG=false

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Website Configuration  
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Domain (untuk SSL)
DOMAIN=your-domain.com

# Database (jika menggunakan)
# DB_URL=postgresql://user:pass@localhost/db
```

### 4. SSL Certificate Setup (HTTPS)

#### Option A: Let's Encrypt (Free)
```bash
# Install Certbot
sudo apt install -y certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Create SSL directory
mkdir -p ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown -R $USER:$USER ssl/
```

#### Option B: Self-Signed (Development)
```bash
# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=ID/ST=Jakarta/L=Jakarta/O=ExploreIndonesia/OU=IT/CN=localhost"
```

### 5. Deploy Application

```bash
# Start all services
./deploy.sh start

# Check status
./deploy.sh status

# Check health
./deploy.sh health

# View logs
./deploy.sh logs
```

## 🌐 Domain & DNS Configuration

### DNS Records
```
Type    Name    Value               TTL
A       @       YOUR_SERVER_IP      300
A       www     YOUR_SERVER_IP      300
CNAME   api     your-domain.com     300
```

### Nginx Configuration for Custom Domain

Edit `nginx.conf`:
```nginx
server_name your-domain.com www.your-domain.com;
```

Enable HTTPS by uncommenting SSL section in `nginx.conf`.

## 📊 Monitoring & Maintenance

### 1. Service Monitoring

```bash
# Check service status
./deploy.sh status

# View real-time logs
./deploy.sh logs

# Check health endpoints
curl http://your-domain.com/health
curl http://your-domain.com/api/
```

### 2. Resource Monitoring

```bash
# Check system resources
htop

# Check Docker resources
docker stats

# Check disk usage
df -h
```

### 3. Log Management

```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs api
docker-compose -f docker-compose.prod.yml logs website

# Clean old logs (run weekly)
docker system prune -f
```

## 🔧 Production Optimizations

### 1. Performance Tuning

**API Optimization:**
```bash
# Increase workers for high traffic
# Edit docker-compose.prod.yml
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Website Optimization:**
```bash
# Increase memory limit in docker-compose.prod.yml
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

### 2. Security Hardening

```bash
# Update Nginx security headers
# Edit nginx.conf to add more security headers

# Set up fail2ban
sudo apt install -y fail2ban

# Configure firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

### 3. Backup Strategy

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/exploreindo"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup data
tar -czf $BACKUP_DIR/exploreindo_$DATE.tar.gz \
    --exclude='*/node_modules' \
    --exclude='*/.*' \
    ./

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab (daily backup at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup.sh") | crontab -
```

## 🚨 Troubleshooting

### Common Issues

1. **Port 80/443 already in use**
```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :443

# Stop conflicting service
sudo systemctl stop apache2  # or nginx
```

2. **API not loading model**
```bash
# Check model file exists
ls -la model/recommendation_artifacts_optimal.pkl

# Check permissions
sudo chown -R $USER:$USER model/
```

3. **Website can't connect to API**
```bash
# Check if API is running
curl http://localhost:8000/

# Check Docker network
docker network ls
docker network inspect exploreindo_exploreindo_network
```

4. **High memory usage**
```bash
# Restart services
./deploy.sh restart

# Check for memory leaks
docker stats --no-stream
```

### Log Analysis

```bash
# API errors
docker-compose -f docker-compose.prod.yml logs api | grep ERROR

# Website errors  
docker-compose -f docker-compose.prod.yml logs website | grep ERROR

# Nginx errors
docker-compose -f docker-compose.prod.yml logs nginx | grep error
```

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Update services
./deploy.sh update

# Or manual update
./deploy.sh stop
docker-compose -f docker-compose.prod.yml build --no-cache
./deploy.sh start
```

### Auto-Update Script

```bash
cat > update.sh << 'EOF'
#!/bin/bash
cd /path/to/exploreindo

# Pull latest changes
git pull origin main

# Update and restart services
./deploy.sh update

# Send notification (optional)
curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"ExploreIndonesia updated successfully"}' \
    YOUR_SLACK_WEBHOOK_URL
EOF
```

## 📈 Performance Monitoring

### Setup Monitoring Dashboard

```bash
# Add monitoring to docker-compose.prod.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
```

### Health Check Endpoints

- **Website Health:** `http://your-domain.com/health`
- **API Health:** `http://your-domain.com/api/`
- **API Documentation:** `http://your-domain.com/api/docs`

## 📞 Support & Maintenance

### Regular Maintenance Tasks

**Daily:**
- Check service status
- Monitor resource usage
- Review error logs

**Weekly:**
- Update system packages
- Clean Docker images/containers
- Review security logs

**Monthly:**
- Update SSL certificates (if manual)
- Performance optimization review
- Backup verification

### Emergency Procedures

1. **Service Down:**
```bash
./deploy.sh restart
./deploy.sh health
```

2. **High Load:**
```bash
# Scale API service
docker-compose -f docker-compose.prod.yml up --scale api=3 -d
```

3. **Out of Disk Space:**
```bash
# Clean Docker
docker system prune -a -f
# Clean logs
sudo journalctl --vacuum-time=7d
```

---

## 🎉 Success!

Your ExploreIndonesia application is now running in production at:

- **Website:** https://your-domain.com
- **API:** https://your-domain.com/api/
- **API Docs:** https://your-domain.com/api/docs

Monitor the application regularly and keep it updated for optimal performance and security.