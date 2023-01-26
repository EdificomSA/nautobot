# Generated by Django 3.1.14 on 2022-02-16 17:38

import django.core.serializers.json
from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion
import nautobot.core.models.fields
import taggit.managers
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0022_objectchange_object_datav2"),
    ]

    operations = [
        migrations.CreateModel(
            name="JobModel",
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
                ("source", models.CharField(db_index=True, editable=False, max_length=110)),
                ("module_name", models.CharField(db_index=True, editable=False, max_length=100)),
                ("job_class_name", models.CharField(db_index=True, editable=False, max_length=100)),
                (
                    "slug",
                    nautobot.core.models.fields.AutoSlugField(
                        blank=True,
                        max_length=320,
                        populate_from=["source", "module_name", "job_class_name"],
                        unique=True,
                    ),
                ),
                ("grouping", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("installed", models.BooleanField(db_index=True, default=True, editable=False)),
                ("enabled", models.BooleanField(default=False)),
                ("commit_default", models.BooleanField(default=True)),
                ("hidden", models.BooleanField(db_index=True, default=False)),
                ("read_only", models.BooleanField(default=False)),
                ("approval_required", models.BooleanField(default=False)),
                ("soft_time_limit", models.FloatField(default=0, validators=[MinValueValidator(0)])),
                ("time_limit", models.FloatField(default=0, validators=[MinValueValidator(0)])),
                ("grouping_override", models.BooleanField(default=False)),
                ("name_override", models.BooleanField(default=False)),
                ("description_override", models.BooleanField(default=False)),
                ("commit_default_override", models.BooleanField(default=False)),
                ("hidden_override", models.BooleanField(default=False)),
                ("read_only_override", models.BooleanField(default=False)),
                ("approval_required_override", models.BooleanField(default=False)),
                ("soft_time_limit_override", models.BooleanField(default=False)),
                ("time_limit_override", models.BooleanField(default=False)),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ["grouping", "name"],
                "managed": True,
                "unique_together": {("grouping", "name"), ("source", "module_name", "job_class_name")},
            },
        ),
        migrations.DeleteModel(
            name="Job",
        ),
        migrations.RenameModel(
            old_name="JobModel",
            new_name="Job",
        ),
        migrations.AddField(
            model_name="jobresult",
            name="job_model",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="results",
                to="extras.job",
            ),
        ),
        migrations.AddField(
            model_name="scheduledjob",
            name="job_model",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="scheduled_jobs",
                to="extras.job",
            ),
        ),
    ]
