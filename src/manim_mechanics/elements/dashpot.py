from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from manim import VGroup, Line

from .base import TwoPointElement, ElementStyle


@dataclass
class DashpotStyle(ElementStyle):
    # Fixed cylinder dimensions (world units). If None, computed ONCE from initial L0.
    body_length: float | None = None
    width: float | None = None

    # Fixed rod lengths (world units). If None, computed ONCE from initial L0.
    rod_start: float | None = None   # start anchor -> cylinder left wall center
    rod_end: float | None = None     # piston center -> end anchor

    # Defaults used ONLY when the above are None (evaluated once at init using L0)
    body_fraction: float = 0.40
    width_fraction: float = 0.18
    rod_start_fraction: float = 0.22

    piston_height_factor: float = 0.80

    # Robustness clamps (world units)
    min_body_length: float = 0.25
    min_width: float = 0.08
    max_width_fraction: float = 0.35


class Dashpot(TwoPointElement):
    """2D dashpot: fixed-size U-body + sliding piston + fixed rod lengths.

    Rule:
    - cylinder is attached to start via fixed rod_start
    - piston is attached to end via fixed rod_end
    - piston is initialized in the middle of the cylinder at t=0
    - after init: only piston position/orientation updates; no resizing; no clamping
    """

    def __init__(self, start, end, style: DashpotStyle = DashpotStyle(), **kwargs):
        self.dashpot_style = style

        # Prevent base from calling _rebuild() before we create the line parts
        super().__init__(start, end, style=style, defer_rebuild=True, **kwargs)

        # Replace the placeholder VMobject from base
        self.remove(self.shape)

        # Primitives
        self.rod_start_ln = Line()
        self.body_left_ln = Line()
        self.body_top_ln = Line()
        self.body_bottom_ln = Line()
        self.rod_end_ln = Line()
        self.piston_ln = Line()

        self.shape = VGroup(
            self.rod_start_ln,
            self.body_left_ln, self.body_top_ln, self.body_bottom_ln,
            self.rod_end_ln,
            self.piston_ln,
        )
        self.shape.set_stroke(width=style.stroke_width, opacity=style.stroke_opacity)
        self.add(self.shape)

        # Resolve fixed geometry ONCE (and set rod_end so piston starts centered)
        self._resolve_geometry_and_center_piston()

        # First frame
        self._rebuild()

    def _resolve_geometry_and_center_piston(self) -> None:
        """Compute fixed geometry values once, and choose rod_end so piston starts centered."""
        a = self.get_start()
        b = self.get_end()
        v0 = b - a
        L0 = float(np.linalg.norm(v0))
        L0 = max(L0, 1e-6)
        e0 = v0 / L0

        st = self.dashpot_style

        # width (fixed)
        w0 = st.width if st.width is not None else st.width_fraction * L0
        w_max = st.max_width_fraction * L0
        w = float(np.clip(w0, st.min_width, max(st.min_width, w_max)))

        # body length (fixed)
        LB0 = st.body_length if st.body_length is not None else st.body_fraction * L0
        LB = float(max(st.min_body_length, LB0))

        # rod_start (fixed)
        rs0 = st.rod_start if st.rod_start is not None else st.rod_start_fraction * L0
        rs = float(max(0.0, rs0))

        # Cylinder placement at t=0
        body_left_center0 = a + e0 * rs
        piston_center0 = body_left_center0 + e0 * (0.5 * LB)  # mid-cylinder at init

        # rod_end (fixed):
        # If user didn't specify rod_end, pick it so piston starts mid-cylinder:
        # piston = b - e0*re  =>  re = dot(b - piston, e0)
        if st.rod_end is None:
            re = float(np.dot(b - piston_center0, e0))
            # Keep it non-negative; if cylinder ends up "past" b, this will go negative.
            # In that case we just take absolute; you said you'll fit manually if needed.
            re = float(abs(re))
        else:
            re = float(max(0.0, st.rod_end))

        self._geom = {"w": w, "LB": LB, "rs": rs, "re": re}

    def _rebuild(self) -> None:
        a = self.get_start()
        b = self.get_end()

        v = b - a
        L = float(np.linalg.norm(v))
        if L < 1e-9:
            eps = np.array([1e-6, 0.0, 0.0])
            for ln in (
                self.rod_start_ln, self.body_left_ln, self.body_top_ln,
                self.body_bottom_ln, self.rod_end_ln, self.piston_ln
            ):
                ln.put_start_and_end_on(a, a + eps)
            return

        e = v / L

        # Perpendicular in XY plane
        perp = np.array([-e[1], e[0], 0.0])
        pn = float(np.linalg.norm(perp))
        perp = perp / pn if pn > 1e-9 else np.array([0.0, 1.0, 0.0])

        w = self._geom["w"]
        LB = self._geom["LB"]
        rs = self._geom["rs"]
        re = self._geom["re"]
        piston_h = w * float(self.dashpot_style.piston_height_factor)

        # Fixed cylinder attachment (start -> cylinder)
        body_left_center = a + e * rs
        body_open_center = body_left_center + e * LB

        left_top = body_left_center + perp * (w / 2)
        left_bot = body_left_center - perp * (w / 2)
        open_top = body_open_center + perp * (w / 2)
        open_bot = body_open_center - perp * (w / 2)

        # Fixed piston attachment (piston -> end)
        # This guarantees right rod length is constant (= re).
        piston_center = b - e * re
        piston_top = piston_center + perp * (piston_h / 2)
        piston_bot = piston_center - perp * (piston_h / 2)

        # Draw primitives
        self.rod_start_ln.put_start_and_end_on(a, body_left_center)

        self.body_left_ln.put_start_and_end_on(left_top, left_bot)
        self.body_top_ln.put_start_and_end_on(left_top, open_top)
        self.body_bottom_ln.put_start_and_end_on(left_bot, open_bot)

        self.piston_ln.put_start_and_end_on(piston_top, piston_bot)
        self.rod_end_ln.put_start_and_end_on(piston_center, b)