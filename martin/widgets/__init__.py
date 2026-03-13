"""
Martin — Widgets package

Public widget exports grouped by category modules.
"""

from .layout import Container, Row, Column, Grid, Stack, Card, Section, Spacer, Divider
from .text import Text, Heading, Paragraph, Link, Code
from .media import Image, Video, Icon, Avatar
from .input import Button, TextField, TextArea, Checkbox, Select, MultiSelect
from .feedback import Badge, Alert
from .navigation import NavBar, Footer, Breadcrumb, Tabs
from .data import Table
from .overlay import Modal
from .special import Raw, ThemeToggle, CookieCategory, CookieBanner
from .compound import (
    Ref,
    ApiCall,
    ResultBox,
    WordCloud,
    Map,
    Timeline,
    TimelineItem,
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
    Chart,
    ChartDataset,
    Calendar,
    CalendarEvent,
)

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
    # Feedback
    "Badge",
    "Alert",
    # Navigation
    "NavBar",
    "Footer",
    "Breadcrumb",
    "Tabs",
    # Data
    "Table",
    # Overlay
    "Modal",
    # Utility / special
    "Raw",
    "ThemeToggle",
    "CookieBanner",
    "CookieCategory",
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
