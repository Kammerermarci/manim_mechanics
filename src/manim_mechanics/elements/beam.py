from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from manim import (
    VGroup,
    RoundedRectangle,
    Circle,
    BLACK,
    ManimColor,
    interpolate_color,
)

from .base import TwoPointElement, ElementStyle


@dataclass
class BeamStyle(ElementStyle):
    # Thickness (what you called "width")
    thickness: float | None = None
    thickness_fraction: float = 0.10
    min_thickness: float = 0.08
    max_thickness_fraction: float = 0.25

    # Stroke to match supports
    stroke_width: float = 2.5

    # Gradient colors (edge -> center)
    edge_fill: str = "#8d8d8d"
    center_fill: str = "#d9d9d9"

    # Gradient layering
    shade_layers: int = 18
    shade_inset_factor: float = 0.42  # fraction of thickness used as max inset

    # End holes
    hole_radius_factor: float = 0.33
    hole_fill: str = "#b7b7b7"
    hole_stroke_width: float = 2.5


class Beam(TwoPointElement):
    """Rounded bar beam with end holes. Start/end anchors are hole centers."""

    def __init__(self, start, end, width: float | None = None, style: BeamStyle = BeamStyle(), **kwargs):
        if width is not None:
            style = BeamStyle(**{**style.__dict__, "thickness": float(width)})

        self.beam_style = style

        # Prevent base placeholder rebuild before multi-part shape exists
        super().__init__(start, end, style=style, defer_rebuild=True, **kwargs)
        self.remove(self.shape)

        self.shape = VGroup()
        self.add(self.shape)

        self._resolve_geometry()
        self._rebuild()

    def _resolve_geometry(self) -> None:
        a = self.get_start()
        b = self.get_end()
        L0 = float(np.linalg.norm(b - a))
        L0 = max(L0, 1e-6)

        st = self.beam_style
        if st.thickness is None:
            t0 = st.thickness_fraction * L0
            t_max = st.max_thickness_fraction * L0
            t = float(np.clip(t0, st.min_thickness, max(st.min_thickness, t_max)))
        else:
            t = float(st.thickness)

        self._geom = {"t": t}

    def _build_local(self, L: float) -> VGroup:
        """Build beam in local coords: origin at midpoint; x-axis along beam."""
        st = self.beam_style
        t = self._geom["t"]
        r = 0.5 * t

        # Pill length: holes are at ±L/2, and end caps extend ±t/2 beyond those centers
        pill_len = L + t

        # Gradient layers
        n = max(2, int(st.shade_layers))
        inset_max = float(st.shade_inset_factor) * t

        edge = ManimColor(st.edge_fill)
        center = ManimColor(st.center_fill)

        layers = VGroup()
        for i in range(n):
            a = i / (n - 1)
            inset = a * inset_max

            w_i = max(1e-6, pill_len - 2 * inset)
            h_i = max(1e-6, t - 2 * inset)
            r_i = max(1e-6, 0.5 * h_i)

            col = interpolate_color(edge, center, a)

            rr = RoundedRectangle(width=w_i, height=h_i, corner_radius=r_i).move_to([0, 0, 0])
            rr.set_fill(col, opacity=1.0)

            # Only outermost has stroke
            if i == 0:
                rr.set_stroke(BLACK, width=st.stroke_width, opacity=1.0)
            else:
                rr.set_stroke(opacity=0.0)

            layers.add(rr)

        # End holes
        hole_r = float(st.hole_radius_factor) * t
        holeL = Circle(radius=hole_r).move_to([-L / 2, 0, 0])
        holeR = Circle(radius=hole_r).move_to([+L / 2, 0, 0])

        for h in (holeL, holeR):
            h.set_fill(ManimColor(st.hole_fill), opacity=1.0)
            h.set_stroke(BLACK, width=st.hole_stroke_width, opacity=1.0)

        return VGroup(layers, holeL, holeR)

    def _rebuild(self) -> None:
        a = self.get_start()
        b = self.get_end()

        v = b - a
        L = float(np.linalg.norm(v))
        if L < 1e-9:
            return

        e = v / L
        ang = float(np.arctan2(e[1], e[0]))
        center = 0.5 * (a + b)

        local = self._build_local(L)
        local.rotate(ang).shift(center)

        # One rigid transform for everything -> holes cannot "wander"
        self.shape.become(local)