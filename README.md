# manim-mechanics

A small helper library providing **anchor‑based mechanical elements** for
[Manim Community Edition](https://docs.manim.community/) scenes.  The package is
focused on 2‑D kinematic sketches and animations rather than solving equations
directly; it gives you building blocks like springs, dashpots, beams and
supports that automatically redraw when their reference points move.

---

## 📌 Key Concepts & Capabilities

- **Anchors**: every element is positioned relative to `Anchor` objects which
  return a 3‑D point (Manim uses 3‑vectors even in 2‑D).  Use
  `PointAnchor.from_mobject()` or custom callables to tie geometry together.

- **Nodes & markers** – `Node2D` objects represent point masses, pins or
  labelled points.  Styles allow for mass shading or pin markers.

- **Elements** – subclasses of `TwoPointElement` that draw between two anchors:
  `Spring`, `Dashpot`, `Beam`, `SolidLine`, plus `Disc` for filled circles.
  Each has a style dataclass controlling dimensions, colours, number of coils,
  etc.

- **Supports/Constraints** – visual fixtures such as
  `PinnedSupport`, `FixedSupport`, `RollerSupport` with flexible orientation.

- **Drivers** – animation helpers:
  `Trajectory2D` (time‑indexed positions) and `bind_position()` to attach any
  `Mobject` to a `ValueTracker` for custom motion.

- **Theming** – convenient functions `use_theme()`, `use_paper_theme()` and
  `apply_theme()` modify Manim defaults for a consistent black‑on‑white or
  dark worksheet look.

- **Updater‑driven redraw** – every element registers its own updater so moving
  an anchor automatically rebuilds the shape each frame.

- **Example scenes** – several ready‑made Scene classes under
  `src/manim_mechanics/scenes/` showcase typical uses:
  `DemoOscillator`, `rzg_konz_1_1`, `rzg_konz_1_2`, and a simple plotting script.

---

## ⚒️ Installation

Install into your development environment with the editable option:

```bash
pip install -e .
```

This will make the `manim_mechanics` package available to your Manim scenes.

---

## 🚀 Quick usage examples

### Basic spring animation

```python
from manim import Scene, ValueTracker, linear
from manim_mechanics import Node2D, Spring, PinnedSupport, use_paper_theme

use_paper_theme()

class SpringScene(Scene):
    def construct(self):
        a = Node2D([0, 0, 0], label="A")
        b = Node2D([2, 0, 0], label="B")
        spring = Spring(a.anchor, b.anchor)
        support = PinnedSupport(a.anchor)

        t = ValueTracker(0.0)
        b.add_updater(lambda m, dt: m.set_position([2 + 0.5 * np.sin(t.get_value()), 0, 0]))
        self.add(a, b, spring, support)
        self.play(t.animate.set_value(6), rate_func=linear, run_time=6)
```

![Spring example](media/images/demo_oscillator/spring_example.png)

### Using a prescribed trajectory

```python
from manim import Scene, ValueTracker
from manim_mechanics import Trajectory2D, bind_position, Node2D, use_paper_theme

use_paper_theme()

class TrajScene(Scene):
    def construct(self):
        t = ValueTracker(0.0)
        traj = Trajectory2D(
            times=[0, 1, 2],
            positions=[[0, 0], [1, 1], [2, 0]],
        )
        dot = Node2D([0, 0, 0])
        bind_position(dot, t, traj.at)
        self.add(dot)
        self.play(t.animate.set_value(2), run_time=2)
```

### Custom styles

```python
from manim_mechanics import NodeStyle, SpringStyle
node = Node2D([0,0,0], style=NodeStyle(marker="mass", radius=0.3))
spring = Spring(a.anchor, b.anchor, style=SpringStyle(n_coils=5, amplitude=0.2))
```

---

## 🧪 Running the provided scenes

Execute any of the example scenes using the Manim CLI.  For high‑quality quick
renders use `-pqh` (preview, high quality).  E.g.

```bash
manim -pqh src/manim_mechanics/scenes/demo_oscillator.py DemoOscillator
```

Other scenes are invoked similarly:

```bash
manim -pqh src/manim_mechanics/scenes/rzg_konz_1_1.py homogen_megoldas
manim -pqh src/manim_mechanics/scenes/rzg_konz_1_1.py partikularis_megoldas
```

> ✅ **Tip:** open the scripts in the `scenes` folder for more realistic
> examples of how to combine nodes, elements and mathematical expressions.

---

## 📄 License & contribution

None


---

Happy animating! ✨
#