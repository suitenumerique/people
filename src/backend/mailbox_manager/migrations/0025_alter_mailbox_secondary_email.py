# Generated by Django 5.1.8 on 2025-04-08 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailbox_manager', '0024_domaininvitation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailbox',
            name='secondary_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='secondary email address'),
        ),
    ]
