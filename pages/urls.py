from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home, name='home'),

    path('about/', views.about, name='about'),

    path('services/', views.services, name='services'),

    path('contact/', views.contact, name='contact'),

    path('faq/', views.faq, name='faq'),

    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),

    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),

    path('data-deletion/', views.data_deletion, name='data_deletion'),
]