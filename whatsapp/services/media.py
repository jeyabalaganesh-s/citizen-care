
import requests

from django.conf import settings


def download_whatsapp_media(media_id):
    """
    Download an image from WhatsApp Cloud API.
    Returns the downloaded image bytes and MIME type.
    """

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"
    }

    # Step 1: Get temporary media URL
    media_url = (
        f"https://graph.facebook.com/"
        f"{settings.WHATSAPP_API_VERSION}/"
        f"{media_id}"
    )

    response = requests.get(
        media_url,
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()

    media_data = response.json()

    download_url = media_data.get("url")
    mime_type = media_data.get("mime_type", "")

    if not download_url:
        raise ValueError("WhatsApp media URL not found.")

    if not mime_type.startswith("image/"):
        raise ValueError("Unsupported media type.")

    # Step 2: Download actual image
    image_response = requests.get(
        download_url,
        headers=headers,
        timeout=30,
    )

    image_response.raise_for_status()

    return image_response.content, mime_type
