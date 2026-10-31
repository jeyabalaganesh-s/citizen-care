from django.utils import timezone
from django.utils.dateparse import parse_datetime

from whatsapp.models import (
    WhatsAppContact,
    WhatsAppConversation,
    WhatsAppMessage,
)


def process_webhook_payload(payload):

    for entry in payload.get('entry', []):

        for change in entry.get('changes', []):

            value = change.get('value', {})

            contacts = value.get('contacts', [])
            messages = value.get('messages', [])

            contact_names = {
                contact.get('wa_id'): (
                    contact.get('profile', {}).get('name', '')
                )
                for contact in contacts
            }

            for message in messages:

                wa_id = message.get('from')

                if not wa_id:
                    continue

                contact, _ = WhatsAppContact.objects.update_or_create(
                    wa_id=wa_id,
                    defaults={
                        'name': contact_names.get(wa_id, ''),
                        'phone_number': wa_id,
                    }
                )

                conversation = (
                    WhatsAppConversation.objects
                    .filter(
                        contact=contact,
                        status='active'
                    )
                    .order_by('-created_at')
                    .first()
                )

                if not conversation:
                    conversation = WhatsAppConversation.objects.create(
                        contact=contact
                    )

                message_type = message.get('type', 'unknown')

                text = ''

                if message_type == 'text':
                    text = message.get(
                        'text', {}
                    ).get('body', '')

                elif message_type == 'button':
                    text = message.get(
                        'button', {}
                    ).get('text', '')

                elif message_type == 'interactive':
                    interactive = message.get(
                        'interactive', {}
                    )

                    text = (
                        interactive.get('button_reply', {}).get('title')
                        or interactive.get('list_reply', {}).get('title')
                        or ''
                    )

                media_id = ''

                if message_type in [
                    'image',
                    'video',
                    'audio',
                    'document',
                    'sticker',
                ]:
                    media_id = message.get(
                        message_type, {}
                    ).get('id', '')

                message_timestamp = None

                timestamp = message.get('timestamp')

                if timestamp:
                    from datetime import datetime, timezone as dt_timezone

                    message_timestamp = datetime.fromtimestamp(
                        int(timestamp),
                        tz=dt_timezone.utc
                    )

                saved_message, created = (
                    WhatsAppMessage.objects.get_or_create(
                        message_id=message.get('id'),
                        defaults={
                            'conversation': conversation,
                            'direction': 'incoming',
                            'message_type': message_type,
                            'text': text,
                            'media_id': media_id,
                            'status': 'received',
                            'raw_payload': message,
                            'timestamp': message_timestamp,
                        }
                    )
                )

                if created:
                    conversation.last_message_at = (
                        message_timestamp or timezone.now()
                    )
                    conversation.save(
                        update_fields=[
                            'last_message_at',
                            'updated_at'
                        ]
                    )

            # Delivery/read status events are processed separately later.