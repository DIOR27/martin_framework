"""
MARTIN — Build webs with Python, Flutter-style.

Usage:
    from martin import App, Card, Row, Column, Text, Image, Button
    from martin import Border, Padding, Shadow, TextStyle, CSS, Colors
"""

from martin.app import App
from martin.styles import (
    CSS,
    StyleBase,
    resolve_styles,
    Border,
    Padding,
    Margin,
    Shadow,
    Size,
    Background,
    TextStyle,
    Opacity,
    Overflow,
    Cursor,
    Colors,
)
from martin.widgets import (
    # Layout
    Container,
    Row,
    Column,
    Card,
    Stack,
    Grid,
    Spacer,
    Divider,
    # Text
    Text,
    Heading,
    Paragraph,
    Link,
    Code,
    # Media
    Image,
    Video,
    Icon,
    # Input
    Button,
    TextField,
    Checkbox,
    Select,
    # Utility
    Badge,
    Avatar,
    Raw,
)

__all__ = [
    "App",
    # Styles
    "CSS",
    "StyleBase",
    "resolve_styles",
    "Border",
    "Padding",
    "Margin",
    "Shadow",
    "Size",
    "Background",
    "TextStyle",
    "Opacity",
    "Overflow",
    "Cursor",
    "Colors",
    # Widgets
    "Container",
    "Row",
    "Column",
    "Card",
    "Stack",
    "Grid",
    "Spacer",
    "Divider",
    "Text",
    "Heading",
    "Paragraph",
    "Link",
    "Code",
    "Image",
    "Video",
    "Icon",
    "Button",
    "TextField",
    "Checkbox",
    "Select",
    "Badge",
    "Avatar",
    "Raw",
]
