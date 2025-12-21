from django import forms

from .models import GuestParticipant


class GuestCheckInForm(forms.ModelForm):
    class Meta:
        model = GuestParticipant
        fields = ["name", "email"]
