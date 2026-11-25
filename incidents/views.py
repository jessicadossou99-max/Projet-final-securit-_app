from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, View

from .forms import IncidentCommentForm, IncidentForm, IncidentManageForm
from .models import AuditEvent, Incident
from .permissions import can_delete_incident, can_manage_incident, can_view_incident, is_administrator

class OwnedIncidentsMixin(LoginRequiredMixin):
    def get_queryset(self):
        user = self.request.user
        if is_administrator(user):
            return Incident.objects.all()
        return Incident.objects.filter(Q(created_by=user) | Q(assigned_to=user)).distinct()

class IncidentListView(OwnedIncidentsMixin, ListView):
    model = Incident
    template_name = "incidents/list.html"
    context_object_name = "incidents"
    paginate_by = 10

class IncidentDetailView(OwnedIncidentsMixin, DetailView):
    model = Incident
    template_name = "incidents/detail.html"
    context_object_name = "incident"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incident = self.object
        context["comment_form"] = IncidentCommentForm()
        context["can_manage"] = can_manage_incident(self.request.user, incident)
        context["can_delete"] = can_delete_incident(self.request.user)
        if context["can_manage"]:
            context["manage_form"] = IncidentManageForm(instance=incident, actor=self.request.user)
        return context

class IncidentCreateView(LoginRequiredMixin, CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = "incidents/form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        AuditEvent.objects.create(incident=self.object, actor=self.request.user, action="created")
        messages.success(self.request, "Your incident has been recorded.")
        return response

    def get_success_url(self):
        return reverse("incidents:detail", kwargs={"pk": self.object.pk})


@method_decorator(require_POST, name="dispatch")
class IncidentCommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        incident = get_object_or_404(Incident, pk=pk)
        if not can_view_incident(request.user, incident):
            raise Http404
        form = IncidentCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.incident = incident
            comment.author = request.user
            comment.save()
            AuditEvent.objects.create(incident=incident, actor=request.user, action="commented")
            messages.success(request, "Your comment has been added.")
        else:
            messages.error(request, "Your comment could not be added.")
        return redirect("incidents:detail", pk=incident.pk)


@method_decorator(require_POST, name="dispatch")
class IncidentManageView(LoginRequiredMixin, View):
    def post(self, request, pk):
        incident = get_object_or_404(Incident, pk=pk)
        if not can_manage_incident(request.user, incident):
            raise Http404
        before = f"status={incident.status}; assigned_to={incident.assigned_to_id or 'none'}"
        form = IncidentManageForm(request.POST, instance=incident, actor=request.user)
        if form.is_valid():
            updated = form.save()
            after = f"status={updated.status}; assigned_to={updated.assigned_to_id or 'none'}"
            if before != after:
                AuditEvent.objects.create(incident=updated, actor=request.user, action="updated", detail=after)
            messages.success(request, "Incident workflow details were updated.")
        else:
            messages.error(request, "The workflow update was not valid.")
        return redirect("incidents:detail", pk=incident.pk)


@method_decorator(require_POST, name="dispatch")
class IncidentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        incident = get_object_or_404(Incident, pk=pk)
        if not can_delete_incident(request.user):
            raise Http404
        reference = incident.reference
        incident.delete()
        messages.success(request, f"{reference} was deleted by an administrator.")
        return redirect("incidents:list")
