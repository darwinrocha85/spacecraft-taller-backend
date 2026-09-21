# spacecraft-taller-backend — AGENTS.md

> Proyecto independiente. Abrir opencode con cwd en `spacecraft-taller-backend/`, nunca en `Projects/`.
> Stack: Python 3.x, FastAPI, SQLAlchemy, SQLite. Tests con pytest.

## Cómo correr (bloques completos en `Projects/RUNBOOK.md` §1 instalar / §2 local)
- Instalar (una vez): `python -m venv .venv` + `.\.venv\Scripts\Activate.ps1` + `python -m pip install -r requirements.txt` + `Copy-Item .env.example .env` (ojo: acá es `.venv`)
- Correr: `.\.venv\Scripts\Activate.ps1` + `python -m uvicorn app.main:app --reload --port 8001` → `http://localhost:8001` (`/docs`)
- Tests: `python -m pip install -r requirements-dev.txt` + `python -m pytest`
- Env (`.env.example`): `ENVIRONMENT, TALLER_DB_PATH, AUTO_SEED, ALLOWED_ORIGINS,`
  `TALLER_INTERNAL_API_KEY`, `BANKIN_API_BASE` (default `localhost:8000`), `BANKIN_API_KEY`

## Reglas que no se rompen
- Máquina de estados: `ENVIADA → RECIBIDA → EN_REVISION → EN_TRABAJO → ESPERANDO_APROBACION_PRESUPUESTO → LISTA_PARA_SALIR → ENTREGADA`
- Endpoint interno (`POST /api/internal/repairs`) exige `X-Internal-Api-Key` siempre (fail-closed).
  Es el único canal que nunca acepta llamadas sin clave.
- Cobro de presupuestos aprobados a BankIn con `note` fijo de origen (auditable en panel gerente).
- Aprobar/cobrar lo hace el admin (`spacecraftSystem`), este repo + su frontend NO aprueban ni cobran.

## Deploy
- `render.yaml` → `spacecraft-taller-backend.onrender.com`, con `BANKIN_API_BASE=https://bankinback.onrender.com`

## No hacer
- No commitear `.env`, `*.db`, `venv/` (ver `.gitignore`).
- No relajar el auth del endpoint interno sin pedirlo.
- No cambiar estados por fuera de la máquina definida.
