# Generated by Django 5.0.6 on 2024-05-19 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0003_rename_html_1_pageyosocp_html_jockey_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventschedule',
            name='schedule_str',
            field=models.CharField(blank=True, default=',', max_length=255, null=True),
        ),
    ]
