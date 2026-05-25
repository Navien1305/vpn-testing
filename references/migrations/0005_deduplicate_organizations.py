from django.db import migrations


def deduplicate_organizations(apps, schema_editor):
    Organization = apps.get_model("references", "Organization")
    User = apps.get_model("accounts", "User")

    groups = {}
    for organization in Organization.objects.order_by("id"):
        key = (organization.name, organization.type)
        groups.setdefault(key, []).append(organization)

    for organizations in groups.values():
        primary = organizations[0]
        duplicate_ids = [organization.id for organization in organizations[1:]]
        if duplicate_ids:
            User.objects.filter(organization_id__in=duplicate_ids).update(organization=primary)
            Organization.objects.filter(id__in=duplicate_ids).delete()
        if primary.city_id:
            primary.city = None
            primary.save(update_fields=["city", "updated_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("references", "0004_vpnappperiod_source_tag"),
    ]

    operations = [
        migrations.RunPython(deduplicate_organizations, migrations.RunPython.noop),
    ]
