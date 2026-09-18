from __future__ import annotations

from app.domain.errors import SparePartNotFoundError
from app.domain.models import SparePart
from app.domain.ports import SparePartRepository


class PartsService:
    def __init__(self, parts: SparePartRepository):
        self._parts = parts

    def list(self, active_only: bool = False) -> list[SparePart]:
        return self._parts.list(active_only=active_only)

    def get(self, spare_part_id: int) -> SparePart:
        part = self._parts.get(spare_part_id)
        if part is None:
            raise SparePartNotFoundError(spare_part_id)
        return part

    def create(self, name: str, price: float, stock_quantity: int | None) -> SparePart:
        return self._parts.add(
            SparePart(id=None, name=name, price=price, stock_quantity=stock_quantity, active=True)
        )

    def update(
        self,
        spare_part_id: int,
        name: str | None,
        price: float | None,
        stock_quantity: int | None,
        active: bool | None,
        stock_quantity_provided: bool = False,
    ) -> SparePart:
        part = self.get(spare_part_id)
        if name is not None:
            part.name = name
        if price is not None:
            part.price = price
        if stock_quantity_provided:
            part.stock_quantity = stock_quantity
        if active is not None:
            part.active = active
        return self._parts.update(part)

    def deactivate(self, spare_part_id: int) -> SparePart:
        part = self.get(spare_part_id)
        part.active = False
        return self._parts.update(part)
