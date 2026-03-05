from app.types import Order, OrderType, PickupStore


def resolve_email(order: Order) -> str:
    if order.orderType == OrderType.DELIVERY:
        return "ops@test.com"
    if order.pickupStore == PickupStore.CABRAMATTA:
        return "cabra_cs@test.com"
    return "lid_cs@test.com"


def build_email_subject(order: Order) -> str:
    date_text = str(order.requiredDate) if order.requiredDate else "today"
    return (
        f"[Order Queue #{order.queueNumber}] {order.orderType.value} - "
        f"{order.customerName} - {date_text}"
    )
