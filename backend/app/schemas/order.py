from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int


class OrderItemOut(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    product: Optional[dict] = None

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    customer_id: UUID
    notes: Optional[str] = None
    items: List[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderOut(BaseModel):
    id: UUID
    order_number: str
    customer_id: UUID
    status: OrderStatus
    total_amount: Decimal
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderDetailOut(OrderOut):
    items: List[OrderItemOut] = []
    customer: Optional[dict] = None

    model_config = {"from_attributes": True}
