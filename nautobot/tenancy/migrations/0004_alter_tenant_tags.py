# Generated by Django 3.2.16 on 2023-01-11 22:12

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        ("tenancy", "0003_mptt_to_tree_queries"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="tenant",
                    name="tags",
                    field=taggit.managers.TaggableManager(through="core.TaggedItem", to="core.Tag"),
                ),
            ],
            database_operations=[],
        )
    ]
