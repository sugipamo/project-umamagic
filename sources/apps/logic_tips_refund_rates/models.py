from django.db import models
from apps.db_netkeiba_tickets.models import HorseRacingTicket
from apps.db_netkeiba_tips.models import HorseRacingTip

class HorseRacingTouchTipManager(models.Model):
    tip = models.ForeignKey(HorseRacingTip, on_delete=models.CASCADE)

    @classmethod
    def next(cls):
        unused_tips = HorseRacingTip.objects.exclude(id__in=cls.objects.values_list('tip_id', flat=True))
        unused_tip = unused_tips.first()
        return unused_tip
    
    @classmethod
    def new_touch_tip(cls):
        tip = cls.next()
        if tip is None:
            return False
        
        tickets = HorseRacingTicket.objects.filter(race_id=tip.race_id)

        touch_tips = []
        for ticket in tickets:
            for i, horse_number in enumerate(ticket.win_str.split()):
                i = int(i) + 1
                horse_number = int(horse_number)

                if tip.horse_number == horse_number:
                    touch_tip = HorseRacingTouchTip(race_id=tip.race_id, tip=tip, ticket=ticket, touch_order=i + 1)
                    touch_tips.append(touch_tip)
                
        cls(tip=tip).save()
        for touch_tip in touch_tips:
            touch_tip.save()

        return True

class HorseRacingTouchTip(models.Model):
    race_id = models.CharField(max_length=255)
    tip = models.ForeignKey(HorseRacingTip, on_delete=models.CASCADE)
    ticket = models.ForeignKey(HorseRacingTicket, on_delete=models.CASCADE)
    touch_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.tip} - {self.ticket}'
    
