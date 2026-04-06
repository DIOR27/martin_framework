from martin import (
    Column,
    Row,
    Grid,
    Card,
    Heading,
    Paragraph,
    Text,
    Button,
    Code,
    Divider,
    Raw,
    PageConfig,
    GradientText,
    TextStyle,
)
# Noise-free scaffolds by default; no toggle exposed


def _t(key, fallback, tag="span"):
    return Raw(f'<{tag} data-i18n="{key}">{fallback}</{tag}>')


_HERO_CSS = Raw("""<style>
.feature-card { transition: transform .2s, box-shadow .2s; }
.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(0,0,0,.12);
}
</style>""")


_FEATURES = [
    ("\u26a1", "home.features.fast.title", "R\u00e1pido", "home.features.fast.desc", "Servidor de desarrollo con hot-reload. Exporta HTML est\u00e1tico listo para producci\u00f3n."),
    ("\U0001f9e9", "home.features.composable.title", "Composable", "home.features.composable.desc", "Construye interfaces complejas con widgets simples y reutilizables."),
    ("\U0001f3a8", "home.features.elegant.title", "Elegante", "home.features.elegant.desc", "Tema oscuro/claro autom\u00e1tico. CSS moderno listo para usar desde el primer momento."),
    ("\U0001f40d", "home.features.python.title", "Solo Python", "home.features.python.desc", "Sin HTML, sin CSS, sin JavaScript. Todo se expresa en Python puro."),
]


def home():
    features = [
        Card(
            class_name="feature-card",
            padding=24,
            radius=14,
            children=[
                Row([
                    Text(icon, style="font-size:26px"),
                    Heading(_t(title_key, title), level=3, style="font-size:16px;margin:0"),
                ], gap=10, align="center"),
                Paragraph(_t(desc_key, desc), style="font-size:14px;color:var(--text-muted);margin-top:8px;line-height:1.6"),
            ],
        )
        for icon, title_key, title, desc_key, desc in _FEATURES
    ]

    return Column(
        gap=0,
        children=[
            _HERO_CSS,

            # ── Hero ──────────────────────────────────────────────────
            Column(
                gap=20,
                padding=64,
                style="max-width:860px;margin:0 auto;align-items:center;text-align:center;padding-top:96px;padding-bottom:80px",
                children=[
                    Row([
                        Text(
                            _t("home.badge", "hola"),
                            style=(
                                "font-size:13px;font-weight:600;letter-spacing:.08em;"
                                "text-transform:uppercase;color:var(--accent);"
                                "background:color-mix(in srgb,var(--accent) 12%,transparent);"
                                "padding:4px 12px;border-radius:999px;"
                                "border:1px solid color-mix(in srgb,var(--accent) 30%,transparent)"
                            ),
                        ),
                    ], justify="center"),
                    Heading(
                        _t("home.hero.title", "Let's build an incredible idea"),
                        level=1,
                        style=[GradientText.aurora(), TextStyle(size="clamp(36px,6vw,64px)", weight="800")],
                    ),
                    Paragraph(
                        _t("home.hero.subtitle", "Construido con Martin Framework \u2014 Python para la web, sin complicaciones."),
                        style="font-size:18px;color:var(--text-muted);max-width:560px;line-height:1.6;margin:0",
                    ),
                    Row(
                        gap=12,
                        justify="center",
                        style="margin-top:8px",
                        children=[
                            Button(_t("home.hero.primary", "Ver componentes"), href="/components", style="padding:11px 24px;font-size:15px"),
                            Button("GitHub", href="https://github.com", variant="ghost", style="padding:11px 24px;font-size:15px"),
                        ],
                    ),
                ],
            ),

            # Noisy blocks removed: scaffold remains clean by default

            # ── Features ──────────────────────────────────────────────
            Column(
                padding=48,
                gap=28,
                style="max-width:1100px;margin:0 auto;padding-top:0",
                children=[
                    Divider(),
                    Heading(_t("home.features.heading", "\u00bfPor qu\u00e9 Martin?"), level=2, style="font-size:26px;font-weight:700;text-align:center"),
                    Grid(columns=2, gap=16, children=features),
                ],
            ),

            # ── Quick start ────────────────────────────────────────────
            Column(
                padding=48,
                gap=20,
                style="max-width:760px;margin:0 auto",
                children=[
                    Divider(),
                    Heading(_t("home.quickstart.heading", "Inicio r\u00e1pido"), level=2, style="font-size:26px;font-weight:700"),
                    Code(
                        "martin new mi_proyecto\ncd mi_proyecto\nmartin run",
                        language="bash",
                        block=True,
                    ),
                    Paragraph(
                        _t("home.quickstart.caption", "Tu aplicaci\u00f3n estar\u00e1 disponible en http://localhost:3908"),
                        style="font-size:14px;color:var(--text-muted)",
                    ),
                ],
            ),
        ],
    ), PageConfig(title="Inicio \u2014 hola", description="Let's build an incredible idea")
