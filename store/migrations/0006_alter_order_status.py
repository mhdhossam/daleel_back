# Generated by Django 5.1.1 on 2024-12-31 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0005_remove_checkout_total_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("PROCESSING", "Processing"),
                    ("SHIPPED", "Shipped"),
                    ("DELIVERED", "Delivered"),
                    ("CANCELLED", "Cancelled"),
                ],
                default="Pending",
                help_text="Current status of the order",
                max_length=20,
            ),
        ),
    ]
