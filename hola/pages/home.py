from martin import (
    Button,
    Calendar,
    CalendarEvent,
    Card,
    Code,
    Column,
    Divider,
    Grid,
    Heading,
    PageConfig,
    Paragraph,
    Raw,
    Row,
    Text,
)


def _t(key, fallback, tag="span"):
    return Raw(f'<{tag} data-i18n="{key}">{fallback}</{tag}>')


_HERO_CSS = Raw("""<style>
.hero-gradient {
    background: linear-gradient(135deg, var(--accent) 0%, color-mix(in srgb, var(--accent) 60%, transparent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.feature-card { transition: transform .2s, box-shadow .2s; }
.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(0,0,0,.12);
}
</style>""")


_FEATURES = [
    (
        "\u26a1",
        "home.features.fast.title",
        "R\u00e1pido",
        "home.features.fast.desc",
        "Servidor de desarrollo con hot-reload. Exporta HTML est\u00e1tico listo para producci\u00f3n.",
    ),
    (
        "\U0001f9e9",
        "home.features.composable.title",
        "Composable",
        "home.features.composable.desc",
        "Construye interfaces complejas con widgets simples y reutilizables.",
    ),
    (
        "\U0001f3a8",
        "home.features.elegant.title",
        "Elegante",
        "home.features.elegant.desc",
        "Tema oscuro/claro autom\u00e1tico. CSS moderno listo para usar desde el primer momento.",
    ),
    (
        "\U0001f40d",
        "home.features.python.title",
        "Solo Python",
        "home.features.python.desc",
        "Sin HTML, sin CSS, sin JavaScript. Todo se expresa en Python puro.",
    ),
]


