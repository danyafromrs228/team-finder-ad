from django import forms
from django.core.exceptions import ValidationError

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "status": forms.Select(choices=Project._meta.get_field('status').choices),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        if github_url and "github.com" not in github_url:
            raise ValidationError("Ссылка должна вести на GitHub")
        return github_url
    