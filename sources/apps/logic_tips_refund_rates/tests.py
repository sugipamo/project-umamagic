from django.test import TestCase
from .models import HorseRacingTouchTip
from apps.db_netkeiba_tips.models import HorseRacingTip
from apps.db_netkeiba_tickets.models import HorseRacingTicket
from .models import HorseRacingTouchTipManager



class RefundRateTestCase(TestCase):
    def test_next(self):
        HorseRacingTip.make_dummy_tips(category='nar', race_id='202444070902')
        HorseRacingTicket.make_dummy_tickets(category='nar', race_id='202444070902')
        tip = HorseRacingTouchTipManager.next()
        self.assertTrue(tip is not None)

    def test_new_touch_tip(self):
        HorseRacingTip.make_dummy_tips(category='race', race_id='202410030811')
        HorseRacingTicket.make_dummy_tickets(category='race', race_id='202410030811')

        while HorseRacingTouchTipManager.new_touch_tip():
            pass
        for tip in HorseRacingTouchTip.objects.all():
            print(tip)