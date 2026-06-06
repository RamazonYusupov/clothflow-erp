# Retail ERP-CRM

Full-stack Retail ERP-CRM with RBAC — built with **FastAPI + Vue 3 + PostgreSQL**.

---

## Local Development

```bash
docker-compose up --build
docker-compose exec backend python seed.py
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Login accounts
| Role    | Email                    | Password     |
|---------|--------------------------|--------------|
| Admin   | ramzan06@gmail.com       | ramzan123    |
| Manager | manager@example.com      | manager123   |
| Kassir  | kassir@example.com       | kassir123    |
| Ombochi | ombochi@example.com      | ombochi123   |

---

## DigitalOcean Deployment Guide

### Step 1 — Create a Droplet

1. Log in to [DigitalOcean](https://cloud.digitalocean.com)
2. Click **Create → Droplets**
3. Choose:
   - **Image:** Ubuntu 22.04 LTS
   - **Size:** Basic — $12/mo (2 GB RAM, 1 vCPU) minimum
   - **Region:** Closest to your users
   - **Authentication:** SSH Key (recommended) or Password
4. Click **Create Droplet**
5. Note the **Droplet IP address**

---

### Step 2 — Connect to the Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

---

### Step 3 — Install Docker & Docker Compose

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose plugin
apt install -y docker-compose-plugin

# Verify
docker --version
docker compose version
```

---

### Step 4 — Push your code to GitHub first

On your local machine (if not done yet):
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/retail-erp-crm.git
git push -u origin main
```

---

### Step 5 — Clone the repo on the Droplet

```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/retail-erp-crm.git erp
cd erp
```

---

### Step 6 — Create the production environment file

```bash
cp .env.prod.example .env.prod
nano .env.prod
```

Fill in the values — replace everything that says `CHANGE_ME`:

```env
POSTGRES_DB=retail_erp
POSTGRES_USER=erp_user
POSTGRES_PASSWORD=MyStr0ngP@ssword123

DATABASE_URL=postgresql://erp_user:MyStr0ngP@ssword123@db:5432/retail_erp
SECRET_KEY=a8f3b2c1d9e4f7a6b5c8d2e1f0a9b3c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALLOWED_ORIGINS=http://YOUR_DROPLET_IP
```

> **Generate a strong SECRET_KEY:**
> ```bash
> openssl rand -hex 32
> ```

Save and exit: `Ctrl+O`, `Enter`, `Ctrl+X`

---

### Step 7 — Deploy

```bash
chmod +x deploy.sh
./deploy.sh
```

This will:
- Build all Docker images
- Start PostgreSQL, Backend (Gunicorn), and Frontend (Nginx)
- Run database migrations
- Seed the database with demo data

---

### Step 8 — Verify

```bash
# Check all containers are running
docker-compose -f docker-compose.prod.yml ps

# Check backend logs
docker-compose -f docker-compose.prod.yml logs backend

# Check frontend logs
docker-compose -f docker-compose.prod.yml logs frontend
```

Open your browser: `http://YOUR_DROPLET_IP`

---

### Step 9 — Set up a domain + HTTPS (optional but recommended)

#### Point your domain to the Droplet
In your domain registrar DNS settings, add an **A record**:
```
Type: A
Name: @  (or www)
Value: YOUR_DROPLET_IP
TTL: 3600
```

#### Install Certbot for free SSL

```bash
# Install Certbot
apt install -y certbot

# Stop frontend container temporarily (frees port 80)
docker-compose -f docker-compose.prod.yml stop frontend

# Get SSL certificate
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates are saved to:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

#### Update nginx.conf for HTTPS

Edit `frontend/nginx.conf` and replace its contents with the HTTPS version:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    root /usr/share/nginx/html;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass         http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location ~* \.(js|css|png|jpg|ico|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Mount the certificates into the frontend container by adding this to `docker-compose.prod.yml` under the `frontend` service:

```yaml
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
```

Update `ALLOWED_ORIGINS` in `.env.prod`:
```
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

Redeploy:
```bash
./deploy.sh
```

#### Auto-renew SSL
```bash
crontab -e
# Add this line:
0 3 * * * docker-compose -f /opt/erp/docker-compose.prod.yml stop frontend && certbot renew --quiet && docker-compose -f /opt/erp/docker-compose.prod.yml start frontend
```

---

### Re-deploying after code changes

```bash
# On the Droplet
cd /opt/erp
./deploy.sh
```

---

## Architecture

```
Internet
    │
    ▼
[Nginx :80/:443]  ← serves Vue static files
    │ /api/*
    ▼
[FastAPI/Gunicorn :8000]  ← REST API
    │
    ▼
[PostgreSQL :5432]  ← data (internal Docker network only)
```

## Roles

| Role    | Dashboard | Customers | Products | Orders | Reports | Users |
|---------|-----------|-----------|----------|--------|---------|-------|
| Admin   | ✅ Full   | ✅ Full   | ✅ Full  | ✅ Full| ✅      | ✅    |
| Manager | ✅        | ✅ No del | 👁 View  | ✅     | ✅      | ❌    |
| Kassir  | ✅        | 👁 View   | 👁 View  | Create | ❌      | ❌    |
| Ombochi | ✅        | ❌        | ✅ No del| ❌     | ❌      | ❌    |
