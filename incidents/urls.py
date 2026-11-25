from django.urls import path
from .views import IncidentCommentCreateView, IncidentCreateView, IncidentDeleteView, IncidentDetailView, IncidentListView, IncidentManageView
app_name = "incidents"
urlpatterns = [
    path("", IncidentListView.as_view(), name="list"),
    path("incidents/new/", IncidentCreateView.as_view(), name="create"),
    path("incidents/<int:pk>/", IncidentDetailView.as_view(), name="detail"),
    path("incidents/<int:pk>/comments/", IncidentCommentCreateView.as_view(), name="comment"),
    path("incidents/<int:pk>/manage/", IncidentManageView.as_view(), name="manage"),
    path("incidents/<int:pk>/delete/", IncidentDeleteView.as_view(), name="delete"),
]
