from __future__ import annotations

import numpy as np
import manim
from manim import Scene, ValueTracker, linear, Tex, Circle, DashedVMobject, TracedPath, always_redraw, Arrow, MathTex, Line, Arc, DashedLine
from manim import ManimColor
from manim_mechanics import (
    Node2D,
    NodeStyle,
    Spring,
    Dashpot,
    PinnedSupport,
    PinnedSupportStyle,
    SolidLine,
    SolidLineStyle,
    FixedSupport,
    Beam,
    use_paper_theme,
)

use_paper_theme()


# manim -pqh src/manim_mechanics/scenes/rzg_konz_1_1.py elso_feladat_tranziens

class homogen_megoldas(Scene):
    def construct(self):
        t = ValueTracker(0.0)

        SF = 12

        m = 2 # kg
        l = 0.2  # m
        k = 100 # N/m
        c = 10 # Ns/m
        r0 = 0.01 # m
        omega = 2 # rad/s
        g = 9.81 # m/s^2

        x0 = 0
        v0 = 0.5

        omega_n = np.sqrt((4 * k / m - g / l) / 10)
        zeta = (c / (10*m)) / (2 * omega_n)
        omega_d = omega_n * np.sqrt(1 - zeta**2)
        T = 2*np.pi/omega_d

        C1 = x0
        C2 = (v0 + zeta * omega_n * x0) / omega_d

        # increase lengths for drawing
        l = l * SF
        r0 = r0 * SF

        origin = np.array([-3, -0.5, 0.0], dtype=float)
        origin_point = Node2D(np.array(origin), style=NodeStyle(marker="pin"))

        def phi_of_t(tt: float) -> float:
            return np.exp(- zeta * omega_n * tt) * ( C1 * np.cos(omega_d * tt) + C2 * np.sin(omega_d * tt))
        
        def C_of_t(tt: float) -> float:
            return origin + np.array([- l * np.sin(phi_of_t(tt)), l * np.cos(phi_of_t(tt)), 0.0])
        
        def D_of_t(tt: float) -> float:
            return origin + np.array([3*l*np.cos(phi_of_t(tt)), 3*l * np.sin(phi_of_t(tt)), 0.0])
        
        def B_of_t(tt: float) -> float:
            return origin + np.array([2*l, 0.8 * l , 0])
        
        def E_of_t(tt: float) -> float:
            return origin + 2/3 * (D_of_t(tt) - origin)
        
        def F_of_t(tt: float) -> float:
            return origin + 1/3 * (D_of_t(tt) - origin)
        
        
        C_point = Node2D(C_of_t(0.0))
        D_point = Node2D(D_of_t(0.0))
        B_point = Node2D(B_of_t(0.0), style=NodeStyle(marker="pin"))
        E_point = Node2D(E_of_t(0.0), style=NodeStyle(marker="pin"))
        F_point = Node2D(F_of_t(0.0), style=NodeStyle(marker="pin"))
        dashpot_ground = Node2D(origin + np.array([l, -0.75*l, 0.0]))

        title = Tex(r"Homogén (tranziens) megoldás, $\varphi_\mathrm{h}(t)$").to_edge(manim.UP)          # top
        note = Tex(r"Kezdeti feltételek: $\varphi(0) = 0\;\mathrm{rad}, \dot{\varphi}(0) = 0.5\;\mathrm{rad/s}$").scale(0.6).to_corner(manim.DOWN)  # bottom-right
        r_of_t_text = Tex(r"$r(t) \equiv 0$").scale(0.6).next_to(B_point.dot, manim.RIGHT, buff=0.6).set_color("#0e7345")
        szog_line = Line(D_point.dot.get_center()+ manim.RIGHT*0.5, D_point.dot.get_center() + manim.RIGHT*0.9).set_color("#0e7345").set_stroke(width=4)
        dot_line = DashedLine(origin, D_point.dot.get_center() + manim.RIGHT*1.2).set_color(manim.BLACK).set_stroke(width=1)
        arc = Arc(D_of_t(0)[0]-origin[0] + 0.7, 0, np.pi/30, arc_center=origin).set_color("#0e7345").set_stroke(width=4)
        mid = arc.point_from_proportion(0.5)
        phi_label = MathTex(r"\varphi").scale(0.6).set_color("#0e7345")
        phi_label.next_to(mid, manim.RIGHT, buff=0.15)
        arc.add_tip(tip_width=0.2, tip_length=0.2)
        szog_line.set_z_index(2)
        self.add(title, dot_line, note, r_of_t_text, szog_line, arc, phi_label)

        time_counter = always_redraw(
            lambda: Tex(rf"$t = {t.get_value():.2f}\ \mathrm{{s}}$")
                .scale(0.6)
                .set_color(manim.BLACK)
                .to_corner(manim.DL, buff=0.25)
        )

        self.add(time_counter)

        C_point.add_updater(lambda m, dt: m.set_position(C_of_t(t.get_value())))
        D_point.add_updater(lambda m, dt: m.set_position(D_of_t(t.get_value())))
        B_point.add_updater(lambda m, dt: m.set_position(B_of_t(t.get_value())))
        E_point.add_updater(lambda m, dt: m.set_position(E_of_t(t.get_value())))
        F_point.add_updater(lambda m, dt: m.set_position(F_of_t(t.get_value())))
        
        support_A = PinnedSupport(origin_point.anchor)
        beam_AC = SolidLine(origin_point.anchor, C_point.anchor, width=0.125)
        beam_AD = SolidLine(origin_point.anchor, D_point.anchor, width=0.125)


        spring_BE = Spring(B_point.anchor, E_point.anchor)
        dashpot_GF = Dashpot(dashpot_ground.anchor, F_point.anchor)

        dashpot_fix = FixedSupport(dashpot_ground.anchor)

        mass_C = Node2D(
            C_of_t(0.0),
            style=NodeStyle(marker="mass", radius=0.4),  # use a sensible radius
        )
        mass_D = Node2D(
            D_of_t(0.0),
            style=NodeStyle(marker="mass", radius=0.4),  # use a sensible radius
        )
        springGuide_point_1 = Node2D(origin + np.array([2*l - 0.25, 0.8 * l , 0]))
        springGuide_point_2 = Node2D(origin + np.array([2*l + 0.25, 0.8 * l , 0]))
        springGuide_point_1.dot.set_opacity(0)
        springGuide_point_2.dot.set_opacity(0)
        springGuide_1 = FixedSupport(springGuide_point_1.anchor, angle = -90, size = 0.15)
        springGuide_2 = FixedSupport(springGuide_point_2.anchor, angle = 90, size = 0.15)


        mass_C.add_updater(lambda m, dt: m.set_position(C_of_t(t.get_value())))
        mass_D.add_updater(lambda m, dt: m.set_position(D_of_t(t.get_value())))

        E_point.set_z_index(1)
        F_point.set_z_index(1)
        B_point.set_z_index(1)
        origin_point.set_z_index(1)

        self.add(C_point, D_point, B_point, E_point, F_point, origin_point, springGuide_point_1, springGuide_point_2,
                  support_A, beam_AC, beam_AD, mass_C, mass_D, 
                  spring_BE, dashpot_GF, dashpot_fix,
                  springGuide_1, springGuide_2)

        self.play(t.animate.set_value(10*T), run_time=5*T, rate_func=linear)

