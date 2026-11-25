from django import forms
from django.contrib.auth import get_user_model

from .models import Incident, IncidentComment
from .permissions import ANALYST_GROUP, is_administrator

class IncidentForm(forms.ModelForm):
    severity = forms.ChoiceField(choices=Incident.Severity.choices, required=False, initial=Incident.Severity.MEDIUM)

    class Meta:
        model = Incident
        # Ownership is never accepted from the browser.
        fields = ["title", "description", "severity"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "A short, descriptive title", "autofocus": True}),
            "description": forms.Textarea(attrs={"rows": 8, "placeholder": "What happened? Include synthetic details only."}),
        }
        help_texts = {
            "title": "3–150 characters.",
            "description": "10–5,000 characters. Use plain text; do not enter passwords or personal data.",
        }

    def clean_severity(self):
        return self.cleaned_data.get("severity") or Incident.Severity.MEDIUM


class IncidentCommentForm(forms.ModelForm):
    class Meta:
        model = IncidentComment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "Add a factual, plain-text note."}),
        }
        help_texts = {"body": "2-2,000 characters. Do not include passwords, tokens, or personal data."}


class IncidentManageForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["status", "assigned_to"]

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        analysts = get_user_model().objects.filter(groups__name=ANALYST_GROUP, is_active=True).order_by("username")
        self.fields["assigned_to"].queryset = analysts
        if not is_administrator(actor):
            self.fields.pop("assigned_to")
