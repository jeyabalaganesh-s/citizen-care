from django.contrib import admin
from .models import Complaint, ComplaintEvidence, ComplaintCategory


class ComplaintEvidenceInline(admin.TabularInline):

    model = ComplaintEvidence
    extra = 0


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):

    list_display = (
        'complaint_id',
        'citizen_name',
        'citizen_phone',
        'category',
        'status',
        'priority',
        'source',
        'assigned_to',
        'created_at',
    )

    list_filter = (
        'status',
        'priority',
        'category',
        'source',
        'created_at',
    )

    search_fields = (
        'complaint_id',
        'citizen_name',
        'citizen_phone',
        'description',
    )

    readonly_fields = (
        'complaint_id',
        'created_at',
        'updated_at',
    )

    inlines = [ComplaintEvidenceInline]


@admin.register(ComplaintEvidence)
class ComplaintEvidenceAdmin(admin.ModelAdmin):

    list_display = (
        'complaint',
        'description',
        'uploaded_at',
    )


@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("is_active",)
    ordering = ("name",)