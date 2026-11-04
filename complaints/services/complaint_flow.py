
from complaints.models import ComplaintCategory
from whatsapp.services.cloud_api import send_interactive_list


def show_complaint_categories(phone_number):

    categories = list(
        ComplaintCategory.objects.filter(
            is_active=True
        ).order_by("name")
    )

    if not categories:
        return None

    rows = [
        {
            "id": f"complaint_{category.id}",
            "title": category.name[:24],
            "description": (category.description or "")[:72]
        }
        for category in categories
    ]

    sections = []

    # WhatsApp allows maximum 10 rows per section
    for start in range(0, len(rows), 10):
        sections.append({
            "title": f"Categories {start + 1}",
            "rows": rows[start:start + 10]
        })

    return send_interactive_list(
        to=phone_number,
        body_text="Please select your complaint reason.",
        button_text="Show Reasons",
        section_title="Complaint Categories",
        rows=rows
    )
