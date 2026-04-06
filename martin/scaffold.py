"""Scaffold templates para `martin new`."""

from datetime import datetime
from pathlib import Path
import shutil
import textwrap


DEFAULT_PROJECT_DESC = "Let's build an incredible idea"

ICON_CANDIDATES = [
    ("assets/default_icon.webp", "icon.webp"),
    ("assets/default_icon.png", "icon.png"),
    ("default_icon.webp", "icon.webp"),
    ("default_icon.png", "icon.png"),
]

SCAFFOLD_ASSETS = [
    ("assets/default_icon.webp", "icon.webp"),
    ("assets/logo_martin_glow.svg", "logo_martin_glow.svg"),
    ("assets/logo_martin_frame.svg", "logo_martin_frame.svg"),
    ("assets/logo_martin_stack.svg", "logo_martin_stack.svg"),
    ("assets/art_dog_field_sunrise.svg", "art_dog_field_sunrise.svg"),
    ("assets/art_dog_field_twilight.svg", "art_dog_field_twilight.svg"),
    ("assets/art_dog_hill_breeze.svg", "art_dog_hill_breeze.svg"),
    ("assets/art_dog_meadow_neon.svg", "art_dog_meadow_neon.svg"),
    ("assets/art_dog_day_blossom.svg", "art_dog_day_blossom.svg"),
    ("assets/art_dog_day_garden.svg", "art_dog_day_garden.svg"),
    ("default_icon.webp", "icon.webp"),
    ("logo_martin_glow.svg", "logo_martin_glow.svg"),
    ("logo_martin_frame.svg", "logo_martin_frame.svg"),
    ("logo_martin_stack.svg", "logo_martin_stack.svg"),
    ("art_dog_field_sunrise.svg", "art_dog_field_sunrise.svg"),
    ("art_dog_field_twilight.svg", "art_dog_field_twilight.svg"),
    ("art_dog_hill_breeze.svg", "art_dog_hill_breeze.svg"),
    ("art_dog_meadow_neon.svg", "art_dog_meadow_neon.svg"),
    ("art_dog_day_blossom.svg", "art_dog_day_blossom.svg"),
    ("art_dog_day_garden.svg", "art_dog_day_garden.svg"),
]


GITIGNORE = (
    textwrap.dedent(
"""
    __pycache__/
    *.py[cod]
    .env
    venv/
    dist/
    .DS_Store
    """
    ).strip()
    + "\n"
)


README_TEMPLATE = (
    textwrap.dedent(
        """
    # {name}

    Proyecto construido con Martin Framework.

    ## Inicio rapido

    ```bash
    martin run
    ```

    ## Exportar

    ```bash
    martin export
    ```
    """
    ).strip()
    + "\n"
)


LOCALE_ES_ES_TEMPLATE = (
    textwrap.dedent(
        """
    msgid ""
    msgstr ""
    "Language: es_ES\\n"
    "Content-Type: text/plain; charset=UTF-8\\n"

    msgid "nav.home"
    msgstr "Inicio"

    msgid "nav.components"
    msgstr "Componentes"

    msgid "nav.start"
    msgstr "Comenzar"

    msgid "footer.rights"
    msgstr "© YEAR PROJECT_NAME"

    msgid "footer.components"
    msgstr "Componentes"

    msgid "home.badge"
    msgstr "PROJECT_NAME"

    msgid "home.hero.title"
    msgstr "PROJECT_DESC"

    msgid "home.hero.subtitle"
    msgstr "Construido con Martin Framework - Python para la web, sin complicaciones."

    msgid "home.hero.primary"
    msgstr "Ver componentes"

    msgid "home.features.heading"
    msgstr "¿Por qué Martin?"

    msgid "home.features.fast.title"
    msgstr "Rápido"

    msgid "home.features.fast.desc"
    msgstr "Servidor de desarrollo con hot-reload. Exporta HTML estático listo para producción."

    msgid "home.features.composable.title"
    msgstr "Composable"

    msgid "home.features.composable.desc"
    msgstr "Construye interfaces complejas con widgets simples y reutilizables."

    msgid "home.features.elegant.title"
    msgstr "Elegante"

    msgid "home.features.elegant.desc"
    msgstr "Tema oscuro/claro automático. CSS moderno listo para usar desde el primer momento."

    msgid "home.features.python.title"
    msgstr "Solo Python"

    msgid "home.features.python.desc"
    msgstr "Sin HTML, sin CSS, sin JavaScript. Todo se expresa en Python puro."

    msgid "home.quickstart.heading"
    msgstr "Inicio rápido"

    msgid "home.quickstart.caption"
    msgstr "Tu aplicación estará disponible en http://localhost:3908"

    msgid "components.title"
    msgstr "Componentes"

    msgid "components.subtitle"
    msgstr "Widgets disponibles con demos en vivo. Haz clic en cualquier elemento para ver cómo funciona."
    """
    ).strip()
    + "\n"
)


