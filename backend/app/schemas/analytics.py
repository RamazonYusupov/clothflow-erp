from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import date


class DashboardKPI(BaseModel):
    total_sales: Decimal
    orders_count: int
    low_stock_count: int
    new_customers: int


class DailyRevenue(BaseModel):
    date: date
    revenue: Decimal


class TopProduct(BaseModel):
    product_id: str
    product_name: str
    total_quantity: int
    total_revenue: Decimal


class DashboardResponse(BaseModel):
    kpi: DashboardKPI
    daily_revenue: List[DailyRevenue]
    top_products: List[TopProduct]


class RevenueResponse(BaseModel):
    from_date: date
    to_date: date
    total_revenue: Decimal
    daily_revenue: List[DailyRevenue]
