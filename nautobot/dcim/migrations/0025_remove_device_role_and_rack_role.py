# Generated by Django 3.2.16 on 2022-12-16 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dcim", "0024_rename_device_and_rack_role"),
        ("ipam", "0011_rename_ipam_roles"),
        ("virtualization", "0012_rename_virtualmachine_roles"),
        ("extras", "0059_rename_configcontext_role"),
    ]

    operations = [
        migrations.DeleteModel(
            name="DeviceRole",
        ),
        migrations.DeleteModel(
            name="RackRole",
        ),
    ]