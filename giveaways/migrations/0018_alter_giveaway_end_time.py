# Generated by Django 4.1.7 on 2023-05-04 09:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("giveaways", "0017_alter_giveaway_end_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="giveaway",
            name="end_time",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2023, 5, 5, 9, 10, 30, 430505, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
