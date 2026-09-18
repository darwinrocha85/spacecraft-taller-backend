from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.adapters.outbound.persistence.orm_models import DamageORM, RepairORM
from app.domain.models import Damage, Repair, RepairStatus, TERMINAL_STATUSES
from app.domain.ports import RepairRepository

_SEP = "||"


def _encode(values: list[str]) -> str:
    return _SEP.join(values)


def _decode(raw: str) -> list[str]:
    return [v for v in raw.split(_SEP) if v] if raw else []


class SqliteRepairRepository(RepairRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, repair: Repair) -> Repair:
        orm = RepairORM(
            spacecraft_id=repair.spacecraft_id,
            spacecraft_name=repair.spacecraft_name,
            spacecraft_model=repair.spacecraft_model,
            status=repair.status.value,
            closed_museum_dates_raw=_encode(repair.closed_museum_dates),
            closed_theater_events_raw=_encode(repair.closed_theater_events),
        )
        orm.damages = [
            DamageORM(category=d.category, subtype=d.subtype) for d in repair.damages
        ]
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return self._to_domain(orm)

    def get(self, repair_id: int) -> Repair | None:
        orm = self._session.get(
            RepairORM, repair_id, options=[joinedload(RepairORM.damages)]
        )
        return self._to_domain(orm) if orm else None

    def list_by_spacecraft(self, spacecraft_id: int) -> list[Repair]:
        stmt = (
            select(RepairORM)
            .options(joinedload(RepairORM.damages))
            .where(RepairORM.spacecraft_id == spacecraft_id)
            .order_by(RepairORM.created_at.desc())
        )
        rows = self._session.execute(stmt).unique().scalars().all()
        return [self._to_domain(r) for r in rows]

    def list_all(self, status: RepairStatus | None = None) -> list[Repair]:
        stmt = select(RepairORM).options(joinedload(RepairORM.damages))
        if status is not None:
            stmt = stmt.where(RepairORM.status == status.value)
        stmt = stmt.order_by(RepairORM.created_at.desc())
        rows = self._session.execute(stmt).unique().scalars().all()
        return [self._to_domain(r) for r in rows]

    def find_active_by_spacecraft(self, spacecraft_id: int) -> Repair | None:
        terminal_values = [s.value for s in TERMINAL_STATUSES]
        stmt = (
            select(RepairORM)
            .options(joinedload(RepairORM.damages))
            .where(RepairORM.spacecraft_id == spacecraft_id)
            .where(RepairORM.status.notin_(terminal_values))
            .order_by(RepairORM.created_at.desc())
        )
        row = self._session.execute(stmt).unique().scalars().first()
        return self._to_domain(row) if row else None

    def update(self, repair: Repair) -> Repair:
        orm = self._session.get(RepairORM, repair.id)
        if orm is None:
            raise ValueError(f"Repair {repair.id} not found for update")
        orm.status = repair.status.value
        orm.delivered_at = repair.delivered_at
        self._session.commit()
        self._session.refresh(orm)
        return self._to_domain(orm)

    def _to_domain(self, orm: RepairORM) -> Repair:
        return Repair(
            id=orm.id,
            spacecraft_id=orm.spacecraft_id,
            spacecraft_name=orm.spacecraft_name,
            spacecraft_model=orm.spacecraft_model,
            status=RepairStatus(orm.status),
            damages=[Damage(id=d.id, category=d.category, subtype=d.subtype) for d in orm.damages],
            closed_museum_dates=_decode(orm.closed_museum_dates_raw),
            closed_theater_events=_decode(orm.closed_theater_events_raw),
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            delivered_at=orm.delivered_at,
        )
