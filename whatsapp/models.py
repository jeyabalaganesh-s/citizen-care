from django.db import models


class WhatsAppContact(models.Model):

    wa_id = models.CharField(
        max_length=30,
        unique=True
    )

    name = models.CharField(
        max_length=150,
        blank=True
    )

    phone_number = models.CharField(
        max_length=30,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name or self.wa_id


class WhatsAppConversation(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('waiting', 'Waiting'),
        ('completed', 'Completed'),
    ]

    contact = models.ForeignKey(
        WhatsAppContact,
        on_delete=models.CASCADE,
        related_name='conversations'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    last_message_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Conversation - {self.contact.wa_id}"


class WhatsAppMessage(models.Model):

    DIRECTION_CHOICES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]

    conversation = models.ForeignKey(
        WhatsAppConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    message_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES
    )

    message_type = models.CharField(
        max_length=30,
        default='text'
    )

    text = models.TextField(
        blank=True
    )

    media_id = models.CharField(
        max_length=255,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        default='received'
    )

    raw_payload = models.JSONField(
        default=dict,
        blank=True
    )

    timestamp = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.direction} - {self.message_type}"