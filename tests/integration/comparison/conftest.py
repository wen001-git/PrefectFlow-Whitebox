"""conftest.py — integration comparison suite.

Registers custom pytest markers so --strict-markers does not reject them.
"""


def pytest_configure(config):  # type: ignore[no-untyped-def]
    config.addinivalue_line(
        "markers",
        "slow: mark integration test as slow (typically > 10 s); excluded from fast CI runs",
    )
