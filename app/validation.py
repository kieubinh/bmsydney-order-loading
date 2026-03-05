from __future__ import annotations

from app.item_master import ITEM_MASTER
from app.types import OrderLineInput


def validate_item_codes(lines: list[OrderLineInput]) -> None:
    for line in lines:
        if line.itemCode not in ITEM_MASTER:
            raise ValueError(f"Invalid or inactive item code: {line.itemCode}")


def merge_duplicate_items(lines: list[OrderLineInput]) -> list[OrderLineInput]:
    merged: dict[str, OrderLineInput] = {}
    for line in lines:
        existing = merged.get(line.itemCode)
        if existing:
            existing.quantity += line.quantity
        else:
            merged[line.itemCode] = OrderLineInput(**line.model_dump())
    return list(merged.values())
