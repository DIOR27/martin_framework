"""Contact model definition."""

from martin.orm import Model, Char, Text, Boolean, Selection


class Contact(Model):
    """A contact / lead record."""

    _name = "contact"
    _description = "Contact"

    _fields = {
        "name": Char(required=True, label="Name"),
        "email": Char(label="Email"),
        "phone": Char(label="Phone"),
        "company": Char(label="Company"),
        "position": Char(label="Position"),
        "notes": Text(label="Notes"),
        "active": Boolean(default=True, label="Active"),
        "status": Selection(
            selection=[
                ("new", "New"),
                ("qualified", "Qualified"),
                ("followup", "Follow-up"),
                ("converted", "Converted"),
                ("lost", "Lost"),
            ],
            default="new",
            label="Status",
        ),
    }
