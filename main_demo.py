"""
Martin Demo — Contacts ERP Module

Run with:
    python main_demo.py
"""

from pathlib import Path

from martin import App, Router, Container, Heading, Paragraph, Button, Row

# ── Router ──────────────────────────────────────────────────────────────
router = Router()


@router.page("/", title="Dashboard")
def home():
    return Container(
        padding=32,
        children=[
            Heading("Martin ERP Demo", level=1),
            Paragraph("Contacts module loaded. Backend auto-registered."),
            Row(gap=12, wrap=True, children=[
                Button("Contacts List", href="/contacts", variant="primary"),
                Button("New Contact", href="/contacts/new", variant="secondary"),
                Button("Contact Details", href="/contacts/1", variant="ghost"),
            ]),
        ],
    )


@router.page("/contacts", title="Contacts")
def contacts():
    from modules.contacts.views import contact_list
    return contact_list()


@router.page("/contacts/new", title="New Contact")
def contact_new():
    from modules.contacts.views import contact_form
    return contact_form()


@router.page("/contacts/detail", title="Contact Detail")
def contact_detail():
    from modules.contacts.views import contact_details
    return contact_details()


@router.page("/dashboard", title="Dashboard CRM")
def dashboard():
    from modules.contacts.views import contact_dashboard
    return contact_dashboard()


# ── App ─────────────────────────────────────────────────────────────────
app = App(
    router=router,
    title="Martin ERP",
    theme="auto",
    theme_toggle=True,
    description="Modular ERP built with Martin Framework",
    lang="en",
)


# ── Backend + ORM Bridge ────────────────────────────────────────────────
from martin.backend import Backend
from martin.orm import auto_register_all, ModelRegistry, get_backend, create_all_tables

backend = Backend(prefix="/api")

# 1. Create DB tables for all registered models
create_all_tables()

# 2. Auto-register REST endpoints
auto_register_all(backend)

# 3. Mount backend on app
backend.mount(app)

# 4. Load demo data
try:
    from modules.contacts.data.demo import load_demo_data
    load_demo_data()
except ImportError:
    pass


# ── Entry ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    open_browser = "--open" in sys.argv
    app.run(open_browser=open_browser)
