# Generated by Django 5.1.1 on 2025-01-02 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0022_alter_order_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[("CART", "CART")], default="CART", max_length=20
            ),
        ),
    ]
