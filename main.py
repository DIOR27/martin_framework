from turtle import color

from click import style

from martin import App, Card, Column, Text, Heading, Image
from martin import Border, Padding, Shadow, TextStyle, Colors
from martin.styles import CSS, Background
from martin.widgets import Button, Container


def build():
    return Container(
        style=Background(Colors.black),
        children=[
            Card(
                style=[Padding(24), Border(radius=12), Shadow.md()],
                children=[
                    Image("assets/logo.png", style=Border(radius=8)),
                    Heading("Hola mundo!", level=1),
                    Text("Bienvenido", style=TextStyle(color=Colors.gray_500)),
                ],
            ),
            Card(
                style=[Padding(16), Border(radius=12), Shadow.md()],
                children=[
                    Image(
                        "foto.jpg", style=[Border(radius=8), CSS("object-fit:cover")]
                    ),
                    Text("Hola mundos", style=TextStyle(size=16, weight="bold")),
                    Button(
                        "Guardar",
                        style=[
                            CSS("background: #e11d48; border: none; color: white"),
                            Border(radius=12),
                            Padding(h=24, v=12),
                        ],
                    ),
                ],
            ),
        ],
    )


App(build=build, title="Mi App").run()
