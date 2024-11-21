
from django.db import migrations, models

from mailbox_manager import enums

def change_mailboxes_status_to_enabled(apps, schema_editor):
    Mailbox = apps.get_model('mailbox_manager', 'Mailbox')
    Mailbox.objects.filter(status=enums.MailboxStatusChoices.PENDING).update(status=enums.MailboxStatusChoices.ENABLED)


class Migration(migrations.Migration):

    dependencies = [
        ('mailbox_manager', '0014_mailbox_status'),
    ]

    operations = [
        migrations.RunPython(change_mailboxes_status_to_enabled, reverse_code=migrations.RunPython.noop),

    ]
