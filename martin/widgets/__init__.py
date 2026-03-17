"""
Martin — Widgets package

Public widget exports grouped by category modules.
"""

from .layout import Container, Row, Column, Grid, Stack, Card, Section, Spacer, Divider
from .text import Text, Heading, Paragraph, Link, Code
from .media import Image, Video, Icon, Avatar
from .input import (
    Button,
    TextField,
    TextArea,
    Checkbox,
    Select,
    MultiSelect,
    Slider,
    ColorPicker,
    DatePicker,
    RadioGroup,
    NumberInput,
    TimePicker,
    ProgressBar,
    Rating,
    FileInput,
    FormGroup,
)
from .feedback import Badge, Alert
from .navigation import NavBar, SideMenu, Footer, Breadcrumb, Tabs
from .data import Table
from .overlay import Modal
from .special import (
    Raw,
    Script,
    Stylesheet,
    StyleTag,
    ThemeToggle,
    CookieCategory,
    CookieBanner,
    SafeArea,
)
from .api import Ref, ApiCall, ResultBox
from .dataviz import WordCloud, Map, Timeline, TimelineItem, Chart, ChartDataset
from .marketing import (
    Hero,
    Gallery,
    GalleryItem,
    Carousel,
    CarouselItem,
    Accordion,
    AccordionItem,
    Testimonials,
    TestimonialItem,
    SlideCarousel,
    SlideItem,
    Pricing,
    PricingPlan,
    FAQ,
    FAQItem,
)
from .calendar import Calendar, CalendarEvent

__all__ = [
    # Layout
    "Container",
    "Row",
    "Column",
    "Grid",
    "Stack",
    "Card",
    "Section",
    "Spacer",
    "Divider",
    # Text
    "Text",
    "Heading",
    "Paragraph",
    "Link",
    "Code",
    # Media
    "Image",
    "Video",
    "Icon",
    "Avatar",
    # Interaction
    "Button",
    "TextField",
    "TextArea",
    "Checkbox",
    "Select",
    "MultiSelect",
    "Slider",
    "ColorPicker",
    "DatePicker",
    "RadioGroup",
    "NumberInput",
    "TimePicker",
    "ProgressBar",
    "Rating",
    "FileInput",
    "FormGroup",
    # Feedback
    "Badge",
    "Alert",
    # Navigation
    "NavBar",
    "SideMenu",
    "Footer",
    "Breadcrumb",
    "Tabs",
    # Data
    "Table",
    # Overlay
    "Modal",
    # Utility / special
    "Raw",
    "Script",
    "Stylesheet",
    "StyleTag",
    "ThemeToggle",
    "CookieBanner",
    "CookieCategory",
    "SafeArea",
    # API
    "Ref",
    "ApiCall",
    "ResultBox",
    # Compound
    "WordCloud",
    "Map",
    "Timeline",
    "TimelineItem",
    "Hero",
    "Gallery",
    "GalleryItem",
    "Carousel",
    "CarouselItem",
    "Accordion",
    "AccordionItem",
    "Testimonials",
    "TestimonialItem",
    "SlideCarousel",
    "SlideItem",
    "Pricing",
    "PricingPlan",
    "FAQ",
    "FAQItem",
    "Chart",
    "ChartDataset",
    "Calendar",
    "CalendarEvent",
]
