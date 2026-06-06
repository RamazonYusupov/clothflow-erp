import csv
import io
from datetime import date, timedelta, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_roles
from app.models.user import UserRole
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.customer import Customer
from app.schemas.analytics import DashboardResponse, DashboardKPI, DailyRevenue, TopProduct, RevenueResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

_dashboard = require_roles(UserRole.admin, UserRole.manager, UserRole.kassir, UserRole.ombochi)
_reports   = require_roles(UserRole.admin, UserRole.manager)


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db), _=Depends(_dashboard)):
    total_sales = db.query(func.sum(Order.total_amount)).filter(
        Order.status.in_([OrderStatus.delivered, OrderStatus.shipped])
    ).scalar() or Decimal("0")

    orders_count = db.query(func.count(Order.id)).scalar() or 0

    low_stock_count = db.query(func.count(Product.id)).filter(
        Product.stock_quantity <= Product.low_stock_threshold,
        Product.is_active == True,
    ).scalar() or 0

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_customers = db.query(func.count(Customer.id)).filter(
        Customer.created_at >= thirty_days_ago
    ).scalar() or 0

    daily_rows = (
        db.query(
            func.date(Order.created_at).label("day"),
            func.sum(Order.total_amount).label("revenue"),
        )
        .filter(
            Order.created_at >= thirty_days_ago,
            Order.status.in_([OrderStatus.delivered, OrderStatus.shipped]),
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )
    daily_revenue = [DailyRevenue(date=r.day, revenue=r.revenue or 0) for r in daily_rows]

    top_rows = (
        db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label("total_quantity"),
            func.sum(OrderItem.subtotal).label("total_revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status.in_([OrderStatus.delivered, OrderStatus.shipped]))
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.subtotal).desc())
        .limit(5)
        .all()
    )
    top_products = [
        TopProduct(
            product_id=str(r.id),
            product_name=r.name,
            total_quantity=r.total_quantity or 0,
            total_revenue=r.total_revenue or 0,
        )
        for r in top_rows
    ]

    return DashboardResponse(
        kpi=DashboardKPI(
            total_sales=total_sales,
            orders_count=orders_count,
            low_stock_count=low_stock_count,
            new_customers=new_customers,
        ),
        daily_revenue=daily_revenue,
        top_products=top_products,
    )


@router.get("/revenue", response_model=RevenueResponse)
def revenue(
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    _=Depends(_reports),
):
    total = db.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) >= from_date,
        func.date(Order.created_at) <= to_date,
        Order.status.in_([OrderStatus.delivered, OrderStatus.shipped]),
    ).scalar() or Decimal("0")

    daily_rows = (
        db.query(
            func.date(Order.created_at).label("day"),
            func.sum(Order.total_amount).label("revenue"),
        )
        .filter(
            func.date(Order.created_at) >= from_date,
            func.date(Order.created_at) <= to_date,
            Order.status.in_([OrderStatus.delivered, OrderStatus.shipped]),
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )
    return RevenueResponse(
        from_date=from_date,
        to_date=to_date,
        total_revenue=total,
        daily_revenue=[DailyRevenue(date=r.day, revenue=r.revenue or 0) for r in daily_rows],
    )


@router.get("/top-products")
def top_products(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    _=Depends(_reports),
):
    rows = (
        db.query(
            Product.id,
            Product.name,
            Product.sku,
            func.sum(OrderItem.quantity).label("total_quantity"),
            func.sum(OrderItem.subtotal).label("total_revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status.in_([OrderStatus.delivered, OrderStatus.shipped]))
        .group_by(Product.id, Product.name, Product.sku)
        .order_by(func.sum(OrderItem.subtotal).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "product_id": str(r.id),
            "product_name": r.name,
            "sku": r.sku,
            "total_quantity": r.total_quantity or 0,
            "total_revenue": float(r.total_revenue or 0),
        }
        for r in rows
    ]


@router.get("/reports/export")
def export_csv(
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    _=Depends(_reports),
):
    orders = (
        db.query(Order)
        .filter(
            func.date(Order.created_at) >= from_date,
            func.date(Order.created_at) <= to_date,
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Order Number", "Customer", "Status", "Total Amount", "Date"])

    for order in orders:
        customer_name = order.customer.full_name if order.customer else ""
        writer.writerow([
            order.order_number,
            customer_name,
            order.status,
            float(order.total_amount),
            order.created_at.strftime("%Y-%m-%d"),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{from_date}_{to_date}.csv"},
    )
