# Generated by Django 5.1.1 on 2024-12-31 00:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_checkout_total_price"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="checkout",
            name="total_price",
        ),
    ]
