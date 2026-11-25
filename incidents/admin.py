from django.contrib import admin
from .models import AuditEvent, Incident, IncidentComment

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "severity", "status", "created_by", "assigned_to", "created_at"]
    list_select_related = ["created_by", "assigned_to"]
    search_fields = ["title", "created_by__username"]
    readonly_fields = ["created_by", "created_at"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(IncidentComment)
class IncidentCommentAdmin(admin.ModelAdmin):
    list_display = ["incident", "author", "created_at"]
    list_select_related = ["incident", "author"]
    readonly_fields = ["author", "created_at"]


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ["incident", "actor", "action", "created_at"]
    list_select_related = ["incident", "actor"]
    readonly_fields = ["incident", "actor", "action", "detail", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
