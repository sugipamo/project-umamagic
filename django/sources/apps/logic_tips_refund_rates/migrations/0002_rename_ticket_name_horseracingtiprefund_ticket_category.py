# Generated by Django 5.0.7 on 2024-08-01 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logic_tips_refund_rates', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='horseracingtiprefund',
            old_name='ticket_name',
            new_name='ticket_category',
        ),
    ]