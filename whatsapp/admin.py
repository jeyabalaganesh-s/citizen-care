from django.contrib import admin
from .models import (
    WhatsAppContact,
    WhatsAppConversation,
    WhatsAppMessage
)


@admin.register(WhatsAppContact)
class WhatsAppContactAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'wa_id',
        'phone_number',
        'created_at',
    )

    search_fields = (
        'name',
        'wa_id',
        'phone_number',
    )


@admin.register(WhatsAppConversation)
class WhatsAppConversationAdmin(admin.ModelAdmin):

    list_display = (
        'contact',
        'status',
        'last_message_at',
        'created_at',
    )

    list_filter = ('status',)


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):

    list_display = (
        'conversation',
        'direction',
        'message_type',
        'status',
        'created_at',
    )

    list_filter = (
        'direction',
        'message_type',
        'status',
    )

    search_fields = (
        'message_id',
        'text',
    )