class partikularis_megoldas(Scene):
    def construct(self):
        t = ValueTracker(0.0)

        SF = 12

        m = 2 # kg
        l = 0.2  # m
        k = 100 # N/m
        c = 10 # Ns/m
        r0 = 0.01 # m
        omega = 2 # rad/s
        g = 9.81 # m/s^2

        x0 = 0
        v0 = 0.5

        omega_n = np.sqrt((4 * k / m - g / l) / 10)
        zeta = (c / (10*m)) / (2 * omega_n)
        omega_d = omega_n * np.sqrt(1 - zeta**2)
        T = 2*np.pi/omega_d

        f0 = - (2 * k * r0) / (10 * m * l * omega_n**2)
        lam = omega / omega_n
        N = 1 / np.sqrt((1-lam**2)**2 + 4 * zeta**2 * lam**2)
        A = N * f0
        theta = np.arctan2(2 * zeta * lam, 1 - lam**2)

        # increase lengths for drawing
        l = l * SF
        r0 = r0 * SF

        origin = np.array([-3, -0.5, 0.0], dtype=float)
        origin_point = Node2D(np.array(origin), style=NodeStyle(marker="pin"))

        def phi_of_t(tt: float) -> float:
            return A * np.sin(omega * tt - theta)
        
        def C_of_t(tt: float) -> float:
            return origin + np.array([- l * np.sin(phi_of_t(tt)), l * np.cos(phi_of_t(tt)), 0.0])
        
        def D_of_t(tt: float) -> float:
            return origin + np.array([3*l*np.cos(phi_of_t(tt)), 3*l * np.sin(phi_of_t(tt)), 0.0])
        
        def B_of_t(tt: float) -> float:
            return origin + np.array([2*l, 0.8 * l , 0]) + np.array([0, -r0 * np.sin(omega * tt), 0])
        
        def E_of_t(tt: float) -> float:
            return origin + 2/3 * (D_of_t(tt) - origin)
        
        def F_of_t(tt: float) -> float:
            return origin + 1/3 * (D_of_t(tt) - origin)
        
        C_point = Node2D(C_of_t(0.0))
        D_point = Node2D(D_of_t(0.0))
        B_point = Node2D(B_of_t(0.0), style=NodeStyle(marker="pin"))
        E_point = Node2D(E_of_t(0.0), style=NodeStyle(marker="pin"))
        F_point = Node2D(F_of_t(0.0), style=NodeStyle(marker="pin"))
        dashpot_ground = Node2D(origin + np.array([l, -0.75*l, 0.0]))

        title = Tex(r"Partikuláris (állandósult) megoldás, $\varphi_\mathrm{p}(t)$").to_edge(manim.UP)          # top
        r_of_t_text = Tex(r"$r(t) = r_0 \sin(\omega t)$").scale(0.6).next_to(B_point.dot, manim.RIGHT, buff=0.85).set_color("#0e7345")
        r_arrow = Arrow(
            manim.UP*0.6, manim.DOWN*0.6,
            buff=0,
            stroke_width=4,
            tip_length=0.18,        # smaller head (tune this)
        ).set_color("#0e7345")

        r_arrow.next_to(r_of_t_text, manim.LEFT, buff=0.1)  # arrow below the text
        szog_line = Line(D_point.dot.get_center()+ manim.RIGHT*0.5, D_point.dot.get_center() + manim.RIGHT*0.9).set_color("#0e7345").set_stroke(width=4)
        dot_line = DashedLine(origin, D_point.dot.get_center() + manim.RIGHT*1.2).set_color(manim.BLACK).set_stroke(width=1)
        arc = Arc(D_of_t(0)[0]-origin[0] + 0.7, 0, np.pi/30, arc_center=origin).set_color("#0e7345").set_stroke(width=4)
        mid = arc.point_from_proportion(0.5)
        phi_label = MathTex(r"\varphi").scale(0.6).set_color("#0e7345")
        phi_label.next_to(mid, manim.RIGHT, buff=0.15)
        arc.add_tip(tip_width=0.2, tip_length=0.2)
        szog_line.set_z_index(2)
        self.add(title, dot_line, r_of_t_text, szog_line, arc, phi_label)
        # If you want it to the left/right instead:
        # r_arrow.next_to(r_of_t_text, manim.LEFT, buff=0.15)

        self.add(r_of_t_text, r_arrow)

        time_counter = always_redraw(
            lambda: Tex(rf"$t = {t.get_value():.2f}\ \mathrm{{s}}$")
                .scale(0.6)
                .set_color(manim.BLACK)
                .to_corner(manim.DL, buff=0.25)
        )

        self.add(time_counter)

        C_point.add_updater(lambda m, dt: m.set_position(C_of_t(t.get_value())))
        D_point.add_updater(lambda m, dt: m.set_position(D_of_t(t.get_value())))
        B_point.add_updater(lambda m, dt: m.set_position(B_of_t(t.get_value())))
        E_point.add_updater(lambda m, dt: m.set_position(E_of_t(t.get_value())))
        F_point.add_updater(lambda m, dt: m.set_position(F_of_t(t.get_value())))
        
        support_A = PinnedSupport(origin_point.anchor)
        beam_AC = SolidLine(origin_point.anchor, C_point.anchor, width=0.125)
        beam_AD = SolidLine(origin_point.anchor, D_point.anchor, width=0.125)


        spring_BE = Spring(B_point.anchor, E_point.anchor)
        dashpot_GF = Dashpot(dashpot_ground.anchor, F_point.anchor)

        dashpot_fix = FixedSupport(dashpot_ground.anchor)

        mass_C = Node2D(
            C_of_t(0.0),
            style=NodeStyle(marker="mass", radius=0.4),  # use a sensible radius
        )
        mass_D = Node2D(
            D_of_t(0.0),
            style=NodeStyle(marker="mass", radius=0.4),  # use a sensible radius
        )
        springGuide_point_1 = Node2D(origin + np.array([2*l - 0.25, 0.8 * l , 0]))
        springGuide_point_2 = Node2D(origin + np.array([2*l + 0.25, 0.8 * l , 0]))
        springGuide_point_1.dot.set_opacity(0)
        springGuide_point_2.dot.set_opacity(0)
        springGuide_1 = FixedSupport(springGuide_point_1.anchor, angle = -90, size = 0.15)
        springGuide_2 = FixedSupport(springGuide_point_2.anchor, angle = 90, size = 0.15)


        mass_C.add_updater(lambda m, dt: m.set_position(C_of_t(t.get_value())))
        mass_D.add_updater(lambda m, dt: m.set_position(D_of_t(t.get_value())))

        E_point.set_z_index(1)
        F_point.set_z_index(1)
        B_point.set_z_index(1)
        origin_point.set_z_index(1)

        self.add(C_point, D_point, B_point, E_point, F_point, origin_point, springGuide_point_1, springGuide_point_2,
                  support_A, beam_AC, beam_AD, mass_C, mass_D, 
                  spring_BE, dashpot_GF, dashpot_fix,
                  springGuide_1, springGuide_2)

        self.play(t.animate.set_value(10*T), run_time=5*T, rate_func=linear)

        

