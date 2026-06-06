from datetime import datetime
import random
import string


def generate_order_number() -> str:
    """Generate a unique order number like ORD-20240606-A3X9"""
    date_str = datetime.utcnow().strftime("%Y%m%d")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{date_str}-{suffix}"
