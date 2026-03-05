from __future__ import annotations

from datetime import date
from io import BytesIO

from openpyxl import Workbook

from app.types import Order


def generate_accrivia_xls(order: Order) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sheet1"

    today = date.today().isoformat()

    sheet["A1"] = order.debtorCode
    sheet["A2"] = today
    sheet["A3"] = (order.requiredDate.isoformat() if order.requiredDate else today)
    sheet["B4"] = order.id
    sheet["B5"] = order.customerName
    sheet["B6"] = order.deliveryAddress or ""
    sheet["B7"] = order.fulfilmentNote or ""
    sheet["B8"] = order.contactNumber

    for index, line in enumerate(order.lines, start=12):
        sheet[f"A{index}"] = line.itemCode
        sheet[f"B{index}"] = line.quantity

    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
