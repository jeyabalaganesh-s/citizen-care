
import logging

from whatsapp.services.media import download_whatsapp_media
from whatsapp.services.storage import save_complaint_evidence

logger = logging.getLogger(__name__)


def process_whatsapp_image(media_id):
    """
    Download an image from WhatsApp and upload it
    directly to Cloudinary.
    """

    # 1. Download image from WhatsApp
    image_bytes, mime_type = download_whatsapp_media(
        media_id
    )

    # 2. Upload image to Cloudinary
    cloudinary_result = save_complaint_evidence(
        image_bytes=image_bytes,
        mime_type=mime_type,
    )

    # 3. Return image information
    return {
        "media_id": media_id,
        "image_url": cloudinary_result["secure_url"],
        "public_id": cloudinary_result["public_id"],
        "mime_type": mime_type,
        "format": cloudinary_result["format"],
    }
