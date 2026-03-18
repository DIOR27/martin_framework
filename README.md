<p align="center">
  <img src="martin/assets/default_icon.webp" width="140" alt="MARTIN logo">
</p>

<h1 align="center">MARTIN Framework</h1>
<p align="center">
<img src="https://img.shields.io/badge/status-pre--alpha-orange">
</p>

<p align="center">
Build beautiful, modern and responsive websites using Python.
</p>

------------------------------------------------------------------------

## Overview

MARTIN is a Python framework for building web interfaces through
**composable UI components**.

Instead of writing HTML and CSS manually, you construct your interface
using Python objects that represent layout structures, visual elements,
and styling primitives.

This approach allows you to focus on **structure, clarity, and design**,
while MARTIN handles the rendering layer.

MARTIN is designed to make web development:

-   **Simple** -- clear, readable Python code\
-   **Fast** -- build interfaces quickly with reusable components\
-   **Modern** -- create visually polished interfaces out of the box\
-   **Responsive** -- layouts adapt naturally to different screens

------------------------------------------------------------------------

## Installation

``` bash
pip install martin-framework
```

For development with enhanced hot-reload support:

``` bash
pip install martin-framework[dev]
```

Run test suite:

``` bash
python -m unittest discover -s tests
```

------------------------------------------------------------------------

## Quick Start

Create a new project:

``` bash
martin new my_project
cd my_project
martin run
```

Your application will be available at:

    http://localhost:3908

------------------------------------------------------------------------

## Example

``` python
from martin import App, Card, Column, Text, Heading, Button
from martin import Border, Padding, Shadow, Colors

def build():
    return Card(
        padding=24,
        radius=16,
        shadow=Shadow.md(),
        children=[
            Heading("Hello MARTIN", level=1, color=Colors.indigo),
            Text("Build modern web interfaces using pure Python", color=Colors.gray_500),
            Button(
                "Get Started",
                background=Colors.indigo,
                color="white",
                radius=8
            ),
        ]
    )

App(
    build=build,
    title="My MARTIN App"
).run()
```

------------------------------------------------------------------------

## Command Line Interface

  Command                                Description
  -------------------------------------- -----------------------------------------
  `martin new <name>`                    Create a new project
  `martin run`                           Start development server
  `martin run --port 8080`               Run server on custom port
  `martin run --no-reload`               Disable hot reload
  `martin export`                        Export static site to `dist/index.html`
  `martin export --out web/index.html`   Export to custom path
  `martin export --with-backend`         Export frontend + Python backend runtime
  `martin version`                       Show installed version

------------------------------------------------------------------------

## Philosophy

MARTIN focuses on a few core principles:

**Readable code**\
Interfaces should be understandable at a glance.

**Composable UI**\
Complex layouts are built from small reusable components.

**Design-first approach**\
Modern visual elements like cards, grids, shadows, gradients, and
responsive layouts are first-class features.

**Python-native**\
No template languages. No mixing multiple syntaxes. Just Python.

------------------------------------------------------------------------

## Built-in Components

MARTIN ships with a growing set of UI primitives:

-   Layout: `Row`, `Column`, `Grid`, `Stack`, `Spacer`
-   Containers: `Container`, `Card`
-   Typography: `Heading`, `Text`, `Paragraph`
-   Media: `Image`, `Video`, `Icon`, `IconPack`
-   Forms: `TextField`, `Checkbox`, `Select`, `MultiSelect`
-   UI Elements: `Button`, `Badge`, `Avatar`, `Divider`
-   Data Visuals: `WordCloud`, `Map`, `Timeline`
-   Utility: `Raw`, `Script`, `Stylesheet`, `StyleTag`, `ThemeToggle`

------------------------------------------------------------------------

## Styling System

MARTIN includes a lightweight styling system designed to keep UI
definitions concise.

Examples:

-   `Padding`
-   `Margin`
-   `Border`
-   `Shadow`
-   `Background`
-   `TextStyle`
-   `GradientText`
-   `MeshBackground`

And a built-in color palette via:

``` python
Colors.indigo
Colors.gray_500
```

All widgets also support universal HTML attributes from Python:

``` python
Row(
    children=[...],
    role="group",
    tabindex=0,
    aria_label="Barra de acciones",
    data_testid="actions-row",
)
```

Several interactive widgets also generate sensible a11y defaults automatically
(`aria-label`) when possible, while still allowing explicit overrides.
This includes controls like `Select`, `MultiSelect`, `ColorPicker`, and `DatePicker`.

MARTIN also ships with a built-in motion library under `martin.fx`:

``` python
from martin import App, Card, Text
from martin.fx import (
    SlideIn, HoverLift, RevealOnScroll,
    Transition, Stagger, ReducedMotion,
)

def build():
    return Card(
        padding=24,
        radius=18,
        style=[
            RevealOnScroll(direction="up", distance=24),
            SlideIn(direction="up", distance=32, delay=0.1),
            Transition("transform", duration=0.25, timing="ease-out"),
            HoverLift(distance=8),
            ReducedMotion.all(),
        ],
        children=[
            Text("Motion comes bundled with martin-framework"),
            Text("You can also import from martin_fx if you prefer."),
        ],
    )
```

