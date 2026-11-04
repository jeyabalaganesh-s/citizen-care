
from django.db import transaction

from complaints.models import Complaint, ComplaintEvidence


@transaction.atomic
def register_whatsapp_complaint(
    citizen_name,
    citizen_phone,
    category,
    description,
    whatsapp_message_id,
    image_url,
    cloudinary_public_id,
    validation_status,
    validation_reason,
):
    """
    Register a complaint only when its evidence
    has passed AI validation.
    """

    # 1. Validate evidence status
    if validation_status != "valid":
        raise ValueError(
            "Complaint cannot be registered without valid evidence."
        )

    if not image_url or not cloudinary_public_id:
        raise ValueError(
            "Complaint evidence is missing."
        )

    if not description.strip():
        raise ValueError(
            "Complaint description is required."
        )

    # 2. Prevent duplicate registration
    existing_complaint = Complaint.objects.filter(
        whatsapp_message_id=whatsapp_message_id
    ).first()

    if existing_complaint:
        return existing_complaint, False

    # 3. Create complaint
    complaint = Complaint.objects.create(
        citizen_name=citizen_name,
        citizen_phone=citizen_phone,
        category=category,
        description=description,
        status="received",
        priority="medium",
        source="whatsapp",
        whatsapp_message_id=whatsapp_message_id,
    )

    # 4. Save Cloudinary evidence
    ComplaintEvidence.objects.create(
        complaint=complaint,
        cloudinary_url=image_url,
        cloudinary_public_id=cloudinary_public_id,
        description=description,
        validation_status=validation_status,
        validation_reason=validation_reason,
    )

    return complaint, True
