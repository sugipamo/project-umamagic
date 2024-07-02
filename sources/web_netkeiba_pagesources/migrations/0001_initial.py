# Generated by Django 5.0.6 on 2024-07-02 14:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race_id', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PageCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PageDbNetkeiba',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web_netkeiba_pagesources.page')),
                ('html', models.BinaryField(blank=True, null=True)),
            ],
            bases=('web_netkeiba_pagesources.page',),
        ),
        migrations.CreateModel(
            name='PageOikiri',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web_netkeiba_pagesources.page')),
                ('html', models.BinaryField(blank=True, null=True)),
            ],
            bases=('web_netkeiba_pagesources.page',),
        ),
        migrations.CreateModel(
            name='PageResult',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web_netkeiba_pagesources.page')),
                ('html', models.BinaryField(blank=True, null=True)),
            ],
            bases=('web_netkeiba_pagesources.page',),
        ),
        migrations.CreateModel(
            name='PageShutuba',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web_netkeiba_pagesources.page')),
                ('html', models.BinaryField(blank=True, null=True)),
            ],
            bases=('web_netkeiba_pagesources.page',),
        ),
        migrations.CreateModel(
            name='PageYoso',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web_netkeiba_pagesources.page')),
                ('html', models.BinaryField(blank=True, null=True)),
            ],
            bases=('web_netkeiba_pagesources.page',),
        ),
        migrations.CreateModel(
            name='PageYosoCp',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web_netkeiba_pagesources.page')),
                ('html_rising', models.BinaryField(blank=True, null=True)),
                ('html_precede', models.BinaryField(blank=True, null=True)),
                ('html_spurt', models.BinaryField(blank=True, null=True)),
                ('html_jockey', models.BinaryField(blank=True, null=True)),
                ('html_trainer', models.BinaryField(blank=True, null=True)),
                ('html_pedigree', models.BinaryField(blank=True, null=True)),
            ],
            bases=('web_netkeiba_pagesources.page',),
        ),
        migrations.CreateModel(
            name='PageYosoPro',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web_netkeiba_pagesources.page')),
                ('html', models.BinaryField(blank=True, null=True)),
            ],
            bases=('web_netkeiba_pagesources.page',),
        ),
        migrations.AddField(
            model_name='page',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='web_netkeiba_pagesources.pagecategory'),
        ),
    ]
