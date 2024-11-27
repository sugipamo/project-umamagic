from django.test import TestCase
from apps.db_netkeiba_tips.models import HorseRacingTip
from apps.db_netkeiba_tickets.models import HorseRacingTicket
from .models import HorseRacingTipRefundManager



class RefundRateTestCase(TestCase):
    def test_next(self):
        HorseRacingTip.make_dummy_tips(category='nar', race_id='202444070902')
        HorseRacingTicket.make_dummy_tickets(category='nar', race_id='202444070902')
        tip = HorseRacingTipRefundManager.next()
        self.assertTrue(tip is not None)

    def test_calc_combination_count(self):
        calc_combination_count = HorseRacingTipRefundManager()._HorseRacingTipRefundManager__calc_combination_count
        def helper(tips):
            tips = [set(t) for t in tips]
            from itertools import product
            cnt = 0
            # print(tips)
            for t in product(*tips):
                if len(set(t)) != len(t):
                    # print("ng", list(t))
                    continue
                # print("ok", list(t))
                cnt += 1
            return calc_combination_count(tips), cnt
        # 3つまで確認
        self.assertEqual(*helper([[1]]))
        self.assertEqual(*helper([[1], [1]]))
        self.assertEqual(*helper([[1, 2], [1, 2]]))
        self.assertEqual(*helper([[1, 2], [3, 4]]))
        self.assertEqual(*helper([[1, 2], [2, 3]]))
        self.assertEqual(*helper([[1, 2], [3, 4], [5, 6]]))
        self.assertEqual(*helper([[1, 2], [2, 3], [3, 4]]))
        self.assertEqual(*helper([[1, 2], [3, 4], [5, 6], [7, 8]]))
        self.assertEqual(*helper([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
        self.assertEqual(*helper([[1, 2, 3], [3, 4, 5], [5, 6, 7]]))
        self.assertEqual(*helper([[1, 2], [2, 3], [3, 4]]))
        self.assertEqual(*helper([[1, 2, 3], [2, 3, 4], [3, 4, 5]]))


    def test_new_refunds(self):
        HorseRacingTip.make_dummy_tips(category='nar', race_id='202444070902')
        HorseRacingTicket.make_dummy_tickets(category='nar', race_id='202444070902')
        tip = HorseRacingTipRefundManager.new_refunds()
        self.assertTrue(tip is not None)

