# Generated by Django 5.0.4 on 2024-04-18 14:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0022_remove_loginrequired_login_url_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loginrequired',
            name='title',
        ),
    ]
