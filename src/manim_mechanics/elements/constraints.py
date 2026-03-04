from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Union

import numpy as np
from manim import (
    VGroup,
    Polygon,
    Circle,
    RoundedRectangle,
    Rectangle,
    Line,
    BLACK,
    ManimColor,
    VMobject,   # <-- add this
)

from ..anchors import Anchor

#AngleLike = Union[float, Callable[[], float]]  # may also be a ValueTracker (has .get_value())

@dataclass
class ConstraintStyle:
    size: float = 0.2
    ground_lines: int = 5
    stroke_width: float = 4.0


class _ConstraintBase(VGroup):
    """Base constraint symbol attached to a single anchor."""

    def __init__(self, anchor: Anchor, style: ConstraintStyle = ConstraintStyle(), z_index: int = -1):
        super().__init__()
        self.anchor = anchor
        self.style = style
        self.shape = VMobject().set_z_index(z_index)
        self.shape.set_stroke(width=style.stroke_width)
        self.add(self.shape)

        self._rebuild()
        self.add_updater(lambda mob, dt: mob._rebuild())

    def get_pos(self) -> np.ndarray:
        return np.array(self.anchor.get_point(), dtype=float).reshape(3)

    def _rebuild(self) -> None:
        raise NotImplementedError


AngleLike = Union[float, Callable[[], float]]  # you can also pass a ValueTracker (handled below)


@dataclass
class PinnedSupportStyle:
    # Global scale for the symbol (world units-ish)
    size: float = 1/4

    # Hole geometry
    hole_radius: float | None = None          # if None -> derived from size
    hole_fill: str = "#b7b7b7"
    hole_stroke_width: float = 2.5

    # Bracket geometry
    bracket_fill: str = "#e6e6e6"
    bracket_stroke_width: float = 2.5
    bracket_outer_pad: float | None = None    # if None -> derived from size
    bracket_stem_height: float | None = None  # distance from outer arc to bracket bottom
    bracket_bottom_width: float | None = None
    arc_left_deg: float = 160.0               # shape of rounded top
    arc_right_deg: float = 20.0
    arc_points: int = 40                      # more points = smoother arc

    # Base plate geometry
    base_width: float | None = None
    base_height: float | None = None
    base_fill: str = "#808080"
    base_stroke_width: float = 2.5
    base_corner_radius: float | None = None

    # Small bolts (decor)
    bolt_width: float | None = None
    bolt_height: float | None = None
    bolt_fill: str = "#dfdede"
    bolt_stroke_width: float = 1.5
    bolt_offset_x: float | None = None

    # Ground line (thin)
    ground_width: float | None = None
    ground_stroke_width: float = 6.0
    ground_gap: float | None = None

    # Ground trapezoid (like FixedSupport)
    trap_fill: str = "#e6e6e6"
    trap_height: float | None = None      # if None -> 2.0 * size
    trap_bottom_ratio: float = 0.65        # bottom width = ratio * top width


