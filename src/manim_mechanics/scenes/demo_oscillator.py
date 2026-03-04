from __future__ import annotations

import numpy as np
from manim import Scene, ValueTracker, linear, Tex, Circle, DashedVMobject

from manim_mechanics import (
    Node2D,
    NodeStyle,
    Spring,
    Dashpot,
    PinnedSupport,
    PinnedSupportStyle,
    Beam,
    use_paper_theme,
)

use_paper_theme()


class DemoOscillator(Scene):
    def construct(self):
        t = ValueTracker(0.0)

        spring_point = Node2D(np.array([-3.0, 0.0, 0.0]))
        damper_point = Node2D(np.array([0.0, -3.0, 0.0]))

        R = 1.0
        w = 5.0
        T = 2 * np.pi / w
        l = 3

        path = DashedVMobject(
            Circle(radius=R).move_to([0, 0, 0]),
            num_dashes=80,      # increase for finer dashes
            dashed_ratio=0.55,  # fraction of dash vs gap
        )
        path.set_z_index(-10)   # behind

        def r_of_t(tt: float) -> np.ndarray:
            return np.array([R * np.cos(w * tt), R * np.sin(w * tt), 0.0])
        def alpha_of_t(tt: float) -> float:
            return np.arcsin(R * np.sin(w * tt) / l)
        def b_of_t(tt: float) -> float:
            return R * np.cos(w * tt) + l * np.cos(alpha_of_t(tt))
        
        b_point = Node2D(np.array([b_of_t(0.0), 0.0, 0.0]))

        mass = Node2D(
            r_of_t(0.0),
            style=NodeStyle(marker="mass", radius=0.3),  # use a sensible radius
        )

        beam = Beam(mass.anchor, b_point.anchor)

        # IMPORTANT: move the marker (center) only
        mass.add_updater(lambda m, dt: m.set_position(r_of_t(float(t.get_value()))))
        b_point.add_updater(lambda m, dt: m.set_position(np.array([b_of_t(float(t.get_value())), 0.0, 0.0])))


        spring = Spring(spring_point.anchor, mass.anchor)
        damper = Dashpot(damper_point.anchor, mass.anchor)
        
        support = PinnedSupport(
            spring_point.anchor
        )

        support_damper = PinnedSupport(
            damper_point.anchor
        )

        title = Tex(
            r"Prescribed vibration: $r(t)=\left[R\cos(\omega t),\,R\sin(\omega t)\right]$"
        ).to_edge([0, 1, 0])

        mass.set_z_index(10)
        beam.set_z_index(0)
        spring.set_z_index(0)
        damper.set_z_index(0)
        support.set_z_index(-1)   # behind
        support_damper.set_z_index(-1)
        spring_point.set_z_index(5)
        damper_point.set_z_index(5)

        # IMPORTANT: add mass BEFORE elements so its updater runs first each frame
        self.add(path, spring_point, damper_point, mass, b_point, beam, support, support_damper, spring, damper, title)

        self.play(t.animate.set_value(3 * T), rate_func=linear, run_time=3 * T)