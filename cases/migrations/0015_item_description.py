# Generated by Django 4.1.7 on 2023-10-28 21:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0014_item_for_sale"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="description",
            field=models.TextField(null=True),
        ),
    ]
