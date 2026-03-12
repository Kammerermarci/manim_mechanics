from __future__ import annotations

from dataclasses import dataclass
from typing import Union

import numpy as np
from manim import (
    Group,
    Circle,
    ImageMobject,
    BLACK,
    ManimColor,
)

from ..anchors import Anchor


@dataclass
class DiscStyle:
    fill: str = "#aaaaaa"       # kept for backward compatibility
    fill_shades: tuple[str, str, str] = ("#bfbfbf", "#aaaaaa", "#808080")
    fill_texture_size: int = 256
    stroke_width: float = 4   # slightly thicker outline for readability
    fill_opacity: float = 1.0


CenterLike = Union[np.ndarray, Anchor]


class Disc(Group):
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

        self.fill = self._make_fill_texture(self.radius)
        self.fill.set_z_index(z_index)
        self.circle = Circle(radius=self.radius)
        self.circle.set_stroke(color=BLACK, width=self.style.stroke_width, opacity=1.0)
        self.circle.set_fill(opacity=0.0)
        self.circle.set_z_index(z_index + 1)

        self.add(self.fill, self.circle)

        self._last_center: np.ndarray | None = None
        self._last_radius: float | None = None

        self._rebuild()
        self.add_updater(lambda mob, dt: mob._rebuild())

    def _blend_rgb(self, t: np.ndarray) -> np.ndarray:
        shades = self.style.fill_shades
        n = len(shades)
        if n == 0:
            c = np.array(ManimColor(self.style.fill).to_rgb(), dtype=float)
            return np.broadcast_to(c, t.shape + (3,))
        if n == 1:
            c = np.array(ManimColor(shades[0]).to_rgb(), dtype=float)
            return np.broadcast_to(c, t.shape + (3,))

        palette = np.array([ManimColor(c).to_rgb() for c in shades], dtype=float)
        pos = (t % 1.0) * n
        idx0 = np.floor(pos).astype(int) % n
        idx1 = (idx0 + 1) % n
        alpha = (pos - np.floor(pos))[..., None]
        return palette[idx0] * (1.0 - alpha) + palette[idx1] * alpha

    def _make_fill_texture(self, radius: float) -> ImageMobject:
        n = max(64, int(self.style.fill_texture_size))
        # Pixel centers in normalized [-1, 1] disc coordinates.
        coords = (np.arange(n, dtype=float) + 0.5) / n
        x = coords * 2.0 - 1.0
        y = coords * 2.0 - 1.0
        xx, yy = np.meshgrid(x, y)
        rr = np.sqrt(xx * xx + yy * yy)
        inside = rr <= 1.0

        # Angular coordinate in [0,1), with optional phase offset for aesthetics.
        theta = np.arctan2(yy, xx)
        t = (theta + np.pi) / (2.0 * np.pi)
        rgb = self._blend_rgb(t)

        rgba = np.zeros((n, n, 4), dtype=np.uint8)
        rgba[..., :3] = np.clip(rgb * 255.0, 0.0, 255.0).astype(np.uint8)
        rgba[..., 3] = np.where(inside, int(np.clip(self.style.fill_opacity * 255.0, 0.0, 255.0)), 0)

        img = ImageMobject(rgba)
        img.width = 2.0 * radius
        img.height = 2.0 * radius
        return img

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
        target_center = self._get_center()

        # Keep style in sync.
        self.circle.set_stroke(color=BLACK, width=self.style.stroke_width, opacity=1.0)

        # Radius updates scale the existing geometry so any ongoing rotation is preserved.
        if self._last_radius is None:
            self._last_radius = self.radius
        elif abs(self.radius - self._last_radius) > 1e-9:
            if self._last_radius > 1e-9:
                self.scale(self.radius / self._last_radius, about_point=self.get_center())
            else:
                self.circle.become(Circle(radius=self.radius))
                self.fill.become(self._make_fill_texture(self.radius))
            self._last_radius = self.radius

        # Position updates shift the whole disc without resetting orientation.
        if self._last_center is None:
            self.move_to(target_center)
        else:
            self.shift(target_center - self._last_center)
        self._last_center = target_center
