from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from manim import VGroup, VMobject

from ..anchors import Anchor


@dataclass
class ElementStyle:
    stroke_width: float = 4.0
    stroke_opacity: float = 1.0


class TwoPointElement(VGroup):
    def __init__(
        self,
        start: Anchor,
        end: Anchor,
        style: ElementStyle = ElementStyle(),
        z_index: int = 0,
        defer_rebuild: bool = False,   # <--- add
    ):
        super().__init__()
        self.start = start
        self.end = end
        self.style = style

        self.shape = VMobject()
        self.shape.set_z_index(z_index)
        self.shape.set_stroke(width=style.stroke_width, opacity=style.stroke_opacity)
        self.add(self.shape)

        # Register updater always (safe after __init__ finishes)
        self.add_updater(lambda mob, dt: mob._rebuild())

        # Only do the immediate rebuild if subclass is ready
        if not defer_rebuild:
            self._rebuild()


    def get_start(self) -> np.ndarray:
        return np.array(self.start.get_point(), dtype=float).reshape(3)

    def get_end(self) -> np.ndarray:
        return np.array(self.end.get_point(), dtype=float).reshape(3)

    def _rebuild(self) -> None:
        """Recompute self.shape points from anchors."""
        raise NotImplementedError
