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


def _copy_from(instance, other):
    instance.__dict__.update(other.__dict__)


def _hex_to_rgba(color: str, alpha: float) -> str:
    if not isinstance(color, str):
        return f"rgba(99,102,241,{alpha})"
    value = color.strip()
    if value.startswith("#"):
        h = value.lstrip("#")
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        if len(h) == 6:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f"rgba({r},{g},{b},{alpha})"
    return value


class FXStyle(StyleBase):
    """Base class for FX styles that may also inject HTML attributes."""

    def fx_attrs(self) -> dict:
        return {}

    def to_css(self) -> dict:
        return {}


def stylesheet() -> str:
    """Return the built-in MARTIN FX stylesheet."""
    return FX_CSS


def script() -> str:
    """Return the built-in MARTIN FX bootstrap script."""
    return FX_JS


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

[data-martin-fx-hover] {
  transition:
    transform var(--martin-fx-hover-duration, 0.22s) var(--martin-fx-hover-timing, ease) var(--martin-fx-hover-delay, 0s),
    box-shadow var(--martin-fx-hover-duration, 0.22s) var(--martin-fx-hover-timing, ease) var(--martin-fx-hover-delay, 0s),
    filter var(--martin-fx-hover-duration, 0.22s) var(--martin-fx-hover-timing, ease) var(--martin-fx-hover-delay, 0s),
    opacity var(--martin-fx-hover-duration, 0.22s) var(--martin-fx-hover-timing, ease) var(--martin-fx-hover-delay, 0s),
    background var(--martin-fx-hover-duration, 0.22s) var(--martin-fx-hover-timing, ease) var(--martin-fx-hover-delay, 0s),
    color var(--martin-fx-hover-duration, 0.22s) var(--martin-fx-hover-timing, ease) var(--martin-fx-hover-delay, 0s),
    border-color var(--martin-fx-hover-duration, 0.22s) var(--martin-fx-hover-timing, ease) var(--martin-fx-hover-delay, 0s);
}

[data-martin-fx-hover~="transform"]:hover,
[data-martin-fx-hover~="transform"]:focus-visible {
  transform: var(--martin-fx-hover-transform);
}

[data-martin-fx-hover~="shadow"]:hover,
[data-martin-fx-hover~="shadow"]:focus-visible {
  box-shadow: var(--martin-fx-hover-shadow);
}

[data-martin-fx-hover~="filter"]:hover,
[data-martin-fx-hover~="filter"]:focus-visible {
  filter: var(--martin-fx-hover-filter);
}

[data-martin-fx-hover~="opacity"]:hover,
[data-martin-fx-hover~="opacity"]:focus-visible {
  opacity: var(--martin-fx-hover-opacity);
}

[data-martin-fx-hover~="background"]:hover,
[data-martin-fx-hover~="background"]:focus-visible {
  background: var(--martin-fx-hover-background);
}

[data-martin-fx-hover~="color"]:hover,
[data-martin-fx-hover~="color"]:focus-visible {
  color: var(--martin-fx-hover-color);
}

[data-martin-fx-hover~="border"]:hover,
[data-martin-fx-hover~="border"]:focus-visible {
  border-color: var(--martin-fx-hover-border-color);
}

[data-martin-fx-reveal] {
  opacity: 0;
  transform:
    translate3d(var(--martin-fx-reveal-x, 0), var(--martin-fx-reveal-y, 18px), 0)
    scale(var(--martin-fx-reveal-scale, 1));
  filter: blur(var(--martin-fx-reveal-blur, 0px));
  transition:
    opacity var(--martin-fx-reveal-duration, 0.7s) var(--martin-fx-reveal-timing, cubic-bezier(0.22, 1, 0.36, 1)) var(--martin-fx-reveal-delay, 0s),
    transform var(--martin-fx-reveal-duration, 0.7s) var(--martin-fx-reveal-timing, cubic-bezier(0.22, 1, 0.36, 1)) var(--martin-fx-reveal-delay, 0s),
    filter var(--martin-fx-reveal-duration, 0.7s) var(--martin-fx-reveal-timing, cubic-bezier(0.22, 1, 0.36, 1)) var(--martin-fx-reveal-delay, 0s);
}

[data-martin-fx-reveal].martin-fx-in {
  opacity: 1;
  transform: translate3d(0, 0, 0) scale(1);
  filter: blur(0);
}

