"""Shared TestClient fixture for whitebox.api tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from whitebox.api.main import app


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--snapshot-update",
        action="store_true",
        default=False,
        help="Overwrite OpenAPI / contract snapshots with the current output.",
    )


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
