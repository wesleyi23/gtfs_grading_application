# Generated by Django 3.1.3 on 2021-02-04 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gtfs_grading_app', '0013_auto_20210114_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result_reference',
            name='published_reference_date',
            field=models.DateTimeField(),
        ),
    ]
