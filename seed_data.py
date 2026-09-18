"""Datos de ejemplo para que el demo no arranque vacío (repuestos con precio). No siembra
reparaciones — esas las crea spacecraftSystem vía POST /api/internal/repairs cuando corresponda.
Se corre automáticamente al arrancar si AUTO_SEED=true y la tabla de repuestos está vacía
(pensado para el disco efímero de Render, igual que hace Bankin)."""
from app.adapters.outbound.persistence import db
from app.adapters.outbound.persistence.orm_models import SparePartORM

DEMO_PARTS = [
    ("Placa de blindaje", 180.0, 20),
    ("Conducto de refrigerante", 45.5, 30),
    ("Modulo de navegacion", 620.0, 5),
    ("Bateria auxiliar", 95.0, 15),
    ("Sellador de casco", 22.0, 50),
    ("Filtro de soporte vital", 38.0, 25),
]


def seed_if_empty() -> None:
    session = db.SessionLocal()
    try:
        if session.query(SparePartORM).count() > 0:
            return
        for name, price, stock in DEMO_PARTS:
            session.add(SparePartORM(name=name, price=price, stock_quantity=stock, active=True))
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed_if_empty()
    print("Seed listo.")
