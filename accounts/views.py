from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import DataDeletionRequestForm
from .models import DataDeletionRequest


from .forms import CitizenRegistrationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('complaints:dashboard')

    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('complaints:dashboard')
    else:
        form = CitizenRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('accounts:login')

    return redirect('complaints:dashboard')


def data_deletion_request(request):
    if request.method == 'POST':
        form = DataDeletionRequestForm(request.POST)

        if form.is_valid():
            DataDeletionRequest.objects.create(
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                reason=form.cleaned_data['reason']
            )

            messages.success(
                request,
                'Your data deletion request has been submitted successfully. '
                'Our team will review your request.'
            )

            return redirect('pages:data_deletion')

    else:
        form = DataDeletionRequestForm()

    return render(
        request,
        'pages/data_deletion.html',
        {'form': form}
    )