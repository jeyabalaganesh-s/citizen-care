
import logging
from datetime import datetime, timezone as dt_timezone

from django.db import transaction
from django.utils import timezone

from whatsapp.models import (
    WhatsAppContact,
    WhatsAppConversation,
    WhatsAppMessage,
)

from whatsapp.services.cloud_api import send_text_message
from whatsapp.services.image_processor import process_whatsapp_image
from ai_assistant.services import generate_ai_response
from ai_assistant.image_validation import validate_complaint_image
from complaints.services import register_whatsapp_complaint


logger = logging.getLogger(__name__)


def get_conversation_history(conversation, current_message):
    previous_messages = (
        conversation.messages
        .filter(message_type="text")
        .exclude(id=current_message.id)
        .order_by("-created_at")[:10]
    )

    history = []

    for message in reversed(list(previous_messages)):
        role = "user" if message.direction == "incoming" else "assistant"

        history.append({
            "role": role,
            "content": message.text,
        })

    return history


def get_complaint_description(conversation, image_message):
    ignored_messages = [
        "hi", "hello", "hey", "ok", "okay",
        "thanks", "thank you",
    ]

    previous_text = (
        conversation.messages
        .filter(
            direction="incoming",
            message_type="text",
            created_at__lt=image_message.created_at,
        )
        .exclude(text="")
        .order_by("-created_at")
    )

    for message in previous_text:
        description = message.text.strip()

        if description.lower() not in ignored_messages:
            return description

    return ""


def get_complaint_category(description):
    text = description.lower()

    category_keywords = {
        "cleanliness": [
            "clean", "dust", "garbage", "waste",
            "dirty", "sanitation", "dustbin",
        ],
        "furniture": [
            "chair", "table", "desk", "sofa",
            "furniture", "cupboard",
        ],
        "electrical": [
            "electric", "light", "switch", "wiring",
            "fan", "power", "socket",
        ],
        "plumbing": [
            "water", "tap", "pipe", "leak",
            "toilet", "drain", "washbasin",
        ],
        "equipment": [
            "computer", "printer", "laptop",
            "projector", "equipment",
        ],
        "safety": [
            "safety", "danger", "fire", "hazard",
            "emergency",
        ],
        "maintenance": [
            "repair", "broken", "damage",
            "maintenance",
        ],
    }

    for category, keywords in category_keywords.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "other"


def send_and_save_reply(conversation, wa_id, reply):
    response = send_text_message(
        to=wa_id,
        message=reply,
    )

    messages = response.get("messages", [])
    outgoing_message_id = messages[0].get("id") if messages else None

    if outgoing_message_id:
        WhatsAppMessage.objects.get_or_create(
            message_id=outgoing_message_id,
            defaults={
                "conversation": conversation,
                "direction": "outgoing",
                "message_type": "text",
                "text": reply,
                "status": "sent",
                "raw_payload": response,
                "timestamp": timezone.now(),
            },
        )

    conversation.last_message_at = timezone.now()
    conversation.save(
        update_fields=["last_message_at", "updated_at"]
    )


def register_confirmed_complaint(conversation, incoming_message, wa_id):
    if conversation.complaint_step != "awaiting_confirmation":
        send_and_save_reply(
            conversation,
            wa_id,
            "There is no complaint currently waiting for confirmation.",
        )
        return

    if (
        conversation.evidence_validation_status != "valid"
        or not conversation.evidence_url
        or not conversation.evidence_public_id
    ):
        send_and_save_reply(
            conversation,
            wa_id,
            "The complaint evidence has not been validated. Please upload the photo again.",
        )
        return

    try:
        with transaction.atomic():
            complaint, created = register_whatsapp_complaint(
                citizen_name=conversation.contact.name or "WhatsApp Citizen",
                citizen_phone=conversation.contact.wa_id,
                category=conversation.complaint_category or "other",
                description=conversation.complaint_description,
                whatsapp_message_id=incoming_message.message_id,
                image_url=conversation.evidence_url,
                cloudinary_public_id=conversation.evidence_public_id,
                validation_status=conversation.evidence_validation_status,
                validation_reason=conversation.evidence_validation_reason,
            )

            conversation.registered_complaint = complaint
            conversation.complaint_step = "registered"
            conversation.status = "completed"
            conversation.save(
                update_fields=[
                    "registered_complaint",
                    "complaint_step",
                    "status",
                    "updated_at",
                ]
            )

        if created:
            reply = (
                "Your complaint has been successfully registered!\n\n"
                f"Complaint ID: {complaint.complaint_id}\n"
                "Our team will review your complaint."
            )
        else:
            reply = (
                "This complaint has already been registered.\n\n"
                f"Complaint ID: {complaint.complaint_id}"
            )

        send_and_save_reply(conversation, wa_id, reply)

    except Exception:
        logger.exception("Complaint registration failed for %s", wa_id)
        send_and_save_reply(
            conversation,
            wa_id,
            "We couldn't register your complaint right now. Please try again later.",
        )


