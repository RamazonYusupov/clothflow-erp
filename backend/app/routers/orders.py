from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import date
from app.dependencies import get_db, require_roles
from app.models.user import UserRole
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.customer import Customer
from app.schemas.order import OrderCreate, OrderOut, OrderDetailOut, OrderStatusUpdate
from app.utils.order_number import generate_order_number

router = APIRouter(prefix="/orders", tags=["orders"])

_view   = require_roles(UserRole.admin, UserRole.manager, UserRole.kassir)
_create = require_roles(UserRole.admin, UserRole.manager, UserRole.kassir)
_edit   = require_roles(UserRole.admin, UserRole.manager)

# Allowed status transitions
STATUS_TRANSITIONS = {
    OrderStatus.new:       [OrderStatus.confirmed, OrderStatus.cancelled],
    OrderStatus.confirmed: [OrderStatus.shipped, OrderStatus.cancelled],
    OrderStatus.shipped:   [OrderStatus.delivered],
    OrderStatus.delivered: [],
    OrderStatus.cancelled: [],
}


@router.get("", response_model=dict)
def list_orders(
    status: Optional[OrderStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(_view),
):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    if from_date:
        query = query.filter(Order.created_at >= from_date)
    if to_date:
        query = query.filter(Order.created_at <= to_date)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [OrderOut.model_validate(o) for o in orders],
    }


@router.post("", response_model=OrderDetailOut, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db), _=Depends(_create)):
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if not data.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    order_items = []
    total_amount = 0

    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id, Product.is_active == True).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
        if product.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}. Available: {product.stock_quantity}",
            )
        subtotal = float(product.price) * item_data.quantity
        total_amount += subtotal
        order_items.append((product, item_data.quantity, float(product.price), subtotal))

    for _ in range(5):
        order_number = generate_order_number()
        if not db.query(Order).filter(Order.order_number == order_number).first():
            break

    order = Order(
        order_number=order_number,
        customer_id=data.customer_id,
        notes=data.notes,
        total_amount=total_amount,
    )
    db.add(order)
    db.flush()

    for product, quantity, unit_price, subtotal in order_items:
        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
        ))
        product.stock_quantity -= quantity

    db.commit()
    db.refresh(order)
    return _order_detail(order, db)


@router.get("/{order_id}", response_model=OrderDetailOut)
def get_order(order_id: UUID, db: Session = Depends(get_db), _=Depends(_view)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _order_detail(order, db)


@router.patch("/{order_id}/status", response_model=OrderDetailOut)
def update_order_status(order_id: UUID, data: OrderStatusUpdate, db: Session = Depends(get_db), _=Depends(_edit)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    allowed = STATUS_TRANSITIONS.get(order.status, [])
    if data.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {order.status} to {data.status}",
        )

    if data.status == OrderStatus.cancelled:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock_quantity += item.quantity

    order.status = data.status
    db.commit()
    db.refresh(order)
    return _order_detail(order, db)


def _order_detail(order: Order, db: Session) -> dict:
    items_out = []
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items_out.append({
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": item.subtotal,
            "product": {"id": str(product.id), "name": product.name, "sku": product.sku} if product else None,
        })
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    return {
        "id": order.id,
        "order_number": order.order_number,
        "customer_id": order.customer_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "notes": order.notes,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": items_out,
        "customer": {"id": str(customer.id), "full_name": customer.full_name, "email": customer.email} if customer else None,
    }
