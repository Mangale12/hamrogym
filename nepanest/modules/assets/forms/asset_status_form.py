from django import forms

from ..models import AssetStatus


class AssetStatusForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.is_system:
            self.fields["code"].disabled = True
            self.fields["code"].widget.attrs["readonly"] = True

    def clean_code(self):
        if self.instance and self.instance.pk and self.instance.is_system:
            return self.instance.code
        return self.cleaned_data.get("code")

    class Meta:
        model = AssetStatus
        fields = [
            "name",
            "code",
            "is_active",
            "remarks",
        ]
