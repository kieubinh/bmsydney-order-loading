from datetime import datetime

from app.queue_service import QueueService
from app.types import OrderType, PickupStore


def test_queue_increments_by_queue_and_date() -> None:
    queue = QueueService()
    date = datetime(2026, 3, 4, 10, 0, 0)

    assert queue.next(OrderType.PICKUP, PickupStore.CABRAMATTA, date) == "CAB-20260304-001"
    assert queue.next(OrderType.PICKUP, PickupStore.CABRAMATTA, date) == "CAB-20260304-002"
    assert queue.next(OrderType.PICKUP, PickupStore.LIDCOMBE, date) == "LID-20260304-001"
    assert queue.next(OrderType.DELIVERY, None, date) == "DEL-20260304-001"

    next_day = datetime(2026, 3, 5, 9, 0, 0)
    assert queue.next(OrderType.PICKUP, PickupStore.CABRAMATTA, next_day) == "CAB-20260305-001"
