"""Excepciones de dominio. Los routers las traducen a HTTPException con {"detail": ...}."""
from __future__ import annotations


class DomainError(Exception):
    """Base para todas las excepciones de dominio."""


class RepairNotFoundError(DomainError):
    def __init__(self, repair_id: int):
        super().__init__(f"No se encontró la reparación {repair_id}")


class ActiveRepairNotFoundError(DomainError):
    def __init__(self, spacecraft_id: int):
        super().__init__(f"No hay reparación activa para la nave {spacecraft_id}")


class BudgetNotFoundError(DomainError):
    def __init__(self, budget_id: int):
        super().__init__(f"No se encontró el presupuesto {budget_id}")


class SparePartNotFoundError(DomainError):
    def __init__(self, spare_part_id: int):
        super().__init__(f"No se encontró el repuesto {spare_part_id}")


class InvalidDamageError(DomainError):
    def __init__(self, category: str, subtype: str):
        super().__init__(
            f"Daño inválido: categoría '{category}' con subtipo '{subtype}' "
            "no existe en el catálogo"
        )


class InvalidStatusTransitionError(DomainError):
    def __init__(self, current: str, requested: str):
        super().__init__(f"Transición de estado inválida: {current} -> {requested}")


class BudgetAlreadyDecidedError(DomainError):
    def __init__(self, budget_id: int, status: str):
        super().__init__(
            f"El presupuesto {budget_id} ya fue decidido (estado actual: {status})"
        )


class ActiveBudgetAlreadyExistsError(DomainError):
    def __init__(self, repair_id: int):
        super().__init__(
            f"Ya existe un presupuesto pendiente de aprobación para la reparación {repair_id}"
        )


class RepairNotReadyForBudgetError(DomainError):
    def __init__(self, repair_id: int, status: str):
        super().__init__(
            f"La reparación {repair_id} no admite un presupuesto en su estado actual ({status})"
        )


class RepairNotReadyForPickupError(DomainError):
    def __init__(self, repair_id: int, status: str):
        super().__init__(
            f"La nave de la reparación {repair_id} todavía no está lista para retirar "
            f"(estado actual: {status})"
        )


# --- Errores al llamar a BankIn (espejo de BankInPaymentService.java) ---


class BankInCardNotFoundError(DomainError):
    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class BankInChargeRejectedError(DomainError):
    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class BankInConfigError(DomainError):
    """Clave de BankIn mal configurada — error nuestro, no del comprador."""


class BankInUnavailableError(DomainError):
    """BankIn no responde (caído, timeout, URL mal apuntada)."""
