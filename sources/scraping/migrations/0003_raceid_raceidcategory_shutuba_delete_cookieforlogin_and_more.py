# Generated by Django 5.0.4 on 2024-04-27 08:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0002_cookieforlogin'),
    ]

    operations = [
        migrations.CreateModel(
            name='RaceId',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raceid', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='RaceIdCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Shutuba',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='CookieForLogin',
        ),
        migrations.AddField(
            model_name='raceid',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scraping.raceidcategory'),
        ),
        migrations.AddField(
            model_name='shutuba',
            name='raceid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scraping.raceid'),
        ),
    ]
