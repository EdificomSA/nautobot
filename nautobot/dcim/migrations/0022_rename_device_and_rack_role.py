# Generated by Django 3.2.16 on 2022-11-25 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dcim", "0021_device_and_rack_roles_data_migrations"),
    ]

    operations = [
        # ##########
        # Device
        # ##########
        migrations.RemoveField(
            model_name="device",
            name="legacy_role",
        ),
        migrations.RenameField(
            model_name="device",
            old_name="new_role",
            new_name="role",
        ),
        # ##########
        # Rack
        # ##########
        migrations.RemoveField(
            model_name="rack",
            name="legacy_role",
        ),
        migrations.RenameField(
            model_name="rack",
            old_name="new_role",
            new_name="role",
        ),
    ]