LOCALE_EN_US_TEMPLATE = (
    textwrap.dedent(
        """
    msgid ""
    msgstr ""
    "Language: en_US\\n"
    "Content-Type: text/plain; charset=UTF-8\\n"

    msgid "nav.home"
    msgstr "Home"

    msgid "nav.components"
    msgstr "Components"

    msgid "nav.start"
    msgstr "Get Started"

    msgid "footer.rights"
    msgstr "© YEAR PROJECT_NAME"

    msgid "footer.components"
    msgstr "Components"

    msgid "home.badge"
    msgstr "PROJECT_NAME"

    msgid "home.hero.title"
    msgstr "PROJECT_DESC"

    msgid "home.hero.subtitle"
    msgstr "Built with Martin Framework - Python for the web, without the usual complexity."

    msgid "home.hero.primary"
    msgstr "View components"

    msgid "home.features.heading"
    msgstr "Why Martin?"

    msgid "home.features.fast.title"
    msgstr "Fast"

    msgid "home.features.fast.desc"
    msgstr "Development server with hot reload. Export static HTML ready for production."

    msgid "home.features.composable.title"
    msgstr "Composable"

    msgid "home.features.composable.desc"
    msgstr "Build complex interfaces from simple, reusable widgets."

    msgid "home.features.elegant.title"
    msgstr "Elegant"

    msgid "home.features.elegant.desc"
    msgstr "Automatic dark and light themes. Modern CSS from day one."

    msgid "home.features.python.title"
    msgstr "Python Only"

    msgid "home.features.python.desc"
    msgstr "No HTML, no CSS, no JavaScript. Everything is expressed in plain Python."

    msgid "home.quickstart.heading"
    msgstr "Quick start"

    msgid "home.quickstart.caption"
    msgstr "Your application will be available at http://localhost:3908"

    msgid "components.title"
    msgstr "Components"

    msgid "components.subtitle"
    msgstr "Available widgets with live demos. Click any element to see how it behaves."
    """
    ).strip()
    + "\n"
)


MAIN_TEMPLATE = (
    textwrap.dedent(
        """
    from martin import *
    # TodoWidget is not imported here to avoid noise in generated scaffolds
    from martin.backend import Backend
    from pages.home import home
    from pages.components import components, register_components_backend
    
    router = Router()
    router.add("/",           home,       title="Inicio")
    router.add("/components", components, title="Componentes")

    _MESSAGES = load_locale_catalogs("locales")
    _LANGUAGE_SWITCHER = LanguageSelector(
        path="locales",
        value="es_ES",
        translations=_MESSAGES,
        width=240,
    )

    # ── Navbar global ──────────────────────────────────────────────────────
    # brand   → cualquier widget: Heading, Image, Row([Image, Heading]) etc.
    #   Solo nombre:    brand=Heading("MiApp", level=3)
    #   Solo logo:      brand=Image("/assets/logo.svg", height=32)
    #   Logo + nombre:  brand=Row([Image("/assets/logo.svg", height=28),
    #                              Heading("MiApp", level=4)], gap=8, align="center")
    # links   → lista de Link, Button u otros widgets (centro)
    # actions → botones/widgets a la derecha (login, CTA, ThemeToggle...)
    # Desde una pagina: return widget, PageConfig(header=False)         # desactiva
    #                   return widget, PageConfig(header=MiNavCustom()) # reemplaza
    _nav = NavBar(
        brand=Heading("PROJECT_NAME", level=3, color="var(--text)", style="letter-spacing:-0.5px"),
        links=[
            Link(Raw('<span data-i18n="nav.home">Inicio</span>'), href="/", style="color:var(--text);text-decoration:none;font-size:14px"),
            Link(Raw('<span data-i18n="nav.components">Componentes</span>'), href="/components", style="color:var(--text-muted);text-decoration:none;font-size:14px"),
        ],
        actions=[
            _LANGUAGE_SWITCHER,
            Button(Raw('<span data-i18n="nav.start">Comenzar</span>'), href="/components", radius=8),
        ],
    )

    _footer = Footer(
        left=Raw('<span data-i18n="footer.rights" style="font-size:13px;color:var(--text-muted)">© YEAR PROJECT_NAME</span>'),
        right=Row([
            Link(Raw('<span data-i18n="footer.components">Componentes</span>'), href="/components",
                 style="font-size:13px;text-decoration:none;color:var(--text-muted)"),
        ], gap=16),
    )

    app = App(
        router=router,
        title="PROJECT_NAME",
        theme="auto",
        header=_nav,
        footer=_footer,
        # logo="logo.png",  # archivo en assets/ — reemplaza el auto-detectado
        description="PROJECT_DESC",
        lang="es-ES",
    )

    backend = Backend(prefix="/api")
    register_components_backend(backend)
    backend.mount(app)

    if __name__ == "__main__":
        app.run()
    """
    ).strip()
    + "\n"
)


