"""Puertos (interfaces) que la capa de aplicación usa, implementados en adapters/outbound."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models import Budget, Repair, RepairStatus, SparePart


class RepairRepository(ABC):
    @abstractmethod
    def add(self, repair: Repair) -> Repair: ...

    @abstractmethod
    def get(self, repair_id: int) -> Repair | None: ...

    @abstractmethod
    def list_by_spacecraft(self, spacecraft_id: int) -> list[Repair]: ...

    @abstractmethod
    def list_all(self, status: RepairStatus | None = None) -> list[Repair]: ...

    @abstractmethod
    def find_active_by_spacecraft(self, spacecraft_id: int) -> Repair | None: ...

    @abstractmethod
    def update(self, repair: Repair) -> Repair: ...


class BudgetRepository(ABC):
    @abstractmethod
    def add(self, budget: Budget) -> Budget: ...

    @abstractmethod
    def get(self, budget_id: int) -> Budget | None: ...

    @abstractmethod
    def list_by_repair(self, repair_id: int) -> list[Budget]: ...

    @abstractmethod
    def find_pending_by_repair(self, repair_id: int) -> Budget | None: ...

    @abstractmethod
    def update(self, budget: Budget) -> Budget: ...


class SparePartRepository(ABC):
    @abstractmethod
    def add(self, spare_part: SparePart) -> SparePart: ...

    @abstractmethod
    def get(self, spare_part_id: int) -> SparePart | None: ...

    @abstractmethod
    def list(self, active_only: bool = False) -> list[SparePart]: ...

    @abstractmethod
    def update(self, spare_part: SparePart) -> SparePart: ...
