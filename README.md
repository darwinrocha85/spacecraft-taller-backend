# spacecraft-taller-backend

Backend independiente (FastAPI + SQLite) para el ciclo de reparación de naves: recibe el aviso
de `spacecraftSystem` cuando una nave entra al taller, gestiona sus sub-estados y presupuestos
(con repuestos propios en stock), y cobra los presupuestos aprobados directo a BankIn.

## Flujo de una reparación
`ENVIADA → RECIBIDA → EN_REVISION → EN_TRABAJO → ESPERANDO_APROBACION_PRESUPUESTO →
LISTA_PARA_SALIR → ENTREGADA`

## Cómo correr en local
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8001
```
(Instalar una vez: `python -m venv .venv` + activar + `pip install -r requirements.txt` +
`Copy-Item .env.example .env`. Ver bloques completos en `Projects/RUNBOOK.md`.)

## Variables de entorno
Ver `.env.example` (sin valores reales). Las relevantes:
| Variable | Para qué |
|---|---|
| `TALLER_INTERNAL_API_KEY` | Clave que `spacecraftSystem` debe enviar para crear reparaciones — el único canal del demo que siempre exige auth |
| `BANKIN_API_BASE` / `BANKIN_API_KEY` | Backend de pagos al que se cobran los presupuestos aprobados |
| `ALLOWED_ORIGINS` | Orígenes CORS adicionales (localhost siempre está permitido) |

## Tests
```powershell
pip install -r requirements-dev.txt
pytest
```

## Repos relacionados
Orquestador: [spacecraftSystem](../spacecraftSystem). Frontend:
[spacecraft-taller-frontend](../spacecraft-taller-frontend).
