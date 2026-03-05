import pytest
from pydantic import ValidationError

from app.types import OrderInput
from app.validation import validate_item_codes


def test_rejects_pickup_without_store() -> None:
    with pytest.raises(ValidationError):
        OrderInput(
            customerName="Test Customer",
            contactNumber="0400000000",
            debtorCode="CASH",
            orderType="Pickup",
            lines=[{"itemCode": "ITEM0001", "quantity": 1}],
        )


def test_rejects_invalid_item_code() -> None:
    order = OrderInput(
        customerName="Test Customer",
        contactNumber="0400000000",
        debtorCode="CASH",
        orderType="Delivery",
        requiredDate="2026-03-01",
        deliveryAddress="1 Test St",
        lines=[{"itemCode": "BADCODE", "quantity": 2}],
    )

    with pytest.raises(ValueError, match="Invalid or inactive item code"):
        validate_item_codes(order.lines)
