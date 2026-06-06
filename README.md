# Retail ERP-CRM

Full-stack Retail ERP-CRM built with **FastAPI + Vue 3 + PostgreSQL**.

## Quick Start

### Prerequisites
- Docker & Docker Compose installed

### Run with Docker

```bash
# Start all services
docker-compose up --build

# In a separate terminal, seed the database (first time only)
docker-compose exec backend python seed.py
```

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Default Login
```
Email:    ramzan06@gmail.com
Password: ramzan123
```

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Update .env DATABASE_URL to point at your local Postgres
# Then:
python seed.py                # Create tables + seed data
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
# Create .env.local:
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

---

## Features

| Module | Features |
|--------|----------|
| **Auth** | JWT login, role-based access (admin/staff) |
| **Dashboard** | KPI cards, daily revenue chart, top products |
| **Customers** | List/search/filter, add/edit/delete, order history |
| **Products** | Inventory with low-stock alerts, categories, CRUD |
| **Orders** | Create orders, status workflow, stock management |
| **Reports** | Revenue by date range, top products, CSV export |

## API Docs

Interactive Swagger UI at http://localhost:8000/docs

## Architecture

```
backend/
  app/
    main.py          FastAPI app + CORS
    models/          SQLAlchemy ORM models
    schemas/         Pydantic v2 schemas
    routers/         API route handlers
    utils/           JWT auth, order number gen
    dependencies.py  DB session, auth middleware

frontend/
  src/
    api/             Axios instance with JWT interceptor
    stores/          Pinia state stores
    router/          Vue Router + auth guard
    views/           Page components
    components/      Reusable UI + chart components
```
