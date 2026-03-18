"""Martin FX - animation, transition and motion helpers for MARTIN widgets."""

from __future__ import annotations

from ..styles import StyleBase


def _seconds(value) -> str:
    if isinstance(value, str):
        return value
    return f"{float(value):g}s"


def _dimension(value, unit="px") -> str:
    if isinstance(value, str):
        return value
    return f"{value}{unit}"


def stylesheet() -> str:
    """Return the built-in MARTIN FX stylesheet."""
    return FX_CSS


FX_CSS = """
@keyframes martin-fx-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes martin-fx-slide-in {
  from {
    opacity: 0;
    transform: translate3d(var(--martin-fx-x, 0), var(--martin-fx-y, 24px), 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

@keyframes martin-fx-scale-in {
  from {
    opacity: 0;
    transform: scale(var(--martin-fx-scale-from, 0.94));
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes martin-fx-blur-in {
  from {
    opacity: 0;
    filter: blur(var(--martin-fx-blur-from, 12px));
  }
  to {
    opacity: 1;
    filter: blur(0);
  }
}

@keyframes martin-fx-rotate-in {
  from {
    opacity: 0;
    transform: rotate(var(--martin-fx-angle-from, 8deg)) scale(0.985);
  }
  to {
    opacity: 1;
    transform: rotate(0deg) scale(1);
  }
}

@keyframes martin-fx-float {
  0%, 100% { transform: translate3d(0, 0, 0); }
  50% { transform: translate3d(0, calc(var(--martin-fx-float-distance, 10px) * -1), 0); }
}

@keyframes martin-fx-pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.9;
    transform: scale(var(--martin-fx-pulse-scale, 1.035));
  }
}

@keyframes martin-fx-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  [style*="martin-fx-"] {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    animation-delay: 0ms !important;
  }
}
""".strip()


class Transition(StyleBase):
    """
    Add CSS transitions with a Python API.

        Transition()
        Transition("transform", duration=0.4, timing="ease-out")
    """

    def __init__(self, property="all", duration=0.22, timing="ease", delay=0):
        self.property = property
        self.duration = duration
        self.timing = timing
        self.delay = delay

    def to_css(self) -> dict:
        return {
            "transition": (
                f"{self.property} {_seconds(self.duration)} {self.timing} "
                f"{_seconds(self.delay)}"
            ).strip()
        }


