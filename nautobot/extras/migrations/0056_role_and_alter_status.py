# Generated by Django 3.2.16 on 2022-11-19 23:15
import uuid

import django.core.serializers.json
from django.db import migrations, models

import nautobot.core.models.fields
import nautobot.extras.models.mixins
import nautobot.extras.utils


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0055_alter_joblogentry_scheduledjob_webhook_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="status",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "slug",
                    nautobot.core.models.fields.AutoSlugField(
                        blank=True, max_length=100, populate_from="name", unique=True
                    ),
                ),
                ("color", nautobot.core.models.fields.ColorField(default="9e9e9e", max_length=6)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("weight", models.PositiveSmallIntegerField(blank=True, null=True)),
                (
                    "content_types",
                    models.ManyToManyField(
                        limit_choices_to=nautobot.extras.utils.RoleModelsQuery(),
                        related_name="roles",
                        to="contenttypes.ContentType",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "abstract": False,
            },
            bases=(models.Model, nautobot.extras.models.mixins.NotesMixin),
        ),
    ]
