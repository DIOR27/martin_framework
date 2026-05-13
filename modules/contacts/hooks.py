"""Contacts module - hooks.

Demonstrates extending other modules' widgets via the hook/slot system.
This module extends its own ResourceForm with extra fields.
"""

from martin.module import extend
from martin.widgets import Select, Badge


@extend("ResourceForm.form_fields", module="contacts", priority=30)
def contact_priority_field(context):
    """Add a priority field to contact forms."""
    return Badge("CRM Module Active", variant="info")


@extend("ResourceForm.header_buttons", module="contacts", priority=10)
def contact_header_buttons(context):
    """Add extra header info."""
    return '<div style="font-size:12px;color:var(--text-muted);margin-bottom:8px">Extended by CRM</div>'
