# Generated by Django 4.1.7 on 2023-04-08 20:56

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bonuscode",
            name="percentage",
        ),
        migrations.RemoveField(
            model_name="bonuscode",
            name="value",
        ),
    ]
