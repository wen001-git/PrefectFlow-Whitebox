# whitebox.api — FastAPI skeleton

Stage 2 / P2.3 — **skeleton only**. All business endpoints return
plausible fixture data so the Next.js frontend (`apps/web/`) can build
typed clients against a stable OpenAPI surface. Real wiring lands in
todo `d-api-contracts`.

## Install

The API extras live in the `[project.optional-dependencies].api` group
of `pyproject.toml`. Pick one of:

```powershell
# Using pip inside the project venv
.venv\Scripts\python.exe -m pip install -e ".[api]"

# Or using uv
uv sync --extra api
```

## Run the dev server

```powershell
uvicorn whitebox.api.main:app --reload
```

Then open <http://127.0.0.1:8000/openapi.json> for the OpenAPI schema or
<http://127.0.0.1:8000/docs> for the Swagger UI.

## Endpoints

> **Note:** every endpoint below returns fixture data — `d-api-contracts`
> will replace the bodies with real registry / engine / renderer output.

| Method | Path                                          | Router       |
|--------|-----------------------------------------------|--------------|
| GET    | `/health`                                     | `health.py`  |
| GET    | `/api/v1/runs`                                | `runs.py`    |
| GET    | `/api/v1/runs/{run_id}`                       | `runs.py`    |
| GET    | `/api/v1/runs/{run_id}/sheets/{sheet_name}`   | `sheets.py`  |
| GET    | `/api/v1/runs/{run_id}/diff`                  | `diff.py`    |
| GET    | `/api/v1/runs/{run_id}/export`                | `export.py` (501) |
| GET    | `/api/v1/lineage/{field_id}`                  | `lineage.py` |

## Layout

```
whitebox/api/
├── __init__.py
├── main.py             # FastAPI app + CORS + router registration
├── deps.py             # DI shims (auth, db session) — dummies for now
├── schemas.py          # Pydantic response models
└── routers/
    ├── __init__.py
    ├── health.py
    ├── runs.py
    ├── sheets.py
    ├── diff.py
    ├── lineage.py
    └── export.py
```

## CORS

CORS is permissive for `http://localhost:3000` / `http://127.0.0.1:3000`
(the Next.js dev origin). Production origins must be added via ADR.
