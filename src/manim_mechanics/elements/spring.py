from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from manim import VMobject

from .base import TwoPointElement, ElementStyle


@dataclass
class SpringStyle(ElementStyle):
    n_coils: int = 8
    amplitude: float = 0.15
    end_fraction: float = 0.12  # fraction of total length kept straight at each end


class Spring(TwoPointElement):
    """2D spring (visual) between two anchors."""

    def __init__(self, start, end, style: SpringStyle = SpringStyle(), **kwargs):
        self.spring_style = style
        super().__init__(start, end, style=style, **kwargs)

    def _rebuild(self) -> None:
        a = self.get_start()
        b = self.get_end()
        v = b - a
        L = float(np.linalg.norm(v))
        if L < 1e-9:
            self.shape.set_points_as_corners([a, a + np.array([1e-6, 0, 0])])
            return

        e = v / L

        # Perpendicular in XY plane
        perp = np.array([-e[1], e[0], 0.0])
        perp_norm = float(np.linalg.norm(perp))
        if perp_norm < 1e-9:
            perp = np.array([0.0, 1.0, 0.0])
        else:
            perp = perp / perp_norm

        n = max(2, int(self.spring_style.n_coils))
        amp = float(self.spring_style.amplitude)
        end_frac = float(self.spring_style.end_fraction)

        x0 = 0.0
        x1 = end_frac * L
        x2 = (1.0 - end_frac) * L
        x3 = L

        # Build polyline points along the spring axis
        pts = [a + e * x0, a + e * x1]

        # coils region
        coil_L = max(1e-9, x2 - x1)
        # Use 2n segments for zig-zag: peaks alternate +/-
        m = 2 * n
        for k in range(1, m):
            s = coil_L * (k / m)
            sign = 1.0 if (k % 2 == 1) else -1.0
            pts.append(a + e * (x1 + s) + perp * (sign * amp))

        pts += [a + e * x2, a + e * x3]

        self.shape.set_points_as_corners(pts)
