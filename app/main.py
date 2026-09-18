import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.adapters.inbound.api.routers import (  # noqa: E402
    catalog,
    internal,
    owner_actions,
    parts,
    repairs_read,
    shop_actions,
)
from app.adapters.outbound.persistence.db import init_db  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if os.environ.get("AUTO_SEED", "true").lower() == "true":
        from seed_data import seed_if_empty

        seed_if_empty()
    yield


app = FastAPI(title="spacecraft-taller-backend", lifespan=lifespan)

extra_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=extra_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog.router)
app.include_router(internal.router)
app.include_router(repairs_read.router)
app.include_router(shop_actions.router)
app.include_router(owner_actions.router)
app.include_router(parts.router)


@app.get("/health")
def health():
    return {"status": "ok", "environment": os.environ.get("ENVIRONMENT", "local")}
