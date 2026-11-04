
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from complaints.models import Complaint
from whatsapp.models import (
    WhatsAppContact,
    WhatsAppConversation,
    WhatsAppMessage,
)
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect

from django.db.models import Q, Prefetch

from whatsapp.services.cloud_api import send_text_message

import logging

logger = logging.getLogger(__name__)
@login_required
def dashboard_home(request):

    # Restrict dashboard access to staff members.
    if not request.user.is_staff:
        raise PermissionDenied

    today = timezone.localdate()
    start_date = today - timedelta(days=6)

    # Complaint statistics
    total_complaints = Complaint.objects.count()

    pending_complaints = Complaint.objects.filter(
        status__in=["received", "under_review"]
    ).count()

    in_progress_complaints = Complaint.objects.filter(
        status="in_progress"
    ).count()

    resolved_complaints = Complaint.objects.filter(
        status="resolved"
    ).count()

    approved_complaints = Complaint.objects.filter(
        status="approved"
    ).count()

    rejected_complaints = Complaint.objects.filter(
        status="rejected"
    ).count()

    # WhatsApp statistics
    total_contacts = WhatsAppContact.objects.count()

    total_conversations = WhatsAppConversation.objects.count()

    active_conversations = WhatsAppConversation.objects.filter(
        status="active"
    ).count()

    waiting_conversations = WhatsAppConversation.objects.filter(
        status="waiting"
    ).count()

    completed_conversations = WhatsAppConversation.objects.filter(
        status="completed"
    ).count()

    total_messages = WhatsAppMessage.objects.count()

    incoming_messages = WhatsAppMessage.objects.filter(
        direction="incoming"
    ).count()

    outgoing_messages = WhatsAppMessage.objects.filter(
        direction="outgoing"
    ).count()

    # Complaints created during the last 7 days
    daily_data = (
        Complaint.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=today,
        )
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    daily_counts = {
        item["day"]: item["total"]
        for item in daily_data
    }

    chart_labels = []
    chart_values = []

    for i in range(7):
        current_date = start_date + timedelta(days=i)

        chart_labels.append(
            current_date.strftime("%d %b")
        )

        chart_values.append(
            daily_counts.get(current_date, 0)
        )

    # Complaint category breakdown
    category_data = (
        Complaint.objects.values("category")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    category_labels = [
        dict(Complaint.CATEGORY_CHOICES).get(
            item["category"],
            item["category"]
        )
        for item in category_data
    ]

    category_values = [
        item["total"]
        for item in category_data
    ]

    # Priority breakdown
    priority_data = (
        Complaint.objects.values("priority")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    priority_labels = [
        dict(Complaint.PRIORITY_CHOICES).get(
            item["priority"],
            item["priority"]
        )
        for item in priority_data
    ]

    priority_values = [
        item["total"]
        for item in priority_data
    ]

    # Recent complaints
    recent_complaints = (
        Complaint.objects
        .order_by("-created_at")[:7]
    )

    # Recent conversations
    recent_conversations = (
        WhatsAppConversation.objects
        .select_related("contact")
        .order_by("-last_message_at", "-created_at")[:7]
    )

    # Recent messages
    recent_messages = (
        WhatsAppMessage.objects
        .select_related("conversation__contact")
        .order_by("-timestamp", "-created_at")[:7]
    )

    context = {
        # Complaint statistics
        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,
        "in_progress_complaints": in_progress_complaints,
        "resolved_complaints": resolved_complaints,
        "approved_complaints": approved_complaints,
        "rejected_complaints": rejected_complaints,

        # WhatsApp statistics
        "total_contacts": total_contacts,
        "total_conversations": total_conversations,
        "active_conversations": active_conversations,
        "waiting_conversations": waiting_conversations,
        "completed_conversations": completed_conversations,
        "total_messages": total_messages,
        "incoming_messages": incoming_messages,
        "outgoing_messages": outgoing_messages,

        # Charts
        "chart_labels": chart_labels,
        "chart_values": chart_values,
        "category_labels": category_labels,
        "category_values": category_values,
        "priority_labels": priority_labels,
        "priority_values": priority_values,

        # Recent activity
        "recent_complaints": recent_complaints,
        "recent_conversations": recent_conversations,
        "recent_messages": recent_messages,
    }

    return render(
        request,
        "dashboard/index.html",
        context
    )


@login_required
def complaints_list(request):

    if not request.user.is_staff:
        raise PermissionDenied

    complaints = Complaint.objects.all()

    # Search
    search = request.GET.get("search", "").strip()

    if search:
        complaints = complaints.filter(
            Q(complaint_id__icontains=search) |
            Q(citizen_name__icontains=search) |
            Q(citizen_phone__icontains=search)
        )

    # Filters
    status = request.GET.get("status", "")
    category = request.GET.get("category", "")
    priority = request.GET.get("priority", "")

    valid_statuses = dict(Complaint.STATUS_CHOICES)
    valid_categories = dict(Complaint.CATEGORY_CHOICES)
    valid_priorities = dict(Complaint.PRIORITY_CHOICES)

    if status in valid_statuses:
        complaints = complaints.filter(status=status)

    if category in valid_categories:
        complaints = complaints.filter(category=category)

    if priority in valid_priorities:
        complaints = complaints.filter(priority=priority)

    # Pagination
    paginator = Paginator(complaints, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "complaints": page_obj.object_list,

        "search": search,
        "selected_status": status,
        "selected_category": category,
        "selected_priority": priority,

        "status_choices": Complaint.STATUS_CHOICES,
        "category_choices": Complaint.CATEGORY_CHOICES,
        "priority_choices": Complaint.PRIORITY_CHOICES,

        "total_complaints": Complaint.objects.count(),
        "filtered_count": paginator.count,
    }

    return render(
        request,
        "dashboard/complaints.html",
        context
    )


@login_required
def complaint_detail(request, complaint_id):

    if not request.user.is_staff:
        raise PermissionDenied

    complaint = get_object_or_404(
        Complaint.objects.prefetch_related("evidences"),
        complaint_id=complaint_id
    )

    context = {
        "complaint": complaint,
        "evidences": complaint.evidences.all(),
        "status_choices": Complaint.STATUS_CHOICES,
        "priority_choices": Complaint.PRIORITY_CHOICES,
    }

    return render(
        request,
        "dashboard/complaint_detail.html",
        context
    )


@login_required
def update_complaint(request, complaint_id):

    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return redirect("dashboard:complaints")

    complaint = get_object_or_404(
        Complaint,
        complaint_id=complaint_id
    )

    new_status = request.POST.get("status")
    new_priority = request.POST.get("priority")

    valid_statuses = dict(Complaint.STATUS_CHOICES)
    valid_priorities = dict(Complaint.PRIORITY_CHOICES)

    if new_status not in valid_statuses:
        messages.error(request, "Invalid complaint status.")
        return redirect(
            "dashboard:complaint_detail",
            complaint_id=complaint_id
        )

    if new_priority not in valid_priorities:
        messages.error(request, "Invalid complaint priority.")
        return redirect(
            "dashboard:complaint_detail",
            complaint_id=complaint_id
        )

    complaint.status = new_status
    complaint.priority = new_priority

    if new_status == "resolved":
        if not complaint.resolved_at:
            complaint.resolved_at = timezone.now()
    else:
        complaint.resolved_at = None

    complaint.reviewed_by = request.user

    complaint.save()

    messages.success(
        request,
        f"Complaint {complaint.complaint_id} updated successfully."
    )

    return redirect(
        "dashboard:complaint_detail",
        complaint_id=complaint_id
    )

@login_required
def conversations_list(request):

    if not request.user.is_staff:
        raise PermissionDenied

    search = request.GET.get("search", "").strip()
    selected_status = request.GET.get("status", "")

    conversations = (
        WhatsAppConversation.objects
        .select_related("contact", "registered_complaint")
        .prefetch_related("messages")
        .order_by("-last_message_at", "-created_at")
    )

    if search:
        conversations = conversations.filter(
            Q(contact__name__icontains=search) |
            Q(contact__phone_number__icontains=search) |
            Q(contact__wa_id__icontains=search)
        )

    valid_statuses = dict(WhatsAppConversation.STATUS_CHOICES)

    if selected_status in valid_statuses:
        conversations = conversations.filter(
            status=selected_status
        )

    selected_id = request.GET.get("conversation")

    selected_conversation = None

    if selected_id:
        selected_conversation = get_object_or_404(
            WhatsAppConversation.objects.select_related(
                "contact",
                "registered_complaint"
            ),
            pk=selected_id
        )

    elif conversations.exists():
        selected_conversation = conversations.first()

    chat_messages = []

    if selected_conversation:
        chat_messages = list(
            selected_conversation.messages.order_by(
                "timestamp",
                "created_at",
                "id"
            )
        )

    context = {
        "conversations": conversations,
        "selected_conversation": selected_conversation,
        "chat_messages": chat_messages,
        "search": search,
        "selected_status": selected_status,
        "status_choices": WhatsAppConversation.STATUS_CHOICES,
    }

    return render(
        request,
        "dashboard/conversations.html",
        context
    )


@login_required
def send_conversation_message(request, conversation_id):

    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return redirect("dashboard:conversations")

    conversation = get_object_or_404(
        WhatsAppConversation.objects.select_related("contact"),
        pk=conversation_id
    )

    reply = request.POST.get("message", "").strip()

    if not reply:
        messages.error(request, "Please enter a message.")
        return redirect(
            f"/dashboard/conversations/?conversation={conversation_id}"
        )

    if conversation.status == "completed":
        messages.error(
            request,
            "This conversation is completed. Reopen it before replying."
        )
        return redirect(
            f"/dashboard/conversations/?conversation={conversation_id}"
        )

    try:
        # Send through your existing WhatsApp Cloud API service.
        response = send_text_message(
            to=conversation.contact.wa_id,
            message=reply
        )

        if not isinstance(response, dict) or response.get("error"):
            raise ValueError("WhatsApp API did not accept the message.")

        api_messages = response.get("messages") or []
        outgoing_message_id = (
            api_messages[0].get("id")
            if api_messages else None
        )

        # Save the outgoing message.
        WhatsAppMessage.objects.create(
            conversation=conversation,
            message_id=outgoing_message_id,
            direction="outgoing",
            message_type="text",
            text=reply,
            status="sent",
            raw_payload=response,
            timestamp=timezone.now()
        )

        conversation.last_message_at = timezone.now()
        conversation.save(
            update_fields=["last_message_at", "updated_at"]
        )

        messages.success(request, "Message sent successfully.")

    except Exception:
        logger.exception(
            "Failed to send dashboard reply for conversation %s",
            conversation_id
        )

        messages.error(
            request,
            "Unable to send the WhatsApp message. Please try again."
        )

    return redirect(
        f"/dashboard/conversations/?conversation={conversation_id}"
    )


@login_required
def update_conversation_status(request, conversation_id):

    if not request.user.is_staff:
        raise PermissionDenied

    if request.method != "POST":
        return redirect("dashboard:conversations")

    conversation = get_object_or_404(
        WhatsAppConversation,
        pk=conversation_id
    )

    new_status = request.POST.get("status")

    valid_statuses = dict(WhatsAppConversation.STATUS_CHOICES)

    if new_status not in valid_statuses:
        messages.error(request, "Invalid conversation status.")
    else:
        conversation.status = new_status
        conversation.save(
            update_fields=["status", "updated_at"]
        )

        messages.success(
            request,
            "Conversation status updated successfully."
        )

    return redirect(
        f"/dashboard/conversations/?conversation={conversation_id}"
    )


@login_required
def messages_list(request):

    if not request.user.is_staff:
        raise PermissionDenied

    whatsapp_messages = (
        WhatsAppMessage.objects
        .select_related(
            "conversation",
            "conversation__contact"
        )
        .order_by("-created_at")
    )

    # Search
    search = request.GET.get("search", "").strip()

    if search:
        whatsapp_messages = whatsapp_messages.filter(
            Q(text__icontains=search) |
            Q(message_id__icontains=search) |
            Q(conversation__contact__name__icontains=search) |
            Q(conversation__contact__phone_number__icontains=search) |
            Q(conversation__contact__wa_id__icontains=search)
        )

    # Direction filter
    direction = request.GET.get("direction", "")

    if direction in ["incoming", "outgoing"]:
        whatsapp_messages = whatsapp_messages.filter(
            direction=direction
        )

    # Message type filter
    message_type = request.GET.get("type", "")

    if message_type in [
        "text", "image", "video", "audio",
        "document", "sticker", "button", "interactive"
    ]:
        whatsapp_messages = whatsapp_messages.filter(
            message_type=message_type
        )

    # Delivery status filter
    status = request.GET.get("status", "")

    if status in ["received", "sent", "delivered", "read", "failed"]:
        whatsapp_messages = whatsapp_messages.filter(
            status=status
        )

    # Date filters
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    import datetime

    try:
        if date_from:
            datetime.date.fromisoformat(date_from)
            whatsapp_messages = whatsapp_messages.filter(
                created_at__date__gte=date_from
            )
        else:
            date_from = ""

    except ValueError:
        date_from = ""

    try:
        if date_to:
            datetime.date.fromisoformat(date_to)
            whatsapp_messages = whatsapp_messages.filter(
                created_at__date__lte=date_to
            )
        else:
            date_to = ""

    except ValueError:
        date_to = ""

    # Pagination
    paginator = Paginator(whatsapp_messages, 20)

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    # Overall statistics
    total_messages = WhatsAppMessage.objects.count()

    incoming_count = WhatsAppMessage.objects.filter(
        direction="incoming"
    ).count()

    outgoing_count = WhatsAppMessage.objects.filter(
        direction="outgoing"
    ).count()

    failed_count = WhatsAppMessage.objects.filter(
        status="failed"
    ).count()

    context = {
        "page_obj": page_obj,
        "whatsapp_messages": page_obj.object_list,

        "search": search,
        "selected_direction": direction,
        "selected_type": message_type,
        "selected_status": status,

        "date_from": date_from,
        "date_to": date_to,

        "total_messages": total_messages,
        "incoming_count": incoming_count,
        "outgoing_count": outgoing_count,
        "failed_count": failed_count,
    }

    return render(
        request,
        "dashboard/messages.html",
        context
    )
