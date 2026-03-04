from __future__ import annotations

from dataclasses import dataclass
from typing import Union

import numpy as np
from manim import VGroup, Circle, BLACK, ManimColor

from ..anchors import Anchor


@dataclass
class DiscStyle:
    fill: str = "#aaaaaa"       # darker gray face
    stroke_width: float = 2.5   # match your other symbols
    fill_opacity: float = 1.0


CenterLike = Union[np.ndarray, Anchor]


class Disc(VGroup):
    """
    Filled disc (circle) with black outline.

    Parameters
    ----------
    center:
        Either a numpy point (x,y,z) or an Anchor.
    radius:
        Disc radius (scene units).
    """

    def __init__(
        self,
        center: CenterLike,
        radius: float,
        style: DiscStyle = DiscStyle(),
        z_index: int = 0,
    ):
        super().__init__()
        self.center = center
        self.radius = float(radius)
        self.style = style

        self.circle = Circle(radius=self.radius)
        self.circle.set_stroke(color=BLACK, width=self.style.stroke_width, opacity=1.0)
        self.circle.set_fill(color=ManimColor(self.style.fill), opacity=self.style.fill_opacity)
        self.circle.set_z_index(z_index)

        self.add(self.circle)

        self._rebuild()
        self.add_updater(lambda mob, dt: mob._rebuild())

    def _get_center(self) -> np.ndarray:
        # Anchor in this project is likely a typing.Protocol -> cannot use isinstance in Py3.12
        if hasattr(self.center, "get_point"):
            return np.array(self.center.get_point(), dtype=float).reshape(3)
        return np.array(self.center, dtype=float).reshape(3)

    def set_center(self, center: CenterLike) -> "Disc":
        self.center = center
        return self

    def set_radius(self, radius: float) -> "Disc":
        self.radius = float(radius)
        return self

    def _rebuild(self) -> None:
        # rebuild radius + position (safe even if you later animate radius)
        self.circle.become(
            Circle(radius=self.radius)
            .set_stroke(color=BLACK, width=self.style.stroke_width, opacity=1.0)
            .set_fill(color=ManimColor(self.style.fill), opacity=self.style.fill_opacity)
            .move_to(self._get_center())
        )