def home():
    return Column(
        gap=0,
        align="stretch",
        justify="flex-start",
        children=[
            Raw(
                "<style>\n.hero-gradient {\n    background: linear-gradient(135deg, var(--accent) 0%, color-mix(in srgb, var(--accent) 60%, transparent) 100%);\n    -webkit-background-clip: text;\n    -webkit-text-fill-color: transparent;\n    background-clip: text;\n}\n.feature-card { transition: transform .2s, box-shadow .2s; }\n.feature-card:hover {\n    transform: translateY(-3px);\n    box-shadow: 0 8px 32px rgba(0,0,0,.12);\n}\n</style>"
            ),
            Column(
                gap=20,
                align="stretch",
                justify="flex-start",
                style="max-width: 860px; margin: 0 auto; align-items: center; text-align: center; padding-top: 96px; padding-bottom: 80px",
                padding=64,
                children=[
                    Calendar(
                        events=[
                            CalendarEvent(
                                title="Launch", date="2026-03-20", color="#6366f1"
                            ),
                            CalendarEvent(
                                title="Demo",
                                date="2026-03-25",
                                start_time="10:00",
                                end_time="11:00",
                                color="#10b981",
                            ),
                            CalendarEvent(
                                title="New Event", date="2026-03-15", color="#6366f1"
                            ),
                        ],
                        initial_view="month",
                        editable=True,
                        height=540,
                        range_select=False,
                        show_views=True,
                        show_today=True,
                        first_day=1,
                        locale="es",
                        accent="var(--accent)",
                        event_colors=[],
                        visible=True,
                        readonly=False,
                        disabled=False,
                        float_position="bottom-right",
                        float_offset=20,
                        float_gap=12,
                        float_z_index=999,
                    ),
                    Row(
                        gap=8,
                        align="center",
                        justify="center",
                        wrap=False,
                        children=[
                            Text(
                                "holassss",
                                style="font-size: 13px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); background: color-mix(in srgb,var(--accent) 12%,transparent); padding: 4px 12px; border-radius: 999px; border: 1px solid color-mix(in srgb,var(--accent) 30%,transparent)",
                            )
                        ],
                    ),
                    Heading(
                        "Let's build an incredible idea",
                        level=1,
                        style="font-size: clamp(36px,6vw,64px); font-weight: 800; letter-spacing: -2px; line-height: 1.1; margin: 0",
                    ),
                    Paragraph(
                        "Construido con Martin Framework — Python para la web, sin complicaciones.",
                        style="font-size: 18px; color: var(--text-muted); max-width: 560px; line-height: 1.6; margin: 0",
                    ),
                    Row(
                        gap=12,
                        align="center",
                        justify="center",
                        wrap=False,
                        style="margin-top: 8px",
                        children=[
                            Button(
                                "Ver componentes",
                                variant="primary",
                                href="/components",
                                disabled=False,
                                style="padding: 11px 24px; font-size: 15px",
                            ),
                            Button(
                                "GitHub",
                                variant="ghost",
                                href="https://github.com",
                                disabled=False,
                                style="padding: 11px 24px; font-size: 15px",
                            ),
                        ],
                    ),
                ],
            ),
            Column(
                gap=28,
                align="stretch",
                justify="flex-start",
                style="max-width: 1100px; margin: 0 auto; padding-top: 0",
                padding=48,
                children=[
                    Divider(color="var(--border)", thickness=1, vertical=False),
                    Heading(
                        "¿Por qué Martin?",
                        level=2,
                        style="font-size: 26px; font-weight: 700; text-align: center",
                    ),
                    Grid(
                        columns=2,
                        gap=16,
                        children=[
                            Card(
                                class_name="feature-card",
                                padding=24,
                                radius=14,
                                children=[
                                    Row(
                                        gap=10,
                                        align="center",
                                        justify="flex-start",
                                        wrap=False,
                                        children=[
                                            Text("⚡", style="font-size: 26px"),
                                            Heading(
                                                "Rápido",
                                                level=3,
                                                style="font-size: 16px; margin: 0",
                                            ),
                                        ],
                                    ),
                                    Paragraph(
                                        "Servidor de desarrollo con hot-reload. Exporta HTML estático listo para producción.",
                                        style="font-size: 14px; color: var(--text-muted); margin-top: 8px; line-height: 1.6",
                                    ),
                                ],
                            ),
                            Card(
                                class_name="feature-card",
                                padding=24,
                                radius=14,
                                children=[
                                    Row(
                                        gap=10,
                                        align="center",
                                        justify="flex-start",
                                        wrap=False,
                                        children=[
                                            Text("🧩", style="font-size: 26px"),
                                            Heading(
                                                "Composable",
                                                level=3,
                                                style="font-size: 16px; margin: 0",
                                            ),
                                        ],
                                    ),
                                    Paragraph(
                                        "Construye interfaces complejas con widgets simples y reutilizables.",
                                        style="font-size: 14px; color: var(--text-muted); margin-top: 8px; line-height: 1.6",
                                    ),
                                ],
                            ),
                            Card(
                                class_name="feature-card",
                                padding=24,
                                radius=14,
                                children=[
                                    Row(
                                        gap=10,
                                        align="center",
                                        justify="flex-start",
                                        wrap=False,
                                        children=[
                                            Text("🎨", style="font-size: 26px"),
                                            Heading(
                                                "Elegante",
                                                level=3,
                                                style="font-size: 16px; margin: 0",
                                            ),
                                        ],
                                    ),
                                    Paragraph(
                                        "Tema oscuro/claro automático. CSS moderno listo para usar desde el primer momento.",
                                        style="font-size: 14px; color: var(--text-muted); margin-top: 8px; line-height: 1.6",
                                    ),
                                ],
                            ),
                            Card(
                                class_name="feature-card",
                                padding=24,
                                radius=14,
                                children=[
                                    Row(
                                        gap=10,
                                        align="center",
                                        justify="flex-start",
                                        wrap=False,
                                        children=[
                                            Text("🐍", style="font-size: 26px"),
                                            Heading(
                                                "Solo Python",
                                                level=3,
                                                style="font-size: 16px; margin: 0",
                                            ),
                                        ],
                                    ),
                                    Paragraph(
                                        "Sin HTML, sin CSS, sin JavaScript. Todo se expresa en Python puro.",
                                        style="font-size: 14px; color: var(--text-muted); margin-top: 8px; line-height: 1.6",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            Column(
                gap=20,
                align="stretch",
                justify="flex-start",
                style="max-width: 760px; margin: 0 auto",
                padding=48,
                children=[
                    Divider(color="var(--border)", thickness=1, vertical=False),
                    Heading(
                        "Inicio rápido",
                        level=2,
                        style="font-size: 26px; font-weight: 700",
                    ),
                    Code(
                        "martin new mi_proyecto\ncd mi_proyecto\nmartin run",
                        language="bash",
                        block=True,
                        copy=True,
                        line_numbers=False,
                        theme="auto",
                        editable=False,
                    ),
                    Paragraph(
                        "Tu aplicación estará disponible en http://localhost:3908",
                        style="font-size: 14px; color: var(--text-muted)",
                    ),
                ],
            ),
        ],
    )
