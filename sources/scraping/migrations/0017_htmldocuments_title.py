# Generated by Django 5.0.4 on 2024-04-14 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0016_htmldocuments_parsed'),
    ]

    operations = [
        migrations.AddField(
            model_name='htmldocuments',
            name='title',
            field=models.CharField(default='', max_length=255),
        ),
    ]