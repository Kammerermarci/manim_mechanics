from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from manim import (
    config,
    WHITE,
    BLACK,
    VMobject,
    Dot,
    Tex,
    MathTex,
)


@dataclass(frozen=True)
class MechanicsTheme:
    background: object = WHITE
    stroke: object = BLACK
    fill: object = BLACK
    text: object = BLACK
    dot: object = BLACK


_THEMES: dict[str, MechanicsTheme] = {
    "paper": MechanicsTheme(background=WHITE, stroke=BLACK, fill=BLACK, text=BLACK, dot=BLACK),
    "dark": MechanicsTheme(background=BLACK, stroke=WHITE, fill=WHITE, text=WHITE, dot=WHITE),
}


def use_theme(name: Literal["paper", "dark"] | str = "paper") -> None:
    """Apply a global theme suitable for manim-mechanics usage.

    Call this once (module-level, before Scene is constructed) for best results.
    """
    theme = _THEMES.get(str(name), _THEMES["paper"])
    apply_theme(theme)


def apply_theme(theme: MechanicsTheme) -> None:
    """Apply a theme globally to Manim defaults."""
    # Global background
    config.background_color = theme.background

    # Global defaults for common primitives/text
    # (affects everything, including your own Tex title, which is what you want here)
    VMobject.set_default(stroke_color=theme.stroke, fill_color=theme.fill)
    Dot.set_default(color=theme.dot)
    Tex.set_default(color=theme.text)
    MathTex.set_default(color=theme.text)


def use_paper_theme() -> None:
    use_theme("paper")