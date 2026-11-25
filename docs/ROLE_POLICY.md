# Incident Desk role and access policy

## Roles

| Role | Capabilities | Explicit restrictions |
| --- | --- | --- |
| Reporter | Creates incidents, views own incidents, adds comments to own incidents | Cannot view, update workflow, assign, or delete another incident |
| Analyst | Views and updates only incidents assigned to them; can add comments | Cannot assign incidents or delete incidents |
| Incident administrator | Views all incidents, assigns analysts, changes status, deletes incidents | Account management stays in Django admin and uses a separate protected route |

The application recognises the Django groups `Incident analysts` and `Incident administrators`. A Django superuser is also an Incident Desk administrator. Run `python manage.py setup_roles` after migrations, then add staff members to these groups from `/admin/`.

## Enforcement

The policy is evaluated on the server for every detail, comment, update, and delete request. The browser never submits `created_by`; ownership is set from the authenticated session. A forbidden resource returns 404 instead of disclosing whether it exists. Deletion accepts only POST with CSRF validation and is reserved for administrators.

## Evidence

`incidents/tests/test_roles.py` exercises the reporter, analyst, and administrator paths, including denial of deletion for a reporter and analyst.
