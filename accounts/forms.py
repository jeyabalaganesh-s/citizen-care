from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CitizenRegistrationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=150,
        required=True
    )

    last_name = forms.CharField(
        max_length=150,
        required=True
    )

    email = forms.EmailField(
        required=True
    )

    phone_number = forms.CharField(
        max_length=15,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'phone_number',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = 'citizen'

        if commit:
            user.save()

        return user


class DataDeletionRequestForm(forms.Form):

    email = forms.EmailField(
        label="Registered Email Address"
    )

    phone_number = forms.CharField(
        max_length=15,
        label="Registered Phone Number"
    )

    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Optional: Tell us why you want to delete your data.'
        })
    )