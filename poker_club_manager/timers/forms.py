from django import forms

from poker_club_manager.events.models import Event

from .models import BlindsTimer


class BlindsTimerForm(forms.ModelForm):
    name = forms.CharField(max_length=255, required=True)
    event = forms.ModelChoiceField(
        queryset=Event.objects.active(),
        required=False,
        widget=forms.RadioSelect(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = BlindsTimer
        fields = [
            "name",
            "event",
        ]

    def clean(self):
        cleaned = super().clean()
        self.levels_data = self._parse_levels()
        return cleaned

    def _parse_play_levels(self, index, data):
        try:
            sb = int(data[f"levels-{index}-small"])
        except (KeyError, ValueError):
            msg = f"Invalid small blind in level {index}"
            raise forms.ValidationError(msg) from None
        if sb <= 0:
            msg = f"Level {index} duration must be positive"
            raise forms.ValidationError(msg)

        try:
            bb = int(data[f"levels-{index}-big"])
        except (KeyError, ValueError):
            msg = f"Invalid big blind in level {index}"
            raise forms.ValidationError(msg) from None
        if bb <= 0:
            msg = f"Level {index} duration must be positive"
            raise forms.ValidationError(msg)
        if sb >= bb:
            msg = f"Level {index}: small blind must be less than big blind"
            raise forms.ValidationError(msg)
        return sb, bb

    def _parse_levels(self):
        levels = []
        index = 1
        data = self.data

        while f"levels-{index}-type" in data:
            level_type = data[f"levels-{index}-type"]

            if level_type == "play":
                sb, bb = self._parse_play_levels(index, data)
                info = {
                    "level_type": "play",
                    "small_blind": sb,
                    "big_blind": bb,
                }
            elif level_type == "break":
                info = {
                    "level_type": "break",
                }
            else:
                msg = f"Invalid level type in level {index}"
                raise forms.ValidationError(msg)

            try:
                duration_minutes = int(data[f"levels-{index}-duration"])
            except (KeyError, ValueError):
                msg = f"Invalid duration in level {index}"
                raise forms.ValidationError(msg) from None

            if duration_minutes <= 0:
                msg = f"Level {index} duration must be positive"
                raise forms.ValidationError(msg)

            info["duration_seconds"] = duration_minutes * 60
            levels.append(info)
            index += 1
            continue

        if not levels:
            msg = "At least one blind level is required."
            raise forms.ValidationError(msg)

        return levels
