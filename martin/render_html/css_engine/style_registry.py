from __future__ import annotations
import hashlib
import json


class StyleRegistry:
    """
    Registra estilos únicos y genera clases hash estables.
    """

    def __init__(self):
        self._styles = {}  # hash -> style_dict

    def register(self, style: dict) -> str:
        """
        Devuelve class_name.
        """
        normalized = self._normalize(style)
        style_json = json.dumps(normalized, sort_keys=True)
        style_hash = hashlib.sha1(style_json.encode()).hexdigest()[:8]

        class_name = f"m-{style_hash}"

        if class_name not in self._styles:
            self._styles[class_name] = normalized

        return class_name

    def get_all(self) -> dict:
        return self._styles

    def _normalize(self, style: dict) -> dict:
        """
        Convierte números a px si aplica.
        """
        result = {}

        for key, value in style.items():
            if isinstance(value, (int, float)):
                result[key] = f"{value}px"
            elif isinstance(value, dict):
                result[key] = self._normalize(value)
            else:
                result[key] = value

        return result
