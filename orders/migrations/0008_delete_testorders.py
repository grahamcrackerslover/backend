# Generated by Django 4.1.7 on 2023-04-30 08:35

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0007_testorders_orders_is_test_instance"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TestOrders",
        ),
    ]
