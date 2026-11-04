
from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),

    path(
        "complaints/",
        views.complaints_list,
        name="complaints"
    ),

    path(
        "complaints/<str:complaint_id>/",
        views.complaint_detail,
        name="complaint_detail"
    ),

    path(
        "complaints/<str:complaint_id>/update/",
        views.update_complaint,
        name="update_complaint"
    ),
    
    path(
        "conversations/",
        views.conversations_list,
        name="conversations"
    ),

    path(
        "conversations/<int:conversation_id>/send/",
        views.send_conversation_message,
        name="send_conversation_message"
    ),

    path(
        "conversations/<int:conversation_id>/status/",
        views.update_conversation_status,
        name="update_conversation_status"
    ),
    
    path(
        "messages/",
        views.messages_list,
        name="messages"
    ),


]
