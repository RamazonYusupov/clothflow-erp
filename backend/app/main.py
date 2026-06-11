import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, customers, products, orders, analytics, users
import app.models  # noqa: F401 — register all models with Base

# Create all tables on startup (use Alembic for production migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Retail ERP API",
    version="2.0.0",
    description="Full-stack Retail ERP with RBAC",
)

# CORS — reads from env so the same image works in dev and prod
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost"
)
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(analytics.router)


@app.get("/health")
def health():
    return {"status": "ok"}
