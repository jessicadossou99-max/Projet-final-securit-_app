"""Safe, owner-scoped search used only by the local synthetic exercise."""
from incidents.models import Incident

def search_incidents(user_id, query):
    # ORM parameter binding keeps the query as data; the owner filter remains mandatory.
    return list(
        Incident.objects.filter(created_by_id=user_id, title__icontains=query)
        .order_by("-created_at", "-pk")
        .values("id", "title", "description")[:20]
    )
