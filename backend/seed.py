"""
Seed script — creates admin user + 60 days of realistic fake data.
Run once:  python seed.py
Re-running is safe (skips already-existing records).
"""
import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.database import SessionLocal, engine, Base
import app.models  # noqa — register all models
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order, OrderItem, OrderStatus

# ── Ensure PostgreSQL enum has all RBAC role values ───────────────────────────
_enum_migrations = [
    "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'manager'",
    "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'kassir'",
    "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'ombochi'",
    "UPDATE users SET role = 'kassir' WHERE role::text = 'staff'",
]
with engine.connect() as _conn:
    for _sql in _enum_migrations:
        try:
            _conn.execute(text(_sql))
            _conn.commit()
        except Exception as _e:
            _conn.rollback()
            # Already exists or no 'staff' rows — safe to ignore
            pass
from app.utils.auth import hash_password
from app.utils.order_number import generate_order_number

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Admin user ────────────────────────────────────────────────────────────────
if not db.query(User).filter(User.email == "ramzan06@gmail.com").first():
    db.add(User(
        email="ramzan06@gmail.com",
        hashed_password=hash_password("ramzan123"),
        full_name="Ramzan",
        role=UserRole.admin,
    ))
    print("✓ Admin user created: ramzan06@gmail.com / ramzan123")

# Sample users for each role
sample_users = [
    dict(email="manager@example.com", password="manager123", full_name="Sara Manager",  role=UserRole.manager),
    dict(email="kassir@example.com",  password="kassir123",  full_name="Ali Kassir",    role=UserRole.kassir),
    dict(email="ombochi@example.com", password="ombochi123", full_name="Jasur Ombochi", role=UserRole.ombochi),
]
for u in sample_users:
    if not db.query(User).filter(User.email == u["email"]).first():
        db.add(User(
            email=u["email"],
            hashed_password=hash_password(u["password"]),
            full_name=u["full_name"],
            role=u["role"],
        ))
        print(f"✓ {u['role']} user created: {u['email']} / {u['password']}")

# ── Categories ────────────────────────────────────────────────────────────────
category_names = ["Electronics", "Clothing", "Food & Beverage", "Home & Garden", "Sports & Outdoors"]
for name in category_names:
    if not db.query(Category).filter(Category.name == name).first():
        db.add(Category(name=name))
db.commit()

cats = {c.name: c for c in db.query(Category).all()}

