# Martin

Build webs with Python, Flutter-style.

## Instalación

```bash
pip install martin
# Con hot reload mejorado:
pip install martin[dev]
```

## Uso rápido

```bash
martin new mi_proyecto
cd mi_proyecto
martin run
```

## CLI

| Comando                              | Descripción                      |
| ------------------------------------ | -------------------------------- |
| `martin new <nombre>`                | Crea un nuevo proyecto           |
| `martin run`                         | Inicia servidor en localhost:309 |
| `martin run --port 8080`             | Puerto personalizado             |
| `martin run --no-reload`             | Sin hot reload                   |
| `martin export`                      | Exporta a `dist/index.html`      |
| `martin export --out web/index.html` | Exporta a ruta personalizada     |
| `martin version`                     | Muestra la versión               |

## Ejemplo

```python
from martin import App, Card, Column, Text, Heading, Button
from martin import Border, Padding, Shadow, Colors

def build():
    return Card(
        padding=24,
        radius=16,
        shadow=Shadow.md(),
        children=[
            Heading("Hola Martin", level=1, color=Colors.indigo),
            Text("Build webs con Python puro", color=Colors.gray_500),
            Button("Empezar", background=Colors.indigo, color="white", radius=8),
        ]
    )

App(build=build, title="Mi App").run()
```
