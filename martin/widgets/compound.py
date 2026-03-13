"""
Martin — Compound Widgets (Compatibility Shim)

This module is kept for backward compatibility.
Import from dedicated modules for new development:
    - martin.widgets.api
    - martin.widgets.dataviz
    - martin.widgets.marketing
    - martin.widgets.calendar
"""

from .api import Ref, ApiCall, ResultBox
from .dataviz import WordCloud, Map, Timeline, TimelineItem, ChartDataset, Chart
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
    'Ref', 'ApiCall', 'ResultBox',
    'WordCloud', 'Map', 'Timeline', 'TimelineItem',
    'Hero', 'Gallery', 'GalleryItem', 'Carousel', 'CarouselItem',
    'Accordion', 'AccordionItem', 'Testimonials', 'TestimonialItem',
    'SlideCarousel', 'SlideItem', 'Pricing', 'PricingPlan', 'FAQ', 'FAQItem',
    'Chart', 'ChartDataset', 'Calendar', 'CalendarEvent',
]
