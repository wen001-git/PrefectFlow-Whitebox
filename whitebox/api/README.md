# whitebox.api — FastAPI skeleton

Stage 2 / P2.3 — **production contracts**. Business endpoints are
served by typed pydantic schemas; bodies come from a fixture provider
that will be swapped for the engine + storage layers in later todos.
The OpenAPI surface is locked under a snapshot test.

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

> **Note:** business endpoints are now backed by typed pydantic schemas
> in `whitebox/api/schemas.py`. The bodies are produced by the fixture
> provider in `whitebox/api/data/fixtures.py` (marked
> `# FIXTURE: replaced by engine/storage in later todos`); the public
> HTTP / JSON contract is stable from `d-api-contracts` onward.

| Method | Path                                                              | Router       |
|--------|-------------------------------------------------------------------|--------------|
| GET    | `/health`                                                         | `health.py`  |
| GET    | `/api/v1/runs`                                                    | `runs.py`    |
| GET    | `/api/v1/runs/{run_id}`                                           | `runs.py`    |
| GET    | `/api/v1/runs/{run_id}/sheets`                                    | `sheets.py`  |
| GET    | `/api/v1/runs/{run_id}/sheets/{sheet_name}`                       | `sheets.py`  |
| GET    | `/api/v1/runs/{run_id}/sheets/{sheet_name}/cells/{cell_ref}`      | `sheets.py`  |
| GET    | `/api/v1/runs/{run_id}/diff?against={other_run_id}`               | `diff.py`    |
| GET    | `/api/v1/runs/{run_id}/export?format=xlsx`                        | `export.py` (501) |
| GET    | `/api/v1/lineage/fields`                                          | `lineage.py` |
| GET    | `/api/v1/lineage/fields/{field_id}`                               | `lineage.py` |

## Layout

```
whitebox/api/
├── __init__.py
├── main.py             # FastAPI app + CORS + router registration
├── deps.py             # DI shims (auth, db session) — dummies for now
├── schemas.py          # Pydantic response models (production contracts)
├── data/
│   ├── __init__.py
│   └── fixtures.py     # FIXTURE provider — replaced by engine/storage later
└── routers/
    ├── __init__.py
    ├── health.py
    ├── runs.py
    ├── sheets.py
    ├── diff.py
    ├── lineage.py
    └── export.py
```

## Contract tests

`tests/api/` includes a snapshot of `/openapi.json` at
`tests/api/openapi_snapshot.json`. To refresh after an intentional,
backwards-compatible change::

    .venv\Scripts\python.exe -m pytest tests/api/test_contract_openapi_snapshot.py --snapshot-update

Breaking changes (renamed/removed paths, dropped fields, narrowed
types) require an ADR before the snapshot is refreshed.

## CORS

CORS is permissive for `http://localhost:3000` / `http://127.0.0.1:3000`
(the Next.js dev origin). Production origins must be added via ADR.
