# Generated by Django 5.1.1 on 2025-01-02 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0021_order_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                blank=True, choices=[("CART", "CART")], max_length=20, null=True
            ),
        ),
    ]