class PinnedSupport(VGroup):
    """
    Pinned support symbol with anchor at the hole center.

    Parameters
    ----------
    anchor:
        Anchor whose point is the hole center.
    angle:
        Rotation about the anchor (degrees). Can be:
        - float
        - callable returning float
        - ValueTracker-like object with .get_value()
    """

    def __init__(
        self,
        anchor: Anchor,
        style: PinnedSupportStyle = PinnedSupportStyle(),
        angle: AngleLike = 0.0,
        z_index: int = -1,
    ):
        super().__init__()
        self.anchor = anchor
        self.style = style
        self.angle = angle

        # Actual parts (must be valid shapes; Polygon cannot be empty)
        eps = 1e-6
        self.bracket = Polygon(
            np.array([0.0, 0.0, 0.0]),
            np.array([eps, 0.0, 0.0]),
            np.array([0.0, eps, 0.0]),
        )
        self.hole = Circle(radius=eps)
        self.base = RoundedRectangle(width=eps, height=eps, corner_radius=0.0)
        self.bolt_l = Rectangle(width=eps, height=eps)
        self.bolt_r = Rectangle(width=eps, height=eps)
        self.ground = Line(np.array([0.0, 0.0, 0.0]), np.array([eps, 0.0, 0.0]))
        self.trap = Polygon(
            np.array([0.0, 0.0, 0.0]),
            np.array([eps, 0.0, 0.0]),
            np.array([0.0, eps, 0.0]),
        )   

        for m in (self.trap, self.ground, self.base, self.bracket, self.hole, self.bolt_l, self.bolt_r):
            m.set_z_index(z_index)

        self.add(self.trap, self.ground, self.base, self.bolt_l, self.bolt_r, self.bracket, self.hole)

        # Build templates in LOCAL coordinates where hole center is at origin
        self._build_templates()

        # First build + updater
        self._rebuild()
        self.add_updater(lambda mob, dt: mob._rebuild())

    def _get_angle(self) -> float:
        """Return rotation in radians; self.angle is stored/treated in DEGREES."""
        a = self.angle
        if hasattr(a, "get_value"):
            deg = float(a.get_value())
        elif callable(a):
            deg = float(a())
        else:
            deg = float(a)

        return np.deg2rad(deg)

    def set_angle(self, angle: float) -> "PinnedSupport":
        self.angle = float(angle)
        return self

    def _build_templates(self) -> None:
        s = float(self.style.size)

        # Resolve dimensions (defaults tuned to match the reference look)
        r_h = float(self.style.hole_radius) if self.style.hole_radius is not None else 0.38 * s
        pad = float(self.style.bracket_outer_pad) if self.style.bracket_outer_pad is not None else 0.22 * s
        r_o = r_h + pad

        stem_h = float(self.style.bracket_stem_height) if self.style.bracket_stem_height is not None else 1.65 * s
        y_bottom = -(r_o + stem_h)

        w_bottom = float(self.style.bracket_bottom_width) if self.style.bracket_bottom_width is not None else 2.35 * s

        base_w = float(self.style.base_width) if self.style.base_width is not None else 3.8 * s
        base_h = float(self.style.base_height) if self.style.base_height is not None else 0.42 * s
        corner_r = float(self.style.base_corner_radius) if self.style.base_corner_radius is not None else 0.10 * s

        bolt_w = float(self.style.bolt_width) if self.style.bolt_width is not None else 0.4 * s
        bolt_h = float(self.style.bolt_height) if self.style.bolt_height is not None else 0.12 * s
        bolt_dx = float(self.style.bolt_offset_x) if self.style.bolt_offset_x is not None else 1.5 * s

        ground_w = float(self.style.ground_width) if self.style.ground_width is not None else 5 * s
        ground_gap = float(self.style.ground_gap) if self.style.ground_gap is not None else 0 * s

        # --- Bracket outline (polygon with rounded top approximated by arc points) ---
        thL = np.deg2rad(self.style.arc_left_deg)
        thR = np.deg2rad(self.style.arc_right_deg)

        # Build arc points from left to right
        thetas = np.linspace(thL, thR, int(self.style.arc_points))
        arc_pts = [np.array([r_o * np.cos(t), r_o * np.sin(t), 0.0]) for t in thetas]

        left_arc = arc_pts[0]
        right_arc = arc_pts[-1]

        left_bottom = np.array([-w_bottom / 2, y_bottom, 0.0])
        right_bottom = np.array([w_bottom / 2, y_bottom, 0.0])

        # polygon points: bottom-left -> left-arc -> arc -> right-arc -> bottom-right
        bracket_pts = [left_bottom, left_arc] + arc_pts[1:-1] + [right_arc, right_bottom]

        bracket_tpl = Polygon(*bracket_pts)
        bracket_tpl.set_stroke(color=BLACK, width=self.style.bracket_stroke_width, opacity=1.0)
        bracket_tpl.set_fill(color=ManimColor(self.style.bracket_fill), opacity=1.0)

        # --- Hole (drawn on top) ---
        hole_tpl = Circle(radius=r_h)
        hole_tpl.set_stroke(color=BLACK, width=self.style.hole_stroke_width, opacity=1.0)
        hole_tpl.set_fill(color=ManimColor(self.style.hole_fill), opacity=1.0)

        # --- Base plate (rounded rectangle) ---
        base_center = np.array([0.0, y_bottom - base_h / 2, 0.0])
        base_tpl = RoundedRectangle(width=base_w, height=base_h, corner_radius=corner_r)
        base_tpl.move_to(base_center)
        base_tpl.set_stroke(color=BLACK, width=self.style.base_stroke_width, opacity=1.0)
        base_tpl.set_fill(color=ManimColor(self.style.base_fill), opacity=1.0)

        # --- Bolts (small rectangles sitting on base) ---
        bolt_y = y_bottom + 0.10 * s
        bolt_l_tpl = Rectangle(width=bolt_w, height=bolt_h)
        bolt_r_tpl = Rectangle(width=bolt_w, height=bolt_h)
        bolt_l_tpl.move_to(np.array([-bolt_dx, bolt_y, 0.0]))
        bolt_r_tpl.move_to(np.array([+bolt_dx, bolt_y, 0.0]))
        for b in (bolt_l_tpl, bolt_r_tpl):
            b.set_stroke(color=BLACK, width=self.style.bolt_stroke_width, opacity=1.0)
            b.set_fill(color=ManimColor(self.style.bolt_fill), opacity=1.0)

        # --- Ground line ---
        y_ground = y_bottom - base_h - ground_gap
        ground_tpl = Line(
            np.array([-ground_w / 2, y_ground, 0.0]),
            np.array([+ground_w / 2, y_ground, 0.0]),
        )
        ground_tpl.set_stroke(color=BLACK, width=self.style.ground_stroke_width, opacity=1.0)

        # --- Ground trapezoid (like FixedSupport), touching the ground line ---
        trap_h = float(self.style.trap_height) if self.style.trap_height is not None else 1.3 * s
        top_w = ground_w
        bot_w = float(self.style.trap_bottom_ratio) * top_w

        trap_pts = [
            np.array([-top_w / 2, y_ground, 0.0]),
            np.array([+top_w / 2, y_ground, 0.0]),
            np.array([+bot_w / 2, y_ground - trap_h, 0.0]),
            np.array([-bot_w / 2, y_ground - trap_h, 0.0]),
        ]
        trap_tpl = Polygon(*trap_pts)
        trap_tpl.set_stroke(opacity=0.0)
        trap_tpl.set_fill(color=ManimColor(self.style.trap_fill), opacity=1.0)

        # Store templates
        self._tpl = {
            "bracket": bracket_tpl,
            "hole": hole_tpl,
            "base": base_tpl,
            "bolt_l": bolt_l_tpl,
            "bolt_r": bolt_r_tpl,
            "ground": ground_tpl,
            "trap": trap_tpl,
        }

    def _rebuild(self) -> None:
        p = np.array(self.anchor.get_point(), dtype=float).reshape(3)
        ang = self._get_angle()

        # Rotate everything about the hole center (local origin), then shift to anchor point
        about = np.array([0.0, 0.0, 0.0])

        self.bracket.become(self._tpl["bracket"].copy().rotate(ang, about_point=about).shift(p))
        self.hole.become(self._tpl["hole"].copy().rotate(ang, about_point=about).shift(p))
        self.base.become(self._tpl["base"].copy().rotate(ang, about_point=about).shift(p))
        self.bolt_l.become(self._tpl["bolt_l"].copy().rotate(ang, about_point=about).shift(p))
        self.bolt_r.become(self._tpl["bolt_r"].copy().rotate(ang, about_point=about).shift(p))
        self.trap.become(self._tpl["trap"].copy().rotate(ang, about_point=about).shift(p))
        self.ground.become(self._tpl["ground"].copy().rotate(ang, about_point=about).shift(p))