def send_ai_reply(conversation, incoming_message, wa_id):
    if not incoming_message.text.strip():
        return

    text = incoming_message.text.strip()
    normalized_text = text.lower().strip(" .,!")

    # Handle explicit confirmation.
    if conversation.complaint_step == "awaiting_confirmation":
        if normalized_text in {"yes", "yes please", "confirm", "confirm complaint"}:
            register_confirmed_complaint(
                conversation,
                incoming_message,
                wa_id,
            )
            return

        if normalized_text in {"no", "no thanks", "cancel"}:
            conversation.complaint_step = "awaiting_problem"
            conversation.complaint_description = ""
            conversation.complaint_category = ""
            conversation.evidence_url = ""
            conversation.evidence_public_id = ""
            conversation.evidence_validation_status = ""
            conversation.evidence_validation_reason = ""
            conversation.last_evidence_message_id = ""
            conversation.save()

            send_and_save_reply(
                conversation,
                wa_id,
                "No problem. The pending complaint has been cancelled. Please describe your office problem if you want to report another issue.",
            )
            return

        send_and_save_reply(
            conversation,
            wa_id,
            "Please reply Yes to register this complaint or No to cancel it.",
        )
        return

    try:
        history = get_conversation_history(
            conversation,
            incoming_message,
        )

        ai_reply = generate_ai_response(
            user_message=text,
            conversation_history=history,
        )

        if ai_reply:
            send_and_save_reply(conversation, wa_id, ai_reply)

    except Exception:
        logger.exception("Failed to generate or send AI reply to %s", wa_id)


def process_incoming_image(conversation, incoming_message, wa_id):
    try:
        if not incoming_message.media_id:
            raise ValueError("WhatsApp image media ID is missing.")

        if conversation.complaint_step == "awaiting_confirmation":
            send_and_save_reply(
                conversation,
                wa_id,
                "Your previous photo has already been validated. Please reply Yes or No to the confirmation message.",
            )
            return

        complaint_description = get_complaint_description(
            conversation,
            incoming_message,
        )

        if not complaint_description:
            send_and_save_reply(
                conversation,
                wa_id,
                "Please describe the office problem before uploading its photo.",
            )
            return

        image_result = process_whatsapp_image(
            incoming_message.media_id
        )

        validation = validate_complaint_image(
            image_url=image_result["image_url"],
            complaint_description=complaint_description,
        )

        status = validation["status"]
        relevant = validation["relevant"]
        reason = validation["reason"]

        if status == "valid" and relevant:
            conversation.complaint_description = complaint_description
            conversation.complaint_category = get_complaint_category(
                complaint_description
            )
            conversation.evidence_url = image_result["image_url"]
            conversation.evidence_public_id = image_result["public_id"]
            conversation.evidence_validation_status = "valid"
            conversation.evidence_validation_reason = reason
            conversation.last_evidence_message_id = incoming_message.message_id
            conversation.complaint_step = "awaiting_confirmation"

            conversation.save()

            reply = (
                "Your photo has been validated successfully.\n\n"
                f"Complaint: {complaint_description}\n"
                f"Category: {conversation.get_complaint_category_display() if hasattr(conversation, 'get_complaint_category_display') else conversation.complaint_category}\n"
                f"Evidence: {reason}\n\n"
                "Would you like to confirm and register this complaint?\n\n"
                "Reply Yes to register or No to cancel."
            )

        elif status == "irrelevant":
            reply = (
                "The uploaded photo does not appear to match your complaint.\n"
                f"Reason: {reason}\n\n"
                "Please upload a relevant photo showing the issue."
            )

        else:
            reply = (
                "I couldn't clearly verify the reported issue from this photo.\n"
                f"Reason: {reason}\n\n"
                "Please upload a clearer photo."
            )

        send_and_save_reply(conversation, wa_id, reply)

    except Exception:
        logger.exception(
            "Failed to process or validate WhatsApp image from %s",
            wa_id,
        )

        try:
            send_and_save_reply(
                conversation,
                wa_id,
                "I received your photo, but couldn't validate it right now. Please try again later.",
            )
        except Exception:
            logger.exception(
                "Failed to send image processing error message to %s",
                wa_id,
            )


