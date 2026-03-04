from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal

import numpy as np
from manim import (
    VGroup,
    Dot,
    Tex,
    Circle,
    BLACK,
    ManimColor,
    interpolate_color,
)

from .anchors import PointAnchor


@dataclass
class NodeStyle:
    radius: float = 0.06
    label_scale: float = 0.5
    label_buff: float = 0.15

    # marker can be a simple dot, shaded "mass", or a larger "pin"
    marker: Literal["dot", "mass", "pin"] = "dot"

    # mass shading settings
    mass_layers: int = 16
    mass_edge_color: str = "#0e7345"   # border color (alpha ff ignored)
    mass_center_color: str = "#1abe72" # center color (alpha ff ignored)
    mass_stroke_color = BLACK
    mass_stroke_width: float = 2.5

    # pin settings
    pin_scale: float = 1.8             # >1 makes it larger than dot radius
    pin_fill_color: str = "#e6e6e6"
    pin_stroke_color = BLACK
    pin_stroke_width: float = 2.5


class Node2D(VGroup):
    """A simple point-mass/node with an exposed anchor."""

    def __init__(
        self,
        position: np.ndarray,
        label: Optional[str] = None,
        style: NodeStyle = NodeStyle(),
        label_direction: np.ndarray | None = None,
        **dot_kwargs,
    ):
        super().__init__()

        self._style = style
        self._label_dir = np.array([1.0, 0.0, 0.0]) if label_direction is None else np.array(label_direction, dtype=float)
        self._label_dir = self._label_dir / (np.linalg.norm(self._label_dir) + 1e-12)

        pos = np.array(position, dtype=float).reshape(3)

        # Marker (keep attribute name .dot for compatibility)
        if style.marker == "mass":
            self.dot = self._make_mass_marker(pos)
        elif style.marker == "pin":
            self.dot = self._make_pin_marker(pos)
        else:
            self.dot = Dot(point=pos, radius=style.radius, **dot_kwargs)

        self.add(self.dot)

        # Label
        self.label = None
        if label is not None:
            self.label = Tex(label).scale(style.label_scale)
            self.add(self.label)

            # Keep label attached automatically
            def _label_update(m, dt):
                m.next_to(self.dot, direction=self._label_dir, buff=style.label_buff)

            self.label.add_updater(_label_update)
            _label_update(self.label, 0)

        # Anchor: center of marker
        self.anchor = PointAnchor.from_mobject(self.dot)

    def _make_mass_marker(self, position: np.ndarray) -> VGroup:
        """Concentric circles approximating a radial gradient."""
        r = float(self._style.radius)
        n = max(2, int(self._style.mass_layers))

        edge = ManimColor(self._style.mass_edge_color)
        center = ManimColor(self._style.mass_center_color)

        layers = VGroup()

        # Outer -> inner circles
        for i in range(n):
            ri = r * (1.0 - i / n)
            alpha = i / (n - 1)
            col = interpolate_color(edge, center, alpha)

            c = Circle(radius=ri).move_to(position)
            c.set_fill(col, opacity=1.0)

            # Only outermost gets the stroke
            if i == 0:
                c.set_stroke(self._style.mass_stroke_color, width=self._style.mass_stroke_width, opacity=1.0)
            else:
                c.set_stroke(opacity=0.0)

            layers.add(c)

        return layers

    def _make_pin_marker(self, position: np.ndarray) -> Circle:
        """A larger circular pin: gray fill with black stroke."""
        r = float(self._style.radius) * float(self._style.pin_scale)
        c = Circle(radius=r).move_to(position)
        c.set_fill(ManimColor(self._style.pin_fill_color), opacity=1.0)
        c.set_stroke(self._style.pin_stroke_color, width=self._style.pin_stroke_width, opacity=1.0)
        return c

    def set_position(self, p: np.ndarray) -> "Node2D":
        self.dot.move_to(np.array(p, dtype=float).reshape(3))
        return self

    def set_label_direction(self, direction: np.ndarray) -> "Node2D":
        d = np.array(direction, dtype=float)
        self._label_dir = d / (np.linalg.norm(d) + 1e-12)
        return self