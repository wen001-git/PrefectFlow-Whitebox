# Smoke test: package importable and version exposed.

from whitebox import __version__


def test_version_exposed() -> None:
    assert isinstance(__version__, str)
    assert __version__ != ""
