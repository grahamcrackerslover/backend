# Generated by Django 4.1.7 on 2023-05-04 09:13

from django.db import migrations, models
import giveaways.models


class Migration(migrations.Migration):
    dependencies = [
        ("giveaways", "0018_alter_giveaway_end_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="giveaway",
            name="end_time",
            field=models.DateTimeField(default=giveaways.models.default_end_time),
        ),
    ]
