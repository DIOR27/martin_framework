from pathlib import Path


TEMPLATE_INDEX = """\
from martin.render_html.html_widgets import Page, Text
from martin.render_html.components import Section, Container, Card, Button
from martin.render_html.layout import Column


class Page(Page):
    def __init__(self):
        super().__init__(
            Section(
                Container(
                    Column(
                        Text(
                            "MARTIN",
                            style={
                                "font_size": 56,
                                "font_weight": 700,
                                "color": "white",
                                "letter_spacing": 3,
                            }
                        ),
                        Text(
                            "Marketing & Information Technologies",
                            style={
                                "font_size": 18,
                                "color": "rgba(255,255,255,0.6)"
                            }
                        ),
                        Card(
                            Column(
                                Text(
                                    "Framework moderno para agencias",
                                    style={
                                        "font_size": 20,
                                        "color": "white"
                                    }
                                ),
                                Button(
                                    "Comenzar",
                                    style={
                                        "background": "white",
                                        "color": "#0f172a",
                                        "hover": {
                                            "background": "#e2e8f0"
                                        }
                                    }
                                ),
                                gap=24
                            ),
                            style={
                                "background": "rgba(255,255,255,0.06)",
                                "backdrop_filter": "blur(30px)",
                                "border": "1px solid rgba(255,255,255,0.1)",
                                "padding": 40,
                                "margin_top": 40
                            }
                        ),
                        gap=16,
                        align="center",
                        style={"text_align": "center"}
                    )
                ),
                style={
                    "height": "100vh",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "background": "radial-gradient(circle at 20% 20%, #1e293b, #0f172a)",
                }
            ),
            title="MARTIN"
        )
"""


TEMPLATE_CONFIG = """\
[project]
name = "martin-site"
"""


def create_project(name: str):
    project_path = Path(name)

    if project_path.exists():
        print(f"❌ La carpeta '{name}' ya existe.")
        return

    # Crear estructura base
    project_path.mkdir()
    pages_dir = project_path / "pages"
    pages_dir.mkdir()

    # Crear pages/index.py
    (pages_dir / "index.py").write_text(TEMPLATE_INDEX)

    # Crear martin.toml
    (project_path / "martin.toml").write_text(TEMPLATE_CONFIG)

    print(f"\n✅ Proyecto '{name}' creado correctamente.")
    print(f"\nEstructura creada:")
    print(f"   {name}/")
    print(f"     pages/index.py")
    print(f"     martin.toml")
    print(f"\nSiguientes pasos:")
    print(f"   cd {name}")
    print(f"   martin dev\n")
