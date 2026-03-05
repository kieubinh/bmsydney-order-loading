from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from app.email_service import build_email_subject, resolve_email
from app.queue_service import QueueService
from app.types import Order, OrderInput
from app.validation import merge_duplicate_items, validate_item_codes
from app.xls import generate_accrivia_xls

app = FastAPI()
queue_service = QueueService()
orders: list[Order] = []


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/api/orders/submit")
def submit_order(payload: OrderInput) -> dict[str, str | int]:
    try:
        validate_item_codes(payload.lines)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    merged_lines = merge_duplicate_items(payload.lines)
    queue_number = queue_service.next(payload.orderType, payload.pickupStore)

    order = Order(
        **payload.model_dump(),
        lines=merged_lines,
        id=str(uuid4()),
        queueNumber=queue_number,
        submittedAt=datetime.utcnow(),
        status="Submitted",
    )

    xls_data = generate_accrivia_xls(order)
    orders.append(order)

    return {
        "orderId": order.id,
        "queueNumber": order.queueNumber,
        "emailTo": resolve_email(order),
        "emailSubject": build_email_subject(order),
        "xlsSizeBytes": len(xls_data),
    }


@app.get("/api/staff/queue")
def staff_queue(orderType: str | None = None, store: str | None = None) -> list[dict]:
    filtered = [
        order
        for order in orders
        if (orderType is None or order.orderType.value == orderType)
        and (store is None or (order.pickupStore and order.pickupStore.value == store))
    ]
    filtered.sort(key=lambda order: order.queueNumber)
    return [order.model_dump(mode="json") for order in filtered]
