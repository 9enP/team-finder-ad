from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
            "name": forms.TextInput(),
            "description": forms.Textarea(),
            "status": forms.Select(
                choices=[("open", "Открыт"), ("closed", "Закрыт")],
            ),
            "github_url": forms.URLInput(),
        }

    def clean_github_url(self):
        url = (self.cleaned_data.get("github_url") or "").strip()
        if not url:
            return ""
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError("Укажите корректный URL.")
        if "github.com" not in url.lower():
            raise ValidationError("Ссылка должна вести на GitHub")
        return url
