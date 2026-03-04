from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from manim import RoundedRectangle, BLACK

from .base import TwoPointElement, ElementStyle


@dataclass
class SolidLineStyle(ElementStyle):
    # Thickness in world units. If None, resolved once from initial length.
    thickness: float | None = None

    # Default: ~1/4 of Beam default thickness logic
    thickness_fraction: float = 0.15 / 4
    min_thickness: float = 0.08 / 4
    max_thickness_fraction: float = 0.25 / 4

    fill = BLACK
    fill_opacity: float = 1.0


class SolidLine(TwoPointElement):
    """Solid black thick line between two anchors (capsule)."""

    def __init__(
        self,
        start,
        end,
        width: float | None = None,
        style: SolidLineStyle = SolidLineStyle(),
        **kwargs,
    ):
        # width is an alias for thickness (world units)
        if width is not None:
            style = SolidLineStyle(**{**style.__dict__, "thickness": float(width)})

        self.line_style = style

        # Avoid base calling _rebuild() before we create our shape
        super().__init__(start, end, style=style, defer_rebuild=True, **kwargs)

        # Replace base placeholder VMobject
        self.remove(self.shape)

        # Valid initial shape
        eps = 1e-6
        self.shape = RoundedRectangle(width=eps, height=eps, corner_radius=0.0)
        self.add(self.shape)

        self._resolve_geometry()
        self._rebuild()

    def _resolve_geometry(self) -> None:
        a = self.get_start()
        b = self.get_end()
        L0 = float(np.linalg.norm(b - a))
        L0 = max(L0, 1e-6)

        st = self.line_style
        if st.thickness is None:
            t0 = st.thickness_fraction * L0
            t_max = st.max_thickness_fraction * L0
            t = float(np.clip(t0, st.min_thickness, max(st.min_thickness, t_max)))
        else:
            t = float(st.thickness)

        self._geom = {"t": t}

    def _rebuild(self) -> None:
        st = self.line_style

        a = self.get_start()
        b = self.get_end()
        v = b - a
        L = float(np.linalg.norm(v))
        if L < 1e-9:
            return

        e = v / L
        ang = float(np.arctan2(e[1], e[0]))
        center = 0.5 * (a + b)

        t = float(self._geom["t"])
        r = 0.5 * t

        pill_len = L + t  # <-- key fix
        local = RoundedRectangle(width=pill_len, height=t, corner_radius=r).move_to([0, 0, 0])
        local.set_fill(st.fill, opacity=st.fill_opacity)
        local.set_stroke(opacity=0.0)

        self.shape.become(local.rotate(ang).shift(center))