@media (prefers-reduced-motion: reduce) {
  [style*="martin-fx-"],
  [data-martin-fx-reduce~="animation"] {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    animation-delay: 0ms !important;
  }

  [data-martin-fx-reduce~="transition"],
  [data-martin-fx-reduce~="hover"] {
    transition: none !important;
  }

  [data-martin-fx-reduce~="reveal"],
  [data-martin-fx-reveal] {
    opacity: 1 !important;
    transform: none !important;
    filter: none !important;
    transition: none !important;
  }
}
""".strip()


FX_JS = """
<script>
(function() {
  function init() {
    var nodes = Array.prototype.slice.call(
      document.querySelectorAll('[data-martin-fx-reveal]')
    );
    if (!nodes.length) return;

    var reduced = false;
    try {
      reduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    } catch (e) {}

    if (reduced || !('IntersectionObserver' in window)) {
      nodes.forEach(function(node) { node.classList.add('martin-fx-in'); });
      return;
    }

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        var node = entry.target;
        var mode = node.getAttribute('data-martin-fx-reveal') || 'once';
        if (entry.isIntersecting) {
          node.classList.add('martin-fx-in');
          if (mode !== 'repeat') observer.unobserve(node);
        } else if (mode === 'repeat') {
          node.classList.remove('martin-fx-in');
        }
      });
    }, { threshold: 0.14, rootMargin: '0px 0px -6% 0px' });

    nodes.forEach(function(node) { observer.observe(node); });
  }

  window._martinFxInit = init;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
