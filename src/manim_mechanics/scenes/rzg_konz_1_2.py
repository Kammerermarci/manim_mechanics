import manim 
import numpy as np
from manim import ValueTracker, linear
from manim_mechanics import (
    Node2D,
    NodeStyle,
    Spring,
    Disc,
    Dashpot,
    PinnedSupport,
    PinnedSupportStyle,
    SolidLine,
    FixedSupport,
    use_paper_theme
)



use_paper_theme()

class homogen_megoldas(manim.Scene):
    def construct(self):
        t = ValueTracker(0.0)

        SF = 3

        m = 8 # kg
        R = 0.5 # m
        k = 100 # N/m
        c = 3 # Ns/m
        F0 = 10 # N
        omega = 10 # rad/s

        theta = 0.5 * m * R**2
        omega_n = np.sqrt(2 * k * R / theta)
        zeta = c * R / (2 * theta * omega_n)
        print(f"zeta = {zeta}")
        omega_d = omega_n * np.sqrt(1 - zeta**2)
        T = 2*np.pi/omega_d

        x0 = 0
        v0 = 5

        C1 = x0
        C2 = (v0 + zeta * omega_n * x0) / omega_d

        # increase lengths for drawing
        R = R * SF

        origin = np.array([0,0,0], dtype=float)
        origin_point = Node2D(np.array(origin), style=NodeStyle(marker="pin"))

        def phi_of_t(tt: float) -> float:        
            return np.exp(- zeta * omega_n * tt) * (C1 * np.cos(omega_d * tt) + C2 * np.sin(omega_d * tt))
        
        def B_of_t(tt: float) -> float:
            return np.array([2*R*np.sin(phi_of_t(tt)), -2*R*(np.cos(phi_of_t(tt))), 0.0])
        
        def C_of_t(tt: float) -> float:
            return np.array([-R*np.sin(phi_of_t(tt)), R*(np.cos(phi_of_t(tt))), 0.0])
        
        def D_of_t(tt: float) -> float:
            return (origin + B_of_t(tt))/2
        
        B_support_point = Node2D(np.array([-2.5, -2*R, 0.0]))
        C_support_point = Node2D(np.array([-2.5, R, 0.0]))

        B_point = Node2D(B_of_t(0.0), style=NodeStyle(marker="pin"))
        C_point = Node2D(C_of_t(0.0), style=NodeStyle(marker="pin"))
        D_point = Node2D(D_of_t(0.0))

        B_point.add_updater(lambda mobj, dt: mobj.set_position(B_of_t(t.get_value())))
        C_point.add_updater(lambda mobj, dt: mobj.set_position(C_of_t(t.get_value())))
        D_point.add_updater(lambda mobj, dt: mobj.set_position(D_of_t(t.get_value())))

        disc = Disc(origin_point.anchor, R)

        pinned_support = PinnedSupport(origin_point.anchor, PinnedSupportStyle(size=0.2))

        spring = Spring(B_support_point.anchor, B_point.anchor)
        dashpot = Dashpot(C_support_point.anchor, C_point.anchor)
        bar = SolidLine(D_point.anchor, B_point.anchor, width=0.1)

        f1 = FixedSupport(B_support_point.anchor, angle = -90)
        f2 = FixedSupport(C_support_point.anchor, angle = -90)

        pinned_support.set_z_index(2)
        B_point.set_z_index(2)
        C_point.set_z_index(2)
        D_point.set_z_index(2)

        self.add(B_point,C_point,D_point,
                disc,pinned_support,spring,dashpot,bar,f1,f2)
        
        self.play(t.animate.set_value(10*T), run_time=10*T, rate_func=linear)
