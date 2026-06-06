from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.dependencies import get_db, require_roles
from app.models.user import UserRole
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut, CategoryCreate, CategoryOut

router = APIRouter(tags=["products"])

_all    = require_roles(UserRole.admin, UserRole.manager, UserRole.kassir, UserRole.ombochi)
_edit   = require_roles(UserRole.admin, UserRole.ombochi)
_delete = require_roles(UserRole.admin)
_cat_edit = require_roles(UserRole.admin, UserRole.ombochi)


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), _=Depends(_all)):
    return db.query(Category).all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _=Depends(_cat_edit)):
    existing = db.query(Category).filter(Category.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# ── Products ──────────────────────────────────────────────────────────────────

@router.get("/products/low-stock", response_model=list[ProductOut])
def low_stock_products(db: Session = Depends(get_db), _=Depends(_all)):
    return (
        db.query(Product)
        .filter(Product.stock_quantity <= Product.low_stock_threshold, Product.is_active == True)
        .all()
    )


@router.get("/products", response_model=dict)
def list_products(
    search: Optional[str] = Query(None),
    category_id: Optional[UUID] = Query(None),
    low_stock: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(_all),
):
    query = db.query(Product).filter(Product.is_active == True)
    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%")
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if low_stock:
        query = query.filter(Product.stock_quantity <= Product.low_stock_threshold)
    total = query.count()
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [ProductOut.model_validate(p) for p in products],
    }


@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db), _=Depends(_edit)):
    existing = db.query(Product).filter(Product.sku == data.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: UUID, db: Session = Depends(get_db), _=Depends(_all)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: UUID, data: ProductUpdate, db: Session = Depends(get_db), _=Depends(_edit)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: UUID, db: Session = Depends(get_db), _=Depends(_delete)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()
