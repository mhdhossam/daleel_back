# Generated by Django 5.1.1 on 2024-12-22 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="is_customer",
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="is_vendor",
        ),
        migrations.AddField(
            model_name="customer",
            name="is_customer",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="vendor",
            name="is_vendor",
            field=models.BooleanField(default=True),
        ),
    ]
