from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

import numpy as np

try:
    from manim import Mobject
except Exception:  # pragma: no cover
    Mobject = object  # type: ignore


class Anchor(Protocol):
    """An Anchor returns a 3D point (Manim uses 3D vectors even for 2D scenes)."""

    def get_point(self) -> np.ndarray:
        ...


@dataclass(frozen=True)
class PointAnchor:
    """Anchor backed by a callable returning a point."""

    _getter: Callable[[], np.ndarray]

    def get_point(self) -> np.ndarray:
        p = self._getter()
        p = np.array(p, dtype=float).reshape(3)
        return p

    @staticmethod
    def from_mobject(mobj: Mobject) -> "PointAnchor":
        return PointAnchor(lambda: mobj.get_center())

    @staticmethod
    def from_callable(fn: Callable[[], np.ndarray]) -> "PointAnchor":
        return PointAnchor(fn)

    def shifted(self, offset) -> "PointAnchor":
        off = np.array(offset, dtype=float).reshape(3)
        return PointAnchor(lambda: self.get_point() + off)

    def __add__(self, offset) -> "PointAnchor":
        return self.shifted(offset)

    def __radd__(self, offset) -> "PointAnchor":
        return self.shifted(offset)

    def __sub__(self, offset) -> "PointAnchor":
        return self.shifted(-np.array(offset, dtype=float).reshape(3))
