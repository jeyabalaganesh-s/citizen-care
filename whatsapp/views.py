import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.views.decorators.csrf import csrf_exempt

from .services.webhook import process_webhook_payload


logger = logging.getLogger(__name__)


def verify_meta_signature(request):

    app_secret = settings.META_APP_SECRET

    if not app_secret:
        return settings.DEBUG

    signature = request.headers.get(
        'X-Hub-Signature-256',
        ''
    )

    if not signature.startswith('sha256='):
        return False

    expected = 'sha256=' + hmac.new(
        app_secret.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)


@csrf_exempt
def whatsapp_webhook(request):

    # Meta webhook verification
    if request.method == 'GET':

        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if (
            mode == 'subscribe'
            and token == settings.WHATSAPP_VERIFY_TOKEN
            and challenge
        ):
            return HttpResponse(challenge)

        return HttpResponseForbidden(
            'Webhook verification failed'
        )

    # Incoming messages and status events
    if request.method == 'POST':

        if not verify_meta_signature(request):
            return HttpResponseForbidden(
                'Invalid webhook signature'
            )

        try:
            payload = json.loads(request.body)

            if payload.get('object') != 'whatsapp_business_account':
                return JsonResponse(
                    {'status': 'ignored'}
                )

            process_webhook_payload(payload)

            return JsonResponse(
                {'status': 'received'}
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Invalid JSON'},
                status=400
            )

        except Exception:
            logger.exception(
                'WhatsApp webhook processing failed'
            )

            return JsonResponse(
                {'error': 'Webhook processing failed'},
                status=500
            )

    return JsonResponse(
        {'error': 'Method not allowed'},
        status=405
    )