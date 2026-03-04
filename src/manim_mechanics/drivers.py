from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
from manim import Mobject, ValueTracker


@dataclass
class Trajectory2D:
    """A 2D trajectory defined by times and positions, with linear interpolation.

    positions: array of shape (N, 2) or (N, 3)
    times: array of shape (N,)
    """

    times: np.ndarray
    positions: np.ndarray

    def __post_init__(self) -> None:
        self.times = np.asarray(self.times, dtype=float).reshape(-1)
        self.positions = np.asarray(self.positions, dtype=float)
        if self.positions.shape[0] != self.times.shape[0]:
            raise ValueError("times and positions must have the same length")
        if self.positions.shape[1] == 2:
            z = np.zeros((self.positions.shape[0], 1), dtype=float)
            self.positions = np.hstack([self.positions, z])
        if self.positions.shape[1] != 3:
            raise ValueError("positions must have shape (N,2) or (N,3)")

    def at(self, t: float) -> np.ndarray:
        # clamp outside range
        if t <= self.times[0]:
            return self.positions[0].copy()
        if t >= self.times[-1]:
            return self.positions[-1].copy()

        i = int(np.searchsorted(self.times, t) - 1)
        t0, t1 = self.times[i], self.times[i + 1]
        p0, p1 = self.positions[i], self.positions[i + 1]
        alpha = (t - t0) / (t1 - t0)
        return (1 - alpha) * p0 + alpha * p1


def bind_position(
    mobj: Mobject,
    t: ValueTracker,
    position_fn: Callable[[float], np.ndarray],
    *,
    also_rotate: Optional[Callable[[float], float]] = None,
) -> None:
    """Bind a mobject's position to a time tracker.

    position_fn(t) -> (3,) ndarray
    also_rotate (optional): function returning rotation angle about Z (radians)
    """

    def _update(m: Mobject, dt: float) -> None:
        tt = float(t.get_value())
        p = np.asarray(position_fn(tt), dtype=float).reshape(3)
        m.move_to(p)
        if also_rotate is not None:
            ang = float(also_rotate(tt))
            # naive: set absolute rotation by tracking current angle (improve later)
            # For skeleton: just rotate incrementally toward target is omitted.
            # Users can manage orientation with their own updaters if needed.
            pass

    mobj.add_updater(_update)
