from __future__ import annotations

from datetime import datetime

from app.types import OrderType, PickupStore


class QueueService:
    def __init__(self) -> None:
        self._counters: dict[str, int] = {}

    def next(
        self,
        order_type: OrderType,
        pickup_store: PickupStore | None,
        now: datetime | None = None,
    ) -> str:
        current = now or datetime.utcnow()
        ymd = current.strftime("%Y%m%d")

        if order_type == OrderType.DELIVERY:
            prefix = "DEL"
        elif pickup_store == PickupStore.CABRAMATTA:
            prefix = "CAB"
        else:
            prefix = "LID"

        key = f"{prefix}-{ymd}"
        next_number = self._counters.get(key, 0) + 1
        self._counters[key] = next_number

        return f"{prefix}-{ymd}-{next_number:03d}"
