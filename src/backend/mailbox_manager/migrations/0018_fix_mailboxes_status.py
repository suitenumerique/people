from django.db import migrations

from mailbox_manager import enums


def change_some_mailboxes_status_to_enabled(apps, schema_editor):
    Mailbox = apps.get_model('mailbox_manager', 'Mailbox')
    Mailbox.objects.filter(
        status=enums.MailboxStatusChoices.PENDING,
        domain__name__in=["mail.numerique.gouv.fr", "data.gouv.fr"]
        ).update(status=enums.MailboxStatusChoices.ENABLED)


class Migration(migrations.Migration):

    dependencies = [
        ('mailbox_manager', '0017_alter_maildomain_status'),
    ]

    operations = [
        migrations.RunPython(change_some_mailboxes_status_to_enabled, reverse_code=migrations.RunPython.noop),

    ]