</script>
""".strip()


class Transition(FXStyle):
    """
    Add CSS transitions with a Python API.

        Transition()
        Transition("transform", duration=0.4, timing="ease-out")
        Transition("transform").hover("translateY(-4px)")
    """

    def __init__(
        self,
        property="all",
        duration=0.22,
        timing="ease",
        delay=0,
        disabled=False,
    ):
        self.property = property
        self.duration = duration
        self.timing = timing
        self.delay = delay
        self.disabled = disabled

    def hover(
        self,
        transform=None,
        *,
        scale=None,
        shadow=None,
        filter=None,
        opacity=None,
        background=None,
        color=None,
        border_color=None,
    ):
        return [
            self,
            Hover(
                transform=transform,
                scale=scale,
                shadow=shadow,
                filter=filter,
                opacity=opacity,
                background=background,
                color=color,
                border_color=border_color,
                duration=self.duration,
                timing=self.timing,
                delay=self.delay,
            ),
        ]

    def to_css(self) -> dict:
        if self.disabled:
            return {"transition": "none"}
        return {
            "transition": (
                f"{self.property} {_seconds(self.duration)} {self.timing} "
                f"{_seconds(self.delay)}"
            ).strip()
        }


class Hover(FXStyle):
    """Generic hover/focus effect controlled from Python."""

    def __init__(
        self,
        *,
        transform=None,
        scale=None,
        shadow=None,
        filter=None,
        opacity=None,
        background=None,
        color=None,
        border_color=None,
        duration=0.22,
        timing="ease",
        delay=0,
    ):
        self.transform = transform
        self.scale = scale
        self.shadow = shadow
        self.filter = filter
        self.opacity = opacity
        self.background = background
        self.color = color
        self.border_color = border_color
        self.duration = duration
        self.timing = timing
        self.delay = delay

    def _transform_value(self):
        pieces = []
        if self.transform:
            pieces.append(str(self.transform))
        if self.scale is not None:
            pieces.append(f"scale({self.scale})")
        return " ".join(pieces) if pieces else None

    def fx_attrs(self) -> dict:
        tokens = []
        if self._transform_value():
            tokens.append("transform")
        if self.shadow is not None:
            tokens.append("shadow")
        if self.filter is not None:
            tokens.append("filter")
        if self.opacity is not None:
            tokens.append("opacity")
        if self.background is not None:
            tokens.append("background")
        if self.color is not None:
            tokens.append("color")
        if self.border_color is not None:
            tokens.append("border")
        return {"data-martin-fx-hover": " ".join(tokens)} if tokens else {}

    def to_css(self) -> dict:
        css = {
            "--martin-fx-hover-duration": _seconds(self.duration),
            "--martin-fx-hover-timing": self.timing,
            "--martin-fx-hover-delay": _seconds(self.delay),
        }
        transform = self._transform_value()
        if transform is not None:
            css["--martin-fx-hover-transform"] = transform
        if self.shadow is not None:
            css["--martin-fx-hover-shadow"] = self.shadow
        if self.filter is not None:
            css["--martin-fx-hover-filter"] = self.filter
        if self.opacity is not None:
            css["--martin-fx-hover-opacity"] = str(self.opacity)
        if self.background is not None:
            css["--martin-fx-hover-background"] = self.background
        if self.color is not None:
            css["--martin-fx-hover-color"] = self.color
        if self.border_color is not None:
            css["--martin-fx-hover-border-color"] = self.border_color
        return css


class HoverLift(Hover):
    def __init__(
        self,
        distance=6,
        *,
        shadow="0 16px 32px rgba(15, 23, 42, 0.18)",
        scale=None,
        duration=0.22,
        timing="ease-out",
        delay=0,
    ):
        super().__init__(
            transform=f"translate3d(0, -{_dimension(distance)}, 0)",
            scale=scale,
            shadow=shadow,
            duration=duration,
            timing=timing,
            delay=delay,
        )


class HoverGlow(Hover):
    def __init__(
        self,
        color="#6366f1",
        *,
        strength=0.32,
        border=True,
        duration=0.24,
        timing="ease-out",
        delay=0,
    ):
        shadow = f"0 0 0 1px {_hex_to_rgba(color, min(strength + 0.12, 0.85))}, 0 18px 48px {_hex_to_rgba(color, strength)}"
        super().__init__(
            shadow=shadow,
            border_color=_hex_to_rgba(color, min(strength + 0.22, 0.95)) if border else None,
            duration=duration,
            timing=timing,
            delay=delay,
        )


class Stagger(FXStyle):
    """Delay helper for grids and lists."""

    def __init__(self, index, step=0.08, start=0, target="animation"):
        self.index = index
        self.step = step
        self.start = start
        self.target = target

    @classmethod
    def delay(cls, index, step=0.08, start=0) -> str:
        return _seconds(start + (index * step))

    def to_css(self) -> dict:
        delay = self.delay(self.index, step=self.step, start=self.start)
        css = {}
        if self.target in ("animation", "both"):
            css["animation-delay"] = delay
        if self.target in ("transition", "both"):
            css["transition-delay"] = delay
        return css


class ReducedMotion(FXStyle):
    """Explicit accessibility helper for reduced motion behavior."""

    def __init__(self, animations=True, transitions=True, reveal=True, hover=True):
        self.animations = animations
        self.transitions = transitions
        self.reveal = reveal
        self.hover = hover

    @classmethod
    def all(cls):
        return cls()

    @classmethod
    def animations_only(cls):
        return cls(transitions=False, reveal=False, hover=False)

    @classmethod
    def transitions_only(cls):
        return cls(animations=False, reveal=False, hover=False)

    def fx_attrs(self) -> dict:
        tokens = []
        if self.animations:
            tokens.append("animation")
        if self.transitions:
            tokens.append("transition")
        if self.reveal:
            tokens.append("reveal")
        if self.hover:
            tokens.append("hover")
        return {"data-martin-fx-reduce": " ".join(tokens)} if tokens else {}


class RevealOnScroll(FXStyle):
    """Reveal content when it enters the viewport."""

    def __init__(
        self,
        direction="up",
        distance=24,
        *,
        scale=1,
        blur=0,
        duration=0.7,
        delay=0,
        timing="cubic-bezier(0.22, 1, 0.36, 1)",
        once=True,
    ):
        offsets = {
            "up": ("0", _dimension(distance)),
            "down": ("0", _dimension(-distance)),
            "left": (_dimension(distance), "0"),
            "right": (_dimension(-distance), "0"),
            "none": ("0", "0"),
        }
        self.x, self.y = offsets.get(direction, offsets["up"])
        self.scale = scale
        self.blur = blur
        self.duration = duration
        self.delay = delay
        self.timing = timing
        self.once = once

    def fx_attrs(self) -> dict:
        return {"data-martin-fx-reveal": "once" if self.once else "repeat"}

    def to_css(self) -> dict:
        return {
            "--martin-fx-reveal-x": self.x,
            "--martin-fx-reveal-y": self.y,
            "--martin-fx-reveal-scale": str(self.scale),
            "--martin-fx-reveal-blur": _dimension(self.blur),
            "--martin-fx-reveal-duration": _seconds(self.duration),
            "--martin-fx-reveal-delay": _seconds(self.delay),
            "--martin-fx-reveal-timing": self.timing,
            "will-change": "opacity, transform, filter",
        }


class Animate(FXStyle):
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
        disabled=False,
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
        self.disabled = disabled

    @classmethod
    def fade_in(cls, duration=0.45, timing="ease-out", delay=0, disabled=False):
        return cls(
            "martin-fx-fade-in",
            duration=duration,
            timing=timing,
            delay=delay,
            will_change="opacity",
            disabled=disabled,
        )

    @classmethod
    def slide_in(
        cls, direction="up", distance=24, duration=0.55, delay=0, disabled=False
    ):
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
            disabled=disabled,
        )

    @classmethod
    def scale_in(cls, start=0.94, duration=0.45, delay=0, disabled=False):
        return cls(
            "martin-fx-scale-in",
            duration=duration,
            timing="cubic-bezier(0.2, 0.8, 0.2, 1)",
            delay=delay,
            will_change="opacity, transform",
            extra_css={"--martin-fx-scale-from": str(start)},
            disabled=disabled,
        )

    @classmethod
    def blur_in(cls, blur=12, duration=0.5, delay=0, disabled=False):
        return cls(
            "martin-fx-blur-in",
            duration=duration,
            timing="ease-out",
            delay=delay,
            will_change="opacity, filter",
            extra_css={"--martin-fx-blur-from": _dimension(blur)},
            disabled=disabled,
        )

    @classmethod
    def rotate_in(
        cls, angle=8, duration=0.55, delay=0, origin="center center", disabled=False
    ):
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
            disabled=disabled,
        )

    @classmethod
    def float(cls, distance=10, duration=3.2, delay=0, disabled=False):
        return cls(
            "martin-fx-float",
            duration=duration,
            timing="ease-in-out",
            delay=delay,
            count="infinite",
            fill="both",
            will_change="transform",
            extra_css={"--martin-fx-float-distance": _dimension(distance)},
            disabled=disabled,
        )

    @classmethod
    def pulse(cls, scale=1.035, duration=2.2, delay=0, disabled=False):
        return cls(
            "martin-fx-pulse",
            duration=duration,
            timing="ease-in-out",
            delay=delay,
            count="infinite",
            fill="both",
            will_change="opacity, transform",
            extra_css={"--martin-fx-pulse-scale": str(scale)},
            disabled=disabled,
        )

    @classmethod
    def spin(cls, duration=1.1, timing="linear", delay=0, disabled=False):
        return cls(
            "martin-fx-spin",
            duration=duration,
            timing=timing,
            delay=delay,
            count="infinite",
            fill="both",
            will_change="transform",
            disabled=disabled,
        )

    def to_css(self) -> dict:
        css = dict(self.extra_css)
        css["animation"] = (
            "none"
            if self.disabled
            else (
                f"{self.name} {_seconds(self.duration)} {self.timing} "
                f"{_seconds(self.delay)} {self.count} {self.direction} {self.fill}"
            )
        )
        if self.state is not None:
            css["animation-play-state"] = self.state
        if self.will_change is not None:
            css["will-change"] = self.will_change
        return css


class FadeIn(Animate):
    def __init__(self, duration=0.45, timing="ease-out", delay=0, disabled=False):
        _copy_from(
            self,
            Animate.fade_in(
                duration=duration, timing=timing, delay=delay, disabled=disabled
            ),
        )


class SlideIn(Animate):
    def __init__(
        self, direction="up", distance=24, duration=0.55, delay=0, disabled=False
    ):
        _copy_from(
            self,
            Animate.slide_in(
                direction=direction,
                distance=distance,
                duration=duration,
                delay=delay,
                disabled=disabled,
            ),
        )


class ScaleIn(Animate):
    def __init__(self, start=0.94, duration=0.45, delay=0, disabled=False):
        _copy_from(
            self,
            Animate.scale_in(
                start=start, duration=duration, delay=delay, disabled=disabled
            ),
        )


class BlurIn(Animate):
    def __init__(self, blur=12, duration=0.5, delay=0, disabled=False):
        _copy_from(
            self,
            Animate.blur_in(
                blur=blur, duration=duration, delay=delay, disabled=disabled
            ),
        )


class RotateIn(Animate):
    def __init__(
        self,
        angle=8,
        duration=0.55,
        delay=0,
        origin="center center",
        disabled=False,
    ):
        _copy_from(
            self,
            Animate.rotate_in(
                angle=angle,
                duration=duration,
                delay=delay,
                origin=origin,
                disabled=disabled,
            ),
        )


class Float(Animate):
    def __init__(self, distance=10, duration=3.2, delay=0, disabled=False):
        _copy_from(
            self,
            Animate.float(
                distance=distance, duration=duration, delay=delay, disabled=disabled
            ),
        )


class Pulse(Animate):
    def __init__(self, scale=1.035, duration=2.2, delay=0, disabled=False):
        _copy_from(
            self,
            Animate.pulse(
                scale=scale, duration=duration, delay=delay, disabled=disabled
            ),
        )


class Spin(Animate):
    def __init__(self, duration=1.1, timing="linear", delay=0, disabled=False):
        _copy_from(
            self,
            Animate.spin(
                duration=duration, timing=timing, delay=delay, disabled=disabled
            ),
        )


__all__ = [
    "FX_CSS",
    "FX_JS",
    "stylesheet",
    "script",
    "FXStyle",
    "Transition",
    "Hover",
    "HoverLift",
    "HoverGlow",
    "Stagger",
    "ReducedMotion",
    "RevealOnScroll",
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