Included presets:

- `FadeIn`
- `SlideIn`
- `ScaleIn`
- `BlurIn`
- `RotateIn`
- `Float`
- `Pulse`
- `Spin`
- `Transition`
- `HoverLift`
- `HoverGlow`
- `Stagger`
- `RevealOnScroll`
- `ReducedMotion`

Composition example:

``` python
from martin import Card
from martin.fx import RevealOnScroll, Stagger, HoverGlow, Transition

cards = [
    Card(
        f"Feature {i+1}",
        style=[
            RevealOnScroll(delay=Stagger.delay(i, step=0.08)),
            Transition("transform", duration=0.24).hover(
                "translateY(-4px)",
                shadow="0 14px 28px rgba(15,23,42,0.14)",
            ),
            HoverGlow("#22c55e"),
        ],
    )
    for i in range(4)
]
```

`Table` also supports built-in client-side export utilities from Python:

``` python
from martin import Table

Table(
    headers=["Nombre", "Ciudad", "Rol"],
    rows=[
        ["Ana Garcia", "Bogota", "Admin"],
        ["Pedro Lopez", "Medellin", "Editor"],
    ],
    searchable=True,
    sortable=True,
    page_size=10,
    export_formats=["csv", "json", "excel", "pdf"],  # or True for all
    export_filename="usuarios",
    export_scope="filtered",  # "filtered" or "page"
)
```

For richer PDF exports you can optionally include `jsPDF` with `Script(...)`.

------------------------------------------------------------------------

## Simple Backend

API helpers are now separated from the core UI package.
If you want a small backend for forms, fetch actions, or JSON endpoints,
use `martin.backend`.

``` python
from martin import App, Button, Column
from martin.backend import Backend, ApiCall, ResultBox

backend = Backend(prefix="/api")

@backend.post("/hello")
def hello(req):
    data = req.json(default={}) or {}
    return {"message": f"Hola {data.get('name', 'Martin')}"}

app = App(
    build=lambda: Column(children=[
        Button("Enviar", on_click=ApiCall("/api/hello", body={"name": "Diego"}, target="result")),
        ResultBox(id="result", format="message"),
    ])
)

backend.mount(app)
```

This keeps `martin` focused on UI while `martin.backend` handles
simple HTTP and request/response helpers.

You can also send emails through SMTP:

``` python
from martin.backend import Backend

backend = Backend(prefix="/api")
backend.configure_smtp(
    host="smtp.gmail.com",
    port=587,
    username="tu_usuario",
    password="tu_password_o_app_password",
    sender="tu_correo@gmail.com",
    sender_name="Mi App",
    use_tls=True,
)

backend.send_mail(
    subject="Nuevo mensaje",
    to="destino@correo.com",
    text="Hola desde Martin",
    html="<b>Hola</b> desde Martin",
)
```

Tambien puedes construir el mailer manualmente con `SMTPConfig` y `Mailer`
si prefieres una configuracion mas explicita.

Para exportarlo junto al frontend:

``` bash
martin export --with-backend
cd dist
python server.py --port 3908
```

Eso genera un export hibrido con:
- frontend estatico
- `server.py`
- `_backend_src/` con snapshot del proyecto
- `route-map.json`
- `.env.example` para SMTP

------------------------------------------------------------------------

## Icon Libraries

You can load popular icon libraries from Python and use them with `Icon`.
This also works with arbitrary CSS icon libraries, as long as the library
exposes class-based icons.

``` python
from martin import Row, IconPack, Icon

Row(
    children=[
        IconPack(["fontawesome", "bootstrap-icons", "material-symbols"]),
        Icon(name="house", provider="fa", variant="solid", size=18),
        Icon(name="airplane", provider="bi", size=18),
        Icon(name="flight_takeoff", provider="material-symbols", variant="rounded", size=20),
    ],
    gap=10,
)
```

You can also pass direct icon classes:

``` python
Icon(name="fa-solid fa-user")
Icon(icon_class="mdi mdi-calendar")
```

For custom class-based libraries, you can load the stylesheet URL directly:

``` python
from martin import IconPack, Icon

IconPack("https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.css")
Icon(name="home-line", provider="ri")
Icon(icon_class="ri ri-rocket-line")
```

Supported built-in providers: `fa`/`fontawesome`, `bi`/`bootstrap-icons`,
`mdi`, `material-icons`, `material-symbols`.

------------------------------------------------------------------------

## Exporting Static Sites

MARTIN can generate static HTML output for deployment.

``` bash
martin export
```

This will produce:

    dist/index.html

You can deploy the generated output to any static hosting service.

------------------------------------------------------------------------

## Project Status

MARTIN is currently in **early development**.

The goal is to evolve into a powerful yet minimal framework for building
modern web interfaces using Python.

Contributions, feedback, and experimentation are welcome.

------------------------------------------------------------------------

## Changelog

Release history and migration notes are tracked in:

`CHANGELOG.md`

------------------------------------------------------------------------

## License

MIT License
