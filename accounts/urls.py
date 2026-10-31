from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path(
        'register/',
        views.register_view,
        name='register'
    ),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            redirect_authenticated_user=True
        ),
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),
    path(
        'data-deletion-request/',
        views.data_deletion_request,
        name='data_deletion_request'
    ),
]