HOME_TEMPLATE = (
    textwrap.dedent(
        """
    from martin import *
    # Noise-free scaffolds by default; no toggle exposed


    def _t(key, fallback, tag="span"):
        return Raw(f'<{tag} data-i18n="{key}">{fallback}</{tag}>')


    _HERO_CSS = Raw(\"\"\"<style>
    .feature-card { transition: transform .2s, box-shadow .2s; }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(0,0,0,.12);
    }
    </style>\"\"\")


    _FEATURES = [
        ("\\u26a1", "home.features.fast.title", "R\\u00e1pido", "home.features.fast.desc", "Servidor de desarrollo con hot-reload. Exporta HTML est\\u00e1tico listo para producci\\u00f3n."),
        ("\\U0001f9e9", "home.features.composable.title", "Composable", "home.features.composable.desc", "Construye interfaces complejas con widgets simples y reutilizables."),
        ("\\U0001f3a8", "home.features.elegant.title", "Elegante", "home.features.elegant.desc", "Tema oscuro/claro autom\\u00e1tico. CSS moderno listo para usar desde el primer momento."),
        ("\\U0001f40d", "home.features.python.title", "Solo Python", "home.features.python.desc", "Sin HTML, sin CSS, sin JavaScript. Todo se expresa en Python puro."),
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
                                _t("home.badge", "PROJECT_NAME"),
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
                            _t("home.hero.title", "PROJECT_DESC"),
                            level=1,
                            style=[GradientText.aurora(), TextStyle(size="clamp(36px,6vw,64px)", weight="800")],
                        ),
                        Paragraph(
                            _t("home.hero.subtitle", "Construido con Martin Framework \\u2014 Python para la web, sin complicaciones."),
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
                        Heading(_t("home.features.heading", "\\u00bfPor qu\\u00e9 Martin?"), level=2, style="font-size:26px;font-weight:700;text-align:center"),
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
                        Heading(_t("home.quickstart.heading", "Inicio r\\u00e1pido"), level=2, style="font-size:26px;font-weight:700"),
                        Code(
                            "martin new mi_proyecto\\ncd mi_proyecto\\nmartin run",
                            language="bash",
                            block=True,
                        ),
                        Paragraph(
                            _t("home.quickstart.caption", "Tu aplicaci\\u00f3n estar\\u00e1 disponible en http://localhost:3908"),
                            style="font-size:14px;color:var(--text-muted)",
                        ),
                    ],
                ),
            ],
        ), PageConfig(title="Inicio \\u2014 PROJECT_NAME", description="PROJECT_DESC")
    """
    ).strip()
    + "\n"
)