class FixedSupport(VGroup):
    """Fixed support: thick black bar with a gray trapezoid underneath.

    - Anchor is at the center of the bar.
    - `angle` is in DEGREES.
    - Trapezoid is wider at the bar and narrower away from it, with no gap.
    - `size` is a direct scale parameter you pass in.
    """

    def __init__(
        self,
        anchor: Anchor,
        size: float = 0.2,
        angle: AngleLike = 0.0,          # DEGREES
        bar_stroke_width: float = 6.0,
        trap_fill: str = "#e6e6e6",
        z_index: int = -2,
    ):
        super().__init__()
        self.anchor = anchor
        self.size = float(size)
        self.angle = angle
        self.bar_stroke_width = float(bar_stroke_width)
        self.trap_fill = trap_fill

        # Valid placeholders (Polygon cannot be empty)
        eps = 1e-6
        self.bar = Line(np.array([0.0, 0.0, 0.0]), np.array([eps, 0.0, 0.0]))
        self.trap = Polygon(
            np.array([0.0, 0.0, 0.0]),
            np.array([eps, 0.0, 0.0]),
            np.array([0.0, eps, 0.0]),
        )

        for m in (self.trap, self.bar):
            m.set_z_index(z_index)

        self.add(self.trap, self.bar)

        self._build_templates()
        self._rebuild()
        self.add_updater(lambda mob, dt: mob._rebuild())

    def _get_angle(self) -> float:
        """Return rotation in radians; self.angle is stored/treated in DEGREES."""
        a = self.angle
        if hasattr(a, "get_value"):
            deg = float(a.get_value())
        elif callable(a):
            deg = float(a())
        else:
            deg = float(a)
        return np.deg2rad(deg)

    def set_angle(self, angle_deg: float) -> "FixedSupport":
        self.angle = float(angle_deg)
        return self

    def set_size(self, size: float) -> "FixedSupport":
        """Size is a direct scale parameter (not a style object)."""
        self.size = float(size)
        self._build_templates()
        return self

    def _build_templates(self) -> None:
        s = float(self.size)

        # Geometry (tweak these multipliers if you want a different look)
        bar_len = 10.0 * s
        h = 2.0 * s
        top_w = 1.0 * bar_len
        bot_w = 0.7 * bar_len

        # Bar template in LOCAL coords (anchor at origin)
        bar_tpl = Line(
            np.array([-bar_len / 2, 0.0, 0.0]),
            np.array([+bar_len / 2, 0.0, 0.0]),
        )
        bar_tpl.set_stroke(color=BLACK, width=self.bar_stroke_width, opacity=1.0)

        # Trapezoid touches the bar (no gap), extends in -Y
        trap_pts = [
            np.array([-top_w / 2, 0.0, 0.0]),
            np.array([+top_w / 2, 0.0, 0.0]),
            np.array([+bot_w / 2, -h, 0.0]),
            np.array([-bot_w / 2, -h, 0.0]),
        ]
        trap_tpl = Polygon(*trap_pts)
        trap_tpl.set_stroke(opacity=0.0)
        trap_tpl.set_fill(color=ManimColor(self.trap_fill), opacity=1.0)

        self._tpl = {"bar": bar_tpl, "trap": trap_tpl}

    def _rebuild(self) -> None:
        p = np.array(self.anchor.get_point(), dtype=float).reshape(3)
        ang = self._get_angle()

        # CRITICAL FIX: rotate BOTH about the SAME local anchor point (origin)
        about = np.array([0.0, 0.0, 0.0])

        self.trap.become(self._tpl["trap"].copy().rotate(ang, about_point=about).shift(p))
        self.bar.become(self._tpl["bar"].copy().rotate(ang, about_point=about).shift(p))

class RollerSupport(_ConstraintBase):
    """Roller support (triangle + small rollers)."""

    def _rebuild(self) -> None:
        p = self.get_pos()
        s = float(self.style.size)

        top = p
        left = p + np.array([-s, -s, 0.0])
        right = p + np.array([s, -s, 0.0])

        # rollers as small segments (placeholder circles would be better later)
        r_y = -s - 0.12
        r1a = p + np.array([-0.35*s, r_y - 0.05, 0.0])
        r1b = p + np.array([-0.35*s, r_y + 0.05, 0.0])
        r2a = p + np.array([0.35*s, r_y - 0.05, 0.0])
        r2b = p + np.array([0.35*s, r_y + 0.05, 0.0])

        base_y = r_y - 0.15
        base_left = p + np.array([-1.2*s, base_y, 0.0])
        base_right = p + np.array([1.2*s, base_y, 0.0])

        pts = [top, left, right, top, r1a, r1b, r2a, r2b, base_left, base_right]
        self.shape.set_points_as_corners(pts)
