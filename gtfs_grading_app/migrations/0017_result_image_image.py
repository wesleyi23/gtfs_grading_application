# Generated by Django 3.1.3 on 2021-02-04 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gtfs_grading_app', '0016_remove_result_image_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='result_image',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]
