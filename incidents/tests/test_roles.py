from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from incidents.models import AuditEvent, Incident, IncidentComment
from incidents.permissions import ADMIN_GROUP, ANALYST_GROUP


class RolePolicyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.reporter = User.objects.create_user(username="reporter", password="test-password-only")
        cls.other_reporter = User.objects.create_user(username="other", password="test-password-only")
        cls.analyst = User.objects.create_user(username="analyst", password="test-password-only")
        cls.administrator = User.objects.create_user(username="administrator", password="test-password-only")
        Group.objects.get_or_create(name=ANALYST_GROUP)[0].user_set.add(cls.analyst)
        Group.objects.get_or_create(name=ADMIN_GROUP)[0].user_set.add(cls.administrator)
        cls.report = Incident.objects.create(title="Reporter issue", description="Synthetic reporter issue details.", created_by=cls.reporter)
        cls.other_report = Incident.objects.create(title="Other issue", description="Synthetic other issue details.", created_by=cls.other_reporter)

    def test_reporter_cannot_view_or_delete_another_report(self):
        self.client.force_login(self.reporter)
        self.assertEqual(self.client.get(reverse("incidents:detail", args=[self.other_report.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("incidents:delete", args=[self.report.pk])).status_code, 404)
        self.assertTrue(Incident.objects.filter(pk=self.report.pk).exists())

    def test_assigned_analyst_can_view_and_update_but_not_delete(self):
        self.report.assigned_to = self.analyst
        self.report.save(update_fields=["assigned_to"])
        self.client.force_login(self.analyst)
        self.assertEqual(self.client.get(reverse("incidents:detail", args=[self.report.pk])).status_code, 200)
        response = self.client.post(reverse("incidents:manage", args=[self.report.pk]), {"status": Incident.Status.IN_REVIEW})
        self.assertRedirects(response, reverse("incidents:detail", args=[self.report.pk]))
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, Incident.Status.IN_REVIEW)
        self.assertEqual(self.client.post(reverse("incidents:delete", args=[self.report.pk])).status_code, 404)

    def test_administrator_can_assign_and_delete(self):
        self.client.force_login(self.administrator)
        response = self.client.post(reverse("incidents:manage", args=[self.report.pk]), {"status": Incident.Status.RESOLVED, "assigned_to": self.analyst.pk})
        self.assertRedirects(response, reverse("incidents:detail", args=[self.report.pk]))
        self.report.refresh_from_db()
        self.assertEqual(self.report.assigned_to, self.analyst)
        self.assertEqual(self.report.status, Incident.Status.RESOLVED)
        self.assertTrue(AuditEvent.objects.filter(incident=self.report, action="updated").exists())
        response = self.client.post(reverse("incidents:delete", args=[self.report.pk]))
        self.assertRedirects(response, reverse("incidents:list"))
        self.assertFalse(Incident.objects.filter(pk=self.report.pk).exists())

    def test_comment_is_bound_to_signed_in_user_and_escaped(self):
        self.client.force_login(self.reporter)
        payload = "<script>alert('x')</script>"
        response = self.client.post(reverse("incidents:comment", args=[self.report.pk]), {"body": payload})
        self.assertRedirects(response, reverse("incidents:detail", args=[self.report.pk]))
        comment = IncidentComment.objects.get()
        self.assertEqual(comment.author, self.reporter)
        response = self.client.get(reverse("incidents:detail", args=[self.report.pk]))
        self.assertNotContains(response, payload)
        self.assertContains(response, "&lt;script&gt;")

    def test_homepage_is_public_and_has_cv_projects(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Dossou Sossi")
        self.assertContains(response, "Incident Desk")
        self.assertContains(response, "MyMovieShelf")
