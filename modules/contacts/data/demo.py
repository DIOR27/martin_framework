"""Demo data for contacts module."""
from martin.orm import get_backend

DATA = [
    {"name": "Ana García", "email": "ana@empresa.com", "phone": "+34 612 345 678",
     "company": "Empresa Tech", "position": "CEO", "status": "qualified", "active": True},
    {"name": "Carlos López", "email": "carlos@startup.io", "phone": "+52 55 1234 5678",
     "company": "Startup.io", "position": "CTO", "status": "new", "active": True},
    {"name": "María Rodríguez", "email": "maria@corp.com", "phone": "+1 555 010 203",
     "company": "Global Corp", "position": "VP Sales", "status": "followup", "active": True},
    {"name": "John Smith", "email": "john@example.com", "phone": "+44 20 7123 4567",
     "company": "Example Ltd", "position": "Product Manager", "status": "converted", "active": False},
    {"name": "Laura Martínez", "email": "laura@agency.co", "phone": "+57 300 123 4567",
     "company": "Agency Co", "position": "Designer", "status": "new", "active": True},
]


def load_demo_data():
    """Load demo contacts if table is empty."""
    backend = get_backend()
    cur = backend.execute("SELECT COUNT(*) as cnt FROM contact")
    row = cur.fetchone()
    if row and row[0] == 0:
        from modules.contacts.models.contact import Contact
        for entry in DATA:
            Contact.create(entry)
        print(f"  contacts: {len(DATA)} demo records loaded")
