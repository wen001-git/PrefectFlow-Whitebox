"""Composable transform pipeline.

Function-composition only — no class hierarchy, no state. The two public
helpers :func:`compose` and :func:`pipe` are inspired by the standard
functional idiom and let callers wire MRC transforms (or any other pure
DataFrame-shaped transforms) into a single callable.

The functions are intentionally generic so that the transform layer never
needs to grow servicer-specific orchestration code.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import reduce
from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

Transform = Callable[[T], U]


def compose(*funcs: Callable[..., object]) -> Callable[..., object]:
    """Right-to-left function composition.

    ``compose(f, g, h)(x) == f(g(h(x)))``. With zero functions returns the
    identity function — convenient as a neutral element when conditionally
    building pipelines.
    """
    if not funcs:
        return lambda x: x

    def _composed(x: object) -> object:
        return reduce(lambda acc, fn: fn(acc), reversed(funcs), x)

    return _composed


def pipe(value: T, *funcs: Callable[..., object]) -> object:
    """Apply ``funcs`` to ``value`` left-to-right.

    ``pipe(x, f, g, h) == h(g(f(x)))``. Mirrors ``toolz.pipe`` and Elixir's
    ``|>`` operator. Pure: no side effects, no IO.
    """
    result: object = value
    for fn in funcs:
        result = fn(result)
    return result


def identity(x: T) -> T:
    """Return ``x`` unchanged. Useful as a placeholder in conditional pipes."""
    return x


__all__ = ["Transform", "compose", "identity", "pipe"]
