# Generated by Django 5.0.6 on 2024-06-22 08:22

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('status', models.IntegerField(choices=[(1, '待機'), (2, '実行中'), (3, '完了'), (4, 'エラー')], default=1)),
                ('event_function', models.CharField(max_length=255)),
                ('nextexecutedatetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('schedule_str_default', models.CharField(blank=True, default='0', max_length=255, null=True)),
                ('schedule_str', models.CharField(blank=True, default=',', max_length=255, null=True)),
                ('latestcalled_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ScheduleDoEventError',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event_schedules.schedule')),
            ],
        ),
    ]
