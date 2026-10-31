from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('citizen', 'Citizen'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='citizen'
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

class DataDeletionRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    email = models.EmailField()
    phone_number = models.CharField(max_length=15)

    reason = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    admin_notes = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.email} - {self.status}"

    class Meta:
        ordering = ['-requested_at']