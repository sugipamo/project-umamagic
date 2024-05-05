# Generated by Django 5.0.4 on 2024-05-05 03:49

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0002_remove_race_html_shutuba_html'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventcategory',
            name='durationtime',
        ),
        migrations.RemoveField(
            model_name='eventschedule',
            name='enddatetime',
        ),
        migrations.RemoveField(
            model_name='eventschedule',
            name='latestexecuted_at',
        ),
        migrations.RemoveField(
            model_name='eventschedule',
            name='startdatetime',
        ),
        migrations.AddField(
            model_name='eventschedule',
            name='nextexecutedatetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AddField(
            model_name='eventschedule',
            name='repeat',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='eventcategory',
            name='repeat',
            field=models.CharField(default='', max_length=255),
        ),
    ]
