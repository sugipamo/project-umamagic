# Generated by Django 5.0.7 on 2024-07-15 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_netkeiba_pagesources', '0002_page_need_update'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='need_update',
        ),
        migrations.AddField(
            model_name='pagedbnetkeiba',
            name='need_update',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pageoikiri',
            name='need_update',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pageresult',
            name='need_update',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pageshutuba',
            name='need_update',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pageyoso',
            name='need_update',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pageyosocp',
            name='need_update',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pageyosopro',
            name='need_update',
            field=models.BooleanField(default=False),
        ),
    ]