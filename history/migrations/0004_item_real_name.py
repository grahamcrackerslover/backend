# Generated by Django 4.1.7 on 2023-04-20 14:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("history", "0003_rename_is_frozen_item_from_shop"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="real_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
