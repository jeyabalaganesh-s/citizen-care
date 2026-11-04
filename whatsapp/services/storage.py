
import cloudinary.uploader


def save_complaint_evidence(image_bytes, mime_type):
    """
    Upload complaint evidence to Cloudinary.
    """

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if mime_type not in allowed_types:
        raise ValueError("Unsupported image format.")

    if len(image_bytes) > 5 * 1024 * 1024:
        raise ValueError("Image exceeds 5 MB limit.")

    result = cloudinary.uploader.upload(
        image_bytes,
        resource_type="image",
        folder="citizen_care/complaint_evidence",
    )

    return {
        "public_id": result["public_id"],
        "secure_url": result["secure_url"],
        "format": result["format"],
        "bytes": result["bytes"],
    }
