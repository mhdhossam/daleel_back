# Generated by Django 5.1.1 on 2025-01-02 23:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0008_alter_order_status"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="status",
            new_name="order_status",
        ),
    ]
