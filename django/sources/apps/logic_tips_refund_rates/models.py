from django.db import models
from apps.db_netkeiba_tickets.models import HorseRacingTicketCategory, HorseRacingTicket
from apps.db_netkeiba_tips.models import HorseRacingTipAuthor, HorseRacingTipMark, HorseRacingTip
from apps.db_netkeiba_tips.models import HorseRacingTipParserForPageYoso, HorseRacingTipParserForPageYosoCp, HorseRacingTipParserForPageYosoPro
from django.contrib.postgres.fields import JSONField

class HorseRacingTipRefundManager(models.Model):
    race_id = models.CharField(max_length=255, unique=True, verbose_name='レースID')
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
        
        existing_race_ids = set(cls.objects.values_list('race_id', flat=True))
        
        race_ids_list = [
            set(p.page_source.race_id for p in parser) - existing_race_ids
            for parser in parsers
        ] + [
            set(HorseRacingTicket.objects.values_list('race_id', flat=True)) - existing_race_ids
        ]

        common_race_ids = set.intersection(*race_ids_list) if race_ids_list else set()

        manager = None
        for race_id in common_race_ids:
            manager = cls.objects.create(race_id=race_id)
        
        return manager
    
    def __calc_combination_count(self, tips):
        cnt = 1
        for tip in tips:
            cnt *= len(tip)

        if len(tips) == 2:
            cnt -= len(tips[0] & tips[1])
        
        if len(tips) == 3:
            cnt -= len(tips[0] & tips[1]) * len(tips[2])
            cnt -= len(tips[1] & tips[2]) * len(tips[0])
            cnt -= len(tips[2] & tips[0]) * len(tips[1])
            cnt += len(tips[0] & tips[1] & tips[2]) * 2

        return cnt

    @classmethod
    def new_refunds(self):
        manager = HorseRacingTipRefundManager.next()
        if manager is None:
            return None
        
        from collections import defaultdict
        tickets = HorseRacingTicket.objects.filter(race_id=manager.race_id)
        ticket_categorys = HorseRacingTicketCategory.objects.filter(id__in=tickets.values_list('category_id', flat=True))
        ticket_categorys_with_horsecount = defaultdict(list)
        for ticket_category in ticket_categorys:
            if ticket_category.is_bracket:
                # "枠は無視"
                continue
            ticket_categorys_with_horsecount[ticket_category.horse_count].append(ticket_category)

        
        tips = defaultdict(list)
        for tip in HorseRacingTip.objects.filter(race_id=manager.race_id):
            tips[(tip.author_id, tip.mark_id)].append(tip.horse_number)

        from itertools import combinations, permutations
        tip_refunds = []
        for i in range(1, 4):
            for tip_combination in combinations(tips.keys(), i):
                tip_combination, horse_numbers = zip(*[(tip, set(tips[tip])) for tip in sorted(tip_combination)])
                cnt = self.__calc_combination_count(self, horse_numbers)
                if cnt == 0:
                    continue

                for ticket_category in ticket_categorys_with_horsecount[i]:
                    if ticket_category.is_fixed:
                        for temp in permutations(zip(tip_combination, horse_numbers)):
                            ordered_tip_combination, ordered_horse_numbers = zip(*temp)
                            tip_refund = HorseRacingTipRefund(
                                ticket_category=ticket_category,
                                count = cnt,
                                refund = 0,          
                                predictions = ordered_tip_combination,
                            )
                            for win_str, refund in tickets.filter(category=ticket_category).values_list('win_str', 'refund'):
                                if len(win_str.split()) != len(ordered_horse_numbers):
                                    raise ValueError("Invalid win_str")
                                if all(i in nums for i, nums in zip(win_str.split(), ordered_horse_numbers)):
                                    tip_refund.refund += refund
                            tip_refunds.append(tip_refund)
                    else:
                        ordered_tip_combination, ordered_horse_numbers = list(tip_combination), list(horse_numbers)
                        tip_refund = HorseRacingTipRefund(
                            ticket_category=ticket_category,
                            count = cnt,
                            refund = 0,          
                            predictions = ordered_tip_combination,
                        )
                        for win_str, refund in tickets.filter(category=ticket_category).values_list('win_str', 'refund'):
                            if len(win_str.split()) != len(ordered_horse_numbers):
                                raise ValueError("Invalid win_str")
                            win_strs = set(win_str.split())
                            for ordered_horse_number in ordered_horse_numbers:
                                for num in ordered_horse_number:
                                    if num in win_strs:
                                        win_strs.remove(num)
                                        break
                            if not win_strs:
                                tip_refund.refund += refund
                        tip_refunds.append(tip_refund)
                            
        for tip_refund in tip_refunds:
            print(tip_refund)
            tip_refund.save()

        manager.need_update = False
        manager.save()
        return manager

class HorseRacingTipRefund(models.Model):
    race_id = models.CharField(max_length=255, verbose_name='レースID')
    ticket_category = models.ForeignKey(HorseRacingTicketCategory, on_delete=models.CASCADE, verbose_name='馬券')
    count = models.IntegerField(verbose_name='購入数')
    refund = models.IntegerField(verbose_name='払戻金額')
    predictions = models.JSONField(verbose_name='予想', default=dict)  # 予想家とマークの情報をJSON形式で保存

    def __str__(self):
        return f'{self.ticket_category.name} {self.count} {self.refund} {self.predictions}'

    @property
    def amount(self):
        return self.count * 100

    @property
    def refund_rate(self):
        if self.amount == 0:
            return 0
        return self.refund / self.amount