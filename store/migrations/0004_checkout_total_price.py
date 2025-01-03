# Generated by Django 5.1.1 on 2024-12-30 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0003_alter_product_category_checkout"),
    ]

    operations = [
        migrations.AddField(
            model_name="checkout",
            name="total_price",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Total price of the order",
                max_digits=10,
            ),
        ),
    ]
