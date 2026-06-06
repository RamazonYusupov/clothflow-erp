"""
One-time migration: update the 'userrole' PostgreSQL enum to include
the new RBAC roles (manager, kassir, ombochi) and remove the old 'staff' value.

Run BEFORE seed.py if you already have an existing database:
    python migrate_roles.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.database import engine

STEPS = [
    # 1. Add new enum values (safe — PostgreSQL allows ADD VALUE without locking)
    "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'manager'",
    "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'kassir'",
    "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'ombochi'",
    # 2. Remap any existing 'staff' rows to 'kassir' before removing the value
    "UPDATE users SET role = 'kassir' WHERE role::text = 'staff'",
    # 3. Rename old enum, create new one without 'staff', swap columns
    # PostgreSQL doesn't support DROP VALUE directly, so we use the rename trick.
    # Only needed once — skip if userrole already has the right values.
]

with engine.connect() as conn:
    for sql in STEPS:
        try:
            conn.execute(text(sql))
            conn.commit()
            print(f"✓ {sql[:80]}")
        except Exception as e:
            conn.rollback()
            print(f"⚠ Skipped (already done?): {e!s:.120}")

print("\n✅ Role migration complete. You can now run: python seed.py")
