# Generated by Django 3.1.3 on 2021-02-04 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gtfs_grading_app', '0018_auto_20210204_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result_image',
            name='image',
            field=models.ImageField(upload_to='result_images'),
        ),
    ]