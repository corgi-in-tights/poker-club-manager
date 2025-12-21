from django import forms

from poker_club_manager.common.models import Season

from .models import Event, GuestParticipant


class EventForm(forms.ModelForm):
    season = forms.ModelChoiceField(
        queryset=Season.objects.all(),
        required=False,
        widget=forms.RadioSelect(),
    )
    title = forms.CharField(max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
    location = forms.CharField(max_length=255, required=True)
    start_date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )
    end_date = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Event
        fields = [
            "season",
            "title",
            "description",
            "start_date",
            "end_date",
            "location",
        ]


class GuestCheckInForm(forms.ModelForm):
    class Meta:
        model = GuestParticipant
        fields = ["name", "email"]
