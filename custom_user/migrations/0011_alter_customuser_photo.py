# Generated by Django 4.1.7 on 2023-12-15 23:43

import custom_user.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("custom_user", "0010_remove_customuser_photo_url_customuser_photo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="photo",
            field=models.ImageField(
                blank=True,
                default="photos/klee.jpeg",
                null=True,
                upload_to=custom_user.models.user_directory_path,
            ),
        ),
    ]
