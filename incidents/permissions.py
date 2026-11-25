"""Centralized, server-side policy for Incident Desk roles."""

ADMIN_GROUP = "Incident administrators"
ANALYST_GROUP = "Incident analysts"


def is_administrator(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name=ADMIN_GROUP).exists())


def is_analyst(user):
    return user.is_authenticated and user.groups.filter(name=ANALYST_GROUP).exists()


def can_view_incident(user, incident):
    return is_administrator(user) or incident.created_by_id == user.id or incident.assigned_to_id == user.id


def can_manage_incident(user, incident):
    return is_administrator(user) or incident.assigned_to_id == user.id


def can_delete_incident(user):
    return is_administrator(user)
