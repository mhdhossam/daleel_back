# Generated by Django 5.1.1 on 2025-01-02 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0020_remove_order_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="status",
            field=models.CharField(blank=True, choices=[], max_length=20, null=True),
        ),
    ]