from django.db import migrations


def lowercase_domain_list(apps, schema_editor):
    """Domains are case-insensitive: store them lowercased so exact matching works."""
    organization_model = apps.get_model("core", "Organization")
    for organization in organization_model.objects.exclude(domain_list=[]):
        lowered = [domain.lower() for domain in organization.domain_list]
        if lowered != organization.domain_list:
            organization.domain_list = lowered
            organization.save(update_fields=["domain_list"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_teamwebhook_protocol"),
    ]

    operations = [
        migrations.RunPython(lowercase_domain_list, migrations.RunPython.noop),
    ]
