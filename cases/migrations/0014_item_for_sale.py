# Generated by Django 4.1.7 on 2023-10-28 16:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0013_rename_ph_price_item_sgd_price_alter_case_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="for_sale",
            field=models.BooleanField(default=True),
        ),
    ]
