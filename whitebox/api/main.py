"""FastAPI app entrypoint for whitebox.api.

Run locally with::

    uvicorn whitebox.api.main:app --reload

OpenAPI schema is published at ``/openapi.json`` for FE codegen.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from whitebox import __version__
from whitebox.api.routers import diff, export, health, lineage, runs, sheets

app: FastAPI = FastAPI(
    title="PrefectFlow-Whitebox API",
    version=__version__,
    description=(
        "Skeleton API for the whitebox re-implementation of remit_validation. "
        "All business endpoints currently return fixture data; real wiring is "
        "scheduled for the d-api-contracts todo."
    ),
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(runs.router)
app.include_router(sheets.router)
app.include_router(diff.router)
app.include_router(lineage.router)
app.include_router(export.router)