COMPONENTS_TEMPLATE = (
    textwrap.dedent(
        """
from martin import *
from martin.backend import ApiCall, Backend, MethodCall, Ref, Response, ResultBox
from martin.fx import (
    FadeIn, SlideIn, ScaleIn, Pulse, Spin, Transition,
    Hover, HoverLift, HoverGlow, Stagger, ReducedMotion, RevealOnScroll,
)
from martin.widgets import __all__ as MARTIN_WIDGETS


    def _slug(name: str) -> str:
        return name.lower().replace("_", "-")


    def _t(key, fallback, tag="span"):
        return Raw(f'<{tag} data-i18n="{key}">{fallback}</{tag}>')


    def _in_studio_preview() -> bool:
        module_name = str(globals().get("__name__", ""))
        return (
            module_name.startswith("_martin_studio_preview_")
            or module_name.startswith("_martin_studio_design_")
        )


    def _sec(title, subtitle, children, widget_name=None):
        anchor_id = f"widget-{_slug(widget_name or title)}"
        return Card(
            id=anchor_id,
            padding=24,
            style="scroll-margin-top:88px",
            children=[
                Column(gap=4, style="margin-bottom:16px", children=[
                    Text(title.upper(),
                         style=TextStyle(size=11, weight="700", color="var(--text-muted)",
                                         letter_spacing=1)),
                    Text(subtitle, style=TextStyle(size=13, color="var(--text-muted)")),
                ]),
                Column(gap=12, children=children),
            ],
            )


    def register_components_backend(backend: Backend):
        _resource_leads = [
            {"id": "1", "nombre": "Ana García", "email": "ana@example.com", "estado": "Nuevo", "plan": "pro", "notas": "Lead inbound desde web."},
            {"id": "2", "nombre": "Luis Torres", "email": "luis@example.com", "estado": "Calificado", "plan": "starter", "notas": "Solicita demo corta."},
            {"id": "3", "nombre": "María Silva", "email": "maria@example.com", "estado": "Seguimiento", "plan": "enterprise", "notas": "Comparando planes empresariales."},
        ]

        @backend.post("/demo/contact")
        def demo_contact(req):
            data = req.json(default={}, silent=True) or {}
            nombre = str(data.get("nombre", "")).strip()
            email = str(data.get("email", "")).strip()
            mensaje = str(data.get("mensaje", "")).strip()

            if not nombre or not email or not mensaje:
                return Response(
                    backend.with_toast(
                        {"message": "Completa nombre, email y mensaje."},
                        message="Completa nombre, email y mensaje.",
                        variant="error",
                        position="top-right",
                    ),
                    status=400,
                )

            if "@" not in email or "." not in email.split("@")[-1]:
                return Response(
                    backend.with_toast(
                        {"message": "Ingresa un email valido."},
                        message="Ingresa un email valido.",
                        variant="error",
                        position="top-right",
                    ),
                    status=400,
                )

            if backend.mailer:
                backend.send_mail(
                    subject=f"Nuevo mensaje desde PROJECT_NAME",
                    to=getattr(backend.mailer.config, "sender", "") or email,
                    text=(
                        f"Nombre: {nombre}\\n"
                        f"Email: {email}\\n\\n"
                        f"Mensaje:\\n{mensaje}"
                    ),
                    html=(
                        "<h2>Nuevo mensaje desde PROJECT_NAME</h2>"
                        f"<p><strong>Nombre:</strong> {nombre}</p>"
                        f"<p><strong>Email:</strong> {email}</p>"
                        f"<p><strong>Mensaje:</strong><br>{mensaje}</p>"
                    ),
                    reply_to=email,
                )
                return backend.with_toast(
                    {"message": "Mensaje enviado por SMTP correctamente."},
                    message="Correo enviado por SMTP.",
                    variant="success",
                    position="top-right",
                )

            return backend.with_toast({
                "message": (
                    "Demo recibida. Configura SMTP con "
                    "backend.configure_smtp(...) para envio real."
                ),
                "nombre": nombre,
                "email": email,
            }, message="Demo recibida correctamente.", variant="success", position="top-right")

        @backend.get("/resources/leads/list")
        def resource_leads_list(req):
            estado = str(req.query.get("estado", "")).strip().lower()
            plan = str(req.query.get("plan", "")).strip().lower()
            query = str(req.query.get("q", "")).strip().lower()
            page = max(1, int(str(req.query.get("page", "1") or "1")))
            per_page = max(1, int(str(req.query.get("per_page", "10") or "10")))
            rows = list(_resource_leads)
            if estado:
                rows = [row for row in rows if str(row.get("estado", "")).strip().lower() == estado]
            if plan:
                rows = [row for row in rows if str(row.get("plan", "")).strip().lower() == plan]
            if query:
                rows = [
                    row for row in rows
                    if query in str(row.get("nombre", "")).strip().lower()
                    or query in str(row.get("email", "")).strip().lower()
                    or query in str(row.get("plan", "")).strip().lower()
                ]
            total = len(rows)
            pages = max(1, (total + per_page - 1) // per_page)
            page = min(page, pages)
            start = (page - 1) * per_page
            page_rows = rows[start : start + per_page]
            return backend.with_toast(
                {"rows": page_rows, "meta": {"page": page, "per_page": per_page, "total": total, "pages": pages}},
                message="Lista de leads actualizada.",
                variant="info",
                position="top-right",
                duration=2200,
            )

        @backend.get("/resources/leads/stats")
        def resource_leads_stats(req):
            total = len(_resource_leads)
            qualified = sum(1 for item in _resource_leads if str(item.get("estado", "")).strip().lower() == "calificado")
            follow_up = sum(1 for item in _resource_leads if str(item.get("estado", "")).strip().lower() == "seguimiento")
            enterprise = sum(1 for item in _resource_leads if str(item.get("plan", "")).strip().lower() == "enterprise")
            return {"stats": {"total": total, "qualified": qualified, "follow_up": follow_up, "enterprise": enterprise}}

        @backend.get("/resources/leads/detail")
        def resource_leads_detail(req):
            wanted = str(req.query.get("id", "1") or "1").strip()
            record = next((item for item in _resource_leads if str(item.get("id", "")).strip() == wanted), None)
            if record is None:
                try:
                    index = max(0, int(wanted))
                except Exception:
                    index = 0
                record = _resource_leads[index] if _resource_leads else {}
            return {"record": dict(record)}

        @backend.post("/resources/leads/save")
        def resource_leads_save(req):
            data = req.json(default={}, silent=True) or {}
            record_id = str(data.get("id", "") or "").strip()
            nombre = str(data.get("nombre", "")).strip()
            email = str(data.get("email", "")).strip()
            plan = str(data.get("plan", "starter") or "starter").strip()
            notas = str(data.get("notas", "")).strip()
            if not nombre or not email:
                return Response(
                    backend.with_toast(
                        {"message": "Nombre y email son obligatorios."},
                        message="Completa nombre y email.",
                        variant="error",
                        position="top-right",
                    ),
                    status=400,
                )
            updated = False
            if record_id:
                for item in _resource_leads:
                    if str(item.get("id", "")).strip() == record_id:
                        item["nombre"] = nombre
                        item["email"] = email
                        item["plan"] = plan
                        item["notas"] = notas
                        item["estado"] = str(data.get("estado", item.get("estado", "Nuevo")) or item.get("estado", "Nuevo")).strip()
                        updated = True
                        break
            if not updated:
                next_id = str(max([int(str(item.get("id", "0") or "0")) for item in _resource_leads] + [0]) + 1)
                _resource_leads.append(
                    {
                        "id": next_id,
                        "nombre": nombre,
                        "email": email,
                        "estado": "Nuevo",
                        "plan": plan,
                        "notas": notas,
                    }
                )
            return backend.with_toast(
                {"message": f"Lead guardado para {nombre}.", "rows": list(_resource_leads)},
                message=f"Lead {'actualizado' if updated else 'guardado'}: {nombre}.",
                variant="success",
                position="top-right",
            )

        @backend.post("/resources/leads/delete")
        def resource_leads_delete(req):
            data = req.json(default={}, silent=True) or {}
            record_id = str(data.get("id", "") or "").strip()
            before = len(_resource_leads)
            _resource_leads[:] = [item for item in _resource_leads if str(item.get("id", "")).strip() != record_id]
            removed = len(_resource_leads) < before
            return backend.with_toast(
                {"deleted": removed, "rows": list(_resource_leads)},
                message="Lead eliminado." if removed else "No se encontró el lead a eliminar.",
                variant="success" if removed else "warning",
                position="top-right",
            )

        @backend.post("/resources/leads/duplicate")
        def resource_leads_duplicate(req):
            data = req.json(default={}, silent=True) or {}
            record_id = str(data.get("id", "") or "").strip()
            source = next((item for item in _resource_leads if str(item.get("id", "")).strip() == record_id), None)
            if source is None:
                return Response(
                    backend.with_toast(
                        {"message": "No se encontró el lead a duplicar."},
                        message="No se encontró el lead a duplicar.",
                        variant="warning",
                        position="top-right",
                    ),
                    status=404,
                )
            next_id = str(max([int(str(item.get("id", "0") or "0")) for item in _resource_leads] + [0]) + 1)
            duplicated = dict(source)
            duplicated["id"] = next_id
            duplicated["nombre"] = str(data.get("nombre") or f"{source.get('nombre', 'Lead')} copia").strip()
            duplicated["email"] = str(data.get("email") or source.get("email") or "").strip()
            duplicated["estado"] = str(data.get("estado") or "Nuevo").strip()
            duplicated["notas"] = str(data.get("notas") or source.get("notas") or "").strip()
            _resource_leads.append(duplicated)
            return backend.with_toast(
                {"message": f"Lead duplicado: {duplicated['nombre']}.", "rows": list(_resource_leads)},
                message=f"Lead duplicado: {duplicated['nombre']}.",
                variant="success",
                position="top-right",
            )

        @backend.post("/resources/leads/bulk")
        def resource_leads_bulk(req):
            data = req.json(default={}, silent=True) or {}
            ids = [str(item).strip() for item in (data.get("ids") or []) if str(item).strip()]
            action = str(data.get("action", "follow_up") or "follow_up").strip()
            if not ids:
                return Response(
                    backend.with_toast(
                        {"message": "Selecciona al menos un lead."},
                        message="Selecciona al menos un lead.",
                        variant="warning",
                        position="top-right",
                    ),
                    status=400,
                )
            changed = 0
            if action == "delete":
                before = len(_resource_leads)
                _resource_leads[:] = [item for item in _resource_leads if str(item.get("id", "")).strip() not in ids]
                changed = before - len(_resource_leads)
            else:
                for item in _resource_leads:
                    if str(item.get("id", "")).strip() in ids:
                        item["estado"] = "Seguimiento"
                        changed += 1
            return backend.with_toast(
                {"rows": list(_resource_leads), "changed": changed, "action": action},
                message=f"Acción masiva aplicada a {changed} lead(s).",
                variant="success",
                position="top-right",
            )

        @backend.post("/auth/login")
        def demo_auth_login(req):
            data = req.json(default={}, silent=True) or {}
            user = str(data.get("user", "")).strip()
            password = str(data.get("password", "")).strip()
            if user != "admin" or password != "martin":
                return Response(
                    backend.with_toast(
                        {"error": "Credenciales inválidas."},
                        message="Credenciales inválidas.",
                        variant="error",
                        position="top-right",
                    ),
                    status=401,
                )
            resp = backend.login({"user": user, "role": "admin"})
            resp.data = backend.with_toast(
                {"message": f"Sesión iniciada para {user}.", "user": user},
                message=f"Bienvenido, {user}.",
                variant="success",
                position="top-right",
            )
            return resp

        @backend.post("/auth/logout")
        def demo_auth_logout(req):
            resp = backend.logout(req)
            resp.data = backend.with_toast(
                {"message": "Sesión cerrada."},
                message="Sesión cerrada.",
                variant="info",
                position="top-right",
            )
            return resp

        @backend.get("/auth/me")
        @backend.require_auth
        def demo_auth_me(req):
            session = backend.get_session(req, default={}) or {}
            return {"user": session}

        @backend.post("/demo/validate/email")
        def demo_validate_email(req):
            data = req.json(default={}, silent=True) or {}
            raw = str(data.get("value", "")).strip().lower()
            taken = {"admin@martin.dev", "soporte@martin.dev", "ventas@martin.dev"}
            if not raw:
                return {"valid": False, "message": "El email es obligatorio."}
            if "@" not in raw or "." not in raw.split("@")[-1]:
                return {"valid": False, "message": "Formato de email inválido."}
            if raw in taken:
                return {"valid": False, "message": "El email ya está en uso."}
            return {"valid": True, "message": "El email está disponible."}

        @backend.post("/demo/contact/validate")
        def demo_contact_validate(req):
            data = req.json(default={}, silent=True) or {}
            errors = {}
            nombre = str(data.get("nombre", "")).strip()
            email = str(data.get("email", "")).strip()
            mensaje = str(data.get("mensaje", "")).strip()
            if not nombre:
                errors["nombre"] = "El nombre es obligatorio."
            if not email or "@" not in email or "." not in email.split("@")[-1]:
                errors["email"] = "Email inválido."
            if not mensaje:
                errors["mensaje"] = "El mensaje no puede estar vacío."
            if errors:
                return Response({"valid": False, "errors": errors}, status=400)
            return {"valid": True, "message": "Todos los campos son válidos."}


    def components():
        # ── Layout ─────────────────────────────────────────────────────
        secs = [
            _sec("Container", "El bloque más básico de Martin.", [
                Container(
                    padding=20,
                    style="background:var(--surface-2);border-radius:8px",
                    children=[Text("Container")],
                ),
            ]),
            _sec("Column", "Hijos apilados verticalmente.", [
                Column(gap=12, children=[
                    Text("Item 1"),
                    Text("Item 2"),
                    Text("Item 3"),
                ]),
            ]),
            _sec("Row", "Hijos en línea horizontal.", [
                Row(gap=12, children=[
                    Text("A"),
                    Text("B"),
                    Text("C"),
                ]),
            ]),
            _sec("Grid", "Cuadrícula flexible.", [
                Grid(columns=3, gap=8, children=[
                    Text(f"Col {i}") for i in range(1, 4)
                ]),
            ]),
            _sec("Card", "Tarjeta con sombra.", [
                Card(padding=20, children=[
                    Text("Contenido de tarjeta"),
                ]),
            ]),
            _sec("Section", "Bloque semántico de sección.", [
                Section(padding=30, children=[
                    Text("Sección"),
                ]),
            ]),
            _sec("Divider", "Línea separadora.", [
                Divider(),
            ]),
            _sec("Spacer", "Espacio flexible.", [
                Row(children=[
                    Text("A"),
                    Spacer(),
                    Text("B"),
                ]),
            ]),
        ]

        # ── Typography ───────────────────────────────────────────────
        secs.append(_sec("Heading", "Encabezados de varios niveles.", [
            Heading("Título 1", level=1),
            Heading("Título 2", level=2),
            Heading("Título 3", level=3),
            Heading("Título 4", level=4),
        ]))

        secs.append(_sec("Text & Paragraph", "Texto simple y párrafos.", [
            Text("Texto en línea"),
            Paragraph("Párrafo de texto más largo con cuerpo."),
        ]))

        secs.append(_sec("Link", "Enlaces.", [
            Link("Ir a inicio", href="/"),
        ]))

        secs.append(_sec("Code", "Bloques de código.", [
            Code("print('hello')", language="python", block=True),
        ]))

        # ── Forms ────────────────────────────────────────────────────
        secs.append(_sec("TextField", "Campo de texto.", [
            TextField(placeholder="Escribe algo..."),
        ]))

        secs.append(_sec("TextArea", "Área de texto multilínea.", [
            TextArea(placeholder="Escribe un mensaje...", rows=4),
        ]))

        secs.append(_sec("Select", "Selector desplegable.", [
            Select(options=[("opt1", "Opción 1"), ("opt2", "Opción 2")], value="opt1"),
        ]))

        secs.append(_sec("MultiSelect", "Selector múltiple.", [
            MultiSelect(options=[("a", "A"), ("b", "B")], value=["a"]),
        ]))

        secs.append(_sec("Checkbox", "Casilla de verificación.", [
            Checkbox(label="Acepto los términos", checked=True),
        ]))

        secs.append(_sec("Slider", "Control deslizante.", [
            Slider(value=50, min=0, max=100),
        ]))

        secs.append(_sec("ColorPicker", "Selector de color.", [
            ColorPicker(value="#818cf8"),
        ]))

        secs.append(_sec("DatePicker", "Selector de fecha.", [
            DatePicker(),
        ]))

        # ── Buttons ─────────────────────────────────────────────────
        secs.append(_sec("Button", "Botones.", [
            Row(gap=8, children=[
                Button("Primario"),
                Button("Secundario", variant="secondary"),
                Button("Ghost", variant="ghost"),
            ]),
        ]))

        # ── Media ────────────────────────────────────────────────────
        secs.append(_sec("Image", "Imágenes.", [
            Image(src="https://picsum.photos/200/100", alt="Demo"),
        ]))

        secs.append(_sec("Avatar", "Avatar de usuario.", [
            Avatar(name="Ana García"),
            Avatar(name="Luis Torres", src="https://i.pravatar.cc/150?img=3"),
        ]))

        # ── Feedback ─────────────────────────────────────────────────
        secs.append(_sec("Alert", "Alerta informativa.", [
            Alert("Esto es una alerta.", variant="info"),
            Alert("Advertencia.", variant="warning"),
            Alert("Error.", variant="error"),
            Alert("Éxito.", variant="success"),
        ]))

        secs.append(_sec("Toast", "Notificación temporal.", [
            Button("Mostrar Toast", onclick=lambda: backend.toast("Mensaje toast")),
        ]))

        secs.append(_sec("Skeleton", "Esqueleto de carga.", [
            Skeleton(height=20),
        ]))

        secs.append(_sec("EmptyState", "Estado vacío.", [
            EmptyState(title="Sin datos", description="No hay elementos que mostrar."),
        ]))

        secs.append(_sec("ErrorState", "Estado de error.", [
            ErrorState(title="Error", description="Algo salió mal."),
        ]))

        # ── Navigation ──────────────────────────────────────────────
        secs.append(_sec("NavBar", "Barra de navegación.", [
            NavBar(
                brand=Heading("MiApp", level=3),
                links=[
                    Link("Inicio", href="/"),
                    Link("Acerca", href="/about"),
                ],
                actions=[Button("Login", variant="ghost")],
            ),
        ]))

        secs.append(_sec("Tabs", "Pestañas.", [
            Tabs(tabs=[("tab1", "Pestaña 1"), ("tab2", "Pestaña 2")]),
        ]))

        secs.append(_sec("Breadcrumb", "Miga de pan.", [
            Breadcrumb(items=[("Home", "/"), ("Products", "/products"), ("Item", "#")]),
        ]))

        # ── Data ────────────────────────────────────────────────────
        secs.append(_sec("Table", "Tabla de datos.", [
            Table(
                columns=["Nombre", "Email", "Estado"],
                rows=[
                    ["Ana", "ana@example.com", "Activo"],
                    ["Luis", "luis@example.com", "Inactivo"],
                ],
            ),
        ]))

        secs.append(_sec("Modal", "Ventana modal.", [
            Button("Abrir Modal", onclick=lambda: backend.open_modal("demo-modal")),
        ]))

        # ── Overlays ────────────────────────────────────────────────
        secs.append(_sec("Drawer", "Panel lateral.", [
            Button("Abrir Drawer", onclick=lambda: backend.open_drawer("demo-drawer")),
        ]))

        secs.append(_sec("CommandPalette", "Paleta de comandos.", [
            Button("Abrir Cmd", onclick=lambda: backend.open_command_palette()),
        ]))

        # ── Layout Advanced ─────────────────────────────────────────
        secs.append(_sec("SplitPane", "Panel dividido.", [
            SplitPane(left=Text("Izquierda"), right=Text("Derecha")),
        ]))

        # ── Special ────────────────────────────────────────────────
        secs.append(_sec("Wizard", "Asistente multipaso.", [
            Wizard(steps=[
                WizardStep(title="Paso 1", children=[Text("Contenido 1")]),
                WizardStep(title="Paso 2", children=[Text("Contenido 2")]),
            ]),
        ]))

        # ── FX ──────────────────────────────────────────────────────
        secs.append(_sec("FadeIn", "Efecto fade in.", [
            FadeIn(child=Text("Fade In")),
        ]))

        secs.append(_sec("SlideIn", "Efecto slide in.", [
            SlideIn(child=Text("Slide In")),
        ]))

        secs.append(_sec("ScaleIn", "Efecto scale in.", [
            ScaleIn(child=Text("Scale In")),
        ]))

        secs.append(_sec("Pulse", "Efecto pulse.", [
            Pulse(child=Text("Pulse")),
        ]))

        secs.append(_sec("Spin", "Efecto spin.", [
            Spin(child=Text("Spin")),
        ]))

        # ── Hover FX ──────────────────────────────────────────────
        secs.append(_sec("Hover", "Efecto hover básico.", [
            Hover(child=Text("Hover Me")),
        ]))

        secs.append(_sec("HoverLift", "Efecto hover lift.", [
            HoverLift(child=Text("Hover Lift")),
        ]))

        secs.append(_sec("HoverGlow", "Efecto hover glow.", [
            HoverGlow(child=Text("Hover Glow")),
        ]))

        # ── GradientText & Glass ──────────────────────────────────────────
        secs.append(_sec("GradientText & Glass", "Estilos especiales de texto y fondo.", [
            Heading(GradientText.aurora("Título Aurora"), level=1),
            Heading(GradientText.indigo_mint("Índigo Menta"), level=2),
            Heading(GradientText.rose_gold("Rosa Dorado"), level=3),
            Glass(child=Text("Glass Effect"), padding=20),
        ], widget_name="GradientText"))

        # ── MeshBackground ─────────────────────────────────────────────────
        secs.append(_sec("MeshBackground", "Fondo de malla.", [
            MeshBackground(child=Text("Mesh Background")),
        ]))

        # ── Resource CRUD ─────────────────────────────────────────────────
        if not _in_studio_preview():
            secs.append(_sec("ResourceTable", "Tabla de recursos con edición inline.", [
                ResourceTable(
                    api="/api/resources/leads/list",
                    columns=[
                        ResourceTable.Column("id", label="ID", width=60),
                        ResourceTable.Column("nombre", label="Nombre", editable=True),
                        ResourceTable.Column("email", label="Email", editable=True),
                        ResourceTable.Column("estado", label="Estado", editable=True),
                        ResourceTable.Column("plan", label="Plan"),
                    ],
                ),
            ]))

            secs.append(_sec("ResourceStats", "Estadísticas de recursos.", [
                ResourceStats(api="/api/resources/leads/stats"),
            ]))

            secs.append(_sec("ResourceKanban", "Vista Kanban de recursos.", [
                ResourceKanban(
                    api="/api/resources/leads/list",
                    columns=[("Nuevo", "Nuevo"), ("Calificado", "Calificado"), ("Seguimiento", "Seguimiento")],
                ),
            ]))

            secs.append(_sec("ResourceFilters", "Filtros de recursos.", [
                ResourceFilters(api="/api/resources/leads/list"),
            ]))

            secs.append(_sec("ResourceActions", "Acciones masivas.", [
                ResourceActions(api="/api/resources/leads/bulk"),
            ]))

        # ── Demo / Debug ─────────────────────────────────────────────
        if not _in_studio_preview():
            secs.append(_sec("Debug / Demo", "Utilidades de demo.", [
                Button("Toast Info", onclick=lambda: backend.toast("Info toast", variant="info")),
                Button("Toast Success", onclick=lambda: backend.toast("Éxito", variant="success")),
                Button("Toast Error", onclick=lambda: backend.toast("Error", variant="error")),
                Button("Toast Warning", onclick=lambda: backend.toast("Advertencia", variant="warning")),
                Button("Abrir Modal", onclick=lambda: backend.open_modal("demo-modal")),
                Button("Abrir Drawer", onclick=lambda: backend.open_drawer("demo-drawer")),
                Button("Abrir CmdPalette", onclick=lambda: backend.open_command_palette()),
            ]))

        # ═════════════════════════════════════════════════════════════════════
        # Render
        # ═════════════════════════════════════════════════════════════════════
        side_items = [
            (sec.children[0].id, Text(sec.children[0].children[0].children[0].text.upper(), style=TextStyle(size=11, weight="600", color="var(--text-muted)")))
            for sec in secs
        ]

        main_content = Column(
            gap=64,
            padding=48,
            style="max-width:1100px;margin:0 auto",
            children=secs,
        )

        return Row(
            gap=0,
            children=[
                SideMenu(
                    title="Widgets",
                    items=side_items,
                    width=210,
                    sticky=True,
                    top=80,
                    style="max-height:calc(100vh - 100px);overflow-y:auto;flex-shrink:0;margin-right:28px",
                ),
                main_content,
            ],
        ), PageConfig(title="Componentes \\u2014 PROJECT_NAME")
    """
    )
)