# ── Products ──────────────────────────────────────────────────────────────────
product_data = [
    # Electronics
    dict(name="Wireless Mouse",         sku="EL-001", price=Decimal("29.99"),  stock_quantity=120, low_stock_threshold=15, category_id=cats["Electronics"].id),
    dict(name="Mechanical Keyboard",    sku="EL-002", price=Decimal("89.99"),  stock_quantity=60,  low_stock_threshold=10, category_id=cats["Electronics"].id),
    dict(name="USB-C Hub 7-Port",       sku="EL-003", price=Decimal("49.99"),  stock_quantity=8,   low_stock_threshold=10, category_id=cats["Electronics"].id),
    dict(name="27\" LED Monitor",       sku="EL-004", price=Decimal("249.99"), stock_quantity=25,  low_stock_threshold=5,  category_id=cats["Electronics"].id),
    dict(name="Noise-Cancelling Headphones", sku="EL-005", price=Decimal("129.99"), stock_quantity=40, low_stock_threshold=8, category_id=cats["Electronics"].id),
    dict(name="Webcam 1080p",           sku="EL-006", price=Decimal("59.99"),  stock_quantity=55,  low_stock_threshold=10, category_id=cats["Electronics"].id),
    dict(name="Laptop Stand",           sku="EL-007", price=Decimal("34.99"),  stock_quantity=90,  low_stock_threshold=15, category_id=cats["Electronics"].id),
    dict(name="Portable SSD 1TB",       sku="EL-008", price=Decimal("89.99"),  stock_quantity=45,  low_stock_threshold=10, category_id=cats["Electronics"].id),
    # Clothing
    dict(name="Classic White T-Shirt",  sku="CL-001", price=Decimal("19.99"),  stock_quantity=200, low_stock_threshold=20, category_id=cats["Clothing"].id),
    dict(name="Slim Fit Jeans",         sku="CL-002", price=Decimal("49.99"),  stock_quantity=100, low_stock_threshold=15, category_id=cats["Clothing"].id),
    dict(name="Hooded Sweatshirt",      sku="CL-003", price=Decimal("39.99"),  stock_quantity=80,  low_stock_threshold=10, category_id=cats["Clothing"].id),
    dict(name="Running Sneakers",       sku="CL-004", price=Decimal("79.99"),  stock_quantity=6,   low_stock_threshold=10, category_id=cats["Clothing"].id),
    dict(name="Winter Jacket",          sku="CL-005", price=Decimal("119.99"), stock_quantity=35,  low_stock_threshold=8,  category_id=cats["Clothing"].id),
    # Food & Beverage
    dict(name="Organic Green Tea (50 bags)", sku="FB-001", price=Decimal("12.99"), stock_quantity=300, low_stock_threshold=30, category_id=cats["Food & Beverage"].id),
    dict(name="Premium Coffee Beans 1kg",    sku="FB-002", price=Decimal("24.99"), stock_quantity=150, low_stock_threshold=20, category_id=cats["Food & Beverage"].id),
    dict(name="Mixed Nuts 500g",             sku="FB-003", price=Decimal("14.99"), stock_quantity=9,   low_stock_threshold=15, category_id=cats["Food & Beverage"].id),
    dict(name="Protein Powder 2kg",          sku="FB-004", price=Decimal("44.99"), stock_quantity=70,  low_stock_threshold=10, category_id=cats["Food & Beverage"].id),
    # Home & Garden
    dict(name="Scented Candle Set",      sku="HG-001", price=Decimal("22.99"), stock_quantity=110, low_stock_threshold=15, category_id=cats["Home & Garden"].id),
    dict(name="Bamboo Cutting Board",    sku="HG-002", price=Decimal("18.99"), stock_quantity=75,  low_stock_threshold=10, category_id=cats["Home & Garden"].id),
    dict(name="Stainless Steel Water Bottle", sku="HG-003", price=Decimal("27.99"), stock_quantity=95, low_stock_threshold=15, category_id=cats["Home & Garden"].id),
    dict(name="Air Purifier",            sku="HG-004", price=Decimal("89.99"), stock_quantity=7,   low_stock_threshold=5,  category_id=cats["Home & Garden"].id),
    # Sports
    dict(name="Yoga Mat",                sku="SP-001", price=Decimal("29.99"), stock_quantity=85,  low_stock_threshold=10, category_id=cats["Sports & Outdoors"].id),
    dict(name="Resistance Band Set",     sku="SP-002", price=Decimal("19.99"), stock_quantity=130, low_stock_threshold=15, category_id=cats["Sports & Outdoors"].id),
    dict(name="Adjustable Dumbbells",    sku="SP-003", price=Decimal("149.99"),stock_quantity=20,  low_stock_threshold=5,  category_id=cats["Sports & Outdoors"].id),
    dict(name="Cycling Helmet",          sku="SP-004", price=Decimal("54.99"), stock_quantity=40,  low_stock_threshold=8,  category_id=cats["Sports & Outdoors"].id),
]

for p in product_data:
    if not db.query(Product).filter(Product.sku == p["sku"]).first():
        db.add(Product(**p))
db.commit()
print(f"✓ {len(product_data)} products seeded")

# ── Customers ─────────────────────────────────────────────────────────────────
customer_data = [
    dict(full_name="Alice Johnson",    email="alice@example.com",   phone="555-0101", address="12 Oak Street, NY"),
    dict(full_name="Bob Smith",        email="bob@example.com",     phone="555-0102", address="34 Pine Ave, CA"),
    dict(full_name="Carol White",      email="carol@example.com",   phone="555-0103", address="56 Maple Rd, TX"),
    dict(full_name="David Brown",      email="david@example.com",   phone="555-0104", address="78 Elm Blvd, FL"),
    dict(full_name="Emma Davis",       email="emma@example.com",    phone="555-0105", address="90 Cedar Ln, WA"),
    dict(full_name="Frank Miller",     email="frank@example.com",   phone="555-0106", address="11 Birch Dr, IL"),
    dict(full_name="Grace Wilson",     email="grace@example.com",   phone="555-0107", address="22 Walnut St, OH"),
    dict(full_name="Henry Moore",      email="henry@example.com",   phone="555-0108", address="33 Ash Ave, GA"),
    dict(full_name="Isabella Taylor",  email="isabella@example.com",phone="555-0109", address="44 Spruce Ct, NJ"),
    dict(full_name="James Anderson",   email="james@example.com",   phone="555-0110", address="55 Willow Way, AZ"),
    dict(full_name="Karen Thomas",     email="karen@example.com",   phone="555-0111", address="66 Poplar Pl, NC"),
    dict(full_name="Liam Jackson",     email="liam@example.com",    phone="555-0112", address="77 Magnolia Dr, VA"),
    dict(full_name="Mia Harris",       email="mia@example.com",     phone="555-0113", address="88 Chestnut St, MA"),
    dict(full_name="Noah Martin",      email="noah@example.com",    phone="555-0114", address="99 Sycamore Rd, CO"),
    dict(full_name="Olivia Garcia",    email="olivia@example.com",  phone="555-0115", address="10 Dogwood Ln, MN"),
    dict(full_name="Peter Martinez",   email="peter@example.com",   phone="555-0116", address="21 Redwood Ave, OR"),
    dict(full_name="Quinn Robinson",   email="quinn@example.com",   phone="555-0117", address="32 Hickory Blvd, TN"),
    dict(full_name="Rachel Clark",     email="rachel@example.com",  phone="555-0118", address="43 Juniper St, MO"),
    dict(full_name="Samuel Rodriguez", email="samuel@example.com",  phone="555-0119", address="54 Locust Ct, WI"),
    dict(full_name="Tina Lewis",       email="tina@example.com",    phone="555-0120", address="65 Pecan Way, KY"),
]

