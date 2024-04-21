# Generated by Django 5.0.4 on 2024-04-13 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0012_alter_eventschedule_latestexecuted_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HtmlDocuments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('html', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]