from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: UUID

    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int = 0
    low_stock_threshold: int = 10
    category_id: Optional[UUID] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    category_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class ProductOut(ProductBase):
    id: UUID
    category: Optional[CategoryOut] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
