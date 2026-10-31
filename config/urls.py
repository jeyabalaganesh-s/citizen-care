from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls')),
    path('complaints/', include('complaints.urls')),
    path('whatsapp/', include('whatsapp.urls')),

    # Citizen Care public website
    path('', include('pages.urls')),
]