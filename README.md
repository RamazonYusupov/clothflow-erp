# Retail ERP

Full-stack Retail ERP with RBAC — **FastAPI + Vue 3 + PostgreSQL + Nginx + HTTPS**

Live at: **https://clothflow.systems**

---

## Local Development

```bash
docker-compose up --build
docker-compose exec backend python seed.py
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs

### Login accounts
| Role    | Email                 | Password   |
|---------|-----------------------|------------|
| Admin   | ramzan06@gmail.com    | ramzan123  |
| Manager | manager@example.com   | manager123 |
| Kassir  | kassir@example.com    | kassir123  |
| Ombochi | ombochi@example.com   | ombochi123 |

---

## Production Deployment — DigitalOcean + clothflow.systems

### Step 1 — Create a Droplet

1. Go to https://cloud.digitalocean.com → **Create → Droplets**
2. Settings:
   - **Image:** Ubuntu 22.04 LTS x64
   - **Plan:** Basic Shared CPU — **$12/mo (2 GB RAM / 1 vCPU / 50 GB SSD)**
   - **Region:** pick closest to your users
   - **Authentication:** SSH Key (add your public key) or Password
3. Click **Create Droplet** — note the **IP address** shown

---

### Step 2 — Point clothflow.systems to the Droplet (Namecheap)

1. Log in to **Namecheap → Domain List → clothflow.systems → Manage**
2. Click the **Advanced DNS** tab
3. Delete any existing A records, then add:

   | Type | Host | Value               | TTL  |
   |------|------|---------------------|------|
   | A    | @    | YOUR_DROPLET_IP     | Auto |
   | A    | www  | YOUR_DROPLET_IP     | Auto |

4. Save. DNS propagates in 5–30 minutes (check with `ping clothflow.systems`)

---

### Step 3 — SSH into the Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

---

### Step 4 — Install Docker

```bash
apt update && apt upgrade -y
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin
# Verify
docker --version && docker compose version
```

---

### Step 5 — Clone your repo

```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/retail-erp.git erp
cd erp
```

---

### Step 6 — Create production environment file

```bash
cp .env.prod.example .env.prod
nano .env.prod
```

Fill in all values — example:

```env
POSTGRES_DB=retail_erp
POSTGRES_USER=erp_user
POSTGRES_PASSWORD=MyStr0ngP@ssword123!

DATABASE_URL=postgresql://erp_user:MyStr0ngP@ssword123!@db:5432/retail_erp
SECRET_KEY=<output of: openssl rand -hex 32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALLOWED_ORIGINS=https://clothflow.systems,https://www.clothflow.systems
```

Generate a secure secret key:
```bash
openssl rand -hex 32
```

Save: `Ctrl+O` → `Enter` → `Ctrl+X`

---

### Step 7 — Get SSL certificate (run ONCE)

Make sure DNS has propagated first (`ping clothflow.systems` should return your IP).

```bash
chmod +x init-ssl.sh deploy.sh
./init-ssl.sh
```

This installs certbot and gets a free Let's Encrypt certificate for both `clothflow.systems` and `www.clothflow.systems`.

---

### Step 8 — Deploy

```bash
./deploy.sh
```

This will:
1. Build all Docker images
2. Start PostgreSQL → FastAPI backend → Nginx frontend
3. Run database migrations
4. Seed demo data
5. Start the certbot auto-renewal sidecar

---

### Step 9 — Verify

```bash
# All containers should show "Up"
docker compose -f docker-compose.prod.yml ps

# Test HTTPS
curl -I https://clothflow.systems
# Should return: HTTP/2 200
```

Open your browser: **https://clothflow.systems** ✅

---

## Re-deploying after code changes

```bash
# On your local machine
git add .
git commit -m "your changes"
git push origin main

# On the Droplet
cd /opt/erp
./deploy.sh
```

---

## Useful server commands

```bash
# View live backend logs
docker compose -f docker-compose.prod.yml logs -f backend

# View nginx logs
docker compose -f docker-compose.prod.yml logs -f frontend

# Restart everything
docker compose -f docker-compose.prod.yml restart

# Open a shell inside the backend container
docker compose -f docker-compose.prod.yml exec backend bash

# Check SSL certificate expiry
certbot certificates
```

---

## Architecture

```
Browser
   │
   │ HTTPS :443
   ▼
┌──────────────────────────────────┐
│  Nginx (Docker)                  │
│  - Serves Vue 3 static files     │
│  - /api/* → proxy to backend     │
│  - HTTP → HTTPS redirect         │
│  - SSL: Let's Encrypt            │
└──────────┬───────────────────────┘
           │ http://backend:8000
           ▼
┌──────────────────────────────────┐
│  FastAPI + Gunicorn (Docker)     │
│  - REST API                      │
│  - JWT auth + RBAC               │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  PostgreSQL 15 (Docker)          │
│  - Internal network only         │
│  - Persistent volume             │
└──────────────────────────────────┘
```

## RBAC Roles

| Role    | Dashboard | Customers   | Products    | Orders       | Reports | Users |
|---------|-----------|-------------|-------------|--------------|---------|-------|
| Admin   | ✅ Full   | ✅ Full     | ✅ Full     | ✅ Full      | ✅      | ✅    |
| Manager | ✅        | ✅ No delete| 👁 View     | ✅ + Status  | ✅      | ❌    |
| Kassir  | ✅        | 👁 View     | 👁 View     | Create only  | ❌      | ❌    |
| Ombochi | ✅        | ❌          | ✅ No delete| ❌           | ❌      | ❌    |
