# Generated by Django 2.1.2 on 2019-06-28 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0082_auto_20190624_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bugs',
            name='reward',
            field=models.BigIntegerField(default=20),
        ),
    ]