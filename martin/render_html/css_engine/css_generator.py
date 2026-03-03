from __future__ import annotations


BREAKPOINTS = {
    "sm": "640px",
    "md": "768px",
    "lg": "1024px",
}


class CSSGenerator:

    def generate(self, styles: dict) -> str:
        css_parts = []

        for class_name, style_dict in styles.items():
            base, responsive, pseudo = self._split(style_dict)

            # Base rules
            if base:
                css_parts.append(self._rule(f".{class_name}", base))

            # Pseudo
            for pseudo_name, pseudo_styles in pseudo.items():
                css_parts.append(
                    self._rule(f".{class_name}:{pseudo_name}", pseudo_styles)
                )

            # Responsive
            for bp, bp_styles in responsive.items():
                media = f"@media (min-width: {BREAKPOINTS[bp]})"
                css_parts.append(
                    f"{media} {{\n{self._rule(f'.{class_name}', bp_styles, indent=2)}\n}}"
                )

        return "\n\n".join(css_parts)

    def _split(self, style_dict: dict):
        base = {}
        responsive = {}
        pseudo = {}

        for key, value in style_dict.items():
            if key in BREAKPOINTS:
                responsive[key] = value
            elif key in ("hover", "focus", "active"):
                pseudo[key] = value
            else:
                base[key] = value

        return base, responsive, pseudo

    def _rule(self, selector: str, styles: dict, indent: int = 0) -> str:
        space = " " * indent
        lines = [f"{space}{selector} {{"]

        for k, v in styles.items():
            lines.append(f"{space}  {self._to_css_prop(k)}: {v};")

        lines.append(f"{space}}}")
        return "\n".join(lines)

    def _to_css_prop(self, key: str) -> str:
        return key.replace("_", "-")
