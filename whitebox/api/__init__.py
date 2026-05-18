"""FastAPI application package for PrefectFlow-Whitebox.

Skeleton stage (P2.3): routers return plausible fixture data so the
Next.js frontend can be built against a stable OpenAPI surface. Real
business logic will be wired in by d-api-contracts and subsequent todos.
"""

from whitebox.api.main import app

__all__ = ["app"]
