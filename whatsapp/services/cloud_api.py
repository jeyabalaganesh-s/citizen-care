import requests
from django.conf import settings


def send_text_message(to, message):

    phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
    access_token = settings.WHATSAPP_ACCESS_TOKEN
    api_version = settings.WHATSAPP_API_VERSION

    if not phone_number_id or not access_token:
        raise ValueError("WhatsApp credentials are missing.")

    url = (
        f"https://graph.facebook.com/"
        f"{api_version}/{phone_number_id}/messages"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message,
        },
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=20,
    )

    response.raise_for_status()

    return response.json()