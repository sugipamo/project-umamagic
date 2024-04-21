# Generated by Django 5.0.4 on 2024-04-14 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0017_htmldocuments_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('cookie', models.FileField(blank=True, null=True, upload_to='cookies/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='eventcategory',
            name='use_method',
            field=models.CharField(default='Test.default_methods', max_length=255),
        ),
    ]