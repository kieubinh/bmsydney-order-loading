from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class OrderType(str, Enum):
    PICKUP = "Pickup"
    DELIVERY = "Delivery"


class PickupStore(str, Enum):
    CABRAMATTA = "Cabramatta"
    LIDCOMBE = "Lidcombe"


class OrderLineInput(BaseModel):
    itemCode: str = Field(min_length=1)
    description: str | None = None
    quantity: float = Field(gt=0)


class OrderInput(BaseModel):
    customerName: str = Field(min_length=1)
    contactNumber: str = Field(min_length=1)
    debtorCode: str = Field(min_length=1)
    orderType: OrderType
    pickupStore: PickupStore | None = None
    requiredDate: date | None = None
    deliveryAddress: str | None = None
    fulfilmentNote: str | None = None
    lines: list[OrderLineInput] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_order_type_requirements(self) -> "OrderInput":
        if self.orderType == OrderType.PICKUP and not self.pickupStore:
            raise ValueError("Pickup store is required")

        if self.orderType == OrderType.DELIVERY:
            if not self.requiredDate:
                raise ValueError("Required date is required for delivery")
            if not self.deliveryAddress:
                raise ValueError("Delivery address is required")
            if not self.contactNumber:
                raise ValueError("Contact number is required")

        return self


class Order(OrderInput):
    id: str
    queueNumber: str
    submittedAt: datetime
    status: Literal["Submitted"]
