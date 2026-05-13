"""Contact views using Resource* widgets."""

from martin import ResourceTable, ResourceForm, ResourceDetails, ResourceView, Column, Heading, Container


def contact_list():
    """Contact list page."""
    return Column(
        gap=16,
        padding=24,
        children=[
            Heading("Contacts", level=1),
            ResourceTable(
                resource="contact",
                columns=[
                    {"key": "name", "label": "Name", "width": 200},
                    {"key": "email", "label": "Email"},
                    {"key": "phone", "label": "Phone"},
                    {"key": "company", "label": "Company"},
                    {"key": "status", "label": "Status", "width": 120},
                    {"key": "active", "label": "Active", "width": 80},
                ],
                searchable=True,
                page_size=25,
            ),
        ],
    )


def contact_form():
    """New contact form page."""
    return Column(
        gap=16,
        padding=24,
        children=[
            Heading("New Contact", level=1),
            ResourceForm(
                resource="contact",
                fields=[
                    {"name": "name", "label": "Name", "type": "text", "required": True},
                    {"name": "email", "label": "Email", "type": "email"},
                    {"name": "phone", "label": "Phone", "type": "text"},
                    {"name": "company", "label": "Company", "type": "text"},
                    {"name": "position", "label": "Position", "type": "text"},
                    {"name": "status", "label": "Status", "type": "select",
                     "options": [["new", "New"], ["qualified", "Qualified"],
                                 ["followup", "Follow-up"], ["converted", "Converted"],
                                 ["lost", "Lost"]]},
                    {"name": "notes", "label": "Notes", "type": "textarea"},
                ],
                title="Contact Information",
                helper_text="Fill in the contact details below.",
                submit_label="Save Contact",
            ),
        ],
    )


def contact_details():
    """Contact detail view."""
    return Column(
        gap=16,
        padding=24,
        children=[
            Heading("Contact Details", level=1),
            ResourceDetails(
                resource="contact",
                title="Contact Info",
                fields=[
                    {"name": "name", "label": "Name"},
                    {"name": "email", "label": "Email"},
                    {"name": "phone", "label": "Phone"},
                    {"name": "company", "label": "Company"},
                    {"name": "status", "label": "Status"},
                    {"name": "active", "label": "Active"},
                    {"name": "notes", "label": "Notes"},
                ],
            ),
        ],
    )


def contact_dashboard():
    """Full resource view: stats + filters + table."""
    return Container(
        padding=24,
        children=[
            Heading("Contacts Dashboard", level=1),
            ResourceView(
                resource="contact",
                title="All Contacts",
                show_stats=True,
                show_toolbar=True,
                show_table=True,
                show_paginator=True,
                columns=[
                    {"key": "name", "label": "Name"},
                    {"key": "email", "label": "Email"},
                    {"key": "status", "label": "Status"},
                ],
                form_fields=[
                    {"name": "name", "label": "Name", "type": "text", "required": True},
                    {"name": "email", "label": "Email", "type": "email"},
                ],
                filters=[
                    {"name": "status", "label": "Status", "type": "select",
                     "options": [["new", "New"], ["qualified", "Qualified"], ["followup", "Follow-up"]]},
                ],
                actions=[
                    {"label": "Refresh", "variant": "secondary",
                     "on_click": "window['contact_table_refresh']&&window['contact_table_refresh']()"},
                ],
                toolbar_actions=[
                    {"label": "Quick Add", "variant": "ghost",
                     "on_click": "console.log('quick add')"},
                ],
                stats_metrics=[
                    {"key": "total", "label": "Total"},
                    {"key": "active", "label": "Active"},
                ],
                helper_text="Manage your contacts from this dashboard.",
            ),
        ],
    )