class Animate(StyleBase):
    """
    Generic animation style.

    Prefer the preset constructors:
        Animate.fade_in()
        Animate.slide_in()
        Animate.scale_in()
        Animate.blur_in()
        Animate.rotate_in()
        Animate.float()
        Animate.pulse()
        Animate.spin()
    """

    def __init__(
        self,
        name: str,
        *,
        duration=0.6,
        timing="cubic-bezier(0.22, 1, 0.36, 1)",
        delay=0,
        count=1,
        direction="normal",
        fill="both",
        state=None,
        will_change=None,
        extra_css=None,
    ):
        self.name = name
        self.duration = duration
        self.timing = timing
        self.delay = delay
        self.count = count
        self.direction = direction
        self.fill = fill
        self.state = state
        self.will_change = will_change
        self.extra_css = dict(extra_css or {})

    @classmethod
    def fade_in(cls, duration=0.45, timing="ease-out", delay=0):
        return cls(
            "martin-fx-fade-in",
            duration=duration,
            timing=timing,
            delay=delay,
            will_change="opacity",
        )

    @classmethod
    def slide_in(cls, direction="up", distance=24, duration=0.55, delay=0):
        offsets = {
            "up": ("0", _dimension(distance)),
            "down": ("0", _dimension(-distance)),
            "left": (_dimension(distance), "0"),
            "right": (_dimension(-distance), "0"),
        }
        x, y = offsets.get(direction, offsets["up"])
        return cls(
            "martin-fx-slide-in",
            duration=duration,
            timing="cubic-bezier(0.22, 1, 0.36, 1)",
            delay=delay,
            will_change="opacity, transform",
            extra_css={
                "--martin-fx-x": x,
                "--martin-fx-y": y,
            },
        )

    @classmethod
    def scale_in(cls, start=0.94, duration=0.45, delay=0):
        return cls(
            "martin-fx-scale-in",
            duration=duration,
            timing="cubic-bezier(0.2, 0.8, 0.2, 1)",
            delay=delay,
            will_change="opacity, transform",
            extra_css={"--martin-fx-scale-from": str(start)},
        )

    @classmethod
    def blur_in(cls, blur=12, duration=0.5, delay=0):
        return cls(
            "martin-fx-blur-in",
            duration=duration,
            timing="ease-out",
            delay=delay,
            will_change="opacity, filter",
            extra_css={"--martin-fx-blur-from": _dimension(blur)},
        )

    @classmethod
    def rotate_in(cls, angle=8, duration=0.55, delay=0, origin="center center"):
        return cls(
            "martin-fx-rotate-in",
            duration=duration,
            timing="cubic-bezier(0.2, 0.9, 0.2, 1)",
            delay=delay,
            will_change="opacity, transform",
            extra_css={
                "--martin-fx-angle-from": _dimension(angle, "deg"),
                "transform-origin": origin,
            },
        )

    @classmethod
    def float(cls, distance=10, duration=3.2, delay=0):
        return cls(
            "martin-fx-float",
            duration=duration,
            timing="ease-in-out",
            delay=delay,
            count="infinite",
            fill="both",
            will_change="transform",
            extra_css={"--martin-fx-float-distance": _dimension(distance)},
        )

    @classmethod
    def pulse(cls, scale=1.035, duration=2.2, delay=0):
        return cls(
            "martin-fx-pulse",
            duration=duration,
            timing="ease-in-out",
            delay=delay,
            count="infinite",
            fill="both",
            will_change="opacity, transform",
            extra_css={"--martin-fx-pulse-scale": str(scale)},
        )

    @classmethod
    def spin(cls, duration=1.1, timing="linear", delay=0):
        return cls(
            "martin-fx-spin",
            duration=duration,
            timing=timing,
            delay=delay,
            count="infinite",
            fill="both",
            will_change="transform",
        )

    def to_css(self) -> dict:
        css = dict(self.extra_css)
        css["animation"] = (
            f"{self.name} {_seconds(self.duration)} {self.timing} "
            f"{_seconds(self.delay)} {self.count} {self.direction} {self.fill}"
        )
        if self.state is not None:
            css["animation-play-state"] = self.state
        if self.will_change is not None:
            css["will-change"] = self.will_change
        return css


class FadeIn(Animate):
    def __init__(self, duration=0.45, timing="ease-out", delay=0):
        base = Animate.fade_in(duration=duration, timing=timing, delay=delay)
        self.__dict__.update(base.__dict__)


class SlideIn(Animate):
    def __init__(self, direction="up", distance=24, duration=0.55, delay=0):
        base = Animate.slide_in(
            direction=direction, distance=distance, duration=duration, delay=delay
        )
        self.__dict__.update(base.__dict__)


class ScaleIn(Animate):
    def __init__(self, start=0.94, duration=0.45, delay=0):
        base = Animate.scale_in(start=start, duration=duration, delay=delay)
        self.__dict__.update(base.__dict__)


class BlurIn(Animate):
    def __init__(self, blur=12, duration=0.5, delay=0):
        base = Animate.blur_in(blur=blur, duration=duration, delay=delay)
        self.__dict__.update(base.__dict__)


class RotateIn(Animate):
    def __init__(self, angle=8, duration=0.55, delay=0, origin="center center"):
        base = Animate.rotate_in(
            angle=angle, duration=duration, delay=delay, origin=origin
        )
        self.__dict__.update(base.__dict__)


class Float(Animate):
    def __init__(self, distance=10, duration=3.2, delay=0):
        base = Animate.float(distance=distance, duration=duration, delay=delay)
        self.__dict__.update(base.__dict__)


class Pulse(Animate):
    def __init__(self, scale=1.035, duration=2.2, delay=0):
        base = Animate.pulse(scale=scale, duration=duration, delay=delay)
        self.__dict__.update(base.__dict__)


class Spin(Animate):
    def __init__(self, duration=1.1, timing="linear", delay=0):
        base = Animate.spin(duration=duration, timing=timing, delay=delay)
        self.__dict__.update(base.__dict__)


__all__ = [
    "FX_CSS",
    "stylesheet",
    "Transition",
    "Animate",
    "FadeIn",
    "SlideIn",
    "ScaleIn",
    "BlurIn",
    "RotateIn",
    "Float",
    "Pulse",
    "Spin",
]
