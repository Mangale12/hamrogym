from django import forms

from ..models import LeadStatus


class LeadStatusForm(forms.ModelForm):
    class Meta:
        model = LeadStatus
        fields = [
            "name",
            "code",
            "sequence",
            "is_default",
            "color",
            "is_closed",
            "is_active",
            "remarks",
        ]
        widgets = {
            "color": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "form-control form-control-color",
                    "title": "Choose status color",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["color"].initial = self.initial.get("color") or getattr(
            self.instance, "color", None
        ) or "#3498DB"
        self.fields["color"].help_text = "Pick the color used to identify this status."

    def clean_code(self):
        return (self.cleaned_data.get("code") or "").strip().lower()

    def clean_name(self):
        return (self.cleaned_data.get("name") or "").strip()

    def clean_color(self):
        return (self.cleaned_data.get("color") or "#3498DB").strip().upper()
