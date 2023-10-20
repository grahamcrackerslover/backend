# Generated by Django 4.1.7 on 2023-09-19 13:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0012_item_ph_price"),
    ]

    operations = [
        migrations.RenameField(
            model_name="item",
            old_name="ph_price",
            new_name="sgd_price",
        ),
        migrations.AlterField(
            model_name="case",
            name="category",
            field=models.CharField(
                choices=[
                    ("mondstadt", "Мондштадт"),
                    ("liyue", "Ли Юэ"),
                    ("sumeru", "Сумеру"),
                    ("inadzuma", "Инадзума"),
                    ("special", "Специальные"),
                ],
                default="mondstadt",
                max_length=10,
            ),
        ),
    ]
