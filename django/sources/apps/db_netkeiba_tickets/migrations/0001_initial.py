# Generated by Django 5.0.7 on 2024-08-01 09:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('web_netkeiba_pagesources', '0003_remove_page_need_update_pagedbnetkeiba_need_update_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HorseRacingTicketCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='馬券名')),
                ('horse_count', models.IntegerField(verbose_name='馬数')),
                ('length', models.IntegerField(verbose_name='当選範囲')),
                ('is_fixed', models.BooleanField(verbose_name='固定')),
                ('is_bracket', models.BooleanField(verbose_name='枠')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
        ),
        migrations.CreateModel(
            name='HorseRacingTicketParser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('success_parsing', models.BooleanField(default=False, verbose_name='パース成功フラグ')),
                ('need_update_at', models.DateTimeField(null=True, verbose_name='次回更新日時')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('page_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web_netkeiba_pagesources.pageresult', verbose_name='取得元ページ')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HorseRacingTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race_id', models.CharField(max_length=255, verbose_name='レースID')),
                ('ambiguous_name', models.CharField(max_length=255, verbose_name='あいまいな馬券名')),
                ('win_str', models.CharField(max_length=255, verbose_name='当選条件')),
                ('refund', models.IntegerField(verbose_name='払戻金')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='db_netkeiba_tickets.horseracingticketcategory', verbose_name='馬券名')),
                ('parser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='db_netkeiba_tickets.horseracingticketparser', verbose_name='取得元')),
            ],
        ),
        migrations.CreateModel(
            name='HorseRacingTicketTouchNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('horse_number', models.IntegerField(verbose_name='馬番号')),
                ('ticket_number_order', models.IntegerField(verbose_name='馬券内順序')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='db_netkeiba_tickets.horseracingticket', verbose_name='馬券')),
            ],
            options={
                'unique_together': {('ticket', 'horse_number', 'ticket_number_order')},
            },
        ),
    ]