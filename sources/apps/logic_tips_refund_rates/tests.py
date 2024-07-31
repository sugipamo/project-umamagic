from django.test import TestCase
from apps.db_netkeiba_tips.models import HorseRacingTip
from apps.db_netkeiba_tickets.models import HorseRacingTicket
from .models import HorseRacingTipRefundManager



class RefundRateTestCase(TestCase):
    def test_next(self):
        HorseRacingTip.make_dummy_tips(category='nar', race_id='202444070902')
        HorseRacingTicket.make_dummy_tickets(category='nar', race_id='202444070902')
        tip = HorseRacingTipRefundManager.next()
        print("tip", tip)
        self.assertTrue(tip is not None)