for c in customer_data:
    if not db.query(Customer).filter(Customer.email == c["email"]).first():
        db.add(Customer(**c))
db.commit()
print(f"✓ {len(customer_data)} customers seeded")

# ── Orders (60 days of history) ───────────────────────────────────────────────
# Only seed orders if none exist yet
if db.query(Order).count() == 0:
    all_customers = db.query(Customer).all()
    all_products  = db.query(Product).all()

    # Generate weights dynamically — always matches the actual product list
    # Products with lower price get slightly higher weight (sell more units)
    product_weights = [
        max(1, int(10 - float(p.price) / 50)) for p in all_products
    ]

    status_progression = [
        OrderStatus.new,
        OrderStatus.confirmed,
        OrderStatus.shipped,
        OrderStatus.delivered,
    ]

    now = datetime.utcnow()
    orders_created = 0

    for day_offset in range(60, 0, -1):
        order_date = now - timedelta(days=day_offset)

        # 2–6 orders per day, slightly more on recent days
        daily_count = random.randint(2, 6)

        for _ in range(daily_count):
            customer = random.choice(all_customers)

            # Pick 1–4 distinct products per order
            num_items = random.randint(1, 4)
            chosen_products = random.choices(all_products, weights=product_weights, k=num_items)
            # Deduplicate while preserving weights
            seen = set()
            unique_products = []
            for p in chosen_products:
                if p.id not in seen:
                    seen.add(p.id)
                    unique_products.append(p)

            # Generate unique order number
            for _ in range(10):
                order_number = generate_order_number()
                if not db.query(Order).filter(Order.order_number == order_number).first():
                    break

            # Determine status based on age
            if day_offset > 45:
                status = OrderStatus.delivered
            elif day_offset > 30:
                status = random.choice([OrderStatus.delivered, OrderStatus.delivered, OrderStatus.shipped])
            elif day_offset > 14:
                status = random.choice([OrderStatus.delivered, OrderStatus.shipped, OrderStatus.confirmed])
            elif day_offset > 5:
                status = random.choice([OrderStatus.confirmed, OrderStatus.shipped, OrderStatus.new])
            else:
                status = random.choice([OrderStatus.new, OrderStatus.new, OrderStatus.confirmed])

            # Small chance of cancellation
            if random.random() < 0.06:
                status = OrderStatus.cancelled

            total_amount = Decimal("0")
            items_to_add = []
            for product in unique_products:
                qty = random.randint(1, 3)
                unit_price = product.price
                subtotal = unit_price * qty
                total_amount += subtotal
                items_to_add.append((product, qty, unit_price, subtotal))

            order = Order(
                order_number=order_number,
                customer_id=customer.id,
                status=status,
                total_amount=total_amount,
                created_at=order_date,
                updated_at=order_date,
            )
            db.add(order)
            db.flush()

            for product, qty, unit_price, subtotal in items_to_add:
                db.add(OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=qty,
                    unit_price=unit_price,
                    subtotal=subtotal,
                ))

            orders_created += 1

    db.commit()
    print(f"✓ {orders_created} orders created across 60 days")
else:
    print("⚠ Orders already exist — skipping order seed")

db.close()
print("\n✅ Seed complete!")
print("   Admin:   ramzan06@gmail.com / ramzan123")
print("   Manager: manager@example.com / manager123")
print("   Kassir:  kassir@example.com  / kassir123")
print("   Ombochi: ombochi@example.com / ombochi123")
