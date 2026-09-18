from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.outbound.persistence.orm_models import SparePartORM
from app.domain.models import SparePart
from app.domain.ports import SparePartRepository


class SqliteSparePartRepository(SparePartRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, spare_part: SparePart) -> SparePart:
        orm = SparePartORM(
            name=spare_part.name,
            price=spare_part.price,
            stock_quantity=spare_part.stock_quantity,
            active=spare_part.active,
        )
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return self._to_domain(orm)

    def get(self, spare_part_id: int) -> SparePart | None:
        orm = self._session.get(SparePartORM, spare_part_id)
        return self._to_domain(orm) if orm else None

    def list(self, active_only: bool = False) -> list[SparePart]:
        stmt = select(SparePartORM)
        if active_only:
            stmt = stmt.where(SparePartORM.active.is_(True))
        stmt = stmt.order_by(SparePartORM.name)
        rows = self._session.execute(stmt).scalars().all()
        return [self._to_domain(r) for r in rows]

    def update(self, spare_part: SparePart) -> SparePart:
        orm = self._session.get(SparePartORM, spare_part.id)
        if orm is None:
            raise ValueError(f"SparePart {spare_part.id} not found for update")
        orm.name = spare_part.name
        orm.price = spare_part.price
        orm.stock_quantity = spare_part.stock_quantity
        orm.active = spare_part.active
        self._session.commit()
        self._session.refresh(orm)
        return self._to_domain(orm)

    def _to_domain(self, orm: SparePartORM) -> SparePart:
        return SparePart(
            id=orm.id,
            name=orm.name,
            price=orm.price,
            stock_quantity=orm.stock_quantity,
            active=orm.active,
        )