class altalanos_megoldas(Scene):
    def construct(self):
        t = ValueTracker(0.0)

        SF = 12

        m = 2 # kg
        l = 0.2  # m
        k = 100 # N/m
        c = 10 # Ns/m
        r0 = 0.01 # m
        omega = 2 # rad/s
        g = 9.81 # m/s^2

        x0 = 0
        v0 = 0.5

        omega_n = np.sqrt((4 * k / m - g / l) / 10)
        zeta = (c / (10*m)) / (2 * omega_n)
        omega_d = omega_n * np.sqrt(1 - zeta**2)
        T = 2*np.pi/omega_d

        f0 = - (2 * k * r0) / (10 * m * l * omega_n**2)
        lam = omega / omega_n
        N = 1 / np.sqrt((1-lam**2)**2 + 4 * zeta**2 * lam**2)
        A = N * f0
        theta = np.arctan2(2 * zeta * lam, 1 - lam**2)

        # increase lengths for drawing
        l = l * SF
        r0 = r0 * SF

        origin = np.array([-3, -0.5, 0.0], dtype=float)
        origin_point = Node2D(np.array(origin), style=NodeStyle(marker="pin"))

        def phi_of_t(tt: float) -> float:
            return 0.0448834 * np.sin(0.0898878 - 2 * tt)+np.exp(-0.25 *tt)* (-0.00402904 * np.cos(3.87718*tt) + 0.073385 * np.sin(3.87718 *tt))
        
        def C_of_t(tt: float) -> float:
            return origin + np.array([- l * np.sin(phi_of_t(tt)), l * np.cos(phi_of_t(tt)), 0.0])
        
        def D_of_t(tt: float) -> float:
            return origin + np.array([3*l*np.cos(phi_of_t(tt)), 3*l * np.sin(phi_of_t(tt)), 0.0])
        
        def B_of_t(tt: float) -> float:
            return origin + np.array([2*l, 0.8 * l , 0]) + np.array([0, -r0 * np.sin(omega * tt), 0])
        
        def E_of_t(tt: float) -> float:
            return origin + 2/3 * (D_of_t(tt) - origin)
        
        def F_of_t(tt: float) -> float:
            return origin + 1/3 * (D_of_t(tt) - origin)
        
        C_point = Node2D(C_of_t(0.0))
        D_point = Node2D(D_of_t(0.0))
        B_point = Node2D(B_of_t(0.0), style=NodeStyle(marker="pin"))
        E_point = Node2D(E_of_t(0.0), style=NodeStyle(marker="pin"))
        F_point = Node2D(F_of_t(0.0), style=NodeStyle(marker="pin"))
        dashpot_ground = Node2D(origin + np.array([l, -0.75*l, 0.0]))


        title = Tex(r"Általános megoldás, $\varphi(t) = \varphi_\mathrm{h}(t)+ \varphi_\mathrm{p}(t)$").to_edge(manim.UP)          # top
        note = Tex(r"Kezdeti feltételek: $\varphi(0) = 0\;\mathrm{rad}, \dot{\varphi}(0) = 0.5\;\mathrm{rad/s}$").scale(0.6).to_corner(manim.DOWN)  # bottom-right
        r_of_t_text = Tex(r"$r(t) = r_0 \sin(\omega t)$").scale(0.6).next_to(B_point.dot, manim.RIGHT, buff=0.85).set_color("#0e7345")
        r_arrow = Arrow(
            manim.UP*0.6, manim.DOWN*0.6,
            buff=0,
            stroke_width=4,
            tip_length=0.18,        # smaller head (tune this)
        ).set_color("#0e7345")
        szog_line = Line(D_point.dot.get_center()+ manim.RIGHT*0.5, D_point.dot.get_center() + manim.RIGHT*0.9).set_color("#0e7345").set_stroke(width=4)
        dot_line = DashedLine(origin, D_point.dot.get_center() + manim.RIGHT*1.2).set_color(manim.BLACK).set_stroke(width=1)
        arc = Arc(D_of_t(0)[0]-origin[0] + 0.7, 0, np.pi/30, arc_center=origin).set_color("#0e7345").set_stroke(width=4)
        mid = arc.point_from_proportion(0.5)
        phi_label = MathTex(r"\varphi").scale(0.6).set_color("#0e7345")
        phi_label.next_to(mid, manim.RIGHT, buff=0.15)
        arc.add_tip(tip_width=0.2, tip_length=0.2)
        szog_line.set_z_index(2)
        self.add(title, dot_line, note, r_of_t_text, szog_line, arc, phi_label)

        r_arrow.next_to(r_of_t_text, manim.LEFT, buff=0.1)  # arrow below the text

        self.add(r_of_t_text, r_arrow)

        time_counter = always_redraw(
            lambda: Tex(rf"$t = {t.get_value():.2f}\ \mathrm{{s}}$")
                .scale(0.6)
                .set_color(manim.BLACK)
                .to_corner(manim.DL, buff=0.25)
        )

        self.add(time_counter)


        C_point.add_updater(lambda m, dt: m.set_position(C_of_t(t.get_value())))
        D_point.add_updater(lambda m, dt: m.set_position(D_of_t(t.get_value())))
        B_point.add_updater(lambda m, dt: m.set_position(B_of_t(t.get_value())))
        E_point.add_updater(lambda m, dt: m.set_position(E_of_t(t.get_value())))
        F_point.add_updater(lambda m, dt: m.set_position(F_of_t(t.get_value())))
        
        support_A = PinnedSupport(origin_point.anchor)
        beam_AC = SolidLine(origin_point.anchor, C_point.anchor, width=0.125)
        beam_AD = SolidLine(origin_point.anchor, D_point.anchor, width=0.125)


        spring_BE = Spring(B_point.anchor, E_point.anchor)
        dashpot_GF = Dashpot(dashpot_ground.anchor, F_point.anchor)

        dashpot_fix = FixedSupport(dashpot_ground.anchor)

        mass_C = Node2D(
            C_of_t(0.0),
            style=NodeStyle(marker="mass", radius=0.4),  # use a sensible radius
        )
        mass_D = Node2D(
            D_of_t(0.0),
            style=NodeStyle(marker="mass", radius=0.4),  # use a sensible radius
        )
        springGuide_point_1 = Node2D(origin + np.array([2*l - 0.25, 0.8 * l , 0]))
        springGuide_point_2 = Node2D(origin + np.array([2*l + 0.25, 0.8 * l , 0]))
        springGuide_point_1.dot.set_opacity(0)
        springGuide_point_2.dot.set_opacity(0)
        springGuide_1 = FixedSupport(springGuide_point_1.anchor, angle = -90, size = 0.15)
        springGuide_2 = FixedSupport(springGuide_point_2.anchor, angle = 90, size = 0.15)


        mass_C.add_updater(lambda m, dt: m.set_position(C_of_t(t.get_value())))
        mass_D.add_updater(lambda m, dt: m.set_position(D_of_t(t.get_value())))

        E_point.set_z_index(1)
        F_point.set_z_index(1)
        B_point.set_z_index(1)
        origin_point.set_z_index(1)

        self.add(C_point, D_point, B_point, E_point, F_point, origin_point, springGuide_point_1, springGuide_point_2,
                  support_A, beam_AC, beam_AD, mass_C, mass_D, 
                  spring_BE, dashpot_GF, dashpot_fix,
                  springGuide_1, springGuide_2)

        self.play(t.animate.set_value(20*T), run_time=10*T, rate_func=linear)