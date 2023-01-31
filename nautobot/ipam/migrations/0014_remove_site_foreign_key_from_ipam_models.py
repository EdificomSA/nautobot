# Generated by Django 3.2.16 on 2023-01-31 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dcim", "0032_remove_site_foreign_key_from_dcim_models"),
        ("ipam", "0013_rename_foreign_keys_and_related_names"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="vlan",
            options={
                "ordering": ("location", "vlan_group", "vid"),
                "verbose_name": "VLAN",
                "verbose_name_plural": "VLANs",
            },
        ),
        migrations.AlterModelOptions(
            name="vlangroup",
            options={
                "ordering": ("location", "name"),
                "verbose_name": "VLAN group",
                "verbose_name_plural": "VLAN groups",
            },
        ),
        migrations.RemoveField(
            model_name="prefix",
            name="site",
        ),
        migrations.RemoveField(
            model_name="vlan",
            name="site",
        ),
        migrations.AlterUniqueTogether(
            name="vlangroup",
            unique_together={("location", "slug"), ("location", "name")},
        ),
        migrations.RemoveField(
            model_name="vlangroup",
            name="site",
        ),
    ]
