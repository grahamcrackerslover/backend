# Generated by Django 4.1.7 on 2023-04-13 08:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("giveaways", "0006_giveaway_winners"),
    ]

    operations = [
        migrations.AddField(
            model_name="giveaway",
            name="price",
            field=models.IntegerField(default=0),
        ),
    ]
