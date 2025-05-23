# Generated by Django 5.1.1 on 2024-10-22 10:07

import core.models
import django.contrib.postgres.fields
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='primary key for the record as UUID', primary_key=True, serialize=False, verbose_name='id')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='date and time at which a record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='date and time at which a record was last updated', verbose_name='updated at')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('registration_id_list', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=128), blank=True, default=list, size=None, verbose_name='registration ID list')),
                ('domain_list', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), blank=True, default=list, size=None, verbose_name='domain list')),
            ],
            options={
                'verbose_name': 'organization',
                'verbose_name_plural': 'organizations',
                'db_table': 'people_organization',
                'constraints': [models.CheckConstraint(condition=models.Q(('registration_id_list__len__gt', 0), ('domain_list__len__gt', 0), _connector='OR'), name='registration_id_or_domain', violation_error_message='An organization must have at least a registration ID or a domain.')],
            },
        ),
        migrations.AddField(
            model_name='team',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='teams', to='core.organization'),
        ),
        migrations.AddField(
            model_name='user',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='users', to='core.organization'),
        ),
        migrations.CreateModel(
            name='OrganizationAccess',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='primary key for the record as UUID', primary_key=True, serialize=False, verbose_name='id')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='date and time at which a record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='date and time at which a record was last updated', verbose_name='updated at')),
                ('role', models.CharField(choices=[('administrator', 'Administrator')], default='administrator', max_length=20)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organization_accesses', to='core.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organization_accesses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Organization/user relation',
                'verbose_name_plural': 'Organization/user relations',
                'db_table': 'people_organization_access',
                'constraints': [models.UniqueConstraint(fields=('user', 'organization'), name='unique_organization_user', violation_error_message='This user is already in this organization.')],
            },
        ),
    ]
