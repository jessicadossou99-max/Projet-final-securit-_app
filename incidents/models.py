from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models

class Incident(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_REVIEW = "in_review", "In review"
        RESOLVED = "resolved", "Resolved"

    title = models.CharField(max_length=150, validators=[MinLengthValidator(3)])
    description = models.TextField(max_length=5000, validators=[MinLengthValidator(10)])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="incidents")
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_incidents")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        indexes = [
            models.Index(fields=["created_by", "-created_at"], name="incident_owner_created_idx"),
            models.Index(fields=["assigned_to", "status"], name="incident_assignee_status_idx"),
        ]

    @property
    def reference(self):
        return f"INC-{self.pk:04d}"

    def __str__(self):
        return f"{self.reference}: {self.title}"


class IncidentComment(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="incident_comments")
    body = models.TextField(max_length=2000, validators=[MinLengthValidator(2)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]


class AuditEvent(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="audit_events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="incident_audit_events")
    action = models.CharField(max_length=50)
    detail = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
