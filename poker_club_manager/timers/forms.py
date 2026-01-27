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

    def _parse_level(self, index, data, keys):
        parsed_values = []
        for key in keys:
            try:
                value = int(data.get(f"levels-{index}-{key}"))
            except ValueError:
                msg = f"Invalid {key} in level {index}"
                raise forms.ValidationError(msg) from None
            if value <= 0:
                msg = f"Level {index} {key} must be positive"
                raise forms.ValidationError(msg)
            parsed_values.append(value)

        return tuple(parsed_values)

    def _parse_play_level(self, index, data):
        sb, bb, duration_minutes = self._parse_level(
            index,
            data,
            ("small", "big", "duration"),
        )
        if sb >= bb:
            msg = f"Level {index} small blind must be less than big blind"
            raise forms.ValidationError(msg)
        return {
            "level_type": "play",
            "small_blind": sb,
            "big_blind": bb,
            "duration_seconds": duration_minutes * 60,
        }

    def _parse_break_level(self, index, data):
        results = self._parse_level(index, data, ("duration",))
        return {
            "level_type": "break",
            "duration_seconds": results[0] * 60,
        }

    def _parse_levels(self):
        levels = []
        index = 1
        data = self.data.copy()

        while f"levels-{index}-type" in data:
            level_type = data.get(f"levels-{index}-type")

            match level_type:
                case "play":
                    levels.append(self._parse_play_level(index, data))
                case "break":
                    levels.append(self._parse_break_level(index, data))
                case _:
                    msg = f"Invalid level type in level {index}: {level_type}"
                    raise forms.ValidationError(msg)
            index += 1

        if not levels:
            msg = "At least one blind level is required."
            raise forms.ValidationError(msg)

        return levels
