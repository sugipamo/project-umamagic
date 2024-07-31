from django.db import models
from apps.db_netkeiba_tickets.models import HorseRacingTicket
from apps.db_netkeiba_tips.models import HorseRacingTip
from apps.db_netkeiba_tips.models import HorseRacingTipParserForPageYoso, HorseRacingTipParserForPageYosoCp, HorseRacingTipParserForPageYosoPro

class HorseRacingTipRefundManager(models.Model):
    race_id = models.CharField(max_length=255, verbose_name='レースID')
    need_update = models.BooleanField(default=True, verbose_name='更新が必要かどうか')

    @classmethod
    def next(cls):
        need_updates = cls.objects.filter(need_update=True)
        if need_updates.exists():
            return need_updates.first()

        parsers = [
            HorseRacingTipParserForPageYoso.objects.select_related('page_source').all(),
            HorseRacingTipParserForPageYosoCp.objects.select_related('page_source').all(),
            HorseRacingTipParserForPageYosoPro.objects.select_related('page_source').all()
        ]
        
        # HorseRacingTipRefundManagerに既に存在するrace_idを取得
        existing_race_ids = set(cls.objects.values_list('race_id', flat=True))
        
        # 各parserからrace_idを取得し、既に存在するrace_idを除外
        race_ids_list = [
            set(p.page_source.race_id for p in parser) - existing_race_ids
            for parser in parsers
        ]

        common_race_ids = set.intersection(*race_ids_list) if race_ids_list else set()

        return_value = None
        for race_id in common_race_ids:  
            return_value = cls.objects.create(race_id=race_id)
        
        return return_value
    