def process_webhook_payload(payload):
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            
        # Process WhatsApp message delivery status updates.
        statuses = value.get("statuses", [])

        for status_event in statuses:

            message_id = status_event.get("id")
            message_status = status_event.get("status")

            if not message_id or message_status not in [
                "sent",
                "delivered",
                "read",
                "failed",
            ]:
                continue

            WhatsAppMessage.objects.filter(
                message_id=message_id,
                direction="outgoing"
            ).update(
                status=message_status
            )


            contacts = value.get("contacts", [])
            messages = value.get("messages", [])

            contact_names = {
                contact.get("wa_id"): contact.get("profile", {}).get("name", "")
                for contact in contacts
            }

            for message in messages:
                wa_id = message.get("from")

                if not wa_id:
                    continue

                contact, _ = WhatsAppContact.objects.update_or_create(
                    wa_id=wa_id,
                    defaults={
                        "name": contact_names.get(wa_id, ""),
                        "phone_number": wa_id,
                    },
                )

                conversation = (
                    WhatsAppConversation.objects
                    .filter(contact=contact, status="active")
                    .order_by("-created_at")
                    .first()
                )

                if not conversation:
                    conversation = WhatsAppConversation.objects.create(
                        contact=contact
                    )

                message_type = message.get("type", "unknown")
                text = ""

                if message_type == "text":
                    text = message.get("text", {}).get("body", "")

                elif message_type == "button":
                    text = message.get("button", {}).get("text", "")

                elif message_type == "interactive":
                    interactive = message.get("interactive", {})
                    text = (
                        interactive.get("button_reply", {}).get("title")
                        or interactive.get("list_reply", {}).get("title")
                        or ""
                    )

                media_id = ""

                if message_type in [
                    "image", "video", "audio", "document", "sticker"
                ]:
                    media_id = message.get(message_type, {}).get("id", "")

                message_timestamp = None
                timestamp = message.get("timestamp")

                if timestamp:
                    message_timestamp = datetime.fromtimestamp(
                        int(timestamp),
                        tz=dt_timezone.utc,
                    )

                saved_message, created = WhatsAppMessage.objects.get_or_create(
                    message_id=message.get("id"),
                    defaults={
                        "conversation": conversation,
                        "direction": "incoming",
                        "message_type": message_type,
                        "text": text,
                        "media_id": media_id,
                        "status": "received",
                        "raw_payload": message,
                        "timestamp": message_timestamp,
                    },
                )

                if not created:
                    continue

                conversation.last_message_at = (
                    message_timestamp or timezone.now()
                )
                conversation.save(
                    update_fields=["last_message_at", "updated_at"]
                )

                if message_type == "text" and text.strip():
                    send_ai_reply(
                        conversation=conversation,
                        incoming_message=saved_message,
                        wa_id=wa_id,
                    )

                elif message_type == "image" and media_id:
                    process_incoming_image(
                        conversation=conversation,
                        incoming_message=saved_message,
                        wa_id=wa_id,
                    )
