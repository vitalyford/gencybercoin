# Generated by Django 2.1.2 on 2020-03-20 23:26

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0090_auto_20200320_1924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='image_file',
            field=models.ImageField(default='/static/user/img/no-image.jpg', upload_to=user.models.image_upload_activities),
        ),
        migrations.AlterField(
            model_name='marketitem',
            name='image_file',
            field=models.ImageField(default='/static/user/img/no-image.jpg', upload_to=user.models.image_upload_market),
        ),
    ]