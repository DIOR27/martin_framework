"""Minimal TODO widget.

Idea: render a visible placeholder for TODO items within the UI. This allows
the philosophy "TODO is a widget" to be realized at runtime and scaffold level.
"""

from ..widget import Widget


class TodoWidget(Widget):
    def __init__(self, text: str = "TODO", **kwargs):
        # Base widget props (style, padding, etc.) are optional; keep minimal.
        self._props = kwargs or {}
        self._text = text

    def render(self) -> str:
        # Simple, clean rendering with a subtle visual cue for TODOs.
        content = str(self._to_plain_text(self._text))
        # Keep markup stable and minimal to preserve elegance.
        html = (
            f'<span class="martin-todo" style="'
            "display:inline-block; padding:2px 6px; border-radius:6px; "
            "border:1px dashed var(--text-muted, #6b7280); color:var(--text-muted, #374151);"
            '">{content}</span>'
        )
        return self._wrap_url(html) if getattr(self, "_props", {}).get("url") else html
