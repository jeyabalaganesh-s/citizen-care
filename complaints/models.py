import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Complaint(models.Model):

    STATUS_CHOICES = [
        ('received', 'Received'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    SOURCE_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('admin', 'Admin Dashboard'),
    ]

    CATEGORY_CHOICES = [
        ('water', 'Water'),
        ('electricity', 'Electricity'),
        ('road', 'Road'),
        ('sanitation', 'Sanitation'),
        ('health', 'Health'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]

    complaint_id = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    citizen_name = models.CharField(
        max_length=150
    )

    citizen_phone = models.CharField(
        max_length=20,
        db_index=True
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    description = models.TextField()

    location = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='received',
        db_index=True
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='whatsapp'
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_complaints'
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.complaint_id:
            self.complaint_id = (
                f"CMP-{timezone.now():%Y%m%d}-"
                f"{uuid.uuid4().hex[:8].upper()}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.complaint_id

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'


class ComplaintEvidence(models.Model):

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='evidences'
    )

    image = models.ImageField(
        upload_to='complaints/evidence/%Y/%m/'
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.complaint.complaint_id} - Evidence"  