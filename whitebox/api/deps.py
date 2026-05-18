"""Dependency-injection shims.

Real implementations (auth, DB session, registry handles) land in
later todos. For now we return inert dummies so routers can declare
their dependency contracts.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentUser:
    username: str
    is_authenticated: bool


@dataclass(frozen=True)
class DbSession:
    """Placeholder for a future DB / registry session handle."""

    name: str


def get_current_user() -> CurrentUser:
    """Stub auth dependency — always returns an anonymous user."""
    return CurrentUser(username="anonymous", is_authenticated=False)


def get_db_session() -> DbSession:
    """Stub DB session dependency — returns a named dummy."""
    return DbSession(name="stub-session")
