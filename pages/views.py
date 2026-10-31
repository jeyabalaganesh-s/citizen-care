from django.shortcuts import render


def home(request):
    return render(request, 'pages/home.html')


def about(request):
    return render(request, 'pages/about.html')


def services(request):
    return render(request, 'pages/services.html')


def contact(request):
    return render(request, 'pages/contact.html')


def faq(request):
    return render(request, 'pages/faq.html')


def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html')


def terms_conditions(request):
    return render(request, 'pages/terms_conditions.html')


def data_deletion(request):
    return render(request, 'pages/data_deletion.html')