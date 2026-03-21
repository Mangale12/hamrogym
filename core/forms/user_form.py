from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "password",
        ]

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        queryset = User.objects.filter(username__iexact=username)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username

    def clean_email(self):
        return (self.cleaned_data.get("email") or "").strip()

    def clean_password(self):
        password = self.cleaned_data.get("password") or ""
        if not self.instance.pk and not password:
            raise forms.ValidationError("Password is required for a new user.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
