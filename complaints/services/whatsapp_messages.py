from complaints.models import ComplaintCategory


def send_complaint_categories(phone_number):
    categories = ComplaintCategory.objects.filter(
        is_active=True
    ).order_by("name")

    rows = [
        {
            "id": f"complaint_{category.id}",
            "title": category.name[:24],
            "description": category.description or ""
        }
        for category in categories
    ]

    if not rows:
        return False

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": "Please select your complaint reason."
            },
            "action": {
                "button": "Show Reasons",
                "sections": [
                    {
                        "title": "Complaint Categories",
                        "rows": rows
                    }
                ]
            }
        }
    }

    # Send payload using your existing WhatsApp Cloud API service